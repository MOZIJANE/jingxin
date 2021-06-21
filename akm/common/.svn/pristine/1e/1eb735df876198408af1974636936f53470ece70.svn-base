#coding=utf-8
# ycat			2018-04-10	  create
# 自动生成web的编辑页面 
import sys,os 
import datetime
import utility
import mongodb as db
import scadaUtility
import json_codec
import bottle
import webutility
import pymongo 
import log
import enhance
	
def _checkCls(cls):
	global g_metaData
	if cls not in g_metaData:
		c = utility.empty_class()
		c.tableName = ""	
		c.idType = db.ObjectId
		c.filter = {}		
		c.sort = None		
		c.fields = []
		c.fieldDict = {}
		g_metaData[cls] = c
	 
class style:
	def __init__(self):
		pass
 
#弹出详细信息 	
#tableName: 对应的数据库表名，必须要是配有对应有meta类型 
#foreignId：外键对应的字段id 
class popup(style):
	def __init__(self,tableName,foreignId):
		style.__init__(self)
		self.tableName = tableName  
		global g_objData
		if self.tableName not in g_objData:
			raise Exception("找不到相应的表"+self.tableName)
		self.urlStr = "/"+utility.app_name()+"/detail?table="+self.tableName
		self.foreignId = foreignId
		
	def url(self,id): 
		pass
		#return self.urlStr+"&id="+str(id)
		
		
#跳转到另一个页面		
class redirect(style):
	def __init__(self,url,idList):
		assert isinstance(idList,list)
		style.__init__(self)
		self.dict = {}
		self.dict["url"] = url
		self.dict["id"] = idList
		
	
#提供class 
class styleClass(style):
	def __init__(self):
		style.__init__(self)
	
#时间戳的字段 	
def timestampField():
	def __call(cls):		
		return field(id="timestamp", name="修改时间", visible=True, readonly=True, default=utility.now,type=datetime)(cls)
	return __call	
	
	
#配置字段的属性 	
# isUnique : 说明该字段是否为唯一字段，None代表可以重复，[]代表自己不能重复，[xxx,xxx]代表多个唯一字段
# style：list类型，可以为[str]代表支持配置不同的class，或者为redirect、popup代表可以跳转 
def field(id, name, visible=True, readonly=False, type=None, editCtrl=None, default=None, rules=[], unique=None,style=None):
	if default is not None:
		if type == datetime.datetime and isinstance(default,datetime.datetime):
			default = utility.date2str(default)
		if type == datetime.date and isinstance(default,datetime.date):
			default =  datetime.datetime.strftime(default,'%Y-%m-%d')
		if type == datetime.time and isinstance(default,datetime.time):
			default = datetime.time.strftime(default,'%H:%M:%S')
	elif type == int or type == float:
		if isinstance(editCtrl,inputNumber):
			if "min" in editCtrl.attrMap:
				default = editCtrl.attrMap["min"]
		else:
			default = 0
	if type == stringList or type == numberList:
		#stringList类型必需要填editCtrl的值 
		assert isinstance(editCtrl,select) or isinstance(editCtrl,checkbox)
		editCtrl.setMultiple()
		if default is not None:
			assert isinstance(default,(list,tuple))
			
	if type == bool and default is None:
		default = False
			
	if editCtrl is None:
		editCtrl = _baseCtrl.create(type)
		
	if id == "_id" and type is None:
		type = db.ObjectId
	if type == db.ObjectId and not readonly:
		#ObjectId不可以编辑 
		raise Exception("type为ObjectId时，不可以编辑")
	
	if unique == True:
			unique = []
			
	def __call(cls):		
		global g_metaData
		c = utility.empty_class()
		c.validate = rules
		c.type = type
		c.id = id
		c.name = name
		c.visible = visible
		c.readonly = readonly
		c.editCtrl = editCtrl
		c.defaultValue = default
		c.rules = rules
		c.unique = unique
		c.style = style
		c.styleDict = {}
		if style:
			for s in style:
				if isinstance(s,redirect):
					if "redirect" not in c.styleDict:
						c.styleDict["redirect"] = s.dict
				elif isinstance(s,popup): 
					if "popup" not in c.styleDict:
						c.styleDict["popup"] = {"url":s.urlStr,"id": s.foreignId}
				elif isinstance(s,styleClass):
					c.styleDict["class"] = s 
		_checkCls(cls)
		g_metaData[cls].fields.insert(0,c)
		g_metaData[cls].fieldDict[c.id] = c
		if id == "_id":
			g_metaData[cls].idType = type
		return cls
	return __call	
	
#取domain的函数，如果为空代表系统不需要domain
#如返回""代表全域查询，即admin	
getDomainFunc = None

#判断是否可以编辑 
def defaultPermission():	
	return True
	
def defaultWriteLog(object,desc):
	log.info(desc)
	
#检查权限的回调函数 	
checkPermissionFunc = defaultPermission
	
#写系统日志的回调函数 
writeLogFunc = defaultWriteLog

#只有一列的layout
class baseLayout:
	def __init__(self,width,split):
		self.dict = {"width":str(width)+"px","split":split,"type":"normal"}
		
class layout1(baseLayout):
	def __init__(self,width=500,split=0):
		baseLayout.__init__(self,width,split)

#有二列的layout		
class layout2(baseLayout):
	def __init__(self,width=900,split=1):
		baseLayout.__init__(self,width,split)

#带经纬度的layout，这个右边会自动生成一个地图，要求field必需要存在longitude和latitude两个字段
class layoutMap(baseLayout):
	def __init__(self,width=500,split=1):
		baseLayout.__init__(self,width,split)
		self.dict["type"] = "map"
	
def table(tableName,title,filter={},sort=None,domain=True,layout=layout1(),permission=["create","edit","delete"]):
	install()
	def __call(cls):
		global g_metaData,g_objData
		_checkCls(cls)
		g_metaData[cls].tableName = tableName
		g_metaData[cls].layout = layout
		g_metaData[cls].title = title
		g_metaData[cls].filter = filter
		g_metaData[cls].sort = sort
		g_metaData[cls].domain = domain
		g_metaData[cls].permission = permission
		g_metaData[cls].appName = utility.app_name()
		g_objData[tableName] = cls()
		for f in g_metaData[cls].fields:
			if isinstance(f.editCtrl,select):
				f.editCtrl.updateUrl(tableName,f.id,utility.app_name())
		return cls
	return __call	
		
