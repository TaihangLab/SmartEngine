from typing import Dict, List
from core.skills.base import BaseSkill, Model
from core.alert_detector import AlertDetector, CrowdDensityAlertDetector

class CrowdDensitySkill(BaseSkill):
    """人流密度监控技能"""
    
    @property
    def name(self) -> str:
        return "crowd_density"
    
    @property
    def models(self) -> List[Model]:
        return [
            Model(
                name="yolov5",
                version="v1",
                endpoint="person-detection-predictor",
                input_shape=[640, 640, 3],
                preprocessing_config={
                    "resize_mode": "letterbox",
                    "mean": [0.485, 0.456, 0.406],
                    "std": [0.229, 0.224, 0.225]
                },
                postprocessing_config={
                    "confidence_threshold": 0.3,  # 降低阈值以检测更多人
                    "nms_threshold": 0.45
                }
            )
        ]
    
    @property
    def pipeline_config(self) -> Dict:
        return {
            "type": "sequential",
            "count_only": True  # 只需要计数，不需要详细位置
        }
    
    @property
    def alert_detector(self) -> AlertDetector:
        return CrowdDensityAlertDetector()
    
    def process_results(self, results: List[Dict]) -> Dict:
        """处理人流密度检测结果"""
        processed_result = {
            "skill_name": self.name,
            "detections": [],
            "metadata": {
                "total_count": 0,
                "density_level": "low"
            }
        }
        
        # 处理检测结果
        for result in results:
            persons = [d for d in result.get("detections", [])
                      if d["class_name"] == "person"]
            processed_result["detections"].extend(persons)
        
        # 计算密度等级
        total_count = len(processed_result["detections"])
        processed_result["metadata"]["total_count"] = total_count
        
        if total_count >= 20:
            density_level = "high"
        elif total_count >= 10:
            density_level = "medium"
        else:
            density_level = "low"
        
        processed_result["metadata"]["density_level"] = density_level
        
        return processed_result 