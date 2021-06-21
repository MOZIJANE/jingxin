#coding=utf-8 
# ycat			 2015/11/17      create
#实时曲线图： 可参见monitor/main_monitor.py例子 
#饼图的例子：可参见rlog/dbscript.xml 
import sys,os
import datetime
import xml.etree.ElementTree as xml
import re
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import webutility
import utility
import mongodb as db  
import json_codec
import log
import dbQuery.dateRange as dateRange
import counter 

class query:
	def __init__(self,nodeText,globalVars={}):
		if isinstance(nodeText,str):
			node = xml.fromstring(nodeText)
		else:
			node=nodeText
		self._no_datagroup = False
		self.name = node.attrib["name"] 
		self._decodeEcharts(node)
		 
		self.collection = node.attrib["collection"]
		
		if "dateField" in node.attrib:
			self.dateField = node.attrib["dateField"]
		else:
			self.dateField =  ""
		
		if "out_collection" in node.attrib:
			self.out_collection = node.attrib["out_collection"]
		else:
			self.out_collection =  ""
		self.variables = []
		self.globalVars = globalVars
		self.type = None
		
		self.url = ""
		nn = node.find("bottle")
		if nn is not None:
			self.url = nn.attrib["url"]
		
		nn = node.findall("bottle/variable")
		for v in nn:
			t = v.attrib["name"].strip()
			assert t not in self.variables
			self.variables.append(t)
		
		tt = ["mongo.aggregate","mongo.map-reduce","mongo.find"]
		for t in tt:
			na = node.find(t)
			if na is not None:
				self.xmlText = xml.tostring(na, encoding="utf-8").decode("utf-8")
				self.type = t
				break
		if not self.type:
			raise Exception("query: Can't find type node")
			
	@staticmethod	
	def _add_pipe(pipe,tag,text):
		if text is None:
			text = ""
		else:
			text = text.strip()
		if tag == "limit":
			r = int(text)
		else: 
			#if text[0] != '{':
			#	text = "{" + text + "}"
			try:
				text = text.replace('\'', '"')
				r = json_codec.load(text)
			except ValueError as e:
				log.error("decode",tag,"failed")
				raise Exception("decode json error:",text)
		pipe.append({"$"+tag:r})
		return pipe
	 
	@counter.count
	def run(self,**variables):
		start = utility.ticks()
		log.debug("Query start",self.name)
		if self.out_collection:
			db.drop_table(self.out_collection)
			
		if self.type == "mongo.aggregate":
			result = self._run_mongo_aggregate(**variables)
		elif self.type == "mongo.map-reduce":
			result = self._run_mongo_mr(**variables)
		elif self.type == "mongo.find":
			result = self._run_mongo_find(**variables)
		else:
			assert 0 
		if utility.ticks() - start > 3000:
			log.info("Query finish`",self.name + "` count=" + str(result.count) + " time=",str((utility.ticks() - start)/1000.0)+"s")
		return result
		
	def _run_mongo_find(self,**variables):
		pipe = []
		text = self._replace_variables(**variables)
		node = xml.fromstring(text) 
		columns = set()
		conds = {}
		sorts = []
		limit = 0
		skip = 0
		
		#自动添加时间过滤器 
		dateRange.getFilter(self.dateField,conds)

		for n in node.getchildren():
			if n.tag == "column":
				assert n.tag not in columns
				columns.add(n.text)
			elif n.tag == "cond":
				p = []
				query._add_pipe(p,n.tag,n.text)
				data = p[0]["$cond"]
				for n in data:
					assert n not in conds
				conds.update(data)
			elif n.tag == "limit":
				limit = int(n.text)
			elif n.tag == "skip":
				skip = int(n.text)
			elif n.tag == "sort":
				text = n.text
				if text[0] != '{':
					text = "{" + text + "}" 
				r = json_codec.load(text)
				sorts.append(r)
		c = list(columns)
		if len(c) == 0:
			c = None
		
		ds = db.find(self.collection,conds,columns=c)
		if sorts:
			for ss in sorts:
				for s in ss:
					ds = ds.sort(s,ss[s])
		if skip:
			ds = ds.skip(skip)
			
		if limit:
			ds = ds.limit(limit)
			
		if self.out_collection and ds.count:
			ll = ds.list()
			if ll:
				db.insert_many(self.out_collection,ll)
		return ds
	
	def _dateRange(self,pipe,text):
		assert self.dateField
		group = {}
		data = json_codec.load(text)
		group["_id"] = { "dateRange": "$"+self.dateField}
		if "_id" in data and data["_id"]:
			if isinstance(data["_id"],dict):
				group["_id"].update(data["_id"])
			else:
				v = data["_id"]
				if v[0] != "$":
					v = "$" + v
				group["_id"]["key"] = v
			del data["_id"]
		group.update(data)
		pipe.append({"$group":group})
		pipe.append({"$sort":{"_id":1}})
	
	def _dateRangeGroup(self,pipe,text):
		assert self.dateField #有dateRangeGroup字段，在xml文件中这个必有要配上 
		group = {}
		data = json_codec.load(text)
		group["_id"] = { "dateRange":dateRange.getGroupOp(self.dateField)}
		idName = "_id.dateRange" 
		if "_id" in data and data["_id"]:
			if isinstance(data["_id"],dict):
				group["_id"].update(data["_id"])
			else:
				v = data["_id"]
				if v[0] != "$":
					v = "$" + v
				group["_id"]["key"] = v
			del data["_id"]
			
		group.update(data)
		pipe.append({"$group":group})
		if dateRange.getType() == "week":
			#进行星期的转换，mongodb的星期范围是between 1 (Sunday) and 7 (Saturday)，所以要加1，再换成中文 
			cond = { "$cond":  [ {"$eq":["$"+idName,1]}, 8, "$_id.dateRange"] }
			pipe.append({"$addFields":{idName:cond}})
			pipe.append({"$sort":{"_id":1}})
			pipe.append({"$addFields":{idName:{"$arrayElemAt":[["异常1","异常2","周一","周二","周三","周四","周五","周六","周日"],"$_id.dateRange"]}}})
		else: 
			pipe.append({"$sort":{"_id":1}})
		return pipe
		
	def _leftjoin(self,pipe,node):
		#select:为连接表的字段，用逗号分隔 
		#from:  为连接表名
		#localField: 主表的字段名
		#foreignField: 连接表的字段名  
		#<leftjoin select="" from="" localField="" foreignField=""></leftjoin>
		table = node.attrib["from"]
		foreignField = node.attrib["foreignField"]
		localField = node.attrib["localField"]
		fields = [ x.strip() for x in node.attrib["select"].split(",") ]
		let = {"localField":"$"+localField}
		project = {"_id":0}
		for f in fields:
			project[f] = 1
			
		match = {"$match": {"$expr": {"$eq": [ "$"+foreignField, "$$"+"localField" ]}}}
		lookup = {"from": table,"let":let,"pipeline":[match,{"$project":project}],"as":table}
		addFields = {"$addFields": {table:{ "$arrayElemAt": ["$"+table, 0 ] }} } 
		pipe.append({"$lookup":lookup})
		#把队列变成单个文档 
		pipe.append(addFields) 
		return pipe
		
	def _run_mongo_aggregate(self,**variables):
		pipe = []
		text = self._replace_variables(**variables)
		node = xml.fromstring(text)
		#自动添加时间过滤器 
		filter = dateRange.getFilter(self.dateField,{})
		if filter:
			pipe.append({"$match":filter})
		
		hasDateRangeGroup = False
		for p in node.getchildren():
			if p.tag == "dateRangeGroup":
				self._no_datagroup = False
				self._dateRangeGroup(pipe,p.text)
			elif p.tag == "dateRange":
				self._no_datagroup = True
				self._dateRange(pipe,p.text)
			elif p.tag == "leftjoin":
				self._leftjoin(pipe,p)
			else:
				query._add_pipe(pipe,p.tag,p.text)

		if self.out_collection:
			self.pipe.append({"$out":self.out_collection})
		#print(pipe,"--------")
		return db.aggregate(self.collection,pipe)

	def _run_mongo_mr(self,**variables): 
		text = self._replace_variables(**variables) 
		node = xml.fromstring(text)
		map = None
		reduce = None
		param = {}
		for n in node.getchildren():
			if n.tag == "map":
				map = n.text.strip(";")
			elif n.tag == "reduce":	
				reduce = n.text.strip(";")
			elif n.tag == "finalize":
				param["finalize"] = n.text.strip(";")
			else:
				p = []
				query._add_pipe(p,n.tag,n.text)
				param[n.tag] = p[0]["$"+n.tag]
		if not map:
			raise Exception("query: Can't find map function")
		if not reduce:
			raise Exception("query: Can't find reduce function")
		
		#自动添加时间过滤器 
		filter = dateRange.getFilter(self.dateField,{})
		if filter:
			if "query" in param:
				param["query"].update(filter)
			else:
				param["query"] = filter

		if self.out_collection:
			param["out"] = self.out_collection
		return db.map_reduce(self.collection,map,reduce,**param)
		
		
	@staticmethod
	def _update_datetime(text):
		while True:
			mm = re.search('datetime\((\s*\d+.\d+.\d+\D+\d+.\d+.\d+\s*)\)',text,re.M|re.S)
			if mm is None:
				return text
			date = mm.group(0) 
			mm = re.search("(\d+)\D(\d+)\D(\d+)\D+(\d+)\D(\d+)\D(\d+)*",date)
			if mm is None:
				assert 0
			date2 = "%s-%s-%s %s:%s:%s"%(mm.group(1),mm.group(2),mm.group(3),mm.group(4),mm.group(5),mm.group(6)) 
			text = text.replace(date,'{"cls_name_xyz":"d.datetime","value":"'+date2+'"}') 
		
	def _replace_variables(self,getParamFunc=webutility.get_param,**variables):
		vv = {}
		#增加系统变量 
		now = utility.now_str()
		vv["now"] = '{"cls_name_xyz":"d.datetime","value":"%s"}'%now
		vv["now_str"] = now
		#增加全局变量 
		vv.update(self.globalVars)
		for v in self.variables:
			if v not in variables:
				vv[v] = getParamFunc(v)
		vv.update(variables)	
		text = self.xmlText
		for v in vv:
			text = text.replace("@"+str(v)+"@",str(vv[v]))
		return query._update_datetime(text)
	
	def _decodeEcharts(self,node):
		self.echarts = {}
		self.series = {}
		
		echartNode = node.find("echarts")
		if echartNode is None:
			return  
			 
		nn = echartNode.find("option")
		if nn is None:
			return 
		for n in list(nn):#.getchildren():
			if not n.text:
				continue
			self.echarts[n.tag] = json_codec.load(n.text)
		#update title
		if "title" not in self.echarts:
			self.echarts["title"] = {}
		self.echarts["title"]["text"] = echartNode.attrib["title"] 
		
		nn = echartNode.find("template")
		assert nn is not None
		self.xAxis = nn.attrib["xAxis"]
		if self.xAxis.lower() == "none" or self.xAxis.lower() == "null":
			#pie chart
			self.xAxis = None
		
		if "refresh" in nn.attrib:
			self.refreshSec = int(nn.attrib["refresh"])
		else:
			self.refreshSec = 0
			
		if "increment" in nn.attrib:
			self.increment = bool(nn.attrib["increment"])
		else:
			self.increment = False
			
		nn = nn.findall("series")
		for n in nn:
			self.series[n.attrib["id"]] = json_codec.load(n.text)
		if not nn:
			return 
	
	#处理网页
	@counter.count
	def handle(self,ds):
		start = utility.ticks()
		def _getKey(row):
			id = row["_id"]
			if isinstance(id,dict):
				#把所有的id除了x轴，全连接起来 
				return ".".join([ str(utility.get_attr(id,x)) for x in id if x != self.xAxis]) #顺序可能有问题 
			else:
				return str(id)
			
		o = utility.clone(self.echarts) 
		series = {}
		legend = []
		i = 0
		xData = dateRange.getAxisData(self._no_datagroup)
		for row in ds:
			if self.xAxis:
				key = _getKey(row)
				for s in self.series:
					k = key+"."+ s 
					if k not in series:
						if key:
							name = key +" - "+self.series[s]["name"]
						else:
							name = self.series[s]["name"]
						if not dateRange.hasSeries(name):
							continue
						legend.append(name)
						series[k] = {"data":dateRange.getEmptyData(self._no_datagroup)}
						series[k].update(utility.clone(self.series[s]))
						series[k]["name"] = name
					index = dateRange.getIndex(row["_id"][self.xAxis],xData,self._no_datagroup)
					if index == -1:
						continue
					series[k]["data"][index] = row[s] 
			else:
				#pie chart 
				for s in self.series:
					series[s] = utility.clone(self.series[s])
					series[s]["data"] = []
					if s not in row:
						continue
					series[s]["data"].append({"name":str(row[s]),"value":None})
					legend.append(str(row[s]))
							
					for col in row:
						if col != s: #col is id 
							series[s]["data"][len(series[s]["data"])-1]["value"] = row[col]
							break
				
		if self.xAxis:
			if "xAxis" not in o:
				o["xAxis"] = {"type": 'category',"data":xData} 
			else:
				o["xAxis"]["data"] = xData
			
			if "yAxis" not in o:
				o["yAxis"] = {"type":"value"}
				
			if "tooltip" not in o:
				o["tooltip"] = {"trigger": "axis"}
		else:
			if "tooltip" not in o:
				o["tooltip"] = {"trigger": "item"}
			
		
		if "legend" not in o:
			o["legend"] = {"orient":"vertical","right": 10}
			
		o["legend"]["data"] = legend
		o["series"] = list(series.values())
		r = {"options":o,"refresh":dateRange.getRefreshSec(self.refreshSec),"increment":self.increment}
		if self.increment:
			#前端把这个id带回来,带上这个id则采用增量的方式   
			r["dateRangeRequestId"] = dateRange.setRequestId(legend)  
		if utility.ticks() - start > 3000:
			log.info("handle finish ",self.name + " time=",str((utility.ticks() - start)/1000.0)+"s")
		return r
			 
			 
			 
			 