g_metaData = {}	
g_objData = {}	

class manager:
	def __init__(self):
		self.data = []

	def load(self):
		self.data = self.query(self._meta.filter,self._meta.sort)
		return self.data
	
	@staticmethod
	def _toMongodbData(data):
		for d in data:
			if isinstance(data[d],datetime.time):
				data[d] = datetime.time.strftime(data[d],'%H:%M:%S')
			elif isinstance(data[d],datetime.date) and not isinstance(data[d],datetime.datetime):
				data[d] = datetime.datetime(data[d].year,data[d].month,data[d].day,0,0,0)
		return data
	
	def _domainFilter(self,filter):
		global getDomainFunc
		if getDomainFunc and self._meta.domain:
			d = getDomainFunc()
			if len(d):
				#空domain代表所有的domain都支持 
				if "domain" in filter:
					raise Exception("getDomainFunc和filter里的domain冲突")
				filter["domain"] = d
		return filter
		
	def query(self,filter={},sort={}):
		f = utility.clone(filter)
		ds = db.find(self._meta.tableName, self._domainFilter(f),columns=list(self.__meta.fieldDict.keys()))
		if sort:
			data = ds.sort(sort).list()
		else:
			data = ds.list()
		return data

	def query_one(self,filter):
		data = db.find_one(self._meta.tableName, self._domainFilter(filter),columns=list(self.__meta.fieldDict.keys()))
		return data
	
	#更时数据时的回调，可重载 
	def updateData(self,data):
		return data
	
	def checkUnique(self,data,id):
		for f in self._meta.fields:
			if f.unique is None:
				continue
			cond = {}
			if "domain" in data:
				cond["domain"] = data["domain"]
			cond[f.id] = data[f.id]
			for c in f.unique:
				cond[c] = data[c]
			if id is not None:
				#update情况下
				if "_id" in cond:
					#说明unique的对象是_id，而且是update状态 
					continue
				#排除自己这条记录  
				cond["_id"] = {"$ne":self._meta.idType(id)}
				
			if db.find_one(self._meta.tableName,cond) is not None:
				e =  Exception(f.name+"为"+data[f.id]+"的数据已经存在")
				e.noprint = True
				raise e
			
	def _updateDomain(self,data):
		global getDomainFunc
		if getDomainFunc and self._meta.domain:
			if "domain" not in data:
				d = getDomainFunc()
				if len(d):
					data["domain"] = d
		return self.updateData(data)
		
	def _updateDefault(self,data):
		for f in self._meta.fields:
			if f.id in data:
				continue
			if f.defaultValue:
				if hasattr(f.defaultValue,"__call__"):
					data[f.id] = f.defaultValue()
				else:
					data[f.id] = f.defaultValue
		return data
		
	def insert(self,data):
		try:
			global writeLogFunc
			d = self._updateDomain(data)
			self.checkUnique(d,None)
			self._updateDefault(d)
			ret = db.insert(self._meta.tableName,manager._toMongodbData(data))
			
			writeLogFunc(self._meta.title,"创建"+self._meta.title + "成功: "+self.metaDesc(data))
			return data["_id"]#ret.inserted_id 
		except Exception as e:
			writeLogFunc(self._meta.title,"创建"+self._meta.title + "失败: "+self.metaDesc(data)+", 原因:"+str(e))
			raise
		
	def delete(self,id):
		idName = ""
		try:
			if not isinstance(id,list):
				db.delete_one(self._meta.tableName,{"_id":id})
				idName = str(id)
				writeLogFunc(self._meta.title,"删除"+self._meta.title + "成功: "+ idName)
			else:
				db.delete_many(self._meta.tableName,{"_id":{"$in":id}})
				idName = ", ".join([str(x) for x in id])
				writeLogFunc(self._meta.title,"删除"+self._meta.title + "成功: "+ idName)
		except Exception as e:
			writeLogFunc(self._meta.title,"删除"+self._meta.title + "失败: "+ idName+", 原因:"+str(e))
			raise
			
		
	def update(self,id,data):
		try:
			d = self._updateDomain(data)
			self.checkUnique(d,id)
			self._updateDefault(d)
			db.update_one(self._meta.tableName,{"_id":id},manager._toMongodbData(data))
			writeLogFunc(self._meta.title,"更新"+self._meta.title + "成功: "+self.metaDesc(data))
		except Exception as e:
			writeLogFunc(self._meta.title,"更新"+self._meta.title + "失败: "+self.metaDesc(data)+", 原因:"+str(e))
			raise 
			
	def get(self,id):
		data = db.find_one(self._meta.tableName,{"_id":self._meta.idType(id)})
		if data is None:
			return {"异常":"找不到ID"+str(id)}
		ret = []
		for field in self._meta.fields:
			if field.id not in data:
				continue
			v = field.editCtrl.toDisplay(data[field.id])
			if isinstance(v,list):
				v = ",".join([str(x) for x in v])
			ret.append({"value":str(v),"label":field.name})
		return ret
			
	def __str__(self):
		return utility.str_obj(self.data)
		
	def drop(self):
		db.delete_many(self._meta.tableName)
		
	def metaDesc(self,data):
		desc = []
		for d in data:
			if d not in self.__meta.fieldDict:
				continue
			v = self._meta.fieldDict[d].editCtrl.toDisplay(data[d])
			desc.append(self._meta.fieldDict[d].name+" : `"+str(v)+"`")
		return ", ".join(desc)
		
	@property
	def _meta(self):
		if not hasattr(self,"__meta"):
			self.__meta = g_metaData[type(self)] 
		mm = self.__meta
		
		#动态增加删除域 
		global getDomainFunc
		if mm.domain:
			id = "domain"
			if getDomainFunc and len(getDomainFunc()) == 0:
				#domain为空时(即admin)的编辑和查询页面不一样的	
				if id not in mm.fieldDict:
					s = select(tableName="u_domain",valueField="_id",nameField="name")
					s.updateUrl("u_domain",id,mm.appName)
					field(id=id, name="域", visible=True, readonly=False, type=str,editCtrl=s,rules=[require()])(type(self))
			else:
				if id in mm.fieldDict and getDomainFunc:
					#删除domain域  
					del mm.fieldDict[id]
					i = 0
					find = False
					for f in mm.fields:
						if f.id == id:
							find = True
							break
						i += 1
					if find:
						del mm.fields[i] 
		return mm
		
	def _metaData(self):
		mm = []
		for f in self._meta.fields:
			m = {}
			m["id"] = f.id
			m["name"] = f.name
			m["visible"] = f.visible
			m["readonly"] = f.readonly
			m["editCtrl"] = f.editCtrl.dict 
			m["rules"] = [ r.attrMap for r in f.rules]
			if f.defaultValue is not None:
				if hasattr(f.defaultValue,"__call__"):
					m["editCtrl"]["default"] = f.defaultValue()
				else:
					m["editCtrl"]["default"] = f.defaultValue
			if f.style is not None:
				m["styleCtrl"] = f.styleDict
			mm.append(m)
		return mm
	
	#重载此函数，用于返回不同的class 
	def getClassStyle(self,row,fieldId):
		assert 0 #如果配置了style的styleClass必须要重载这个函数 
		return []
		
	def urlDetail(self,id):
		return self.get(id)
		
	def urlQuery(self,params=None):
		global checkPermissionFunc
		permission = checkPermissionFunc()
		self.load()
		 
		for d in self.data:
			if isinstance(d["_id"],db.ObjectId):
				d["_id"] = str(d["_id"]) 
			for n in d:
				if n not in self._meta.fieldDict:
					continue
				field = self._meta.fieldDict[n]
				if field.type == datetime.time and isinstance(d[n],datetime.time):
					d[n] = "%02d:%02d:%02d"%(d[n].hour,d[n].minute,d[n].second)
				elif field.type == datetime.date and isinstance(d[n],datetime.date):
					d[n] = "%04d-%02d-%02d"%(d[n].year,d[n].month,d[n].day) 
				else:
					d[n] = field.editCtrl.toDisplay(d[n])
		pp = {}
		for p in  self._meta.permission:
			pp[p] = permission
		return {"title":self._meta.title,"meta":self._metaData(),"data":self.data,"permission":pp,"layout":self._meta.layout.dict}	
		
	def urlDelete(self,params):
		try:
			#注意，以前的数据为objectId，后面换成str，会导致无法删除objectId的数据 
			ids = [ manager._getValue(self._meta.idType,x) for x in params["idList"] ]
			self.delete(ids)
		except:
			raise
	
	def urlUpdate(self,params):
		id = manager._getValue(self._meta.idType, params["_id"])
		self.update(id,self._getWebData(params))
		
	def urlInsert(self,params):
		if self._meta.idType == db.ObjectId and "_id" in params:
			raise Exception("不可以新增ObjectId")
		self.insert(self._getWebData(params))
	
	@staticmethod
	def _getValue(type,value,ctrl=None):
		if type == str:
			return str(value)
		if type == int:
			return int(value)
		if type == float:
			return float(value)
		if type == db.ObjectId:
			return db.ObjectId(value)
		if type == stringList:
			return [str(x) for x in value]
		if type == numberList:
			return [int(x) for x in value]
		if type == bool or type == datetime.datetime or datetime.time or  type == datetime.date or type == password:
			return ctrl.toValue(value)			
		return value
		
	def _getWebData(self,params):
		data = {}
		for f in self._meta.fields:
			if f.id in params:
				v = params[f.id]
				data[f.id] = self._getValue(f.type,v,f.editCtrl)
		return data
	
	
