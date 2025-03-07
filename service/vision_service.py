import grpc
import uuid
from concurrent import futures
from datetime import datetime

from core.skill_manager import skill_manager
from core.storage_manager import storage_manager
from core.message_queue import message_queue
from core.video_processor import video_processor
from config.config import settings

# 导入生成的gRPC代码
import vision_service_pb2
import vision_service_pb2_grpc

class VisionServiceServicer(vision_service_pb2_grpc.VisionServiceServicer):
    async def DetectImage(self, request, context):
        """处理单张图片检测请求"""
        try:
            # 生成请求ID
            request_id = str(uuid.uuid4())
            
            # 调用技能进行检测
            result = await skill_manager.invoke_skill(
                request.skill_name,
                {"image": request.image_data}
            )
            
            # 如果检测到目标，保存图片
            if result.get("detections"):
                image_path = await storage_manager.save_image(
                    request.image_data,
                    "image_alert"
                )
                
                # 构建结果消息
                message = {
                    "id": request_id,
                    "skill_name": request.skill_name,
                    "alert_level": request.alert_level,
                    "timestamp": datetime.now().timestamp(),
                    "image_url": storage_manager.get_object_url(image_path),
                    "detections": result["detections"]
                }
                
                # 发送到消息队列
                await message_queue.send_detection_result(message)
            
            return vision_service_pb2.DetectionResponse(
                request_id=request_id,
                status="success",
                message="Detection completed successfully"
            )
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return vision_service_pb2.DetectionResponse(
                request_id="",
                status="error",
                message=str(e)
            )
    
    async def DetectVideoStream(self, request, context):
        """处理视频流检测请求"""
        try:
            # 启动视频流处理
            stream_id = await video_processor.process_stream(
                stream_url=request.stream_url,
                skill_name=request.skill_name,
                alert_level=request.alert_level,
                frame_interval=request.frame_interval,
                roi=list(request.roi),
                schedule=request.schedule
            )
            
            return vision_service_pb2.DetectionResponse(
                request_id=stream_id,
                status="success",
                message="Video stream processing started"
            )
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return vision_service_pb2.DetectionResponse(
                request_id="",
                status="error",
                message=str(e)
            )

def serve():
    """启动gRPC服务器"""
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=settings.GRPC_MAX_WORKERS)
    )
    vision_service_pb2_grpc.add_VisionServiceServicer_to_server(
        VisionServiceServicer(), server
    )
    server.add_insecure_port(f'[::]:{settings.GRPC_PORT}')
    return server

if __name__ == '__main__':
    import asyncio
    
    async def main():
        server = serve()
        await server.start()
        print(f"Server started on port {settings.GRPC_PORT}")
        await server.wait_for_termination()
    
    asyncio.run(main()) 