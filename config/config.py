"""系统配置文件"""

# 播放器配置
PLAYER_CONFIG = {
    'default_fullscreen': True,
    'default_topmost': True,
    'auto_restart_on_error': True,
    'max_retry_times': 3
}

# 安全配置
SAFETY_CONFIG = {
    'enable_watchdog': True,  # 启用看门狗
    'check_interval': 60,  # 检查间隔(秒)
    'backup_content': 'videos/default.mp4',  # 备用内容
    'enable_heartbeat': True  # 启用心跳检测
}

# 日志配置
LOG_CONFIG = {
    'log_dir': 'logs',
    'max_log_days': 30,  # 日志保留天数
    'log_level': 'INFO'
}

# 网络配置
NETWORK_CONFIG = {
    'connection_timeout': 10,  # 连接超时(秒)
    'retry_interval': 5,  # 重试间隔(秒)
    'max_retry': 3  # 最大重试次数
}