###################  控件定义 	###################		
class _baseCtrl:
	def __init__(self,type):
		self.attrMap = {}
		self.dict = {"type":type,"attr":self.attrMap}
		
	def set(self,key,value):
		if value is not None:
			self.attrMap[key] = value
	
	@staticmethod
	def create(type):
		if type == db.ObjectId:
			return noneCtrl()
		if type == str:
			return input()
		if type == int:
			return inputNumber()
		if type == float:
			return inputNumber()
		if type == datetime.datetime:
			return datetimePicker()
		if type == datetime.date:
			return datePicker()
		if type == datetime.time:
			return timePicker()
		if type == bool:
			return switch()
		if type == password:
			return inputPassword()
		return  noneCtrl()
		
	def toDisplay(self,value):
		return value
	
	def toValue(self,display):
		return display
		
		
class noneCtrl(_baseCtrl):
	def __init__(self):
		_baseCtrl.__init__(self,None)
		
		
class datetimePicker(_baseCtrl):
	def __init__(self):
		_baseCtrl.__init__(self,"datetimePicker")		
		
	def toValue(self,display):
		return utility.str2date(str(display))
		
		
class datePicker(_baseCtrl):
	def __init__(self):
		_baseCtrl.__init__(self,"datePicker")
		
	def toValue(self,display):
		return datetime.datetime.strptime(display,'%Y-%m-%d').date()

		
class timePicker(_baseCtrl):
	def __init__(self):
		_baseCtrl.__init__(self,"timePicker")		
	
	def toValue(self,display):
		return datetime.datetime.strptime(display,'%H:%M:%S').time()
		
		
class input(_baseCtrl):
	def __init__(self,minlength=None,maxlength=255,placeholder=None):
		_baseCtrl.__init__(self,"input")
		self.set("minlength",minlength)
		self.set("maxlength",maxlength)
		self.set("placeholder",placeholder)
		
	def toValue(self,display):
		return str(display)
		
		
class inputPassword(_baseCtrl):
	def __init__(self,minlength=None,maxlength=None,placeholder=None):
		_baseCtrl.__init__(self,"inputPassword")
		self.set("minlength",minlength)
		self.set("maxlength",maxlength)
		self.set("placeholder",placeholder)
		
	def toValue(self,display):
		value = str(display)
		if len(value) < 30:
			return password.scramble(value)
		return value
	
	
class inputNumber(_baseCtrl):
	def __init__(self,min=None,max=None,step=None):
		_baseCtrl.__init__(self,"inputNumber")
		self.set("min",min)
		self.set("max",max)
		self.set("step",step)
		
		
class slider(inputNumber):
	def __init__(self,min=None,max=None,step=None):
		inputNumber.__init__(self,min,max,step)
		self.dict["type"] = "slider"
		
		

