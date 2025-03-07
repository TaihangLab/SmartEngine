from typing import Dict, List
from core.alert_detector.base import AlertDetector

class PersonAlertDetector(AlertDetector):
    """人员检测异常检测器"""
    
    def is_alert(self, detections: List[Dict], alert_level: str) -> bool:
        # 示例：当检测到人员时触发报警
        return any(d["class_name"] == "person" for d in detections) 