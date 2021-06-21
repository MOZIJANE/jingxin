#coding=utf-8 
# ycat			2017-08-03	  create
import os,sys
import PyQt5.QtWidgets 
import PyQt5.QtGui 
import PyQt5.QtCore
import qtawesome as qta

import setup
if __name__ == '__main__':
	setup.setCurPath(__file__) 
	
class checkBtn:
	def __init__(self,color1="black",color2="black"):
		self.iconCheck = qta.icon("fa.check-square-o",color=color1)
		self.iconUncheck = qta.icon("fa.square-o",color=color2)
		
class switchBtn:
	def __init__(self,color1="green",color2="gray"):
		self.iconCheck = qta.icon("fa.toggle-on",color=color1)
		self.iconUncheck = qta.icon("fa.toggle-off",color=color2)	
		
class minusBtn:
	def __init__(self,color1="black",color2="black"):
		self.iconCheck = qta.icon("fa.minus-square-o",color=color1)
		self.iconUncheck = qta.icon("fa.square-o",color=color2)
		
class plusBtn:
	def __init__(self,color1="black",color2="black"):
		self.iconCheck = qta.icon("fa.plus-square-o",color=color1)
		self.iconUncheck = qta.icon("fa.square-o",color=color2)
		
	
class checkbox(PyQt5.QtWidgets.QPushButton): 
	def __init__(self,text,checked = False):
		super(checkbox, self).__init__(text) 
		self.setFlat(True)
		self.setIconSize(PyQt5.QtCore.QSize(30,30))
		self._check = checked 
		self.clicked.connect(self._onClick) 
		self.setLayoutDirection(PyQt5.QtCore.Qt.RightToLeft) 
		self.setBtnType(checkBtn())
	
	def setBtnType(self,btnType):
		self.btnType = btnType
		if self.isChecked():
			self.setIcon(self.btnType.iconCheck)
		else:
			self.setIcon(self.btnType.iconUncheck)
	
	def isChecked(self):
		return self._check
	
	def setChecked(self,value): 
		self._check = not value
		self._onClick(value) 
	
	#PyQt5.QtCore.Qt.RightToLeft 
	def setDirection(self,dir):
		self.setLayoutDirection(dir)
	
	def _onClick(self,checked):  
		if self._check: 
			self._check = False
		else: 
			self._check = True
		self.setBtnType(self.btnType)
		self.toggled.emit(self._check) 
		
	def setSize(self,w,h): 
		self.setIconSize(PyQt5.QtCore.QSize(w,h))
		
	def setFontSize(self,size):
		f = self.font()
		f.setPointSize(size)
		self.setFont(f)
		

#三态选择按钮，用鼠标右键选择 	
class checkbox3(checkbox):
	def __init__(self,text,value = 0): 
		super(checkbox3, self).__init__(text,checked=False) 
		self.style = (plusBtn(color1="green",color2="gray"),minusBtn(color1="red",color2="gray"))
		self.setValue(value)
	
	
	def mousePressEvent(self,event): 	
		if event.button() == 2:
			if self.btnType == self.style[0]:
				self.setBtnType(self.style[1])
				self.setChecked(True)
			else:
				self.setChecked(not self.isChecked())
		else:
			if self.btnType == self.style[1]:
				self.setBtnType(self.style[0])
				self.setChecked(True)
				return
		super(checkbox, self).mousePressEvent(event) 
	
	
	@property
	def value(self):
		if not self.isChecked():
			return 0
		if self.btnType == self.style[0]:
			return 1 
		else:
			return -1
			
		 
	def setValue(self,v):
		if v == 1: 
			self.setBtnType(self.style[0])
			self.setChecked(True)
		elif v == -1:
			self.setBtnType(self.style[1])
			self.setChecked(True)
		else:
			self.setBtnType(self.style[0])
			self.setChecked(False)
		self._value = v
		


if __name__ == '__main__':
	app = PyQt5.QtWidgets.QApplication(sys.argv)
	
	class dlg(PyQt5.QtWidgets.QDialog): 
		def __init__(self):
			super(dlg, self).__init__() 
			layout = PyQt5.QtWidgets.QHBoxLayout()
			nn = checkbox(text="hello")
			nn.setBtnType(checkBtn())
			layout.addWidget(nn)
			
			nn = checkbox(text="hello")
			nn.setBtnType(switchBtn())
			nn.setSize(40,40)
			layout.addWidget(nn)
			
			nn = checkbox3(text="hello") 
			nn.setFontSize(19)
			nn.setSize(40,40)
			layout.addWidget(nn)

			self.setLayout(layout)
			self.setWindowTitle("QT测试")	 	
			self.setMinimumSize(400,400)
			 
	d = dlg() 
	d.show() 
	sys.exit(app.exec_())
