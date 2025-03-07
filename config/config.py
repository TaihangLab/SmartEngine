from pydantic import BaseSettings

class Settings(BaseSettings):
    # RocketMQ配置
    ROCKETMQ_NAME_SERVER: str = "localhost:9876"
    ROCKETMQ_GROUP_ID: str = "vision_engine_group"
    ROCKETMQ_TOPIC: str = "vision_results"
    
    # MinIO配置
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "vision-alerts"
    MINIO_SECURE: bool = False
    
    # KServe配置
    KSERVE_NAMESPACE: str = "kserve-models"
    
    # gRPC服务配置
    GRPC_PORT: int = 50051
    GRPC_MAX_WORKERS: int = 10
    
    # 视频处理配置
    DEFAULT_FRAME_INTERVAL: int = 1  # 默认抽帧间隔（秒）
    VIDEO_CHUNK_DURATION: int = 10   # 视频片段持续时间（秒）
    
    # 存储配置
    ALERT_RETENTION_DAYS: int = 30   # 预警数据保留天数
    
    class Config:
        env_file = ".env"

settings = Settings() 