#coding=utf-8 
# ycat			2017-08-03	  create
# 带屏幕键盘的数字输入框 
import os,sys
import qtawesome as qta

import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)

from PyQt5.QtCore import Qt,QEvent,QPoint
from PyQt5.QtGui import QPalette,QColor
from PyQt5.QtWidgets import (QApplication, QGridLayout, QHBoxLayout,QLayout, QLineEdit,QLabel,
		QSizePolicy, QToolButton, QWidget,QTextEdit,QDialog,QPushButton)
import ui.popDlg
import qtutility,enhance
		
#TODO ycat:   4. 退格键不支持 ,5 数字键盘的按下显示状态 

class numberBox(QLineEdit):
	pad = None
	def __init__(self, value = 0, min = 0, max = sys.maxsize,parent=None):
		super(numberBox, self).__init__(parent)	
		if numberBox.pad is None:
			numberBox.pad = numberPad()
		self.setReadOnly(True)
		self.precision = 0
		self._min = min
		self._max = max
		if self.range[0] < 0:
			self.sign = True
		else:
			self.sign = False
		self._setValue(value,showWarning=False)
		
	@property
	def min(self):
		return self._min
		
	@min.setter
	def min(self,value):
		self._min = value
		if value<0:
			self.sign = True
		else:
			self.sign = False
		
	@property
	def max(self):
		return self._max
		
	@max.setter
	def max(self,value):
		self._max = value
		
	def fontSize(self):
		return self.font().pointSize()
		
	def setFontSize(self,size):
		font = self.font()
		font.setPointSize(size)
		self.setFont(font)
	
	def setValue(self,v):
		return self._setValue(v,True)
	
	def _setValue(self,v,showWarning):
		min,max = self.range
		if v < min:
			if showWarning: 
				qtutility.showWaring("请输入%d~%d的数字"%(min,max))
			v = min
		elif v > max:
			if showWarning:
				qtutility.showWaring("请输入%d~%d的数字"%(min,max))
			v = max
		if self.precision == 0:
			s = str(int(v))
		else:
			f = "%%0.%df"%self.precision
			s = f%float(v)
		self.setText(s)
	
	def value(self):
		text = self.text()
		return float(text)
	
	@property
	def range(self):
		m1 = self._min
		if enhance.is_callable(self._min):
			m1 = self._min()
		m2 = self._max
		if enhance.is_callable(self._max):
			m2 = self._max()
		return (m1,m2)
	
	#QMouseEvent 
	def mousePressEvent(self,event):
		pad = numberBox.pad
		pad.waitingForOperand = True
		pad.setValueFunc = self.setValue
		pad.setPrecision(self.precision)
		pad.setSign(self.sign)
		pad.setValue(self.text())
		pad.show(self)

