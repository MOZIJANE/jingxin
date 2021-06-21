#coding=utf-8
# ycat			2017-09-05	  create
# 界面元数据管理器 
import sys,os
import uuid
import collections
import qtawesome as qta	
import PyQt5
from PyQt5.QtCore import Qt,QEvent,QPoint
from PyQt5.QtGui import QPalette,QColor
from PyQt5.QtWidgets import (QApplication, QGridLayout, QHBoxLayout,QLayout, QLineEdit,QVBoxLayout,QFormLayout,QLabel,QCheckBox,QComboBox,
		QSizePolicy,QTableView, QToolButton, QWidget,QTextEdit,QDialog,QPushButton,QHeaderView,QAbstractItemView)
from PyQt5.QtGui import (QStandardItemModel,QStandardItem)
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import log
import ui.inputBox
import ui.numberBox
import ui.checkbox
import qtutility
import utility
import enhance
import json_codec as json
DEFAULT_CODEC = "utf-8"		

g_modified_marker = "<font color = red>*</font>"

def _setModified(label):
	t = label.text()
	if len(t) <= len(g_modified_marker) or t[0:len(g_modified_marker)] != g_modified_marker:
		label.setText(g_modified_marker+label.text())
				
def _clearModified(label):
	t = label.text()
	if len(t) > len(g_modified_marker) and t[0:len(g_modified_marker)] == g_modified_marker:
		label.setText(label.text()[len(g_modified_marker):])
		 
def scramble(s):
	if len(s):
		return utility.md5("ycat"+s) 
	else:
		return s

class pwdCtrl(PyQt5.QtWidgets.QLineEdit):	 
	def __init__(self):
		super(pwdCtrl, self).__init__() 
		self.setEchoMode(QLineEdit.Password)
	
	#QMouseEvent
	def mousePressEvent(self,event):
		self.setText("")
		super(pwdCtrl, self).mousePressEvent(event) 
			

