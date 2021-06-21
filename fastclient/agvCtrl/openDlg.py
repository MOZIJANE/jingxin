#coding=utf-8 
# ycat			2019-11-03	  create
import os,sys
import math
import PyQt5  
import qtawesome as qta
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)  
import utility
import local
import ui.tableDlg
import mapMgr 


class openDlg(PyQt5.QtWidgets.QDialog):	
	def __init__(self):
		super(openDlg, self).__init__()
		self.setWindowIcon( qta.icon("fa.map-o",color='blue'))
		self.setWindowTitle("选择地图文件") 
		self.table = ui.tableDlg.tableWidget()
		self.table.doubleClicked.connect(self.doubleClicked)
		
		self.setMinimumSize(600,400)
		self.setWindowFlags(PyQt5.QtCore.Qt.WindowCloseButtonHint) 		
		l = PyQt5.QtWidgets.QVBoxLayout()
		#l.setSpacing(10) 
		l.addWidget(self.table)  
		l.addLayout(self.createBtns())
		self.setLayout(l) 
		
		mm = mapMgr.getMapList()
		self.table.addColumn("ID","名称")
		for m in mm:
			self.table.addRow((m["id"],m["name"]))
		self.mapId = None
		
	def doubleClicked(self,index):
		self.accept()
	
	def createButtonLayout(self):
		l2 = PyQt5.QtWidgets.QHBoxLayout()
		l2.addStretch(1) 
		l2.setSpacing(20)
		return l2
		
	def createBtns(self):
		l2 = self.createButtonLayout()
		b = PyQt5.QtWidgets.QPushButton(qta.icon("fa.check",scale_factor=1.5,color="green"),"确定")
		b.setMinimumHeight(40)
		b.clicked.connect(self.accept)
		b.setFixedWidth(80)
		self.okBtn = b
		l2.addWidget(b) 
		
		b = PyQt5.QtWidgets.QPushButton(qta.icon("fa.remove",scale_factor=1.5,color="red"),"取消")
		b.setMinimumHeight(40)
		b.clicked.connect(self.reject)
		b.setFixedWidth(80)
		l2.addWidget(b)
		return l2 
		
	def accept(self):
		row = self.table.selectRow
		if row:
			self.mapId = row[0] 
		super(openDlg, self).accept()
		
		
if __name__ == '__main__':
	app = PyQt5.QtWidgets.QApplication(sys.argv)
	t = openDlg()
	t.show()
	sys.exit(app.exec_())










	
