# ChromeDriver 配置指南

## 概述

ChromeDriver 是用于控制 Chrome 浏览器的工具，系统使用它来播放网页直播。本指南将帮助您配置 ChromeDriver 路径。

## 为什么需要配置 ChromeDriver？

### 默认行为

系统默认使用系统 PATH 环境变量中的 ChromeDriver。如果：
- ChromeDriver 已添加到 PATH
- ChromeDriver 版本与 Chrome 浏览器匹配

则无需额外配置。

### 需要手动配置的情况

1. **ChromeDriver 不在 PATH 中**
   - 下载了 ChromeDriver 但未添加到 PATH
   - 想使用特定位置的 ChromeDriver

2. **多个 ChromeDriver 版本**
   - 系统中有多个 ChromeDriver
   - 需要指定使用哪一个

3. **便携式部署**
   - 将系统部署到其他电脑
   - ChromeDriver 放在项目目录中

## 配置方法

### 方法1：使用配置界面（推荐）

1. **打开配置界面**
   ```bash
   # 方式1：通过启动器
   运行 scripts\launcher.bat
   点击 "ChromeDriver 配置"
   
   # 方式2：直接运行
   scripts\chromedriver_config.bat
   
   # 方式3：Python命令
   python src/ui/chromedriver_config.py
   ```

2. **配置路径**
   - 点击"浏览..."按钮选择 ChromeDriver 文件
   - 或直接输入完整路径
   - 留空则使用系统 PATH

3. **启用自动检测**
   - 勾选"启用自动检测"（推荐）
   - 如果自定义路径无效，自动使用 PATH

4. **测试配置**
   - 点击"检测 Chrome 版本"查看浏览器版本
   - 点击"检测 ChromeDriver 版本"查看驱动版本
   - 点击"测试连接"验证配置是否正确

5. **保存配置**
   - 点击"保存配置"
   - 重启播放系统后生效

### 方法2：手动编辑配置文件

编辑 `config/config.py`：

```python
# ChromeDriver 配置
CHROMEDRIVER_CONFIG = {
    'custom_path': 'C:/path/to/chromedriver.exe',  # 自定义路径
    'auto_detect': True  # 启用自动检测
}
```

**参数说明**：
- `custom_path`: ChromeDriver 完整路径
  - 留空 `''` 使用系统 PATH
  - 示例：`'C:/tools/chromedriver.exe'`
  - 示例：`'drivers/chromedriver.exe'`（相对路径）

- `auto_detect`: 自动检测
  - `True`: 如果自定义路径无效，使用 PATH（推荐）
  - `False`: 只使用自定义路径

## ChromeDriver 安装

### 自动安装（推荐）

```bash
python install_chromedriver.py
```

此脚本会：
1. 检测 Chrome 浏览器版本
2. 下载匹配的 ChromeDriver
3. 自动配置路径

### 手动安装

1. **检查 Chrome 版本**
   - 打开 Chrome 浏览器
   - 地址栏输入：`chrome://version/`
   - 查看版本号（如：120.0.6099.109）

2. **下载 ChromeDriver**
   - 访问：https://chromedriver.chromium.org/downloads
   - 或：https://googlechromelabs.github.io/chrome-for-testing/
   - 下载与 Chrome 版本匹配的 ChromeDriver

3. **解压文件**
   - 解压下载的 zip 文件
   - 得到 `chromedriver.exe`

4. **配置路径**
   - 方式1：添加到 PATH 环境变量
   - 方式2：使用配置界面指定路径
   - 方式3：放在项目 `drivers/` 目录并配置

## 版本匹配

### 重要提示

ChromeDriver 版本必须与 Chrome 浏览器版本匹配！

### 版本对应关系

| Chrome 版本 | ChromeDriver 版本 |
|------------|------------------|
| 120.x.x.x  | 120.x.x.x        |
| 119.x.x.x  | 119.x.x.x        |
| 118.x.x.x  | 118.x.x.x        |

主版本号（第一个数字）必须相同。

### 检查版本

**Chrome 版本**：
```bash
# 方法1：浏览器
chrome://version/

# 方法2：命令行
"C:\Program Files\Google\Chrome\Application\chrome.exe" --version

# 方法3：配置界面
点击 "检测 Chrome 版本"
```

**ChromeDriver 版本**：
```bash
# 方法1：命令行
chromedriver --version

# 方法2：配置界面
点击 "检测 ChromeDriver 版本"
```

## 配置示例

### 示例1：使用系统 PATH

```python
CHROMEDRIVER_CONFIG = {
    'custom_path': '',  # 留空
    'auto_detect': True
}
```

**适用场景**：
- ChromeDriver 已添加到 PATH
- 标准安装方式

### 示例2：使用绝对路径

