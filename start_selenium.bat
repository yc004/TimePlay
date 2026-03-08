@echo off
chcp 65001 >nul
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║          电视播放系统 - Selenium版                         ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 特性:
echo   ✓ 使用Selenium + ChromeDriver
echo   ✓ 绕过反爬虫检测
echo   ✓ 模拟真实浏览器
echo   ✓ 支持所有网页直播
echo.
echo 要求:
echo   • Chrome浏览器
echo   • ChromeDriver (自动管理)
echo   • Selenium
echo   • webdriver-manager
echo.
echo 正在检查依赖...
echo.

REM 检查Selenium
python -c "import selenium" 2>nul
if errorlevel 1 (
    echo ✗ Selenium未安装
    echo.
    echo 正在安装Selenium...
    pip install selenium
    if errorlevel 1 (
        echo.
        echo ✗ 安装失败
        pause
        exit /b 1
    )
    echo ✓ Selenium安装成功
) else (
    echo ✓ Selenium已安装
)

REM 检查webdriver-manager
python -c "import webdriver_manager" 2>nul
if errorlevel 1 (
    echo ✗ webdriver-manager未安装
    echo.
    echo 正在安装webdriver-manager...
    pip install webdriver-manager
    if errorlevel 1 (
        echo.
        echo ✗ 安装失败
        pause
        exit /b 1
    )
    echo ✓ webdriver-manager安装成功
) else (
    echo ✓ webdriver-manager已安装
)

echo.
echo ════════════════════════════════════════════════════════════
echo 依赖检查完成，正在启动系统...
echo ════════════════════════════════════════════════════════════
echo.

python start_with_selenium.py

if errorlevel 1 (
    echo.
    echo ════════════════════════════════════════════════════════════
    echo 启动失败
    echo ════════════════════════════════════════════════════════════
    echo.
    echo 请运行诊断工具:
    echo   python install_chromedriver.py
    echo.
    pause
)
