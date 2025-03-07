import cv2
import asyncio
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
import io

from core.skill_manager import skill_manager
from core.storage_manager import storage_manager
from core.message_queue import message_queue
from config.config import settings

class VideoProcessor:
    def __init__(self):
        self.active_streams = {}
        self.frame_buffer = {}  # 用于存储视频帧的缓冲区
    
    async def process_stream(
        self,
        stream_url: str,
        skill_name: str,
        alert_level: str,
        frame_interval: int = None,
        roi: List[str] = None,
        schedule: str = None
    ):
        """处理视频流"""
        stream_id = f"{stream_url}_{skill_name}"
        
        if stream_id in self.active_streams:
            raise ValueError(f"Stream {stream_url} is already being processed")
        
        # 初始化帧缓冲区
        self.frame_buffer[stream_id] = []
        
        # 创建处理任务
        task = asyncio.create_task(
            self._process_stream_task(
                stream_id,
                stream_url,
                skill_name,
                alert_level,
                frame_interval or settings.DEFAULT_FRAME_INTERVAL,
                roi,
                schedule
            )
        )
        
        self.active_streams[stream_id] = task
        return stream_id
    
    async def stop_stream(self, stream_id: str):
        """停止视频流处理"""
        if stream_id in self.active_streams:
            self.active_streams[stream_id].cancel()
            del self.active_streams[stream_id]
            if stream_id in self.frame_buffer:
                del self.frame_buffer[stream_id]
    
    async def _process_stream_task(
        self,
        stream_id: str,
        stream_url: str,
        skill_name: str,
        alert_level: str,
        frame_interval: int,
        roi: Optional[List[str]],
        schedule: Optional[str]
    ):
        """视频流处理任务"""
        cap = cv2.VideoCapture(stream_url)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video stream: {stream_url}")
        
        try:
            frame_count = 0
            last_process_time = 0
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                
                # 更新帧缓冲区
                self.frame_buffer[stream_id].append(frame)
                # 保持缓冲区大小为fps * VIDEO_CHUNK_DURATION
                max_buffer_size = fps * settings.VIDEO_CHUNK_DURATION
                if len(self.frame_buffer[stream_id]) > max_buffer_size:
                    self.frame_buffer[stream_id].pop(0)
                
                # 按照指定间隔处理帧
                if current_time - last_process_time >= frame_interval:
                    # 处理当前帧
                    await self._process_frame(
                        frame,
                        stream_id,
                        skill_name,
                        alert_level,
                        roi,
                        fps
                    )
                    last_process_time = current_time
                
                frame_count += 1
                
                # 检查是否应该继续处理（基于调度）
                if schedule and not self._should_process(schedule):
                    await asyncio.sleep(60)  # 休眠1分钟后再检查
                    continue
                
                await asyncio.sleep(0.1)  # 避免CPU过载
                
        except asyncio.CancelledError:
            pass
        finally:
            cap.release()
            if stream_id in self.active_streams:
                del self.active_streams[stream_id]
            if stream_id in self.frame_buffer:
                del self.frame_buffer[stream_id]
    
    async def _process_frame(
        self,
        frame: np.ndarray,
        stream_id: str,
        skill_name: str,
        alert_level: str,
        roi: Optional[List[str]],
        fps: int
    ):
        """处理单个视频帧"""
        # 转换frame为bytes
        _, buffer = cv2.imencode('.jpg', frame)
        image_bytes = buffer.tobytes()
        
        # 调用技能进行检测
        result = await skill_manager.invoke_skill(
            skill_name,
            {"image": image_bytes}
        )
        
        # 检查是否需要报警
        if result.get("detections") and skill_manager.check_alert(
            skill_name,
            result["detections"],
            alert_level
        ):
            # 保存预警图片
            image_path = await storage_manager.save_image(
                image_bytes,
                f"video_alert/{stream_id}"
            )
            
            # 保存视频片段
            video_path = await self._save_video_chunk(
                stream_id,
                fps,
                f"video_alert/{stream_id}"
            )
            
            # 构建结果消息
            message = {
                "id": f"{stream_id}_{datetime.now().timestamp()}",
                "stream_id": stream_id,
                "skill_name": skill_name,
                "alert_level": alert_level,
                "timestamp": datetime.now().timestamp(),
                "image_url": storage_manager.get_object_url(image_path),
                "video_url": storage_manager.get_object_url(video_path),
                "detections": result["detections"]
            }
            
            # 发送到消息队列
            await message_queue.send_detection_result(message)
    
    async def _save_video_chunk(self, stream_id: str, fps: int, alert_type: str) -> str:
        """保存视频片段"""
        if stream_id not in self.frame_buffer or not self.frame_buffer[stream_id]:
            return None
            
        # 获取视频帧
        frames = self.frame_buffer[stream_id]
        
        # 创建临时视频文件
        temp_path = f"temp_{stream_id}.mp4"
        height, width = frames[0].shape[:2]
        
        # 创建视频写入器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_path, fourcc, fps, (width, height))
        
        try:
            # 写入帧
            for frame in frames:
                out.write(frame)
            
            # 释放视频写入器
            out.release()
            
            # 读取临时文件
            with open(temp_path, 'rb') as f:
                video_data = f.read()
            
            # 删除临时文件
            import os
            os.remove(temp_path)
            
            # 保存到MinIO
            return await storage_manager.save_video(video_data, alert_type)
            
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e
    
    def _should_process(self, schedule: str) -> bool:
        """检查当前时间是否在处理调度范围内"""
        if not schedule:
            return True
            
        # 简单的时间范围检查实现
        # 格式: "HH:MM-HH:MM"
        try:
            current_time = datetime.now().time()
            start_time, end_time = schedule.split('-')
            start_hour, start_minute = map(int, start_time.split(':'))
            end_hour, end_minute = map(int, end_time.split(':'))
            
            start = datetime.now().replace(
                hour=start_hour,
                minute=start_minute
            ).time()
            end = datetime.now().replace(
                hour=end_hour,
                minute=end_minute
            ).time()
            
            return start <= current_time <= end
            
        except:
            return True  # 如果解析失败，默认总是处理

# 全局视频处理器实例
video_processor = VideoProcessor() 