########### unit test ###############
def test_leftjoin():
	ds = [{ "_id" : 11111, "item" : "almonds", "price" : 12, "quantity" : 2 },
			{ "_id" : 22222, "item" : "pecans", "price" : 20, "quantity" : 1 },
			{ "_id" : 33333  },
			{ "_id" : 44444, "item" : "noexist", "price" : 20, "quantity" : 1 }
		]
	db.drop_table("test_orders")
	db.insert_many("test_orders",ds)
	
	ds = [
	{ "_id" : 1, "itemN" : "almonds", "description": "product 1", "instock" : 120 },
	{ "_id" : 2, "itemN" : "bread", "description": "product 2", "instock" : 80 },
	{ "_id" : 3, "itemN" : "pecans", "description": "product 3", "instock" : 60 },
	{ "_id" : 4, "itemN" : "pecans", "description": "product 4", "instock" : 70 },
	{ "_id" : 5, "itemN": None, "description": "Incomplete" },
	{ "_id" : 6 }]
	db.drop_table("test_inventory")
	db.insert_many("test_inventory",ds)
	
	ds = [
	{ "_id" : 1, "itemNM" : "almonds", "description": "product 11", "instock2" : 120 },
	{ "_id" : 2, "itemNM" : "bread", "description": "product 22", "instock2" : 80 },
	{ "_id" : 3, "itemNM" : "pecans", "description": "product 33", "instock2" : 60 },
	{ "_id" : 4, "itemNM" : "pecans", "description": "product 44", "instock2" : 70 },
	{ "_id" : 5, "itemNM": None, "description": "Incomplete" },
	{ "_id" : 6 }]
	db.drop_table("test_inventory2")
	db.insert_many("test_inventory2",ds)
	s = """
		<query name="ycat测试2" collection="test_orders" out_collection="" dateField=""> 
			<mongo.aggregate>
				<leftjoin select="description,instock" from="test_inventory" localField="item" foreignField="itemN"></leftjoin>
				<leftjoin select="description" from="test_inventory2" localField="test_inventory.instock" foreignField="instock2"></leftjoin>
			</mongo.aggregate>
	</query>
	"""
	q = query(s)
	ds = q.run().list()
	print(ds)
	assert 4 == len(ds)
	assert 6 == len(ds[0])
	assert ds[0]["_id"] == 11111
	assert ds[0]["item"] == "almonds"
	assert ds[0]["price"] == 12
	assert ds[0]["quantity"] == 2
	assert ds[0]["test_inventory"]["description"] == "product 1"
	assert ds[0]["test_inventory2"]["description"] == "product 11"
	assert ds[0]["test_inventory"]["instock"] == 120
	assert 2 == len(ds[0]["test_inventory"])
	assert ds[1]["_id"] == 22222
	assert ds[1]["item"] == "pecans" 
	assert ds[1]["test_inventory"]["description"] == "product 3"
	assert ds[1]["test_inventory2"]["description"] == "product 33"
	assert ds[1]["test_inventory"]["instock"] == 60
	assert ds[2]["_id"] == 33333 
	assert ds[2]["test_inventory"] == {}
	assert ds[3]["_id"] == 44444 
	assert "test_inventory" not in ds[3]
	db.drop_table("test_orders")
	db.drop_table("test_inventory")
	db.drop_table("test_inventory2")
	 

