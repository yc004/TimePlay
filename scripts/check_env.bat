@echo off
chcp 65001 >nul
cd /d "%~dp0.."

echo ====================================
echo 环境检查工具
echo ====================================
echo.

echo 1. 检查Python...
python --version
if errorlevel 1 (
    echo [错误] Python未安装或未添加到PATH
    goto :end
) else (
    echo [成功] Python已安装
)
echo.

echo 2. 检查依赖包...
echo.

echo 检查 PyQt5...
python -c "import PyQt5; print('[成功] PyQt5 已安装')" 2>nul || echo [错误] PyQt5 未安装

echo 检查 PyQtWebEngine...
python -c "import PyQt5.QtWebEngineWidgets; print('[成功] PyQtWebEngine 已安装')" 2>nul || echo [错误] PyQtWebEngine 未安装

echo 检查 python-vlc...
python -c "import vlc; print('[成功] python-vlc 已安装')" 2>nul || echo [错误] python-vlc 未安装

echo 检查 schedule...
python -c "import schedule; print('[成功] schedule 已安装')" 2>nul || echo [错误] schedule 未安装

echo 检查 requests...
python -c "import requests; print('[成功] requests 已安装')" 2>nul || echo [错误] requests 未安装

echo 检查 flask...
python -c "import flask; print('[成功] flask 已安装')" 2>nul || echo [错误] flask 未安装

echo.
echo 3. 检查VLC播放器...
if exist "C:\Program Files\VideoLAN\VLC\vlc.exe" (
    echo [成功] VLC播放器已安装
) else if exist "C:\Program Files (x86)\VideoLAN\VLC\vlc.exe" (
    echo [成功] VLC播放器已安装
) else (
    echo [警告] 未找到VLC播放器，请从 https://www.videolan.org/vlc/ 下载安装
)

echo.
echo 4. 检查项目结构...
if exist "src\core\player.py" (
    echo [成功] 项目结构正确
) else (
    echo [错误] 项目结构不正确，请确认在项目根目录运行
)

echo.
echo ====================================
echo 检查完成
echo ====================================
echo.
echo 如果有错误，请运行 scripts\install.bat 安装依赖
echo.

:end
pause
