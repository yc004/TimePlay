"""基于浏览器的直播播放器 - 直接在浏览器中播放视频"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings, QWebEngineProfile, QWebEnginePage
from src.utils.logger import Logger

class BrowserPlayerPage(QWebEnginePage):
    """自定义页面，用于控制播放"""
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)
        self.logger = Logger()
    
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        """捕获JavaScript控制台消息 - 用于调试"""
        self.logger.info(f"浏览器JS [{level}]: {message} (行{lineNumber})")
    
    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        """拦截导航请求"""
        self.logger.info(f"导航请求: {url.toString()}")
        return True


class BrowserPlayer(QWidget):
    """基于浏览器的播放器 - 直接显示浏览器窗口"""
    def __init__(self, url, parent=None):
        super().__init__(parent)
        self.url = url
        self.logger = Logger()
        self.auto_play_timer = None
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 设置背景色为黑色
        self.setStyleSheet("background-color: #000000;")
        
        # 配置 Profile
        profile = QWebEngineProfile.defaultProfile()
        
        # 设置User-Agent
        profile.setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # 启用持久化存储
        profile.setPersistentCookiesPolicy(QWebEngineProfile.AllowPersistentCookies)
        
        # 创建自定义页面
        page = BrowserPlayerPage(profile)
        
        # 创建WebView
        self.web_view = QWebEngineView()
        self.web_view.setPage(page)
        
        # 设置WebView背景色
        self.web_view.setStyleSheet("background-color: #000000;")
        
        # 配置设置 - 启用所有必要的功能
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
        settings.setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.AllowWindowActivationFromJavaScript, True)
        settings.setAttribute(QWebEngineSettings.ShowScrollBars, False)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
        
        # 页面加载完成后的处理
        self.web_view.loadFinished.connect(self.on_load_finished)
        self.web_view.loadProgress.connect(self.on_load_progress)
        
        # 加载URL
        self.logger.info(f"开始加载直播页面: {self.url}")
        self.load_url(self.url)
        
        layout.addWidget(self.web_view)
    
    def on_load_progress(self, progress):
        """页面加载进度"""
        if progress % 20 == 0:  # 每20%记录一次
            self.logger.info(f"页面加载进度: {progress}%")
    
    def load_url(self, url):
        """加载URL"""
        # 直接加载URL，不使用iframe
        self.logger.info(f"直接加载URL: {url}")
        self.web_view.load(QUrl(url))
    
    def on_load_finished(self, ok):
        """页面加载完成"""
        if not ok:
            self.logger.error("页面加载失败")
            # 显示错误信息
            error_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {
                        background: #000;
                        color: #fff;
                        font-family: Arial, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                    }
                    .error {
                        text-align: center;
                        font-size: 24px;
                    }
                </style>
            </head>
            <body>
                <div class="error">
                    <h1>页面加载失败</h1>
                    <p>无法加载直播页面</p>
                    <p>请检查网络连接或URL是否正确</p>
                </div>
            </body>
            </html>
            """
            self.web_view.setHtml(error_html)
            return
        
        self.logger.info("页面加载完成，准备注入自动播放脚本")
        
        # 先检查页面内容
        self.check_page_content()
        
        # 延迟注入JavaScript，确保页面完全加载
        self.auto_play_timer = QTimer()
        self.auto_play_timer.timeout.connect(self.inject_autoplay_script)
        self.auto_play_timer.setSingleShot(True)
        self.auto_play_timer.start(3000)  # 3秒后注入
    
    def check_page_content(self):
        """检查页面内容"""
        check_js = """
        (function() {
            return {
                title: document.title,
                bodyText: document.body ? document.body.innerText.substring(0, 200) : 'no body',
                videoCount: document.getElementsByTagName('video').length,
                iframeCount: document.getElementsByTagName('iframe').length,
                hasError: document.body ? document.body.innerText.includes('错误') || document.body.innerText.includes('error') : false
            };
        })();
        """
        self.web_view.page().runJavaScript(check_js, self._on_page_check)
    
    def _on_page_check(self, result):
        """页面检查结果"""
        if result:
            self.logger.info(f"页面信息: 标题={result.get('title')}, 视频数={result.get('videoCount')}, iframe数={result.get('iframeCount')}")
            if result.get('hasError'):
                self.logger.warning(f"页面可能有错误: {result.get('bodyText')}")
    
    def inject_autoplay_script(self):
        """注入自动播放和全屏脚本"""
        self.logger.info("注入自动播放和全屏脚本")
        
        js_code = """
        (function() {
            console.log('=== 自动播放和全屏脚本开始 ===');
            
            document.body.style.backgroundColor = '#000';
            document.documentElement.style.backgroundColor = '#000';
            
            function playAllVideos() {
                var videos = document.getElementsByTagName('video');
                console.log('找到 ' + videos.length + ' 个视频元素');
                
                for (var i = 0; i < videos.length; i++) {
                    var video = videos[i];
                    video.style.display = 'block';
                    video.style.visibility = 'visible';
                    video.style.opacity = '1';
                    video.muted = false;
                    video.autoplay = true;
                    video.controls = false;
                    video.playsInline = true;
                    
                    var playPromise = video.play();
                    if (playPromise !== undefined) {
                        playPromise.then(function() {
                            console.log('视频播放成功');
                        }).catch(function(error) {
                            console.log('视频播放失败:', error);
                            video.muted = true;
                            video.play().catch(function(e) {
                                console.log('静音播放也失败:', e);
                            });
                        });
                    }
                }
                return videos.length;
            }
            
            function clickPlayButtons() {
                var selectors = [
                    'button[class*="play"]',
                    'div[class*="play"]',
                    '.vjs-big-play-button',
                    '[aria-label*="播放"]'
                ];
                
                var clickCount = 0;
                selectors.forEach(function(selector) {
                    var buttons = document.querySelectorAll(selector);
                    buttons.forEach(function(button) {
                        if (button.offsetParent !== null) {
                            button.click();
                            clickCount++;
                        }
                    });
                });
                return clickCount;
            }
            
            function tryFullscreen() {
                var videos = document.getElementsByTagName('video');
                if (videos.length > 0) {
                    var video = videos[0];
                    
                    // 先尝试视频元素的全屏API
                    if (video.requestFullscreen) {
                        video.requestFullscreen().then(function() {
                            console.log('视频全屏成功');
                        }).catch(function(err) {
                            console.log('视频全屏失败:', err);
                            // 如果API失败，使用CSS强制全屏
                            forceVideoFullscreen(video);
                        });
                    } else if (video.webkitRequestFullscreen) {
                        video.webkitRequestFullscreen();
                    } else {
                        // 如果不支持全屏API，使用CSS强制全屏
                        forceVideoFullscreen(video);
                    }
                } else {
                    var elem = document.documentElement;
                    if (elem.requestFullscreen) {
                        elem.requestFullscreen().catch(function(err) {
                            console.log('文档全屏失败:', err);
                        });
                    } else if (elem.webkitRequestFullscreen) {
                        elem.webkitRequestFullscreen();
                    }
                }
            }
            
            function forceVideoFullscreen(video) {
                console.log('使用CSS强制视频全屏...');
                
                // 设置视频样式为全屏
                video.style.position = 'fixed';
                video.style.top = '0';
                video.style.left = '0';
                video.style.width = '100vw';
                video.style.height = '100vh';
                video.style.zIndex = '999999';
                video.style.objectFit = 'contain';
                video.style.backgroundColor = '#000';
                
                // 隐藏其他元素
                document.body.style.overflow = 'hidden';
                
                // 隐藏页面其他内容
                var allElements = document.body.children;
                for (var i = 0; i < allElements.length; i++) {
                    if (!allElements[i].contains(video)) {
                        allElements[i].style.display = 'none';
                    }
                }
                
                console.log('CSS强制全屏已应用');
            }
            
            function forcePlayerFullscreen() {
                console.log('尝试强制播放器全屏...');
                
                // 查找播放器容器
                var playerSelectors = [
                    '.player',
                    '.video-player',
                    '[class*="player"]',
                    '[id*="player"]',
                    'video'
                ];
                
                var player = null;
                for (var i = 0; i < playerSelectors.length; i++) {
                    var elements = document.querySelectorAll(playerSelectors[i]);
                    if (elements.length > 0) {
                        player = elements[0];
                        break;
                    }
                }
                
                if (player) {
                    console.log('找到播放器，应用全屏样式');
                    player.style.position = 'fixed';
                    player.style.top = '0';
                    player.style.left = '0';
                    player.style.width = '100vw';
                    player.style.height = '100vh';
                    player.style.zIndex = '999999';
                    
                    // 如果播放器内有视频，也设置视频样式
                    var videos = player.getElementsByTagName('video');
                    if (videos.length > 0) {
                        videos[0].style.width = '100%';
                        videos[0].style.height = '100%';
                        videos[0].style.objectFit = 'contain';
                    }
                }
            }
            
            function clickFullscreenButtons() {
                var selectors = [
                    'button[class*="fullscreen"]',
                    '[aria-label*="全屏"]',
                    '.vjs-fullscreen-control'
                ];
                
                var clicked = false;
                selectors.forEach(function(sel) {
                    if (!clicked) {
                        var buttons = document.querySelectorAll(sel);
                        buttons.forEach(function(btn) {
                            if (btn.offsetParent !== null && !clicked) {
                                btn.click();
                                clicked = true;
                            }
                        });
                    }
                });
                return clicked;
            }
            
            playAllVideos();
            clickPlayButtons();
            
            setTimeout(function() {
                // 先尝试点击全屏按钮
                var clicked = clickFullscreenButtons();
                
                // 如果没有找到全屏按钮，使用API
                if (!clicked) {
                    tryFullscreen();
                }
                
                // 无论如何，都尝试强制播放器全屏
                setTimeout(function() {
                    forcePlayerFullscreen();
                }, 1000);
            }, 3000);
            
            var retryCount = 0;
            var retryInterval = setInterval(function() {
                retryCount++;
                playAllVideos();
                clickPlayButtons();
                
                var videos = document.getElementsByTagName('video');
                var hasPlaying = false;
                for (var i = 0; i < videos.length; i++) {
                    if (!videos[i].paused) {
                        hasPlaying = true;
                        break;
                    }
                }
                
                if (hasPlaying || retryCount >= 15) {
                    clearInterval(retryInterval);
                }
            }, 2000);
            
            console.log('=== 脚本已注入 ===');
        })();
        """
        
        self.web_view.page().runJavaScript(js_code)
        self.logger.info("自动播放和全屏脚本已注入")
    
    def cleanup(self):
        """清理资源"""
        if self.auto_play_timer:
            self.auto_play_timer.stop()
            self.auto_play_timer = None
