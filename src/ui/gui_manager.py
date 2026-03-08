"""图形化管理界面"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QLabel, QMessageBox, QFileDialog, QTimeEdit,
                             QComboBox, QLineEdit, QCheckBox, QDialog, QStackedWidget,
                             QButtonGroup, QRadioButton)
from PyQt5.QtCore import Qt, QTime
import json
from src.utils.logger import Logger
from src.ui.schedule_calendar_view import ScheduleCalendarView

class ScheduleManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger = Logger()
        self.schedules = []
        self.init_ui()
        self.load_schedules()
        
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("播放时间表管理")
        self.setGeometry(100, 100, 1100, 700)
        
        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 标题
        title = QLabel("校园闭路电视播放时间表")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # 视图切换和按钮栏
        top_layout = QHBoxLayout()
        
        # 视图切换
        view_group_widget = QWidget()
        view_group_layout = QHBoxLayout(view_group_widget)
        view_group_layout.setContentsMargins(0, 0, 0, 0)
        
        view_label = QLabel("视图:")
        view_label.setStyleSheet("font-weight: bold;")
        view_group_layout.addWidget(view_label)
        
        self.radio_list = QRadioButton("列表视图")
        self.radio_list.setChecked(True)
        self.radio_list.toggled.connect(self.switch_view)
        view_group_layout.addWidget(self.radio_list)
        
        self.radio_calendar = QRadioButton("课程表视图")
        self.radio_calendar.toggled.connect(self.switch_view)
        view_group_layout.addWidget(self.radio_calendar)
        
        view_group_layout.addStretch()
        top_layout.addWidget(view_group_widget)
        
        top_layout.addStretch()
        
        # 操作按钮
        self.btn_add = QPushButton("添加任务")
        self.btn_add.clicked.connect(self.add_schedule)
        top_layout.addWidget(self.btn_add)
        
        self.btn_edit = QPushButton("编辑任务")
        self.btn_edit.clicked.connect(self.edit_schedule)
        top_layout.addWidget(self.btn_edit)
        
        self.btn_delete = QPushButton("删除任务")
        self.btn_delete.clicked.connect(self.delete_schedule)
        top_layout.addWidget(self.btn_delete)
        
        self.btn_save = QPushButton("保存配置")
        self.btn_save.clicked.connect(self.save_schedules)
        self.btn_save.setStyleSheet("background-color: #4CAF50; color: white;")
        top_layout.addWidget(self.btn_save)
        
        layout.addLayout(top_layout)
        
        # 创建堆叠窗口用于切换视图
        self.stacked_widget = QStackedWidget()
        
        # 列表视图
        list_view_widget = QWidget()
        list_view_layout = QVBoxLayout(list_view_widget)
        list_view_layout.setContentsMargins(0, 0, 0, 0)
        
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "任务名称", "开始时间", "结束时间", "星期", "类型", "内容", "启用"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # 禁止所有编辑触发器
        self.table.setSelectionBehavior(QTableWidget.SelectRows)  # 整行选择
        self.table.setSelectionMode(QTableWidget.SingleSelection)  # 单选
        self.table.doubleClicked.connect(self.edit_schedule)  # 双击编辑
        list_view_layout.addWidget(self.table)
        
        self.stacked_widget.addWidget(list_view_widget)
        
        # 课程表视图
        self.calendar_view = ScheduleCalendarView()
        self.stacked_widget.addWidget(self.calendar_view)
        
        layout.addWidget(self.stacked_widget)
        
        # 状态栏
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        layout.addWidget(self.status_label)
    
    def load_schedules(self):
        """加载时间表"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '../../config/schedule.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.schedules = data.get('schedules', [])
            self.refresh_table()
            self.calendar_view.load_schedules(self.schedules)
            self.status_label.setText(f"已加载 {len(self.schedules)} 个任务")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载配置失败: {e}")
    
    def switch_view(self):
        """切换视图"""
        if self.radio_list.isChecked():
            self.stacked_widget.setCurrentIndex(0)
            self.status_label.setText("列表视图")
        else:
            self.stacked_widget.setCurrentIndex(1)
            self.calendar_view.load_schedules(self.schedules)
            self.status_label.setText("表格视图")
    
    def refresh_table(self):
        """刷新表格"""
        self.table.setRowCount(len(self.schedules))
        weekday_names = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "日"}
        
        for i, item in enumerate(self.schedules):
            # ID
            id_item = QTableWidgetItem(str(item['id']))
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)  # 禁止编辑
            self.table.setItem(i, 0, id_item)
            
            # 任务名称
            name_item = QTableWidgetItem(item['name'])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)  # 禁止编辑
            self.table.setItem(i, 1, name_item)
            
            # 开始时间
            start_item = QTableWidgetItem(item.get('start_time', ''))
            start_item.setFlags(start_item.flags() & ~Qt.ItemIsEditable)  # 禁止编辑
            self.table.setItem(i, 2, start_item)
            
            # 结束时间
            end_item = QTableWidgetItem(item.get('end_time', ''))
            end_item.setFlags(end_item.flags() & ~Qt.ItemIsEditable)  # 禁止编辑
            self.table.setItem(i, 3, end_item)
            
            # 星期显示
            weekdays = item.get('weekdays', [1, 2, 3, 4, 5, 6, 7])
            weekday_str = "".join([weekday_names.get(d, str(d)) for d in sorted(weekdays)])
            weekday_item = QTableWidgetItem(weekday_str)
            weekday_item.setFlags(weekday_item.flags() & ~Qt.ItemIsEditable)  # 禁止编辑
            self.table.setItem(i, 4, weekday_item)
            
            # 类型
            item_type = item['type']
            if item_type == 'playlist':
                type_str = f"播放列表({len(item.get('playlist', []))}项)"
            else:
                type_str = item_type
            type_item = QTableWidgetItem(type_str)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)  # 禁止编辑
            self.table.setItem(i, 5, type_item)
            
            # 内容
            if item_type == 'video':
                content = item.get('path', '')
            elif item_type == 'web':
                content = item.get('url', '')
            elif item_type == 'playlist':
                content = f"{len(item.get('playlist', []))}个项目"
            else:
                content = ''
            content_item = QTableWidgetItem(content)
            content_item.setFlags(content_item.flags() & ~Qt.ItemIsEditable)  # 禁止编辑
            self.table.setItem(i, 6, content_item)
            
            # 启用状态
            enabled = "是" if item.get('enabled', True) else "否"
            enabled_item = QTableWidgetItem(enabled)
            enabled_item.setFlags(enabled_item.flags() & ~Qt.ItemIsEditable)  # 禁止编辑
            self.table.setItem(i, 7, enabled_item)
    
    def add_schedule(self):
        """添加任务"""
        dialog = ScheduleDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_schedule = dialog.get_schedule()
            new_schedule['id'] = max([s['id'] for s in self.schedules], default=0) + 1
            self.schedules.append(new_schedule)
            self.refresh_table()
            self.calendar_view.load_schedules(self.schedules)
            self.status_label.setText("已添加新任务")
    
    def edit_schedule(self):
        """编辑任务"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "提示", "请先选择要编辑的任务")
            return
        
        dialog = ScheduleDialog(self, self.schedules[current_row])
        if dialog.exec_() == QDialog.Accepted:
            self.schedules[current_row] = dialog.get_schedule()
            self.schedules[current_row]['id'] = int(self.table.item(current_row, 0).text())
            self.refresh_table()
            self.calendar_view.load_schedules(self.schedules)
            self.status_label.setText("任务已更新")
    
    def delete_schedule(self):
        """删除任务"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "提示", "请先选择要删除的任务")
            return
        
        reply = QMessageBox.question(self, "确认", "确定要删除这个任务吗？",
                                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            del self.schedules[current_row]
            self.refresh_table()
            self.calendar_view.load_schedules(self.schedules)
            self.status_label.setText("任务已删除")
    
    def save_schedules(self):
        """保存配置"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), '../../config/schedule.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump({'schedules': self.schedules}, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "成功", "配置已保存")
            self.status_label.setText("配置已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {e}")


class ScheduleDialog(QDialog):
    def __init__(self, parent=None, schedule=None):
        super().__init__(parent)
        self.schedule = schedule
        self.playlist = []
        self.selected_weekdays = [1, 2, 3, 4, 5]
        self.init_ui()
        if schedule:
            self.load_schedule(schedule)
    
    def init_ui(self):
        """初始化对话框"""
        self.setWindowTitle("任务编辑")
        self.setModal(True)
        self.resize(500, 500)
        layout = QVBoxLayout(self)
        
        # 任务名称
        layout.addWidget(QLabel("任务名称:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)
        
        # 时间段
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("开始时间:"))
        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setDisplayFormat("HH:mm")
        time_layout.addWidget(self.start_time_edit)
        
        time_layout.addWidget(QLabel("结束时间:"))
        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setDisplayFormat("HH:mm")
        time_layout.addWidget(self.end_time_edit)
        layout.addLayout(time_layout)
        
        # 星期选择
        weekday_layout = QHBoxLayout()
        weekday_layout.addWidget(QLabel("播放星期:"))
        self.weekday_label = QLabel("一二三四五")
        weekday_layout.addWidget(self.weekday_label)
        self.btn_select_weekday = QPushButton("选择...")
        self.btn_select_weekday.clicked.connect(self.select_weekdays)
        weekday_layout.addWidget(self.btn_select_weekday)
        weekday_layout.addStretch()
        layout.addLayout(weekday_layout)
        
        # 说明文字
        info_label = QLabel("注意：现在所有任务都使用播放列表格式")
        info_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        layout.addWidget(info_label)
        
        # 轮播列表编辑
        layout.addWidget(QLabel("播放列表:"))
        self.btn_edit_playlist = QPushButton("编辑播放列表...")
        self.btn_edit_playlist.clicked.connect(self.edit_playlist)
        layout.addWidget(self.btn_edit_playlist)
        
        # 播放列表信息
        self.playlist_info_label = QLabel("0个播放项")
        self.playlist_info_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.playlist_info_label)
        
        # 轮播循环
        self.loop_check = QCheckBox("循环播放列表")
        self.loop_check.setChecked(True)
        layout.addWidget(self.loop_check)
        
        # 全屏
        self.fullscreen_check = QCheckBox("全屏播放")
        self.fullscreen_check.setChecked(True)
        layout.addWidget(self.fullscreen_check)
        
        # 置顶
        self.topmost_check = QCheckBox("窗口置顶")
        self.topmost_check.setChecked(True)
        layout.addWidget(self.topmost_check)
        
        # 启用
        self.enabled_check = QCheckBox("启用此任务")
        self.enabled_check.setChecked(True)
        layout.addWidget(self.enabled_check)
        
        layout.addStretch()
        
        # 按钮
        button_layout = QHBoxLayout()
        self.btn_ok = QPushButton("确定")
        self.btn_ok.clicked.connect(self.validate_and_accept)
        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.btn_ok)
        button_layout.addWidget(btn_cancel)
        layout.addLayout(button_layout)
    
    def on_type_changed(self, type_text):
        """类型改变时更新界面（已废弃，保留用于兼容）"""
        pass
    
    def select_weekdays(self):
        """选择星期"""
        from src.ui.playlist_editor import WeekdaySelector
        dialog = WeekdaySelector(self, self.selected_weekdays)
        if dialog.exec_() == QDialog.Accepted:
            self.selected_weekdays = dialog.get_selected_weekdays()
            self._update_weekday_label()
    
    def _update_weekday_label(self):
        """更新星期显示"""
        weekday_names = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "日"}
        text = "".join([weekday_names.get(d, str(d)) for d in sorted(self.selected_weekdays)])
        self.weekday_label.setText(text if text else "未选择")
    
    def edit_playlist(self):
        """编辑播放列表"""
        from src.ui.playlist_editor import PlaylistEditor
        dialog = PlaylistEditor(self, self.playlist)
        if dialog.exec_() == QDialog.Accepted:
            self.playlist = dialog.get_playlist()
            self._update_playlist_info()
    
    def _update_playlist_info(self):
        """更新播放列表信息"""
        count = len(self.playlist)
        types = {}
        for item in self.playlist:
            item_type = item.get('type', 'unknown')
            types[item_type] = types.get(item_type, 0) + 1
        
        info_parts = [f"{count}个播放项"]
        if types:
            type_names = {'video': '视频', 'image': '图片', 'web': '网页'}
            type_info = ", ".join([f"{types[t]}{type_names.get(t, t)}" for t in types])
            info_parts.append(f"({type_info})")
        
        self.playlist_info_label.setText(" ".join(info_parts))
    
    def browse_file(self):
        """浏览文件（已废弃，保留用于兼容）"""
        pass
    
    def load_schedule(self, schedule):
        """加载任务数据"""
        self.name_edit.setText(schedule['name'])
        
        # 时间
        start_parts = schedule.get('start_time', '00:00').split(':')
        self.start_time_edit.setTime(QTime(int(start_parts[0]), int(start_parts[1])))
        end_parts = schedule.get('end_time', '00:00').split(':')
        self.end_time_edit.setTime(QTime(int(end_parts[0]), int(end_parts[1])))
        
        # 星期
        self.selected_weekdays = schedule.get('weekdays', [1, 2, 3, 4, 5])
        self._update_weekday_label()
        
        # 播放列表（统一格式）
        if schedule['type'] == 'playlist':
            self.playlist = schedule.get('playlist', [])
        else:
            # 兼容旧格式：自动转换为播放列表
            if schedule['type'] == 'video':
                self.playlist = [{
                    'type': 'video',
                    'path': schedule.get('path', ''),
                    'comment': '从旧格式转换'
                }]
            elif schedule['type'] == 'web':
                self.playlist = [{
                    'type': 'web',
                    'url': schedule.get('url', ''),
                    'duration': 300,
                    'comment': '从旧格式转换'
                }]
        
        self._update_playlist_info()
        
        # 选项
        self.fullscreen_check.setChecked(schedule.get('fullscreen', True))
        self.topmost_check.setChecked(schedule.get('topmost', True))
        self.enabled_check.setChecked(schedule.get('enabled', True))
        self.loop_check.setChecked(schedule.get('loop', True))
    
    def get_schedule(self):
        """获取任务数据"""
        schedule = {
            'name': self.name_edit.text(),
            'start_time': self.start_time_edit.time().toString("HH:mm"),
            'end_time': self.end_time_edit.time().toString("HH:mm"),
            'weekdays': self.selected_weekdays,
            'type': 'playlist',  # 统一使用playlist类型
            'fullscreen': self.fullscreen_check.isChecked(),
            'topmost': self.topmost_check.isChecked(),
            'enabled': self.enabled_check.isChecked(),
            'playlist': self.playlist,
            'loop': self.loop_check.isChecked()
        }
        
        return schedule
    
    def validate_and_accept(self):
        """验证并接受"""
        # 基本验证
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "验证失败", "请输入任务名称")
            return
        
        if not self.playlist:
            QMessageBox.warning(self, "验证失败", "播放列表不能为空，请至少添加一个播放项")
            return
        
        # 时间验证
        start_time = self.start_time_edit.time()
        end_time = self.end_time_edit.time()
        
        if start_time >= end_time:
            QMessageBox.warning(self, "验证失败", "结束时间必须晚于开始时间")
            return
        
        # 检查任务重叠
        if not self.check_overlap():
            return
        
        # 验证通过，接受对话框
        self.accept()
    
    def check_overlap(self):
        """
        检查任务是否与现有任务重叠
        
        Returns:
            bool: True表示没有重叠，False表示有重叠
        """
        # 获取当前任务的时间和星期
        start_time = self.start_time_edit.time()
        end_time = self.end_time_edit.time()
        weekdays = self.selected_weekdays
        
        # 转换为分钟数便于比较
        start_minutes = start_time.hour() * 60 + start_time.minute()
        end_minutes = end_time.hour() * 60 + end_time.minute()
        
        # 获取当前任务的ID（如果是编辑模式）
        current_id = self.schedule.get('id') if self.schedule else None
        
        # 获取父窗口的所有任务
        parent_window = self.parent()
        if not hasattr(parent_window, 'schedules'):
            return True
        
        # 检查每个现有任务
        overlapping_tasks = []
        for existing_schedule in parent_window.schedules:
            # 跳过当前正在编辑的任务
            if current_id and existing_schedule.get('id') == current_id:
                continue
            
            # 跳过禁用的任务
            if not existing_schedule.get('enabled', True):
                continue
            
            # 检查星期是否有交集
            existing_weekdays = existing_schedule.get('weekdays', [])
            common_weekdays = set(weekdays) & set(existing_weekdays)
            
            if not common_weekdays:
                # 没有共同的星期，不会重叠
                continue
            
            # 检查时间是否重叠
            existing_start_str = existing_schedule.get('start_time', '00:00')
            existing_end_str = existing_schedule.get('end_time', '23:59')
            
            existing_start = QTime.fromString(existing_start_str, "HH:mm")
            existing_end = QTime.fromString(existing_end_str, "HH:mm")
            
            existing_start_minutes = existing_start.hour() * 60 + existing_start.minute()
            existing_end_minutes = existing_end.hour() * 60 + existing_end.minute()
            
            # 检查时间段是否重叠
            # 两个时间段重叠的条件：不是(A结束 <= B开始 或 B结束 <= A开始)
            if not (end_minutes <= existing_start_minutes or existing_end_minutes <= start_minutes):
                # 有重叠
                weekday_names = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "日"}
                common_weekday_str = "".join([weekday_names.get(d, str(d)) for d in sorted(common_weekdays)])
                
                overlapping_tasks.append({
                    'name': existing_schedule.get('name', '未命名'),
                    'time': f"{existing_start_str}-{existing_end_str}",
                    'weekdays': common_weekday_str
                })
        
        # 如果有重叠，显示详细信息
        if overlapping_tasks:
            message = "任务时间重叠！同一时间只能有一个播放任务。\n\n"
            message += "与以下任务冲突：\n\n"
            
            for i, task in enumerate(overlapping_tasks, 1):
                message += f"{i}. {task['name']}\n"
                message += f"   时间：{task['time']}\n"
                message += f"   星期：{task['weekdays']}\n\n"
            
            message += "请调整任务的时间或星期设置。"
            
            QMessageBox.warning(self, "任务重叠", message)
            return False
        
        return True


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = ScheduleManager()
    window.show()
    sys.exit(app.exec_())
