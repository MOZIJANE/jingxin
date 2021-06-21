#coding=utf-8 
# ycat			2017-08-03	  create
# 失去焦点，就自动退出的对话框
import os,sys 

import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)

from PyQt5.QtCore import Qt,QEvent,QPoint
from PyQt5.QtGui import QPalette,QColor,QPainter
from PyQt5.QtWidgets import QApplication, QDialog,QHBoxLayout,QPushButton

#取结果例子	
#self.finished.connect(self.onFinish)		
#def onFinish(self,result):  
#	if result == QDialog.Accepted:
#		pass
 
class popDlg(QDialog): 
	def __init__(self, isTransparent = False, parent=None):
		super(popDlg, self).__init__(parent)
		self.isTransparent = isTransparent

		#设置透明色的方法 
		flags = Qt.FramelessWindowHint| Qt.WindowMinimizeButtonHint| Qt.WindowSystemMenuHint | Qt.SplashScreen
		self.setAttribute(Qt.WA_TranslucentBackground, True)
		
		self.setWindowFlags(flags)
		self.setFocusPolicy(Qt.StrongFocus)
		self.installEventFilter(self)
		
		self.startPos = None 

	def onClick(self): 
		self.show(self.sender())
	
	def showAt(self,posX,posY,width,height): 
		self.setWindowModality(Qt.WindowModal)
		super(popDlg, self).show()
		screen = QApplication.desktop().screenGeometry()
		r = self.rect() 		
		def calX():
			#TODO:ycat总感觉算的有问题 
			x = posX
			if x < 0:		 
				return 0  
			if screen.contains(QPoint(x+r.width(),posY)): 
				return x
			#if screen.contains(QPoint(x+width,posY)): 
			#	return x-r.width()+width
			return screen.width() - r.width()
			
		def calY(x):
			y = posY
			if y < 0: 
				return 0
			if screen.contains(QPoint(x,y+r.height()+height)): 
				return y+height
			if screen.contains(QPoint(x,y - r.height() - height)): 
				return y-r.height() 
			return y
		xx = calX()
		self.move(calX(),calY(xx)) 
	
	def show(self,parent):
		p = parent.mapToGlobal(parent.pos()) - parent.pos()  
		r = self.rect() 
		self.showAt(p.x(),p.y(),parent.width(),parent.height())
 
	def eventFilter(self, source, event):
		if source != self:
			return False
		if QEvent.WindowDeactivate == event.type():
			if not self.isClosing:
				self.accept() 
			return True
		return False
	
	def accept(self):
		self.isClosing = True
		super(popDlg, self).accept()
		
	def reject(self):
		self.isClosing = True
		super(popDlg, self).reject()
		
	#QShowEvent 
	def	showEvent(self,event):
		self.isClosing = False 
	
	#QPaintEvent 
	def paintEvent(self,event):
		super(popDlg, self).paintEvent(event)
		if not self.isTransparent:
			p = QPainter(self)
			r = event.rect()
			p.fillRect(r,QColor("gray"))
			r.moveTopLeft(QPoint(-4,-4))
			p.fillRect(r,QColor("darkgray"))
	
	#QMouseEvent 
	def mouseMoveEvent(self ,event):	
		if self.startPos is not None: 
			startPos = self.pos() + event.pos() - self.startPos
			self.move(startPos)
		super(popDlg, self).mouseMoveEvent(event)
		
	#QMouseEvent
	def mousePressEvent(self ,event):
		self.startPos = event.pos() 
		super(popDlg, self).mousePressEvent(event)
		
	#QMouseEvent
	def mouseReleaseEvent(self,event):
		self.startPos = None 
		super(popDlg, self).mouseReleaseEvent(event)
		
if __name__ == '__main__':
	import ui.menuDlg
	ui.menuDlg.runTest() 
	
