"""空闲时显示的黑屏窗口"""
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from datetime import datetime
from src.utils.logger import Logger

class IdleWindow(QWidget):
    """空闲黑屏窗口"""
    
    def __init__(self, display_config=None):
        super().__init__()
        self.display_config = display_config
        self.logger = Logger()
        self.clock_timer = None
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        # 设置窗口属性
        self.setWindowTitle("校园闭路电视播放系统")
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        # 设置黑色背景
        self.setStyleSheet("background-color: #000000;")
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加时钟显示（可选）
        self.clock_label = QLabel()
        self.clock_label.setAlignment(Qt.AlignCenter)
        self.clock_label.setStyleSheet("""
            color: #333333;
            font-size: 48px;
            font-family: Arial;
            padding: 20px;
        """)
        layout.addStretch()
        layout.addWidget(self.clock_label)
        layout.addStretch()
        
        # 应用显示配置
        self._apply_display_config()
        
        # 启动时钟更新
        self.start_clock()
        
        self.logger.info("空闲窗口已创建")
    
    def _apply_display_config(self):
        """应用显示配置"""
        if self.display_config:
            geometry = self.display_config.get_display_geometry()
            display_mode = self.display_config.config.get('display_mode', 'fullscreen')
            
            # 设置窗口位置和大小
            self.setGeometry(
                geometry['x'],
                geometry['y'],
                geometry['width'],
                geometry['height']
            )
            
            # 保存显示模式，但不立即显示
            self.display_mode = display_mode
        else:
            # 没有配置，默认全屏
            self.display_mode = 'fullscreen'
    
    def show_window(self):
        """显示窗口"""
        # 根据显示模式显示窗口
        if hasattr(self, 'display_mode') and self.display_mode == 'fullscreen':
            self.logger.info(f"以全屏模式显示窗口")
            self.showFullScreen()
        else:
            self.logger.info(f"以窗口模式显示")
            self.show()
        
        # 强制窗口到最前面
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.raise_()
        self.activateWindow()
        
        # 在Windows上，使用额外的方法确保窗口显示
        import sys
        if sys.platform == 'win32':
            try:
                import ctypes
                hwnd = int(self.winId())
                ctypes.windll.user32.SetForegroundWindow(hwnd)
                ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                ctypes.windll.user32.SetFocus(hwnd)
            except Exception as e:
                self.logger.warning(f"Windows窗口激活失败: {e}")
        
        # 输出窗口信息
        self.logger.info(f"窗口几何: x={self.x()}, y={self.y()}, w={self.width()}, h={self.height()}")
        self.logger.info(f"窗口可见: {self.isVisible()}")
        self.logger.info(f"窗口激活: {self.isActiveWindow()}")
        self.logger.info("空闲窗口已显示")
    
    def start_clock(self):
        """启动时钟更新"""
        self.update_clock()
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)  # 每秒更新
    
    def update_clock(self):
        """更新时钟显示"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.clock_label.setText(current_time)
    
    def stop_clock(self):
        """停止时钟更新"""
        if self.clock_timer:
            self.clock_timer.stop()
            self.clock_timer = None
    
    def hide_window(self):
        """隐藏窗口"""
        self.hide()
        self.logger.info("空闲窗口已隐藏")
    
    def cleanup(self):
        """清理资源"""
        self.stop_clock()
        self.close()
        self.logger.info("空闲窗口已关闭")
