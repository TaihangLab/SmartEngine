from datetime import datetime
import os
from minio import Minio
from config.config import settings

class StorageManager:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        
        # 确保bucket存在
        if not self.client.bucket_exists(settings.MINIO_BUCKET):
            self.client.make_bucket(settings.MINIO_BUCKET)
            
        # 设置生命周期规则
        self._set_lifecycle_policy()
    
    def _set_lifecycle_policy(self):
        """设置对象存储生命周期策略"""
        config = {
            "Rules": [
                {
                    "ID": "expire_old_data",
                    "Status": "Enabled",
                    "Expiration": {
                        "Days": settings.ALERT_RETENTION_DAYS
                    }
                }
            ]
        }
        self.client.set_bucket_lifecycle(settings.MINIO_BUCKET, config)
    
    def _generate_object_path(self, alert_type: str) -> str:
        """生成对象存储路径"""
        now = datetime.now()
        return f"{alert_type}/{now.year}/{now.month:02d}/{now.day:02d}/{now.timestamp()}"
    
    async def save_image(self, image_data: bytes, alert_type: str = "image") -> str:
        """保存图片数据"""
        object_path = f"{self._generate_object_path(alert_type)}.jpg"
        
        # 上传图片
        self.client.put_object(
            bucket_name=settings.MINIO_BUCKET,
            object_name=object_path,
            data=image_data,
            length=len(image_data),
            content_type="image/jpeg"
        )
        
        return object_path
    
    async def save_video(self, video_data: bytes, alert_type: str = "video") -> str:
        """保存视频数据"""
        object_path = f"{self._generate_object_path(alert_type)}.mp4"
        
        # 上传视频
        self.client.put_object(
            bucket_name=settings.MINIO_BUCKET,
            object_name=object_path,
            data=video_data,
            length=len(video_data),
            content_type="video/mp4"
        )
        
        return object_path
    
    def get_object_url(self, object_path: str) -> str:
        """获取对象的访问URL"""
        return self.client.presigned_get_object(
            bucket_name=settings.MINIO_BUCKET,
            object_name=object_path,
            expires=3600  # URL有效期1小时
        )

# 全局存储管理器实例
storage_manager = StorageManager() 