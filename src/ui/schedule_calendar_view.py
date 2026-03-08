"""课程表风格的时间表视图"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QScrollArea, QFrame, QPushButton, QGridLayout)
from PyQt5.QtCore import Qt, QTime, QTimer
from PyQt5.QtGui import QColor, QPalette
from src.utils.ui_config import ui_config
from datetime import datetime

class ScheduleCalendarView(QWidget):
    """课程表风格视图 - 横向星期，纵向时间"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.schedules = []
        self.config = ui_config  # 使用UI配置
        self.time_indicator_line = None  # 时间指示线
        self.time_indicator_label = None  # 时间标签
        self.time_update_timer = None  # 时间更新定时器
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建课程表容器（不使用滚动区域，直接填充）
        self.calendar_widget = QWidget()
        self.calendar_layout = QVBoxLayout(self.calendar_widget)
        self.calendar_layout.setSpacing(0)
        self.calendar_layout.setContentsMargins(5, 5, 5, 5)
        
        layout.addWidget(self.calendar_widget)
    
    def load_schedules(self, schedules):
        """加载时间表数据"""
        self.schedules = schedules
        self.refresh_view()
    
    def refresh_view(self):
        """刷新视图"""
        # 清空现有内容
        while self.calendar_layout.count():
            item = self.calendar_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 停止时间更新定时器
        if self.time_update_timer:
            self.time_update_timer.stop()
            self.time_update_timer = None
        
        # 清理时间指示线
        if self.time_indicator_line:
            self.time_indicator_line.deleteLater()
            self.time_indicator_line = None
        if self.time_indicator_label:
            self.time_indicator_label.deleteLater()
            self.time_indicator_label = None
        
        if not self.schedules:
            empty_label = QLabel("暂无播放任务")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #999; font-size: 16px; padding: 50px;")
            self.calendar_layout.addWidget(empty_label)
            return
        
        # 创建网格布局
        grid_widget = QWidget()
        self.grid = QGridLayout(grid_widget)
        
        # 从配置获取间距
        spacing = self.config.get_calendar_layout('grid_spacing')
        self.grid.setSpacing(spacing)
        self.grid.setContentsMargins(0, 0, 0, 0)
        
        # 设置列拉伸，使所有列平均分配空间
        for col in range(1, 8):  # 7个星期列
            self.grid.setColumnStretch(col, 1)
        
        # 动态生成时间段（根据实际任务时间）
        time_slots = self._generate_dynamic_time_slots()
        
        # 设置行拉伸，使所有行根据时间段长度按比例分配空间
        for row in range(len(time_slots)):
            # 计算时间段的分钟数作为拉伸权重
            slot_minutes = self._get_slot_duration_minutes(time_slots[row])
            self.grid.setRowStretch(row + 1, slot_minutes)
        
        # 创建表头（星期）
        self._create_header()
        
        # 按星期分组任务
        weekday_schedules = self._group_by_weekday()
        
        # 为每个星期创建合并后的任务块
        weekday_blocks = {}
        for weekday in range(1, 8):
            if weekday in weekday_schedules:
                weekday_blocks[weekday] = self._merge_time_blocks(
                    weekday_schedules[weekday], 
                    time_slots
                )
            else:
                weekday_blocks[weekday] = []
        
        # 创建时间行
        for row, time_slot in enumerate(time_slots):
            # 时间标签列
            time_label = self._create_time_label(time_slot)
            self.grid.addWidget(time_label, row + 1, 0)
            
            # 为每个星期创建格子
            for col, weekday in enumerate(range(1, 8)):
                # 检查这个格子是否已被上面的合并块占用
                if self._is_cell_occupied(weekday_blocks[weekday], row):
                    continue
                
                # 查找从这个时间段开始的任务块
                block = self._find_block_at_row(weekday_blocks[weekday], row)
                
                if block:
                    # 创建任务块（可能跨多行）
                    task_widget = self._create_task_block(block)
                    self.grid.addWidget(task_widget, row + 1, col + 1, block['span'], 1)
                else:
                    # 创建空白格子
                    empty_cell = self._create_empty_cell()
                    self.grid.addWidget(empty_cell, row + 1, col + 1)
        
        # 添加网格布局，设置拉伸因子使其填充所有可用空间
        self.calendar_layout.addWidget(grid_widget, 1)
        
        # 创建时间指示线（如果启用）
        if self.config.is_time_indicator_enabled():
            self._create_time_indicator()
            self._start_time_update_timer()
        
        # 延迟更新指示线位置，确保布局完成
        QTimer.singleShot(100, self._update_time_indicator_position)
    
    def _create_header(self):
        """创建表头（横向星期）"""
        # 从配置获取尺寸
        min_width = self.config.get_calendar_layout('time_column_min_width')
        max_width = self.config.get_calendar_layout('time_column_max_width')
        min_height = self.config.get_calendar_layout('header_min_height')
        max_height = self.config.get_calendar_layout('header_max_height')
        
        # 左上角空白
        corner_label = QLabel("")
        corner_label.setMinimumWidth(min_width)
        corner_label.setMaximumWidth(max_width)
        corner_label.setMinimumHeight(min_height)
        corner_label.setMaximumHeight(max_height)
        
        # 从配置获取颜色
        corner_bg = self.config.get_calendar_color('corner_bg')
        corner_border = self.config.get_calendar_color('corner_border')
        corner_label.setStyleSheet(f"""
            background-color: {corner_bg};
            border: 1px solid {corner_border};
        """)
        self.grid.addWidget(corner_label, 0, 0)
        
        # 星期标题
        weekday_names = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        for col, weekday_name in enumerate(weekday_names):
            weekday_label = QLabel(weekday_name)
            weekday_label.setAlignment(Qt.AlignCenter)
            weekday_label.setMinimumHeight(min_height)
            weekday_label.setMaximumHeight(max_height)
            
            # 使用配置的样式
            weekday_label.setStyleSheet(self.config.get_header_style())
            self.grid.addWidget(weekday_label, 0, col + 1)
    
    def _create_time_label(self, time_slot):
        """创建时间标签"""
        # 从配置获取尺寸
        min_width = self.config.get_calendar_layout('time_column_min_width')
        max_width = self.config.get_calendar_layout('time_column_max_width')
        min_height = self.config.get_calendar_layout('cell_min_height')
        
        time_label = QLabel(time_slot)
        time_label.setAlignment(Qt.AlignCenter)
        time_label.setMinimumWidth(min_width)
        time_label.setMaximumWidth(max_width)
        time_label.setMinimumHeight(min_height)
        
        # 使用配置的样式
        time_label.setStyleSheet(self.config.get_time_label_style())
        return time_label
    
    def _create_task_block(self, block):
        """创建任务块（可能跨多个时间段）"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Box)
        widget.setLineWidth(2)
        
        # 获取任务类型并应用对应样式
        schedule_type = block['schedule'].get('type', 'playlist')
        widget.setStyleSheet(self.config.get_task_block_style(schedule_type))
        
        # 从配置获取布局参数
        padding = self.config.get_calendar_layout('task_block_padding')
        spacing = self.config.get_calendar_layout('task_block_spacing')
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(padding, padding, padding, padding)
        layout.setSpacing(spacing)
        
        schedule = block['schedule']
        
        # 任务名称
        name_font = self.config.get_calendar_font('task_name')
        name_label = QLabel(schedule['name'])
        name_label.setStyleSheet(self.config.get_font_style('task_name'))
        name_label.setWordWrap(True)
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)
        
        # 时间
        time_label = QLabel(f"{schedule.get('start_time', '')} - {schedule.get('end_time', '')}")
        time_label.setStyleSheet(self.config.get_font_style('time_display'))
        time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(time_label)
        
        # 播放列表内容详情
        if schedule_type == 'playlist':
            playlist = schedule.get('playlist', [])
            if playlist:
                # 创建内容列表
                content_text = self._format_playlist_content(playlist)
                content_label = QLabel(content_text)
                
                # 从配置获取内容样式
                content_font = self.config.get_calendar_font('playlist_content')
                line_height = self.config.get_calendar_layout('content_line_height')
                content_label.setStyleSheet(
                    f"{self.config.get_font_style('playlist_content')}; line-height: {line_height};"
                )
                content_label.setWordWrap(True)
                content_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
                layout.addWidget(content_label)
            else:
                content_label = QLabel("播放列表为空")
                content_label.setStyleSheet(f"{self.config.get_font_style('playlist_content')}; font-style: italic;")
                content_label.setAlignment(Qt.AlignCenter)
                layout.addWidget(content_label)
        else:
            # 旧格式兼容
            content_label = QLabel(schedule_type)
            content_label.setStyleSheet(self.config.get_font_style('playlist_content'))
            content_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(content_label)
        
        layout.addStretch()
        
        return widget
    
    def _format_playlist_content(self, playlist):
        """格式化播放列表内容为显示文本"""
        if not playlist:
            return ""
        
        lines = []
        
        # 从配置获取最大显示项数和文件名长度
        max_items = self.config.get_calendar_content('max_playlist_items')
        max_length = self.config.get_calendar_content('filename_max_length')
        show_icons = self.config.get_calendar_content('show_icons')
        
        for i, item in enumerate(playlist[:max_items], 1):
            item_type = item.get('type', 'unknown')
            
            # 从配置获取图标
            icon = self.config.get_icon(item_type) if show_icons else ''
            
            # 获取显示名称
            if item_type == 'video' or item_type == 'image':
                path = item.get('path', '')
                if path:
                    import os
                    name = os.path.basename(path)
                    # 截断过长的文件名
                    if len(name) > max_length:
                        name = name[:max_length-3] + '...'
                else:
                    name = '未知文件'
            elif item_type == 'web':
                url = item.get('url', '')
                # 提取域名或显示简短URL
                if 'cctv' in url.lower():
                    name = 'CCTV直播'
                elif url:
                    # 简化URL显示
                    if len(url) > max_length:
                        name = url[:max_length-3] + '...'
                    else:
                        name = url
                else:
                    name = '网页直播'
            else:
                name = item_type
            
            # 添加时长信息
            duration = item.get('duration', 0)
            if duration > 0:
                if duration >= 60:
                    duration_str = f"{duration//60}分"
                else:
                    duration_str = f"{duration}秒"
            else:
                duration_str = "自动" if item_type == 'video' else ""
            
            # 组合显示文本
            if show_icons:
                if duration_str:
                    lines.append(f"{icon} {name} ({duration_str})")
                else:
                    lines.append(f"{icon} {name}")
            else:
                if duration_str:
                    lines.append(f"{name} ({duration_str})")
                else:
                    lines.append(name)
        
        # 如果还有更多项
        if len(playlist) > max_items:
            lines.append(f"... 还有 {len(playlist) - max_items} 项")
        
        return "\n".join(lines)
    
    def _create_empty_cell(self):
        """创建空白格子"""
        # 从配置获取尺寸
        min_height = self.config.get_calendar_layout('cell_min_height')
        
        cell = QFrame()
        cell.setFrameStyle(QFrame.Box)
        cell.setLineWidth(1)
        cell.setMinimumHeight(min_height)
        
        # 使用配置的样式
        cell.setStyleSheet(self.config.get_empty_cell_style())
        
        layout = QVBoxLayout(cell)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 从配置获取空白符号样式
        empty_font = self.config.get_calendar_font('empty_cell')
        empty_label = QLabel("—")
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setStyleSheet(
            f"color: {empty_font.get('color', '#BDBDBD')}; font-size: {empty_font.get('size', 32)}px;"
        )
        layout.addWidget(empty_label)
        
        return cell
    
    def _merge_time_blocks(self, schedules, time_slots):
        """合并相同任务的连续时间段"""
        blocks = []
        
        for schedule in schedules:
            if not schedule.get('enabled', True):
                continue
            
            task_start = QTime.fromString(schedule.get('start_time', '00:00'), "HH:mm")
            task_end = QTime.fromString(schedule.get('end_time', '23:59'), "HH:mm")
            
            # 找出任务覆盖的所有时间段
            covered_rows = []
            for row, time_slot in enumerate(time_slots):
                start_str, end_str = time_slot.split('-')
                slot_start = QTime.fromString(start_str.strip(), "HH:mm")
                slot_end = QTime.fromString(end_str.strip(), "HH:mm")
                
                if self._time_overlaps(slot_start, slot_end, task_start, task_end):
                    covered_rows.append(row)
            
            if covered_rows:
                # 创建一个块，记录起始行和跨度
                blocks.append({
                    'schedule': schedule,
                    'start_row': covered_rows[0],
                    'span': len(covered_rows),
                    'rows': covered_rows
                })
        
        return blocks
    
    def _is_cell_occupied(self, blocks, row):
        """检查某个格子是否已被占用"""
        for block in blocks:
            if row in block['rows'] and row != block['start_row']:
                return True
        return False
    
    def _find_block_at_row(self, blocks, row):
        """查找从指定行开始的任务块"""
        for block in blocks:
            if block['start_row'] == row:
                return block
        return None
    
    def _get_time_slots(self):
        """获取时间段列表（旧方法，保留用于兼容）"""
        # 定义时间段（每2小时一段）
        return [
            "06:00-08:00",
            "08:00-10:00",
            "10:00-12:00",
            "12:00-14:00",
            "14:00-16:00",
            "16:00-18:00",
            "18:00-20:00",
            "20:00-22:00"
        ]
    
    def _generate_dynamic_time_slots(self):
        """
        根据实际任务时间动态生成时间段
        收集所有任务的开始和结束时间，生成精确的时间段划分
        """
        # 收集所有时间点
        time_points = set()
        
        # 添加默认的起止时间
        time_points.add(QTime(6, 0))   # 06:00
        time_points.add(QTime(22, 0))  # 22:00
        
        # 收集所有任务的开始和结束时间
        for schedule in self.schedules:
            if not schedule.get('enabled', True):
                continue
            
            start_time_str = schedule.get('start_time', '06:00')
            end_time_str = schedule.get('end_time', '22:00')
            
            start_time = QTime.fromString(start_time_str, "HH:mm")
            end_time = QTime.fromString(end_time_str, "HH:mm")
            
            if start_time.isValid():
                time_points.add(start_time)
            if end_time.isValid():
                time_points.add(end_time)
        
        # 排序时间点
        sorted_times = sorted(time_points, key=lambda t: t.hour() * 60 + t.minute())
        
        # 生成时间段
        time_slots = []
        for i in range(len(sorted_times) - 1):
            start = sorted_times[i]
            end = sorted_times[i + 1]
            
            # 格式化时间段字符串
            slot_str = f"{start.toString('HH:mm')}-{end.toString('HH:mm')}"
            time_slots.append(slot_str)
        
        return time_slots
    
    def _get_slot_duration_minutes(self, time_slot):
        """
        获取时间段的持续分钟数
        
        Args:
            time_slot: 时间段字符串，格式 "HH:mm-HH:mm"
            
        Returns:
            int: 持续分钟数
        """
        start_str, end_str = time_slot.split('-')
        start_time = QTime.fromString(start_str.strip(), "HH:mm")
        end_time = QTime.fromString(end_str.strip(), "HH:mm")
        
        start_minutes = start_time.hour() * 60 + start_time.minute()
        end_minutes = end_time.hour() * 60 + end_time.minute()
        
        return end_minutes - start_minutes
    
    def _group_by_weekday(self):
        """按星期分组"""
        weekday_schedules = {}
        for schedule in self.schedules:
            weekdays = schedule.get('weekdays', [1, 2, 3, 4, 5, 6, 7])
            for weekday in weekdays:
                if weekday not in weekday_schedules:
                    weekday_schedules[weekday] = []
                weekday_schedules[weekday].append(schedule)
        return weekday_schedules
    
    def _time_overlaps(self, slot_start, slot_end, task_start, task_end):
        """检查时间段是否重叠"""
        # 转换为分钟数便于比较
        slot_start_min = slot_start.hour() * 60 + slot_start.minute()
        slot_end_min = slot_end.hour() * 60 + slot_end.minute()
        task_start_min = task_start.hour() * 60 + task_start.minute()
        task_end_min = task_end.hour() * 60 + task_end.minute()
        
        # 检查重叠
        return not (task_end_min <= slot_start_min or task_start_min >= slot_end_min)
    
    def _create_time_indicator(self):
        """创建时间指示线"""
        if not self.config.is_time_indicator_enabled():
            return
        
        # 创建时间指示线（红色横线）
        self.time_indicator_line = QFrame(self.calendar_widget)
        self.time_indicator_line.setFrameShape(QFrame.HLine)
        self.time_indicator_line.setFrameShadow(QFrame.Plain)
        
        # 从配置获取样式
        color = self.config.get_time_indicator('color')
        width = self.config.get_time_indicator('width')
        opacity = self.config.get_time_indicator('opacity')
        
        self.time_indicator_line.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border: none;
                min-height: {width}px;
                max-height: {width}px;
            }}
        """)
        self.time_indicator_line.setWindowOpacity(opacity)
        self.time_indicator_line.raise_()  # 置于最上层
        
        # 创建时间标签（如果启用）
        if self.config.get_time_indicator('show_time_label'):
            self.time_indicator_label = QLabel(self.calendar_widget)
            self.time_indicator_label.setAlignment(Qt.AlignCenter)
            
            label_bg = self.config.get_time_indicator('time_label_bg')
            label_color = self.config.get_time_indicator('time_label_color')
            label_size = self.config.get_time_indicator('time_label_size')
            
            self.time_indicator_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {label_bg};
                    color: {label_color};
                    font-size: {label_size}px;
                    font-weight: bold;
                    padding: 2px 8px;
                    border-radius: 3px;
                }}
            """)
            self.time_indicator_label.raise_()  # 置于最上层
        
        # 初始更新位置
        self._update_time_indicator_position()
    
    def _start_time_update_timer(self):
        """启动时间更新定时器"""
        if not self.config.is_time_indicator_enabled():
            return
        
        # 获取更新间隔（毫秒）
        interval = self.config.get_time_indicator('update_interval')
        
        self.time_update_timer = QTimer(self)
        self.time_update_timer.timeout.connect(self._update_time_indicator_position)
        self.time_update_timer.start(interval)
    
    def _update_time_indicator_position(self):
        """更新时间指示线位置"""
        if not self.time_indicator_line or not hasattr(self, 'grid'):
            return
        
        # 获取当前时间和星期
        now = datetime.now()
        current_time = QTime(now.hour, now.minute)
        current_weekday = now.isoweekday()  # 1=周一, 7=周日
        
        # 更新时间标签文本
        if self.time_indicator_label:
            self.time_indicator_label.setText(now.strftime("%H:%M"))
        
        # 计算时间指示线的Y位置
        y_position = self._calculate_time_position(current_time)
        
        if y_position is None:
            # 当前时间不在显示范围内，隐藏指示线
            self.time_indicator_line.hide()
            if self.time_indicator_label:
                self.time_indicator_label.hide()
            return
        
        # 获取网格布局的几何信息
        if not self.grid.count():
            return
        
        # 获取表头（第0行）的widget来确定表头高度
        header_item = self.grid.itemAtPosition(0, 0)
        if not header_item or not header_item.widget():
            return
        header_widget = header_item.widget()
        header_height = header_widget.height()
        
        # 获取当前星期对应的列（1-7对应列1-7）
        weekday_col = current_weekday
        
        # 获取当前星期列的第一个单元格（第1行）来确定列的位置
        cell_item = self.grid.itemAtPosition(1, weekday_col)
        if not cell_item or not cell_item.widget():
            # 如果没有找到单元格，隐藏指示线
            self.time_indicator_line.hide()
            if self.time_indicator_label:
                self.time_indicator_label.hide()
            return
        
        # 获取单元格widget
        cell_widget = cell_item.widget()
        
        # 获取单元格在calendar_widget中的全局位置
        cell_global_pos = cell_widget.mapTo(self.calendar_widget, cell_widget.rect().topLeft())
        cell_x = cell_global_pos.x()
        cell_width = cell_widget.width()
        
        # 获取时间列的widget来确定时间列宽度
        time_col_item = self.grid.itemAtPosition(1, 0)
        if not time_col_item or not time_col_item.widget():
            return
        time_col_widget = time_col_item.widget()
        time_col_global_pos = time_col_widget.mapTo(self.calendar_widget, time_col_widget.rect().topLeft())
        time_col_x = time_col_global_pos.x()
        
        # 计算Y坐标（表头高度 + 时间段内的位置）
        y_pos = header_height + y_position
        
        # 显示指示线
        self.time_indicator_line.show()
        if self.time_indicator_label:
            self.time_indicator_label.show()
        
        # 设置指示线位置和宽度（仅在当前星期列）
        line_width = self.config.get_time_indicator('width')
        self.time_indicator_line.setGeometry(
            cell_x,  # X: 当前星期列的X坐标
            int(y_pos),  # Y: 计算出的位置
            cell_width,  # 宽度: 单元格宽度
            line_width  # 高度: 线宽
        )
        
        # 设置时间标签位置（在时间列中）
        if self.time_indicator_label:
            label_width = 60
            label_height = 20
            self.time_indicator_label.setGeometry(
                time_col_x + 5,  # X: 时间列内左侧
                int(y_pos - label_height / 2),  # Y: 居中对齐
                label_width,
                label_height
            )
    
    def _calculate_time_position(self, current_time):
        """
        计算当前时间在网格中的位置
        
        Args:
            current_time: QTime对象
            
        Returns:
            float: Y坐标位置（相对于网格顶部），如果不在范围内返回None
        """
        # 获取动态生成的时间段列表
        time_slots = self._generate_dynamic_time_slots()
        
        # 如果没有时间段，返回None
        if not time_slots:
            return None
        
        # 将当前时间转换为分钟数
        current_minutes = current_time.hour() * 60 + current_time.minute()
        
        # 遍历时间段，找到当前时间所在的位置
        for row, time_slot in enumerate(time_slots):
            start_str, end_str = time_slot.split('-')
            slot_start = QTime.fromString(start_str.strip(), "HH:mm")
            slot_end = QTime.fromString(end_str.strip(), "HH:mm")
            
            slot_start_min = slot_start.hour() * 60 + slot_start.minute()
            slot_end_min = slot_end.hour() * 60 + slot_end.minute()
            
            # 检查当前时间是否在这个时间段内
            if slot_start_min <= current_minutes < slot_end_min:
                # 获取该行实际的单元格高度（使用第一列的时间标签）
                time_cell_item = self.grid.itemAtPosition(row + 1, 0)
                if not time_cell_item or not time_cell_item.widget():
                    return None
                
                actual_cell_height = time_cell_item.widget().height()
                
                # 计算在时间段内的相对位置
                progress = (current_minutes - slot_start_min) / (slot_end_min - slot_start_min)
                
                # 计算Y坐标（累加前面所有行的高度 + 当前行内的位置）
                y_pos = 0
                for prev_row in range(row):
                    prev_cell_item = self.grid.itemAtPosition(prev_row + 1, 0)
                    if prev_cell_item and prev_cell_item.widget():
                        y_pos += prev_cell_item.widget().height()
                
                # 加上当前行内的位置
                y_pos += progress * actual_cell_height
                
                return y_pos
        
        # 当前时间不在任何时间段内
        return None
    
    def resizeEvent(self, event):
        """窗口大小改变时更新时间指示线位置"""
        super().resizeEvent(event)
        if self.time_indicator_line and hasattr(self, 'grid'):
            # 使用更长的延迟确保布局完成
            QTimer.singleShot(200, self._update_time_indicator_position)
    
    def showEvent(self, event):
        """显示时更新时间指示线位置"""
        super().showEvent(event)
        if self.time_indicator_line and hasattr(self, 'grid'):
            QTimer.singleShot(200, self._update_time_indicator_position)