class metaItem:
	#name为中文名
	#fieldName为英文名
	#ctrl为具体实现控件类型
	#valueType数据类型 
	#defaultValue为默认数据
	def __init__(self,name,fieldName,ctrl,valueType,defaultValue=None):
		self.name = name
		self.fieldName = fieldName
		self.ctrlClass = ctrl
		self.valueType = valueType 
		self.readonly = False
		self._defaultValue = defaultValue
		self.tooltip = ""
		self.isCheckble=False
		#numberbox
		self.min = None
		self.max = None
		
		#select
		self.items = []	
		
		#textBox
		self.maxSize = None
		self.minSize = None
		
		#float
		self.precision = None
		
		#password
		self.scrambleFunc = None
	
		
	def saveData(self):
		r = {}
		r["name"] = self.name
		r["fieldName"] = self.fieldName
		r["ctrlClass"] = enhance.typeName(self.ctrlClass)
		r["valueType"] = self.valueType
		r["tooltip"] = self.tooltip
		if self.isCheckble:
			r["isCheckble"] = str(self.isCheckble)
		if self.readonly:
			r["readonly"] = str(self.readonly)
		if self._defaultValue is not None:
			r["defaultValue"] = str(self.defaultValue)
		if self.min is not None:
			r["min"] = self.min
		if self.max is not None:
			r["max"] = self.max
		if self.items:
			r["items"] = self.items
		if self.maxSize is not None:
			r["maxSize"] = self.maxSize
		if self.minSize is not None:
			r["minSize"] = self.minSize
		if self.precision is not None:
			r["precision"] = self.precision
		if self.scrambleFunc is not None:
			r["scrambleFunc"] = enhance.typeName(self.scrambleFunc)
		return r
	
	@staticmethod
	def loadData(data):
		c = enhance.getType(data["ctrlClass"])
		m = metaItem(name=data["name"],fieldName=data["fieldName"],ctrl=c,valueType=data["valueType"],defaultValue=None)
		if "tooltip" in data:
			m.tooltip = data["tooltip"]
		if "readonly" in data:
			m.readonly = bool(data["readonly"])
		if "defaultValue" in data:
			m.defaultValue = data["defaultValue"]
			m.defaultValue = m.value(data["defaultValue"])
		if "min" in data:
			m.min = data["min"]
		if "max" in data:
			m.max = data["max"]
		if "items" in data:
			m.items = data["items"]
		if "maxSize" in data:
			m.maxSize = data["maxSize"]		
		if "minSize" in data:
			m.maxSize = data["minSize"]	
		if "precision" in data:
			m.maxSize = data["precision"]	
		if "scrambleFunc" in data:
			m.scrambleFunc = enhance.getType(data["scrambleFunc"])
		if "isCheckble" in data:
			m.isCheckble = bool(data["isCheckble"])
		return m 
	
	def addCtrl(self,formLayout,editable):
		if editable:
			c1 = self.getCtrl()
			label = self.getLabel(self.name,editable)
			formLayout.addRow(label,c1)
			if self.valueType == "pwd": #and newDlg:
				c2 = self.getCtrl()
				label2 = self.getLabel(self.name.strip()+"确认")
				formLayout.addRow(label2,c2)
				return (c1,c2),(label.findChild(QLabel, 'mainLabel'),label2.findChild(QLabel, 'mainLabel')),(label.findChild(QCheckBox, 'mainCheckBox'),label2.findChild(QCheckBox, 'mainCheckBox'))
			else:
				return c1,label.findChild(QLabel, 'mainLabel'),label.findChild(QCheckBox, 'mainCheckBox')
		else:
			c = QLineEdit()
			c.setReadOnly(True)
			if self.tooltip:
				c.setToolTip(self.tooltip)
			font = c.font()
			font.setPointSize(self.meta.fontSize)
			qtutility.setBackgroupColor(c,"lightgray")
			c.setFont(font) 
			label = self.getLabel(self.name,editable)
			formLayout.addRow(label,c)
			return c,label.findChild(QLabel, 'mainLabel'),label.findChild(QCheckBox, 'mainCheckBox')
	
	def getLabel(self,text,editable=False):
		if not text.endswith(":"):
			text = text +":"
		c = QLabel(text)
		font = c.font()
		font.setPointSize(self.meta.fontSize)
		c.setFont(font)
		if self.tooltip:
			c.setToolTip(self.tooltip)
		w= QWidget()
		l=QHBoxLayout()
		l.setContentsMargins(0,0,0,0)
		c.setObjectName('mainLabel')
		cb= QCheckBox()
		cb.setObjectName('mainCheckBox')
		cb.setEnabled(editable)
		if self.isCheckble:
			l.addWidget(cb)
		l.addWidget(c)
		w.setLayout(l)
		return w
		
	@property
	def defaultValue(self):
		if self._defaultValue is not None:
			return self._defaultValue
		if self.valueType == "int" or self.valueType == "float":
			return 0
		if self.valueType == "bool":
			return False
		return ""
	
	@defaultValue.setter
	def defaultValue(self,v):
		self._defaultValue = v
	
	def getCtrl(self):
		c = self.ctrlClass()
		font = c.font()
		font.setPointSize(self.meta.fontSize)
		c.setFont(font) 
		if self.tooltip:
			c.setToolTip(self.tooltip)
		if self.valueType == "int":
			if self.min is not None:
				c.setMinimum(self.min)
			else:
				c.setMinimum(-9999)
			if self.max is not None:
				c.setMaximum(self.max)
			else:
				c.setMaximum(9999)
		elif self.valueType == "float":
			if self.min is not None:
				c.setMinimum(self.min)
			else:
				c.setMinimum(-9999)
			if self.max is not None:
				c.setMaximum(self.max)
			else:
				c.setMaximum(9999)
			if self.precision is not None:
				c.setDecimals(self.precision)
		elif self.valueType == "select" or self.valueType == "bool":
			for i in self.items:
				c.addItem(i[1],i[0])
		elif self.valueType == "str":
			# c.setReadOnly(self.readonly)
			if self.maxSize:
				c.setMaxLength(self.maxSize)
		c.setEnabled(not self.readonly)
		return c
	 
	def value(self,obj):
		#if obj == "None":
		#	return None
		if isinstance(obj,QWidget):
			v = qtutility.getValue(obj)
		else:
			v = utility.get_attr(obj,self.fieldName)
			
		if v is None:
			v = self.defaultValue
		if self.valueType == "int":
			if v == "":
				return self.defaultValue
			return int(v)
		elif self.valueType == "float":
			if v == "":
				return self.defaultValue
			return float(v)
		elif self.valueType == "bool":
			return bool(v)
		elif self.valueType == "pwd":
			if len(v) < 15:
				#说明是原始密码 
				return self.scrambleFunc(v)
			else:
				return v
		else:
			return v
			
	def valueStr(self,obj):
		v = self.value(obj)
		if self.valueType == "float": 
			p = 2
			if self.precision is not None:
				p = self.precision
			return ("%0."+str(p)+"f")%v
		elif self.valueType == "pwd":
			return "●"*len(v)
		elif self.valueType == "select" or self.valueType == "bool":
			for i in self.items:
				if i[0] == v:
					return str(i[1])
		return str(v)
	
	def setValue(self,obj,v):
		utility.set_attr(obj,self.fieldName,v)
		
	def check(self,ctrls):
		if self.valueType == "pwd":
			if isinstance(ctrls,tuple):
				if qtutility.getValue(ctrls[0]) != qtutility.getValue(ctrls[1]):
					return self.name+"不同相"
		if self.valueType == "str" or self.valueType == "pwd":
			if isinstance(ctrls,tuple):
				v = qtutility.getValue(ctrls[0])
			else:
				v = qtutility.getValue(ctrls)
			if v == "":
				return self.name+"不能为空"
		return None	
	
			
