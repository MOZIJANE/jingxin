#coding=utf-8
# ycat			2019-10-16	  create
# 表格对话框 
import sys,os 
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import PyQt5.QtWidgets 
import PyQt5.QtCore
import PyQt5.QtGui

class MyQStandardItemModel(PyQt5.QtGui.QStandardItemModel):
	def __init__(self):
		PyQt5.QtGui.QStandardItemModel.__init__(self)

	def data(self, index, role=None):
		if role == PyQt5.QtCore.Qt.TextAlignmentRole:
			return PyQt5.QtCore.Qt.AlignLeft
		return PyQt5.QtGui.QStandardItemModel.data(self, index, role)

#https://blog.csdn.net/LaoYuanPython/article/details/103797461?utm_medium=distribute.pc_relevant.none-task-blog-baidujs_title-1&spm=1001.2101.3001.4242
class treeWidget(PyQt5.QtWidgets.QWidget):
	def __init__(self):
		super(treeWidget, self).__init__()
		self.model = MyQStandardItemModel()
		self.tree = PyQt5.QtWidgets.QTreeView() 
		 
		self.tree.setModel(self.model) 
		self.tree.setEditTriggers(PyQt5.QtWidgets.QAbstractItemView.NoEditTriggers)
		self.tree.setSelectionBehavior(PyQt5.QtWidgets.QAbstractItemView.SelectRows) 
		self.tree.setSelectionMode(PyQt5.QtWidgets.QAbstractItemView.SingleSelection) 
		self.tree.header().setSectionResizeMode(PyQt5.QtWidgets.QHeaderView.ResizeToContents)
		self.tree.setSortingEnabled(True)
		self.tree.header().setDefaultAlignment(PyQt5.QtCore.Qt.AlignLeft)
		#signal 
		self.doubleClicked = self.tree.doubleClicked
		
		l = PyQt5.QtWidgets.QHBoxLayout()
		l.addWidget(self.tree)  
		self.setLayout(l)  

		
	#设置表头格式 
	#type =Stretch(1),Interactive(2),ResizeToContents(3)
	def setHeaderStyle(self,type):
		if type == 1:
			self.tree.header().setSectionResizeMode(PyQt5.QtWidgets.QHeaderView.Stretch)
		elif type == 2:
			self.tree.header().setSectionResizeMode(PyQt5.QtWidgets.QHeaderView.Interactive)
		else:
			self.tree.header().setSectionResizeMode(0, PyQt5.QtWidgets.QHeaderView.ResizeToContents)
	
	@property
	def columnCount(self):
		return self.model.columnCount()
		
	@property
	def count(self):
		return self.model.rowCount()
	
	@property
	def header(self):
		return self.tree.header()
		
	def addColumn(self,*params):
		def add(text): 
			count = self.columnCount
			self.model.setHorizontalHeaderItem(count, PyQt5.QtGui.QStandardItem(text)) 
			#self.header.setSectionResizeMode(PyQt5.QtWidgets.QHeaderView.ResizeToContents)
			self.header.setOffset(-1)
		for p in params:
			add(p)
		
		
	def addRow(self,): 
		return self.update(self.model.rowCount(),*rows)
		
		
	def addNode(self,parent,text,*rows): 
		def getNodeRowIndex(item):
			r = 0
			while item:
				r += item.rowCount()
				item = item.parent()
			return r
			
			
		item = PyQt5.QtGui.QStandardItem(text)
		if rows:
			ii = [PyQt5.QtGui.QStandardItem(t) for t in rows]
			ii.insert(0,item)
			items = ii
		else:
			items = item

		if parent is None:
			self.model.appendRow(items)
		else:
			parent.appendRow(items)
			
		#item.setChild(0,PyQt5.QtGui.QStandardItem(str(rows[0])))
		#rowIndex = getNodeRowIndex(item)
		#k = self.model.index(0, 0, item.index());
		#for i,cell in enumerate(rows): 
		#	self.setItem(k,i+1,cell)
		return item
		
	def collapseAll(self):
		self.tree.collapseAll()
		
	def expandAll(self):
		self.tree.expandAll()
		
	##因为用序号删除，所以要倒着删除 
	#def remove(self,index):
	#	self.model.removeRows(index,1)
	#	
	def clear(self):
		self.model.clear()
	#	
	#@property
	#def selectIndex(self):
	#	ss = self.tree.selectedIndexes()
	#	if ss:
	#		return ss[0].row()
	#	return -1
	#	
	#@property
	#def selectRow(self):
	#	i = self.selectIndex
	#	if i == -1:
	#		return None
	#	return self.getRow(i)
	#
	#def getRow(self,index):
	#	row = []
	#	for c in range(self.model.columnCount()):
	#		row.append(self.getItemText(index,c))
	#	return row 
		
	
	#def setItemColor(self,rowIndex,cellIndex,color=None,bgColor=None):
	#	assert color or bgColor
	#	if color:
	#		self.getItem(rowIndex,cellIndex).setForeground(PyQt5.QtGui.QBrush(PyQt5.QtGui.QColor(color)))
	#	if bgColor:
	#		self.getItem(rowIndex,cellIndex).setBackground(PyQt5.QtGui.QBrush(PyQt5.QtGui.QColor(bgColor)))

		
	#def getItem(self,rowIndex,cellIndex):
	#	return self.model.item(rowIndex,cellIndex)
	#	
	#def getItemText(self,rowIndex,cellIndex):
	#	return self.model.item(rowIndex,cellIndex).text()
		 
	#def setData(self,rowIndex,cellIndex,data):
	#	self.getItem(rowIndex,cellIndex).setData(data)
	#	
	#def getData(self,rowIndex,cellIndex):
	#	return self.getItem(rowIndex,cellIndex).data()
		 
	#def sort(self,index,asc=True):
	#	if asc:
	#		order = PyQt5.QtCore.Qt.AscendingOrder
	#	else:
	#		order = PyQt5.QtCore.Qt.DescendingOrder
	#	self.tree.sortByColumn(index,order)
	
		
class treeDlg(PyQt5.QtWidgets.QDialog):	
	def __init__(self,title=""):
		super(treeDlg, self).__init__()
		self.setWindowTitle(title) 
		self.tree = treeWidget()
		
		self.setMinimumSize(600,100)
		self.setWindowFlags(PyQt5.QtCore.Qt.WindowCloseButtonHint) 		
		l = PyQt5.QtWidgets.QVBoxLayout()
		l.setSpacing(0) 
		l.setContentsMargins(0,0,0,0)
		l.addWidget(self.tree)  
		self.setLayout(l) 
		
		self.addColumn = self.tree.addColumn
		self.addNode = self.tree.addNode
		self.expandAll = self.tree.expandAll
		self.collapseAll = self.tree.collapseAll
		  
		
	
if __name__ == '__main__':
	import qtawesome as qta
	app = PyQt5.QtWidgets.QApplication(sys.argv)
	t = treeDlg()
	t.addColumn("ycat1")
	t.addColumn("ycat2")
#	t.addColumn("ycat3")
	r1 = t.addNode(None,"1","1.1")
	i = t.addNode(r1,"","2.2")
	print(i)
#	t.addRow(["a1","a2","a3"])
#	t.tree.setItemColor(1,2,"green","blue")
	t.show()
#	t.tree.sort(2)
#	t.tree.setData(1,2,"ycat")
#	assert t.tree.getData(1,2) == "ycat"
	sys.exit(app.exec_())

