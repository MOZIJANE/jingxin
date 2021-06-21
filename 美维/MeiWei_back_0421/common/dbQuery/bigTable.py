#coding=utf-8
# ycat			2018-04-10	  create
# 带分页的大数据查询
# 自定义表：可参见monitor/main_monitor.py 
# 常规用法：可参见rlog/main_rlog.py
import sys,os
import re
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import datetime
import utility
import mongodb as db
import scadaUtility
import json_codec
import bottle
import webutility
import pymongo 
import meta
import dbQuery.dateRange
import xlwt
	
def _checkCls(cls):
	global g_metaData
	if cls not in g_metaData:
		c = utility.empty_class()
		c.tableName = ""	
		c.urlName = ""	
		c.idType = db.ObjectId
		c.filter = {}		
		c.sort = None		
		c.fields = []
		c.fieldDict = {} 
		c.leftjoin = None 
		c.exportExcel = True
		g_metaData[cls] = c 
	 
class style:
	def __init__(self):
		pass
 
#弹出详细信息 	
#tableName: 对应的数据库表名，必须要是配有对应有meta类型 
popup = meta.popup  
		
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
	
#提供leftjoin操作  
#进行左连接操作,localField代表本地的ID，table为外键的表，foreignField为外键表的列名
#生成的列名为 table.xxx
#注意：leftjoin出来的字段，是无法进行过滤的  
def leftjoin(table,selectColumn,localField,foreignField="_id"):
	def __call(cls):
		global g_metaData
		_checkCls(cls)
		o = utility.empty_class()
		o.table = table
		o.localField = localField
		o.foreignField = foreignField
		o.selectColumn = selectColumn
		g_metaData[cls].leftjoin = o
		return cls
	return __call		

#配置字段的属性 	
# sortable：是否支持排序
# searchable：是否支持模糊查找，仅支持字符串类型 
# style：可以为[str]代表支持配置不同的class，或者为redirect、popup代表可以跳转 
# formatFunc：用于格式化，def format(value)
def field(id, name,searchable=True,sortable=True,style=None,formatFunc=None,visible=True):
	def __call(cls):		
		global g_metaData
		c = utility.empty_class() 
		# c.id = id.replace(".","#") #js不支持.操作 
		c.id = id
		c.name = name
		c.style = style
		c.styleDict = {}
		c.searchable = searchable
		c.sortable = sortable
		c.formatFunc = formatFunc
		c.visible = visible
		if style:
			for s in style:
				if isinstance(s,redirect):
					if "redirect" not in c.styleDict:
						c.styleDict["redirect"] = s.dict
				elif isinstance(s,popup): 
					if "popup" not in c.styleDict:
						c.styleDict["popup"] = {"url":s.urlStr,"id": s.foreignId}
				#elif isinstance(s,styleClass):
				#	c.styleDict["class"] = s 
		_checkCls(cls)
		g_metaData[cls].fields.insert(0,c)
		g_metaData[cls].fieldDict[c.id] = c
		if id == "_id":
			g_metaData[cls].idType = type
		return cls
	return __call	
 
#dateRangeField：为需要时间过滤的字段，为空代表没有时间过滤   
#urlName：为url表名的别名，这样多个bigtable显示一个表 
#exportExcel：为是否导出到excel表 
def table(tableName,title,dateRangeField,domain=True,defaultSortId=None,defaultSortDir=None,urlName="",exportExcel=True):
	install()
	if not urlName:
		urlName = tableName
			
	def __call(cls):
		global g_metaData,g_objData 
		_checkCls(cls)
		g_metaData[cls].tableName = tableName
		g_metaData[cls].urlName = urlName
		g_metaData[cls].title = title
		g_metaData[cls].domain = domain
		g_metaData[cls].dateRangeField = dateRangeField
		g_metaData[cls].defaultSortId = defaultSortId
		g_metaData[cls].defaultSortDir = defaultSortDir
		g_metaData[cls].exportExcel = exportExcel
		g_objData[urlName] = cls() 
		if defaultSortDir:
			assert defaultSortDir == "asc" or defaultSortDir == "desc"  
		return cls
	return __call	
		
