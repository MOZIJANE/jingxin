import sys,os
import PyQt5
import PyQt5.QtWidgets 
import PyQt5.QtCore
import PyQt5.QtGui
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import qtawesome as qta
import ui.treeDlg
import qtutility
		
class confUI(PyQt5.QtWidgets.QWidget):
	def __init__(self):
		super(confUI, self).__init__()  
		self.tree = ui.treeDlg.treeWidget()
		self.tree.tree.setSortingEnabled(False)
		self.tree.addColumn("key")
		self.tree.addColumn("value")
		qtutility.setFontSize(self.tree,11)
		layout = PyQt5.QtWidgets.QVBoxLayout()
		layout.addWidget(self.tree)
		self.setLayout(layout)
	
	def setData(self,dictVal):
		self.tree.clear()
		self.tree.addColumn("key")
		self.tree.addColumn("value")
		for k in dictVal:
			parent = self.tree.addNode(parent=None,text=k)
			parent.setIcon(qta.icon('fa.cogs'))
			s =  dictVal[k]
			if isinstance(s,dict):
				for v in s:
					self.tree.addNode(parent,v,str(s[v]))
			else:
				self.tree.addNode(parent,"",str(s))
		
		
	def expandAll(self):
		self.tree.expandAll()
		
		
class confDlg(PyQt5.QtWidgets.QDialog): 
		def __init__(self):
			super(confDlg, self).__init__() 
			layout = PyQt5.QtWidgets.QHBoxLayout()
			layout.setSpacing(0) 
			layout.setContentsMargins(0,0,0,0)
		
			self.conf = confUI()
			layout.addWidget(self.conf) 
			self.setLayout(layout)
			self.setWindowTitle("查看配置")	 	
			self.setMinimumSize(400,600)
			self.setWindowFlags(PyQt5.QtCore.Qt.WindowCloseButtonHint) 		
			self.setWindowIcon(qta.icon('fa.list'))
			self.expandAll = self.conf.expandAll
			
		def setData(self,dict):
			return self.conf.setData(dict)
			

################## unit test ##################

if __name__ == '__main__': 
	import config
	app = PyQt5.QtWidgets.QApplication(sys.argv)
	d = confDlg() 
	d.setData(config.getData())
	d.expandAll()
	d.show() 
	sys.exit(app.exec_())

	
	
	
	
	
	
	
	
	
	