def test_decodeEcharts(): 
	s = """<query name="ycat测试5" collection="test_test_aggregate2" out_collection=""  dateField="startTime"> 
		<bottle url="">
			<variable name="test1"/>
			<variable name="test2"/>	
		</bottle>
		<echarts title="大数据量面积图2">
			<template xAxis="dateRange">
				<!-- serirs将是N乘M的关系，N是_id个数减1(即减去X轴的值)，M是除_id之外的参数个数 -->
				<series id="value1">{"type":"bar","name":"测试数据1"}</series>
				<series id="value2">{"type":"line","name":"测试数据2"}</series>
			</template>
			<option>
				<title>{"left": "center","text": "大数据量面积图"}</title>
				<legend></legend>
				<tooltip></tooltip>
				<dataset></dataset>
				<xAxis>{"type":"category"}</xAxis>
				<yAxis></yAxis>
				<series>[{"type":"bar"},{"type":"bar"},{"type":"bar"}]</series>
			</option>
		</echarts>
		<mongo.aggregate>
			<dateRangeGroup>
				{"_id": {"key1":"$strValue"},"value1": { "$sum": 1},"value2": { "$sum": "$intValue"}}
			</dateRangeGroup>
		</mongo.aggregate></query>
	"""
	webutility.set_test_param("dateRangeStart","2018-06-21T23:59:59.999Z")
	webutility.set_test_param("dateRangeEnd","2018-06-23T23:59:59.999Z")
	webutility.set_test_param("dateRangeType","date") 
	
	q = query(s)
	assert q.refreshSec == 0
	assert q.increment == False
	assert q.echarts["title"] ==  {'left': 'center', 'text': '大数据量面积图2'}
	assert q.xAxis == "dateRange"
	assert 2 == len(q.series)
	assert q.series["value1"] == {"name":"测试数据1" ,"type": "bar" } 
	assert q.series["value2"] == {"name":"测试数据2" ,"type":"line" } 
	
	db.drop_table("test_test_aggregate2")
	date = datetime.datetime(2018,6,22,8,49,21)
	for i in range(1000):
		d = {"test1":str(i%5),"startTime":date,"intValue":i%100,"strValue":"key"+str(i%5)}
		date += datetime.timedelta(hours=1)
		db.insert("test_test_aggregate2",d) 
	webutility.set_test_param("dateRangeType","date")
	ds = q.run().list()
	
	ss = q.handle(ds) 
	
	