g_metaData = {}	
g_objData = {}	

class manager:
	def __init__(self):
		pass
 
	def _domainFilter(self,filter):
		if meta.getDomainFunc and self._meta.domain:
			d = meta.getDomainFunc()
			if len(d):
				#空domain代表所有的domain都支持 
				if "domain" in filter:
					raise Exception("getDomainFunc和filter里的domain冲突")
				filter["domain"] = d
		return filter
		
	@property
	def _meta(self):
		if not hasattr(self,"__meta"):
			self.__meta = g_metaData[type(self)] 
		mm = self.__meta
		
		#动态增加删除域 
		if mm.domain:
			id = "domain"
			if meta.getDomainFunc and len(meta.getDomainFunc()) == 0:
				#domain为空时(即admin)的编辑和查询页面不一样的	
				if id not in mm.fieldDict:
					field(id=id, name="域")(type(self))
			else:
				if id in mm.fieldDict and meta.getDomainFunc:
					del mm.fieldDict[id]
					assert mm.fields[0].id == id
					del mm.fields[0]
		return mm
		
	def _metaData(self):
		mm = []
		for f in self._meta.fields:
			m = {}
			m["id"] = f.id.replace(".","#") #js不支持.操作 
			m["name"] = f.name
			m["sortable"] = f.sortable
			m["searchable"] = f.searchable 
			m["visible"] = f.visible
			if f.style is not None: 
				m["styleCtrl"] = f.styleDict	
			mm.append(m)
		return mm
	
	#重载此函数，用于返回不同的class 
	def getClassStyle(self,row,fieldId):
		assert 0 #如果配置了style的styleClass必须要重载这个函数 
		return [] 
		
				
	#current是以1为开始
	#pageSize为-1代表不分页 
	def urlQuery(self,pageSize,current,sortId,sortDir,filter=""): 
		assert pageSize
		assert current > 0
		cond = {}
		if filter:
			conds = []
			for f in self._meta.fields:
				if not f.searchable:
					continue
				conds.append({f.id:re.compile(".*"+filter+".*")})
			if len(conds) == 1:
				cond = conds[0]
			elif len(conds) != 0:
				cond = {"$or":conds}
		cond = self._domainFilter(cond)
		if self._meta.dateRangeField:
			cond = dbQuery.dateRange.getFilter(datetimeField=self._meta.dateRangeField,filter=cond)
		cols = list(self._meta.fieldDict.keys())
		if self._meta.leftjoin is not None:
			if self._meta.leftjoin.localField not in cols:
				cols.append(self._meta.leftjoin.localField)
		
		ds = self.queryData(self._meta.tableName, cond,columns=cols)   
		total = ds.count
		
		if total != -1:
			#aggregate结果就是-1 
			current -= 1 
			if current * pageSize > total:
				current = int(total / pageSize)
			if not sortId:
				sortId = self._meta.defaultSortId
				sortDir = self._meta.defaultSortDir
			if sortId:
				assert sortDir == "asc" or sortDir == "desc"
				if sortDir == "asc":
					dir = db.ASCENDING
				else:
					dir = db.DESCENDING
				ds = ds.sort(sortId,dir)
			
			if pageSize > 0: 
				if current > 0:
					ds = ds.skip(current*pageSize)
				ds = ds.limit(pageSize)
		
		if self._meta.leftjoin is not None:
			l = self._meta.leftjoin
			#js不支持.操作，所以用#代替 
			ds.leftjoin(l.localField,l.table,l.foreignField,l.selectColumn,join_str="#")
			
		data = ds.list()  
		self.updateData(data)
		for d in data:
			for n in d:
				if n in self._meta.fieldDict and self._meta.fieldDict[n].formatFunc:
					d[n] = self._meta.fieldDict[n].formatFunc(d[n])
					continue
				if isinstance(d[n],datetime.datetime):
					d[n] = utility.date2str(d[n])
				else:
					d[n] = str(d[n])  
		
		#self._updateStyle(data)
		page = {}
		page["current"] = current+1
		page["pageSize"] = pageSize
		page["total"] = total
		page["sort"] = {"id":sortId,"dir":sortDir}	 
		return {"title":self._meta.title,"meta":self._metaData(),"exportExcel":self._meta.exportExcel,"data":data,"page":page}	
		
	#重启这个函数进行数据更新  
	def updateData(self,data):
		return data
		
	def queryData(self,tableName, cond,columns):
		return db.find(tableName, cond,columns=columns)  
		
		 
