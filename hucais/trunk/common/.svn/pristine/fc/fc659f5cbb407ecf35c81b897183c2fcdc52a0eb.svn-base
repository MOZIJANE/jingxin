#coding=utf-8 
# ycat			2019-11-03	  create
import os,sys
import math
import PyQt5  
import datetime
import numpy as np
import qtawesome as qta
import matplotlib.pyplot as plt  
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__) 
import ui.listDlg
import ui.chartWidget
import traceReader
import qtutility
import utility
import ui.confUI
import local
import log
import enhance
import counter

class charUI(ui.chartWidget.chartWidget): 
	def __init__(self,reader,parent):
		super(charUI, self).__init__("trace",addToolbar=True)  	
		self.reader = reader
		self.parent = parent
		#self.setMinimumHeight(400)
		self.reader.selectChanged.connect(self.update)
		
	def update(self,*params):
		self.switch()
		self.reader.draw()
		self.draw()
		 
		
		
class filterUI(PyQt5.QtWidgets.QWidget):
	def __init__(self,reader,parent):
		super(filterUI, self).__init__()  
		self.isChanging = False 
		self.reader = reader
		self.reader.selectChanged.connect(self.setSelect)
		self.parent = parent
		layout = PyQt5.QtWidgets.QHBoxLayout()
		self.createFilter(layout)
		self.setLayout(layout)
		self.setFixedHeight(80)
		traceReader.alarmDecoder = self.decodeAlarm
		
	def createFilter(self,layout):
		groupBox = PyQt5.QtWidgets.QGroupBox("过滤条件")
		h = PyQt5.QtWidgets.QHBoxLayout()
		
		self.combo = PyQt5.QtWidgets.QComboBox()
		self.combo.addItem('10秒',10)
		self.combo.addItem('30秒',30)
		self.combo.addItem('1分钟',60)
		self.combo.addItem('2分钟',120)
		self.combo.addItem('5分钟',300)
		self.combo.addItem('10分钟',600)
		self.combo.addItem('30分钟',1800)
		self.combo.setFixedWidth(60)
		qtutility.setValue(self.combo,60)
		qtutility.setChangedEvent(self.combo,self.comboChange)
		
		self.slider = PyQt5.QtWidgets.QSlider(PyQt5.QtCore.Qt.Horizontal)
		self.slider.setFixedWidth(100)
		self.slider.setMinimum(0)
		self.slider.setTickPosition(PyQt5.QtWidgets.QSlider.TicksBelow)
		qtutility.setChangedEvent(self.slider,self.sliderChange)
		
		
		self.filterLabel = PyQt5.QtWidgets.QLabel("")
		h.addWidget(self.slider)
		h.addWidget(self.combo)
		h.addWidget(self.filterLabel)
		  
		b = PyQt5.QtWidgets.QPushButton("图表")
		b.setFixedSize(50,20)
		b.clicked.connect(self.selectChart)
		h.addWidget(b)
		
		b = PyQt5.QtWidgets.QPushButton("告警")
		b.setFixedSize(50,20)
		b.clicked.connect(self.selectAlarm)
		h.addWidget(b)
		
		b = PyQt5.QtWidgets.QPushButton("事件")
		b.setFixedSize(50,20)
		b.clicked.connect(self.selectEvent)
		h.addWidget(b)
		
		b = PyQt5.QtWidgets.QPushButton("显示")
		b.setFixedSize(50,20)
		b.clicked.connect(self.selectDisplay)
		h.addWidget(b)
		
		groupBox.setLayout(h)
		layout.addWidget(groupBox)
		return groupBox
		
	def selectDisplay(self,event):
		tt = ["数据","事件","告警","对象","日志"]
		dlg = ui.listDlg.listDlg("选择显示文本")
		dlg.setMinimumWidth(400)
		for t in tt:
			dlg.addItem(t,checkable=True)
			
		for k in self.parent.textUI.types:
			dlg.setCheckByLabel(tt[k])	
			
		if 1 == dlg.exec():
			kk = dlg.getCheckItemLabels()
			ii = [ tt.index(k) for k in kk] 
			self.parent.textUI.setTypes(ii)
		
		
	def updateSlider(self):
		if self.reader.count == 0:
			return
		sec = self.reader.timespan.total_seconds()
		span = self.reader.maxTime - self.reader.minTime
		s = math.ceil(span.total_seconds() / sec)
		self.slider.setMaximum(span.total_seconds())
		self.slider.setSingleStep(s) 
		if s <= 1:
			self.slider.setEnabled(False)
		else:
			self.slider.setEnabled(True)
		if s > 10:
			s = span.total_seconds()/10
		else:
			s = sec
		self.slider.setTickInterval(s)
			 
	def setSelect(self,index):
		#if self.isChanging:
		#	return
		if index < 0:
			return
		if index >= self.reader.count:
			return
		if self.reader.count == 0:
			return
		dt  = self.reader.data[index][1] - self.reader.minTime
		step  = qtutility.getValue(self.combo)
		begin = int(dt.total_seconds() / step) * step 
		self.isChanging = True
		qtutility.setValue(self.slider,begin) 
		self.isChanging = False 
			
		
	def sliderChange(self,*param):
		if self.reader.count == 0:
			return
		sec = qtutility.getValue(self.slider)+1
		self.reader.currentTime = self.reader.minTime + datetime.timedelta(seconds=sec)
		#print(self.isChanging,sec)
		if not self.isChanging:
			index = self.reader.selectByTime(self.reader.currentTime)
		self.parent.charUI.update() 
		
	def comboChange(self,*param):
		sec = qtutility.getValue(self.combo) 
		self.reader.timespan = datetime.timedelta(seconds=sec)
		self.updateSlider()
		self.parent.charUI.update() 
		
		
	def selectChart(self,event):
		dlg = ui.listDlg.listDlg("选择参数")
		for k in sorted(self.reader.keys):
			dlg.addItem(k,checkable=True)
		
		if self.reader.filter_keys:
			for k in self.reader.filter_keys:
				dlg.setCheckByLabel(k)	
		
		if 1 == dlg.exec():
			kk = dlg.getCheckItemLabels()
			self.reader.setKeyFilter(kk)
			self.changeFilter()
		
	def selectEvent(self,event):
		dlg = ui.listDlg.listDlg("选择事件")
		dlg.setMinimumWidth(400)
		for k in sorted(self.reader.events):
			dlg.addItem(k,checkable=True)
			
		if self.reader.filter_events:
			for k in self.reader.filter_events:
				dlg.setCheckByLabel(k)	
		if 1 == dlg.exec():
			kk = dlg.getCheckItemLabels()
			self.reader.setEventFilter(kk)
			self.changeFilter()
		
	
	def decodeAlarm(self,text):
		import alarmNode.alarmType
		def _decode(key):
			i = key.find(".")
			if i == -1:
				return key,"None"
			return key[0:i],key[i+1:]
		id,instance = _decode(text)
		t = alarmNode.alarmType.get(id)
		if t:
			v = t['cname']
			if instance != "None":
				v += "." + instance
			return v
		return text
		
	def selectAlarm(self,event): 
		dlg = ui.listDlg.listDlg("选择告警")
		for k in sorted(self.reader.alarms):
			dlg.addItem(k,checkable=True)
			
		if self.reader.filter_alarms:
			for k in self.reader.filter_alarms:
				dlg.setCheckByLabel(k) 
				
		for i in range(dlg.list.list.count()):
			item = dlg.list.list.item(i)
			text = item.text()
			v = self.decodeAlarm(text) 
			item.setText(v)
			item.tag = text
		
		if 1 == dlg.exec():
			rr = []
			for i in range(dlg.list.list.count()):
				item = dlg.list.list.item(i)
				if item.checkState() == PyQt5.QtCore.Qt.Checked:
					rr.append(item.tag) 
			self.reader.setAlarmFilter(rr)
			self.changeFilter() 
		
		
	def onValueChange(self,sender):
		self.changeFilter()
		#sender.stateChanged(sender)
	
		
	def update(self): 
		self.updateSlider()
		self.reader.timespan = datetime.timedelta(seconds=qtutility.getValue(self.combo))
		self.reader.currentTime = self.reader.minTime
		return

	def changeFilter(self):
		self.reader.UI.charUI.update()
		self.reader.UI.textUI.update()  
		
	