def test_dateRangeGroup():
	s = """
		<query name="ycat测试2" collection="test_test_aggregate2" out_collection=""  dateField="startTime"> 
		<mongo.aggregate>
			<dateRangeGroup>
				{"_id": {"key1":"$strValue"},"value1": { "$sum": 1},"value2": { "$sum": "$intValue"}}
			</dateRangeGroup>
		</mongo.aggregate>
	</query>
	"""
	q = query(s)
	webutility.set_test_param("dateRangeType","date")
	p = q._dateRangeGroup([],"""{"value1": { "$sum": 1}}""")[0]["$group"]
	assert 2 == len(p)
	assert p["_id"] == {"dateRange": {"$hour":"$startTime"}}
	assert p["value1"] == { "$sum": 1}
	
	webutility.set_test_param("dateRangeType","week")
	p = q._dateRangeGroup([],"""{"_id":"test1","value1": { "$sum": 1},"value2": { "$sum": 2}}""")[0]["$group"]
	assert 3 == len(p)
	assert p["_id"] == {"key":"$test1","dateRange": {"$dayOfWeek":"$startTime"}}
	assert p["value1"] == { "$sum": 1}
	assert p["value2"] == { "$sum": 2}
	
	webutility.set_test_param("dateRangeType","dates")
	p = q._dateRangeGroup([],"""{"_id":{"kk":"$test1"},"value1": { "$sum": 1},"value2": { "$sum": 2}}""")[0]["$group"]
	assert 3 == len(p)
	assert p["_id"] == {"kk":"$test1","dateRange": {"$dateToString": {"format": "%Y-%m-%d", "date": "$startTime"}}}
	assert p["value1"] == { "$sum": 1}
	assert p["value2"] == { "$sum": 2}
	
	db.drop_table("test_test_aggregate2")
	date = datetime.datetime(2018,6,22,8,49,21)
	for i in range(1000):
		d = {"test1":str(i/100),"startTime":date,"intValue":i%100}
		date += datetime.timedelta(hours=1)
		db.insert("test_test_aggregate2",d)
	webutility.set_test_param("dateRangeType","date")
	webutility.set_test_param("dateRangeStart","2018-06-22T08:49:21.000Z")
	webutility.set_test_param("dateRangeEnd","2018-06-23T08:49:21.000Z")
	ds = q.run().list()
	assert 16 == len(ds)
	
	webutility.set_test_param("dateRangeType","week")
	webutility.set_test_param("dateRangeStart","2018-06-22T08:49:21.000Z")
	webutility.set_test_param("dateRangeEnd","2018-07-23T08:49:21.000Z")
	ds = q.run().list()
	assert 7 == len(ds)
	assert "周一" == ds[0]["_id"]["dateRange"]
	assert "周六" == ds[5]["_id"]["dateRange"]
	assert "周日" == ds[6]["_id"]["dateRange"]
	
	webutility.set_test_param("dateRangeType","dates")
	webutility.set_test_param("dateRangeStart","2018-06-22T08:49:21.000Z")
	webutility.set_test_param("dateRangeEnd","2018-07-23T08:49:21.000Z")
	ds = q.run().list()
	assert 32 == len(ds)
	db.drop_table("test_test_aggregate2") 

	
