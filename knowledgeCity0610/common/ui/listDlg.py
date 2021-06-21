#coding=utf-8 
# ycat			2017-08-11	  create
# 列表显示 
import os,sys
import qtawesome as qta

import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import PyQt5
from PyQt5.QtCore import Qt,QEvent,QPoint,QSize
from PyQt5.QtGui import QPalette,QColor
from PyQt5.QtWidgets import QApplication, QListWidgetItem,QDialog,QListWidget,QVBoxLayout, QPushButton,QListView
import ui.popDlg
import enhance

class listWidget(PyQt5.QtWidgets.QWidget):
	def __init__(self):
		super(listWidget, self).__init__()
		self.list = QListWidget()
		#TODO：未完成 
		#self.list.setCursor(Qt.PointingHandCursor)
		#self.list.itemClicked.connect(self._itemClicked) 
		#self.list.verticalScrollBar().setStyleSheet("QScrollBar{width:18px;}")
		#self.list.horizontalScrollBar().setStyleSheet("QScrollBar{height:18px;}")
		self.layout = QVBoxLayout()
		self.layout.addWidget(self.list)
		self.setLayout(self.layout)
		
	def addColumn(self):
		pass
		
	def addRow(self,*params):
		pass
	
	
	

#用法:
#注册clicked事件，取出点的button的值 
#menu.clicked.connect(self.onClick)
#def onClick(self,value):
#	print(value,menu.result)
class listDlg(ui.popDlg.popDlg): 
	def __init__(self, fontSize=10,isIconMode = False,iconSize=48,parent=None):
		super(listDlg, self).__init__(isTransparent=False,parent=None)
		self.iconSize = iconSize
		self.fontSize = fontSize 
		
		self.list = QListWidget()
		self.list.setCursor(Qt.PointingHandCursor)
		self.list.itemClicked.connect(self._itemClicked) 
		self.list.verticalScrollBar().setStyleSheet("QScrollBar{width:18px;}")
		self.list.horizontalScrollBar().setStyleSheet("QScrollBar{height:18px;}")
		if isIconMode:
			self.list.setViewMode(QListView.IconMode)
			self.list.setMovement(QListView.Static)
			self.list.setIconSize(QSize(iconSize,iconSize))
		
		self.layout = QVBoxLayout()
		self.layout.addWidget(self.list)
		self.setLayout(self.layout)
				
		self.result = None
		self.selected = enhance.event()
	
	def clear(self):
		self.list.clear()
	
	def add(self,value,text,icon):
		i = QListWidgetItem(text) 
		if icon:
			i.setIcon(icon)
		i.value = value 
		font = i.font() 
		font.setPointSize(self.fontSize)
		i.setFont(font)
		self.list.addItem(i)
		return i
		
	def selectItem(self,value):
		for i in range(self.list.count()):
			if self.list.item(i).value == value:
				self.list.scrollToItem(self.list.item(i))
				self.list.setCurrentItem(self.list.item(i))
				break
	
	#QListWidgetItem  
	def _itemClicked(self,item):  
		self.result = item.value 
		self.close()
		self.selected.emit(self.result)
	
 
####################################################
def runTest():
	class dlg(QDialog):  
		def __init__(self):
			super(dlg, self).__init__()  
			list = listDlg(isIconMode=True,fontSize=30)
			self.list = list
			for i in range(100):
				list.add(1,"test",qta.icon("fa.edit",color="green"))
			list.add(2,"test",qta.icon("fa.edit",color="green"))
			list.add(3,"test",qta.icon("fa.edit",color="green"))
			list.add(4,"test",qta.icon("fa.edit",color="green"))
			list.selectItem(4)
		
			layout = QVBoxLayout() 
			b = QPushButton("ggggggg")
			b.clicked.connect(list.onClick)
			layout.addWidget(b)
			
			b = QPushButton("ggggggg")
			b.clicked.connect(list.onClick)
			layout.addWidget(b)
			
			aa = listWidget()
			layout.addWidget(aa)
			
			list.selected.connect(self.onClick)
			
			self.setLayout(layout)
			self.setWindowTitle("QT测试")	
			self.setWindowFlags(self.windowFlags()& ~Qt.WindowMaximizeButtonHint& Qt.WindowMinimizeButtonHint) 		
			self.setMinimumSize(400,400)
		
		def onClick(self,value):
			print(value,self.list.result)
			
	app = QApplication(sys.argv)
	d = dlg() 
	d.show() 
	sys.exit(app.exec_())		

if __name__ == '__main__':
	runTest()
