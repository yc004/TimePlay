@echo off
chcp 65001 >nul
cd /d "%~dp0\.."
python src/ui/chromedriver_config.py
pause
