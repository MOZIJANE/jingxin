# coding: utf-8
# author: ives
# date: 2018-01-11
# desc: 

import sys
import os
import win32gui
import win32api
import win32con
import time
import threading
import uiScanServer
import bottle


import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QStatusBar, QTableWidgetItem, QAbstractItemView)
from PyQt5.QtGui import (QPalette, QColor)
from PyQt5.QtCore import (Qt)


class scanProxy(PyQt5.QtWidgets.QMainWindow, uiScanServer.Ui_MainWindow):
	def __init__(self, parent = None):
		super(scanProxy, self).__init__(parent) 
		self.setupUi(self)


class uiMgr():
	def __init__(self):
		self.__threadRun = True
		self.__threadPtr = threading.Thread(target=self.__threadFunc, args=('uiMainThread',))
		self.__threadPtr.setDaemon(False)
		self.__app = None
		self.__ui = None

	def __del__(self):
		self.stop()

	#启动线程
	def start(self):
		self.__threadRun = True
		if not self.__threadPtr.isAlive():
			self.__threadPtr.start()

	#停止线程
	def stop(self):
		self.__threadRun = False
		if self.__threadPtr.isAlive():
			self.__threadPtr.join()
		
	def __threadFunc(self, args):
		self.__app = PyQt5.QtWidgets.QApplication(sys.argv)
		self.__ui = scanProxy()
		self.__ui.show() 
		sys.exit(self.__app.exec_())


@bottle.route('/assemble1/scan/jig', method='Get')
def urlScanJig():
	jigId = bottle.request.forms.getunicode('id', encoding="utf-8")
	print('+++++++++++ jigId=', jigId)
	return "ok"


#========================================== unit test ==========================================

if __name__ == '__main__':
	#ui = uiMgr()
	#ui.start()
	bottle.run(host='0.0.0.0', port=9012,debug=True,reloader=True)


