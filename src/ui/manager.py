"""启动管理界面"""
import sys
from PyQt5.QtWidgets import QApplication
from gui_manager import ScheduleManager

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ScheduleManager()
    window.show()
    sys.exit(app.exec_())
