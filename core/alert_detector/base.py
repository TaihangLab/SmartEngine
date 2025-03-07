from abc import ABC, abstractmethod
from typing import Dict, List

class AlertDetector(ABC):
    """异常检测器基类"""
    
    @abstractmethod
    def is_alert(self, detections: List[Dict], alert_level: str) -> bool:
        """判断检测结果是否需要报警
        
        Args:
            detections: 检测结果列表
            alert_level: 报警等级
            
        Returns:
            bool: 是否需要报警
        """
        pass 