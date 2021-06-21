# coding: utf-8
# author: ives
# date: 2017-11-15
# desc: MES包装区

import sys
import os
import win32gui
import win32api
import win32con
import time
import datetime
import threading
import uiMesPack
import mqtt
import configparser
import mongodb as db
import xlwt

import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QStatusBar, QTableWidgetItem, QAbstractItemView, QMessageBox)
from PyQt5.QtGui import (QPalette, QColor)
from PyQt5.QtCore import (Qt, QDateTime, QTime, QCoreApplication)


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
	
def sleep(s):
	global _exited 
	ms = s*1000
	start = time.time()*1000
	while not _exited:
		if time.time()*1000 - start < ms: 
			QCoreApplication.processEvents()
		else:
			return True
	else:
		log.warning("延时调用退出_exited= %d"%_exited)
		return False
	return True
	
class packProxy(PyQt5.QtWidgets.QMainWindow, uiMesPack.Ui_MainWindow):
	def __init__(self, parent = None):
		super(packProxy, self).__init__(parent) 
		self.setupUi(self)
		self.__mainHandle = 0
		self.__snHandle = 0
		self.__craftworkHandle = 0
		self.__jobNumHandle = 0
		self.__locNumHandle = 0
		self.__scanHandle = 0
		self.__initHandleFailed = False
		self.__threadRun = True
		self.__threadCmd = threading.Thread(target=self.__threadCmdFunc, args=('packProduct',))
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
		packIndex = -1
		for idx in range(cnt):
			linelength = win32gui.SendMessage(handle, win32con.CB_GETLBTEXT, idx, linetext)
			ss =linetext[0:linelength*2].decode()
			s2 = ""
			for idy in range(linelength):
				s2 += ss[idy * 2]
			if len(s2) > 0:
				self.craftworkBox.addItem(s2)
			if s2.find('Pack') >= 0:
				packIndex = idx
		if packIndex != -1:
			self.craftworkBox.setCurrentIndex(packIndex)

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
		
		# self.__snHandle = win32gui.FindWindowEx(self.__mainHandle, 0,None,"")
		# self.__checkHandle(self.__snHandle, '')
		# self.__scanHandle = win32gui.FindWindowEx(self.__mainHandle, 0, None, "扫描")
		# self.__checkHandle(self.__scanHandle, '扫描')
		# self.__initHandleFailed = False

	def __initStatusbar(self):
		if self.__initHandleFailed:
			self.statusBar().showMessage('查找MES客户端失败')
			self.statusBar().setStyleSheet("color:red;") 
		else:
			self.statusBar().showMessage('查找MES客户端成功')
			self.statusBar().setStyleSheet("color:green;") 

	def __initOther(self):
		enable = not self.__initHandleFailed
		enable = True
		self.craftworkBox.setEnabled(enable)
		self.singleSn.setEnabled(enable)
		if enable:
			self.singleSn.setFocus()
		self.snTable.setEnabled(enable)
		self.snTable.setColumnWidth(0, 200)
		self.snTable.setColumnWidth(1, 80)
		self.snTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
		
		palette = QPalette()
		palette.setColor(QPalette.WindowText, Qt.red) 
		self.num_job.setPalette(palette)
		palette2 = QPalette()
		palette2.setColor(QPalette.WindowText, Qt.blue) 
		self.num_loc.setPalette(palette2)
		
		self.singleSn.returnPressed.connect(self.__singleScan)
		self.craftworkBox.currentIndexChanged.connect(self.__craftworkChange)
		self.btnClear.clicked.connect(self.__resetTable)
		self.btnScan.clicked.connect(self.scanAll)
		self.__craftworkChange()
		self.__loadCalcNum()
		tm = time.time()
		dt = QDateTime.fromMSecsSinceEpoch(tm * 1000)
		dt.setTime(QTime.fromString("08:00:00"))
		self.dt_begin.setDateTime(dt)
		dt.setTime(QTime.fromString("21:00:00"))
		self.dt_end.setDateTime(dt)
		self.btn_createForm.clicked.connect(self.createForm)

	def createForm(self):
		dtBegin = datetime.datetime.strptime(self.dt_begin.text(), "%Y/%m/%d %H:%M")
		dtEnd = datetime.datetime.strptime(self.dt_end.text(), "%Y/%m/%d %H:%M")
		ds = db.find('u_product', {'status' : 'finish', 'location' : self.__seatId, 'packEnd': {'$lte' : dtEnd, '$gte': dtBegin}}, \
			['productTypeId', 'productName', 'job', 'packEnd'])
		infos = {}
		while ds.next():
			if not ds.get('packEnd'):
				continue
			jobId = ds['job']
			if jobId not in infos:
				infos[jobId] = {'sapId' : ds['productTypeId'], 'productName' : ds['productName'], 'num' : 1}
			else:
				infos[jobId]['num'] = infos[jobId]['num'] + 1
		data = []
		for key in infos:
			data.append({"jobId":key, "sapId": infos[key]['sapId'], "productName": infos[key]['productName'], \
				"num" : infos[key]['num']})
		self.saveForm(data, dtBegin, dtEnd)

	def saveProduct(self,productId):
		fileName = sys.path[0] + '\DataLog' + "\%s扫码记录.txt"%(datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d'))
		try:
			if not os.path.isdir(sys.path[0] + '\DataLog'):
				os.makedirs(sys.path[0] + '\DataLog')
			fd = open(fileName,'a+')
			fd.write(datetime.datetime.strftime(datetime.datetime.now(),'%H:%M:%S') + " " + productId + "\n")
			fd.close()
		except Exception as e:
			reply = QMessageBox.information(self,"消息", ("\n生成%s失败\n"%fileName + str(e) + "\n"), QMessageBox.Yes)

	def saveForm(self, data, dtBegin, dtEnd):
		fileName = self.__filePath + self.__seatId + ("_%s(%s-%s).xls" %(dtEnd.strftime("%Y%m%d"), \
			dtBegin.strftime("%H%M"), dtEnd.strftime("%H%M")))
		try:
			fd = xlwt.Workbook()
			sheet1 = fd.add_sheet(u'sheet1',cell_overwrite_ok=True)
			row0 = [u'行标签',u'整机代码',u'整机型号',u'计数项：整机编号']
			for i in range(0,len(row0)):
				sheet1.write(0,i,row0[i],self.setStyle('Times New Roman',240,True))
			sheet1.col(0).set_width(3000)
			sheet1.col(1).set_width(7500)
			sheet1.col(2).set_width(10000)
			sheet1.col(3).set_width(7500)
			dataLen = len(data)
			total = 0
			for i in range(dataLen):
				sheet1.write(i + 1, 0, data[i]["jobId"], self.setStyle('Times New Roman',220,False))
				sheet1.write(i + 1, 1, data[i]["sapId"], self.setStyle('Times New Roman',220,False))
				sheet1.write(i + 1, 2, data[i]["productName"], self.setStyle('Times New Roman',220,False))
				sheet1.write(i + 1, 3, data[i]["num"], self.setStyle('Times New Roman',220,False))
				total += data[i]["num"]
			row2 = [u'#N/A',u'#N/A',u'#N/A']
			for i in range(0,len(row2)):
				sheet1.write(dataLen + 1, i, row2[i], self.setStyle('Times New Roman',220,False))
			row3 = [u'(空白)',u'(空白)',u'(空白)']
			for i in range(0,len(row3)):
				sheet1.write(dataLen + 2, i, row3[i], self.setStyle('Times New Roman',220,False))
			row4 = [u'总计', '', '', total]
			for i in range(0,len(row4)):
				sheet1.write(dataLen + 3, i, row4[i], self.setStyle2())

			fd.save(fileName)
			reply = QMessageBox.information(self,"消息", ("\n生成报表成功\n\n%s\n" %fileName), QMessageBox.Yes)
		except Exception as e:
			reply = QMessageBox.information(self,"消息", ("\n生成报表失败\n\n" + str(e) + "\n"), QMessageBox.Yes)

	def setStyle(self, name, height, bold=False):
		style = xlwt.XFStyle()
		font = xlwt.Font()
		font.name = name
		font.bold = bold
		font.color_index = 4
		font.height = height
		style.font = font
		return style
	
	def setStyle2(self):
		style = xlwt.XFStyle()
		font = xlwt.Font()
		font.name = 'Times New Roman'
		font.bold = True
		font.color_index = 4
		font.height = 220
		style.font = font
		pt = xlwt.Pattern()
		pt.pattern = 1 #设置底纹的图案索引，1为实心，2为50%灰色，对应为excel文件单元格格式中填充中的图案样式
		pt.pattern_fore_colour = 22	#设置底纹的前景色，对应为excel文件单元格格式中填充中的背景色
		pt.pattern_back_colour = 35	#设置底纹的背景色，对应为excel文件单元格格式中填充中的图案颜色
		style.pattern = pt
		return style

	def __resetTable(self):
		self.snTable.setRowCount(0)

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
		suNum = 0
		faNum = 0
		for i in range (rows):
			productId = self.snTable.item(i,0).text()
			self.snTable.setCurrentCell(i,0)
			result = self.__addProduct(productId)
			mqtt.mqttObjSend(self.__lineTopic, {'productId' : productId.upper(), "seatId" : self.__seatId})
			if result == 1:
				suNum += 1
				item2 = QTableWidgetItem("成功")
				item2.setBackground(QColor(0,255,0))
				self.snTable.setItem(i, 1, item2)
			else:
				faNum += 1
				item2 = QTableWidgetItem("失败")
				item2.setBackground(QColor(255,0,0))
				self.snTable.setItem(i, 1, item2)
				if result != 2:
					break
			# sleep(0.2)
		QMessageBox.information(self,"消息", ("\nMES过站共计%d个，\n成功共计%d个，失败共计%d个\t"%(rows,suNum,faNum)), QMessageBox.Yes)

	def __singleScan(self):
		productId = self.singleSn.text().replace(' ', '')
		productId = productId.replace('\n', '')
		productId = productId.replace('\r', '')
		if len(productId) < 1:
			return
		if productId in self.__productHistory:
			self.singleSn.clear()
			return
		else:
			self.__productHistory.append(productId)
		self.saveProduct(productId)
		self.singleSn.setText('')
		row = self.snTable.rowCount()
		self.snTable.setRowCount(row + 1)
		item = QTableWidgetItem(productId)
		self.snTable.setItem(row, 0, item)

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

	#def __saveToDb(self, productId):
	#	db.update_one('u_product', {'_id' : productId}, {'area' : 'pack', 'status' : 'finish'}, True)
	
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
			
	def __addProduct(self, productId):
		#检查mes客户端
		self.__checkHandleagain()
		self.__initStatusbar()
		if self.__initHandleFailed:
			QMessageBox.information(self,"消息", ("\n请检查MES客户端是否打开\n\n"), QMessageBox.Yes)
			return 0
		if self.__snHandle < 1 or self.__scanHandle < 1:
			return 3
		self.__loadCalcNum()
		
		while self.find_Handle():
			print ("存在窗口-----",productId)
			sleep(0.1) 
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
			sleep(0.1)
			print ("循环内----",cnt)
		print ("循环外",productId,"-----",self.__flag)
		if self.__flag == 3:	#有错误
			return 2
		self.__flag = 2
		self.__loadCalcNum()
		return 1
		
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
				while (self.__flag == 1) and (cnt < 10):
					print (cnt)
					cnt += 1
					print ('提问',self.closeMesMsgForm('提问',"否(&N)"))
					tag = tag + self.closeMesMsgForm('警告',"确定") 
					print ('警告',tag)
					print ('提示',self.closeMesMsgForm('提示',"OK"))
					print ('Please wait...',self.closeMesMsg('Please wait...',"&Continue"))
					print ('Microsoft .NET Framework',self.closeMesMsg('Microsoft .NET Framework',"&Continue"))
					sleep(0.1)
				if tag > 0:
					self.__flag = 3 #设置错误
				if self.__flag != 3:
					self.__flag = 2
			finally:
				self.__condCmd.release()

	def find_Handle(self):
		titleList = ["提问","警告","提示","Please wait...","Microsoft .NET Framework"]
		for title in titleList:
			# handle = win32gui.FindWindow(0,title)
			# if handle > 0:
				# return True
			for i in range(2):
				handle = win32gui.FindWindow(0,title)
				if handle > 0:
					return True
				sleep(0.1)
		return False
		
	def closeMesMsgForm(self, formTitle, btnCaption):
		alertHandle = win32gui.FindWindow(0, formTitle)
		if alertHandle < 1:
			return 0
		index = 5
		try:
			while index > 0 :
				index -= 1
				alertHandle = win32gui.FindWindow(0,formTitle)
				if alertHandle < 1:
					continue
				else:
					btnHandle = win32gui.FindWindowEx(alertHandle,0,None,btnCaption)
					if btnHandle != 0:
						win32api.SendMessage(btnHandle, win32con.BM_CLICK, 0, 0)
						break
				sleep(0.1)
			return 1
		except Exception as e:
			print ("MES窗口点击异常---%s"%e)
			return 1
		
	def closeMesMsg(self, formTitle, btnCaption):
		alertHandle = win32gui.FindWindow(0, formTitle)
		if alertHandle < 1:
			return 0
		index = 5
		try:
			while index > 0 :
				index -= 1
				alertHandle = win32gui.FindWindow(0,formTitle)
				if alertHandle < 1:
					continue
				else:
					win32api.SendMessage(alertHandle, win32con.WM_CLOSE, 0, 0)
					return 1
				sleep(0.1)
			return 1
		except Exception as e:
			print ("MES窗口点击异常---%s"%e)
			return 1
		
def run_app():
	app = PyQt5.QtWidgets.QApplication(sys.argv)
	mainWin = packProxy()
	mainWin.initAll()
	mainWin.start()
	mainWin.show() 
	sys.exit(app.exec_())


#========================================== unit test ==========================================
def test_sendMqtt():
	mqtt.initMqttObj('172.16.64.252')
	while True:
		mqtt.mqttObjSend('scada/mesPackClient/product', {'productId' : 'ives0123'})
		time.sleep(1)

def test_select():
	dtBegin = datetime.datetime.strptime('2018/01/23 08:30', "%Y/%m/%d %H:%M")
	dtEnd = datetime.datetime.strptime('2018/01/23 18:30', "%Y/%m/%d %H:%M")
	ds = db.find('u_product', {'status' : 'finish', 'location' : 'pack01', 'packEnd': {'$lte' : dtEnd, '$gte': dtBegin}}, \
		['productTypeId', 'productName', 'job', 'packEnd'])
	print(ds)


if __name__ == '__main__':
	#test_sendMqtt()
	#test_select()
	run_app()


