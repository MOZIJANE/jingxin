#coding = utf-8
#lizhenwei 		2017-08-29		create
# 手柄扫描线程
import os,sys
from PyQt5.QtCore import(QThread,QTimer,pyqtSignal,pyqtSlot)
from PyQt5.QtWidgets import (QApplication)

import setup 
if __name__ == '__main__':
	setup.setCurPath(__file__)
import utility
from driver.handstick  import handStickApi
	
class handStickThd(QThread):
	sgKeyPressed = pyqtSignal(int)
	sgKeyReleased = pyqtSignal(int)
	sgKeyClicked = pyqtSignal(int)
	
	def __init__(self):
		super(handStickThd, self).__init__()
		handStickApi.openStick()
		self.isStop = False
		
	def close(self):
		self.stop()
		self.quit()
		if not utility.is_test():
			handStickApi.closeStick()
	
	def startThd(self):
		self.isStop = False
		self.start()
		
	def stopThd(self):
		self.isStop = True
		self.wait()
	
	@staticmethod
	def eqaulList(list1,list2):
		if len(list1) != len(list2):
			return False
		for i1 in list1:
			if i1 not in list2:
				return False
		return True
			
	def run(self):
		curKeyList = []
		preKeyList = handStickApi.getInput()
		while not self.isStop:
			QThread.msleep(5)
			s = utility.ticks()
			curKeyList = handStickApi.getInput()
			if curKeyList is None:
				return
			# 只处理单键情况
			if len(curKeyList) > 1:
				continue
			if not handStickThd.eqaulList(curKeyList, preKeyList):
				if not preKeyList:
					print("handStickApi perss delay: ",utility.ticks() - s)
					# 有按键按下
					self.sgKeyPressed.emit(curKeyList[0])
				else:
					print("handStickApi release delay: ",utility.ticks() - s)
					import threading
					print("thd emit id: ",threading.currentThread().ident)
					# 有按键释放
					self.sgKeyReleased.emit(preKeyList[0])
					self.sgKeyClicked.emit(preKeyList[0])
					
			preKeyList = curKeyList[:]
		else:
			# 等待下次开始
			self.isStop = False
		
def test():
	app = QApplication(sys.argv)
	a = handStickThd()
	a.start()
	return app.exec_()
	
if __name__ == '__main__':
	test()