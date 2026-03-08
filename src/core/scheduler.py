"""增强的调度器模块 - 支持时间段、星期和轮播"""
import json
import threading
import time
from datetime import datetime, timedelta
from PyQt5.QtCore import QObject, pyqtSignal
from src.utils.logger import Logger

class EnhancedScheduler(QObject):
    # 定义信号用于在主线程中执行播放
    play_video_signal = pyqtSignal(str, bool, bool, int, bool)
    play_image_signal = pyqtSignal(str, bool, bool, int)  # 新增图片播放信号
    play_web_signal = pyqtSignal(str, bool, bool, int)
    stop_signal = pyqtSignal()
    
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.logger = Logger()
        self.schedules = []
        self.running = False
        self.thread = None
        self.current_schedule = None
        self.playlist_index = 0
        
        # 连接信号到播放器方法
        self.play_video_signal.connect(self.player.play_video)
        self.play_image_signal.connect(self.player.play_image)
        self.play_web_signal.connect(self.player.play_web_stream)
        self.stop_signal.connect(self.player.stop_current)
        
    def load_schedules(self):
        """加载播放时间表"""
        try:
            import os
            config_path = os.path.join(os.path.dirname(__file__), '../../config/schedule.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.schedules = data.get('schedules', [])
            self.logger.info(f"成功加载 {len(self.schedules)} 个播放任务")
            return True
        except Exception as e:
            self.logger.error(f"加载时间表失败: {e}")
            return False
    
    def start(self):
        """启动调度器"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._schedule_loop, daemon=True)
        self.thread.start()
        self.logger.info("调度器已启动")
    
    def stop(self):
        """停止调度器"""
        self.running = False
        if self.thread:
            self.thread.join()
        self.logger.info("调度器已停止")
    
    def _schedule_loop(self):
        """调度循环"""
        while self.running:
            try:
                now = datetime.now()
                current_time = now.strftime("%H:%M")
                current_weekday = now.isoweekday()  # 1=周一, 7=周日
                
                # 检查是否有需要执行的任务
                active_schedule = self._find_active_schedule(current_time, current_weekday)
                
                if active_schedule:
                    if self.current_schedule != active_schedule:
                        # 新任务开始
                        self.logger.info(f"开始执行任务: {active_schedule['name']}")
                        self.current_schedule = active_schedule
                        self.playlist_index = 0
                        self._execute_schedule(active_schedule)
                    elif active_schedule.get('type') == 'playlist':
                        # 检查轮播是否需要切换下一个
                        self._check_playlist_next(active_schedule)
                else:
                    if self.current_schedule:
                        # 当前任务结束
                        self.logger.info(f"任务结束: {self.current_schedule['name']}")
                        self.stop_signal.emit()
                        self.current_schedule = None
                        self.playlist_index = 0
                
                time.sleep(5)  # 每5秒检查一次
                
            except Exception as e:
                self.logger.error(f"调度循环异常: {e}")
                time.sleep(5)
    
    def _find_active_schedule(self, current_time, current_weekday):
        """查找当前应该执行的任务"""
        for schedule in self.schedules:
            if not schedule.get('enabled', True):
                continue
            
            # 检查星期
            weekdays = schedule.get('weekdays', [1, 2, 3, 4, 5, 6, 7])
            if current_weekday not in weekdays:
                continue
            
            # 检查时间段
            start_time = schedule.get('start_time')
            end_time = schedule.get('end_time')
            
            if self._is_time_in_range(current_time, start_time, end_time):
                return schedule
        
        return None
    
    def _is_time_in_range(self, current_time, start_time, end_time):
        """检查当前时间是否在指定时间段内"""
        try:
            current = datetime.strptime(current_time, "%H:%M")
            start = datetime.strptime(start_time, "%H:%M")
            end = datetime.strptime(end_time, "%H:%M")
            
            if end < start:
                # 跨越午夜的情况
                return current >= start or current < end
            else:
                return start <= current < end
        except:
            return False
    
    def _execute_schedule(self, schedule):
        """执行播放任务"""
        schedule_type = schedule.get('type')
        
        self.logger.info(f"执行任务类型: {schedule_type}")
        
        # 只支持播放列表类型
        if schedule_type == 'playlist':
            self._play_playlist(schedule)
        else:
            self.logger.warning(f"不支持的任务类型: {schedule_type}，请使用playlist类型")
    
    def _play_playlist(self, schedule):
        """播放轮播列表"""
        playlist = schedule.get('playlist', [])
        if not playlist:
            self.logger.warning("播放列表为空")
            return
        
        # 获取当前播放项
        if self.playlist_index >= len(playlist):
            if schedule.get('loop', True):
                self.playlist_index = 0
            else:
                self.logger.info("播放列表已完成")
                return
        
        item = playlist[self.playlist_index]
        fullscreen = schedule.get('fullscreen', True)
        topmost = schedule.get('topmost', True)
        
        # 获取媒体类型和路径
        item_type = item.get('type')
        path_or_url = item.get('path') or item.get('url')
        
        if not path_or_url:
            self.logger.error(f"播放项 {self.playlist_index + 1} 缺少路径或URL")
            self.playlist_index += 1
            self._play_playlist(schedule)
            return
        
        # 如果没有指定类型，自动检测
        if not item_type:
            item_type = self.player.get_media_type(path_or_url)
            self.logger.info(f"自动检测媒体类型: {item_type}")
        
        # 获取播放时长
        duration = item.get('duration', 0)
        
        # 如果是视频且没有指定时长，自动获取视频时长
        if item_type == 'video' and duration == 0:
            self.logger.info(f"正在获取视频时长: {path_or_url}")
            duration = self.player.get_video_duration(path_or_url)
            if duration > 0:
                self.logger.info(f"视频时长: {duration}秒")
            else:
                self.logger.warning("无法获取视频时长，使用默认值300秒")
                duration = 300
        
        # 如果是图片且没有指定时长，使用默认值
        if item_type == 'image' and duration == 0:
            duration = item.get('default_duration', 5)  # 默认5秒
            self.logger.info(f"图片使用默认时长: {duration}秒")
        
        # 获取循环参数
        loop = item.get('loop', False)
        
        self.logger.info(f"播放列表项 {self.playlist_index + 1}/{len(playlist)}")
        self.logger.info(f"类型: {item_type}, 路径: {path_or_url}, 时长: {duration}秒, 循环: {loop}")
        
        # 使用信号在主线程中播放
        if item_type == 'video':
            self.play_video_signal.emit(path_or_url, fullscreen, topmost, duration, loop)
        elif item_type == 'image':
            self.play_image_signal.emit(path_or_url, fullscreen, topmost, duration)
        elif item_type == 'web':
            self.play_web_signal.emit(path_or_url, fullscreen, topmost, duration)
        else:
            self.logger.error(f"不支持的媒体类型: {item_type}")
            self.playlist_index += 1
            self._play_playlist(schedule)
            return
        
        # 记录播放开始时间
        self.playlist_start_time = time.time()
        self.playlist_duration = duration
    
    def _check_playlist_next(self, schedule):
        """检查轮播是否需要切换到下一个"""
        if not hasattr(self, 'playlist_start_time'):
            return
        
        elapsed = time.time() - self.playlist_start_time
        
        if elapsed >= self.playlist_duration:
            # 切换到下一个
            self.playlist_index += 1
            playlist = schedule.get('playlist', [])
            
            if self.playlist_index >= len(playlist):
                if schedule.get('loop', True):
                    self.playlist_index = 0
                else:
                    self.stop_signal.emit()
                    return
            
            self._play_playlist(schedule)
    
    def _calculate_remaining_duration(self, schedule):
        """计算剩余播放时长"""
        try:
            now = datetime.now()
            end_time_str = schedule.get('end_time')
            end_time = datetime.strptime(end_time_str, "%H:%M")
            end_time = now.replace(hour=end_time.hour, minute=end_time.minute, second=0)
            
            if end_time < now:
                end_time += timedelta(days=1)
            
            remaining = (end_time - now).total_seconds()
            return int(remaining)
        except:
            return 0