```python
CHROMEDRIVER_CONFIG = {
    'custom_path': 'C:/tools/chromedriver.exe',
    'auto_detect': True
}
```

**适用场景**：
- ChromeDriver 在固定位置
- 多个版本需要指定

### 示例3：使用相对路径

```python
CHROMEDRIVER_CONFIG = {
    'custom_path': 'drivers/chromedriver.exe',
    'auto_detect': True
}
```

**适用场景**：
- 便携式部署
- ChromeDriver 在项目目录中

### 示例4：禁用自动检测

```python
CHROMEDRIVER_CONFIG = {
    'custom_path': 'C:/tools/chromedriver.exe',
    'auto_detect': False
}
```

**适用场景**：
- 严格控制使用的版本
- 避免使用 PATH 中的旧版本

## 故障排除

### 问题1：找不到 ChromeDriver

**错误信息**：
```
ChromeDriver错误: 'chromedriver' executable needs to be in PATH
```

**解决方法**：
1. 使用配置界面指定 ChromeDriver 路径
2. 或将 ChromeDriver 添加到 PATH
3. 或运行 `python install_chromedriver.py`

### 问题2：版本不匹配

**错误信息**：
```
session not created: This version of ChromeDriver only supports Chrome version XX
```

**解决方法**：
1. 检查 Chrome 版本：配置界面 → "检测 Chrome 版本"
2. 下载匹配的 ChromeDriver
3. 更新配置路径

### 问题3：配置不生效

**可能原因**：
- 配置文件未保存
- 播放系统未重启

**解决方法**：
1. 确认配置已保存
2. 停止播放系统
3. 重新启动播放系统

### 问题4：测试连接失败

**检查步骤**：
1. 确认 Chrome 浏览器已安装
2. 确认 ChromeDriver 文件存在
3. 确认版本匹配
4. 查看详细错误信息

**常见错误**：
- 文件不存在：检查路径是否正确
- 权限不足：以管理员身份运行
- 端口占用：关闭其他 Chrome 实例

## 高级配置

### 多显示器配置

如果使用多个显示器播放不同内容，可以为每个显示器配置不同的 ChromeDriver：

```python
# 这需要修改代码，暂不支持
# 未来版本可能添加此功能
```

### 便携式部署

将 ChromeDriver 放在项目目录中：

```
project/
  ├── drivers/
  │   └── chromedriver.exe
  ├── config/
  │   └── config.py
  └── ...
```

配置：
```python
CHROMEDRIVER_CONFIG = {
    'custom_path': 'drivers/chromedriver.exe',
    'auto_detect': True
}
```

### 自动更新

创建更新脚本 `update_chromedriver.bat`：

```batch
@echo off
echo 更新 ChromeDriver...
python install_chromedriver.py
echo 完成！
pause
```

定期运行此脚本保持 ChromeDriver 最新。

## 最佳实践

### 推荐配置

```python
CHROMEDRIVER_CONFIG = {
    'custom_path': '',  # 使用 PATH
    'auto_detect': True  # 启用自动检测
}
```

**优点**：
- 简单易用
- 自动适应系统环境
- 便于维护

### 定期检查

1. **每月检查一次**
   - Chrome 浏览器版本
   - ChromeDriver 版本
   - 是否需要更新

2. **更新后测试**
   - 使用配置界面测试连接
   - 播放一个测试直播
   - 确认功能正常

### 备份配置

```bash
# 备份配置文件
copy config\config.py config\config.py.backup
```

## 相关文件

- `config/config.py` - 配置文件
- `src/ui/chromedriver_config.py` - 配置界面
- `src/core/selenium_player.py` - Selenium 播放器
- `src/core/selenium_player_auto.py` - 自动播放器
- `install_chromedriver.py` - 自动安装脚本
- `scripts/chromedriver_config.bat` - 快速启动脚本

## 技术支持

### 获取帮助

1. 查看日志：`logs/tv_system_*.log`
2. 使用配置界面的检测工具
3. 运行测试连接

### 常用命令

```bash
# 检查 Chrome 版本
"C:\Program Files\Google\Chrome\Application\chrome.exe" --version

# 检查 ChromeDriver 版本
chromedriver --version

# 测试 ChromeDriver
chromedriver --help

# 打开配置界面
python src/ui/chromedriver_config.py

# 自动安装
python install_chromedriver.py
```

## 总结

1. **默认配置**：留空使用 PATH（最简单）
2. **自定义路径**：指定 ChromeDriver 位置（更灵活）
3. **版本匹配**：确保版本一致（最重要）
4. **定期更新**：保持最新版本（推荐）
5. **测试验证**：使用配置界面测试（确保正常）

配置完成后，系统将使用指定的 ChromeDriver 播放网页直播。
