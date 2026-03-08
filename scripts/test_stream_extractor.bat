@echo off
chcp 65001
cd /d "%~dp0.."
echo ====================================
echo 视频流提取测试工具
echo ====================================
echo.

python tests/test_stream_extractor.py

if errorlevel 1 (
    echo.
    echo 启动失败
    pause
)
