"""显示设置界面"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QComboBox, QSpinBox,
                             QGroupBox, QRadioButton, QButtonGroup, QMessageBox,
                             QFrame, QApplication)
from PyQt5.QtCore import Qt, QRect, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen
from src.utils.display_config import DisplayConfig
from src.core.player import MediaPlayer

class ScreenPreview(QWidget):
    """显示器预览组件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.screens = []
        self.selected_screen = 0
        self.custom_rect = None
        self.setMinimumSize(600, 400)
        
    def set_screens(self, screens):
        """设置显示器列表"""
        self.screens = screens
        self.update()
    
    def set_selected_screen(self, index):
        """设置选中的显示器"""
        self.selected_screen = index
        self.update()
    
    def set_custom_rect(self, rect):
        """设置自定义矩形"""
        self.custom_rect = rect
        self.update()
    
    def paintEvent(self, event):
        """绘制预览"""
        if not self.screens:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 计算缩放比例
        min_x = min(s['x'] for s in self.screens)
        min_y = min(s['y'] for s in self.screens)
        max_x = max(s['x'] + s['width'] for s in self.screens)
        max_y = max(s['y'] + s['height'] for s in self.screens)
        
        total_width = max_x - min_x
        total_height = max_y - min_y
        
        scale_x = (self.width() - 40) / total_width if total_width > 0 else 1
        scale_y = (self.height() - 40) / total_height if total_height > 0 else 1
        scale = min(scale_x, scale_y)
        
        # 绘制每个显示器
        for i, screen in enumerate(self.screens):
            x = int((screen['x'] - min_x) * scale) + 20
            y = int((screen['y'] - min_y) * scale) + 20
            w = int(screen['width'] * scale)
            h = int(screen['height'] * scale)
            
            # 选中的显示器高亮
            if i == self.selected_screen:
                painter.setPen(QPen(QColor(0, 120, 215), 3))
                painter.setBrush(QColor(0, 120, 215, 50))
            else:
                painter.setPen(QPen(QColor(100, 100, 100), 2))
                painter.setBrush(QColor(200, 200, 200, 100))
            
            painter.drawRect(x, y, w, h)
            
            # 绘制显示器信息
            painter.setPen(QColor(0, 0, 0))
            info_text = f"显示器 {i + 1}"
            if screen.get('is_primary'):
                info_text += " (主)"
            painter.drawText(x + 5, y + 20, info_text)
            painter.drawText(x + 5, y + 40, f"{screen['width']}x{screen['height']}")
        
        # 绘制自定义矩形
        if self.custom_rect:
            cx, cy, cw, ch = self.custom_rect
            x = int((cx - min_x) * scale) + 20
            y = int((cy - min_y) * scale) + 20
            w = int(cw * scale)
            h = int(ch * scale)
            
            painter.setPen(QPen(QColor(255, 0, 0), 2, Qt.DashLine))
            painter.setBrush(QColor(255, 0, 0, 30))
            painter.drawRect(x, y, w, h)