def test_update_datetime():
	assert '<group>{"cls_name_xyz":"d.datetime","value":"2018-12-26 16:27:34"}</group>' == query._update_datetime("<group>datetime(2018-12-26 16:27:34)</group>")
	assert '<group>{"cls_name_xyz":"d.datetime","value":"2018-12-26 16:27:34"}</group>' == query._update_datetime("<group>datetime(2018,12,26,16,27,34)</group>")
	ss = """'<group>datetime(2018,12,26,16,27,34)</group>'
	'<group>datetime(2018,12,26,16,27,34)</group>'"""
	sss = """'<group>{"cls_name_xyz":"d.datetime","value":"2018-12-26 16:27:34"}</group>'
	'<group>{"cls_name_xyz":"d.datetime","value":"2018-12-26 16:27:34"}</group>'"""
	assert sss == query._update_datetime(ss)

def test_replace_variables():
	def getParam(v):
		return "c_"+str(v)
	s = """
		<query name="统计排名前10的AP的总流量" collection="pie_ap_traffic" out_collection="pie_ap_traffic2"  >
		<bottle url="/service/chart/pie/test_pie">
			<variable name="test1"/>
			<variable name="test2"/>
		</bottle> 
		<mongo.aggregate>
			<match>"@test1@:@test2@"</match>
			<group>datetime(2017,12,31,22,14,43)</group>
			<sort>"value":-1</sort>
			<limit>10</limit>
			<match>@aaa@:@bbb@</match>
			<project>@now@</project>
			<project2>@now_str@</project2>
		</mongo.aggregate>
	</query>
	"""
	utility.set_now(datetime.datetime(2018,1,5,9,2,15))
	q = query(s,globalVars={"aaa":1,"bbb":2})
	assert q.url == "/service/chart/pie/test_pie"
	ss = q._replace_variables(getParamFunc=getParam)
	sss = """<mongo.aggregate>
			<match>"c_test1:c_test2"</match>
			<group>{"cls_name_xyz":"d.datetime","value":"2017-12-31 22:14:43"}</group>
			<sort>"value":-1</sort>
			<limit>10</limit>
			<match>1:2</match>
			<project>{"cls_name_xyz":"d.datetime","value":"2018-01-05 09:02:15"}</project>
			<project2>2018-01-05 09:02:15</project2>
		</mongo.aggregate>"""
	assert ss.strip() == sss.strip()
	sss = """<mongo.aggregate>
			<match>"c_test1:c_test2"</match>
			<group>{"cls_name_xyz":"d.datetime","value":"2017-12-31 22:14:43"}</group>
			<sort>"value":-1</sort>
			<limit>10</limit>
			<match>my_aaa:2</match>
			<project>{"cls_name_xyz":"d.datetime","value":"2018-01-05 09:02:15"}</project>
			<project2>2018-01-05 09:02:15</project2>
		</mongo.aggregate>"""
	ss = q._replace_variables(getParamFunc=getParam,aaa="my_aaa")
	assert ss.strip() == sss.strip()
	utility.set_now(None)

	