class switch(_baseCtrl):
	#active-text	打开时的文字描述
	#inactive-text	关闭时的文字描述
	def __init__(self,trueText="YES",falseText="NO"):
		_baseCtrl.__init__(self,"switch")
		self.set("activeText",trueText)
		self.set("inactiveText",falseText) 
		self.set("activeValue",True)
		self.set("inactiveValue",False)
		self.set("activeColor","#13ce66")
		self.set("inactiveColor","gray")
	
	def toDisplay(self,value):
		if value:
			return self.attrMap["activeText"]
		else:
			return self.attrMap["inactiveText"]
		
	def toValue(self,display):
		if isinstance(display,bool):
			return display
		if display == self.attrMap["activeText"]:
			return True
		return False
		
#选择控件，可以为2种写法
#静态写法:
#			s = select()
#			s.add("value1","蛋挞")
#			s.add("value2","蛋糕")
#			s.add("value3","雪糕")
#
#数据库写法(自动根据表，生成url)：
#			s = select(tableName="c_log_level",valueField="_id",nameField="name")
#
g_databaseSelect = {} 
class select(_baseCtrl):
	#parentId为级联ID，例如省->市的级联，即parent的@field的id 
	#parentValueField为级联选择表的父ID，即select.tableName的字段名 
	def __init__(self,tableName=None,valueField="_id",nameField="name",
		domain=True,parentValueField=None,parentId=None,parentType=None,placeholder=None):
		_baseCtrl.__init__(self,"select")		
		self._items = []
		self._itemsCache = None
		self.tableName = tableName
		self.valueField = valueField
		self.nameField = nameField 
		self.domain = domain
		self.domainValue = ""
		self.parentValueField = parentValueField
		self.parentType = parentType
		if parentId is not None:
			assert self.tableName
			assert parentValueField
			assert parentType
		self.dict["parentId"] = parentId 
		self.isStatic = False
			
	def add(self,value,label,parent=None):
		self.isStatic = True
		self.domainValue = None
		self._items.append({"value":value,"label":label,"parent":parent})
			
	def clearAll():
		global g_databaseSelect
		for s in g_databaseSelect:
			g_databaseSelect[s].clear()
		
	def clear(self):
		if self.isStatic:
			return
		self._items.clear()
		
	def _domain(self):
		global getDomainFunc
		if getDomainFunc and self.domain:
			domain = getDomainFunc()
			if domain:
				return domain
		return None
	
	def items(self,parentId):
		domain = self._domain()
		if domain is not None and self.domainValue is not None:
			#切换domain清掉缓冲 
			if self.domainValue != domain:
				self._items.clear()
				
		if len(self._items): 
			if parentId is None:
				return [{"value":x["value"],"label":x["label"]} for x in self._items]
			return [{"value":x["value"],"label":x["label"]} for x in self._items if x["parent"] == self.parentType(parentId)]
		#from database
		list = []
		cond = {}
		self.domainValue = domain
		if domain is not None:
			cond["$or"] = [{"domain":domain},{"domain":{"$exists": False}}]
		assert self.tableName 
		if self.parentType is not None:
			assert self.parentValueField is not None
			assert self.parentType is not None
			ds = db.find(self.tableName,cond,columns=[self.valueField,self.nameField,self.parentValueField])
			while ds.next():
				self._items.append({"value":ds[self.valueField],"label":ds[self.nameField],"parent":ds[self.parentValueField]})
		else:
			ds = db.find(self.tableName,cond,columns=[self.valueField,self.nameField])
			while ds.next():
				self._items.append({"value":ds[self.valueField],"label":ds[self.nameField],"parent":None})
		if 0 == len(self._items):
			return []
		return self.items(parentId)
	
	def toDisplay(self,value):
		#TODO:这里有优化的空间，访问数据库太多了 
		def _display(value):
			for i in self.items(None):
				if str(value) == str(i["value"]):
					return i["label"]
			return None
		if isinstance(value,list):
			return [ _display(x) for x in value ]
		else:
			return _display(value)
		
	def toValue(self,display):
		for i in self.items(None):
			if display == i["label"]:
				return i["value"]
		return None
		
	def updateUrl(self,table,field,appName):
		global g_databaseSelect
		g_databaseSelect[table+"."+field] = self
		self.dict["url"] = "/api/"+appName+"/object/select?id="+table+"."+field
	
	def setMultiple(self):
		self.attrMap["multiple"] = True
		
#自定义的select框
class customSelect(select):
	def __init__(self):
		select.__init__(self) 
		self.isStatic = True
		
	#格式：[{"value":value,"label":label}...]
	@enhance.abstract
	def items(self,parentId):
		pass
		
		
class radio(select):	
	def __init__(self,tableName=None,valueField="_id",nameField="name"):
		select.__init__(tableName,valueField,nameField,placeholder=None)

		
class checkbox(select):
	def __init__(self,tableName=None,valueField="_id",nameField="name"):
		select.__init__(tableName,valueField,nameField,placeholder=None)
		self.setMultiple()
		
###################  类型定义 	###################
#密码类型，等同于str,int，bool，不是密码控件 	
class password:
	@staticmethod
	def scramble(pwd):
		return utility.md5(pwd+"hello")		
		
#objectId类型，不可编辑 		
ObjectId = db.ObjectId

#字符串列表类型 
class stringList:
	pass

#数据列表类型 
class numberList:
	pass	
		
#类型支持： 	str, 	int, 		float, 		 datetime,		 datetime.date, datetime.time, password, 		
#类型默认参数： input,	inputNumber,inputNumber, datetimePicker, datePicker,	   timePicker,	  inputPassword,	switch

#布尔型 
#bool
#switch 

#整型可选控件
#slice, select, radio 

#字符串可选控件
#richText,  select, radio

#stringList列表类型
#checkbox, multi-select 

#控件参见 http://element.eleme.io/#/zh-CN/component/radio

###################  校验定义 	###################
#校验控制 
class rule:
	def __init__(self):
		self.attrMap = {"trigger" : "blur"}
		
#必选判断  		
class require(rule):
	def __init__(self,message="该字段为必选字段"):
		rule.__init__(self)
		self.attrMap["required"] = True
		self.attrMap["message"] = message

#正规判断	
class regex(rule):
	def __init__(self,regexPattern,message):
		rule.__init__(self)
		self.attrMap["message"] = message
		self.attrMap["type"] = "string"
		self.attrMap["pattern"] = regexPattern
	
