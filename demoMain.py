# encoding: UTF-8

"""
璇ユ枃浠朵腑鍖呭惈鐨勬槸浜ゆ槗骞冲彴鐨勪富鍑芥暟锛�
灏嗗簳灞傘�佷腑灞傘�佷笂灞傜殑鍔熻兘瀵煎叆锛屽苟杩愯銆�
"""

import ctypes
import sys

from windEngine import MainEngine
from demoUi import *

#----------------------------------------------------------------------
def main():
    """涓荤▼搴忓叆鍙�"""
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('vn.py demo')  # win7浠ヤ笅璇锋敞閲婃帀璇ヨ   
    
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('vnpy.ico'))
    
    me = MainEngine()
    
    mw = MainWindow(me.ee, me)
    mw.showMaximized()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
    