class metaData: 
	def __init__(self,objType,title,iconName=""):
		if isinstance(objType,str):
			objType = enhance.getType(objType)
		self.objType = objType
		self.fields = collections.OrderedDict()
		self.title = title
		self.iconName = iconName
		self.primaryKeys = set()
		self.fontSize = 10
		self.attributes = {}	#特殊的属性，比如对话框的大小等 
	
	def setPrimary(self,name,*param):
		self.primaryKeys.clear()
		self.primaryKeys.add(name)
		assert name in self.fields
		for p in param:
			assert p in self.fields
			self.primaryKeys.add(p)
	
	def _getPrimary(self,obj):
		r = ""
		for k in self.primaryKeys:
			v = self.fields[k].value(obj)
			r += str(v) + "@@"
		return r
	 
	def addText(self,name,fieldName,ctrl=PyQt5.QtWidgets.QLineEdit,
					readonly=False,isCheckble=False,maxSize=None):
		assert fieldName not in self.fields
		m = metaItem(name,fieldName,ctrl,"str")
		m.readonly = readonly
		m.isCheckble = isCheckble
		m.maxSize = maxSize
		m.meta = self
		self.fields[fieldName] = m
		return m

	def addPwd(self,name,fieldName,ctrl=pwdCtrl,scrambleFunc = scramble):
		import ui.meta
		if ctrl == pwdCtrl:
			ctrl = ui.meta.pwdCtrl
		if scrambleFunc == scramble:
			scrambleFunc = ui.meta.scramble
		assert fieldName not in self.fields
		m = metaItem(name,fieldName,ctrl,"pwd")
		m.scrambleFunc = scrambleFunc
		m.meta = self
		self.fields[fieldName] = m
		return m
		
	def addInt(self,name,fieldName,ctrl=PyQt5.QtWidgets.QSpinBox,min = None, max = None,readonly=False,isCheckble=False):
		assert fieldName not in self.fields
		m = metaItem(name,fieldName,ctrl,"int")
		m.readonly = readonly
		m.isCheckble = isCheckble
		m.min = min
		m.max = max
		m.meta = self
		self.fields[fieldName] = m
		return m
		
	def addBool(self,name,fieldName,falseText="",trueText="",readonly=False,isCheckble=False):
		assert fieldName not in self.fields
		ctrl = PyQt5.QtWidgets.QComboBox
		m = metaItem(name,fieldName,ctrl,"bool")
		m.readonly = readonly
		m.isCheckble = isCheckble
		m.items = [(False,falseText),(True,trueText)]
		m.meta = self
		self.fields[fieldName] = m
		return m
		
	def addFloat(self,name,fieldName,precision=2,ctrl=PyQt5.QtWidgets.QDoubleSpinBox,min = None, max = None,readonly=False,isCheckble=False):
		assert fieldName not in self.fields
		m = metaItem(name,fieldName,ctrl,"float")
		m.precision = precision
		m.readonly = readonly
		m.isCheckble = isCheckble
		m.min = min
		m.max = max
		m.meta = self
		self.fields[fieldName] = m
		return m
		
	#values为[(1,"xxx1"),(2,"xxx2")]的列表 
	def addSelect(self,name,fieldName,items,ctrl=PyQt5.QtWidgets.QComboBox,readonly=False,isCheckble=False):
		assert fieldName not in self.fields
		m = metaItem(name,fieldName,ctrl,"select")
		m.readonly = readonly
		m.isCheckble = isCheckble
		m.items = items
		self.fields[fieldName] = m
		m.meta = self
		return m
 		
	def addNewLine(self):
		self.fields[uuid.uuid1()] = "newLine"
	
	def addSpace(self):
		self.fields[uuid.uuid1()] = "space"
		
	def addGroup(self,name):
		self.fields[uuid.uuid1()] = name
		
	def __len__(self):
		return len(self.fields)
		
	def __iter__(self):
		for item in self.fields:
			yield self.fields[item]
			
	def clearModified(self):
		for f in self:
			if not isinstance(f,str):
				f.isModified = False
	
	def save(self,fileName):
		ff = []
		for f in self.fields:
			f = self.fields[f]
			if isinstance(f,str): #newline,space 
				ff.append(f)
			else:
				ff.append(f.saveData())
		r = {}
		r["title"] = self.title
		r["iconName"] = self.iconName
		r["fields"] = ff
		r["primaryKeys"] = list(self.primaryKeys)
		r["objType"] = enhance.typeName(self.objType)
		r["fontSize"] = self.fontSize
		if self.attributes:
			r["attributes"] = self.attributes
		json.dump_file(fileName,r)
	
	@staticmethod
	def load(fileName):
		mm = metaData(None,None,None)
		r = json.load_file(fileName)
		mm.title = r["title"]
		mm.iconName = r["iconName"]
		if "fontSize" in r:
			mm.fontSize = r["fontSize"]
		ff = collections.OrderedDict()
		for f in r["fields"]:
			if isinstance(f,str):	#newline,space,group 
				ff[uuid.uuid1()] = f
			else:
				m = metaItem.loadData(f)
				m.meta = mm
				if m.fieldName in ff:
					print("repeat fieldName",m.fieldName,ff)
				assert m.fieldName not in ff
				ff[m.fieldName] = m
		mm.fields = ff
		mm.objType = enhance.getType(r["objType"])
		mm.primaryKeys = set(r["primaryKeys"])
		if "attributes" in r:
			mm.attributes = r["attributes"]
		return mm
		

