"""设置Python路径 - 在所有模块开始时导入"""
import sys
import os

# 获取项目根目录
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# 添加到Python路径
if project_root not in sys.path:
    sys.path.insert(0, project_root)