class textEditCtrl(PyQt5.QtWidgets.QPlainTextEdit):
	def __init__(self,parent):
		self.parent = parent
		super(textEditCtrl, self).__init__()   
		
	def mousePressEvent(self,event):
		ret = super(textEditCtrl, self).mousePressEvent(event)  
		c = self.cursorForPosition(event.pos());
		c.select(PyQt5.QtGui.QTextCursor.LineUnderCursor)
		self.setTextCursor(c)
		self.moveCursor(PyQt5.QtGui.QTextCursor.EndOfLine,PyQt5.QtGui.QTextCursor.MoveAnchor) 
		self.moveCursor(PyQt5.QtGui.QTextCursor.StartOfLine,PyQt5.QtGui.QTextCursor.KeepAnchor) 
		#得出选择的text
		t = self.textCursor().selectedText()
		i = t.find(" ")
		if i == -1:
			return ret
		t = t[0:i]
		log.debug("select:",self.textCursor().selectedText())
		try:
			d = int(t)
		except Exception as e:
			log.exception("toInt() error:"+t,e)
			return ret
		self.parent.onmousepress(d)
		return ret
		 
		
		
class textUI(PyQt5.QtWidgets.QWidget):
	def __init__(self,reader,parent):
		super(textUI, self).__init__()  
		self.parent = parent
		self.reader = reader
		self.types = [0,1,2,3,4]
		self.reader.selectChanged.connect(self.setSelect)
		self.textEdit= textEditCtrl(self)
		self.textEdit.setLineWrapMode(0)	#Text is not wrapped at all
		self.textEdit.setReadOnly(True)
		
		layout = PyQt5.QtWidgets.QVBoxLayout()
		layout.addWidget(self.textEdit)
		self.setLayout(layout)
		
	def findIndex(self,index):
		doc = self.textEdit.document()
		def getIndex(i):
			t = doc.findBlockByNumber(i).text()
			k = t.find(" ")
			if k == -1:
				return None
			return int(t[0:k])
			
		# 二分查找 
		def binSearch(left, right, x):
			if right >= left:
				mid = (left + (right - left) // 2)
				mid_no = getIndex(mid)
				if mid_no is None:
					return -1
					
				if mid_no == x:
					return mid
				elif mid_no > x:
					return binSearch(left, mid - 1, x)
				else:
					return binSearch(mid + 1, right, x)
			else: 
				l = getIndex(left)
				if l is None:
					return -1
				return left
				#if abs((r-x)) < abs((l-x)):
				#	return right
				#return left
		return binSearch(0,doc.blockCount(),index)
		
	def setSelect(self,index):
		doc = self.textEdit.document()
		i = self.findIndex(index)
		if i == -1:
			return
		block = doc.findBlockByNumber(i)
		c = PyQt5.QtGui.QTextCursor(block)
		self.textEdit.setTextCursor(c) 
		c.select(PyQt5.QtGui.QTextCursor.LineUnderCursor)
		self.textEdit.setTextCursor(c)
		self.textEdit.moveCursor(PyQt5.QtGui.QTextCursor.EndOfLine,PyQt5.QtGui.QTextCursor.MoveAnchor) 
		self.textEdit.moveCursor(PyQt5.QtGui.QTextCursor.StartOfLine,PyQt5.QtGui.QTextCursor.KeepAnchor) 
	  
		
	def onmousepress(self,index):
		self.reader.setSelect(index)
		
	def update(self):
		ss = []
		f = "{} {}: {}\t:{}"
		for k,dt,v,t1,t2,i in self.reader.getIter(keys=None):
			if t1 not in self.types:
				continue
			if isinstance(v,bytes):
				v = str(v[0:30])
			if t1 == 2:
				if t2 == "c":
					k = "clear "+ str(k)
			ss.append(f.format(i,utility.str_datetime(dt,True),k,str(v)))
		self.textEdit.setPlainText("\n".join(ss))	
		if self.reader.selectIndex is not None:
			self.setSelect(self.reader.selectIndex)
			
	def setTypes(self,tt):
		self.types = tt
		self.update()
		
		

class traceUI(PyQt5.QtWidgets.QWidget): 
	def __init__(self):
		super(traceUI, self).__init__()  
		self.reader = traceReader.reader()
		self.reader.onselect = self.onselect
		self.reader.UI = self
		 
		self.filterUI = filterUI(self.reader,self)
		self.charUI = charUI(self.reader,self)
		self.textUI = textUI(self.reader,self)
		
		self.splitter = PyQt5.QtWidgets.QSplitter(PyQt5.QtCore.Qt.Vertical)
		self.splitter.setStyleSheet("QSplitter::handle{background-color:lightgray}")
		layout = PyQt5.QtWidgets.QVBoxLayout()
		
		layout.addWidget(self.charUI) 
		layout.addWidget(self.filterUI) 
		w = PyQt5.QtWidgets.QWidget()
		w.setLayout(layout)
		self.splitter.addWidget(w)
		self.splitter.addWidget(self.textUI)
		
		layout2 = PyQt5.QtWidgets.QVBoxLayout()
		layout2.addWidget(self.splitter) 
		self.setLayout(layout2)
		self.openAct = PyQt5.QtWidgets.QAction(qta.icon('fa.folder-open-o',color='black'), "&Open", triggered=self.open)
		#self.showConfAct = PyQt5.QtWidgets.QAction(qta.icon('fa.cogs',color='blue'), "&Config", triggered=self.showConf)
		self.decodeAct = PyQt5.QtWidgets.QAction(qta.icon('fa.calculator',color='orange'), "&Decode", triggered=self.decodeAll)
		self.charUI.toolbar.insertAction(self.charUI.homeAct,self.openAct)
		self.charUI.toolbar.addAction(self.decodeAct)
		#self.charUI.toolbar.addAction(self.showConfAct)
		self.openEvent = enhance.event()
		self.filename = ""
		
	def decodeAll(self):
		import slam.laser
		for o in self.reader.getObjsIter(decode=True):
			pass
		self.textUI.update()   
		
	@property
	def toolbar(self):
		return self.charUI.toolbar
		
	def onselect(self,xmin,xmax):
		self.update()
		
	def load(self,files):
		if isinstance(files,list):
			self.filename = files[0]
		else:
			self.filename = files
			
		if isinstance(files,str):
			files = [files,]
		self.reader.clear()
		self.update()
		for f in files:
			self.reader.load(f)
		self.update()
	
	def update(self): 
		c = counter.counter()
		self.filterUI.update() 
		log.info("update filterUI used",c.get(),"ms")
		self.charUI.update() 	
		log.info("update charUI used",c.get(),"ms")
		self.textUI.update()   
		log.info("update textUI used",c.get(),"ms")
		
	def open(self):
		files, ok = PyQt5.QtWidgets.QFileDialog.getOpenFileNames(self,
                  "选择调试文件",
                  "./",
                  "trace files (*.data);;All Files (*)")
		if not ok:
			return
		self.load(files)
		self.openEvent.emit()
		
	#def showConf(self):
	#	ui.confUI.confDlg(self.reader.getConf()).exec() 
			

if __name__ == '__main__':
	app = PyQt5.QtWidgets.QApplication(sys.argv)
	
	class dlg(PyQt5.QtWidgets.QDialog): 
		def __init__(self):
			super(dlg, self).__init__() 
			layout = PyQt5.QtWidgets.QHBoxLayout()
			nn = traceUI() 
			nn.load("test/20210413_15.data")
			
			layout.addWidget(nn) 
			self.setLayout(layout)
			self.setWindowTitle("QT测试")	 	
			self.setMinimumSize(600,800)
			self.setWindowFlags(PyQt5.QtCore.Qt.WindowMinimizeButtonHint)  
			 
	d = dlg() 
	d.show() 
	sys.exit(app.exec_())