class editWidget(PyQt5.QtWidgets.QWidget): 
	def __init__(self,obj,meta,editable):
		super(editWidget, self).__init__() 
		self.changedCallbacks = {}
		self.enableCallbacks = {}
		self.meta = meta
		self._editable = editable
		self.ctrls = {}	
		ll = QVBoxLayout()
		self.setLayout(ll)
		self.createCtrls(obj)
		self.currentID = None
		
		
	def onChanged(self,ctrl,label,event):
		if not self._editable:
			return
		if ctrl.meta.value(ctrl) != ctrl.oldValue:
			ctrl.isModified = True
			_setModified(label)
		else:
			ctrl.isModified = False
			_clearModified(label)
		if ctrl.meta.fieldName in self.changedCallbacks:
			self.changedCallbacks[ctrl.meta.fieldName](ctrl.meta.fieldName,ctrl.meta.value(ctrl))

	def onEnableChanged(self, ctrl, cb, event):
		if not self._editable:
			return
		ctrl.setEnabled(cb.isChecked())
		if ctrl.meta.fieldName in self.enableCallbacks:
			self.enableCallbacks[ctrl.meta.fieldName](ctrl.meta.fieldName, cb.isChecked())

	def createLayout(self,layoutClass=QVBoxLayout,editable=True):
		ctrls = {}
		mainLayout = layoutClass()
		mainLayout.setSpacing(20)
		mainLayout.setAlignment(Qt.AlignTop)
		l = None
		group = None
		for f in self.meta:
			if isinstance(f,str):
				if f == "newLine":
					l = QFormLayout()
					l.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
					l.setSpacing(10)  
					mainLayout.addLayout(l)
				elif f == "space":
					q = QWidget()
					q.setFixedSize(20,20)
					l.addRow(q)
				else:
					group = PyQt5.QtWidgets.QGroupBox(f)
					font = group.font()
					font.setPointSize(self.meta.fontSize)
					group.setFont(font) 
					#group.setCheckable(True)
					l = QFormLayout()
					l.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
					l.setSpacing(10) 
					group.setLayout(l)
					mainLayout.addWidget(group)
				continue
			if l is None:
				l = QFormLayout()
				l.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
				l.setSpacing(10) 
				mainLayout.addLayout(l)
			c,labels,cbs = f.addCtrl(l,editable=editable)
			if c:
				if isinstance(c,tuple):
					#c[0].meta = f
					for i,cc in enumerate(c):
						cc.meta = f
						cc.label = labels[i]
						cc.cb = cbs[i]
						cc.oldValue = cc.meta.value(cc)
						cc.isModified = False
						qtutility.setChangedEvent(cc,enhance.bind(self.onChanged,cc,labels[i]))
						qtutility.setChangedEvent(cc.cb,enhance.bind(self.onEnableChanged,cc,cc.cb))
				else:
					c.meta = f
					c.label = labels
					c.cb = cbs
					c.oldValue = c.meta.value(c)
					c.isModified = False
					qtutility.setChangedEvent(c,enhance.bind(self.onChanged,c,labels))
					qtutility.setChangedEvent(c.cb, enhance.bind(self.onEnableChanged, c, c.cb))

				ctrls[f.fieldName] = c  
		return (mainLayout,ctrls)
	
	def createCtrls(self,obj):
		qtutility.clearLayout(self.layout())
		l,self.ctrls = self.createLayout(editable=self.editable)
		self.layout().addLayout(l)
		self.setValue(obj)
		return l
		
	def check(self,manager=None):
		for item in self.meta:
			if isinstance(item,str):
				continue
			msg = item.check(self.ctrls[item.fieldName])
			if msg:
				log.warning(msg)
				return msg
			if manager:
				msg = manager.checkRepeat(self.getObj())
				if msg:
					log.warning(msg)
					return msg
		return ""
		
	def setValue(self,obj): 
		assert isinstance(obj,self.meta.objType)
		if hasattr(obj,"id"):
			self.currentID = obj.id
		if isinstance(obj,dict):
			if "id" in obj:
				self.currentID = obj["id"]
				
		for key in self.ctrls:
			cc = self.ctrls[key]
			if isinstance(cc,tuple):
				if self.editable:
					v = cc[0].meta.value(obj)
				else:
					v = cc[0].meta.valueStr(obj)
				for c in cc:
					qtutility.setValue(c,v) 
			else:
				if self.editable:
					v = cc.meta.value(obj)
				else:
					v = cc.meta.valueStr(obj)
				qtutility.setValue(cc,v)  
		self.obj = obj
		self.clearModified()
		return obj
		
	def getCtrl(self,name):
		c = self.ctrls[name]
		if isinstance(c,tuple):
			return c[0]
		return c
		
	def getValue(self,name):
		c = self.getCtrl(name)
		return c.meta.value(c)
			
	def setItem(self,name,value):
		# assert self.editable
		c = self.getCtrl(name)
		if not self.editable:
			value = c.meta.valueStr({name: value})
		qtutility.setValue(c,value)

	def setValueEnabled(self,name,value):
		c = self.getCtrl(name)
		qtutility.setValue(c.cb,value)
		
	def getObj(self,modifiedOnly=False): 
		return self._get(self.meta.objType(),modifiedOnly=modifiedOnly)
		
	def getDict(self,modifiedOnly=False):
		return self._get({},modifiedOnly=modifiedOnly)
		
	def _get(self,obj,modifiedOnly):
		if self.currentID is not None:
			utility.set_attr(obj,"id",self.currentID)
		for key in self.ctrls:
			cc = self.ctrls[key]
			b = False
			if isinstance(cc,tuple):
				v = cc[0].meta.value(cc[0])
				b = cc[0].isModified or cc[1].isModified
			else:
				b = cc.isModified
				v = cc.meta.value(cc)
			if modifiedOnly and not b:
				continue
			utility.set_attr(obj,key,v)
		return obj
		
	@property
	def editable(self):
		return self._editable
	
	@editable.setter
	def editable(self,v):
		self._editable = v
		self.createCtrls(self.obj)
		
	def clearModified(self):
		labels = []
		for cc in self.ctrls:
			cc = self.ctrls[cc]
			if isinstance(cc,tuple):
				for c in cc:
					c.oldValue = c.meta.value(c)
					c.isModified = False
					labels.append(c.label)
			else:
				cc.oldValue = cc.meta.value(cc)
				cc.isModified = False
				labels.append(cc.label)
		for label in labels:
			_clearModified(label)
	
	def setChangedEvent(self,name,callback):
		self.changedCallbacks[name] = callback

	def setEnableChangedEvent(self,name,callback):
		self.enableCallbacks[name] = callback

