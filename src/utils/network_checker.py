"""网络连接检查模块"""
import requests
import threading
import time
from src.utils.logger import Logger
from config.config import NETWORK_CONFIG

class NetworkChecker:
    def __init__(self):
        self.logger = Logger()
        self.is_connected = True
        self.check_thread = None
        self.running = False
        
    def start(self):
        """启动网络检查"""
        self.running = True
        self.check_thread = threading.Thread(target=self._check_loop, daemon=True)
        self.check_thread.start()
        self.logger.info("网络检查已启动")
    
    def stop(self):
        """停止网络检查"""
        self.running = False
        if self.check_thread:
            self.check_thread.join()
    
    def _check_loop(self):
        """检查循环"""
        while self.running:
            self.is_connected = self.check_connection()
            if not self.is_connected:
                self.logger.warning("网络连接异常")
            time.sleep(30)  # 每30秒检查一次
    
    def check_connection(self, url="https://www.baidu.com", timeout=5):
        """检查网络连接"""
        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except:
            return False
    
    def is_online(self):
        """获取网络状态"""
        return self.is_connected
