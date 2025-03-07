from typing import Dict, List
from core.alert_detector.base import AlertDetector

class VehicleAlertDetector(AlertDetector):
    """车辆检测异常检测器"""
    
    def __init__(self, speed_threshold: float = 60.0):
        self.speed_threshold = speed_threshold
    
    def is_alert(self, detections: List[Dict], alert_level: str) -> bool:
        # 示例：当检测到超速车辆时触发报警
        for detection in detections:
            if detection["class_name"] == "vehicle":
                speed = float(detection["attributes"].get("speed", 0))
                if speed > self.speed_threshold:
                    return True
        return False 