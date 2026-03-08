"""显示器配置模块"""
import json
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QScreen
from src.utils.logger import Logger

class DisplayConfig:
    def __init__(self):
        self.logger = Logger()
        self.config_file = 'display_config.json'
        self.config = self.load_config()
        
    def load_config(self):
        """加载显示配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"加载显示配置失败: {e}")
        
        # 默认配置
        return {
            'display_mode': 'fullscreen',  # fullscreen, windowed, custom
            'screen_index': 0,  # 主显示器索引
            'window_geometry': {
                'x': 0,
                'y': 0,
                'width': 1920,
                'height': 1080
            }
        }
    
    def save_config(self):
        """保存显示配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            self.logger.info("显示配置已保存")
            return True
        except Exception as e:
            self.logger.error(f"保存显示配置失败: {e}")
            return False
    
    def get_available_screens(self):
        """获取所有可用的显示器"""
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        
        screens = []
        for i, screen in enumerate(app.screens()):
            geometry = screen.geometry()
            screens.append({
                'index': i,
                'name': screen.name(),
                'x': geometry.x(),
                'y': geometry.y(),
                'width': geometry.width(),
                'height': geometry.height(),
                'is_primary': screen == app.primaryScreen()
            })
        
        return screens
    
    def get_screen_by_index(self, index):
        """根据索引获取显示器"""
        app = QApplication.instance()
        if not app:
            return None
        
        screens = app.screens()
        if 0 <= index < len(screens):
            return screens[index]
        return None
    
    def get_display_geometry(self):
        """获取当前配置的显示区域"""
        mode = self.config.get('display_mode', 'fullscreen')
        screen_index = self.config.get('screen_index', 0)
        
        if mode == 'fullscreen':
            # 全屏模式：使用指定显示器的完整区域
            screen = self.get_screen_by_index(screen_index)
            if screen:
                geometry = screen.geometry()
                return {
                    'x': geometry.x(),
                    'y': geometry.y(),
                    'width': geometry.width(),
                    'height': geometry.height()
                }
        elif mode == 'custom':
            # 自定义模式：使用配置的窗口位置和大小
            return self.config.get('window_geometry', {
                'x': 0, 'y': 0, 'width': 1920, 'height': 1080
            })
        
        # 默认返回主显示器
        app = QApplication.instance()
        if app:
            screen = app.primaryScreen()
            geometry = screen.geometry()
            return {
                'x': geometry.x(),
                'y': geometry.y(),
                'width': geometry.width(),
                'height': geometry.height()
            }
        
        return {'x': 0, 'y': 0, 'width': 1920, 'height': 1080}
    
    def set_display_mode(self, mode):
        """设置显示模式"""
        self.config['display_mode'] = mode
        self.save_config()
    
    def set_screen_index(self, index):
        """设置显示器索引"""
        self.config['screen_index'] = index
        self.save_config()
    
    def set_window_geometry(self, x, y, width, height):
        """设置窗口位置和大小"""
        self.config['window_geometry'] = {
            'x': x,
            'y': y,
            'width': width,
            'height': height
        }
        self.save_config()
