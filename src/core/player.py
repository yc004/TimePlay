import vlc
import time
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QLabel
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import QPixmap
from src.utils.display_config import DisplayConfig
from src.core.browser_player import BrowserPlayer
from src.core.idle_window import IdleWindow
from src.utils.logger import Logger
import sys
import os

class MediaPlayer:
    def __init__(self, use_selenium=True, show_idle_window=True):
        """
        初始化媒体播放器
        
        Args:
            use_selenium: 是否使用Selenium播放器（推荐，可绕过反爬虫）
            show_idle_window: 是否在空闲时显示黑屏窗口
        """
        self.current_window = None
        self.vlc_instance = vlc.Instance('--no-xlib')
        self.vlc_player = self.vlc_instance.media_player_new()
        self.timer = None
        self.display_config = DisplayConfig()
        self.logger = Logger()
        self.use_selenium = use_selenium
        self.selenium_player = None  # Selenium播放器实例
        self.show_idle_window = show_idle_window
        self.idle_window = None  # 空闲窗口实例
        
        # 循环播放相关
        self.loop_enabled = False  # 是否启用循环
        self.current_video_path = None  # 当前播放的视频路径
        self.current_video_params = None  # 当前视频的播放参数
        
        # 如果启用空闲窗口，立即创建并显示
        if self.show_idle_window:
            self._create_idle_window()
            self._show_idle_window()
        
    def play_video(self, video_path, fullscreen=True, topmost=True, duration=0, loop=False):
        """
        播放视频文件
        
        Args:
            video_path: 视频文件路径
            fullscreen: 是否全屏
            topmost: 是否置顶
            duration: 播放时长（秒），0表示不限制
            loop: 是否循环播放
        """
        self._hide_idle_window()
        self.stop_current(show_idle=False)
        
        # 保存循环播放参数
        self.loop_enabled = loop
        self.current_video_path = video_path
        self.current_video_params = {
            'fullscreen': fullscreen,
            'topmost': topmost,
            'duration': duration,
            'loop': loop
        }
        
        self.logger.info(f"播放视频: {video_path}, 循环: {loop}")
        
        # 创建并配置播放窗口
        self.current_window = self._create_window("视频播放", topmost, fullscreen)
        
        # 设置VLC播放器
        if sys.platform.startswith('win'):
            self.vlc_player.set_hwnd(int(self.current_window.winId()))
        
        # 加载并播放媒体
        media = self.vlc_instance.media_new(video_path)
        self.vlc_player.set_media(media)
        
        # 设置循环播放
        if loop:
            # 监听播放结束事件
            event_manager = self.vlc_player.event_manager()
            event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self._on_video_end)
            self.logger.info("已启用循环播放监听")
        
        self.vlc_player.play()
        
        # 设置定时停止
        self._set_timer(duration)
    
    def _on_video_end(self, event):
        """
        视频播放结束回调
        
        Args:
            event: VLC事件对象
        """
        if self.loop_enabled and self.current_video_path:
            self.logger.info("视频播放结束，准备循环播放")
            
            # 使用QTimer在主线程中重新播放
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(100, self._restart_video)
        else:
            self.logger.info("视频播放结束")
    
    def _restart_video(self):
        """重新开始播放视频（在主线程中调用）"""
        if not self.loop_enabled or not self.current_video_path:
            return
        
        try:
            self.logger.info("重新开始循环播放")
            
            # 停止当前播放
            self.vlc_player.stop()
            
            # 重新加载并播放媒体
            media = self.vlc_instance.media_new(self.current_video_path)
            self.vlc_player.set_media(media)
            
            # 重新附加事件监听器
            event_manager = self.vlc_player.event_manager()
            event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self._on_video_end)
            
            # 播放
            self.vlc_player.play()
            self.logger.info("循环播放已重新开始")
        except Exception as e:
            self.logger.error(f"循环播放失败: {e}")
    
    def play_image(self, image_path, fullscreen=True, topmost=True, duration=5):
        """
        播放图片
        
        Args:
            image_path: 图片文件路径
            fullscreen: 是否全屏
            topmost: 是否置顶
            duration: 显示时长（秒），默认5秒
        """
        self._hide_idle_window()
        self.stop_current(show_idle=False)
        
        self.logger.info(f"显示图片: {image_path}, 时长: {duration}秒")
        
        # 创建并配置显示窗口
        self.current_window = self._create_window("图片显示", topmost, fullscreen)
        
        # 创建图片标签
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setStyleSheet("background-color: black;")
        
        # 加载图片
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            # 根据窗口大小缩放图片
            geometry = self.display_config.get_display_geometry()
            scaled_pixmap = pixmap.scaled(
                geometry['width'], 
                geometry['height'], 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            image_label.setPixmap(scaled_pixmap)
        else:
            self.logger.error(f"无法加载图片: {image_path}")
            image_label.setText("图片加载失败")
            image_label.setStyleSheet("color: white; background-color: black; font-size: 24px;")
        
        # 设置布局
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(image_label)
        self.current_window.setLayout(layout)
        
        # 设置定时停止
        self._set_timer(duration)
    
    @staticmethod
    def get_video_duration(video_path):
        """
        获取视频时长（秒）
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            int: 视频时长（秒），失败返回0
        """
        try:
            # 创建临时VLC实例
            instance = vlc.Instance('--no-xlib')
            media = instance.media_new(video_path)
            media.parse()
            
            # 等待解析完成
            timeout = 5  # 5秒超时
            start_time = time.time()
            while time.time() - start_time < timeout:
                if media.get_duration() > 0:
                    duration_ms = media.get_duration()
                    duration_sec = duration_ms / 1000
                    return int(duration_sec)
                time.sleep(0.1)
            
            # 如果parse失败，尝试使用播放器
            player = instance.media_player_new()
            player.set_media(media)
            player.play()
            time.sleep(0.5)
            
            duration_ms = media.get_duration()
            player.stop()
            
            if duration_ms > 0:
                duration_sec = duration_ms / 1000
                return int(duration_sec)
            
            return 0
        except Exception as e:
            Logger().error(f"获取视频时长失败: {e}")
            return 0
    
    @staticmethod
    def get_media_type(file_path):
        """
        判断媒体文件类型
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 'video', 'image', 'web', 或 'unknown'
        """
        if not file_path:
            return 'unknown'
        
        # 检查是否是URL
        if file_path.startswith('http://') or file_path.startswith('https://'):
            return 'web'
        
        # 检查文件扩展名
        ext = os.path.splitext(file_path)[1].lower()
        
        video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg']
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.svg']
        
        if ext in video_extensions:
            return 'video'
        elif ext in image_extensions:
            return 'image'
        else:
            return 'unknown'
    
    def play_web_stream(self, url, fullscreen=True, topmost=True, duration=0):
        """播放网页直播流"""
        # 隐藏空闲窗口
        self._hide_idle_window()
        
        # 关闭当前播放（不重新显示空闲窗口）
        self.stop_current(show_idle=False)
        
        # 判断URL类型
        if self._is_direct_stream_url(url):
            # 直接是流URL（m3u8等），使用VLC播放
            self._play_stream_with_vlc(url, fullscreen, topmost, duration)
        else:
            # 网页URL，根据配置选择播放器
            if self.use_selenium:
                self._play_with_selenium(url, fullscreen, topmost, duration)
            else:
                self._play_with_browser(url, fullscreen, topmost, duration)
    
    def _is_direct_stream_url(self, url):
        """判断是否是直接的流URL"""
        # 只有明确的流格式才用VLC，其他都用浏览器
        stream_extensions = ['.m3u8', '.flv', '.ts']
        url_lower = url.lower()
        
        # 检查是否包含流扩展名
        has_extension = any(ext in url_lower for ext in stream_extensions)
        
        # 检查是否是rtmp协议
        is_rtmp = url_lower.startswith('rtmp://')
        
        # 检查是否明确是流URL（不是网页）
        is_not_webpage = not any(x in url_lower for x in ['http://', 'https://']) or has_extension
        
        return (has_extension or is_rtmp) and ('cctv.com' not in url_lower or has_extension)
    
    def _play_stream_with_vlc(self, url, fullscreen, topmost, duration):
        """使用VLC播放直播流"""
        self.logger.info(f"使用VLC播放流: {url}")
        
        # 创建并配置播放窗口
        self.current_window = self._create_window("直播播放", topmost, fullscreen)
        
        # 设置VLC播放器
        if sys.platform.startswith('win'):
            self.vlc_player.set_hwnd(int(self.current_window.winId()))
        
        # 加载并播放媒体
        media = self.vlc_instance.media_new(url)
        media.add_option(':network-caching=1000')
        media.add_option(':http-user-agent=Mozilla/5.0')
        self.vlc_player.set_media(media)
        self.vlc_player.play()
        
        # 设置定时停止
        self._set_timer(duration)
    
    def _play_with_browser(self, url, fullscreen, topmost, duration):
        """使用浏览器播放器播放"""
        self.logger.info(f"使用浏览器播放: {url}")
        
        # 创建并配置播放窗口
        self.current_window = self._create_window("直播播放", topmost, fullscreen)
        
        # 创建布局并添加浏览器播放器
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(BrowserPlayer(url))
        self.current_window.setLayout(layout)
        
        # 设置定时停止
        self._set_timer(duration)
    
    def _play_with_selenium(self, url, fullscreen, topmost, duration):
        """使用Selenium播放器播放"""
        self.logger.info(f"使用Selenium播放: {url}")
        
        try:
            # 导入Selenium播放器（优先使用自动管理版）
            try:
                from src.core.selenium_player_auto import SeleniumPlayerAuto
                PlayerClass = SeleniumPlayerAuto
            except ImportError:
                from src.core.selenium_player import SeleniumPlayer
                PlayerClass = SeleniumPlayer
            
            # 获取显示配置
            geometry = self.display_config.get_display_geometry()
            
            # 直接使用schedule中的fullscreen参数
            # fullscreen=True: 使用Kiosk全屏模式
            # fullscreen=False: 使用App模式，按display_config大小显示
            self.logger.info(f"播放参数 - 全屏: {fullscreen}")
            
            # 创建播放器
            self.selenium_player = PlayerClass(
                url=url,
                fullscreen=fullscreen,  # 直接使用schedule的fullscreen参数
                position=(geometry['x'], geometry['y']),
                size=(geometry['width'], geometry['height'])
            )
            
            # 启动播放器
            if not self.selenium_player.start():
                raise Exception("Selenium播放器启动失败")
            
            # 设置定时停止
            self._set_timer(duration)
            
        except Exception as e:
            self.logger.error(f"Selenium播放器错误: {e}")
            self.logger.info("回退到浏览器播放器")
            if self.selenium_player:
                try:
                    self.selenium_player.stop()
                except:
                    pass
                self.selenium_player = None
            self._play_with_browser(url, fullscreen, topmost, duration)
    
    def _apply_display_config(self, use_fullscreen):
        """应用显示配置"""
        geometry = self.display_config.get_display_geometry()
        display_mode = self.display_config.config.get('display_mode', 'fullscreen')
        
        # 设置窗口位置和大小
        self.current_window.setGeometry(
            geometry['x'],
            geometry['y'],
            geometry['width'],
            geometry['height']
        )
        
        # 根据配置决定是否全屏
        if display_mode == 'fullscreen' and use_fullscreen:
            self.current_window.showFullScreen()
        else:
            self.current_window.show()
    
    def _create_window(self, title, topmost, fullscreen):
        """创建并配置播放窗口"""
        window = QWidget()
        window.setWindowTitle(title)
        
        # 设置窗口属性
        flags = Qt.FramelessWindowHint
        if topmost:
            flags |= Qt.WindowStaysOnTopHint
        window.setWindowFlags(flags)
        
        # 应用显示配置
        geometry = self.display_config.get_display_geometry()
        display_mode = self.display_config.config.get('display_mode', 'fullscreen')
        
        window.setGeometry(geometry['x'], geometry['y'], geometry['width'], geometry['height'])
        
        if display_mode == 'fullscreen' and fullscreen:
            window.showFullScreen()
        else:
            window.show()
        
        return window
    
    def _set_timer(self, duration):
        """设置定时停止"""
        if duration > 0:
            self.timer = QTimer()
            self.timer.timeout.connect(self.stop_current)
            self.timer.start(duration * 1000)
    
    def stop_current(self, show_idle=True):
        """
        停止当前播放
        
        Args:
            show_idle: 是否显示空闲窗口（默认True）
        """
        if self.timer:
            self.timer.stop()
            self.timer = None
        
        # 停止Selenium播放器
        if self.selenium_player:
            self.selenium_player.stop()
            self.selenium_player = None
        
        # 清理循环播放状态
        if self.loop_enabled:
            try:
                # 分离事件监听器
                event_manager = self.vlc_player.event_manager()
                event_manager.event_detach(vlc.EventType.MediaPlayerEndReached)
                self.logger.info("已移除循环播放监听")
            except Exception as e:
                self.logger.error(f"移除事件监听器失败: {e}")
        
        self.loop_enabled = False
        self.current_video_path = None
        self.current_video_params = None
            
        if self.vlc_player.is_playing():
            self.vlc_player.stop()
            
        if self.current_window:
            self.current_window.close()
            self.current_window = None
        
        # 根据参数决定是否显示空闲窗口
        if show_idle:
            self._show_idle_window()
    
    def _create_idle_window(self):
        """创建空闲窗口"""
        if not self.idle_window:
            self.idle_window = IdleWindow(self.display_config)
            self.logger.info("空闲窗口已创建")
    
    def _show_idle_window(self):
        """显示空闲窗口"""
        if self.show_idle_window and self.idle_window:
            self.idle_window.show_window()
    
    def _hide_idle_window(self):
        """隐藏空闲窗口"""
        if self.idle_window:
            self.idle_window.hide_window()
    
    def cleanup(self):
        """清理所有资源"""
        self.stop_current()
        if self.idle_window:
            self.idle_window.cleanup()
            self.idle_window = None
