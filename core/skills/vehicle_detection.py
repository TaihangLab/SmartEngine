from typing import Dict, List
from core.skills.base import BaseSkill, Model
from core.alert_detector import AlertDetector, VehicleAlertDetector

class VehicleDetectionSkill(BaseSkill):
    """车辆检测技能"""
    
    @property
    def name(self) -> str:
        return "vehicle_detection"
    
    @property
    def models(self) -> List[Model]:
        return [
            Model(
                name="yolov5",
                version="v1",
                endpoint="vehicle-detection-predictor",
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
            ),
            Model(
                name="vehicle_speed",
                version="v1",
                endpoint="vehicle-speed-predictor",
                input_shape=[224, 224, 3],
                preprocessing_config={
                    "resize_mode": "crop"
                },
                postprocessing_config={
                    "min_speed": 0.0
                }
            )
        ]
    
    @property
    def pipeline_config(self) -> Dict:
        return {
            "type": "cascade",
            "steps": [
                {"model": "yolov5", "output": "vehicles"},
                {"model": "vehicle_speed", "input": "vehicles", "output": "speeds"}
            ]
        }
    
    @property
    def alert_detector(self) -> AlertDetector:
        return VehicleAlertDetector(speed_threshold=60.0)
    
    def process_results(self, results: List[Dict]) -> Dict:
        """处理车辆检测和速度估计结果"""
        if len(results) != 2:
            raise ValueError("Vehicle detection requires both detection and speed estimation results")
            
        detection_result = results[0]
        speed_result = results[1]
        
        processed_result = {
            "skill_name": self.name,
            "detections": []
        }
        
        # 将速度信息添加到检测结果中
        for detection in detection_result.get("detections", []):
            vehicle_id = detection.get("id")
            if vehicle_id in speed_result:
                detection["attributes"]["speed"] = speed_result[vehicle_id]["speed"]
            processed_result["detections"].append(detection)
        
        return processed_result 