from typing import Dict, List
from core.skills.base import BaseSkill, Model
from core.alert_detector import AlertDetector, FireSmokeAlertDetector

class FireSmokeDetectionSkill(BaseSkill):
    """火灾烟雾检测技能"""
    
    @property
    def name(self) -> str:
        return "fire_smoke_detection"
    
    @property
    def models(self) -> List[Model]:
        return [
            Model(
                name="fire_smoke_detector",
                version="v1",
                endpoint="fire-smoke-predictor",
                input_shape=[416, 416, 3],
                preprocessing_config={
                    "resize_mode": "letterbox"
                },
                postprocessing_config={
                    "confidence_threshold": 0.6,
                    "nms_threshold": 0.5
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
        return FireSmokeAlertDetector() 