#url判断 	 
class url(rule):
	def __init__(self,message="请输入正确的URL地址"):	
		rule.__init__(self)
		self.attrMap["message"] = message
		self.attrMap["type"] = "url"
	
#16进制判断 	 
class hex(rule):
	def __init__(self,message="请输入正确的十六进制"):	
		rule.__init__(self)
		self.attrMap["message"] = message
		self.attrMap["type"] = "hex"

#email判断 	 
class email(rule):
	def __init__(self,message="请输入正确的email地址"):	
		rule.__init__(self)
		self.attrMap["message"] = message	
		self.attrMap["type"] = "email"
		 
	 
def _urlSelect():
	list = []
	id = webutility.get_param("id")
	parentId = webutility.get_param("parentId")
	if parentId is not None and 0 == len(parentId):
		parentId = None
	global g_databaseSelect
	if id in g_databaseSelect:
		list = g_databaseSelect[id].items(parentId)
	return {"list":list}
 
def _urlManage(): 
	global g_objData
	table = webutility.get_param("table")
	method = webutility.get_param("method")
	params = None
	if method != "query":
		payload = bottle.request.body.read().decode('utf-8')
		params =  json_codec.load(payload)
	result = curdObject(method, params, table)
	select.clearAll() #防止数据不会变化 
	return result
 
def _urlDetail(): 
	table = webutility.get_param("table")
	id = webutility.get_param("id")
	global g_objData
	return {"list":g_objData[table].get(id)}

g_installModule = set()

def install():
	global g_installModule
	n = utility.app_name()
	if n not in g_installModule:
		g_installModule.add(utility.app_name())
		scadaUtility.add("/api/" + n + "/detail",_urlDetail)
		scadaUtility.add("/api/" + n + "/object",_urlManage)
		scadaUtility.add("/api/" + n + "/object/select",_urlSelect)

def curdObject(method, params, table):
	objMgr = g_objData[table]
	try:
		if method == "insert":
			return objMgr.urlInsert(params)
		elif method == "update":
			return objMgr.urlUpdate(params)
		elif method == "delete":
			return objMgr.urlDelete(params)
		else:
			return objMgr.urlQuery(params)
	except pymongo.errors.DuplicateKeyError:
		e = Exception("输入的键值重复")
		e.noprint = True
		raise e


################### unit test 	###################
testSel1 = select()	
testSel1.add(1,"科室1")
testSel1.add(2,"科室2")
testSel1.add(3,"科室3")
testSel1.add(4,"科室4")
	
testSel2 = select()	
testSel2.add(1,"科室1")
testSel2.add(2,"科室2")
testSel2.add(3,"科室3")
testSel2.add(4,"科室4")
testSel2.add(5,"科室5")
	
def testselect():
	testSel2 = select(tableName="c_ycat_test",valueField="_id",nameField="name")
	db.drop_table("c_ycat_test")
	for i in range(10):
		d = {}
		d["_id"] = str(i+100)
		d["name"] = "智能"+str(i)
		d["ppid"] = i
		db.insert("c_ycat_test",d)
	@table("u_ycat_test3","测试数据3",layout=layout1(width=500))
	@field(id="_id",name="id",visible=False,readonly=True)
	@field(id="selectValue",name="选择字段1",type=int,editCtrl=testSel1,default=1)
	@field(id="selectValue2",name="选择字段2",type=str,editCtrl=testSel2,default="105")
	class testObj3(manager):
		def __init__(self):
			pass
	o = testObj3()
	o.drop()
	d = {}
	d["selectValue"] = 3
	d["selectValue2"] = "108"
	o.insert(d)

	o.load()
	data = o.urlQuery()["data"] 
	assert len(data) == 1
	assert data[0]["selectValue"] == "科室3"
	assert data[0]["selectValue2"] == "智能8"
	
	data = o.urlQuery()
	#test layout
	l = data["layout"]
	assert l["width"] == "500px"
	assert l["split"] == 0
	o.drop()
	
	testSel3 = select(tableName="c_ycat_test",valueField="_id",nameField="name",parentValueField="ppid",parentId="selectValue",parentType=int)
	ii = testSel3.items("1") 
	assert 1 == len(ii)
	assert '101' == ii[0]["value"]
	assert "智能1" == ii[0]["label"] 
	o.drop()
	db.drop_table("c_ycat_test")

