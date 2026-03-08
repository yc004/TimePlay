"""紧急插播功能模块"""
import json
import os
from datetime import datetime
from src.utils.logger import Logger

class EmergencyBroadcast:
    def __init__(self, player):
        self.player = player
        self.logger = Logger()
        self.emergency_file = 'emergency.json'
        
    def trigger(self, content_type, content_path, duration=0, message=""):
        """触发紧急插播"""
        try:
            self.logger.warning(f"紧急插播触发: {message}")
            
            # 记录紧急插播信息
            self._log_emergency(content_type, content_path, message)
            
            # 停止当前播放
            self.player.stop_current()
            
            # 播放紧急内容
            if content_type == 'video':
                self.player.play_video(content_path, fullscreen=True, topmost=True, duration=duration)
            elif content_type == 'web':
                self.player.play_web_stream(content_path, fullscreen=True, topmost=True, duration=duration)
            
            self.logger.info("紧急插播已启动")
            return True
            
        except Exception as e:
            self.logger.error(f"紧急插播失败: {e}")
            return False
    
    def _log_emergency(self, content_type, content_path, message):
        """记录紧急插播日志"""
        log_entry = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': content_type,
            'content': content_path,
            'message': message
        }
        
        # 读取现有日志
        logs = []
        if os.path.exists(self.emergency_file):
            try:
                with open(self.emergency_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                pass
        
        # 添加新日志
        logs.append(log_entry)
        
        # 保存日志（保留最近100条）
        with open(self.emergency_file, 'w', encoding='utf-8') as f:
            json.dump(logs[-100:], f, ensure_ascii=False, indent=2)
    
    def get_history(self, limit=10):
        """获取紧急插播历史"""
        if not os.path.exists(self.emergency_file):
            return []
        
        try:
            with open(self.emergency_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
                return logs[-limit:]
        except:
            return []
