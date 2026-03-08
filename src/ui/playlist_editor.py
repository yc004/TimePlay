"""轮播列表编辑器"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QLabel, QLineEdit,
                             QComboBox, QFileDialog, QMessageBox, QCheckBox,
                             QTimeEdit, QListWidget)
from PyQt5.QtCore import Qt, QTime

class PlaylistEditor(QDialog):
    def __init__(self, parent=None, playlist=None):
        super().__init__(parent)
        self.playlist = playlist if playlist else []
        self.init_ui()
        self.load_playlist()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("播放列表编辑")
        self.setModal(True)
        self.resize(800, 550)
        
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("播放列表项目:")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # 说明
        info_label = QLabel("提示：视频时长为0时自动获取完整时长，图片默认5秒")
        info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info_label)
        
        # 列表表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["类型", "路径/URL", "时长(秒)", "循环", "操作"])
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setColumnWidth(0, 80)
        self.table.setColumnWidth(2, 80)
        self.table.setColumnWidth(3, 60)
        self.table.setColumnWidth(4, 100)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # 禁止所有编辑触发器
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # 整行选择
        self.table.setSelectionMode(QTableWidget.SingleSelection)  # 单选
        layout.addWidget(self.table)
        
        # 按钮栏
        button_layout = QHBoxLayout()
        
        btn_add_video = QPushButton("添加视频")
        btn_add_video.clicked.connect(self.add_video)
        button_layout.addWidget(btn_add_video)
        
        btn_add_image = QPushButton("添加图片")
        btn_add_image.clicked.connect(self.add_image)
        button_layout.addWidget(btn_add_image)
        
        btn_add_web = QPushButton("添加网页")
        btn_add_web.clicked.connect(self.add_web)
        button_layout.addWidget(btn_add_web)
        
        btn_move_up = QPushButton("↑上移")
        btn_move_up.clicked.connect(self.move_up)
        button_layout.addWidget(btn_move_up)
        
        btn_move_down = QPushButton("↓下移")
        btn_move_down.clicked.connect(self.move_down)
        button_layout.addWidget(btn_move_down)
        
        btn_delete = QPushButton("删除")
        btn_delete.clicked.connect(self.delete_item)
        button_layout.addWidget(btn_delete)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # 统计信息
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.stats_label)
        
        # 确定取消按钮
        ok_cancel_layout = QHBoxLayout()
        btn_ok = QPushButton("确定")
        btn_ok.clicked.connect(self.accept)
        btn_ok.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px 20px;")
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        btn_cancel.setStyleSheet("padding: 8px 20px;")
        ok_cancel_layout.addStretch()
        ok_cancel_layout.addWidget(btn_ok)
        ok_cancel_layout.addWidget(btn_cancel)
        layout.addLayout(ok_cancel_layout)
    
    def load_playlist(self):
        """加载播放列表"""
        self.table.setRowCount(len(self.playlist))
        for i, item in enumerate(self.playlist):
            # 类型
            item_type = item.get('type', 'unknown')
            type_item = QTableWidgetItem(item_type)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)  # 禁止编辑
            self.table.setItem(i, 0, type_item)
            
            # 路径/URL
            path = item.get('path', item.get('url', ''))
            # 只显示文件名或URL的最后部分
            if path:
                import os
                display_path = os.path.basename(path) if '/' in path or '\\' in path else path
                if len(display_path) > 40:
                    display_path = display_path[:37] + '...'
            else:
                display_path = ''
            path_item = QTableWidgetItem(display_path)
            path_item.setToolTip(path)  # 完整路径作为提示
            path_item.setFlags(path_item.flags() & ~Qt.ItemIsEditable)  # 禁止编辑
            self.table.setItem(i, 1, path_item)
            
            # 时长
            duration = item.get('duration', 0)
            if duration == 0 and item_type == 'video':
                duration_text = "自动"
            elif duration == 0 and item_type == 'image':
                duration_text = "默认(5)"
            else:
                duration_text = str(duration)
            duration_item = QTableWidgetItem(duration_text)
            duration_item.setFlags(duration_item.flags() & ~Qt.ItemIsEditable)  # 禁止编辑
            self.table.setItem(i, 2, duration_item)
            
            # 循环
            loop = "是" if item.get('loop', False) else ""
            loop_item = QTableWidgetItem(loop)
            loop_item.setFlags(loop_item.flags() & ~Qt.ItemIsEditable)  # 禁止编辑
            self.table.setItem(i, 3, loop_item)
            
            # 操作按钮
            btn_edit = QPushButton("编辑")
            btn_edit.clicked.connect(lambda checked, row=i: self.edit_item(row))
            self.table.setCellWidget(i, 4, btn_edit)
        
        self._update_stats()
    
    def _update_stats(self):
        """更新统计信息"""
        total = len(self.playlist)
        types = {}
        total_duration = 0
        
        for item in self.playlist:
            item_type = item.get('type', 'unknown')
            types[item_type] = types.get(item_type, 0) + 1
            duration = item.get('duration', 0)
            if duration > 0:
                total_duration += duration
        
        type_names = {'video': '视频', 'image': '图片', 'web': '网页'}
        type_info = ", ".join([f"{types[t]}{type_names.get(t, t)}" for t in types])
        
        stats = f"共 {total} 项"
        if type_info:
            stats += f" ({type_info})"
        if total_duration > 0:
            minutes = total_duration // 60
            seconds = total_duration % 60
            stats += f" | 总时长: {minutes}分{seconds}秒"
        
        self.stats_label.setText(stats)
    
    def add_video(self):
        """添加视频"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择视频文件", "",
            "视频文件 (*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm *.m4v *.mpg *.mpeg);;所有文件 (*.*)"
        )
        if file_path:
            # 询问是否自动获取时长
            from PyQt5.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self, "视频时长",
                "是否自动获取视频时长？\n\n选择'是'：自动获取完整时长\n选择'否'：手动设置时长",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                duration = 0  # 0表示自动获取
                loop = False
            else:
                duration, loop = self._get_duration_and_loop()
                if duration is None:
                    return
            
            self.playlist.append({
                'type': 'video',
                'path': file_path,
                'duration': duration,
                'loop': loop
            })
            self.load_playlist()
    
    def add_image(self):
        """添加图片"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片文件", "",
            "图片文件 (*.jpg *.jpeg *.png *.gif *.bmp *.webp *.tiff *.svg);;所有文件 (*.*)"
        )
        if file_path:
            duration, _ = self._get_duration_and_loop(default_duration=5, show_loop=False)
            if duration is None:
                return
            
            self.playlist.append({
                'type': 'image',
                'path': file_path,
                'duration': duration if duration > 0 else 5
            })
            self.load_playlist()
    
    def add_web(self):
        """添加网页"""
        from PyQt5.QtWidgets import QInputDialog
        url, ok = QInputDialog.getText(self, "添加网页", "请输入网页URL:")
        if ok and url:
            duration, _ = self._get_duration_and_loop(default_duration=300, show_loop=False)
            if duration is None:
                return
            
            self.playlist.append({
                'type': 'web',
                'url': url,
                'duration': duration if duration > 0 else 300
            })
            self.load_playlist()
    
    def _get_duration_and_loop(self, default_duration=0, show_loop=True):
        """获取播放时长和循环设置"""
        dialog = QDialog(self)
        dialog.setWindowTitle("播放设置")
        dialog.setModal(True)
        
        layout = QVBoxLayout(dialog)
        
        # 时长设置
        layout.addWidget(QLabel("播放时长(秒):"))
        duration_layout = QHBoxLayout()
        duration_spin = QComboBox()
        duration_spin.setEditable(True)
        duration_spin.addItems(["0 (自动)", "5", "10", "15", "30", "60", "120", "300", "600"])
        if default_duration > 0:
            duration_spin.setCurrentText(str(default_duration))
        duration_layout.addWidget(duration_spin)
        layout.addLayout(duration_layout)
        
        # 循环设置
        loop_check = None
        if show_loop:
            loop_check = QCheckBox("循环播放")
            layout.addWidget(loop_check)
        
        # 按钮
        button_layout = QHBoxLayout()
        btn_ok = QPushButton("确定")
        btn_ok.clicked.connect(dialog.accept)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(dialog.reject)
        button_layout.addStretch()
        button_layout.addWidget(btn_ok)
        button_layout.addWidget(btn_cancel)
        layout.addLayout(button_layout)
        
        if dialog.exec_() == QDialog.Accepted:
            duration_text = duration_spin.currentText().split()[0]
            try:
                duration = int(duration_text)
            except:
                duration = default_duration
            loop = loop_check.isChecked() if loop_check else False
            return duration, loop
        
        return None, None
    
    def edit_item(self, row):
        """编辑播放项"""
        if row < 0 or row >= len(self.playlist):
            return
        
        item = self.playlist[row]
        item_type = item.get('type')
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"编辑{item_type}")
        dialog.setModal(True)
        dialog.resize(500, 200)
        
        layout = QVBoxLayout(dialog)
        
        # 路径/URL
        layout.addWidget(QLabel("路径/URL:"))
        path_edit = QLineEdit(item.get('path', item.get('url', '')))
        path_edit.setReadOnly(True)
        layout.addWidget(path_edit)
        
        # 时长
        layout.addWidget(QLabel("播放时长(秒):"))
        duration_spin = QComboBox()
        duration_spin.setEditable(True)
        if item_type == 'video':
            duration_spin.addItems(["0 (自动)", "30", "60", "120", "300", "600"])
        elif item_type == 'image':
            duration_spin.addItems(["5", "10", "15", "30", "60"])
        else:
            duration_spin.addItems(["60", "120", "300", "600", "1800", "3600"])
        duration_spin.setCurrentText(str(item.get('duration', 0)))
        layout.addWidget(duration_spin)
        
        # 循环（仅视频）
        loop_check = None
        if item_type == 'video':
            loop_check = QCheckBox("循环播放")
            loop_check.setChecked(item.get('loop', False))
            layout.addWidget(loop_check)
        
        # 按钮
        button_layout = QHBoxLayout()
        btn_ok = QPushButton("确定")
        btn_ok.clicked.connect(dialog.accept)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(dialog.reject)
        button_layout.addStretch()
        button_layout.addWidget(btn_ok)
        button_layout.addWidget(btn_cancel)
        layout.addLayout(button_layout)
        
        if dialog.exec_() == QDialog.Accepted:
            duration_text = duration_spin.currentText().split()[0]
            try:
                item['duration'] = int(duration_text)
            except:
                pass
            
            if loop_check:
                item['loop'] = loop_check.isChecked()
            
            self.load_playlist()
    
    def move_up(self):
        """上移"""
        current_row = self.table.currentRow()
        if current_row > 0:
            self.playlist[current_row], self.playlist[current_row - 1] = \
                self.playlist[current_row - 1], self.playlist[current_row]
            self.load_playlist()
            self.table.setCurrentCell(current_row - 1, 0)
    
    def move_down(self):
        """下移"""
        current_row = self.table.currentRow()
        if 0 <= current_row < len(self.playlist) - 1:
            self.playlist[current_row], self.playlist[current_row + 1] = \
                self.playlist[current_row + 1], self.playlist[current_row]
            self.load_playlist()
            self.table.setCurrentCell(current_row + 1, 0)
    
    def delete_item(self):
        """删除项目"""
        current_row = self.table.currentRow()
        if current_row >= 0:
            del self.playlist[current_row]
            self.load_playlist()
    
    def get_playlist(self):
        """获取轮播列表"""
        return self.playlist


class WeekdaySelector(QDialog):
    def __init__(self, parent=None, selected_weekdays=None):
        super().__init__(parent)
        self.selected_weekdays = selected_weekdays if selected_weekdays else [1, 2, 3, 4, 5]
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("选择星期")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("选择播放的星期:"))
        
        self.checkboxes = {}
        weekdays = [
            (1, "星期一"),
            (2, "星期二"),
            (3, "星期三"),
            (4, "星期四"),
            (5, "星期五"),
            (6, "星期六"),
            (7, "星期日")
        ]
        
        for day_num, day_name in weekdays:
            checkbox = QCheckBox(day_name)
            checkbox.setChecked(day_num in self.selected_weekdays)
            self.checkboxes[day_num] = checkbox
            layout.addWidget(checkbox)
        
        # 快捷按钮
        quick_layout = QHBoxLayout()
        btn_weekdays = QPushButton("工作日")
        btn_weekdays.clicked.connect(self.select_weekdays)
        quick_layout.addWidget(btn_weekdays)
        
        btn_weekend = QPushButton("周末")
        btn_weekend.clicked.connect(self.select_weekend)
        quick_layout.addWidget(btn_weekend)
        
        btn_all = QPushButton("全选")
        btn_all.clicked.connect(self.select_all)
        quick_layout.addWidget(btn_all)
        
        layout.addLayout(quick_layout)
        
        # 确定取消按钮
        button_layout = QHBoxLayout()
        btn_ok = QPushButton("确定")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(btn_ok)
        button_layout.addWidget(btn_cancel)
        layout.addLayout(button_layout)
    
    def select_weekdays(self):
        """选择工作日"""
        for day_num, checkbox in self.checkboxes.items():
            checkbox.setChecked(day_num in [1, 2, 3, 4, 5])
    
    def select_weekend(self):
        """选择周末"""
        for day_num, checkbox in self.checkboxes.items():
            checkbox.setChecked(day_num in [6, 7])
    
    def select_all(self):
        """全选"""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(True)
    
    def get_selected_weekdays(self):
        """获取选中的星期"""
        return [day_num for day_num, checkbox in self.checkboxes.items() if checkbox.isChecked()]
