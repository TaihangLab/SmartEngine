import asyncio
import logging
from logging.config import dictConfig
from pythonjsonlogger import jsonlogger

from service.vision_service import serve
from config.config import settings

# 配置日志
logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': jsonlogger.JsonFormatter,
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
            'stream': 'ext://sys.stdout'
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO'
        }
    }
}

dictConfig(logging_config)
logger = logging.getLogger(__name__)

async def main():
    try:
        # 启动gRPC服务器
        server = serve()
        await server.start()
        
        logger.info(
            "Vision AI Engine started",
            extra={
                "port": settings.GRPC_PORT,
                "workers": settings.GRPC_MAX_WORKERS
            }
        )
        
        # 等待服务器终止
        await server.wait_for_termination()
        
    except Exception as e:
        logger.error(
            "Error starting Vision AI Engine",
            extra={"error": str(e)}
        )
        raise

if __name__ == "__main__":
    asyncio.run(main()) 