@echo off
echo ========================================
echo 浏览器播放器测试工具
echo ========================================
echo.

cd /d "%~dp0\.."

echo 正在启动测试工具...
echo.
python tests\test_browser_player.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo 错误: 测试工具启动失败
    echo 错误代码: %ERRORLEVEL%
    echo.
    echo 可能的原因:
    echo 1. Python未安装或未添加到PATH
    echo 2. 缺少依赖包 (PyQt5, PyQtWebEngine)
    echo 3. 项目路径有问题
    echo.
    echo 请运行 scripts\check_env.bat 检查环境
)

echo.
pause
