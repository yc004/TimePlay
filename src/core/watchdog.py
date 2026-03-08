"""播出安全看门狗模块"""
import time
import threading
from datetime import datetime
from src.utils.logger import Logger
from config.config import SAFETY_CONFIG

class Watchdog:
    def __init__(self, player, schedule_system):
        self.player = player
        self.schedule_system = schedule_system
        self.logger = Logger()
        self.is_running = False
        self.last_heartbeat = time.time()
        self.thread = None
        
    def start(self):
        """启动看门狗"""
        if not SAFETY_CONFIG['enable_watchdog']:
            return
            
        self.is_running = True
        self.thread = threading.Thread(target=self._monitor, daemon=True)
        self.thread.start()
        self.logger.info("播出安全看门狗已启动")
    
    def stop(self):
        """停止看门狗"""
        self.is_running = False
        if self.thread:
            self.thread.join()
    
    def heartbeat(self):
        """更新心跳"""
        self.last_heartbeat = time.time()
    
    def _monitor(self):
        """监控播放状态"""
        check_interval = SAFETY_CONFIG['check_interval']
        
        while self.is_running:
            try:
                # 检查心跳
                if SAFETY_CONFIG['enable_heartbeat']:
                    if time.time() - self.last_heartbeat > check_interval * 2:
                        self.logger.warning("系统心跳异常，尝试恢复...")
                        self._recover()
                
                # 检查播放状态
                if not self._check_playback():
                    self.logger.warning("播放异常，启动备用内容...")
                    self._play_backup()
                
                time.sleep(check_interval)
                
            except Exception as e:
                self.logger.error(f"看门狗监控异常: {e}")
    
    def _check_playback(self):
        """检查播放状态"""
        # 检查是否有窗口在播放
        if self.player.current_window is None:
            return True  # 可能是空闲时段
        
        # 检查VLC播放器状态
        if self.player.vlc_player and self.player.vlc_player.is_playing():
            return True
        
        return False
    
    def _recover(self):
        """恢复系统"""
        try:
            self.logger.info("正在恢复系统...")
            self.player.stop_current()
            self.last_heartbeat = time.time()
        except Exception as e:
            self.logger.error(f"系统恢复失败: {e}")
    
    def _play_backup(self):
        """播放备用内容"""
        try:
            backup_file = SAFETY_CONFIG['backup_content']
            self.logger.info(f"播放备用内容: {backup_file}")
            self.player.play_video(backup_file, fullscreen=True, topmost=True)
        except Exception as e:
            self.logger.error(f"播放备用内容失败: {e}")
