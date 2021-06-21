#coding=utf-8 
# ycat			2017-08-03	  create
import os,sys
import qtawesome as qta

import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)

from PyQt5.QtCore import Qt,QEvent,QPoint,QSize
from PyQt5.QtGui import QPalette,QColor
from PyQt5.QtWidgets import QApplication, QDialog,QGridLayout,QToolButton,QHBoxLayout,QPushButton,QSizePolicy
import ui.popDlg
import enhance

#用法:
#注册clicked事件，取出点的button的值 
#menu.clicked.connect(self.onClick)
#def onClick(self,value):
#	print(value,menu.result)
class menuDlg(ui.popDlg.popDlg): 
	def __init__(self, iconSize=48,fontSize=10,parent=None):
		super(menuDlg, self).__init__(isTransparent=True,parent=None)
		self.iconSize = iconSize
		self.fontSize = fontSize 
		self.layout = QGridLayout()
		self.setLayout(self.layout)
		self.result = None
		self.clicked = enhance.event()
	
	def clear(self):
		while self.layout.count():
			w = self.layout.itemAt(0).widget()
			self.layout.removeWidget(w)
			w.setParent(None) 
	
	def add(self,value,text,icon,fromRow,fromColumn,rowSpan=1,columnSpan=1):
		b = self._createButton(value,text,icon) 
		self.layout.addWidget(b,fromRow,fromColumn,rowSpan,columnSpan)
		b.clicked.connect(self._clickBtn)
	
	def addColseButton(self,text,fromRow,fromColumn,rowSpan=1,columnSpan=1):
		self.add(None,text,qta.icon("fa.close",color="red",scale_factor=1),fromRow,fromColumn,rowSpan,columnSpan)
		
	def _clickBtn(self):
		self.result = self.sender().value
		self.close()
		self.clicked.emit(self.result)
	
	def _createButton(self,value,text,icon):
		btn = QToolButton()
		btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
		btn.setText(text)
		btn.setIcon(icon)
		btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)	
		btn.setCursor(Qt.PointingHandCursor)
		#p = QPalette(self.palette())
		#p.setColor(QPalette.ButtonText,  QColor("gray"))
		#self.setPalette(p)
		btn.setIconSize(QSize(self.iconSize,self.iconSize))	
		font = btn.font() 
		font.setPointSize(self.fontSize)
		btn.setFont(font)
		btn.value = value
		return btn 
		
	def getButton(self,value):
		for i in range(self.layout.count()):
			b = self.layout.itemAt(i).widget()
			if b.value == value:
				return b
		return None
			 
		
####################################################
def runTest():
	class dlg(QDialog):  
		def __init__(self):
			super(dlg, self).__init__()  
			menu = menuDlg()
			menu.add(1,"test",qta.icon("fa.edit",color="yellow",scale_factor=1),0,0,1,1) 
			menu.add(2,"test",qta.icon("fa.edit",color="blue",scale_factor=1),0,1,1,1) 
			menu.add(3,"test",qta.icon("fa.edit",color="green",scale_factor=1),0,2,1,1)  
			menu.addColseButton("关闭",0,3,1,1) 
			self.menu=menu
		
			layout = QHBoxLayout() 
			b = QPushButton("ggggggg")
			b.clicked.connect(menu.onClick)
			layout.addWidget(b)
			
			b = QPushButton("ggggggg")
			b.clicked.connect(menu.onClick)
			layout.addWidget(b)
			
			menu.clicked.connect(self.onClick)
			
			self.setLayout(layout)
			self.setWindowTitle("QT测试")	
			self.setWindowFlags(self.windowFlags()& ~Qt.WindowMaximizeButtonHint& Qt.WindowMinimizeButtonHint) 		
			self.setMinimumSize(400,400)
		
		def onClick(self,value):
			print(value,self.menu.result,self.menu.getButton(value).text())
			
	app = QApplication(sys.argv)
	d = dlg() 
	d.show() 
	sys.exit(app.exec_())		

if __name__ == '__main__':
	runTest()