def testreadxml():
	s = """
		<query name="统计排名前10的AP的总流量" collection="pie_ap_traffic" out_collection="pie_ap_traffic2"  >
		<bottle url="/service/chart/pie/test_pie">
			<variable name="test1"/>
			<variable name="test2"/>
		</bottle> 	
		<variable name="test1"/>
		<variable name="test2"/>
		<mongo.aggregate>
			<match>"capwap_apip":{"$exists":"true"}</match>
			<group>"_id" : "$capwap_apip", "value" : {"$sum":"$stream_len"}</group>
			<sort>"value":-1</sort>
			<limit>10</limit>
			<match>"capwap_apip22":{"$exists":"true"}</match>
			<project>"value":{"$divide":["$value",1]}</project>
		</mongo.aggregate>
	</query>
	"""
	q = query(s,globalVars={"aaa":1,"bbb":2})
	assert q.url == "/service/chart/pie/test_pie"
	assert q.name == "统计排名前10的AP的总流量"
	assert q.collection == "pie_ap_traffic"
	assert q.variables == ["test1","test2"] 
	assert q.type == "mongo.aggregate"
	assert q.out_collection == "pie_ap_traffic2"
	assert q.globalVars == {"aaa":1,"bbb":2}
	m = {"$match":{"capwap_apip":{"$exists":"true"}}}
	g = {"$group":{"_id" : "$capwap_apip", "value" : {"$sum":"$stream_len"}}}
	s = {"$sort":{"value":-1}}
	l = {"$limit":10}
	m2= {"$match":{"capwap_apip22":{"$exists":"true"}}}
	p = {"$project":{"value":{"$divide":["$value",1]}}}
	#assert q.pipe == [m,g,s,l,m2,p]