def _urlManage(): 
	table = webutility.get_param("table")
	current = webutility.get_param("current",1)
	pageSize = webutility.get_param("pageSize",100)
	sortId = webutility.get_param("sortId","")
	sortDir = webutility.get_param("sortDir","asc")
	filter = webutility.get_param("searchText","")
	
	global g_objData
	return g_objData[table].urlQuery(pageSize=pageSize,current=current,sortId=sortId,sortDir=sortDir,filter=filter)

def _urlExport(): 
	table = webutility.get_param("table")
	current = webutility.get_param("current",1)
	pageSize = -1 #不分页 
	sortId = webutility.get_param("sortId","")
	sortDir = webutility.get_param("sortDir","asc")
	filter = webutility.get_param("searchText","")
	
	global BASE_PATH
	global g_objData
	data = g_objData[table].urlQuery(pageSize=pageSize,current=current,sortId=sortId,sortDir=sortDir,filter=filter)
	filename = _writeExcel(BASE_PATH,data["title"],[x["name"] for x in data["meta"]],[x["id"] for x in data["meta"]],[x["visible"] for x in data["meta"]],data["data"])
	return {"path":"/static/download/"+filename}
	
#下载文件地址 
BASE_PATH = os.path.abspath(os.path.dirname(__file__)+"/../../vue/dist") + "/static/download/"

def _writeExcel(path,title,fields,fieldsId,visiables,data): 
	#https://www.cnblogs.com/MrLJC/p/3715783.html 
	t = utility.date2str(utility.now())
	t = t.replace("-","")
	t = t.replace(" ","")
	t = t.replace(":","")
	workbook = xlwt.Workbook(encoding = 'ascii')
	sheet = workbook.add_sheet(title)
	
	font = xlwt.Font() 		# Create the Font
	font.name = 'Times New Roman'
	font.bold = True 
	style = xlwt.XFStyle() 	# Create the Style
	style.font = font 		# Apply the Font to the Style
	i = 0
	for f,v in zip(fields,visiables):
		if v:
			sheet.write(0, i, label =f, style= style)
			sheet.col(i).width = 3333*2
			i+=1
	for i,row in enumerate(data): 
		colIndex = 0
		for cell,v in zip(fieldsId,visiables):
			if v: 
				sheet.write(i+1, colIndex, label=row[cell]) 
				colIndex += 1
	fileName = utility.md5(title+"_"+t)+".xls"
	workbook.save(path+fileName)
	return fileName
	
g_installModule = set()

def install(n=None):
	global g_installModule
	if n is None:
		n = utility.app_name()
	if n not in g_installModule:
		g_installModule.add(n)
		scadaUtility.add("/api/"+n+"/bigtable",_urlManage)
		scadaUtility.add("/api/"+n+"/bigtable/export",_urlExport)

