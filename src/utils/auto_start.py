"""Windows开机自启动配置"""
import os
import sys
import winreg

def add_to_startup():
    """添加到开机自启动"""
    try:
        # 获取当前脚本路径
        if getattr(sys, 'frozen', False):
            # 如果是打包后的exe
            app_path = sys.executable
        else:
            # 如果是Python脚本
            app_path = os.path.join(os.getcwd(), 'start.bat')
        
        # 注册表路径
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        # 打开注册表
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        
        # 设置值
        winreg.SetValueEx(key, "TVScheduleSystem", 0, winreg.REG_SZ, app_path)
        
        # 关闭注册表
        winreg.CloseKey(key)
        
        print("✓ 已添加到开机自启动")
        return True
        
    except Exception as e:
        print(f"✗ 添加开机自启动失败: {e}")
        return False

def remove_from_startup():
    """从开机自启动移除"""
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        
        try:
            winreg.DeleteValue(key, "TVScheduleSystem")
            print("✓ 已从开机自启动移除")
        except FileNotFoundError:
            print("! 未找到自启动项")
        
        winreg.CloseKey(key)
        return True
        
    except Exception as e:
        print(f"✗ 移除开机自启动失败: {e}")
        return False

def check_startup():
    """检查是否已设置开机自启动"""
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
        
        try:
            value, _ = winreg.QueryValueEx(key, "TVScheduleSystem")
            winreg.CloseKey(key)
            print(f"✓ 已设置开机自启动: {value}")
            return True
        except FileNotFoundError:
            winreg.CloseKey(key)
            print("! 未设置开机自启动")
            return False
            
    except Exception as e:
        print(f"✗ 检查失败: {e}")
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("开机自启动配置工具")
    print("=" * 50)
    print()
    print("1. 添加到开机自启动")
    print("2. 从开机自启动移除")
    print("3. 检查自启动状态")
    print("0. 退出")
    print()
    
    choice = input("请选择操作 (0-3): ")
    
    if choice == '1':
        add_to_startup()
    elif choice == '2':
        remove_from_startup()
    elif choice == '3':
        check_startup()
    elif choice == '0':
        print("退出")
    else:
        print("无效选择")
    
    input("\n按回车键退出...")
