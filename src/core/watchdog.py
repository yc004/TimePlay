"""播出安全看门狗模块"""
import time
import threading
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal
from src.utils.logger import Logger
from config.config import SAFETY_CONFIG

class Watchdog(QObject):
    # 定义信号用于在主线程中执行恢复操作
    recover_signal = pyqtSignal()
    
    def __init__(self, player, schedule_system):
        super().__init__()
        self.player = player
        self.schedule_system = schedule_system
        self.logger = Logger()
        self.is_running = False
        self.last_heartbeat = time.time()
        self.thread = None
        
        # 连接信号到恢复方法
        self.recover_signal.connect(self._do_recover)
        
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
                    self.logger.warning("播放异常，尝试恢复...")
                    self._recover()
                
                time.sleep(check_interval)
                
            except Exception as e:
                self.logger.error(f"看门狗监控异常: {e}")
                import traceback
                self.logger.error(traceback.format_exc())
                time.sleep(check_interval)  # 出错后也要等待，避免死循环
    
    def _check_playback(self):
        """检查播放状态"""
        try:
            # 获取当前应该播放的任务
            current_task = self.schedule_system.get_current_task()
            
            # 如果当前没有任务，不需要检查
            if not current_task:
                # 空闲时段，不检查播放状态
                # 注意：不在这里操作空闲窗口，避免线程问题
                return True
            
            # 如果有任务，检查是否有播放窗口或播放器在运行
            has_window = self.player.current_window is not None
            has_selenium = self.player.selenium_player is not None
            is_vlc_playing = self.player.vlc_player and self.player.vlc_player.is_playing()
            
            # 如果有任何播放活动，认为正常
            if has_window or has_selenium or is_vlc_playing:
                return True
            
            # 有任务但没有播放活动，说明播放异常
            self.logger.warning(f"检测到播放异常：当前应播放任务 '{current_task.get('name', '未知')}' 但没有播放活动")
            return False
            
        except Exception as e:
            self.logger.error(f"检查播放状态时出错: {e}")
            return True  # 出错时返回True，避免误触发恢复
    
    def _recover(self):
        """触发恢复（在看门狗线程中调用）"""
        # 使用信号在主线程中执行恢复操作
        self.recover_signal.emit()
    
    def _do_recover(self):
        """执行恢复操作（在主线程中调用）"""
        try:
            self.logger.info("正在恢复系统...")
            
            # 停止当前播放（如果有）
            self.player.stop_current(show_idle=False)
            
            # 获取当前应该播放的任务
            current_task = self.schedule_system.get_current_task()
            
            if current_task:
                # 重新启动当前任务
                self.logger.info(f"重新启动任务: {current_task.get('name', '未知')}")
                self.schedule_system.execute_task(current_task)
            else:
                # 没有任务，显示空闲窗口
                self.logger.info("当前无任务，显示空闲窗口")
                self.player._show_idle_window()
            
            self.last_heartbeat = time.time()
            self.logger.info("✓ 系统恢复完成")
            
        except Exception as e:
            self.logger.error(f"系统恢复失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    def _play_backup(self):
        """播放备用内容"""
        try:
            backup_file = SAFETY_CONFIG['backup_content']
            self.logger.info(f"播放备用内容: {backup_file}")
            self.player.play_video(backup_file, fullscreen=True, topmost=True)
        except Exception as e:
            self.logger.error(f"播放备用内容失败: {e}")
