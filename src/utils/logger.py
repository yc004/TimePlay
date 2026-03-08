import logging
from datetime import datetime
import os

class Logger:
    def __init__(self, log_dir='logs'):
        """初始化日志系统"""
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_file = os.path.join(
            log_dir, 
            f"tv_system_{datetime.now().strftime('%Y%m%d')}.log"
        )
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('TVSystem')
    
    def info(self, message):
        """记录信息"""
        self.logger.info(message)
    
    def error(self, message):
        """记录错误"""
        self.logger.error(message)
    
    def warning(self, message):
        """记录警告"""
        self.logger.warning(message)
