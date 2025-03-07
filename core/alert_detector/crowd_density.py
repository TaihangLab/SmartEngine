from typing import Dict, List
from core.alert_detector.base import AlertDetector

class CrowdDensityAlertDetector(AlertDetector):
    """人流密度异常检测器"""
    
    def __init__(self, density_threshold: Dict[str, int] = None):
        self.density_threshold = density_threshold or {
            "high": 20,    # 高密度阈值
            "medium": 10,  # 中密度阈值
            "low": 5      # 低密度阈值
        }
    
    def is_alert(self, detections: List[Dict], alert_level: str) -> bool:
        # 统计检测到的人数
        person_count = sum(1 for d in detections if d["class_name"] == "person")
        
        # 根据报警等级判断是否超过阈值
        threshold = self.density_threshold.get(
            alert_level.lower(),
            self.density_threshold["medium"]
        )
        
        return person_count >= threshold 