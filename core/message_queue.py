import json
from typing import Dict
from rocketmq.client import Producer, Message
from config.config import settings

class MessageQueue:
    def __init__(self):
        self.producer = Producer(settings.ROCKETMQ_GROUP_ID)
        self.producer.set_name_server_address(settings.ROCKETMQ_NAME_SERVER)
        self.producer.start()
    
    async def send_detection_result(self, result: Dict):
        """发送检测结果到消息队列"""
        try:
            # 将结果转换为JSON字符串
            message_body = json.dumps(result)
            
            # 创建消息
            msg = Message(settings.ROCKETMQ_TOPIC)
            msg.set_keys(result.get("id", ""))
            msg.set_tags(result.get("skill_name", ""))
            msg.set_body(message_body)
            
            # 发送消息
            self.producer.send_sync(msg)
            
        except Exception as e:
            # 这里应该添加proper logging
            print(f"Error sending message to RocketMQ: {str(e)}")
            raise
    
    def __del__(self):
        """确保在对象销毁时关闭producer"""
        if hasattr(self, 'producer'):
            self.producer.shutdown()

# 全局消息队列实例
message_queue = MessageQueue() 