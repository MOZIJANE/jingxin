#coding=utf-8
#lizhenwei			2017-08-28		modify
# 手柄控制
import os,sys
from PyQt5.QtCore import (Qt,QTimer,QThread,QCoreApplication,QObject, pyqtSignal,pyqtSlot)
from PyQt5.QtWidgets import (QApplication,QWidget, QDialog,QPushButton, QLabel,QGridLayout, QHBoxLayout, QVBoxLayout)
import setup 
if __name__ == '__main__':
	setup.setCurPath(__file__)
from driver.handstick import handStickApi
from driver.handstick import command
import utility
import json
from driver.handstick import stickKeyCfg
import time

keepPressKeyList = ["xForward","yForward","zUp","rForward","xBack","yBack","rBack","zDown","tempUp", "tempDown"]
# 与UI相关的按键，涉及到界面响应，通过qt的信号与槽连接
uiKeys = ["test", "stop", "reset","pageUp","itemUp","itemDown","pageDown","locate","stepUp","stepDown","updateCoord"] 

class handStickCtrl(QThread):
	sgClickTest = pyqtSignal()
	sgClickStop = pyqtSignal()
	sgClickReset = pyqtSignal()
	sgClickPageUp = pyqtSignal()
	sgClickPageDown = pyqtSignal()
	sgClickItemUp = pyqtSignal()
	sgClickItemDown = pyqtSignal()
	sgClickLocate = pyqtSignal()
	sgClickStepUp = pyqtSignal()
	sgClickStepDown = pyqtSignal()
	sgClickUpdateCoord = pyqtSignal()
	
	def __init__(self):
		super(handStickCtrl, self).__init__()	
		self.isStop = False		
		self.isOpened = False
		if not utility.is_test():
			self.openStick()
		
	def openStick(self):
		if self.isOpened:
			return
		if not handStickApi.openStick():
			raise Exception("打开手柄失败!")
		self.isOpened = True
		
	def close(self):
		self.disable()
		if not utility.is_test():
			handStickApi.closeStick()
		self.isOpened = False
		
	def enable(self):
		if utility.is_test():
			self.isOpened = True
			return
		if not self.isOpened:
			self.openStick()
		self.isOpened = True
		command.emit("clicked", "speedLow")
		self.onShowMsg("Enable",0)
		self.startThd()
		
	def disable(self):
		'失效但手柄依旧打开的'
		if utility.is_test():
			self.isOpened = False
			return
		self.stopThd()
		if self.isOpened:
			self.onShowMsg("Disable",0)
			self.onClearMsg(1)
					
	def onShowMsg(self, msg, rowId):
		handStickApi.clearMsgRow(rowId)
		handStickApi.showMsgRow(msg, rowId)
		
	def onClearMsg(self, rowId):
		if rowId == -1:
			return handStickApi.clearMsg()
		else:
			return handStickApi.clearMsgRow(rowId)

	def startThd(self):
		'开启线程'
		self.isStop = False
		self.start()
		
	def stopThd(self):
		'停止线程'
		self.isStop = True
		self.wait()
			
	@staticmethod
	def eqaulList(list1,list2):
		if list1 and not list2:
			return False
		if not list1 and list2:
			return False
		if not list1 and not list2:
			return True
		if len(list1) != len(list2):
			return False
		for i1 in list1:
			if i1 not in list2:
				return False
		return True
	
	def _emitUIKeys(self, tkeyName):
		if tkeyName == "test":
			self.sgClickTest.emit()
		elif tkeyName == "stop":
			self.sgClickStop.emit()
		elif tkeyName == "reset":
			self.sgClickReset.emit()
		elif tkeyName == "pageUp":
			self.sgClickPageUp.emit()
		elif tkeyName == "pageDown":
			self.sgClickPageDown.emit()
		elif tkeyName == "itemUp":
			self.sgClickItemUp.emit()
		elif tkeyName == "itemDown":
			self.sgClickItemDown.emit()
		elif tkeyName == "locate":
			self.sgClickLocate.emit()
		elif tkeyName == "stepUp":
			self.sgClickStepUp.emit()
		elif tkeyName == "stepDown":
			self.sgClickStepDown.emit()
		elif tkeyName == "updateCoord":
			self.sgClickUpdateCoord.emit()
	
	def run(self):
		global keepPressKeyList, uiKeys
		curKeyList = []
		preKeyList = []
		keepKeyPresed = {} # tkey:time
		emitpress = False # 只发送一次pressdown
		tdelayms = stickKeyCfg.g_pressDelayMs
		while not self.isStop:
			QThread.msleep(20)
			curKeyList = handStickApi.getInput()
			# 读取失败
			if curKeyList is None:
				continue
			# 只处理单键情况
			if len(curKeyList) > 1:
				continue
			if curKeyList:
				curkeypressed = curKeyList[0]
			else:
				curkeypressed = None
						
			if curkeypressed in keepKeyPresed:
				if time.time()*1000 - keepKeyPresed[curkeypressed]>tdelayms:
					tkeyPos = stickKeyCfg.keyPosMap()[curkeypressed]
					tkeyName = stickKeyCfg.keyNameMap()[tkeyPos]
					if not emitpress:
						command.emit("pressDown", tkeyName)
						emitpress = True
				
			if not handStickCtrl.eqaulList(curKeyList, preKeyList):
				if not preKeyList:
					# 有按键按下
					tkey = curKeyList[0]
					tkeyPos = stickKeyCfg.keyPosMap()[tkey]
					tkeyName = stickKeyCfg.keyNameMap()[tkeyPos]
					if tkeyName:
						if tkeyName in keepPressKeyList:
							if not keepKeyPresed:
								keepKeyPresed[tkey] = time.time()*1000
						elif tkeyName not in uiKeys:
							command.emit("pressDown", tkeyName)
				else:
					# 有按键释放
					tkey = preKeyList[0]
					tkeyPos = stickKeyCfg.keyPosMap()[tkey]
					tkeyName = stickKeyCfg.keyNameMap()[tkeyPos]
					
					if tkey in keepKeyPresed:
						if time.time()*1000 - keepKeyPresed[tkey] < tdelayms:
							command.emit("clicked", tkeyName)
						else:
							command.emit("pressUp", tkeyName)
						keepKeyPresed = {}
						emitpress = False
					elif tkeyName in uiKeys:
						self._emitUIKeys(tkeyName)
					else:
						command.emit("pressUp", tkeyName)
						command.emit("clicked", tkeyName)
					
			preKeyList = curKeyList[:]
		else:
			# 等待下次开始
			self.isStop = False	
		
