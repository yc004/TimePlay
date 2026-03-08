@echo off
chcp 65001 >nul
cd /d "%~dp0.."

echo ====================================
echo 显示器配置工具
echo ====================================
echo.

python src/ui/display_settings_ui.py

if errorlevel 1 (
    echo.
    echo 启动失败，请检查Python环境
    echo.
)

pause
