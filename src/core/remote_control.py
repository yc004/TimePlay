"""远程控制服务器模块"""
from flask import Flask, request, jsonify
import threading
from src.utils.logger import Logger
from src.core.emergency_broadcast import EmergencyBroadcast

class RemoteControlServer:
    def __init__(self, player, schedule_system, port=5000):
        self.app = Flask(__name__)
        self.player = player
        self.schedule_system = schedule_system
        self.logger = Logger()
        self.port = port
        self.emergency = EmergencyBroadcast(player)
        self.setup_routes()
        
    def setup_routes(self):
        """设置API路由"""
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """获取系统状态"""
            return jsonify({
                'status': 'running',
                'schedules_count': len(self.schedule_system.schedules),
                'is_playing': self.player.current_window is not None
            })
        
        @self.app.route('/api/schedules', methods=['GET'])
        def get_schedules():
            """获取播放时间表"""
            return jsonify({
                'schedules': self.schedule_system.schedules
            })
        
        @self.app.route('/api/emergency', methods=['POST'])
        def emergency_broadcast():
            """紧急插播"""
            data = request.json
            content_type = data.get('type')
            content_path = data.get('path')
            duration = data.get('duration', 0)
            message = data.get('message', '')
            
            success = self.emergency.trigger(content_type, content_path, duration, message)
            
            return jsonify({
                'success': success,
                'message': '紧急插播已触发' if success else '紧急插播失败'
            })
        
        @self.app.route('/api/stop', methods=['POST'])
        def stop_playback():
            """停止播放"""
            self.player.stop_current()
            return jsonify({
                'success': True,
                'message': '播放已停止'
            })
        
        @self.app.route('/api/reload', methods=['POST'])
        def reload_schedule():
            """重新加载时间表"""
            try:
                self.schedule_system.load_schedules()
                self.schedule_system.setup_schedule()
                return jsonify({
                    'success': True,
                    'message': '时间表已重新加载'
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'重新加载失败: {e}'
                })
    
    def start(self):
        """启动远程控制服务器"""
        def run():
            self.logger.info(f"远程控制服务器启动在端口 {self.port}")
            self.app.run(host='0.0.0.0', port=self.port, debug=False)
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
