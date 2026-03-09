# 更新日志

## [最新] 2026-03-09

### 新增功能

#### ChromeDriver 手动配置功能 ✅

添加了手动配置 ChromeDriver 文件位置的功能，方便用户管理不同版本的 ChromeDriver。

**主要特性**：
- 图形化配置界面
- Chrome 浏览器版本检测
- ChromeDriver 版本检测
- 连接测试功能
- 自动检测回退机制
- 支持绝对路径和相对路径

**使用方法**：
```bash
# 方法1：通过启动器
运行启动器 → 点击 "ChromeDriver 配置"

# 方法2：直接运行
scripts\chromedriver_config.bat

# 方法3：Python命令
python src/ui/chromedriver_config.py
```

**配置说明**：
```python
# config/config.py
CHROMEDRIVER_CONFIG = {
    'custom_path': '',  # ChromeDriver 路径（留空使用系统 PATH）
    'auto_detect': True  # 启用自动检测（推荐）
}
```

**新增文件**：
- `src/ui/chromedriver_config.py` - 配置界面
- `scripts/chromedriver_config.bat` - 快速启动脚本
- `docs/ChromeDriver配置指南.md` - 详细配置指南
- `docs/ChromeDriver快速配置.md` - 快速配置说明

**修改文件**：
- `config/config.py` - 添加 CHROMEDRIVER_CONFIG
- `src/core/selenium_player.py` - 支持自定义路径
- `src/core/selenium_player_auto.py` - 支持自定义路径
- `src/ui/launcher.py` - 添加配置入口
- `docs/快速参考.md` - 更新文档
- `docs/系统运行说明.md` - 更新文档

**使用场景**：
1. ChromeDriver 不在系统 PATH 中
2. 需要使用特定版本的 ChromeDriver
3. 多个 ChromeDriver 版本共存
4. 便携式部署（ChromeDriver 在项目目录）

---

## [之前] 2026-03-08

### 修复和优化

#### 1. 控制台窗口隐藏 ✅

**问题**：点击"启动播放系统"后会弹出命令行窗口。

**解决方案**：
- 使用 `pythonw.exe` 启动（无控制台窗口）
- 使用 `STARTUPINFO` 和 `CREATE_NO_WINDOW` 标志
- 系统在后台运行

**修改文件**：
- `src/ui/launcher.py`

#### 2. 看门狗功能完善 ✅

**问题**：播放窗口被关闭后，看门狗没有自动恢复。

**解决方案**：
- 改进播放状态检查逻辑
- 检查多种播放器类型（VLC、Selenium）
- 根据当前任务自动恢复播放

**修改文件**：
- `src/core/watchdog.py`
- `src/core/scheduler.py`

#### 3. 系统启动卡死修复 ✅

**问题**：启动播放系统后程序未响应。

**解决方案**：
- 使用 Qt 信号-槽机制
- 所有 GUI 操作在主线程执行
- 看门狗继承 QObject

**修改文件**：
- `src/core/watchdog.py`

#### 4. 浏览器关闭优化 ✅

**问题**：停止播放时浏览器无法关闭。

**解决方案**：
- 三层关闭机制
- 使用 psutil 强制终止进程

**修改文件**：
- `src/core/selenium_player.py`
- `src/core/selenium_player_auto.py`

#### 5. 网页直播启动优化 ✅

**问题**：播放网页直播需要等待10-30秒。

**解决方案**：
- 移除 webdriver-manager 检测
- 直接使用系统 ChromeDriver
- 启动速度降至1-2秒

**修改文件**：
- `src/core/selenium_player_auto.py`

#### 6. 任务重叠检查 ✅

**问题**：可以创建时间重叠的播放任务。

**解决方案**：
- 保存前检查时间段重叠
- 检查星期交集
- 显示详细冲突信息

**修改文件**：
- `src/ui/gui_manager.py`

#### 7. 课程表视图优化 ✅

**问题**：任务时间不在整点时显示不准确。

**解决方案**：
- 动态生成时间段
- 按时间段长度调整行高
- 时间指示线精确显示

**修改文件**：
- `src/ui/schedule_calendar_view.py`

#### 8. 空时间表闪退修复 ✅

**问题**：没有播放任务时打开课程表视图会闪退。

**解决方案**：
- 改进错误处理
- 添加空检查

**修改文件**：
- `src/ui/schedule_calendar_view.py`

---

## 系统特性

### 核心功能

- ✅ 多媒体播放（视频、图片、网页直播）
- ✅ 定时播放任务
- ✅ 播放列表和轮播
- ✅ 多显示器支持
- ✅ 全屏和窗口模式
- ✅ 空闲窗口（黑屏+时钟）

### 安全保障

- ✅ 看门狗自动恢复
- ✅ 心跳检测
- ✅ 播放异常恢复
- ✅ 进程管理

### 配置管理

- ✅ 图形化配置界面
- ✅ 显示器配置
- ✅ 播放时间表管理
- ✅ ChromeDriver 配置
- ✅ 开机自启动

### 用户界面

- ✅ 启动器（集成所有功能）
- ✅ 时间表管理器
- ✅ 课程表视图
- ✅ 播放列表编辑器
- ✅ 配置工具

---

## 技术栈

- Python 3.7+
- PyQt5（GUI）
- VLC（视频播放）
- Selenium + ChromeDriver（网页直播）
- Chrome 浏览器

---

## 文档

### 用户文档

- `docs/快速入门.md` - 快速开始指南
- `docs/使用手册.md` - 详细使用说明
- `docs/快速参考.md` - 快速参考手册
- `docs/系统运行说明.md` - 运行和维护指南
- `docs/配置说明.md` - 配置文件说明
- `docs/故障排除.md` - 常见问题解决

### ChromeDriver 文档

- `docs/ChromeDriver配置指南.md` - 详细配置指南
- `docs/ChromeDriver快速配置.md` - 快速配置说明

### 技术文档

- `docs/项目结构说明.md` - 项目结构
- `docs/项目说明.md` - 项目概述

---

## 已知问题

目前没有已知的严重问题。

---

## 计划功能

### 短期计划

- [ ] 系统托盘图标
- [ ] 远程控制 Web 界面
- [ ] 更多播放模式（画中画、分屏）

### 长期计划

- [ ] 外部监控程序（独立进程）
- [ ] Windows 服务模式
- [ ] 移动端控制
- [ ] 云端配置同步

---

## 贡献

欢迎提交问题和建议！

---

## 许可证

请查看 LICENSE 文件。
