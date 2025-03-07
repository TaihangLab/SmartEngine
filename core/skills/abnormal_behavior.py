from typing import Dict, List
from core.skills.base import BaseSkill, Model
from core.alert_detector import AlertDetector, AbnormalBehaviorAlertDetector

class AbnormalBehaviorSkill(BaseSkill):
    """异常行为检测技能"""
    
    @property
    def name(self) -> str:
        return "abnormal_behavior"
    
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
            ),
            Model(
                name="behavior_classifier",
                version="v1",
                endpoint="behavior-classifier-predictor",
                input_shape=[224, 224, 3],
                preprocessing_config={
                    "resize_mode": "crop",
                    "sequence_length": 16  # 行为分类需要时序信息
                },
                postprocessing_config={
                    "confidence_threshold": 0.7
                }
            )
        ]
    
    @property
    def pipeline_config(self) -> Dict:
        return {
            "type": "cascade",
            "steps": [
                {"model": "yolov5", "output": "persons"},
                {"model": "behavior_classifier", "input": "persons", "output": "behaviors"}
            ]
        }
    
    @property
    def alert_detector(self) -> AlertDetector:
        return AbnormalBehaviorAlertDetector()
    
    def process_results(self, results: List[Dict]) -> Dict:
        """处理异常行为检测结果"""
        if len(results) != 2:
            raise ValueError("Abnormal behavior detection requires both person detection and behavior classification results")
        
        detection_result = results[0]
        behavior_result = results[1]
        
        processed_result = {
            "skill_name": self.name,
            "detections": []
        }
        
        # 将行为信息添加到检测结果中
        for detection in detection_result.get("detections", []):
            person_id = detection.get("id")
            if person_id in behavior_result:
                detection["attributes"]["behavior"] = behavior_result[person_id]["behavior"]
                detection["attributes"]["behavior_confidence"] = behavior_result[person_id]["confidence"]
            processed_result["detections"].append(detection)
        
        return processed_result 