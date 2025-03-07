# Vision AI Engine

智能视觉AI平台的引擎层，提供图像和视频流处理能力。

## 功能特性

- 支持单张图片检测
- 支持视频流实时检测
- 灵活的技能和模型管理
- 基于KServe的模型部署
- 使用RocketMQ进行消息传递
- 支持MinIO对象存储
- gRPC服务接口

## 系统要求

- Python 3.8+
- KServe
- RocketMQ
- MinIO

## 安装

1. 克隆代码仓库：

```bash
git clone <repository-url>
cd vision-ai-engine
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 配置环境变量：

创建 `.env` 文件并设置以下配置：

```env
ROCKETMQ_NAME_SERVER=localhost:9876
ROCKETMQ_GROUP_ID=vision_engine_group
ROCKETMQ_TOPIC=vision_results

MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=vision-alerts

KSERVE_NAMESPACE=kserve-models

GRPC_PORT=50051
GRPC_MAX_WORKERS=10
```

## 使用方法

1. 启动服务：

```bash
python main.py
```

2. 调用服务：

服务提供两个主要的gRPC接口：

- DetectImage：处理单张图片
- DetectVideoStream：处理视频流

可以使用gRPC客户端调用这些接口。

## 技能配置

技能配置示例：

```python
skill = Skill(
    name="person_detection",
    models=[
        Model(
            name="yolov5",
            version="v1",
            endpoint="person-detection-predictor",
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
        )
    ],
    pipeline_config={
        "type": "sequential"
    }
)

skill_manager.register_skill(skill)
```

## 项目结构

```
vision-ai-engine/
├── config/
│   └── config.py         # 配置管理
├── core/
│   ├── skill_manager.py  # 技能管理
│   ├── storage_manager.py # 存储管理
│   ├── message_queue.py  # 消息队列
│   └── video_processor.py # 视频处理
├── protos/
│   └── vision_service.proto # gRPC接口定义
├── service/
│   └── vision_service.py   # gRPC服务实现
├── main.py                 # 主程序入口
├── requirements.txt        # 项目依赖
└── README.md              # 项目文档
```

## 开发说明

1. 添加新技能：
   - 在 `skill_manager.py` 中注册新技能
   - 配置相关的模型和处理流程

2. 自定义处理流程：
   - 修改 `video_processor.py` 中的帧处理逻辑
   - 在 `skill_manager.py` 中添加新的处理管线

3. 调整存储策略：
   - 在 `storage_manager.py` 中修改存储规则
   - 配置对象生命周期管理

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交变更
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License 