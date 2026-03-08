@echo off
chcp 65001 >nul
cd /d "%~dp0.."

echo ====================================
echo 校园闭路电视播放系统
echo ====================================
echo.
echo 系统启动中...
echo.

python run.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo 系统运行出错！
    echo ========================================
    echo.
    echo 请查看 logs 目录下的日志文件
    echo 或运行 scripts\install.bat 安装依赖
    echo.
)

echo.
pause
