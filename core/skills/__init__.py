from typing import Dict
from core.skills.base import BaseSkill
from core.skills.person_detection import PersonDetectionSkill
from core.skills.vehicle_detection import VehicleDetectionSkill
from core.skills.fire_smoke_detection import FireSmokeDetectionSkill
from core.skills.intrusion_detection import IntrusionDetectionSkill
from core.skills.crowd_density import CrowdDensitySkill
from core.skills.abnormal_behavior import AbnormalBehaviorSkill

# 技能注册表
available_skills: Dict[str, BaseSkill] = {
    "person_detection": PersonDetectionSkill(),
    "vehicle_detection": VehicleDetectionSkill(),
    "fire_smoke_detection": FireSmokeDetectionSkill(),
    "intrusion_detection": IntrusionDetectionSkill(),
    "crowd_density": CrowdDensitySkill(),
    "abnormal_behavior": AbnormalBehaviorSkill()
} 