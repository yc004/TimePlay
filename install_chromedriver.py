"""检查和安装ChromeDriver"""
import os
import sys
import subprocess
import re
import urllib.request
import zipfile
import shutil
from pathlib import Path

def get_chrome_version():
    """获取Chrome版本"""
    try:
        # Windows
        if sys.platform == 'win32':
            import winreg
            key_paths = [
                r"SOFTWARE\Google\Chrome\BLBeacon",
                r"SOFTWARE\Wow6432Node\Google\Chrome\BLBeacon"
            ]
            
            for key_path in key_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                    version, _ = winreg.QueryValueEx(key, "version")
                    winreg.CloseKey(key)
                    return version
                except:
                    continue
            
            # 尝试从命令行获取
            try:
                result = subprocess.run(
                    ['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v', 'version'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    match = re.search(r'version\s+REG_SZ\s+(\S+)', result.stdout)
                    if match:
                        return match.group(1)
            except:
                pass
        
        return None
    except Exception as e:
        print(f"获取Chrome版本失败: {e}")
        return None

def check_chromedriver():
    """检查ChromeDriver是否已安装"""
    try:
        result = subprocess.run(
            ['chromedriver', '--version'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            version_match = re.search(r'ChromeDriver (\S+)', result.stdout)
            if version_match:
                return version_match.group(1)
        return None
    except:
        return None

def install_selenium():
    """安装Selenium"""
    print("检查Selenium...")
    try:
        import selenium
        print(f"✓ Selenium已安装 (版本: {selenium.__version__})")
        return True
    except ImportError:
        print("✗ Selenium未安装")
        print("正在安装Selenium...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'selenium'], check=True)
            print("✓ Selenium安装成功")
            return True
        except Exception as e:
            print(f"✗ Selenium安装失败: {e}")
            return False

def install_webdriver_manager():
    """安装webdriver-manager (自动管理ChromeDriver)"""
    print("\n推荐安装webdriver-manager (自动管理ChromeDriver)...")
    try:
        import webdriver_manager
        print(f"✓ webdriver-manager已安装")
        return True
    except ImportError:
        print("正在安装webdriver-manager...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'webdriver-manager'], check=True)
            print("✓ webdriver-manager安装成功")
            return True
        except Exception as e:
            print(f"✗ webdriver-manager安装失败: {e}")
            return False

def main():
    """主函数"""
    print("=" * 60)
    print("ChromeDriver 检查和安装工具")
    print("=" * 60)
    print()
    
    # 检查Chrome
    print("1. 检查Chrome浏览器...")
    chrome_version = get_chrome_version()
    if chrome_version:
        print(f"✓ Chrome已安装 (版本: {chrome_version})")
        major_version = chrome_version.split('.')[0]
        print(f"  主版本号: {major_version}")
    else:
        print("✗ 未检测到Chrome浏览器")
        print("  请先安装Chrome浏览器: https://www.google.com/chrome/")
        return
    
    print()
    
    # 检查ChromeDriver
    print("2. 检查ChromeDriver...")
    driver_version = check_chromedriver()
    if driver_version:
        print(f"✓ ChromeDriver已安装 (版本: {driver_version})")
        driver_major = driver_version.split('.')[0]
        if driver_major == major_version:
            print("✓ ChromeDriver版本与Chrome匹配")
        else:
            print(f"⚠ 版本不匹配 (Chrome: {major_version}, ChromeDriver: {driver_major})")
            print("  建议重新安装ChromeDriver")
    else:
        print("✗ ChromeDriver未安装或不在PATH中")
    
    print()
    
    # 安装Selenium
    print("3. 检查Selenium...")
    if not install_selenium():
        return
    
    print()
    
    # 安装webdriver-manager
    print("4. 检查webdriver-manager...")
    install_webdriver_manager()
    
    print()
    print("=" * 60)
    print("安装建议")
    print("=" * 60)
    print()
    
    if driver_version and driver_version.split('.')[0] == major_version:
        print("✓ 所有组件已就绪，可以使用Selenium播放器")
    else:
        print("推荐使用webdriver-manager自动管理ChromeDriver:")
        print()
        print("方法1: 使用webdriver-manager (推荐)")
        print("  已安装webdriver-manager，修改代码使用自动管理")
        print()
        print("方法2: 手动下载ChromeDriver")
        print(f"  1. 访问: https://chromedriver.chromium.org/downloads")
        print(f"  2. 下载与Chrome {major_version}匹配的版本")
        print(f"  3. 解压到系统PATH目录")
        print()
    
    print("=" * 60)
    print("下一步")
    print("=" * 60)
    print()
    print("运行测试:")
    print("  python test_selenium_player.py")
    print()

if __name__ == '__main__':
    main()
