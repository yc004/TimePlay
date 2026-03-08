"""UI配置管理器"""
import json
import os

class UIConfig:
    """UI配置管理类"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化配置"""
        if self._config is None:
            self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            config_path = os.path.join(
                os.path.dirname(__file__), 
                '../../config/ui_config.json'
            )
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        except Exception as e:
            print(f"加载UI配置失败: {e}")
            self._config = self._get_default_config()
    
    def reload_config(self):
        """重新加载配置（用于调试）"""
        self._config = None
        self.load_config()
    
    def _get_default_config(self):
        """获取默认配置"""
        return {
            "calendar_view": {
                "fonts": {
                    "weekday_header": {"size": 20, "weight": "bold", "color": "white"},
                    "task_name": {"size": 20, "weight": "bold", "color": "#1976D2"},
                    "time_display": {"size": 16, "weight": "bold", "color": "#555"},
                    "time_label": {"size": 18, "weight": "bold", "color": "#1976D2"},
                    "playlist_content": {"size": 15, "weight": "normal", "color": "#444"},
                    "empty_cell": {"size": 32, "color": "#BDBDBD"}
                },
                "layout": {
                    "grid_spacing": 2,
                    "task_block_padding": 12,
                    "task_block_spacing": 10,
                    "content_line_height": 1.8,
                    "time_column_min_width": 90,
                    "time_column_max_width": 110,
                    "header_min_height": 45,
                    "header_max_height": 55,
                    "cell_min_height": 80
                },
                "colors": {
                    "playlist_bg": "#E8F5E9",
                    "playlist_border": "#4CAF50",
                    "video_bg": "#FFF9C4",
                    "video_border": "#FBC02D",
                    "web_bg": "#E1F5FE",
                    "web_border": "#03A9F4",
                    "empty_cell_bg": "#FAFAFA",
                    "empty_cell_border": "#E0E0E0",
                    "header_bg": "#2196F3",
                    "header_border": "#1976D2",
                    "corner_bg": "#1976D2",
                    "corner_border": "#0D47A1",
                    "time_label_bg": "#E3F2FD",
                    "time_label_border": "#BBDEFB"
                },
                "content": {
                    "max_playlist_items": 5,
                    "filename_max_length": 20,
                    "show_icons": True,
                    "icons": {
                        "video": "🎬",
                        "image": "🖼️",
                        "web": "🌐",
                        "unknown": "📄"
                    }
                }
            }
        }
    
    # 便捷访问方法
    
    def get_calendar_font(self, element):
        """获取课程表字体配置"""
        return self._config.get('calendar_view', {}).get('fonts', {}).get(element, {})
    
    def get_calendar_layout(self, key):
        """获取课程表布局配置"""
        return self._config.get('calendar_view', {}).get('layout', {}).get(key)
    
    def get_calendar_color(self, key):
        """获取课程表颜色配置"""
        return self._config.get('calendar_view', {}).get('colors', {}).get(key)
    
    def get_calendar_content(self, key):
        """获取课程表内容配置"""
        return self._config.get('calendar_view', {}).get('content', {}).get(key)
    
    def get_time_indicator(self, key):
        """获取时间指示线配置"""
        return self._config.get('calendar_view', {}).get('time_indicator', {}).get(key)
    
    def is_time_indicator_enabled(self):
        """检查时间指示线是否启用"""
        return self._config.get('calendar_view', {}).get('time_indicator', {}).get('enabled', True)
    
    def get_icon(self, media_type):
        """获取媒体类型图标"""
        icons = self._config.get('calendar_view', {}).get('content', {}).get('icons', {})
        return icons.get(media_type, icons.get('unknown', '📄'))
    
    # 样式生成方法
    
    def get_font_style(self, element):
        """生成字体样式字符串"""
        font = self.get_calendar_font(element)
        style_parts = []
        
        if 'size' in font:
            style_parts.append(f"font-size: {font['size']}px")
        if 'weight' in font:
            style_parts.append(f"font-weight: {font['weight']}")
        if 'color' in font:
            style_parts.append(f"color: {font['color']}")
        
        return "; ".join(style_parts)
    
    def get_task_block_style(self, task_type):
        """生成任务块样式"""
        bg_key = f"{task_type}_bg"
        border_key = f"{task_type}_border"
        
        bg_color = self.get_calendar_color(bg_key)
        border_color = self.get_calendar_color(border_key)
        
        return f"""
            QFrame {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 5px;
            }}
        """
    
    def get_header_style(self):
        """生成表头样式"""
        font = self.get_calendar_font('weekday_header')
        bg = self.get_calendar_color('header_bg')
        border = self.get_calendar_color('header_border')
        
        return f"""
            background-color: {bg};
            color: {font.get('color', 'white')};
            font-weight: {font.get('weight', 'bold')};
            font-size: {font.get('size', 20)}px;
            border: 1px solid {border};
        """
    
    def get_time_label_style(self):
        """生成时间标签样式"""
        font = self.get_calendar_font('time_label')
        bg = self.get_calendar_color('time_label_bg')
        border = self.get_calendar_color('time_label_border')
        
        return f"""
            background-color: {bg};
            color: {font.get('color', '#1976D2')};
            font-weight: {font.get('weight', 'bold')};
            font-size: {font.get('size', 18)}px;
            border: 1px solid {border};
        """
    
    def get_empty_cell_style(self):
        """生成空白单元格样式"""
        bg = self.get_calendar_color('empty_cell_bg')
        border = self.get_calendar_color('empty_cell_border')
        
        return f"""
            QFrame {{
                background-color: {bg};
                border: 1px solid {border};
            }}
        """


# 全局配置实例
ui_config = UIConfig()
