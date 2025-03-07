from typing import Dict, List
from core.alert_detector.base import AlertDetector

class IntrusionAlertDetector(AlertDetector):
    """入侵检测异常检测器"""
    
    def is_alert(self, detections: List[Dict], alert_level: str) -> bool:
        # 示例：当在指定区域检测到人员时触发报警
        for detection in detections:
            if detection["class_name"] == "person":
                # 检查是否在禁区
                if detection["attributes"].get("in_restricted_area", False):
                    return True
        return False 