class numberPad(ui.popDlg.popDlg):
	NumDigitButtons = 10
	
	class Button(QToolButton):
		def __init__(self, text, iconName, color, parent=None):
			super(numberPad.Button, self).__init__(parent)
			self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
			self.setText(text)
			if iconName:
				self.setIcon(qta.icon(iconName,color=color))
				self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)			
			font = self.font() 
			font.setPointSize(font.pointSize() + 1)
			self.setFont(font)
			self.setCursor(Qt.PointingHandCursor)
			
			p = QPalette(self.palette())
			p.setColor(QPalette.ButtonText,  QColor(color))
			self.setAutoFillBackground(True)
			self.setPalette(p) 
			
		def sizeHint(self):
			size = super(numberPad.Button, self).sizeHint()
			size.setHeight(size.height() + 25)
			size.setWidth(max(size.width(), size.height()))
			return size			
	
	def __init__(self, parent=None):
		super(numberPad, self).__init__(parent)
		self.setWindowIcon(qta.icon("fa.calculator",color=QColor(staticMgr.accentColor)))
		self.setWindowTitle("numberPad")
	  
		self.setFixedSize(300,300)    
		self.waitingForOperand = True
		
		self.display = QLineEdit('0')
		self.display.setReadOnly(True)
		self.display.setAlignment(Qt.AlignRight)
		self.display.setMaxLength(15)
		font = self.display.font()
		font.setPointSize(font.pointSize() + 10)
		self.display.setFont(font)
		self.precision = 0
		self.pendingSign = ""

		self.digitButtons = []
		for i in range(numberPad.NumDigitButtons):
			self.digitButtons.append(self.createButton(str(i),"","blue",self.digitClicked))

		self.pointButton = self.createButton("小数.","","blue", self.pointClicked)
		self.pointButton.setEnabled(False)
		 
		mainLayout = QGridLayout()
		mainLayout.addWidget(self.display, 0, 0, 1, 4) 
	
		for i in range(1, numberPad.NumDigitButtons):
			row = ((9 - i) / 3) + 1
			column = ((i - 1) % 3) 
			mainLayout.addWidget(self.digitButtons[i], row, column)

		mainLayout.addWidget(self.digitButtons[0], 4, 0,1,2)
		self.signButton = self.createButton("±","","blue", self.signClicked)
		self.signButton.setEnabled(False)
		#mainLayout.addWidget(self.signButton, 4, 1)
		mainLayout.addWidget(self.signButton, 5, 2)
		mainLayout.addWidget(self.pointButton, 4, 2)
		
		btn = self.createButton("确\n认","fa.check","white",self.accept)
		btn.setStyleSheet("background-color:limegreen;color:white;")
		mainLayout.addWidget(btn, 1, 3,3,1)

		self.backspaceButton = self.createButton("退格","fa.long-arrow-left","red",self.backspaceClicked)
		self.clearButton = self.createButton("清零(&C)","fa.remove","red",self.clear)
		mainLayout.addWidget(self.clearButton, 5, 0, 1, 2)
		#mainLayout.addWidget(self.backspaceButton, 5, 2)
		btn = self.createButton("取\n消","","red",self.reject)
		btn.setStyleSheet("background-color:orangered;color:white;")
		mainLayout.addWidget(btn, 4, 3, 2, 1)
		
		self.setLayout(mainLayout)
		self.setValueFunc = None	
		self.finished.connect(self.onFinish)

	def digitClicked(self):
		clickedButton = self.sender()
		digitValue = int(clickedButton.text())
		if self.value() == 0 and digitValue == 0.0:
			return
		sign = self.pendingSign
		if self.waitingForOperand:
			self.display.clear()
			self.waitingForOperand = False
			self.pendingSign = "" 
		t = sign+self.display.text() + str(digitValue)
		if len(t) > 1 and "." not in self.display.text():
			t = t.lstrip("0")
		self.display.setText(t)

	def pointClicked(self):
		if self.waitingForOperand:
			self.display.setText('0')

		if "." not in self.display.text():
			self.display.setText(self.display.text() + ".")
		self.waitingForOperand = False

	def setPrecision(self,value):
		assert value >= 0
		self.precision = value
		p = QPalette(self.pointButton.palette())
		if value == 0:
			p.setColor(QPalette.ButtonText,  QColor("gray")) 
			self.pointButton.setEnabled(False)
		else:
			p.setColor(QPalette.ButtonText,  QColor("blue")) 
			self.pointButton.setEnabled(True)
		self.pointButton.setPalette(p) 
		self.setValue(self.value())
	
	def signClicked(self): 
		if self.waitingForOperand:
			if self.pendingSign == "-":
				self.pendingSign = ""
			else:
				self.pendingSign = "-"
			return
		text = self.display.text()
		value = float(text)
		if value > 0.0:
			text = "-" + text
		elif value < 0.0:
			text = text[1:]
		self.display.setText(text)
	
	def setSign(self,value):
		p = QPalette(self.signButton.palette())
		self.signButton.setEnabled(value)
		if value:
			p.setColor(QPalette.ButtonText,  QColor("blue")) 
		else:
			p.setColor(QPalette.ButtonText,  QColor("gray")) 
		self.signButton.setPalette(p)  
	
	def setValue(self,v): 
		if self.precision == 0:
			try:
				s = str(int(v))
			except:
				s = "0"
			#if int(v) != 0:
			#	self.waitingForOperand = False
			#else:
			#	self.waitingForOperand = True
		else:
			f = "%%0.%df"%self.precision
			try:
				s = f%float(v)
			except:
				s = f%0.0
			#if float(v) != 0:
			#	self.waitingForOperand = False
			#else:
			#	self.waitingForOperand = True
		self.display.setText(s)
	
	def value(self):
		text = self.display.text()
		return float(text) 
		
	def backspaceClicked(self):
		if self.waitingForOperand:
			return
		text = self.display.text()[:-1]
		if not text or text=="-":
			text = '0'
			self.waitingForOperand = True
		self.setValue(text)

	def clear(self):
		#if self.waitingForOperand:
		#	return
		if self.precision == 0:
			self.display.setText('0')
		else:
			f = "%%0.%df"%self.precision
			self.display.setText(f%0.0)
		#self.setValue("0")
		self.waitingForOperand = True
		
	def createButton(self, text, iconName, color, member):
		button = numberPad.Button(text,iconName,color)
		button.clicked.connect(member)
		return button
	   
	def onFinish(self,result):  
		if self.setValueFunc:
			if result == QDialog.Accepted:
				self.setValueFunc(self.value())
	
	#QKeyEvent
	def keyPressEvent(self,event):
		k = event.key() 
		if k >= Qt.Key_0 and k<=Qt.Key_9:
			self.digitButtons[k-Qt.Key_0].click()
		elif k == Qt.Key_Backslash:
			self.backspaceButton.click()
		elif k  == Qt.Key_C or k == Qt.Key_Delete:
			self.clearButton.click() 
		elif k == Qt.Key_Period:
			if self.pointButton.isEnabled():
				self.pointButton.click()
		elif k==Qt.Key_Escape :
			self.reject()
		elif k == Qt.Key_Enter or k==Qt.Key_Return:
			self.accept()
		
			 
		
if __name__ == '__main__':
	class dlg(QDialog): 
		def __init__(self):
			super(dlg, self).__init__() 
			layout = QHBoxLayout()
			nn = numberBox(min=50,max=100)
			nn.precision = 0
			nn.setFontSize(40) 
			nn.setText("99")
			layout.addWidget(nn)
			
			dd = numberBox(min=nn.value,max=500)
			dd.setFontSize(20)
			dd.precision = 2
			layout.addWidget(dd)
			layout.addWidget(QPushButton("ggggggg"))
			layout.addWidget(QPushButton("ggggggg"))
			
			nn = numberBox(min=-500,max=100)
			#nn.precision = 2
			nn.setFontSize(40) 
			nn.setText("-99")
			layout.addWidget(nn)
			
			self.setLayout(layout)
			self.setWindowTitle("QT测试")	
			self.setWindowFlags(self.windowFlags()& ~Qt.WindowMaximizeButtonHint& Qt.WindowMinimizeButtonHint) 		
			self.setMinimumSize(400,400)
			
	app = QApplication(sys.argv)
	d = dlg() 
	d.show() 
	sys.exit(app.exec_())
