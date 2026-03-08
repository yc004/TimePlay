"""系统启动入口 - 处理导入路径"""
import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 导入并运行主程序
if __name__ == '__main__':
    import main
