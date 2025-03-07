from typing import Dict, List, Optional
import kserve
from kubernetes import client, config
from core.skills import BaseSkill, available_skills

class SkillManager:
    def __init__(self):
        self._skills: Dict[str, BaseSkill] = {}
        self._init_kserve_client()
        self._register_available_skills()
    
    def _init_kserve_client(self):
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()
        
        self.k8s_client = client.CustomObjectsApi()
    
    def _register_available_skills(self):
        """注册所有可用的技能"""
        for skill_name, skill in available_skills.items():
            self._skills[skill_name] = skill
    
    def register_skill(self, skill: BaseSkill):
        """注册新技能"""
        self._skills[skill.name] = skill
    
    def get_skill(self, skill_name: str) -> Optional[BaseSkill]:
        """获取技能配置"""
        return self._skills.get(skill_name)
    
    def list_skills(self) -> List[str]:
        """列出所有可用技能"""
        return list(self._skills.keys())
    
    async def invoke_skill(self, skill_name: str, input_data: Dict) -> Dict:
        """调用技能进行推理"""
        skill = self.get_skill(skill_name)
        if not skill:
            raise ValueError(f"Skill {skill_name} not found")
        
        pipeline_config = skill.pipeline_config
        pipeline_type = pipeline_config.get("type", "sequential")
        
        if pipeline_type == "sequential":
            # 顺序执行所有模型
            results = []
            current_input = input_data
            
            for model in skill.models:
                # 调用KServe推理服务
                kserve_client = kserve.KServeClient()
                response = await kserve_client.predict(
                    name=model.name,
                    data=current_input,
                    version=model.version
                )
                results.append(response)
                
                # 如果模型输出需要作为下一个模型的输入，在这里处理
                if "output_as_input" in pipeline_config:
                    current_input = self._process_intermediate_result(response)
            
            return skill.process_results(results)
            
        elif pipeline_type == "cascade":
            # 级联处理，每个模型的输出会影响下一个模型的输入
            results = []
            intermediate_data = {}
            
            for step in pipeline_config["steps"]:
                model_name = step["model"]
                model = next(m for m in skill.models if m.name == model_name)
                
                # 准备输入数据
                if "input" in step and step["input"] in intermediate_data:
                    current_input = self._prepare_cascade_input(
                        input_data,
                        intermediate_data[step["input"]],
                        model
                    )
                else:
                    current_input = input_data
                
                # 调用KServe推理服务
                kserve_client = kserve.KServeClient()
                response = await kserve_client.predict(
                    name=model.name,
                    data=current_input,
                    version=model.version
                )
                results.append(response)
                
                # 保存中间结果
                if "output" in step:
                    intermediate_data[step["output"]] = response
            
            return skill.process_results(results)
            
        elif pipeline_type == "parallel":
            # 并行执行所有模型
            import asyncio
            
            async def call_model(model):
                kserve_client = kserve.KServeClient()
                return await kserve_client.predict(
                    name=model.name,
                    data=input_data,
                    version=model.version
                )
            
            # 并行调用所有模型
            results = await asyncio.gather(
                *(call_model(model) for model in skill.models)
            )
            
            return skill.process_results(list(results))
        
        else:
            raise ValueError(f"Unsupported pipeline type: {pipeline_type}")
    
    def _process_intermediate_result(self, result: Dict) -> Dict:
        """处理中间结果，准备作为下一个模型的输入"""
        # 这里可以添加通用的中间结果处理逻辑
        return result
    
    def _prepare_cascade_input(
        self,
        original_input: Dict,
        previous_output: Dict,
        next_model: BaseSkill
    ) -> Dict:
        """准备级联处理的输入数据"""
        # 根据模型的预处理配置准备输入
        input_data = original_input.copy()
        input_data.update({
            "previous_output": previous_output,
            "model_config": next_model.preprocessing_config
        })
        return input_data
    
    def check_alert(self, skill_name: str, detections: List[Dict], alert_level: str) -> bool:
        """检查是否需要报警
        
        Args:
            skill_name: 技能名称
            detections: 检测结果
            alert_level: 报警等级
            
        Returns:
            bool: 是否需要报警
        """
        skill = self.get_skill(skill_name)
        if not skill:
            raise ValueError(f"Skill {skill_name} not found")
            
        return skill.alert_detector.is_alert(detections, alert_level)

# 全局技能管理器实例
skill_manager = SkillManager() 