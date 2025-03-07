from typing import Dict
from core.alert_detector.base import AlertDetector
from core.alert_detector.person import PersonAlertDetector
from core.alert_detector.vehicle import VehicleAlertDetector
from core.alert_detector.fire_smoke import FireSmokeAlertDetector
from core.alert_detector.intrusion import IntrusionAlertDetector
from core.alert_detector.crowd_density import CrowdDensityAlertDetector
from core.alert_detector.abnormal_behavior import AbnormalBehaviorAlertDetector

# 异常检测器注册表
alert_detectors: Dict[str, AlertDetector] = {
    "person_detection": PersonAlertDetector(),
    "vehicle_detection": VehicleAlertDetector(),
    "fire_smoke_detection": FireSmokeAlertDetector(),
    "intrusion_detection": IntrusionAlertDetector(),
    "crowd_density": CrowdDensityAlertDetector(),
    "abnormal_behavior": AbnormalBehaviorAlertDetector()
} 