def testMeta():		
	@table("u_ycat_test2","测试数据2",layout=layout2())
	@field(id="_id",name="id",type=ObjectId,visible=False,readonly=True)
	@field(id="strValue",name="字符字段",type=str,editCtrl=input(placeholder="ycat test"),default="ycat111",readonly=True,visible=True,rules=[email(),hex(),require(message="hello ycat")])
	@field(id="dataValue",name="日期1",type=datetime.datetime,default=datetime.datetime(2018,4,11,15,5,41),rules=[url(),regex("\d*.*",message="hello ycat2")])
	@field(id="dataValue2",name="日期2",type=datetime.date,default=datetime.date(2018,4,11),rules=[require()])
	@field(id="dataValue3",name="日期3",type=datetime.time,default=datetime.time(15,5,41))
	@field(id="boolValue",name="布尔字段",type=bool,default=True)
	@field(id="passwordValue",name="密码字段",type=password,default="123456")
	class testObj2(manager):
		def __init__(self):
			pass 
			
	o = testObj2()
	o.drop()
	data = o.urlQuery()
	m = data["meta"]
	#test layout
	l = data["layout"]
	assert l["width"] == "900px"
	assert l["split"] == 1
	
	assert len(m[0]["rules"]) == 0
	e = m[1]["editCtrl"]
	assert e["type"] == "input"
	assert e["attr"]["placeholder"] == "ycat test"
	assert e["default"] == "ycat111"
	assert m[1]["name"] == "字符字段"
	assert m[1]["id"] == "strValue"
	assert m[1]["visible"] == True
	assert m[1]["readonly"] == True
	assert len(m[1]["rules"]) == 3
	assert m[1]["rules"][0]["message"] == "请输入正确的email地址"
	assert m[1]["rules"][0]["trigger"] == "blur"
	assert m[1]["rules"][0]["type"] == "email"
	assert m[1]["rules"][1]["message"] == "请输入正确的十六进制"
	assert m[1]["rules"][1]["type"] == "hex"
	assert m[1]["rules"][1]["trigger"] == "blur"
	assert m[1]["rules"][2]["message"] == "hello ycat"
	assert m[1]["rules"][2]["required"] == True 
	
	e = m[2]["editCtrl"]
	assert e["type"] == "datetimePicker" 
	assert e["default"] == "2018-04-11 15:05:41"
	assert m[2]["name"] == "日期1"
	assert m[2]["id"] == "dataValue" 
	assert len(m[2]["rules"]) == 2
	assert m[2]["rules"][0]["message"] == "请输入正确的URL地址"
	assert m[2]["rules"][0]["trigger"] == "blur"
	assert m[2]["rules"][0]["type"] == "url"
	assert m[2]["rules"][1]["message"] == "hello ycat2"
	assert m[2]["rules"][1]["type"] == "string"
	assert m[2]["rules"][1]["pattern"] == "\d*.*"
	assert m[2]["rules"][1]["trigger"] == "blur"
	
	e = m[3]["editCtrl"]
	assert e["type"] == "datePicker" 
	assert e["default"] == "2018-04-11"
	assert m[3]["name"] == "日期2"
	assert m[3]["id"] == "dataValue2"
	assert len(m[3]["rules"]) == 1
	assert m[3]["rules"][0]["message"] == "该字段为必选字段"
	assert m[3]["rules"][0]["required"] == True 
	
	e = m[4]["editCtrl"]
	assert e["type"] == "timePicker" 
	assert e["default"] == "15:05:41"
	assert m[4]["name"] == "日期3"
	assert m[4]["id"] == "dataValue3"
	assert len(m[4]["rules"]) == 0
	
	e = m[5]["editCtrl"]
	assert e["type"] == "switch"
	assert e["default"] == True
	assert m[5]["name"] == "布尔字段"
	assert m[5]["id"] == "boolValue"
	assert len(m[5]["rules"]) == 0
	
	e = m[6]["editCtrl"]
	assert e["type"] ==  "inputPassword" 
	assert e["default"] == "123456"
	assert m[6]["name"] == "密码字段"
	assert m[6]["id"] == "passwordValue"
	assert len(m[6]["rules"]) == 0
		
@table("u_ycat_test","测试数据",layout=layout2())
@field(id="_id",name="id",visible=False,readonly=True)
@field(id="strValue", name="字符字段", type=str, editCtrl=input(placeholder="ycat test"), default=None, rules=[url(),regex("\d+",message="hello ycat2")])
@field(id="intValue", name="整型字段", type=int, default=None, rules=[require()])
@field(id="floatValue", name="浮点字段", type=float, default=None, rules=[require()])
@field(id="dataValue", name="日期时间字段", type=datetime.datetime, default=None, rules=[])
@field(id="dataValue2",name="日期2",type=datetime.date,default=datetime.date(2018,4,11))
@field(id="dataValue3",name="日期3",type=datetime.time,default=datetime.time(15,5,41))
@field(id="boolValue", name="布尔字段", type=bool, default=None, rules=[require()])
@field(id="passwordValue", name="密码字段", type=password, default=None, rules=[email(),hex(),require(message="hello ycat")])
@field(id="selValue",name="选择字段",type=int,editCtrl=testSel1,default=2)
@field(id="listValue",name="列表字段",type=stringList,editCtrl=testSel2,default=["1","2"])
@timestampField()
class testObj1(manager):
	def __init__(self):
		pass