################### unit test 	################### 
def testleft():	
	@table("r_ycat_bigtable2","左连接测试",dateRangeField=None)
	@leftjoin("r_ycat_leftjoin",["name"],"strfield1","_id")
	@field("_id","ID",searchable=True)
	@field("strfield1","字符串1",searchable=True)
	@field("strfield2","字符串2",searchable=True)  
	@field("r_ycat_leftjoin.name","字符串3",searchable=True)  
	class testBig2(manager):
		pass
	db.drop_table("r_ycat_bigtable2")
	db.drop_table("r_ycat_leftjoin")
	o = testBig2()
	now = datetime.datetime(2018,6,14,9,44,35)
	dtList = []
	for i in range(20):
		data = {}
		data["strfield1"] = str(i%5)
		data["strfield2"] = "软件测试字符串"+str(i)   
		db.insert("r_ycat_bigtable2",data)
	for i in range(5):
		data = {}
		data["_id"] = str(i%5)
		data["name"] = "name"+str(i%5)
		db.insert("r_ycat_leftjoin",data)
	data = o.urlQuery(pageSize=300,current=1,sortId=None,sortDir=None,filter=None)
	assert 20 == len(data["data"])
	for i in range(20):
		assert data["data"][i]["strfield1"] ==  str(i%5)
		assert data["data"][i]["strfield2"] == "软件测试字符串"+str(i)   
		assert data["data"][i]["r_ycat_leftjoin#name"] == "name"+ str(i%5)
	name = _writeExcel("./",data["title"],[x["name"] for x in data["meta"]],[x["id"] for x in data["meta"]],[False,True,True,True],data["data"]) 
	os.remove("./"+name)
	db.drop_table("r_ycat_bigtable2")
	db.drop_table("r_ycat_leftjoin")
	
def testsearch():
	webutility.set_test_param("dateRangeLastSec",None)
	webutility.set_test_param("dateRangeType","dates") 
	webutility.set_test_param("dateRangeStart","2000-06-19T00:00:00.000Z") 
	webutility.set_test_param("dateRangeEnd","2020-06-19T23:59:59.999Z") 
	
	
	@table("r_ycat_bigtable2","分表表格测试2",dateRangeField="datefield")
	@field("_id","ID",searchable=True)
	@field("strfield1","字符串1",searchable=True)
	@field("strfield2","字符串2",searchable=True) 
	@field("intfield","整形字段",searchable=True)
	@field("datefield","日期字段",searchable=True)
	class testBig2(manager):
		pass
	db.drop_table("r_ycat_bigtable2")

	o = testBig2()
	now = datetime.datetime(2018,6,14,9,44,35)
	dtList = []
	for i in range(199):
		data = {}
		data["strfield1"] = "姚舜测试字符串"+str(i)
		data["strfield2"] = "软件测试字符串"+str(i)
		data["intfield"] = 1000 + i
		data["datefield"] = now + datetime.timedelta(hours=i)
		dtList.append(utility.date2str(data["datefield"]))
		db.insert("r_ycat_bigtable2",data)
	data = o.urlQuery(pageSize=300,current=1,sortId=None,sortDir=None,filter="姚舜")["data"]
	assert 199 == len(data)
	data = o.urlQuery(pageSize=300,current=1,sortId=None,sortDir=None)["data"]
	assert 199 == len(data)
	
	
	data = o.urlQuery(pageSize=300,current=1,sortId=None,sortDir=None,filter="姚舜测试字符串100")["data"]
	assert 1 == len(data)
	assert data[0]["strfield1"] == "姚舜测试字符串100"
	assert data[0]["intfield"] == '1100'
	assert dtList[100] == data[0]["datefield"]
	data = o.urlQuery(pageSize=300,current=1,sortId=None,sortDir=None,filter="软件测试字符串99")["data"]
	assert 1 == len(data)
	assert data[0]["strfield1"] == "姚舜测试字符串99"
	assert data[0]["intfield"] == '1099'
	
	#test _writeExcel
	data = o.urlQuery(pageSize=300,current=1,sortId=None,sortDir=None)
	assert 199 == len(data["data"])
	name = _writeExcel("./",data["title"],[x["name"] for x in data["meta"]],[x["id"] for x in data["meta"]],[False,True,True,True,True],data["data"]) 
	import xlrd
	ee =  xlrd.open_workbook("./"+name)
	sheet = ee.sheets()[0]
	nrows = sheet.nrows 
	assert 200 == nrows
	assert sheet.row_values(0)[0] == "字符串1"
	assert sheet.row_values(0)[1] == "字符串2"
	assert sheet.row_values(0)[2] == "整形字段"
	assert sheet.row_values(0)[3] == "日期字段"
	for i in range(0,nrows-1):
		assert sheet.row_values(i+1)[0] == "姚舜测试字符串"+str(i)
		assert sheet.row_values(i+1)[1] == "软件测试字符串"+str(i)
		assert sheet.row_values(i+1)[2] == str(1000 + i)
		assert sheet.row_values(i+1)[3] == utility.date2str(now + datetime.timedelta(hours=i))
	os.remove("./"+name)
	db.drop_table("r_ycat_bigtable2")
	
	
