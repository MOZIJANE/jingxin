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
		self.list.itemClicked.connect(self._itemClicked) 
		#self.list.verticalScrollBar().setStyleSheet("QScrollBar{width:18px;}")
		#self.list.horizontalScrollBar().setStyleSheet("QScrollBar{height:18px;}")
		self.layout = QVBoxLayout()
		self.layout.addWidget(self.list)
		self.setLayout(self.layout)
		
	def clear(self):
		self.list.clear()
		
	def addItem(self,name,checkable=False,checked=False,icon=None):
		item = QListWidgetItem()
		item.checkable = checkable
		item.setData(Qt.DisplayRole, name)
		if checkable:
			if checked:
				item.setData(Qt.CheckStateRole, Qt.Checked)
			else:
				item.setData(Qt.CheckStateRole, Qt.Unchecked)
		if icon is not None:
			item.setIcon(icon) 
		self.list.addItem(item)
		return item
		
	#QListWidgetItem  
	def _itemClicked(self,item):  
		if not item.checkable:
			return
		if item.checkState() == Qt.Checked:
			item.setCheckState(Qt.Unchecked)
		else:
			item.setCheckState(Qt.Checked)
		
	#返回所有check的item名字列表 
	def getCheckItemLabels(self):
		rr = []
		for i in range(self.list.count()):
			item = self.list.item(i)
			if item.checkState() == Qt.Checked:
				rr.append(item.text())
		return rr
		
	def setCheckByLabel(self,label):
		for i in range(self.list.count()):
			if self.list.item(i).text() == label:
				self.list.item(i).setCheckState(Qt.Checked)
		
		
class listDlg(PyQt5.QtWidgets.QDialog):	
	def __init__(self,title=""):
		super(listDlg, self).__init__()
		self.setWindowTitle(title) 
		self.setWindowIcon(qta.icon("fa.list"))
		
		self.list = listWidget()
		
		self.setMinimumSize(80,100)
		self.setWindowFlags(PyQt5.QtCore.Qt.WindowCloseButtonHint) 		
		l = PyQt5.QtWidgets.QVBoxLayout()
		l.setSpacing(0) 
		l.setContentsMargins(0,0,0,0)
		l.addWidget(self.list)  
		self.setLayout(l) 
		
		self.addItem = self.list.addItem
		self.clear = self.list.clear	
		self.setCheckByLabel = self.list.setCheckByLabel
		self.getCheckItemLabels = self.list.getCheckItemLabels
		
		l2 = PyQt5.QtWidgets.QHBoxLayout()
		b = QPushButton(qta.icon("fa.check",scale_factor=1.5,color="green"),"确定")
		b.setMinimumHeight(30)
		b.clicked.connect(self.accept)
		b.setFixedWidth(80)
		self.okBtn = b
		l2.addWidget(b) 
		
		b = QPushButton(qta.icon("fa.remove",scale_factor=1.5,color="red"),"取消")
		b.setMinimumHeight(30)
		b.clicked.connect(self.reject)
		b.setFixedWidth(80)
		l2.addWidget(b)
		l.addLayout(l2)
	
	

#用法:
#注册clicked事件，取出点的button的值 
#menu.clicked.connect(self.onClick)
#def onClick(self,value):
#	print(value,menu.result)
class listPopDlg(ui.popDlg.popDlg): 
	def __init__(self, fontSize=10,isIconMode = False,iconSize=48,parent=None):
		super(listPopDlg, self).__init__(isTransparent=False,parent=None)
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
def testlistPopDlg():
	class dlg(QDialog):  
		def __init__(self):
			super(dlg, self).__init__()  
			list = listPopDlg(isIconMode=False,fontSize=10)
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

def testlist1():
	app = PyQt5.QtWidgets.QApplication(sys.argv)
	class dlg(PyQt5.QtWidgets.QDialog): 
		def __init__(self):
			super(dlg, self).__init__() 
			layout = PyQt5.QtWidgets.QHBoxLayout()
			nn = listWidget() 
			nn.addItem("ycat1",True)
			layout.addWidget(nn)
			self.setLayout(layout)
			self.setWindowTitle("QT测试")	 	
			self.setMinimumSize(400,400)
			 
	d = dlg() 
	d.show() 
	sys.exit(app.exec_())


def testlistDlg():
	app = QApplication(sys.argv)
	d = listDlg() 
	d.addItem("ycat",checkable=True)
	d.list.getCheckItemLabels()
	d.show() 
	sys.exit(app.exec_())	
	

if __name__ == '__main__':
	#testlist1()
	#testlistPopDlg()
	testlistDlg()