def test_add_pipe(): 
	text = '{"_id" : "xxxx", "type":{"$sum":[datetime(2017-12-26 16:27:34),datetime(2018-12-26 16:27:34)]}}'
	p = []
	r = query._add_pipe(p,"match",'{"capwap_apip":{"$exists":"false"}}') 
	assert len(r) == 1
	assert "$match" in r[0]
	v = r[0]["$match"] 
	assert v["capwap_apip"]["$exists"] == "false"
	r = query._add_pipe(p,"group",query._update_datetime(text)) 
	
	assert len(r) == 2
	assert "$group" in r[1]
	v = r[1]["$group"] 
	assert v["_id"] == "xxxx" 
	assert v["type"]["$sum"] == [datetime.datetime(2017,12,26,16,27,34),datetime.datetime(2018,12,26,16,27,34)]

def test_aggregate():
	data = {
	  "_id": "10280",
	  "city": "NEW YORK",
	  "state": "NY",
	  "pop": 5574,
	  "loc": [
		-74.016323,
		40.710537
	  ]
	}	
	db.drop_table("test_test_aggregate")
	db.insert("test_test_aggregate",data)
	s = """<query name="ycat测试" collection="test_test_aggregate" out_collection="" > 
		<mongo.aggregate>
			<group>{"_id": { "state": "$state", "city": "$city" },"pop": { "$sum": "$pop" }}</group>
			<sort>{ "pop": 1 }</sort>
			<group><![CDATA[{
        "_id" : "$_id.state",
        "biggestCity":  { "$last": "$_id.city" },
        "biggestPop":   { "$last": "$pop" },
        "smallestCity": { "$first": "$_id.city" },
        "smallestPop":  { "$first": "$pop" }
      }
	  ]]></group>
			<project><![CDATA[{
					"_id": 0,
				  "state": "$_id",
				  "biggestCity":  { "name": "$biggestCity",  "pop": "$biggestPop" },
				  "smallestCity": { "name": "$smallestCity", "pop": "$smallestPop" }
				} 
				]]>
			</project>
		</mongo.aggregate>
	</query>"""
	q = query(s)
	ds = q.run()
	assert ds.next()
	assert ds["state"] == "NY"
	assert ds["biggestCity"] == {'pop': 5574, 'name': 'NEW YORK'}
	assert ds["smallestCity"] == {'pop': 5574,'name': 'NEW YORK'}
	db.drop_table("test_test_aggregate")
	
