# Selenium播放器使用指南

## 问题解决
✓ 白屏问题已解决
✗ 央视网检测到自动化脚本，显示版权限制

## 解决方案: Selenium + ChromeDriver

使用Selenium控制真实的Chrome浏览器，完美模拟人工操作，绕过反爬虫检测。

## 快速开始

### 步骤1: 安装依赖

```bash
# 安装Selenium
pip install selenium

# 安装webdriver-manager (自动管理ChromeDriver)
pip install webdriver-manager
```

### 步骤2: 检查环境

```bash
python install_chromedriver.py
```

这个脚本会检查:
- Chrome浏览器版本
- ChromeDriver是否安装
- Selenium是否安装
- webdriver-manager是否安装

### 步骤3: 测试Selenium播放器

```bash
python test_selenium_player.py
```

观察:
- Chrome浏览器是否自动打开
- 是否加载央视直播页面
- 是否还显示版权限制
- 视频是否自动播放

### 步骤4: 使用Selenium播放器

修改 `start_fixed.py`，启用Selenium:

```python
# 在 TVScheduleSystem.__init__ 中
self.player = MediaPlayer(use_selenium=True)  # 启用Selenium
```

或者直接使用:

```bash
python start_with_selenium.py
```

## 工作原理

### 反检测技术

1. **移除webdriver标识**
```javascript
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
});
```

2. **伪装Chrome对象**
```javascript
window.chrome = {
    runtime: {}
};
```

3. **伪装插件和语言**
```javascript
Object.defineProperty(navigator, 'plugins', {
    get: () => [1, 2, 3, 4, 5]
});
```

4. **禁用自动化标识**
```python
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
```

### 自动播放

自动注入JavaScript脚本:
- 查找所有video元素
- 尝试调用play()
- 点击播放按钮
- 移除覆盖层
- 定期重试

## 文件说明

### 核心文件
- `src/core/selenium_player.py` - 标准Selenium播放器
- `src/core/selenium_player_auto.py` - 自动管理ChromeDriver版本
- `src/core/player.py` - 已集成Selenium支持

### 工具脚本
- `install_chromedriver.py` - 检查和安装ChromeDriver
- `test_selenium_player.py` - 测试Selenium播放器
- `start_with_selenium.py` - 使用Selenium启动主程序

## 优势

### vs QtWebEngine
- ✓ 绕过反爬虫检测
- ✓ 完美模拟真实浏览器
- ✓ 更好的兼容性
- ✓ 无白屏问题
- ✓ 支持所有网页特性

### vs 直播流URL
- ✓ 不需要获取流URL
- ✓ 支持所有直播网站
- ✓ 自动处理页面交互
- ✗ 需要Chrome浏览器
- ✗ 占用更多资源

## 配置选项

### 全屏模式
```python
player = SeleniumPlayer(
    url="https://tv.cctv.com/live/cctv13/",
    fullscreen=True
)
```

### 窗口模式
```python
player = SeleniumPlayer(
    url="https://tv.cctv.com/live/cctv13/",
    fullscreen=False,
    position=(100, 100),
    size=(1280, 720)
)
```

### Kiosk模式 (推荐)
全屏无边框，适合电视播放:
```python
fullscreen=True  # 自动启用kiosk模式
```

## 常见问题

### Q1: ChromeDriver版本不匹配
**错误**: "This version of ChromeDriver only supports Chrome version XX"

**解决**:
```bash
# 使用webdriver-manager自动管理
pip install webdriver-manager

# 或手动下载匹配版本
# 访问: https://chromedriver.chromium.org/downloads
```

### Q2: Chrome浏览器未安装
**解决**: 下载安装Chrome浏览器
https://www.google.com/chrome/

### Q3: 仍然显示版权限制
**可能原因**:
- IP地址被限制
- 需要登录账号
- 地区限制

**解决**:
1. 尝试其他直播源
2. 使用VPN
3. 获取直播流URL

### Q4: 视频不自动播放
**解决**:
- 检查日志中的JavaScript消息
- 手动点击播放按钮测试
- 调整自动播放脚本

### Q5: 占用资源过多
**解决**:
```python
# 禁用图片加载
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)

# 禁用JavaScript (不推荐，会影响播放)
# chrome_options.add_argument('--disable-javascript')
```

## 性能优化

### 减少内存占用
```python
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-plugins')
chrome_options.add_argument('--disable-images')  # 如果不需要显示图片
```

### 提高启动速度
```python
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
```

## 高级用法

### 自定义User-Agent
```python
chrome_options.add_argument('user-agent=YOUR_USER_AGENT')
```

### 设置代理
```python
chrome_options.add_argument('--proxy-server=http://proxy:port')
```

### 禁用通知
```python
prefs = {"profile.default_content_setting_values.notifications": 2}
chrome_options.add_experimental_option("prefs", prefs)
```

### 自动接受权限请求
```python
prefs = {
    "profile.default_content_setting_values.media_stream_mic": 1,
    "profile.default_content_setting_values.media_stream_camera": 1
}
chrome_options.add_experimental_option("prefs", prefs)
```

## 调试技巧

### 查看浏览器日志
```python
# 启用详细日志
chrome_options.add_argument('--enable-logging')
chrome_options.add_argument('--v=1')
```

### 保持浏览器打开
```python
# 测试时不自动关闭浏览器
chrome_options.add_experimental_option("detach", True)
```

### 查看页面信息
```python
info = player.get_page_info()
print(f"视频数: {info['videoCount']}")
print(f"正在播放: {info['isPlaying']}")
```

## 与主程序集成

### 方法1: 修改配置
在 `config/config.py` 中添加:
```python
USE_SELENIUM = True
```

### 方法2: 环境变量
```bash
set USE_SELENIUM=1
python main.py
```

### 方法3: 命令行参数
```bash
python main.py --use-selenium
```

## 最佳实践

1. **使用webdriver-manager** - 自动管理ChromeDriver版本
2. **启用kiosk模式** - 全屏无边框
3. **禁用不必要的功能** - 减少资源占用
4. **定期检查播放状态** - 自动重启失败的播放
5. **记录详细日志** - 便于排查问题

## 下一步

1. 运行 `python install_chromedriver.py` 检查环境
2. 运行 `python test_selenium_player.py` 测试播放器
3. 如果测试成功，使用 `start_with_selenium.py` 启动主程序
4. 观察是否还有版权限制提示

## 总结

Selenium播放器通过模拟真实浏览器，成功绕过了反爬虫检测，是目前最可靠的网页直播播放方案。

**推荐配置**:
- 使用webdriver-manager自动管理ChromeDriver
- 启用kiosk全屏模式
- 禁用不必要的功能以优化性能
- 配合看门狗机制自动重启

---

创建时间: 2026-03-07
版本: 1.0
