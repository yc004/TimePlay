"""系统启动器 - 集成所有功能"""
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QGroupBox,
                             QMessageBox)
from PyQt5.QtCore import Qt, QProcess
from PyQt5.QtGui import QFont, QIcon
import subprocess

class LauncherWindow(QMainWindow):
    """启动器主窗口"""
    def __init__(self):
        super().__init__()
        self.processes = {}
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("校园闭路电视播放系统 - 启动器")
        self.setGeometry(100, 100, 600, 500)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 标题
        title = QLabel("校园闭路电视播放系统")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("padding: 20px; color: #0078D4;")
        layout.addWidget(title)
        
        # 系统控制
        system_group = QGroupBox("系统控制")
        system_layout = QVBoxLayout(system_group)
        
        btn_start = QPushButton("启动播放系统")
        btn_start.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                padding: 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        btn_start.clicked.connect(self.start_system)
        system_layout.addWidget(btn_start)
        
        btn_stop = QPushButton("停止播放系统")
        btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 16px;
                padding: 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        btn_stop.clicked.connect(self.stop_system)
        system_layout.addWidget(btn_stop)
        
        layout.addWidget(system_group)
        
        # 配置工具
        config_group = QGroupBox("配置工具")
        config_layout = QVBoxLayout(config_group)
        
        btn_display = QPushButton("显示器配置")
        btn_display.setStyleSheet(self._get_button_style("#2196F3"))
        btn_display.clicked.connect(self.open_display_settings)
        config_layout.addWidget(btn_display)
        
        btn_schedule = QPushButton("播放时间表管理")
        btn_schedule.setStyleSheet(self._get_button_style("#2196F3"))
        btn_schedule.clicked.connect(self.open_schedule_manager)
        config_layout.addWidget(btn_schedule)
        
        btn_autostart = QPushButton("开机自启动设置")
        btn_autostart.setStyleSheet(self._get_button_style("#2196F3"))
        btn_autostart.clicked.connect(self.open_autostart_settings)
        config_layout.addWidget(btn_autostart)
        
        layout.addWidget(config_group)
        
        # 测试工具
        test_group = QGroupBox("测试工具")
        test_layout = QVBoxLayout(test_group)
        
        btn_test = QPushButton("播放器测试")
        btn_test.setStyleSheet(self._get_button_style("#FF9800"))
        btn_test.clicked.connect(self.open_player_test)
        test_layout.addWidget(btn_test)
        
        layout.addWidget(test_group)
        
        # 状态栏
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-top: 1px solid #ccc;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
    
    def _get_button_style(self, color):
        """获取按钮样式"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """
    
    def start_system(self):
        """启动播放系统"""
        try:
            if 'main' in self.processes:
                QMessageBox.warning(self, "提示", "播放系统已在运行中")
                return
            
            # 检查显示配置
            config_path = os.path.join(project_root, 'config', 'display_config.json')
            if not os.path.exists(config_path):
                reply = QMessageBox.question(
                    self, "提示",
                    "未找到显示配置，是否先配置显示器？",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.open_display_settings()
                    return
            
            # 使用subprocess.Popen启动，这样窗口可以正常显示
            import subprocess
            import sys
            
            # 使用start_with_selenium.py而不是run.py
            script_path = os.path.join(project_root, 'start_with_selenium.py')
            
            # 在Windows上使用CREATE_NEW_CONSOLE标志
            if sys.platform == 'win32':
                # 创建新的控制台窗口
                process = subprocess.Popen(
                    ['python', script_path],
                    cwd=project_root,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:
                process = subprocess.Popen(
                    ['python', script_path],
                    cwd=project_root
                )
            
            self.processes['main'] = process
            
            self.status_label.setText("播放系统已启动")
            QMessageBox.information(self, "成功", 
                "播放系统已启动\n\n"
                "空闲窗口应该已显示（黑屏+时钟）\n"
                "等待播放任务开始时会自动切换到播放内容")
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            QMessageBox.critical(self, "错误", f"启动失败:\n{e}\n\n详细信息:\n{error_detail}")
    
    def stop_system(self):
        """停止播放系统"""
        if 'main' in self.processes:
            try:
                process = self.processes['main']
                
                # 尝试正常终止
                process.terminate()
                
                # 等待进程结束
                import time
                for i in range(30):  # 等待最多3秒
                    if process.poll() is not None:
                        break
                    time.sleep(0.1)
                
                # 如果还没结束，强制杀死
                if process.poll() is None:
                    process.kill()
                
                del self.processes['main']
                self.status_label.setText("播放系统已停止")
                QMessageBox.information(self, "成功", "播放系统已停止")
            except Exception as e:
                QMessageBox.warning(self, "警告", f"停止时出错: {e}")
                # 即使出错也删除进程引用
                if 'main' in self.processes:
                    del self.processes['main']
        else:
            QMessageBox.warning(self, "提示", "播放系统未运行")
    
    def open_display_settings(self):
        """打开显示设置"""
        try:
            script_path = os.path.join(project_root, 'src', 'ui', 'display_settings_ui.py')
            
            if not os.path.exists(script_path):
                QMessageBox.critical(self, "错误", f"文件不存在: {script_path}")
                return
            
            subprocess.Popen(['python', script_path], cwd=project_root)
            self.status_label.setText("已打开显示器配置")
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            QMessageBox.critical(self, "错误", f"打开失败:\n{e}\n\n详细信息:\n{error_detail}")
    
    def open_schedule_manager(self):
        """打开时间表管理"""
        try:
            script_path = os.path.join(project_root, 'src', 'ui', 'gui_manager.py')
            
            # 检查文件是否存在
            if not os.path.exists(script_path):
                QMessageBox.critical(self, "错误", f"文件不存在: {script_path}")
                return
            
            # 启动进程并捕获输出
            process = subprocess.Popen(
                ['python', script_path],
                cwd=project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.status_label.setText("已打开播放时间表管理")
            
            # 等待一小段时间检查是否启动成功
            import time
            time.sleep(0.5)
            
            # 检查进程是否还在运行
            if process.poll() is not None:
                # 进程已退出，读取错误信息
                stdout, stderr = process.communicate()
                error_msg = stderr if stderr else stdout
                if error_msg:
                    QMessageBox.critical(self, "错误", f"启动失败:\n{error_msg}")
                else:
                    QMessageBox.critical(self, "错误", "程序启动后立即退出")
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            QMessageBox.critical(self, "错误", f"打开失败:\n{e}\n\n详细信息:\n{error_detail}")
    
    def open_autostart_settings(self):
        """打开自启动设置"""
        try:
            script_path = os.path.join(project_root, 'src', 'utils', 'auto_start.py')
            subprocess.Popen(['python', script_path], cwd=project_root)
            self.status_label.setText("已打开开机自启动设置")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开失败: {e}")
    
    def open_player_test(self):
        """打开播放器测试"""
        try:
            script_path = os.path.join(project_root, 'tests', 'test_player.py')
            subprocess.Popen(['python', script_path], cwd=project_root)
            self.status_label.setText("已打开播放器测试")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开失败: {e}")
    
    def closeEvent(self, event):
        """关闭事件"""
        # 停止所有进程
        for process in self.processes.values():
            try:
                process.terminate()
                # 等待进程结束（subprocess.Popen方式）
                import time
                for i in range(10):  # 等待最多1秒
                    if process.poll() is not None:
                        break
                    time.sleep(0.1)
                
                # 如果还没结束，强制杀死
                if process.poll() is None:
                    process.kill()
            except Exception as e:
                print(f"关闭进程时出错: {e}")
        
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LauncherWindow()
    window.show()
    sys.exit(app.exec_())
