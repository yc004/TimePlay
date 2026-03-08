@echo off
chcp 65001 >nul
cd /d "%~dp0.."

echo ====================================
echo 测试模块导入
echo ====================================
echo.

python test_imports.py

echo.
pause
