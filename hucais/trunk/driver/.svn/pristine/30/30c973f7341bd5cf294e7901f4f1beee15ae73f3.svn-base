# coding: utf-8
# author: ives
# date: 2017-11-15
# desc: 

import sys
import os
import win32gui
import win32api
import win32con
import time
import datetime
import json
import threading
import uiMesAssemble
import mqtt
import configparser

import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QStatusBar, QTableWidgetItem, QAbstractItemView, QMessageBox)
from PyQt5.QtGui import (QPalette, QColor)
from PyQt5.QtCore import (Qt, QCoreApplication)


def find_subHandle(pHandle, index=0):  
	handle = win32gui.FindWindowEx(pHandle, 0, None, None)  
	while index > 0:  
		handle = win32gui.FindWindowEx(pHandle, handle, None, None)  
		index -= 1  
	return handle  


def getToolStripContainer1Handle(mainHandle):
	handle = find_subHandle(mainHandle, 0)
	if handle > 0:
		title = str(win32gui.GetWindowText(handle))
		if title == "toolStripContainer1" :
			return handle
	return 0


def getProduceClientHandle(toolStripHandle):
	orderList = [0,0,1,0,1,0,0,0]
	handle = toolStripHandle
	for order in orderList:
		if handle < 1:
			return 0
		handle = find_subHandle(handle, order)
	if handle > 0:
		title = str(win32gui.GetWindowText(handle))
		if title == "生产客户端" :
			return handle
	return 0


def getTargetHandle(produceHandle, orderList):
	handle = produceHandle
	for order in orderList:
		if handle < 1:
			return 0
		handle = find_subHandle(handle, order)
	return handle

	
_exited = False

def resumeSleep():
	global _exited
	_exited = False
	
def stopSleep():
	global _exited
	_exited = True
	
def mysleep(s):
	global _exited 
	ms = s*1000
	start = time.time()*1000
	while not _exited:
		if time.time()*1000 - start < ms: 
			QCoreApplication.processEvents()
		else:
			return True
	else:
		#log.warning("延时调用退出_exited= %d"%_exited)
		return False
	return True