def testmr():
	data = {
    "_id": "50a8240b927d5d8b5891743c",
    "cust_id": "abc123",
    "ord_date": datetime.datetime(2018,1,8,0,0,0),
    "status": 'A',
    "price": 25,
    "items": [ { "sku": "mmm", "qty": 5, "price": 2.5 },
              { "sku": "nnn", "qty": 5, "price": 2.5 } ]
}
	s = """
	<query name="按每小时统计上下行流量" collection="test_test_mr"    out_collection="">
		<mongo.map-reduce>
			<query>{"ord_date":{"$gte": datetime(2018,1,8,0,0,0)}}</query>
			<map>
			<![CDATA[
			function() {
                       for (var idx = 0; idx < this.items.length; idx++) {
                           var key = this.items[idx].sku;
                           var value = {
                                         count: 1,
                                         qty: this.items[idx].qty
                                       };
                           emit(key, value);
                       }
                    }
			]]>
			</map>
			<reduce>
			<![CDATA[
			function(keySKU, countObjVals) {
                     reducedVal = { count: 0, qty: 0 };

                     for (var idx = 0; idx < countObjVals.length; idx++) {
                         reducedVal.count += countObjVals[idx].count;
                         reducedVal.qty += countObjVals[idx].qty;
                     }

                     return reducedVal;
                  }
			]]>
			</reduce>
			<finalize>
			<![CDATA[
			function (key, reducedVal) {

                       reducedVal.avg = reducedVal.qty/reducedVal.count;

                       return reducedVal;

                    }
			]]>
			</finalize> 
		</mongo.map-reduce>
		</query>
	"""
	db.drop_table("test_test_mr")
	db.insert("test_test_mr",data)
	q =  query(s)
	dd = q.run()
	
	assert len(dd) == 2
	assert dd[0]["_id"] == "mmm"
	assert dd[0]["value"] == {'count': 1.0, 'qty': 5.0, 'avg': 5.0}
	
	assert dd[1]["_id"] == "nnn"
	assert dd[1]["value"] == {'count': 1.0, 'qty': 5.0, 'avg': 5.0}
	 
	db.drop_table("test_test_mr")
	db.drop_table("test_test_mr_results")
	
def test_find():
	db.drop_table("test_test_find")
	db.drop_table("test_test_find_out")
	db.insert_many("test_test_find",[
		   { "item": "journal", "qty": 25, "tags": ["blank", "red"], "dim_cm": [ 14, 21 ] },
		   { "item": "notebook", "qty": 50, "tags": ["red", "blank"], "dim_cm": [ 14, 21 ] },
		   { "item": "paper", "qty": 100, "tags": ["red", "blank", "plain"], "dim_cm": [ 14, 21 ] },
		   { "item": "planner", "qty": 75, "tags": ["blank", "red"], "dim_cm": [ 22.85, 30 ] },
		   { "item": "postcard", "qty": 45, "tags": ["blue"], "dim_cm": [ 10, 15.25 ] }
		])
	s = """	<query name="test_find" collection="test_test_find" out_collection="test_test_find_out" >
		<mongo.find>
		</mongo.find>
	</query>
	"""
	import pymongo 
	q = query(s)
	dd = q.run()
	dd = dd.list()
	assert len(dd) == 5
	assert dd[0]["item"] == "journal"
	assert dd[0]["qty"] == 25
	assert dd[0]["tags"] == ["blank", "red"]
	assert dd[0]["dim_cm"] == [ 14, 21 ]
	
	s = """	<query name="test_find" collection="test_test_find" out_collection="test_test_find_out" >
		<mongo.find>
			<sort>"qty":-1</sort>
			<limit>3</limit>
			<skip>2</skip>
		</mongo.find>
	</query>
	"""
	q = query(s)
	dd = q.run()
	dd = dd.list()
	assert len(dd) == 3
	assert dd[0]["qty"] == 50
	assert dd[1]["qty"] == 45
	assert dd[2]["qty"] == 25
	
	s = """	<query name="test_find" collection="test_test_find" out_collection="test_test_find_out">
		<mongo.find>
			<cond>{ "dim_cm": { "$elemMatch": { "$gt": 22, "$lt": 30 } } }</cond>
			<cond>{"item":"planner"}</cond>
			<column>qty</column>
			<column>dim_cm</column>	
		</mongo.find>
	</query>
	"""
	q = query(s)
	dd = q.run().list()  
	assert len(dd) == 1
	assert dd[0]["qty"] == 75
	assert dd[0]["dim_cm"] ==  [22.85, 30]	
	assert "tags" not in dd[0]
	
	s = """	<query name="test_find" collection="test_test_find_out" out_collection="" >
		<mongo.find>
		</mongo.find>
	</query>
	"""
	q = query(s)
	dd = q.run()
	dd = dd.list()
	assert len(dd) == 1
	assert dd[0]["qty"] == 75
	assert dd[0]["dim_cm"] ==  [22.85, 30]
	assert "tags" not in dd[0]
	
	db.drop_table("test_test_find")
	db.drop_table("test_test_find_out")


if __name__== "__main__":
	utility.run_tests()
	#test_find()
	

