"""将旧格式的schedule.json迁移到新的播放列表格式"""
import json
import os
import shutil
from datetime import datetime

def migrate_schedule(input_file='config/schedule.json', output_file=None, backup=True):
    """
    迁移时间表配置
    
    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径（默认覆盖输入文件）
        backup: 是否备份原文件
    """
    if not os.path.exists(input_file):
        print(f"错误: 文件不存在 - {input_file}")
        return False
    
    # 读取原配置
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    schedules = data.get('schedules', [])
    if not schedules:
        print("配置文件中没有任务")
        return False
    
    print(f"找到 {len(schedules)} 个任务")
    print()
    
    # 备份原文件
    if backup:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{input_file}.backup_{timestamp}"
        shutil.copy2(input_file, backup_file)
        print(f"已备份原文件到: {backup_file}")
        print()
    
    # 迁移任务
    migrated_schedules = []
    for i, schedule in enumerate(schedules, 1):
        schedule_type = schedule.get('type')
        name = schedule.get('name', f'任务{i}')
        
        print(f"处理任务 {i}: {name} (类型: {schedule_type})")
        
        if schedule_type == 'playlist':
            # 已经是播放列表格式，保持不变
            print("  ✓ 已是播放列表格式，保持不变")
            migrated_schedules.append(schedule)
        
        elif schedule_type == 'video':
            # 转换视频任务为播放列表
            print("  → 转换为播放列表格式")
            new_schedule = {
                'name': name,
                'start_time': schedule.get('start_time'),
                'end_time': schedule.get('end_time'),
                'weekdays': schedule.get('weekdays', [1,2,3,4,5,6,7]),
                'type': 'playlist',
                'fullscreen': schedule.get('fullscreen', True),
                'topmost': schedule.get('topmost', True),
                'enabled': schedule.get('enabled', True),
                'loop': schedule.get('loop', True),
                'playlist': [
                    {
                        'type': 'video',
                        'path': schedule.get('path'),
                        'loop': schedule.get('loop', False),
                        'comment': f'从单个视频任务迁移'
                    }
                ],
                'id': schedule.get('id', i)
            }
            migrated_schedules.append(new_schedule)
            print(f"  ✓ 已转换")
        
        elif schedule_type == 'web':
            # 转换网页任务为播放列表
            print("  → 转换为播放列表格式")
            new_schedule = {
                'name': name,
                'start_time': schedule.get('start_time'),
                'end_time': schedule.get('end_time'),
                'weekdays': schedule.get('weekdays', [1,2,3,4,5,6,7]),
                'type': 'playlist',
                'fullscreen': schedule.get('fullscreen', True),
                'topmost': schedule.get('topmost', True),
                'enabled': schedule.get('enabled', True),
                'loop': True,
                'playlist': [
                    {
                        'type': 'web',
                        'url': schedule.get('url'),
                        'duration': 300,  # 默认5分钟
                        'comment': f'从单个网页任务迁移'
                    }
                ],
                'id': schedule.get('id', i)
            }
            migrated_schedules.append(new_schedule)
            print(f"  ✓ 已转换")
        
        else:
            print(f"  ✗ 未知类型: {schedule_type}，跳过")
        
        print()
    
    # 保存新配置
    new_data = {'schedules': migrated_schedules}
    
    output_path = output_file or input_file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)
    
    print("=" * 60)
    print(f"迁移完成！")
    print(f"原任务数: {len(schedules)}")
    print(f"新任务数: {len(migrated_schedules)}")
    print(f"输出文件: {output_path}")
    if backup:
        print(f"备份文件: {backup_file}")
    print("=" * 60)
    
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("时间表配置迁移工具")
    print("=" * 60)
    print()
    print("此工具将旧格式的配置转换为新的播放列表格式")
    print()
    
    # 检查配置文件
    config_file = 'config/schedule.json'
    if not os.path.exists(config_file):
        print(f"错误: 配置文件不存在 - {config_file}")
        return
    
    # 询问用户
    print(f"将要迁移: {config_file}")
    print("原文件将被自动备份")
    print()
    
    response = input("是否继续? (y/n): ").strip().lower()
    if response != 'y':
        print("已取消")
        return
    
    print()
    print("=" * 60)
    print()
    
    # 执行迁移
    success = migrate_schedule(config_file)
    
    if success:
        print()
        print("请检查新配置文件，确认迁移正确后重启播放系统")
    else:
        print()
        print("迁移失败，请检查错误信息")

if __name__ == '__main__':
    main()
