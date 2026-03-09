"""ChromeDriver配置界面"""
import sys
import os
import subprocess

# 添加项目根目录到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit,
                             QFileDialog, QMessageBox, QGroupBox, QTextEdit,
                             QCheckBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from config.config import CHROMEDRIVER_CONFIG


class ChromeDriverConfigWindow(QMainWindow):
    """ChromeDriver配置窗口"""
    
    def __init__(self):
        super().__init__()
        self.config_file = os.path.join(project_root, 'config', 'config.py')
        self.init_ui()
        self.load_config()
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("ChromeDriver 配置")
        self.setGeometry(100, 100, 700, 500)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 标题
        title = QLabel("ChromeDriver 配置")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("padding: 15px; color: #0078D4;")
        layout.addWidget(title)
        
        # 说明
        info_label = QLabel(
            "配置 ChromeDriver 路径以支持网页直播播放。\n"
            "如果留空，系统将使用 PATH 环境变量中的 ChromeDriver。"
        )
        info_label.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # ChromeDriver路径配置
        path_group = QGroupBox("ChromeDriver 路径")
        path_layout = QVBoxLayout(path_group)
        
        # 路径输入
        path_input_layout = QHBoxLayout()
        
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("留空则使用系统 PATH 中的 ChromeDriver")
        path_input_layout.addWidget(self.path_input)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_chromedriver)
        browse_btn.setFixedWidth(100)
        path_input_layout.addWidget(browse_btn)
        
        path_layout.addLayout(path_input_layout)
        
        # 自动检测选项
        self.auto_detect_checkbox = QCheckBox("启用自动检测（推荐）")
        self.auto_detect_checkbox.setToolTip("启用后，如果自定义路径无效，将自动使用系统 PATH")
        path_layout.addWidget(self.auto_detect_checkbox)
        
        layout.addWidget(path_group)
        
        # 检测工具
        detect_group = QGroupBox("检测工具")
        detect_layout = QVBoxLayout(detect_group)
        
        # 检测按钮
        detect_btn_layout = QHBoxLayout()
        
        check_chrome_btn = QPushButton("检测 Chrome 版本")
        check_chrome_btn.clicked.connect(self.check_chrome_version)
        detect_btn_layout.addWidget(check_chrome_btn)
        
        check_driver_btn = QPushButton("检测 ChromeDriver 版本")
        check_driver_btn.clicked.connect(self.check_chromedriver_version)
        detect_btn_layout.addWidget(check_driver_btn)
        
        test_btn = QPushButton("测试连接")
        test_btn.clicked.connect(self.test_connection)
        detect_btn_layout.addWidget(test_btn)
        
        detect_layout.addLayout(detect_btn_layout)
        
        # 检测结果
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(150)
        self.result_text.setStyleSheet("background-color: #f9f9f9; font-family: Consolas, monospace;")
        detect_layout.addWidget(self.result_text)
        
        layout.addWidget(detect_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("保存配置")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        save_btn.clicked.connect(self.save_config)
        button_layout.addWidget(save_btn)
        
        reset_btn = QPushButton("重置")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 14px;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        reset_btn.clicked.connect(self.reset_config)
        button_layout.addWidget(reset_btn)
        
        layout.addLayout(button_layout)
        
        # 帮助信息
        help_label = QLabel(
            "提示：\n"
            "• ChromeDriver 版本必须与 Chrome 浏览器版本匹配\n"
            "• 下载地址：https://chromedriver.chromium.org/downloads\n"
            "• 或使用：python install_chromedriver.py 自动安装"
        )
        help_label.setStyleSheet("padding: 10px; color: #666; font-size: 11px;")
        help_label.setWordWrap(True)
        layout.addWidget(help_label)
        
    def load_config(self):
        """加载配置"""
        try:
            custom_path = CHROMEDRIVER_CONFIG.get('custom_path', '')
            auto_detect = CHROMEDRIVER_CONFIG.get('auto_detect', True)
            
            self.path_input.setText(custom_path)
            self.auto_detect_checkbox.setChecked(auto_detect)
            
            self.log_result("✓ 配置加载成功")
        except Exception as e:
            self.log_result(f"✗ 加载配置失败: {e}")
    
    def browse_chromedriver(self):
        """浏览选择ChromeDriver文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择 ChromeDriver",
            "",
            "可执行文件 (*.exe);;所有文件 (*.*)"
        )
        
        if file_path:
            self.path_input.setText(file_path)
            self.log_result(f"已选择: {file_path}")
    
    def check_chrome_version(self):
        """检测Chrome版本"""
        try:
            self.log_result("正在检测 Chrome 版本...")
            
            # Windows上的Chrome路径
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
            ]
            
            chrome_path = None
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_path = path
                    break
            
            if not chrome_path:
                self.log_result("✗ 未找到 Chrome 浏览器")
                return
            
            # 获取版本
            result = subprocess.run(
                [chrome_path, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            version = result.stdout.strip()
            self.log_result(f"✓ Chrome 版本: {version}")
            
        except subprocess.TimeoutExpired:
            self.log_result("✗ 检测超时")
        except Exception as e:
            self.log_result(f"✗ 检测失败: {e}")
    
    def check_chromedriver_version(self):
        """检测ChromeDriver版本"""
        try:
            self.log_result("正在检测 ChromeDriver 版本...")
            
            # 获取配置的路径
            custom_path = self.path_input.text().strip()
            
            if custom_path:
                if not os.path.exists(custom_path):
                    self.log_result(f"✗ 文件不存在: {custom_path}")
                    return
                driver_path = custom_path
            else:
                driver_path = "chromedriver"  # 使用PATH中的
            
            # 获取版本
            result = subprocess.run(
                [driver_path, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            version = result.stdout.strip()
            self.log_result(f"✓ ChromeDriver 版本: {version}")
            
        except FileNotFoundError:
            self.log_result("✗ ChromeDriver 未找到（不在 PATH 中）")
        except subprocess.TimeoutExpired:
            self.log_result("✗ 检测超时")
        except Exception as e:
            self.log_result(f"✗ 检测失败: {e}")
    
    def test_connection(self):
        """测试ChromeDriver连接"""
        try:
            self.log_result("正在测试 ChromeDriver 连接...")
            
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            
            # 配置选项
            options = Options()
            options.add_argument('--headless')  # 无头模式
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--log-level=3')
            
            # 获取配置的路径
            custom_path = self.path_input.text().strip()
            
            if custom_path:
                if not os.path.exists(custom_path):
                    self.log_result(f"✗ 文件不存在: {custom_path}")
                    return
                self.log_result(f"使用自定义路径: {custom_path}")
                service = Service(executable_path=custom_path)
                driver = webdriver.Chrome(service=service, options=options)
            else:
                self.log_result("使用系统 PATH 中的 ChromeDriver")
                driver = webdriver.Chrome(options=options)
            
            # 测试访问页面
            driver.get("https://www.baidu.com")
            title = driver.title
            
            driver.quit()
            
            self.log_result(f"✓ 连接测试成功！")
            self.log_result(f"  测试页面标题: {title}")
            
        except Exception as e:
            self.log_result(f"✗ 连接测试失败: {e}")
            import traceback
            self.log_result(traceback.format_exc())
    
    def save_config(self):
        """保存配置"""
        try:
            custom_path = self.path_input.text().strip()
            auto_detect = self.auto_detect_checkbox.isChecked()
            
            # 验证路径
            if custom_path and not os.path.exists(custom_path):
                reply = QMessageBox.question(
                    self,
                    "确认",
                    f"指定的文件不存在：\n{custom_path}\n\n是否仍要保存？",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
            
            # 读取配置文件
            with open(self.config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 更新配置
            import re
            
            # 更新 custom_path
            pattern = r"'custom_path':\s*'[^']*'"
            replacement = f"'custom_path': '{custom_path}'"
            content = re.sub(pattern, replacement, content)
            
            # 更新 auto_detect
            pattern = r"'auto_detect':\s*(True|False)"
            replacement = f"'auto_detect': {auto_detect}"
            content = re.sub(pattern, replacement, content)
            
            # 写回文件
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log_result("✓ 配置保存成功")
            QMessageBox.information(
                self,
                "成功",
                "配置已保存！\n\n重启播放系统后生效。"
            )
            
        except Exception as e:
            self.log_result(f"✗ 保存配置失败: {e}")
            QMessageBox.critical(self, "错误", f"保存配置失败：\n{e}")
    
    def reset_config(self):
        """重置配置"""
        reply = QMessageBox.question(
            self,
            "确认",
            "确定要重置配置吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.path_input.clear()
            self.auto_detect_checkbox.setChecked(True)
            self.log_result("配置已重置（未保存）")
    
    def log_result(self, message):
        """记录结果"""
        self.result_text.append(message)
        # 滚动到底部
        scrollbar = self.result_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


def main():
    app = QApplication(sys.argv)
    window = ChromeDriverConfigWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