g_handStickCtrl = None
def ctrl():
	global g_handStickCtrl
	if not g_handStickCtrl:
		g_handStickCtrl = handStickCtrl()
	return g_handStickCtrl
		
def enable():
	ctrl().enable()
	
def disable():
	ctrl().disable()

def close():
	ctrl().close()
	
def showStickMsg(msg, rowId):
	ctrl().onShowMsg(msg, rowId)
	
def clearStickMsg(rowId):
	ctrl().onClearMsg(rowId)
		
def testStickDlg():	
	class StickDlg(QDialog):
		This = None
		def __init__(self):
			super(StickDlg, self).__init__()
			self.label = QLabel()
			self.label.setFixedSize(100,200)
			self.enBtn = QPushButton("手柄使能")
			self.enStick = False
			self.enBtn.setFixedSize(100,200)
			self.enBtn.clicked.connect(self.onEnBtn)
			lay = QVBoxLayout()
			lay.addWidget(self.label)
			lay.addWidget(self.enBtn)
			self.setLayout(lay)
			StickDlg.This = self
			showStickMsg("Disable", 0)
		
		# 频繁切换，showStickMsg 显示有问题	
		def onEnBtn(self):
			if not self.enStick:
				self.enStick = True
				self.enBtn.setText("手柄失效")
				ctrl().enable()
			else:
				self.enStick = False
				self.enBtn.setText("手柄使能")
				ctrl().disable()
		
		def closeEvent(self,event):
			ctrl().close()
			super(StickDlg, self).closeEvent(event)
		# @staticmethod
		# @command.register("clicked","start")
		# def keystart():
			# StickDlg.This.label.setText("clicked start key")
			# showStickMsg("clicked start", 1)
		
		@staticmethod
		@command.register("clicked","stop")
		def keystart():
			StickDlg.This.label.setText("clicked stop key")
			showStickMsg("clicked stop", 1)
			
		@staticmethod
		@command.register("clicked","reset")
		def keystart():
			StickDlg.This.label.setText("clicked reset key")
			showStickMsg("clicked reset", 1)
			
	app = QApplication(sys.argv)
	dlg = StickDlg()	
	dlg.show()
	return app.exec_()
	
if __name__ == "__main__":
	testStickDlg()