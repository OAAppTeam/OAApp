# encoding: UTF-8

"""
程序入口，整合上层界面，中层引擎与底层接口
"""

import ctypes
import sys

from windEngine import MainEngine
from demoUi import *

#----------------------------------------------------------------------
def main():
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('vn.py demo')
    
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('vnpy.ico'))
    me = MainEngine()
    mw = MainWindow(me.ee, me)
    mw.showMaximized()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
    
