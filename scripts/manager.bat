@echo off
chcp 65001 >nul
cd /d "%~dp0.."

echo ====================================
echo 播放时间表管理界面
echo ====================================
echo.

python src/ui/gui_manager.py

if errorlevel 1 (
    echo.
    echo 启动失败，请检查Python环境
    echo.
)

pause
