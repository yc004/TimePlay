"""使用Selenium播放器启动系统"""
import os
import sys
import signal
import atexit

# 应用白屏修复
os.environ['QTWEBENGINE_DISABLE_SANDBOX'] = '1'
os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--disable-gpu --no-sandbox'

# 添加src目录到路径
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
        
        # 关键: 启用Selenium播放器和空闲窗口
        self.player = MediaPlayer(use_selenium=True, show_idle_window=True)
        
        self.logger = Logger()
        self.scheduler = EnhancedScheduler(self.player)
        self.watchdog = None
        self.heartbeat_timer = None
        
        # 注册信号处理器和退出处理器
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        atexit.register(self.shutdown)
        
        self.logger.info("=" * 60)
        self.logger.info("电视播放系统 - Selenium版")
        self.logger.info("=" * 60)
        self.logger.info("✓ 使用Selenium播放器 (绕过反爬虫检测)")
        self.logger.info("✓ 启用空闲黑屏窗口")
        self.logger.info("=" * 60)
    
    def _signal_handler(self, signum, frame):
        """处理终止信号"""
        self.logger.info(f"收到信号 {signum}，正在关闭系统...")
        self.shutdown()
        sys.exit(0)
    
    def run(self):
        """运行系统"""
        if not self.scheduler.load_schedules():
            self.logger.error("加载时间表失败，系统退出")
            return
        
        self.scheduler.start()
        self.watchdog = Watchdog(self.player, self.scheduler)
        self.watchdog.start()
        
        self.heartbeat_timer = QTimer()
        self.heartbeat_timer.timeout.connect(self.on_heartbeat)
        self.heartbeat_timer.start(1000)
        
        self.logger.info("系统启动成功，等待定时任务...")
        
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
    print("\n" + "=" * 60)
    print("电视播放系统 - Selenium版")
    print("=" * 60)
    print()
    print("特性:")
    print("  ✓ 使用Selenium + ChromeDriver")
    print("  ✓ 绕过反爬虫检测")
    print("  ✓ 模拟真实浏览器")
    print("  ✓ 支持所有网页直播")
    print()
    print("要求:")
    print("  • Chrome浏览器")
    print("  • ChromeDriver (自动管理)")
    print("  • Selenium (pip install selenium)")
    print("  • webdriver-manager (pip install webdriver-manager)")
    print()
    print("如果遇到问题，请运行: python install_chromedriver.py")
    print()
    print("=" * 60)
    print()
    
    system = TVScheduleSystem()
    system.run()
