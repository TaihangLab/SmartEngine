from typing import Dict, List
from core.skills.base import BaseSkill, Model
from core.alert_detector import AlertDetector, PersonAlertDetector

class PersonDetectionSkill(BaseSkill):
    """人员检测技能"""
    
    @property
    def name(self) -> str:
        return "person_detection"
    
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
            "type": "sequential"
        }
    
    @property
    def alert_detector(self) -> AlertDetector:
        return PersonAlertDetector() 