def testLoad():
	o = testObj1()
	o.drop()
	o.load()
	assert len(o.data) == 0
	info = {}
	info["strValue"] = "姚舜测试"
	info["intValue"] = 1000
	info["floatValue"] = 99.4
	now = utility.now()
	info["dataValue"] = now
	info["boolValue"] = True
	info["dataValue2"] = now.date()
	info["dataValue3"] = now.time()
	info["passwordValue"] = 123456
	info["selValue"] = 3
	info["listValue"] = ["2","3","4"]
	o.insert(info)
	o.load()
	assert len(o.data) == 1 
	assert utility.equal(utility.now() , o.data[0]["timestamp"] ,dateDiffSecond = 3)  
	
	info = {}
	info["strValue"] = "姚舜测试2"
	info["intValue"] = 1002
	info["floatValue"] = 299.4
	now2= now + datetime.timedelta(seconds=60*10)
	info["dataValue"] = now2
	info["dataValue2"] = now2.date()
	info["dataValue3"] = now2.time()
	info["boolValue"] = False
	info["selValue"] = 2
	info["passwordValue"] = 1234561
	info["listValue"] = ["3"]
	o.insert(info)
	d = o.get(info["_id"]) 
	assert len(d) == 12
	i = 0
	assert d[i]["label"] == "id" and d[i]["value"] == str(info["_id"])
	i += 1
	assert d[i]["label"] == "字符字段" and d[i]["value"] == "姚舜测试2"
	i += 1
	assert d[i]["label"] == "整型字段" and d[i]["value"] == "1002"
	i += 1
	assert d[i]["label"] == "浮点字段" and d[i]["value"] == "299.4"
	i += 1
	assert d[i]["label"] == "日期时间字段"  
	i += 1
	assert d[i]["label"] == "日期2"  
	i += 1
	assert d[i]["label"] == "日期3" 
	i += 1
	assert d[i]["label"] == "布尔字段" and d[i]["value"] == "NO"
	i += 1
	assert d[i]["label"] == "密码字段" 
	i += 1
	assert d[i]["label"] == "选择字段" and d[i]["value"] == "科室2"
	i += 1
	assert d[i]["label"] == "列表字段" and d[i]["value"] == "科室3"
	i += 1
	info = {}
	info["strValue"] = "姚舜测试3"
	info["intValue"] = 1003
	info["floatValue"] = 399.4
	now3= now + datetime.timedelta(seconds=60*30)
	info["dataValue"] = now3
	info["dataValue2"] = now3.date()
	info["dataValue3"] = now3.time()
	info["boolValue"] = True
	info["selValue"] = 1
	info["listValue"] = ["1"]
	o.insert(info)
	
	o.load()
	assert len(o.data) == 3
	d = o.data[0]
	assert "_id" in d
	assert d["strValue"] == "姚舜测试"
	assert d["intValue"] == 1000
	assert d["floatValue"] == 99.4
	assert utility.equal(d["dataValue"],now,dateDiffSecond=0.8)
	assert utility.equal(d["dataValue2"],datetime.datetime(now.date().year,now.date().month,now.date().day),dateDiffSecond=0.8)
	assert str(d["dataValue3"]) == str(now.time()).split(".")[0]
	assert d["listValue"] == ["2","3","4"]
	assert 3 == d["selValue"]
	assert utility.equal(utility.now() , o.data[0]["timestamp"] ,dateDiffSecond = 3)
	
	d = o.data[1]
	assert "_id" in d
	assert d["strValue"] == "姚舜测试2"
	assert d["intValue"] == 1002
	assert d["floatValue"] == 299.4
	assert utility.equal(d["dataValue"],now2,dateDiffSecond=0.8)
	assert utility.equal(d["dataValue"],now2,dateDiffSecond=0.8)
	assert utility.equal(d["dataValue2"],datetime.datetime(now2.date().year,now2.date().month,now2.date().day),dateDiffSecond=0.8)
	assert str(d["dataValue3"]) == str(now2.time()).split(".")[0]
	assert d["listValue"] == ["3"]
	assert 2 == d["selValue"]
	assert utility.equal(utility.now() , o.data[0]["timestamp"] ,dateDiffSecond = 3)
	
	qq = o.urlQuery()
	assert qq["title"] == "测试数据"
	m = qq["meta"]
	dd = qq["data"]
	assert 3 == len(dd)
	i = 0
	assert m[i]["id"] == "_id"
	assert m[i]["name"] == "id"
	assert m[i]["visible"] == False
	assert m[i]["readonly"] == True
	i = 1
	assert m[i]["id"] == "strValue"
	assert m[i]["name"] == "字符字段"
	assert m[i]["visible"] == True
	assert m[i]["readonly"] == False
	i = 2
	assert m[i]["id"] == "intValue"
	assert m[i]["name"] == "整型字段"
	assert m[i]["visible"] == True
	assert m[i]["readonly"] == False
	assert m[i]["editCtrl"]["default"] == 0
	i = 3
	assert m[i]["id"] == "floatValue"
	assert m[i]["name"] == "浮点字段"
	assert m[i]["visible"] == True
	assert m[i]["readonly"] == False
	assert m[i]["editCtrl"]["default"] == 0
	i = 4
	assert m[i]["id"] == "dataValue"
	assert m[i]["name"] == "日期时间字段"
	assert m[i]["visible"] == True
	assert m[i]["readonly"] == False	
	d = dd[0]
	assert "_id" in d
	assert d["strValue"] == "姚舜测试"
	assert d["intValue"] == 1000
	assert d["floatValue"] == 99.4
	assert d["selValue"] == "科室3"
	assert d["listValue"] == ["科室2","科室3","科室4"]
	assert utility.equal(d["dataValue"],now,dateDiffSecond=0.8)
	
	d = dd[1]
	assert "_id" in d
	assert d["strValue"] == "姚舜测试2"
	assert d["intValue"] == 1002
	assert d["floatValue"] == 299.4
	assert d["selValue"] == "科室2"
	assert d["listValue"] == ["科室3"]
	assert utility.equal(d["dataValue"],now2,dateDiffSecond=0.8)

def testunique():
	def getDomain1():
		return "test_ycat1"
	def getDomain2():
		return "test_ycat2"
	global getDomainFunc
	getDomainFunc = getDomain1
	@table("u_ycat_test_unique","测试数据",layout=layout2())
	@field(id="_id",name="id",visible=False,readonly=True)
	@field(id="strValue1", name="字符字段1", type=str,unique=True)
	@field(id="strValue2", name="字符字段2", type=str,unique=["strValue3"])
	@field(id="strValue3", name="字符字段3", type=str)
	class testObj3(manager):
		def __init__(self):
			pass
	o = testObj3()
	o.drop()
	data={}
	data["strValue1"] = "1"
	data["strValue2"] = "2"
	data["strValue3"] = "3"
	o.insert(data)
	id = data["_id"]
	assert 1 == len(o.load())
	data={}
	data["strValue1"] = "1" #1重复
	data["strValue2"] = "22"
	data["strValue3"] = "33"
	try:
		o.insert(data)
		assert 0
	except Exception as e:
		assert str(e).find("字符字段1") != -1 
		
	data={}
	data["strValue1"] = "11"
	data["strValue2"] = "2" #2,3重复
	data["strValue3"] = "3"
	try:
		o.insert(data)
		assert 0
	except Exception as e:
		assert str(e).find("字符字段2") != -1
	
	data={}
	data["strValue1"] = "11"
	data["strValue2"] = "2" #2,3重复
	data["strValue3"] = "3"
	try:
		o.insert(data)
		assert 0
	except Exception as e:
		assert str(e).find("字符字段2") != -1
	assert 1 == len(o.load())
	
	#test update 
	data={}
	data["strValue1"] = "1.1"
	data["strValue2"] = "2.1"
	data["strValue3"] = "3.1"
	id2 = o.insert(data)
	
	data={}
	data["strValue1"] = "1" #1重复 
	data["strValue2"] = "22" 
	data["strValue3"] = "33"
	o.update(id,data)

	try:
		o.update(id2,data)
		assert 0
	except Exception as e:
		assert str(e).find("字符字段1") != -1
	data={}
	data["strValue1"] = "11"
	data["strValue2"] = "2"  #2,3重复
	data["strValue3"] = "3"
	o.update(id,data)
	
	data={}
	data["strValue1"] = "11" #1重复
	data["strValue2"] = "2" 
	data["strValue3"] = "3"
	try:
		o.update(id2,data)
		assert 0
	except Exception as e:
		assert str(e).find("字符字段1") != -1
	
	data={}
	data["strValue1"] = "1"
	data["strValue2"] = "2"  #2,3重复
	data["strValue3"] = "3"
	try:
		o.update(id2,data)
		assert 0
	except Exception as e: 
		assert str(e).find("字符字段2") != -1
	
	data["strValue1"] = "111"
	data["strValue2"] = "222"  
	data["strValue3"] = "333"
	o.update(id,data)
	
	#仅2重复 
	data={}
	data["strValue1"] = "1111"
	data["strValue2"] = "222"
	data["strValue3"] = "3332"
	o.insert(data)
	assert 3 == len(o.load())
	
	getDomainFunc = getDomain2
	#domain不一样
	data={}
	data["strValue1"] = "1"
	data["strValue2"] = "2" 
	data["strValue3"] = "3"
	o.insert(data)
	getDomainFunc = None
	assert 4 == len(o.load())
	o.drop()
	
