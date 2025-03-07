from typing import Dict, List
from core.alert_detector.base import AlertDetector

class FireSmokeAlertDetector(AlertDetector):
    """火灾烟雾检测异常检测器"""
    
    def is_alert(self, detections: List[Dict], alert_level: str) -> bool:
        # 示例：当检测到火灾或烟雾时触发报警
        alert_classes = {"fire", "smoke"}
        confidence_threshold = {
            "high": 0.7,
            "medium": 0.5,
            "low": 0.3
        }.get(alert_level.lower(), 0.5)
        
        return any(
            d["class_name"] in alert_classes and 
            d["confidence"] >= confidence_threshold 
            for d in detections
        ) 