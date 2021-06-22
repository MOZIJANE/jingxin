#coding=utf-8
# ycat			2017-09-05	  create
# 自动生成序列化的功能 
import sys,os
import codecs
import pickle
import uuid
import collections
import qtawesome as qta	
from PyQt5.QtCore import Qt,QEvent,QPoint
from PyQt5.QtGui import QPalette,QColor
from PyQt5.QtWidgets import (QApplication, QGridLayout, QHBoxLayout,QLayout, QLineEdit,QVBoxLayout,QFormLayout,QLabel,QComboBox,
		QSizePolicy,QTableView, QToolButton, QWidget,QTextEdit,QDialog,QPushButton,QHeaderView,QAbstractItemView)
from PyQt5.QtGui import (QStandardItemModel,QStandardItem)
		
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import ui.inputBox
import ui.numberBox
import ui.checkbox
import qtutility
import utility
from meta import *
BTN_MIN_HEIGTH = 30
DEFAULT_FONT_SIZE = 10
#默认的数据管理器  
class manager:
	def __init__(self,objType,meta):
		self.data = collections.OrderedDict()
		self.isModified = False
		self.objType = objType
		self.meta = meta
	
	def __str__(self):
		return utility.str_obj(self.data)
	
	def save(self,filename): 
		with open(filename,"wb") as f:
			pickle.dump(self.data,f)
		self.isModified = False
		
	def load(self,filename):
		#if not os.path.exists(filename):
		with open(filename,"rb") as f:
			self.data = pickle.load(f)
		self.isModified = False
	
	def new(self):
		return self.objType()
	
	def add(self,obj):
		assert isinstance(obj,self.objType)
		id = ""
		if hasattr(obj,"id"):
			id = getattr(obj,"id")
		if not id:
			id = uuid.uuid1()
			obj.id = id
		self.data[id] = obj
		self.isModified = True
		
	def delete(self,id):
		if id in self.data:
			del self.data[id]
		self.isModified = True	
		
	def update(self,id,obj):
		assert isinstance(obj,self.objType)
		obj.id = id
		self.data[id] = obj
		self.isModified = True 
		
	def isExist(self,id):
		return id in self.data
		
	def __len__(self):
		return len(self.data)
		
	def __iter__(self):
		for d in self.data:
			yield self.data[d]
			
	def checkRepeat(self,obj):
		if len(self.meta.primaryKeys) == 0:
			return
		s = []
		for d in self:
			assert d.id != ""
			if d.id == obj.id:
				continue
			s.append(self.meta._getPrimary(d))
		if self.meta._getPrimary(obj) in s:
			return self.meta.title + "已经存在"
		return None
		
