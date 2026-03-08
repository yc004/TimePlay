"""诊断播放问题"""
import os
import sys
from datetime import datetime

print("=" * 60)
print("播放系统诊断工具")
print("=" * 60)
print()

# 1. 检查当前时间
current_time = datetime.now()
print(f"1. 当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"   星期: {current_time.isoweekday()} (1=周一, 7=周日)")
print()

# 2. 检查配置文件
print("2. 检查配置文件:")
schedule_path = "config/schedule.json"
if os.path.exists(schedule_path):
    print(f"   ✓ {schedule_path} 存在")
    import json
    with open(schedule_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        schedules = data.get('schedules', [])
        print(f"   ✓ 找到 {len(schedules)} 个任务")
        print()
        for i, schedule in enumerate(schedules, 1):
            print(f"   任务 {i}: {schedule.get('name')}")
            print(f"      类型: {schedule.get('type')}")
            print(f"      时间: {schedule.get('start_time')} - {schedule.get('end_time')}")
            print(f"      星期: {schedule.get('weekdays')}")
            print(f"      启用: {schedule.get('enabled')}")
            
            # 检查是否在播放时间内
            start_time = schedule.get('start_time')
            end_time = schedule.get('end_time')
            current_time_str = current_time.strftime("%H:%M")
            current_weekday = current_time.isoweekday()
            
            weekdays = schedule.get('weekdays', [])
            in_weekday = current_weekday in weekdays
            
            # 简单的时间比较
            in_time = start_time <= current_time_str < end_time
            
            if in_weekday and in_time and schedule.get('enabled'):
                print(f"      状态: ✓ 应该正在播放")
            else:
                print(f"      状态: ✗ 不在播放时间")
                if not in_weekday:
                    print(f"         原因: 今天不在播放星期列表中")
                if not in_time:
                    print(f"         原因: 当前时间不在播放时间段内")
                if not schedule.get('enabled'):
                    print(f"         原因: 任务未启用")
            
            # 检查视频文件
            if schedule.get('type') == 'video':
                video_path = schedule.get('path')
                if video_path and os.path.exists(video_path):
                    size_mb = os.path.getsize(video_path) / (1024 * 1024)
                    print(f"      视频: ✓ 文件存在 ({size_mb:.1f} MB)")
                else:
                    print(f"      视频: ✗ 文件不存在或路径错误")
                    print(f"         路径: {video_path}")
            
            print()
else:
    print(f"   ✗ {schedule_path} 不存在")
    print()

# 3. 检查依赖
print("3. 检查依赖:")
try:
    import vlc
    print("   ✓ python-vlc 已安装")
except ImportError:
    print("   ✗ python-vlc 未安装")

try:
    from PyQt5.QtWidgets import QApplication
    print("   ✓ PyQt5 已安装")
except ImportError:
    print("   ✗ PyQt5 未安装")

try:
    from selenium import webdriver
    print("   ✓ selenium 已安装")
except ImportError:
    print("   ✗ selenium 未安装")

print()

# 4. 检查日志
print("4. 最近的日志 (最后10行):")
log_file = f"logs/tv_system_{current_time.strftime('%Y%m%d')}.log"
if os.path.exists(log_file):
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines[-10:]:
            print(f"   {line.rstrip()}")
else:
    print(f"   ✗ 日志文件不存在: {log_file}")

print()
print("=" * 60)
print("诊断完成")
print("=" * 60)
