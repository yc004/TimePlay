import sys
import os
import signal
import atexit

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from core.player import MediaPlayer
from utils.logger import Logger
from core.watchdog import Watchdog
from core.scheduler import EnhancedScheduler

class TVScheduleSystem:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.player = MediaPlayer(show_idle_window=True)  # 启用空闲窗口
        self.logger = Logger()
        self.scheduler = EnhancedScheduler(self.player)
        self.watchdog = None
        self.heartbeat_timer = None
        
        # 注册信号处理器和退出处理器
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        atexit.register(self.shutdown)
    
    def _signal_handler(self, signum, frame):
        """处理终止信号"""
        self.logger.info(f"收到信号 {signum}，正在关闭系统...")
        self.shutdown()
        sys.exit(0)
    
    def run(self):
        """运行系统"""
        # 加载时间表
        if not self.scheduler.load_schedules():
            self.logger.error("加载时间表失败，系统退出")
            return
        
        # 启动调度器
        self.scheduler.start()
        
        # 启动看门狗
        self.watchdog = Watchdog(self.player, self.scheduler)
        self.watchdog.start()
        
        # 设置心跳定时器（每秒触发一次）
        self.heartbeat_timer = QTimer()
        self.heartbeat_timer.timeout.connect(self.on_heartbeat)
        self.heartbeat_timer.start(1000)  # 1秒
        
        self.logger.info("系统启动成功，等待定时任务...")
        
        # 启动Qt事件循环
        try:
            sys.exit(self.app.exec_())
        except KeyboardInterrupt:
            self.shutdown()
    
    def on_heartbeat(self):
        """心跳回调"""
        if self.watchdog:
            self.watchdog.heartbeat()
    
    def shutdown(self):
        """关闭系统"""
        self.logger.info("系统正在关闭...")
        
        if self.heartbeat_timer:
            self.heartbeat_timer.stop()
        
        self.scheduler.stop()
        
        if self.watchdog:
            self.watchdog.stop()
        
        self.player.cleanup()  # 使用cleanup而不是stop_current
        self.logger.info("✓ 系统已关闭")

if __name__ == '__main__':
    system = TVScheduleSystem()
    system.run()
