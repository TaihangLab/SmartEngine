from typing import Dict, List
from core.alert_detector.base import AlertDetector

class AbnormalBehaviorAlertDetector(AlertDetector):
    """异常行为检测器"""
    
    def __init__(self):
        # 定义异常行为类型及其对应的警报等级
        self.behavior_alert_levels = {
            "fighting": "high",
            "falling": "high",
            "running": "medium",
            "loitering": "low"
        }
    
    def is_alert(self, detections: List[Dict], alert_level: str) -> bool:
        alert_level = alert_level.lower()
        alert_level_scores = {"high": 3, "medium": 2, "low": 1}
        required_score = alert_level_scores.get(alert_level, 2)
        
        for detection in detections:
            if "behavior" in detection["attributes"]:
                behavior = detection["attributes"]["behavior"]
                behavior_level = self.behavior_alert_levels.get(behavior, "low")
                behavior_score = alert_level_scores.get(behavior_level, 1)
                
                if behavior_score >= required_score:
                    return True
        
        return False 