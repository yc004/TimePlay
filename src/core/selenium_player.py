"""基于Selenium的直播播放器 - 绕过反爬虫检测"""
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from src.utils.logger import Logger

class SeleniumPlayer:
    """基于Selenium的播放器 - 模拟真实浏览器"""
    
    def __init__(self, url, fullscreen=True, position=None, size=None):
        """
        初始化Selenium播放器
        
        Args:
            url: 直播URL
            fullscreen: 是否全屏
            position: 窗口位置 (x, y)
            size: 窗口大小 (width, height)
        """
        self.url = url
        self.fullscreen = fullscreen
        self.position = position or (0, 0)
        self.size = size or (1920, 1080)
        self.driver = None
        self.logger = Logger()
        
    def start(self):
        """启动播放器"""
        try:
            self.logger.info(f"启动Selenium播放器: {self.url}")
            
            # 配置Chrome选项
            chrome_options = Options()
            
            # 关键: 反检测配置
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 性能优化
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            # 禁用不必要的功能
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-popup-blocking')
            
            # 自动播放媒体
            chrome_options.add_argument('--autoplay-policy=no-user-gesture-required')
            
            # 设置User-Agent (模拟真实浏览器)
            chrome_options.add_argument(
                'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            )
            
            # 窗口设置
            if self.fullscreen:
                chrome_options.add_argument('--start-fullscreen')
                chrome_options.add_argument('--kiosk')  # Kiosk模式，无边框全屏
            else:
                chrome_options.add_argument(f'--window-position={self.position[0]},{self.position[1]}')
                chrome_options.add_argument(f'--window-size={self.size[0]},{self.size[1]}')
            
            # 日志级别
            chrome_options.add_argument('--log-level=3')  # 只显示严重错误
            
            # 创建driver
            self.logger.info("初始化ChromeDriver...")
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # 关键: 移除webdriver标识
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    
                    // 伪装Chrome对象
                    window.chrome = {
                        runtime: {}
                    };
                    
                    // 伪装权限
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                    
                    // 伪装插件
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    
                    // 伪装语言
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['zh-CN', 'zh', 'en']
                    });
                '''
            })
            
            self.logger.info(f"加载页面: {self.url}")
            self.driver.get(self.url)
            
            # 等待页面加载
            self.logger.info("等待页面加载...")
            time.sleep(3)
            
            # 尝试自动播放
            self._auto_play()
            
            # 隐藏鼠标光标（如果全屏）
            if self.fullscreen:
                self._hide_cursor()
            
            self.logger.info("✓ Selenium播放器启动成功")
            return True
            
        except WebDriverException as e:
            self.logger.error(f"ChromeDriver错误: {e}")
            self.logger.error("请确保已安装ChromeDriver，并且版本与Chrome浏览器匹配")
            return False
        except Exception as e:
            self.logger.error(f"启动播放器失败: {e}")
            return False
    
    def _auto_play(self):
        """自动播放视频"""
        try:
            self.logger.info("尝试自动播放...")
            
            # 注入自动播放脚本
            auto_play_script = """
            (function() {
                console.log('=== 自动播放脚本开始 ===');
                
                // 查找并播放所有视频
                function playVideos() {
                    var videos = document.getElementsByTagName('video');
                    console.log('找到 ' + videos.length + ' 个视频元素');
                    
                    for (var i = 0; i < videos.length; i++) {
                        var video = videos[i];
                        video.muted = false;
                        video.autoplay = true;
                        video.controls = false;  // 隐藏控制条
                        
                        video.play().then(function() {
                            console.log('✓ 视频播放成功');
                        }).catch(function(err) {
                            console.log('尝试静音播放...');
                            video.muted = true;
                            video.play().catch(function(e) {
                                console.log('✗ 播放失败:', e);
                            });
                        });
                    }
                }
                
                // 点击播放按钮
                function clickPlayButtons() {
                    var selectors = [
                        'button[class*="play"]',
                        'div[class*="play"]',
                        '.vjs-big-play-button',
                        '[aria-label*="播放"]',
                        '[aria-label*="play"]'
                    ];
                    
                    selectors.forEach(function(sel) {
                        var buttons = document.querySelectorAll(sel);
                        buttons.forEach(function(btn) {
                            if (btn.offsetParent !== null) {
                                console.log('点击播放按钮:', sel);
                                btn.click();
                            }
                        });
                    });
                }
                
                // 移除覆盖层
                function removeOverlays() {
                    var overlays = document.querySelectorAll(
                        '[class*="overlay"], [class*="mask"], [class*="cover"], [class*="modal"]'
                    );
                    overlays.forEach(function(el) {
                        el.style.display = 'none';
                    });
                }
                
                // 立即执行
                playVideos();
                clickPlayButtons();
                removeOverlays();
                
                // 定期重试
                var retries = 0;
                var interval = setInterval(function() {
                    retries++;
                    if (retries > 10) {
                        clearInterval(interval);
                        return;
                    }
                    
                    playVideos();
                    clickPlayButtons();
                    
                    // 检查是否有视频在播放
                    var videos = document.getElementsByTagName('video');
                    for (var i = 0; i < videos.length; i++) {
                        if (!videos[i].paused) {
                            console.log('✓ 检测到视频正在播放');
                            clearInterval(interval);
                            return;
                        }
                    }
                }, 2000);
                
                console.log('=== 自动播放脚本已激活 ===');
            })();
            """
            
            self.driver.execute_script(auto_play_script)
            self.logger.info("✓ 自动播放脚本已注入")
            
        except Exception as e:
            self.logger.warning(f"自动播放失败: {e}")
    
    def _hide_cursor(self):
        """隐藏鼠标光标"""
        try:
            hide_cursor_script = """
            var style = document.createElement('style');
            style.innerHTML = '* { cursor: none !important; }';
            document.head.appendChild(style);
            """
            self.driver.execute_script(hide_cursor_script)
            self.logger.info("✓ 已隐藏鼠标光标")
        except Exception as e:
            self.logger.warning(f"隐藏光标失败: {e}")
    
    def refresh(self):
        """刷新页面"""
        if self.driver:
            self.logger.info("刷新页面...")
            self.driver.refresh()
            time.sleep(3)
            self._auto_play()
    
    def stop(self):
        """停止播放器"""
        if self.driver:
            self.logger.info("关闭Selenium播放器")
            try:
                # 先尝试正常关闭
                self.driver.quit()
                self.logger.info("✓ 浏览器已正常关闭")
            except Exception as e:
                self.logger.error(f"关闭driver时出错: {e}")
                # 如果quit失败，尝试强制关闭
                try:
                    self.logger.info("尝试强制关闭浏览器...")
                    self.driver.close()
                    self.driver.quit()
                    self.logger.info("✓ 浏览器已强制关闭")
                except Exception as e2:
                    self.logger.error(f"强制关闭也失败: {e2}")
                    # 最后尝试：直接终止进程
                    try:
                        import psutil
                        import os
                        current_pid = os.getpid()
                        for proc in psutil.process_iter(['pid', 'name']):
                            try:
                                # 查找Chrome进程（排除当前进程）
                                if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                                    if proc.info['pid'] != current_pid:
                                        proc.kill()
                                        self.logger.info(f"✓ 已终止Chrome进程: {proc.info['pid']}")
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass
                    except ImportError:
                        self.logger.warning("psutil未安装，无法强制终止进程")
                    except Exception as e3:
                        self.logger.error(f"终止进程失败: {e3}")
            finally:
                self.driver = None
    
    def is_running(self):
        """检查播放器是否运行中"""
        if not self.driver:
            return False
        try:
            # 尝试获取当前URL，如果失败说明浏览器已关闭
            _ = self.driver.current_url
            return True
        except:
            return False
    
    def execute_script(self, script):
        """执行JavaScript脚本"""
        if self.driver:
            return self.driver.execute_script(script)
        return None
    
    def get_page_info(self):
        """获取页面信息"""
        if not self.driver:
            return None
        
        try:
            info_script = """
            return {
                url: window.location.href,
                title: document.title,
                videoCount: document.getElementsByTagName('video').length,
                hasVideo: document.getElementsByTagName('video').length > 0,
                isPlaying: (function() {
                    var videos = document.getElementsByTagName('video');
                    for (var i = 0; i < videos.length; i++) {
                        if (!videos[i].paused) return true;
                    }
                    return false;
                })()
            };
            """
            return self.driver.execute_script(info_script)
        except Exception as e:
            self.logger.warning(f"获取页面信息失败: {e}")
            return None


class SeleniumPlayerManager:
    """Selenium播放器管理器"""
    
    def __init__(self):
        self.current_player = None
        self.logger = Logger()
    
    def play(self, url, fullscreen=True, position=None, size=None):
        """播放直播"""
        # 停止当前播放
        self.stop()
        
        # 创建新播放器
        self.current_player = SeleniumPlayer(url, fullscreen, position, size)
        
        # 启动播放
        success = self.current_player.start()
        
        if not success:
            self.current_player = None
            return False
        
        return True
    
    def stop(self):
        """停止播放"""
        if self.current_player:
            self.current_player.stop()
            self.current_player = None
    
    def refresh(self):
        """刷新当前播放"""
        if self.current_player:
            self.current_player.refresh()
    
    def is_playing(self):
        """检查是否正在播放"""
        if not self.current_player:
            return False
        return self.current_player.is_running()
    
    def get_info(self):
        """获取当前播放信息"""
        if self.current_player:
            return self.current_player.get_page_info()
        return None