class managerDlg(QDialog): 
	def __init__(self,manager,filename):
		super(managerDlg, self).__init__() 
		
		self.manager = manager
		self.filename = filename
		
		bb = self.createButtons()
		layout = QVBoxLayout()
		layout.addWidget(self.createTable()) 	
		layout.addLayout(bb)
		self.setLayout(layout)
		
		self.setWindowFlags(Qt.WindowCloseButtonHint) 		
		self.setFixedSize(500,500)
		self.setWindowTitle(manager.meta.title+"管理") 
		self.finished.connect(self.closeEvent)
		
	def createButtonLayout(self):
		h = QHBoxLayout()
		h.setSpacing(20) 
		return h 
		
	def createButtons(self): 
		buttonLayout = self.createButtonLayout()
		
		button = QPushButton(qta.icon("fa.file-o",scale_factor=1.2,color="green"),"新建")
		button.setMinimumHeight(BTN_MIN_HEIGTH) 
		qtutility.setFontSize(button,DEFAULT_FONT_SIZE)
		button.clicked.connect(self.clickNew)
		buttonLayout.addWidget(button)
		
		button = QPushButton(qta.icon("fa.edit",scale_factor=1.2,color="blue"),"编辑")
		button.setMinimumHeight(BTN_MIN_HEIGTH) 
		button.clicked.connect(self.clickEdit)
		qtutility.setFontSize(button,DEFAULT_FONT_SIZE)
		buttonLayout.addWidget(button)
		self.editBtn = button
		
		button = QPushButton(qta.icon("fa.trash-o",scale_factor=1.2,color="red"),"删除")
		button.setMinimumHeight(BTN_MIN_HEIGTH) 
		button.clicked.connect(self.clickDel)
		qtutility.setFontSize(button,DEFAULT_FONT_SIZE)
		buttonLayout.addWidget(button) 
		self.delBtn = button
		
		button = QPushButton(qta.icon("fa.close",scale_factor=1.2,color="black"),"关闭")
		button.setMinimumHeight(BTN_MIN_HEIGTH)
		qtutility.setFontSize(button,DEFAULT_FONT_SIZE)
		button.clicked.connect(self.reject)
		buttonLayout.addWidget(button)
		self.editBtn.setEnabled(False)
		self.delBtn.setEnabled(False) 
		return buttonLayout
		
	def createTable(self):
		self.table = QTableView()	
		self.reload()
		self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.table.setSelectionBehavior(QAbstractItemView.SelectRows) 
		self.table.setSelectionMode(QAbstractItemView.SingleSelection) 
		self.table.setColumnWidth(1,150)
		 
		self.table.verticalHeader().hide()     
		self.table.clicked.connect(self.itemSelectChange)
		self.table.doubleClicked.connect(self.clickEdit)
		return self.table
		
	def reload(self):
		self.model = QStandardItemModel()
		self.model.clear()
		i = 0
		for item in self.manager.meta: 
			if isinstance(item,str):
				continue
			self.model.setHorizontalHeaderItem(i, QStandardItem(item.name)) 
			i+=1
		for i,info in enumerate(self.manager): 
			h = 0
			for m in self.manager.meta:
				if isinstance(m,str):
					continue
				item = QStandardItem(m.valueStr(info))
				if h == 0:
					item.setData(info)
				self.model.setItem(i, h, item)
				h+=1
		self.table.setModel(self.model)
		self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)		
  
	def data(self):
		i = self.table.currentIndex()
		if i is None or i.row() == -1: 
			return None 
		return self.model.item(i.row(),0).data()
	
	def clickEdit(self):
		obj = self.data()
		if obj is None:
			return 
		dlg = editDlg(self.manager.new(),self.manager.meta,manager=self.manager)
		dlg.setValue(obj)
		if dlg.exec_() == dlg.Accepted:
			self.manager.update(obj.id,dlg.getObj())
			self.manager.save(self.filename)
			self.reload()
	
	def clickNew(self): 
		dlg = editDlg(self.manager.new(),self.manager.meta,manager=self.manager)
		if dlg.exec_() == dlg.Accepted:
			self.manager.add(dlg.getObj())
			self.manager.save(self.filename)
			self.reload()
			
	def clickDel(self):
		obj = self.data()
		if obj is None:
			return
		self.manager.delete(obj.id)
		self.manager.save(self.filename)
		self.reload()
	
	def itemSelectChange(self):
		if self.data() is None:
			self.editBtn.setEnabled(False)
			self.delBtn.setEnabled(False) 
		else:
			self.editBtn.setEnabled(True)
			self.delBtn.setEnabled(True) 
	#QCloseEvent 
	def closeEvent(self,event): 
		self.table.setModel(None)
	
	
if __name__ == '__main__': 
	class testData:
		def __init__(self):
			self.aaa = 1000
			self.bbb = "hello world"
			self.ccc = "11"
			self.ddd = 0.0
			self.eee = 1
		
		def meta(self):
			m = metaData(testData,"测试对话框")
			m.addInt("字段1","aaa")
			m.addText("字段2","bbb")
			#m.addNewLine()
			m.addPwd("字段3","ccc")
			m.addFloat("字段4","ddd")
			m.addSelect("字段5","eee",[(0,"item0"),(1,"item1"),(2,"item2"),(4,"item4")])
			m.setPrimary("aaa")
			return m
			
	app = QApplication(sys.argv)
	data = testData()
	m = manager(testData,data.meta())
	for i in range(10):
		t = testData()
		t.aaa = 1000+i
		m.add(t)
	m.add(testData())
	d = managerDlg(m,"test/testmanger.txt")  
	sys.exit(d.exec_())
	
	
	
	
	
	
	