class DisplaySettingsWindow(QMainWindow):
    """显示设置窗口"""
    def __init__(self):
        super().__init__()
        self.display_config = DisplayConfig()
        self.screens = self.display_config.get_available_screens()
        self.preview_window = None
        self.init_ui()
        self.load_current_config()
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("显示设置")
        self.setGeometry(100, 100, 800, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 标题
        title = QLabel("显示器配置")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # 显示器信息
        info_group = QGroupBox("可用显示器")
        info_layout = QVBoxLayout(info_group)
        
        for screen in self.screens:
            info_text = f"显示器 {screen['index'] + 1}: {screen['name']} - "
            info_text += f"{screen['width']}x{screen['height']} "
            info_text += f"位置({screen['x']}, {screen['y']})"
            if screen['is_primary']:
                info_text += " [主显示器]"
            
            label = QLabel(info_text)
            info_layout.addWidget(label)
        
        layout.addWidget(info_group)
        
        # 显示模式选择
        mode_group = QGroupBox("显示模式")
        mode_layout = QVBoxLayout(mode_group)
        
        self.mode_group = QButtonGroup()
        
        self.radio_fullscreen = QRadioButton("全屏模式")
        self.radio_fullscreen.toggled.connect(self.on_mode_changed)
        self.mode_group.addButton(self.radio_fullscreen, 0)
        mode_layout.addWidget(self.radio_fullscreen)
        
        self.radio_custom = QRadioButton("自定义窗口")
        self.radio_custom.toggled.connect(self.on_mode_changed)
        self.mode_group.addButton(self.radio_custom, 1)
        mode_layout.addWidget(self.radio_custom)
        
        layout.addWidget(mode_group)
        
        # 显示器选择（全屏模式）
        self.screen_group = QGroupBox("选择显示器")
        screen_layout = QHBoxLayout(self.screen_group)
        screen_layout.addWidget(QLabel("显示器:"))
        
        self.screen_combo = QComboBox()
        for screen in self.screens:
            text = f"显示器 {screen['index'] + 1} - {screen['width']}x{screen['height']}"
            if screen['is_primary']:
                text += " (主)"
            self.screen_combo.addItem(text, screen['index'])
        self.screen_combo.currentIndexChanged.connect(self.on_screen_changed)
        screen_layout.addWidget(self.screen_combo)
        screen_layout.addStretch()
        
        layout.addWidget(self.screen_group)
        
        # 自定义窗口设置
        self.custom_group = QGroupBox("自定义窗口位置和大小")
        custom_layout = QVBoxLayout(self.custom_group)
        
        # 位置
        pos_layout = QHBoxLayout()
        pos_layout.addWidget(QLabel("X:"))
        self.spin_x = QSpinBox()
        self.spin_x.setRange(-10000, 10000)
        self.spin_x.valueChanged.connect(self.on_custom_changed)
        pos_layout.addWidget(self.spin_x)
        
        pos_layout.addWidget(QLabel("Y:"))
        self.spin_y = QSpinBox()
        self.spin_y.setRange(-10000, 10000)
        self.spin_y.valueChanged.connect(self.on_custom_changed)
        pos_layout.addWidget(self.spin_y)
        pos_layout.addStretch()
        custom_layout.addLayout(pos_layout)
        
        # 大小
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("宽度:"))
        self.spin_width = QSpinBox()
        self.spin_width.setRange(100, 10000)
        self.spin_width.setValue(1920)
        self.spin_width.valueChanged.connect(self.on_custom_changed)
        size_layout.addWidget(self.spin_width)
        
        size_layout.addWidget(QLabel("高度:"))
        self.spin_height = QSpinBox()
        self.spin_height.setRange(100, 10000)
        self.spin_height.setValue(1080)
        self.spin_height.valueChanged.connect(self.on_custom_changed)
        size_layout.addWidget(self.spin_height)
        size_layout.addStretch()
        custom_layout.addLayout(size_layout)
        
        layout.addWidget(self.custom_group)
        
        # 预览区域
        preview_group = QGroupBox("显示器布局预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview = ScreenPreview()
        self.preview.set_screens(self.screens)
        preview_layout.addWidget(self.preview)
        
        layout.addWidget(preview_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        self.btn_test = QPushButton("测试显示")
        self.btn_test.clicked.connect(self.test_display)
        button_layout.addWidget(self.btn_test)
        
        self.btn_save = QPushButton("保存配置")
        self.btn_save.clicked.connect(self.save_config)
        self.btn_save.setStyleSheet("background-color: #4CAF50; color: white;")
        button_layout.addWidget(self.btn_save)
        
        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self.close)
        button_layout.addWidget(self.btn_cancel)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # 状态栏
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        layout.addWidget(self.status_label)
    
    def load_current_config(self):
        """加载当前配置"""
        config = self.display_config.config
        
        # 显示模式
        mode = config.get('display_mode', 'fullscreen')
        if mode == 'fullscreen':
            self.radio_fullscreen.setChecked(True)
        else:
            self.radio_custom.setChecked(True)
        
        # 显示器索引
        screen_index = config.get('screen_index', 0)
        self.screen_combo.setCurrentIndex(screen_index)
        
        # 自定义窗口
        geometry = config.get('window_geometry', {})
        self.spin_x.setValue(geometry.get('x', 0))
        self.spin_y.setValue(geometry.get('y', 0))
        self.spin_width.setValue(geometry.get('width', 1920))
        self.spin_height.setValue(geometry.get('height', 1080))
        
        self.update_preview()
    
    def on_mode_changed(self):
        """模式改变"""
        is_fullscreen = self.radio_fullscreen.isChecked()
        self.screen_group.setEnabled(is_fullscreen)
        self.custom_group.setEnabled(not is_fullscreen)
        self.update_preview()
    
    def on_screen_changed(self):
        """显示器改变"""
        self.update_preview()
    
    def on_custom_changed(self):
        """自定义设置改变"""
        self.update_preview()
    
    def update_preview(self):
        """更新预览"""
        if self.radio_fullscreen.isChecked():
            screen_index = self.screen_combo.currentData()
            self.preview.set_selected_screen(screen_index)
            self.preview.set_custom_rect(None)
        else:
            self.preview.set_selected_screen(-1)
            x = self.spin_x.value()
            y = self.spin_y.value()
            w = self.spin_width.value()
            h = self.spin_height.value()
            self.preview.set_custom_rect((x, y, w, h))
    
    def test_display(self):
        """测试显示"""
        try:
            # 获取当前配置
            if self.radio_fullscreen.isChecked():
                mode = 'fullscreen'
                screen_index = self.screen_combo.currentData()
                screen = self.display_config.get_screen_by_index(screen_index)
                if not screen:
                    QMessageBox.warning(self, "错误", "无法获取显示器信息")
                    return
                geometry = screen.geometry()
                x, y, w, h = geometry.x(), geometry.y(), geometry.width(), geometry.height()
            else:
                mode = 'custom'
                x = self.spin_x.value()
                y = self.spin_y.value()
                w = self.spin_width.value()
                h = self.spin_height.value()
            
            # 创建测试窗口
            self.preview_window = QWidget()
            self.preview_window.setWindowTitle("显示测试 - 5秒后自动关闭")
            self.preview_window.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
            self.preview_window.setGeometry(x, y, w, h)
            self.preview_window.setStyleSheet("background-color: black;")
            
            # 添加测试信息
            label = QLabel(self.preview_window)
            label.setText(f"显示测试\n\n模式: {mode}\n位置: ({x}, {y})\n大小: {w}x{h}\n\n5秒后自动关闭")
            label.setStyleSheet("color: white; font-size: 24px;")
            label.setAlignment(Qt.AlignCenter)
            label.setGeometry(0, 0, w, h)
            
            self.preview_window.show()
            
            # 5秒后自动关闭
            QTimer.singleShot(5000, self.close_preview)
            
            self.status_label.setText("正在测试显示...")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"测试显示失败: {e}")
    
    def close_preview(self):
        """关闭预览窗口"""
        if self.preview_window:
            self.preview_window.close()
            self.preview_window = None
        self.status_label.setText("测试完成")
    
    def save_config(self):
        """保存配置"""
        try:
            if self.radio_fullscreen.isChecked():
                self.display_config.set_display_mode('fullscreen')
                screen_index = self.screen_combo.currentData()
                self.display_config.set_screen_index(screen_index)
            else:
                self.display_config.set_display_mode('custom')
                x = self.spin_x.value()
                y = self.spin_y.value()
                w = self.spin_width.value()
                h = self.spin_height.value()
                self.display_config.set_window_geometry(x, y, w, h)
            
            QMessageBox.information(self, "成功", "显示配置已保存\n重启系统后生效")
            self.status_label.setText("配置已保存")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DisplaySettingsWindow()
    window.show()
    sys.exit(app.exec_())
