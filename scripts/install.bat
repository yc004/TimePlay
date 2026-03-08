@echo off
chcp 65001
echo ====================================
echo 校园闭路电视自动播放系统 - 安装程序
echo ====================================
echo.

echo 正在检查Python环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

echo.
echo 正在安装依赖包...
pip install -r requirements.txt

echo.
echo 正在下载VLC播放器...
echo 请手动下载并安装VLC播放器: https://www.videolan.org/vlc/
echo.

echo 创建必要的目录...
if not exist "videos" mkdir videos
if not exist "logs" mkdir logs

echo.
echo ====================================
echo 安装完成！
echo ====================================
echo.
echo 使用说明:
echo 1. 编辑 schedule.json 配置播放时间表
echo 2. 将视频文件放入 videos 目录
echo 3. 运行 start.bat 启动系统
echo.
pause
