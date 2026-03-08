@echo off
chcp 65001
cd /d "%~dp0.."
echo ====================================
echo 显示配置测试
echo ====================================
echo.

python tests/test_display.py

if errorlevel 1 (
    echo.
    echo 测试失败
    pause
)
