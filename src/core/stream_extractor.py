"""直播流提取器 - 从网页中提取视频流URL"""
import time
import re
from PyQt5.QtCore import QUrl, QTimer, QObject, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
from src.utils.logger import Logger

class StreamExtractorPage(QWebEnginePage):
    """自定义页面，用于拦截网络请求"""
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        self.stream_urls = []
        self.logger = Logger()
    
    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        """拦截导航请求"""
        url_str = url.toString()
        
        # 检查是否是视频流URL
        if self._is_stream_url(url_str):
            self.logger.info(f"发现视频流: {url_str}")
            if url_str not in self.stream_urls:
                self.stream_urls.append(url_str)
        
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)
    
    def _is_stream_url(self, url):
        """判断是否是视频流URL"""
        stream_patterns = [
            r'\.m3u8',
            r'\.flv',
            r'\.mp4',
            r'\.ts',
            r'/live/',
            r'/stream/',
            r'hls',
            r'rtmp://',
        ]
        url_lower = url.lower()
        return any(re.search(pattern, url_lower) for pattern in stream_patterns)


class StreamExtractor(QObject):
    """直播流提取器"""
    stream_found = pyqtSignal(str)  # 找到流时发出信号
    extraction_failed = pyqtSignal(str)  # 提取失败时发出信号
    
    def __init__(self):
        super().__init__()
        self.logger = Logger()
        self.web_view = None
        self.page = None
        self.timeout_timer = None
        self.check_timer = None
        
    def extract_stream(self, url, timeout=15):
        """提取视频流URL"""
        self.logger.info(f"开始提取视频流: {url}")
        
        # 创建Profile
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # 创建自定义页面
        self.page = StreamExtractorPage(profile)
        
        # 创建WebView（隐藏）
        self.web_view = QWebEngineView()
        self.web_view.setPage(self.page)
        self.web_view.hide()
        
        # 页面加载完成后注入JavaScript
        self.web_view.loadFinished.connect(self._on_load_finished)
        
        # 加载页面
        self.web_view.load(QUrl(url))
        
        # 设置超时定时器
        self.timeout_timer = QTimer()
        self.timeout_timer.timeout.connect(self._on_timeout)
        self.timeout_timer.setSingleShot(True)
        self.timeout_timer.start(timeout * 1000)
        
        # 定期检查是否找到流
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self._check_streams)
        self.check_timer.start(1000)  # 每秒检查一次
    
    def _on_load_finished(self, ok):
        """页面加载完成"""
        if not ok:
            self.logger.error("页面加载失败")
            return
        
        self.logger.info("页面加载完成，开始提取视频流")
        
        # 注入JavaScript提取视频流
        js_code = """
        (function() {
            var streams = [];
            
            // 方法1: 查找video标签的src
            var videos = document.getElementsByTagName('video');
            for (var i = 0; i < videos.length; i++) {
                if (videos[i].src) {
                    streams.push(videos[i].src);
                }
                if (videos[i].currentSrc) {
                    streams.push(videos[i].currentSrc);
                }
            }
            
            // 方法2: 查找source标签
            var sources = document.getElementsByTagName('source');
            for (var i = 0; i < sources.length; i++) {
                if (sources[i].src) {
                    streams.push(sources[i].src);
                }
            }
            
            // 方法3: 尝试从页面脚本中提取
            var scripts = document.getElementsByTagName('script');
            for (var i = 0; i < scripts.length; i++) {
                var content = scripts[i].textContent || scripts[i].innerHTML;
                
                // 查找m3u8链接
                var m3u8Matches = content.match(/https?:\/\/[^\s"']+\.m3u8[^\s"']*/gi);
                if (m3u8Matches) {
                    streams = streams.concat(m3u8Matches);
                }
                
                // 查找flv链接
                var flvMatches = content.match(/https?:\/\/[^\s"']+\.flv[^\s"']*/gi);
                if (flvMatches) {
                    streams = streams.concat(flvMatches);
                }
            }
            
            // 方法4: 监听video元素的事件
            setTimeout(function() {
                var videos = document.getElementsByTagName('video');
                for (var i = 0; i < videos.length; i++) {
                    videos[i].play().catch(function(e) {});
                    if (videos[i].src) {
                        streams.push(videos[i].src);
                    }
                    if (videos[i].currentSrc) {
                        streams.push(videos[i].currentSrc);
                    }
                }
            }, 2000);
            
            return streams;
        })();
        """
        
        self.page.runJavaScript(js_code, self._on_js_result)
    
    def _on_js_result(self, result):
        """JavaScript执行结果"""
        if result:
            self.logger.info(f"JavaScript提取到 {len(result)} 个流")
            for stream_url in result:
                if stream_url and stream_url not in self.page.stream_urls:
                    self.page.stream_urls.append(stream_url)
    
    def _check_streams(self):
        """检查是否找到流"""
        if self.page and self.page.stream_urls:
            # 找到流，选择最佳的
            best_stream = self._select_best_stream(self.page.stream_urls)
            if best_stream:
                self.logger.info(f"成功提取视频流: {best_stream}")
                self._cleanup()
                self.stream_found.emit(best_stream)
    
    def _select_best_stream(self, streams):
        """选择最佳的视频流"""
        # 优先级: m3u8 > flv > mp4 > 其他
        m3u8_streams = [s for s in streams if '.m3u8' in s.lower()]
        if m3u8_streams:
            return m3u8_streams[0]
        
        flv_streams = [s for s in streams if '.flv' in s.lower()]
        if flv_streams:
            return flv_streams[0]
        
        mp4_streams = [s for s in streams if '.mp4' in s.lower()]
        if mp4_streams:
            return mp4_streams[0]
        
        return streams[0] if streams else None
    
    def _on_timeout(self):
        """超时处理"""
        self.logger.warning("视频流提取超时")
        self._cleanup()
        self.extraction_failed.emit("提取超时")
    
    def _cleanup(self):
        """清理资源"""
        if self.timeout_timer:
            self.timeout_timer.stop()
            self.timeout_timer = None
        
        if self.check_timer:
            self.check_timer.stop()
            self.check_timer = None
        
        if self.web_view:
            self.web_view.close()
            self.web_view = None
        
        self.page = None


class StreamCache:
    """视频流缓存"""
    def __init__(self):
        self.cache = {}
        self.logger = Logger()
    
    def get(self, url):
        """获取缓存的流URL"""
        return self.cache.get(url)
    
    def set(self, url, stream_url):
        """设置缓存"""
        self.cache[url] = stream_url
        self.logger.info(f"缓存视频流: {url} -> {stream_url}")
    
    def clear(self):
        """清除缓存"""
        self.cache.clear()
