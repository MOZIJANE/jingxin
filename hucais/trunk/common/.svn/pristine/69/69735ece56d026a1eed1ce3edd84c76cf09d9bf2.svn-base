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
			return PyQt5.QtCore.Qt.AlignCenter
		return PyQt5.QtGui.QStandardItemModel.data(self, index, role)


#https://blog.csdn.net/jia666666/article/details/81627589 
class tableWidget(PyQt5.QtWidgets.QWidget):
	def __init__(self):
		super(tableWidget, self).__init__()
		# self.model = PyQt5.QtGui.QStandardItemModel()
		self.model = MyQStandardItemModel()
		self.table = PyQt5.QtWidgets.QTableView() 
		self.table.setModel(self.model) 
		self.table.setEditTriggers(PyQt5.QtWidgets.QAbstractItemView.NoEditTriggers)
		self.table.setSelectionBehavior(PyQt5.QtWidgets.QAbstractItemView.SelectRows) 
		self.table.setSelectionMode(PyQt5.QtWidgets.QAbstractItemView.SingleSelection) 
		#self.header.setStretchLastSection(True)
		self.header.setSectionResizeMode(PyQt5.QtWidgets.QHeaderView.ResizeToContents)
		self.table.setShowGrid(True)
		self.table.setSortingEnabled(True)
		
		# s = "QHeaderView::section {""color: black;padding-left: 4px;border: 1px solid #6c6c6c;}"
		s = "QHeaderView::section {""padding-left: 4px;}"
		# self.header.setStyleSheet(s)
		self.table.verticalHeader().setStyleSheet(s)
		self.table.horizontalHeader().setSectionResizeMode(PyQt5.QtWidgets.QHeaderView.Stretch)

		#signal 
		self.doubleClicked = self.table.doubleClicked
		
		l = PyQt5.QtWidgets.QHBoxLayout()
		l.addWidget(self.table)  
		self.setLayout(l)  
		
	#设置表头格式 
	#type =Stretch(1),Interactive(2),ResizeToContents(3)
	def setHeaderStyle(self,type):
		if type == 1:
			self.table.horizontalHeader().setSectionResizeMode(PyQt5.QtWidgets.QHeaderView.Stretch)
		elif type == 2:
			self.table.horizontalHeader().setSectionResizeMode(PyQt5.QtWidgets.QHeaderView.Interactive)
		else:
			self.table.horizontalHeader().setSectionResizeMode(0, PyQt5.QtWidgets.QHeaderView.ResizeToContents)
	
	@property
	def columnCount(self):
		return self.model.columnCount()
		
	@property
	def count(self):
		return self.model.rowCount()
	
	@property
	def header(self):
		return self.table.horizontalHeader()
		
	def addColumn(self,*params):
		def add(text): 
			count = self.columnCount
			self.model.setHorizontalHeaderItem(count, PyQt5.QtGui.QStandardItem(text)) 
			#self.header.setSectionResizeMode(PyQt5.QtWidgets.QHeaderView.ResizeToContents)
			self.header.setOffset(-1)
		for p in params:
			add(p)
		
	def addRow(self,*rows): 
		return self.update(self.model.rowCount(),*rows)
		
	def update(self,index,*rows): 
		if len(rows) == 1:
			row = rows[0]
		else:
			row = rows 
		if isinstance(row,(tuple,list)):
			for i,cell in enumerate(row): 
				self.setItem(index,i,cell)
		else:
			self.setItem(index,0,row)
		return index
		
	def setItem(self,rowIndex,cellIndex,item):
		if isinstance(item,PyQt5.QtWidgets.QWidget):
			self.model.setCellWidget(rowIndex,cellIndex,item)
		else:
			self.model.setItem(rowIndex,cellIndex,PyQt5.QtGui.QStandardItem(str(item)))
		
		
	#因为用序号删除，所以要倒着删除 
	def remove(self,index):
		self.model.removeRows(index,1)
		
	def clear(self):
		self.model.clear()
		
	@property
	def selectIndex(self):
		ss = self.table.selectedIndexes()
		if ss:
			return ss[0].row()
		return -1
		
	@property
	def selectRow(self):
		i = self.selectIndex
		if i == -1:
			return None
		return self.getRow(i)
	
	def getRow(self,index):
		row = []
		for c in range(self.model.columnCount()):
			row.append(self.getItemText(index,c))
		return row 
		
	
	def setItemColor(self,rowIndex,cellIndex,color=None,bgColor=None):
		assert color or bgColor
		if color:
			self.getItem(rowIndex,cellIndex).setForeground(PyQt5.QtGui.QBrush(PyQt5.QtGui.QColor(color)))
		if bgColor:
			self.getItem(rowIndex,cellIndex).setBackground(PyQt5.QtGui.QBrush(PyQt5.QtGui.QColor(bgColor)))
		 
	def setIcon(self,rowIndex,cellIndex,icon):
		self.getItem(rowIndex,cellIndex).setIcon(icon)
		
	def getItem(self,rowIndex,cellIndex):
		return self.model.item(rowIndex,cellIndex)
		
	def getItemText(self,rowIndex,cellIndex):
		return self.model.item(rowIndex,cellIndex).text()
		 
	def setData(self,rowIndex,cellIndex,data):
		self.getItem(rowIndex,cellIndex).setData(data)
		
	def getData(self,rowIndex,cellIndex):
		return self.getItem(rowIndex,cellIndex).data()
		 
	def sort(self,index,asc=True):
		if asc:
			order = PyQt5.QtCore.Qt.AscendingOrder
		else:
			order = PyQt5.QtCore.Qt.DescendingOrder
		self.table.sortByColumn(index,order)
	
		
class tableDlg(PyQt5.QtWidgets.QDialog):	
	def __init__(self,title=""):
		super(tableDlg, self).__init__()
		self.setWindowTitle(title) 
		self.table = tableWidget()
		
		self.setMinimumSize(600,100)
		self.setWindowFlags(PyQt5.QtCore.Qt.WindowCloseButtonHint) 		
		l = PyQt5.QtWidgets.QVBoxLayout()
		l.setSpacing(0) 
		l.setContentsMargins(0,0,0,0)
		l.addWidget(self.table)  
		self.setLayout(l) 
		
		self.addColumn = self.table.addColumn
		self.addRow = self.table.addRow
		self.clear = self.table.clear
		  
		
	
if __name__ == '__main__':
	import qtawesome as qta
	app = PyQt5.QtWidgets.QApplication(sys.argv)
	t = tableDlg()
	t.addColumn("ycat1")
	t.addColumn("ycat2")
	t.addColumn("ycat3")
	t.addRow(["1","2","3"])
	t.addRow(["a1","a2","a3"])
	t.table.setItemColor(1,2,"green","blue")
	t.show()
	t.table.sort(2)
	t.table.setIcon(1,2,qta.icon("fa.copy",color="red"))
	t.table.setData(1,2,"ycat")
	assert t.table.getData(1,2) == "ycat"
	sys.exit(app.exec_())