class assembleProxy(PyQt5.QtWidgets.QMainWindow, uiMesAssemble.Ui_MainWindow):
	def __init__(self, parent = None):
		super(assembleProxy, self).__init__(parent) 
		self.setupUi(self)
		self.__mainHandle = 0
		self.__snHandle = 0
		self.__craftworkHandle = 0
		self.__jobNumHandle = 0
		self.__locNumHandle = 0
		self.__scanHandle = 0
		self.__initHandleFailed = False
		self.__threadRun = True
		self.__threadCmd = threading.Thread(target=self.__threadCmdFunc, args=('assembleProduct',))
		self.__threadCmd.setDaemon(False)
		self.__condCmd = threading.Condition()
		self.__flag = 0
		self.__lineTopic = ""
		self.__seatId = ""
		self.__filePath = ""
		self.__productHistory = []

	def __del__(self):
		self.stop()
		
	def __loadCfg(self):
		fileName = './default.ini'
		if not os.path.exists(fileName):
			fileName = os.path.dirname(__file__) + '/default.ini'
			if not os.path.exists(fileName):
				print('can not find default.ini file!')
				exit(1)
		try:
			config = configparser.ConfigParser()
			config.read(fileName)
			svrIp = str(config.get("mqtt", "ip"))
			port = int(config.get("mqtt", "port"))
			user = str(config.get("mqtt", "user"))
			pwd = str(config.get("mqtt", "password"))
			self.__lineTopic = ("scada/%s/product" %(str(config.get("line", "name"))))
			mqtt.initMqttObj(svrIp, user, pwd, port)
			self.__seatId = str(config.get("device", "seatId"))
			self.__filePath = str(config.get("other", "packFilePath"))
			if len(self.__filePath) > 0 and (self.__filePath[-1] != "/" and self.__filePath[-1] != "\\"):
				self.__filePath += "\\"
		except:
			print('read default.ini failed!')
			exit(2)

	def __initCraftwork(self):
		import struct
		if self.__craftworkHandle < 1:
			return
		handle = self.__craftworkHandle
		bufLen = struct.pack('i', 255)
		linetext = bytearray()
		for b in bufLen:
			linetext.append(b)
		for b in bytearray(253):
			linetext.append(b)
			
		cnt = win32gui.SendMessage(handle, win32con.CB_GETCOUNT, 0, 0)
		for idx in range(cnt):
			linelength = win32gui.SendMessage(handle, win32con.CB_GETLBTEXT, idx, linetext)
			ss =linetext[0:linelength*2].decode()
			s2 = ""
			for idy in range(linelength):
				s2 += ss[idy * 2]
			if len(s2) > 0:
				self.craftworkBox.addItem(s2)

	def __checkHandle(self, handle, handleName):
		print('[handle]: %s = %X' %(handleName, handle))
		if handle < 1:
			self.__initHandleFailed = True

	def __initHandle(self):
		self.__mainHandle = win32gui.FindWindow(0, 'SIEMENS-SIMATIC IT MES Client')
		# self.__mainHandle = win32gui.FindWindow(0, 'Mod MES Client')
		if self.__mainHandle < 1:
			print('can not find \'SIEMENS-SIMATIC IT MES Client\' ')
			self.__initHandleFailed = True
			return
		toolStripHandle = getToolStripContainer1Handle(self.__mainHandle)
		if toolStripHandle < 1:
			print('can not find \'toolStripContainer1\' handle.')
			self.__initHandleFailed = True
			return
		produceHandle = getProduceClientHandle(toolStripHandle)
		if produceHandle < 1:
			print('can not find \'生产客户端\' handle.')
			self.__initHandleFailed = True
			return
		
		self.__snHandle = getTargetHandle(produceHandle, [4,10])
		self.__checkHandle(self.__snHandle, 'sn')
			
		self.__craftworkHandle = getTargetHandle(produceHandle, [5,0])
		self.__checkHandle(self.__craftworkHandle, 'craftwork')
			
		self.__jobNumHandle = getTargetHandle(produceHandle, [3,1])
		self.__checkHandle(self.__jobNumHandle, 'jobNum')

		self.__locNumHandle = getTargetHandle(produceHandle, [3,0])
		self.__checkHandle(self.__locNumHandle, 'locNum')

		self.__scanHandle = getTargetHandle(produceHandle, [2])
		self.__checkHandle(self.__scanHandle, 'scan')
		self.__initHandleFailed = False

	def __initStatusbar(self):
		if self.__initHandleFailed:
			self.statusBar().showMessage('查找MES客户端失败')
			self.statusBar().setStyleSheet("color:red;") 
		else:
			self.statusBar().showMessage('查找MES客户端成功')
			self.statusBar().setStyleSheet("color:green;") 

	def __initOther(self):
		enable = True #not self.__initHandleFailed
		self.craftworkBox.setEnabled(enable)
		self.singleSn.setEnabled(enable)
		self.multiSn.setEnabled(enable)
		self.multiNum.setEnabled(enable)
		self.multiNum.setText('')
		if enable:
			self.singleSn.setFocus()
		self.btnClear.setEnabled(enable)
		self.btnScan.setEnabled(enable)
		self.multiCreateSn.setEnabled(enable)
		self.snTable.setEnabled(enable)
		self.snTable.setColumnWidth(0, 220)
		self.snTable.setColumnWidth(1, 100)
		self.snTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
		
		palette = QPalette()
		palette.setColor(QPalette.WindowText, Qt.red) 
		self.num_job.setPalette(palette)
		palette2 = QPalette()
		palette2.setColor(QPalette.WindowText, Qt.blue) 
		self.num_loc.setPalette(palette2)
		
		self.singleSn.returnPressed.connect(self.__singleScan)
		self.multiSn.returnPressed.connect(self.__multiSnFinish)
		self.multiNum.returnPressed.connect(self.__createSn)
		self.multiCreateSn.clicked.connect(self.__createSn)
		self.craftworkBox.currentIndexChanged.connect(self.__craftworkChange)
		self.btnClear.clicked.connect(self.__multiReset)
		self.btnScan.clicked.connect(self.scanAll)
		self.__craftworkChange()
		self.__loadCalcNum()
		if not os.path.isdir(sys.path[0] + '\DataLog'):
			os.makedirs(sys.path[0] + '\DataLog')

	def saveProduct(self,productId, ret):
		fileName = sys.path[0] + '\DataLog' + "\%sScan.txt"%(datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d'))
		try:
			fd = open(fileName,'a+')
			fd.write(datetime.datetime.strftime(datetime.datetime.now(),'%H:%M:%S') + " " + productId + " return " + str(ret) + "\n")
			fd.close()
		except Exception as e:
			reply = QMessageBox.information(self,"消息", ("\n生成%s失败\n"%fileName + str(e) + "\n"), QMessageBox.Yes)

	def __checkHandleagain(self):
		if self.__initHandleFailed:	#重新检查
			self.__initHandle()
		else:
			mainHandle = win32gui.FindWindow(0, 'SIEMENS-SIMATIC IT MES Client')
			# mainHandle = win32gui.FindWindow(0, 'Mod MES Client')
			if mainHandle != self.__mainHandle:
				self.__initHandleFailed = True

	def scanAll(self):
		rows = self.snTable.rowCount()
		for i in range (rows):
			if self.snTable.item(i, 1).text() == "成功":
				continue
			productId = self.snTable.item(i,0).text()
			self.snTable.setCurrentCell(i,0)
			result = self.__addProduct(productId)
			self.saveProduct(productId, result)
			if result == 0:
				mqtt.mqttObjSend(self.__lineTopic, {'productId' : productId.upper(), "seatId" : self.__seatId})
				item2 = QTableWidgetItem("成功")
				item2.setBackground(QColor(0,255,0))
				self.snTable.setItem(i, 1, item2)
			elif result == 1:
				item2 = QTableWidgetItem("未执行")
				#item2.setBackground(QColor(0,255,0))
				self.snTable.setItem(i, 1, item2)
				break
			else:
				item2 = QTableWidgetItem("失败")
				item2.setBackground(QColor(255,0,0))
				self.snTable.setItem(i, 1, item2)
	
	def __singleScan(self):
		productId = self.singleSn.text().replace(' ', '')
		productId = productId.replace('\n', '')
		productId = productId.replace('\r', '')
		if len(productId) < 1:
			return
		if productId in self.__productHistory:
			self.singleSn.clear()
			QMessageBox.information(self,"消息", ("\n序列号%s已经扫描。\n"%productId), QMessageBox.Yes)
			return
		else:
			self.__productHistory.append(productId)
		self.singleSn.setText('')
		ret = self.__addProduct(productId)
		self.saveProduct(productId, ret)
		if ret == 0:
			row = self.snTable.rowCount()
			self.snTable.setRowCount(row + 1)
			item = QTableWidgetItem(productId)
			self.snTable.setItem(row, 0, item)
			item2 = QTableWidgetItem("成功")
			item2.setBackground(QColor(0,255,0))
			self.snTable.setItem(row, 1, item2)
			mqtt.mqttObjSend(self.__lineTopic, {'productId' : productId.upper(), "seatId" : self.__seatId})
		elif ret == 2:
			row = self.snTable.rowCount()
			self.snTable.setRowCount(row + 1)
			item = QTableWidgetItem(productId)
			self.snTable.setItem(row, 0, item)
			item2 = QTableWidgetItem("失败")
			item2.setBackground(QColor(255,0,0))
			self.snTable.setItem(row, 1, item2)

	def __multiSnFinish(self):
		self.multiNum.setText('')
		self.multiNum.setFocus()

	def __createSn(self):
		self.snTable.setRowCount(0)
		productId = self.multiSn.text().replace(' ', '')
		if len(productId) < 1:
			return
		cnt = self.multiNum.text().replace(' ', '')
		if not cnt.isdigit():
			return
		num = int(cnt)
		if num < 1:
			return
		
		prolen = len(productId)
		snStr = productId
		snNum = -1
		for i in range(1, prolen + 1):
			if productId[-i] not in '0123456789':
				index = prolen - i + 1
				snStr = productId[0:index]
				s2 = productId[index:]
				if s2.isdigit():
					snNum = int(s2)
				break
		numLen = prolen - len(snStr)
		if snNum > -1:
			self.snTable.setRowCount(num)
			for i in range(num):
				s1 = str(snNum + i)
				while len(s1) < numLen:
					s1 = '0' + s1
				item = QTableWidgetItem(snStr + s1)
				self.snTable.setItem(i, 0, item)
				item2 = QTableWidgetItem("未执行")
				self.snTable.setItem(i, 1, item2)

	def __multiReset(self):
		self.multiNum.setText('')
		self.multiSn.setText('')
		self.snTable.setRowCount(0)
		self.multiSn.setFocus()

	def __craftworkChange(self):
		index = self.craftworkBox.currentIndex()
		if self.__craftworkHandle > 0:
			win32api.SendMessage(self.__craftworkHandle, win32con.CB_SETCURSEL, index, 0)

	def __loadCalcNum(self):
		self.num_job.setText('0')
		self.num_loc.setText('0')
		if self.__jobNumHandle > 0:
			self.num_job.setText(win32gui.GetWindowText(self.__jobNumHandle))
		if self.__locNumHandle > 0:
			self.num_loc.setText(win32gui.GetWindowText(self.__locNumHandle))
	
	def initAll(self):
		self.__loadCfg()
		self.__initHandle()
		self.__initCraftwork()
		self.__initStatusbar()
		self.__initOther()

	#启动线程
	def start(self):
		self.__threadRun = True
		if not self.__threadCmd.isAlive():
			self.__threadCmd.start()

	#停止线程
	def stop(self):
		self.__threadRun = False
		if self.__threadCmd.isAlive():
			self.__condCmd.acquire()
			self.__condCmd.notify()
			self.__condCmd.release()
			#self.__threadCmd.join()

	#0: 执行成功, 1: 未执行, 2: 执行失败
	def __addProduct(self, productId):
		#检查mes客户端
		self.__checkHandleagain()
		self.__initStatusbar()
		if self.__initHandleFailed:
			QMessageBox.information(self,"消息", ("\n请检查MES客户端是否打开\n\n"), QMessageBox.Yes)
			return 1
		if self.__snHandle < 1 or self.__scanHandle < 1:
			return 1
		if self.findMsgForm():
			QMessageBox.information(self,"消息", ("\n请先关闭MES客户端的提示窗口\n\n"), QMessageBox.Yes)
			return 1
		win32api.SendMessage(self.__snHandle, win32con.WM_SETTEXT, 0, productId)
		win32api.PostMessage(self.__scanHandle, win32con.BM_CLICK, 0, 0)	#非阻塞方式
		self.__condCmd.acquire()
		self.__flag = 1
		self.__condCmd.notify()
		self.__condCmd.release()
		cnt = 0
		while cnt < 20:
			if self.__flag == 3 or self.__flag == 2:
				break
			cnt = cnt + 1
			mysleep(0.1)
		self.__loadCalcNum()
		if self.__flag == 3:	#有错误
			return 2
		else:
			return 0
		
	def __threadCmdFunc(self, args):
		while self.__threadRun:
			self.__condCmd.acquire()
			self.__condCmd.wait()
			if not self.__threadRun:
				self.__condCmd.release()
				break
			cnt = 0
			tag = 0
			try:
				while (self.__flag == 1) and (cnt < 15):
					cnt += 1
					self.closeMesMsgForm('提问', "否(&N)")
					tag = tag + self.closeMesMsgForm('警告', "确定")
					self.closeMesMsgForm('提示', "OK")
					self.closeMesMsgForm('Please wait...', None)
					self.closeMesMsgForm('Microsoft .NET Framework', None)
					mysleep(0.1)
				if tag > 0:
					self.__flag = 3 #设置错误
				else:
					self.__flag = 2
			finally:
				self.__condCmd.release()

	def findMsgForm(self):
		titleList = ["提问","警告","提示","Please wait...","Microsoft .NET Framework"]
		for title in titleList:
			handle = win32gui.FindWindow(0,title)
			if handle > 0:
				return True
			#for i in range(2):
				#handle = win32gui.FindWindow(0,title)
				#if handle > 0:
					#return True
				#mysleep(0.1)
		return False
		
	def closeMesMsgForm(self, formTitle, btnCaption=None):
		alertHandle = win32gui.FindWindow(0, formTitle)
		if alertHandle < 1:
			return 0
		try:
			if btnCaption is None:
				win32api.SendMessage(alertHandle, win32con.WM_CLOSE, 0, 0)
			else:
				btnHandle = win32gui.FindWindowEx(alertHandle, 0, None, btnCaption)
				if btnHandle > 0:
					win32api.SendMessage(btnHandle, win32con.BM_CLICK, 0, 0)
			return 1
		except Exception as e:
			print ("MES窗口点击异常---%s"%formTitle)
			return 1

			
def run_app():
	app = PyQt5.QtWidgets.QApplication(sys.argv)
	mainWin = assembleProxy()
	mainWin.initAll()
	mainWin.start()
	mainWin.show() 
	sys.exit(app.exec_())


if __name__ == '__main__':
	run_app()


