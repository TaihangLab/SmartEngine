from typing import Dict, List
from abc import ABC, abstractmethod
from pydantic import BaseModel
from core.alert_detector import AlertDetector

class Model(BaseModel):
    name: str
    version: str
    endpoint: str
    input_shape: List[int]
    preprocessing_config: Dict
    postprocessing_config: Dict

class BaseSkill(ABC):
    """技能基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """技能名称"""
        pass
    
    @property
    @abstractmethod
    def models(self) -> List[Model]:
        """技能使用的模型列表"""
        pass
    
    @property
    @abstractmethod
    def pipeline_config(self) -> Dict:
        """技能的处理管线配置"""
        pass
    
    @property
    @abstractmethod
    def alert_detector(self) -> AlertDetector:
        """技能的异常检测器"""
        pass
    
    def process_results(self, results: List[Dict]) -> Dict:
        """处理模型推理结果
        
        Args:
            results: 模型推理结果列表
            
        Returns:
            Dict: 处理后的结果
        """
        processed_result = {
            "skill_name": self.name,
            "detections": []
        }
        
        # 默认实现：合并所有检测结果
        for result in results:
            if "detections" in result:
                processed_result["detections"].extend(result["detections"])
        
        return processed_result 