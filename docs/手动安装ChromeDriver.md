# 手动安装ChromeDriver指南

## 问题
webdriver-manager无法自动下载ChromeDriver（网络问题）

## 解决方案：手动安装

### 步骤1: 检查Chrome版本

1. 打开Chrome浏览器
2. 点击右上角三个点 → 帮助 → 关于Google Chrome
3. 记下版本号，例如：`120.0.6099.109`
4. 主版本号是第一个数字，例如：`120`

### 步骤2: 下载ChromeDriver

#### 方法A: 官方下载（推荐）

1. 访问：https://googlechromelabs.github.io/chrome-for-testing/
2. 找到与你的Chrome版本匹配的ChromeDriver
3. 下载Windows版本（chromedriver-win64.zip）

#### 方法B: 镜像下载（国内推荐）

1. 访问淘宝镜像：https://registry.npmmirror.com/binary.html?path=chromedriver/
2. 找到对应版本号的文件夹
3. 下载 `chromedriver_win32.zip`

#### 方法C: 直接下载链接

Chrome 120版本示例：
```
https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/120.0.6099.109/win64/chromedriver-win64.zip
```

替换版本号为你的Chrome版本。

### 步骤3: 安装ChromeDriver

#### 方法1: 添加到系统PATH（推荐）

1. 解压下载的zip文件
2. 将 `chromedriver.exe` 复制到一个固定位置，例如：
   ```
   C:\Program Files\ChromeDriver\chromedriver.exe
   ```

3. 添加到系统PATH：
   - 右键"此电脑" → 属性
   - 高级系统设置 → 环境变量
   - 在"系统变量"中找到"Path"
   - 点击"编辑" → "新建"
   - 添加：`C:\Program Files\ChromeDriver`
   - 确定保存

4. 验证安装：
   ```bash
   # 打开新的命令提示符
   chromedriver --version
   ```

#### 方法2: 放在项目目录

1. 解压下载的zip文件
2. 将 `chromedriver.exe` 复制到项目根目录
3. 修改代码使用本地路径（见下文）

### 步骤4: 验证安装

运行测试：
```bash
python test_selenium_player.py
```

如果成功，应该看到Chrome浏览器自动打开。

## 使用本地ChromeDriver

如果ChromeDriver在项目目录，修改 `src/core/selenium_player_auto.py`：

```python
# 在文件开头添加
import os

# 在 start() 方法中，替换driver创建部分：
# 检查本地是否有chromedriver
local_driver = os.path.join(os.path.dirname(__file__), '..', '..', 'chromedriver.exe')
if os.path.exists(local_driver):
    self.logger.info(f"使用本地ChromeDriver: {local_driver}")
    from selenium.webdriver.chrome.service import Service
    service = Service(local_driver)
    self.driver = webdriver.Chrome(service=service, options=chrome_options)
else:
    # 使用系统ChromeDriver
    self.driver = webdriver.Chrome(options=chrome_options)
```

## 常见问题

### Q1: ChromeDriver版本不匹配
**错误**: "This version of ChromeDriver only supports Chrome version XX"

**解决**: 下载与Chrome版本匹配的ChromeDriver

### Q2: 找不到chromedriver
**错误**: "chromedriver.exe not found"

**解决**: 
1. 确认已添加到PATH
2. 重启命令提示符
3. 或使用绝对路径

### Q3: 权限被拒绝
**错误**: "Permission denied"

**解决**: 
1. 以管理员身份运行
2. 检查文件权限
3. 关闭防病毒软件

### Q4: 仍然无法连接
**错误**: "Could not reach host"

**解决**: 
1. 确认已手动安装ChromeDriver
2. 使用标准selenium_player.py（不使用webdriver-manager）
3. 修改player.py使用标准版本

## 切换到标准Selenium播放器

如果webdriver-manager一直有问题，使用标准版本：

### 修改 src/core/player.py

找到这一行：
```python
from src.core.selenium_player_auto import SeleniumPlayerAuto
```

改为：
```python
from src.core.selenium_player import SeleniumPlayer as SeleniumPlayerAuto
```

这样就会使用标准版本，不依赖webdriver-manager。

## 验证步骤

### 1. 检查Chrome版本
```bash
# 在Chrome地址栏输入
chrome://version/
```

### 2. 检查ChromeDriver版本
```bash
chromedriver --version
```

### 3. 测试Selenium
```bash
python test_selenium_player.py
```

### 4. 启动系统
```bash
start_selenium.bat
```

## 推荐配置

### 最稳定的方案

1. **手动下载ChromeDriver**
   - 下载与Chrome版本匹配的ChromeDriver
   - 添加到系统PATH

2. **使用标准Selenium播放器**
   - 不依赖webdriver-manager
   - 直接使用系统ChromeDriver

3. **配置文件**
   ```python
   # src/core/player.py
   from src.core.selenium_player import SeleniumPlayer
   ```

## 快速修复脚本

创建 `fix_chromedriver.bat`:

```batch
@echo off
echo 检查ChromeDriver...
chromedriver --version
if errorlevel 1 (
    echo.
    echo ChromeDriver未安装或不在PATH中
    echo.
    echo 请按照以下步骤操作:
    echo 1. 检查Chrome版本
    echo 2. 下载对应版本的ChromeDriver
    echo 3. 添加到系统PATH
    echo.
    echo 详细说明请查看: 手动安装ChromeDriver.md
    pause
) else (
    echo.
    echo ChromeDriver已正确安装
    echo.
    echo 测试Selenium播放器...
    python test_selenium_player.py
)
```

## 总结

如果webdriver-manager无法下载：
1. ✅ 手动下载ChromeDriver
2. ✅ 添加到系统PATH
3. ✅ 使用标准Selenium播放器
4. ✅ 测试验证

这样就不依赖网络下载，更加稳定可靠。

---

更新时间: 2026-03-07
