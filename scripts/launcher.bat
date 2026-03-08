@echo off
chcp 65001 >nul
cd /d "%~dp0.."

echo ====================================
echo 校园闭路电视播放系统 - 启动器
echo ====================================
echo.
echo 当前目录: %CD%
echo 正在启动...
echo.

python src/ui/launcher.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo 启动失败！
    echo ========================================
    echo.
    echo 可能的原因:
    echo 1. Python未安装或未添加到PATH
    echo 2. 缺少依赖包 - 请运行 scripts\install.bat
    echo 3. 代码有错误 - 查看上面的错误信息
    echo.
)

echo.
pause
