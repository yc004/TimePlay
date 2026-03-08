@echo off
chcp 65001 >nul
cls
echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║          ChromeDriver 检查和修复工具                       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo 步骤1: 检查Chrome浏览器...
echo.

reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version 2>nul
if errorlevel 1 (
    reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Google\Chrome\BLBeacon" /v version 2>nul
    if errorlevel 1 (
        echo ✗ 未检测到Chrome浏览器
        echo.
        echo 请先安装Chrome浏览器:
        echo https://www.google.com/chrome/
        echo.
        pause
        exit /b 1
    )
)

echo ✓ Chrome浏览器已安装
echo.

echo 步骤2: 检查ChromeDriver...
echo.

chromedriver --version 2>nul
if errorlevel 1 (
    echo ✗ ChromeDriver未安装或不在PATH中
    echo.
    echo ════════════════════════════════════════════════════════════
    echo 解决方案
    echo ════════════════════════════════════════════════════════════
    echo.
    echo 方法1: 手动下载安装 (推荐)
    echo   1. 查看详细指南: 手动安装ChromeDriver.md
    echo   2. 下载ChromeDriver
    echo   3. 添加到系统PATH
    echo.
    echo 方法2: 使用标准Selenium播放器
    echo   不依赖webdriver-manager，直接使用系统ChromeDriver
    echo.
    echo 方法3: 将chromedriver.exe放在项目根目录
    echo   下载后直接放在这个文件夹
    echo.
    pause
    exit /b 1
) else (
    echo ✓ ChromeDriver已安装
    echo.
)

echo 步骤3: 检查版本匹配...
echo.

REM 获取Chrome版本
for /f "tokens=3" %%i in ('reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version 2^>nul ^| find "version"') do set CHROME_VERSION=%%i
if not defined CHROME_VERSION (
    for /f "tokens=3" %%i in ('reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Google\Chrome\BLBeacon" /v version 2^>nul ^| find "version"') do set CHROME_VERSION=%%i
)

REM 获取ChromeDriver版本
for /f "tokens=2" %%i in ('chromedriver --version 2^>nul') do set DRIVER_VERSION=%%i

echo Chrome版本: %CHROME_VERSION%
echo ChromeDriver版本: %DRIVER_VERSION%
echo.

REM 提取主版本号
for /f "tokens=1 delims=." %%i in ("%CHROME_VERSION%") do set CHROME_MAJOR=%%i
for /f "tokens=1 delims=." %%i in ("%DRIVER_VERSION%") do set DRIVER_MAJOR=%%i

if "%CHROME_MAJOR%"=="%DRIVER_MAJOR%" (
    echo ✓ 版本匹配
) else (
    echo ⚠ 版本不匹配
    echo.
    echo Chrome主版本: %CHROME_MAJOR%
    echo ChromeDriver主版本: %DRIVER_MAJOR%
    echo.
    echo 建议下载匹配版本的ChromeDriver
    echo 查看: 手动安装ChromeDriver.md
    echo.
)

echo.
echo 步骤4: 测试Selenium播放器...
echo.
pause

python test_selenium_player.py

echo.
echo ════════════════════════════════════════════════════════════
echo 测试完成
echo ════════════════════════════════════════════════════════════
echo.
echo 如果测试成功，可以使用:
echo   start_selenium.bat
echo.
echo 如果仍有问题，请查看:
echo   手动安装ChromeDriver.md
echo.
pause
