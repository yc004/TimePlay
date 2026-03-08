"""基于Selenium的播放器 - 自动管理ChromeDriver"""
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from src.utils.logger import Logger

class SeleniumPlayerAuto:
    """基于Selenium的播放器 - 使用webdriver-manager自动管理ChromeDriver"""
    
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
            
            # 设置User-Agent
            chrome_options.add_argument(
                'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            )
            
            # 窗口设置
            if self.fullscreen:
                # Kiosk模式 - 完全隐藏所有浏览器UI并全屏
                chrome_options.add_argument(f'--window-position={self.position[0]},{self.position[1]}')
                chrome_options.add_argument(f'--window-size={self.size[0]},{self.size[1]}')
                chrome_options.add_argument('--kiosk')
            else:
                # 非全屏模式 - 使用App模式隐藏UI，但保持窗口大小可控
                # 注意：必须先设置位置和大小，再设置--app
                chrome_options.add_argument(f'--window-position={self.position[0]},{self.position[1]}')
                chrome_options.add_argument(f'--window-size={self.size[0]},{self.size[1]}')
                # 使用--app模式隐藏地址栏，但不指定URL（在get时加载）
                chrome_options.add_argument('--app=data:text/html,<html></html>')  # 临时页面            
            # 以下参数对全屏和非全屏都适用
            # 禁用浏览器UI元素
            chrome_options.add_argument('--disable-infobars')
            chrome_options.add_argument('--disable-translate')
            chrome_options.add_argument('--disable-features=TranslateUI')
            chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
            
            # 隐藏滚动条
            chrome_options.add_argument('--hide-scrollbars')
            
            # 禁用各种提示和通知
            chrome_options.add_experimental_option('prefs', {
                'profile.default_content_setting_values.notifications': 2,
                'credentials_enable_service': False,
                'profile.password_manager_enabled': False
            })
            
            # 合并excludeSwitches（只设置一次）
            chrome_options.add_experimental_option('excludeSwitches', [
                'enable-automation',
                'enable-logging'
            ])
            
            # 日志级别
            chrome_options.add_argument('--log-level=3')
            
            # 直接使用系统ChromeDriver，不进行检测和安装
            self.logger.info("使用系统ChromeDriver...")
            self.driver = webdriver.Chrome(options=chrome_options)
            self.logger.info("✓ ChromeDriver创建成功")
            
            # 移除webdriver标识
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    
                    window.chrome = {
                        runtime: {}
                    };
                    
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                    
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    
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
            
            # 调整窗口位置和大小（仅非全屏模式）
            # Kiosk模式下调用set_window_size会退出全屏
            if not self.fullscreen:
                self._adjust_window_position()
            
            # 隐藏可能残留的浏览器UI元素
            self._hide_browser_ui()
            
            # 自动播放
            self._auto_play()
            
            # 隐藏光标
            if self.fullscreen:
                self._hide_cursor()
            
            self.logger.info("✓ Selenium播放器启动成功")
            return True
            
        except WebDriverException as e:
            self.logger.error(f"ChromeDriver错误: {e}")
            self.logger.error("请运行: python install_chromedriver.py")
            return False
        except Exception as e:
            self.logger.error(f"启动播放器失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _auto_play(self):
        """自动播放视频"""
        try:
            self.logger.info("注入自动播放和全屏脚本...")
            
            # 读取外部JavaScript文件
            script_path = os.path.join(os.path.dirname(__file__), 'autoplay_script.js')
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    auto_play_script = f.read()
            except:
                # 如果文件不存在，使用简化的内联脚本
                auto_play_script = """
                (function() {
                    // 播放所有视频
                    var videos = document.getElementsByTagName('video');
                    for (var i = 0; i < videos.length; i++) {
                        videos[i].muted = false;
                        videos[i].play().catch(function() {
                            videos[i].muted = true;
                            videos[i].play();
                        });
                    }
                    
                    // 点击播放按钮
                    document.querySelectorAll('button[class*="play"], .vjs-big-play-button').forEach(function(btn) {
                        if (btn.offsetParent !== null) btn.click();
                    });
                    
                    // 强制播放器全屏
                    setTimeout(function() {
                        var player = document.querySelector('.player, .video-player, [class*="player"], video');
                        if (player) {
                            player.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:999999;background:#000';
                            document.body.style.overflow = 'hidden';
                        }
                    }, 3000);
                })();
                """
            
            self.driver.execute_script(auto_play_script)
            self.logger.info("✓ 自动播放和全屏脚本已注入")
            
        except Exception as e:
            self.logger.warning(f"自动播放失败: {e}")
    
    def _hide_cursor(self):
        """隐藏鼠标光标"""
        try:
            self.driver.execute_script("""
                var style = document.createElement('style');
                style.innerHTML = '* { cursor: none !important; }';
                document.head.appendChild(style);
            """)
            self.logger.info("✓ 已隐藏鼠标光标")
        except Exception as e:
            self.logger.warning(f"隐藏光标失败: {e}")
    
    def _hide_browser_ui(self):
        """隐藏浏览器UI元素（通过JavaScript）"""
        try:
            self.logger.info("隐藏浏览器UI元素...")
            
            hide_ui_script = """
            (function() {
                console.log('=== 隐藏浏览器UI ===');
                
                // 隐藏可能的浏览器UI元素
                var style = document.createElement('style');
                style.innerHTML = `
                    /* 隐藏滚动条 */
                    ::-webkit-scrollbar {
                        display: none !important;
                    }
                    
                    body {
                        overflow: hidden !important;
                        -ms-overflow-style: none !important;
                        scrollbar-width: none !important;
                    }
                    
                    /* 确保页面填满整个窗口 */
                    html, body {
                        margin: 0 !important;
                        padding: 0 !important;
                        width: 100vw !important;
                        height: 100vh !important;
                    }
                `;
                document.head.appendChild(style);
                
                console.log('✓ UI隐藏样式已应用');
            })();
            """
            
            self.driver.execute_script(hide_ui_script)
            self.logger.info("✓ 浏览器UI元素已隐藏")
            
        except Exception as e:
            self.logger.warning(f"隐藏浏览器UI失败: {e}")
    
    def _adjust_window_position(self):
        """调整窗口位置和大小（确保与配置一致）"""
        try:
            self.logger.info(f"调整窗口位置: x={self.position[0]}, y={self.position[1]}, w={self.size[0]}, h={self.size[1]}")
            
            # 使用Selenium API调整窗口（多次尝试确保生效）
            for attempt in range(3):
                try:
                    # 先设置位置
                    self.driver.set_window_position(self.position[0], self.position[1])
                    time.sleep(0.2)
                    
                    # 再设置大小
                    self.driver.set_window_size(self.size[0], self.size[1])
                    time.sleep(0.2)
                    
                    # 验证是否设置成功
                    actual_pos = self.driver.get_window_position()
                    actual_size = self.driver.get_window_size()
                    
                    pos_ok = abs(actual_pos['x'] - self.position[0]) < 10 and abs(actual_pos['y'] - self.position[1]) < 10
                    size_ok = abs(actual_size['width'] - self.size[0]) < 50 and abs(actual_size['height'] - self.size[1]) < 50
                    
                    if pos_ok and size_ok:
                        self.logger.info(f"✓ 窗口调整成功 (尝试 {attempt + 1}/3)")
                        break
                    else:
                        self.logger.warning(f"窗口大小未达到预期，重试... (尝试 {attempt + 1}/3)")
                        
                except Exception as e:
                    self.logger.warning(f"调整窗口失败 (尝试 {attempt + 1}/3): {e}")
                    if attempt == 2:
                        raise
            
            # 记录最终窗口位置
            try:
                actual_pos = self.driver.get_window_position()
                actual_size = self.driver.get_window_size()
                self.logger.info(f"最终窗口位置: x={actual_pos['x']}, y={actual_pos['y']}, w={actual_size['width']}, h={actual_size['height']}")
            except:
                pass
                
        except Exception as e:
            self.logger.warning(f"调整窗口位置失败: {e}")
    
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
            _ = self.driver.current_url
            return True
        except:
            return False
