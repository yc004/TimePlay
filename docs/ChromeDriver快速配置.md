# ChromeDriver 快速配置

## 一分钟配置

### 步骤1：打开配置界面

```bash
scripts\chromedriver_config.bat
```

或在启动器中点击"ChromeDriver 配置"

### 步骤2：检测版本

1. 点击"检测 Chrome 版本" - 查看浏览器版本
2. 点击"检测 ChromeDriver 版本" - 查看驱动版本

### 步骤3：处理结果

**情况A：版本匹配**
- 两个版本号的主版本（第一个数字）相同
- 点击"测试连接"验证
- 无需配置，直接使用

**情况B：版本不匹配或找不到 ChromeDriver**
- 运行自动安装：
  ```bash
  python install_chromedriver.py
  ```
- 或手动下载并配置路径

### 步骤4：配置路径（可选）

如果 ChromeDriver 不在系统 PATH 中：

1. 点击"浏览..."选择 ChromeDriver 文件
2. 或输入完整路径
3. 勾选"启用自动检测"
4. 点击"保存配置"

### 步骤5：测试

点击"测试连接"，看到"✓ 连接测试成功"即可。

## 常见问题

### Q: 留空还是填路径？

**留空（推荐）**：
- ChromeDriver 已在 PATH 中
- 使用 `install_chromedriver.py` 安装的

**填路径**：
- ChromeDriver 在特定位置
- 需要使用特定版本

### Q: 如何获取 ChromeDriver？

**方法1：自动安装（推荐）**
```bash
python install_chromedriver.py
```

**方法2：手动下载**
1. 访问：https://chromedriver.chromium.org/downloads
2. 下载与 Chrome 版本匹配的版本
3. 解压得到 `chromedriver.exe`
4. 使用配置界面指定路径

### Q: 版本必须完全一致吗？

不需要。主版本号（第一个数字）相同即可。

例如：
- Chrome 120.0.6099.109
- ChromeDriver 120.0.6099.71

这样是可以的。

### Q: 配置后需要重启吗？

是的。保存配置后需要重启播放系统。

## 验证配置

配置完成后，启动播放系统并播放一个网页直播，确认能正常播放。

## 获取帮助

详细文档：`docs/ChromeDriver配置指南.md`