class editDlg(QDialog):
	def __init__(self,obj,meta,manager=None,editable=False):
		super(editDlg, self).__init__()
		self.setWindowFlags(Qt.WindowCloseButtonHint)
		self.ctrl = editWidget(obj,meta,editable=editable)
		self.ctrl.setChangedEvent("ddd", self.ondddChanged)
		self.ctrl.setEnableChangedEvent("ddd", self.ondddEnableChanged)
		self.ctrl.setChangedEvent("bbb", self.ondddChanged)
		self.ctrl.setEnableChangedEvent("bbb", self.ondddEnableChanged)
		self.manager = manager
		if meta.iconName:
			self.setWindowIcon(qta.icon(meta.iconName,color='white'))
		if "width" in meta.attributes:
			w = meta.attributes["width"]
		else:
			w = 600
		if "height" in meta.attributes:
			h = meta.attributes["height"]
		else:
			h = max(len(meta)*50,150)
		self.setFixedWidth(w)		
		self.setFixedHeight(h)		
		
		ll = QVBoxLayout()
		ll.addWidget(self.ctrl)
		ll.addLayout(self.createBtns())
		self.setLayout(ll)
		self.setValue(obj)
		self.setWindowTitle("新建"+meta.title) 
		
	@property
	def currentID(self):
		return self.currentID
		
	def createBtns(self):
		l2 = QHBoxLayout()
		l2.addStretch(1) 
		l2.setSpacing(20)
		
		b = QPushButton(qta.icon("fa.edit",scale_factor=1.1,color="blue"),"编辑")
		b.setMinimumHeight(40)
		b.clicked.connect(self.edit)
		b.setFixedWidth(80)
		l2.addWidget(b)
		
		b = QPushButton(qta.icon("fa.check",scale_factor=1.5,color="green"),"确定")
		b.setMinimumHeight(40)
		b.clicked.connect(self.accept)
		b.setFixedWidth(80)
		self.okBtn = b
		l2.addWidget(b) 
		
		b = QPushButton(qta.icon("fa.remove",scale_factor=1.5,color="red"),"取消")
		b.setMinimumHeight(40)
		b.clicked.connect(self.reject)
		b.setFixedWidth(80)
		l2.addWidget(b)
		return l2 
		
	def edit(self):
		self.ctrl.editable = not self.ctrl.editable
		
	def accept(self):
		msg = self.ctrl.check(self.manager)
		if msg:
			qtutility.showWaring(msg)
			return
		super(editDlg, self).accept()
		
	def setValue(self,obj): 
		self.ctrl.setValue(obj)
		self.setWindowTitle("编辑"+self.ctrl.meta.title)	
		return obj
		
	def getObj(self,modifiedOnly): 
		return self.ctrl.getObj(modifiedOnly=modifiedOnly)
		
	def getDict(self,modifiedOnly):
		return self.ctrl.getDict(modifiedOnly=modifiedOnly)

	def ondddEnableChanged(self, obj, value):
		if str(obj)=='bbb':
			self.ctrl.setValueEnabled('ddd',True)
		print('{0}选择框改变了:{1}'.format(str(obj),value))

	def ondddChanged(self, obj, value):
		print('{0}的值改变了:{1}'.format(str(obj),value))

