from typing import Dict, List
from core.skills.base import BaseSkill, Model
from core.alert_detector import AlertDetector, IntrusionAlertDetector

class IntrusionDetectionSkill(BaseSkill):
    """入侵检测技能"""
    
    @property
    def name(self) -> str:
        return "intrusion_detection"
    
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
                    "confidence_threshold": 0.5,
                    "nms_threshold": 0.45
                }
            )
        ]
    
    @property
    def pipeline_config(self) -> Dict:
        return {
            "type": "sequential",
            "roi_check": True  # 启用ROI检查
        }
    
    @property
    def alert_detector(self) -> AlertDetector:
        return IntrusionAlertDetector()
    
    def process_results(self, results: List[Dict]) -> Dict:
        """处理入侵检测结果，添加ROI信息"""
        processed_result = {
            "skill_name": self.name,
            "detections": []
        }
        
        for result in results:
            for detection in result.get("detections", []):
                # 检查检测框是否在受限区域内
                detection["attributes"]["in_restricted_area"] = self._check_roi(
                    detection["bbox"]
                )
                processed_result["detections"].append(detection)
        
        return processed_result
    
    def _check_roi(self, bbox: Dict) -> bool:
        """检查边界框是否在受限区域内"""
        # 这里需要实现具体的ROI检查逻辑
        # 可以通过配置文件或其他方式定义受限区域
        return True  # 示例实现 