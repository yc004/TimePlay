@echo off
chcp 65001
cd /d "%~dp0.."
echo ====================================
echo 播放器测试工具
echo ====================================
echo.

python tests/test_player.py

if errorlevel 1 (
    echo.
    echo 测试失败
    pause
)