def testDomain():
	import re
	def getDomain1():
		return "test_ycat1"
	def getDomain2():
		return "test_ycat2"
	def getDomain():
		return ""
	db.delete_many("u_domain",{"_id":re.compile("^test")}) 
	db.insert("u_domain",{"_id":"test_ycat1","name":"测试域1"})
	db.insert("u_domain",{"_id":"test_ycat2","name":"测试域2"})

	global getDomainFunc
	getDomainFunc = getDomain2
	
	@table("u_ycat_test31","测试数据3")
	@field(id="_id",name="id",visible=False,readonly=True)
	@field(id="strValue1", name="字符字段1", type=str)
	@field(id="strValue2", name="字符字段2", type=str)
	class testObj3(manager):
		def __init__(self):
			pass
	getDomainFunc = getDomain1

	obj = testObj3()
	obj.drop()
	data = {}
	data["strValue1"] = "strValue11"
	data["strValue2"] = "strValue22"
	id1 = obj.insert(data)
	getDomainFunc = getDomain2
	qq = obj.urlQuery()
	m = qq["meta"]
	assert 3 == len(m)
	data = {}
	data["strValue1"] = "strValue12"
	data["strValue2"] = "strValue23"
	id2 = obj.insert(data)
	ds = db.find("u_ycat_test31").list()
	assert 2 == len(ds)
	assert str(ds[0]["_id"]) == str(id1)
	assert ds[0]["strValue1"] == "strValue11"
	assert ds[0]["strValue2"] == "strValue22"
	assert ds[0]["domain"] == "test_ycat1"
	assert str(ds[1]["_id"]) == str(id2)
	assert ds[1]["strValue1"] == "strValue12"
	assert ds[1]["strValue2"] == "strValue23"
	assert ds[1]["domain"] == "test_ycat2"
	
	ds = obj.query()
	assert len(ds) == 1
	assert str(ds[0]["_id"]) == str(id2)
	assert ds[0]["strValue1"] == "strValue12"
	assert ds[0]["strValue2"] == "strValue23"
#	assert ds[0]["domain"] == "test_ycat2"
	getDomainFunc = getDomain1
	qq = obj.urlQuery()
	m = qq["meta"]
	assert 3 == len(m)
	
	ds = obj.query()
	assert len(ds) == 1
	assert str(ds[0]["_id"]) == str(id1)
	assert ds[0]["strValue1"] == "strValue11"
	assert ds[0]["strValue2"] == "strValue22"
#	assert ds[0]["domain"] == "test_ycat1"
	getDomainFunc = getDomain
	ds = obj.query()
	assert 2 == len(ds)
	assert str(ds[0]["_id"]) == str(id1)
	assert ds[0]["strValue1"] == "strValue11"
	assert ds[0]["strValue2"] == "strValue22"
#	assert ds[0]["domain"] == "test_ycat1"
	assert str(ds[1]["_id"]) == str(id2)
	assert ds[1]["strValue1"] == "strValue12"
	assert ds[1]["strValue2"] == "strValue23"
#	assert ds[1]["domain"] == "test_ycat2"
	qq = obj.urlQuery()
	m = qq["meta"]
	assert 4 == len(m)
	db.delete_many("u_domain",{"_id":re.compile("^test")}) 
	obj.drop()
		
def testpopup():
	@table("u_ycat_test33","测试数据3",domain=False)
	@field(id="_id",name="id",visible=False,readonly=True)
	@field(id="aa", name="字符字段1", type=str)
	@field(id="bb", name="字符字段2", type=str)
	class testObj3(manager):
		def __init__(self):
			pass
		
	@table("u_ycat_test34","测试数据4",domain=False)
	@field(id="_id",name="id",visible=False,readonly=True)
	@field(id="cc", name="字符字段1", type=str,style=[popup("u_ycat_test33")])
	@field(id="dd", name="字符字段2", type=str,style=[redirect("/ycat"),styleClass()])
	class testObj4(manager):
		def __init__(self):
			pass
		def getClassStyle(self,row,fieldId):
			return row[fieldId]
			
	o1 = testObj3()
	o2 = testObj4()
	o1.drop()
	o2.drop()
	data = {}
	data["aa"] = "ycat1"
	data["bb"] = "姚舜测试1"
	id1 = o1.insert(data)
	data = {}
	data["aa"] = "ycat2"
	data["bb"] = "姚舜测试2"
	id2 = o1.insert(data)
	data = {}
	data["cc"] = str(id1)
	data["dd"] = str(id1)
	o2.insert(data)
	data = {}
	data["cc"] = str(id2)
	data["dd"] = str(id2)
	o2.insert(data)
	qq = o2.urlQuery()
	m = qq["meta"] 
	assert m[1]["styleCtrl"]["popup"] 
	assert "redirect" not in m[1]["styleCtrl"] 
	assert "class" not in m[1]["styleCtrl"]
	assert "popup" not in m[2]["styleCtrl"] 
	assert  m[2]["styleCtrl"]["redirect"] 
	assert m[2]["styleCtrl"]["class"] 
	dd = qq["data"]
	assert dd[0]["@redirect"] == {"dd":["/ycat?id="+str(id1)]}
	assert dd[0]["@popup"] == {"cc":['/api/common/detail?table=u_ycat_test33&id=' +str(id1)]}
	assert dd[1]["@redirect"] == {"dd":["/ycat?id="+str(id2)]}
	assert dd[1]["@popup"] == {"cc":['/api/common/detail?table=u_ycat_test33&id=' +str(id2)]}
	assert dd[0]["@class"] == {"dd":str(id1)}
	assert dd[1]["@class"] == {"dd":str(id2)}
	o1.drop()
	o2.drop()
	
		
if __name__ == '__main__':
	utility.run_tests()
	#testDomain()
	#import webutility
	#webutility.run(port=8999)

	


	
	
	
	
	
	
	
	
	
	
	
	