def test1():
	@table("r_ycat_bigtable1","分表表格测试",dateRangeField="datefield")
	@field("_id","ID")
	@field("strfield","字符串")
	@field("listfield","列表字段")
	@field("objfield","对象列表字段")
	@field("intfield","整形字段")
	@field("datefield","日期字段")
	class testBig(manager):
		pass
	db.drop_table("r_ycat_bigtable1")
	o = testBig()
	now = datetime.datetime(2018,6,14,9,44,35)
	for i in range(199):
		data = {}
		data["strfield"] = "姚舜测试字符串"+str(i)
		data["listfield"] = [x+i for x in range(10)]
		data["objfield"] = [ {"v1":x+i,"v2":str(x)} for x in range(10)]
		data["intfield"] = 1000 + i
		data["datefield"] = now + datetime.timedelta(hours=i)
		db.insert("r_ycat_bigtable1",data)
	mm = o.urlQuery(pageSize=30,current=1,sortId=None,sortDir=None)
	assert mm["title"] == "分表表格测试"
	p = mm["page"]
	assert p["total"] == 199
	assert p["current"] == 1
	assert p["sort"]["id"] is None
	assert p["sort"]["dir"] is None
	dd = mm["data"]
	assert 30 == len(dd)
	i = 0
	for d in dd:
		assert d["strfield"] == "姚舜测试字符串"+str(i)
		assert d["listfield"] == str([x+i for x in range(10)])
		assert d["objfield"] == str([ {"v1":x+i,"v2":str(x)} for x in range(10)])
		assert d["intfield"] == str(1000 + i)
		assert d["datefield"] == str(utility.date2str(now + datetime.timedelta(hours=i)))
		i+=1
		
	#sort 
	mm = o.urlQuery(pageSize=30,current=8,sortId="intfield",sortDir="asc")
	assert mm["title"] == "分表表格测试"
	p = mm["page"]
	assert p["total"] == 199
	assert p["current"] == 7
	assert p["sort"]["id"] == "intfield"
	assert p["sort"]["dir"] == "asc"
	dd = mm["data"]
	assert 19 == len(dd)
	i = 180
	for d in dd:
		assert d["strfield"] == "姚舜测试字符串"+str(i)
		assert d["listfield"] == str([x+i for x in range(10)])
		assert d["objfield"] == str([ {"v1":x+i,"v2":str(x)} for x in range(10)])
		assert d["intfield"] == str(1000 + i)
		assert d["datefield"] == str(utility.date2str(now + datetime.timedelta(hours=i)))
		i+=1
		
	#sort 
	mm = o.urlQuery(pageSize=200,current=8,sortId="intfield",sortDir="desc")
	assert mm["title"] == "分表表格测试"
	p = mm["page"]
	assert p["total"] == 199
	assert p["current"] == 1
	assert p["sort"]["id"] == "intfield"
	assert p["sort"]["dir"] == "desc"
	dd = mm["data"]
	assert 199 == len(dd)
	
	#sort 
	mm = o.urlQuery(pageSize=50,current=2,sortId="intfield",sortDir="desc")
 
	assert mm["title"] == "分表表格测试"
	p = mm["page"]
	assert p["total"] == 199
	assert p["current"] == 2
	assert p["sort"]["id"] == "intfield"
	assert p["sort"]["dir"] == "desc"
	dd = mm["data"]
	
	assert 50 == len(dd)
	db.drop_table("r_ycat_bigtable1") 
	
if __name__ == '__main__':
	utility.run_tests() 
	


	
	
	
	
	
	
	
	
	
	
	
	