def show(filename):
	app = PyQt5.QtWidgets.QApplication(sys.argv)
	m = metaData.load(filename)	
	d = editDlg({},m) 
	d.show() 
	sys.exit(app.exec_())

########### unit test ###########
def test():
	a = scramble
	m = metaData(dict,"测试对话框")
	m.addInt("字段int","aaa",min=10,max=20,isCheckble=True)
	m.addText("字段text","bbb",maxSize=12,isCheckble=True)
	#m.addNewLine()
	a= m.addFloat("字段float","ddd",isCheckble=True)
	a.tooltip = "字段fffffffffloooooooat"
	m2 = m.addSelect("字段select","eee",[(0,"item0"),(1,"item1"),(2,"item2"),(4,"item4")])
	m2._defaultValue=2
	
	m.addGroup("test2")
	m.addBool("字段bool","cccbb",falseText="禁用",trueText="启用")
	m.addGroup("test1")
	m.addPwd("字段pwd","ccc")
	m.setPrimary("aaa")
	m.save("test/testmeta.json")
	
	vv = {'aaa': 12, 'bbb': '13', 
		  'ccc': '2f71758b439918d452c641d9236ffd61', 
		  'ddd': 16.0, 'eee': 1, 'cccbb': True}
	
	app = PyQt5.QtWidgets.QApplication(sys.argv)
	m2 = metaData.load("test/testmeta.json")	
	d = editDlg({},m2) 
	d.setValue(vv)
	d.show() 
	app.exec_()
	print("modified:",d.getDict(True))
	sys.exit()
	
if __name__ == '__main__': 
	# show("./area_meta.json")
	test()
	
	
	
	
	
	
	