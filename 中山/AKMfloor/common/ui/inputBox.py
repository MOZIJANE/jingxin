#coding=utf-8 
# ycat			2017-08-03	  create
# 自动弹出屏幕键盘的输入框 
import os,sys 
import qtawesome as qta
import subprocess,platform
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
from PyQt5.QtCore import Qt,QEvent,QPoint
from PyQt5.QtGui import QPalette,QColor
from PyQt5.QtWidgets import (QApplication, QGridLayout, QHBoxLayout,QLayout, QLineEdit,
		QSizePolicy, QToolButton, QWidget,QTextEdit,QDialog,QPushButton)
 		
class softKeyboard:
	def __init__(self,handPad = True):
		self.keyboard_process = None
		self.processName = ""
		self.handPad = handPad
		#TODO: win7有时不带手写键盘 
		self.handPad = False

	def show(self): 
		if platform.system() == "Linux":
			try:
				cmd_path = "xvkbd"
				self.keyboard_process = subprocess.Popen([cmd_path])
				self.processName = "xvkbd"
				return
			except OSError:
				pass

		elif platform.system() == "Windows":
			if self.handPad:
				cmd = r"C:\Program Files\Common Files\Microsoft Shared\ink\TabTip.exe"
				self.processName = "TabTip.exe"
			else:
				cmd = r"C:\WINDOWS\system32\osk.exe"
				self.processName = "osk.exe"
			self.keyboard_process = subprocess.Popen([cmd], shell=True)

	def hide(self): 
		if platform.system() == "Windows":
			cmd = "taskkill /im "+self.processName+" /f  1>nosence.txt 2>&1"
			os.system(cmd)
			#cmd = "taskkill /im TabTip.exe /f"
			#os.system(cmd)
		else:
			if self.keyboard_process is not None:
				self.keyboard_process.kill()
				self.keyboard_process = None


class inputBox(QLineEdit): 
	def __init__(self,handPad = True,parent=None):   
		super(inputBox, self).__init__(parent)
		self.keyboard = softKeyboard(handPad) 
		
	def dlg(self):
		while True:
			p =  self.parentWidget()
			if isinstance(p,QDialog):
				return p
	
	#QMouseEvent
	def mousePressEvent(self,event): 
		self.keyboard.show() 
		super(inputBox, self).mousePressEvent(event)
	
	def focusInEvent(self,event):  
		return
		self.keyboard.show() 
		super(inputBox, self).focusInEvent(event)
		
	#QFocusEvent 
	def focusOutEvent(self,event): 
		if self.dlg().isActiveWindow():
			self.keyboard.hide() 
		super(inputBox, self).focusOutEvent(event)
		
	def setFontSize(self,size):
		font = self.font()
		font.setPointSize(size)
		self.setFont(font) 
	
	#QCloseEvent
	def closeEvent(event):
		self.keyboard.hide()
	
if __name__ == '__main__':
	class dlg(QDialog): 
		def __init__(self):
			super(dlg, self).__init__() 
			layout = QHBoxLayout()
			nn = inputBox() 
			nn.setText("99")
			nn.setFontSize(20)
			layout.addWidget(nn)
			
			dd = inputBox() 
			layout.addWidget(dd) 
			layout.addWidget(QPushButton("ggggggg"))
			layout.addWidget(QPushButton("ggggggg"))
			self.setLayout(layout)
			self.setWindowTitle("QT测试")	
			self.setWindowFlags(self.windowFlags()& ~Qt.WindowMaximizeButtonHint& Qt.WindowMinimizeButtonHint) 		
			self.setMinimumSize(400,400)
			
	app = QApplication(sys.argv)
	d = dlg() 
	d.show() 
	sys.exit(app.exec_())

