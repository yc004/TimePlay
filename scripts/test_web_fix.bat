@echo off
chcp 65001 >nul
echo ========================================
echo 网页直播白屏问题测试工具
echo ========================================
echo.

:menu
echo 请选择测试选项:
echo 1. 对比测试 (原版 vs 改进版)
echo 2. 单独测试改进版
echo 3. 应用修复
echo 4. 查看最新日志
echo 5. 退出
echo.

set /p choice="请输入选项 (1-5): "

if "%choice%"=="1" goto compare
if "%choice%"=="2" goto test_improved
if "%choice%"=="3" goto apply_fix
if "%choice%"=="4" goto view_log
if "%choice%"=="5" goto end

echo 无效的选项，请重试
echo.
goto menu

:compare
echo.
echo 启动对比测试...
echo 这将并排显示原版和改进版播放器
echo.
python test_browser_comparison.py
goto menu

:test_improved
echo.
echo 启动改进版测试...
echo.
python test_web_live.py
goto menu

:apply_fix
echo.
echo 启动修复工具...
echo.
python apply_fix.py
goto menu

:view_log
echo.
echo 查看最新日志...
echo.
for /f "delims=" %%i in ('dir /b /od logs\tv_system_*.log') do set latest=%%i
if defined latest (
    echo 最新日志文件: logs\%latest%
    echo.
    type logs\%latest%
    echo.
) else (
    echo 没有找到日志文件
)
pause
goto menu

:end
echo.
echo 退出
exit /b 0
