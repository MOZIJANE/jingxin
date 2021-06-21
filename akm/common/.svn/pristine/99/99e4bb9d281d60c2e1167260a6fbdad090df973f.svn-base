#!/usr/bin/env python3.2
# -*- coding: utf-8 -*-
import pymongo
import config
import utility
import threading
import lock
import sys
import bson.code
import log
import counter

ObjectId = bson.objectid.ObjectId

class statInfo:
	def __init__(self):
		self.successCount = 0
		self.failCount = 0
		self.indexCount = 0
		self.totalExamDoc = 0
		self.totalKeyExamDoc = 0
		self.totalRetDoc = 0
		self.bucket = counter.bucket()
	
class statsInfo:
	def __init__(self):
		self.stat = {}
		
	def add(self,obj):
		ee = obj.explain()
		e = ee["executionStats"]
		table = ee["queryPlanner"]["namespace"] + ".find"
		if table not in self.stat:
			self.stat[table] = statInfo()
		s = self.stat[table]
		if e["executionSuccess"]:
			s.successCount += 1
		else:
			s.failCount += 1
		
		if "winningPlan" in ee["queryPlanner"] and "inputStage" in ee["queryPlanner"]["winningPlan"]:
			ww = ee["queryPlanner"]["winningPlan"]
			if "inputStage" in ww: 
				if ww["inputStage"]["stage"] == "IXSCAN":
					s.indexCount += 1
		s.totalKeyExamDoc += e["totalKeysExamined"]
		s.totalExamDoc += e["totalDocsExamined"]
		s.totalRetDoc += e["nReturned"]
		s.bucket.add(e["executionTimeMillis"])
	
	def addSuccess(self,table,time):
		if table not in self.stat:
			self.stat[table] = statInfo()
		s = self.stat[table]
		s.successCount += 1
		s.bucket.add(time)
		
	def addFail(self,table,time):
		if table not in self.stat:
			self.stat[table] = statInfo()
		s = self.stat[table]
		s.failCount += 1
		s.bucket.add(time)
		

class mongodb:
	def __init__(self):
		self._isConnect = None
		self.db = None
		self.account = ''
		self.passwd = ''
		self.conn = None
		self.query = self.find
		self.query_one = self.find_one
		self.update_set_remove = self.update_array_remove
		self.stat = statsInfo()
		if not config.getbool("mongo","enable",True):
			log.error("mongo db is disabled")
		
	def disconnect(self):
		self.conn.close()	
		self.db = None
		
	def isConnect(self): 
		if not config.getbool("mongo","enable",True):
			return False
		if self._isConnect is None:
			return self.get_conn() is not None
		return self._isConnect
		
	def get_conn(self):
		if self.db is None:
			self._get_db()
		return self.conn
					
	def insert(self, table, request):
		return  self._get_db()[table].insert_one(request)
		
	def insert_many(self, table, request):
		return self._get_db()[table].insert_many(request)	
		
	def delete_many(self, table, request=''):
		if request == '':
			return self._get_db()[table].remove()
		return self._get_db()[table].delete_many(request)
		
	def delete_one(self, table, request):
		return self._get_db()[table].delete_one(request)

	#https://docs.mongodb.org/manual/reference/operator/update/
	#http://api.mongodb.org/python/current/api/pymongo/collection.html#pymongo.collection.Collection.update_many 
	#具体操作方法见该网页  
	def update_op_one(self, table, filter, update_op, update_or_insert):
		return self._get_db()[table].update_one(filter, update_op, upsert = update_or_insert)
	
	def update_op_many(self, table, filter, update_op, update_or_insert):
		return self._get_db()[table].update_many(filter, update_op, upsert = update_or_insert)

	def update_one(self, table, filter, fields, update_or_insert = False):
		return self.update_op_one(table,filter,{"$set":fields},update_or_insert)

	def update_many(self, table, filter, fields, update_or_insert = False):
		return self.update_op_many(table,filter,{"$set":fields},update_or_insert)
	
	#filter为doc的过滤器
	#field为集合列名
	#values为集合的值列表 
	def update_array_push(self, table, filter, field, values, update_many = False, update_or_insert = False):
		if update_many:
			func = self.update_op_many
		else:
			func = self.update_op_one
		if isinstance(values,(list,tuple)):
			return func(table,filter,{"$push":{field: {"$each":values}}},update_or_insert)
		else:
			return func(table,filter,{"$push":{field:values}},update_or_insert)
	
	#删除所有的数组中的值，包括所有重复的值 
	def update_array_remove(self, table, filter, field, values, update_many = False):
		if update_many:
			func = self.update_op_many
		else:
			func = self.update_op_one
		if isinstance(values,(list,tuple)):
			return func(table,filter,{"$pull":{field:{"$in":values}}},update_or_insert = False)
		else:
			return func(table,filter,{"$pull":{field:values}},update_or_insert = False)
	
	def update_set_add(self, table, filter, field, values, update_many = False):
		if update_many:
			func = self.update_op_many
		else:
			func = self.update_op_one
		return func(table,filter,{"$addToSet":{field:values}},update_or_insert = False)
	
	def remove_field(self, table, filter, fields, update_many = False):
		cond = {}
		if isinstance(fields,str):
			cond[fields] = ""
		else:
			for x in fields:
				cond[x] = ""
			
		if update_many:
			return self.update_op_many(table,filter,{"$unset":cond},update_or_insert = False)
		else:
			return self.update_op_one(table,filter,{"$unset":cond},update_or_insert = False)
	
	#fields为dict，{old_name1:new_name1,old_name2:new_name2}
	def rename_field(self, table, filter, fields, update_many = False):
		if update_many:
			return self.update_op_many(table,filter,{"$rename":fields},update_or_insert = False)
		else:
			return self.update_op_one(table,filter,{"$rename":fields},update_or_insert = False)
		
	def increase(self, table, filter, fields, update_many = False):
		if update_many:
			return self.update_op_many(table,filter,{"$inc":fields},False)
		else:
			return self.update_op_one(table,filter,{"$inc":fields},False)
	 
	#columns为列名的列表，可以指定单独读那些列，例如 ['c1','c2','c3']，默认都会带_id列 		
	def find(self, table, filter = None, columns=None):
		if columns == []:
			columns = None
		db = self._get_db()
		if db is None:
			raise Exception("mongodb is not connected")
		ds = dataset(db[table].find(filter=filter,projection=columns))
		self.stat.add(ds)
		self.stat.add(ds)
		return ds

	def find_one(self, table, filter = None, columns=None):
		return self._get_db()[table].find_one(filter=filter,projection=columns)

	def create_index(self, table, index):
		if isinstance(index,(tuple,list)):	
			return self._create_indexs(table,index)
		return self._get_db()[table].create_index(index)

	#index对象["index1","index2",...,"indexN"] 
	def _create_indexs(self, table, index):
		return self.create_index_op(table, [(x,pymongo.ASCENDING) for x in index])
	
	#index对象： ([("hello", DESCENDING),...,("world", ASCENDING)], name="hello_world") 
	def create_index_op(self, table, index):
		return self._get_db()[table].create_index(index)

	def get_indexes(self, table):
		return dataset(self._get_db()[table].list_indexes())

	#index_name就是create_index的返回值 
	def drop_index(self,table,index_name):	
		return self._get_db()[table].drop_index(index_name)

	def drop_index_by_table(self, table):
		ds = self.get_indexes(table)
		while ds.next():
			if "_id_" == ds["name"]:
				continue
			self.drop_index(table,ds["name"])

	def drop_table(self, table):
		return self._get_db().drop_collection(table)
	
	def get_count(self, table):
		return self._get_db()[table].count()
	
	def get_table_name_list(self):
		return self._get_db().collection_names()
		
	def _auth(self,account,passwd):
		return self.db.authenticate(account,passwd)
		
	#不能用于shareding环境,直接返回{}的列表对象	 
	def group(self,table, key, condition, initial, reduce, finalize,**kwargs):
		return self._get_db()[table].group(key,condition,initial,reduce,finalize,**kwargs)
	
	def aggregate(self, table, pipeline, **kwargs):
		#log.debug("aggregate : " +  table + " pipe: " + str(pipeline))
		if isinstance(pipeline,dict):
			ret = self._get_db()[table].aggregate([pipeline,], **kwargs)
		else:
			ret = self._get_db()[table].aggregate(pipeline, **kwargs)
		return dataset(ret)

	#如果out为inline时，返回list<dict<_id,value>>的字典
	#如果out不为inline，还需要调用map_reduce(), out.find())来取得dataset
	#可以使用query="xxx"等参数
	#If full_response is False (default) returns the result documents in a list,
	#Otherwise, returns the full response from the server to the map reduce command.
	def map_reduce(self,table, mapper,reducer,out={"inline":1},full_response=False,**kwargs):
		#log.debug("map_reduce : " +  table +  ", mapper: " + mapper + ", reduce: " + reducer)
		ret = self._get_db()[table].map_reduce(mapper,reducer,out,full_response=full_response,**kwargs)
		return ret["results"]

	def _get_db(self): 
		if self.db is not None:
			try:
				#ret = self._auth(self.account, self.passwd)
				if self.conn.is_primary:
					return self.db
				else:
					self.db = None
					self.conn.close()
			except pymongo.errors.NetworkTimeout as e:
				log.exception('Connect mongodb error!',e)
				self.db = None
				self.conn.close()

		serverlist = config.get("mongo","servers")
		dbname = config.get("mongo","db")
		replica = config.get("mongo","replica")
		self.account = config.get("mongo","user")
		self.passwd = config.get("mongo","pwd")
		assert dbname != ""
		assert serverlist != ""
		
		servers = str(serverlist).split(',')
		try:
			for ss in servers:
				server = ss.split(':')
				self.conn = pymongo.MongoClient(server[0],int(server[1]))
				lock.sleep(3)
				
				#在终端下，发现is_primary是非阻塞，所以要sleep 3 秒等待判断返回
				if self.conn.is_primary: 
					log.info("Mongodb connect to %s port %s" %(self.conn.address[0],self.conn.address[1]))			
					break
				else:
					self.conn.close()
			
			self.db = pymongo.database.Database(self.conn,dbname)
			self._isConnect = True
			ret = True
			#ret = self._auth(self.account, self.passwd)
			if not ret:
				log.debug('Config mongodb auth failed!')			
				self.db = None
				self.conn.close()
		except (pymongo.errors.InvalidName,pymongo.errors.NetworkTimeout,pymongo.errors.ServerSelectionTimeoutError) as e:
			self._isConnect = False
			self.db = None
			self.conn.close()
			if isinstance(e,pymongo.errors.ServerSelectionTimeoutError):
				e.noprint = True
			log.exception('Connect mongodb error!',e)
		finally: 
			return self.db
		
#用于排序		 
DESCENDING = pymongo.DESCENDING
ASCENDING = pymongo.ASCENDING
TEXT = pymongo.TEXT
		
class dataset(object):
	default_codec = "utf-8"
	static_tables = {} #存放静态表 c_的

	def _get_static_table(table):
		if table[:2] != "c_":
			return None
		if table in dataset.static_tables:
			return dataset.static_tables[table]
		return None
		
	def _save_static_table(table,ds):
		if table[:2] != "c_":
			return
		dataset.static_tables[table] = ds

	def _wrap(func):
		def __call(*p,**pp):
			r = func(*p,**pp)
			if isinstance(r,pymongo.cursor.Cursor):
				return dataset(r)
			return r
		return __call
	
	def __init__(self, cursor):
		self._row = None
		self.isPrinted = False
		self.cursor = cursor
		self._count = -1
		self.next_count = 0
		self.lefts = {}
		
		if self.is_countable:
			#参见 http://api.mongodb.org/python/current/api/pymongo/cursor.html
			self.limit = dataset._wrap(cursor.limit)
			self.sort = dataset._wrap(cursor.sort)
			self.collection = dataset._wrap(cursor.collection)
			self.distinct = dataset._wrap(cursor.distinct)
			self.explain = dataset._wrap(cursor.explain)
			self.hint = dataset._wrap(cursor.hint)
			self.max = dataset._wrap(cursor.max)
			self.min = dataset._wrap(cursor.min)
			#self.rewind = dataset._wrap(cursor.rewind)
			self.skip = dataset._wrap(cursor.skip)
			self.where = dataset._wrap(cursor.where)
			self.max_scan = dataset._wrap(cursor.max_scan)
	
	def rewind(self):
		if not self.is_countable:
			return
		self.next_count = 0
		self._row = None
		return self.cursor.rewind()
	
	@property
	def is_countable(self):
		#如果是CommandCursor，不能返回count，即aggregate对象的返回值  
		return not isinstance(self.cursor,pymongo.command_cursor.CommandCursor)
	
	@property	
	def count(self):
		if not self.is_countable:
			return -1
		if self._count == -1:
			self._count = self.cursor.count()
		return self._count
			
	def next(self): 
		#不能打印过后，又调用next，即只能遍历一次  
		assert not self.isPrinted
		if self.cursor.alive and self.count != 0:
			if self.count != -1 and self.next_count >= self.count:
				return False
			try:
				self._row = self.cursor.next()
			except StopIteration as e:
				log.exception('mongodb cursor error!',e)
				return False
			self.next_count += 1
			return True
		self._row = None
		return False
		
	def get(self, col, default_value = None):
		assert self._row is not None
		if len(self.lefts):
			info = self._left_join_info(col)
			if info:
				return self._get_left_join(info,col, default_value)
		if col not in self._row:
			return default_value
		else:
			return self._row[col]
	
	def __getitem__(self, key):
		return self.get(key)
	
	#进行左连接操作,col代表本地的ID，join_table为外键的表，join_col为外键表的列名
	#生成的列名为 join_table.xxx 
	def leftjoin(self,col,join_table,join_col="_id",selectColumn=[],join_str="."):
		d = utility.empty_class()
		d.col = col
		d.join_col = join_col
		d.join_table = join_table
		d.join_str = join_str
		d.selectColumn = selectColumn
		data = dataset._get_static_table(join_table)
		if data is None:
			data = {}
			ds = find(join_table) #因为要缓存，所以不能加上列过滤 ,columns=selectColumn)
			for v in ds.cursor:
				data[str(v[join_col])] = v
			dataset._save_static_table(join_table,data)
		d.data = data
		self.lefts[join_table] = d
		return self
		
	def _left_join_info(self,col):
		for d in self.lefts:
			if col.find(d+self.lefts[d].join_str) == 0:
				return self.lefts[d]
		return None
	
	def _get_left_join(self,info,col, default_value = None):
		i = str(self[info.col])
		if i in info.data:
			c = col[len(info.join_table)+1:]
			if c in info.data[i]:
				return info.data[i][c] #id找到，
			else:
				return default_value #key找不到，返回None 
		else:
			#left join规则，ID找不到，返回None 
			return default_value
	
	def row(self):
		return self._row
	
	#把当前行复制到list[]，list item为dict对象 
	def list(self):
		self.rewind()
		ret = []
		while self.next():
			x = self._row #dict 
			for left in self.lefts:
				left = self.lefts[left]
				if len(left.data):
					#这个是dict 
					for n in left.data:
						dd = left.data[n]
						#取出第一列 
						for d in dd:
							#取出每个列的列名 
							if left.selectColumn and d not in left.selectColumn:
								continue
							x[left.join_table+left.join_str+d] = self._get_left_join(left,left.join_table+left.join_str+d)
						break
			ret.append(x)
		self.rewind()
		return ret
		
	#把当前行复制到dict[]，key为_id, item为dict对象 
	def dict(self):
		self.rewind()
		ret = {}
		for x in self.cursor:
			ret[x["_id"]] = x
		self.rewind()
		return ret
		
	def __getattr__(self, key):
		if key == "cursor":
			return self.cursor 
		return self[key]
	
	def __str__(self):
		#如果游标正在一半，打印完会导致游标复位 
		self.rewind()
		s = ""
		for x in self.cursor:
			s += str(x) + "\n"
		self.rewind()	
		if s == "":
			s = "[Empty set]"
		if not self.is_countable:
			self.isPrinted = True
		return s

class dicset(object):
	default_codec = "utf-8"
	
	def __init__(self, cursor):
		self._dic = cursor
		
	def get(self, key, default_value = None):
		assert self._dic is not None
		if key not in self._dic:
			return default_value
		else:
			return self._dic[key]
	
	def __getitem__(self, key):
		return self.get(key)

g_mongodb = None

def _get_mongodb(): 
	global g_mongodb
	if g_mongodb is None:
		g_mongodb = mongodb()
	return g_mongodb
	
def wrap_stat(func):
	def __call(*p,**pp):
		global g_mongodb
		tick = utility.ticks()
		try:
			r = func(*p,**pp)
			g_mongodb.stat.addSuccess(g_mongodb.db.name+"."+p[0]+"."+func.__name__,utility.ticks()-tick)
			return r
		except Exception as e:
			if g_mongodb is not None and g_mongodb.db is not None:
				g_mongodb.stat.addFail(g_mongodb.db.name+"."+p[0]+"."+func.__name__,utility.ticks()-tick)
			raise
	return __call


insert			  = wrap_stat(_get_mongodb().insert)
insert_many		 = wrap_stat(_get_mongodb().insert_many)

update_one		  = wrap_stat(_get_mongodb().update_one)
update_many		 = wrap_stat(_get_mongodb().update_many)

update_op_one		   = wrap_stat(_get_mongodb().update_op_one)
update_op_many		   = wrap_stat(_get_mongodb().update_op_many)

#删除doc的某个列 
remove_field	= wrap_stat(_get_mongodb().remove_field)

#修改某一列的名字
rename_field	= wrap_stat(_get_mongodb().rename_field)

#在队列中增加值  
update_array_push = wrap_stat(_get_mongodb().update_array_push)

#在队列中删除值 
update_array_remove = wrap_stat(_get_mongodb().update_array_remove)

#在集合中增加值 
update_set_add = wrap_stat(_get_mongodb().update_set_add)

#在集合中删除值 
update_set_remove = wrap_stat(_get_mongodb().update_set_remove)

#对doc的某些列做加减运算
increase			= wrap_stat(_get_mongodb().increase)

delete_many		 = wrap_stat(_get_mongodb().delete_many)
delete_one		  = wrap_stat(_get_mongodb().delete_one)

find				= _get_mongodb().find
find_one			= wrap_stat(_get_mongodb().find_one)

isConnect = _get_mongodb().isConnect

#给函数起个别名
query_one = find_one
query = find

get_count = wrap_stat(_get_mongodb().get_count)
get_table_name_list = wrap_stat(_get_mongodb().get_table_name_list)
create_index = wrap_stat(_get_mongodb().create_index)
#create_indexs = wrap_stat(_get_mongodb().create_indexs)
create_index_op = wrap_stat(_get_mongodb().create_index_op)
get_indexes = wrap_stat(_get_mongodb().get_indexes)
drop_index = wrap_stat(_get_mongodb().drop_index)
drop_index_by_table = wrap_stat(_get_mongodb().drop_index_by_table)
drop_table = wrap_stat(_get_mongodb().drop_table)
group = wrap_stat(_get_mongodb().group)
aggregate = wrap_stat(_get_mongodb().aggregate)
map_reduce = wrap_stat(_get_mongodb().map_reduce)
disconnect = wrap_stat(_get_mongodb().disconnect)  

#############################	unit test	###########################
def test_find_projection():
	table = 'test_sta'
	drop_table(table)
	for i in range(10):
		request = {'a1':i,'b1':0,'c1':11}
		insert(table, request)
	ds = find(table,None,["b1"])
	for d in ds.cursor:
		assert "_id" in d
		assert "b1" in d 
		assert not "a1" in d
		assert not "c1" in d
	ds = find(table,None,['c1','b1'])
	for d in ds.cursor:
		assert "_id" in d
		assert "c1" in d
		assert "b1" in d
		assert not "a1" in d
	d = find_one(table,{"a1":0},['a1','c1'])
	assert "c1" in d
	assert "a1" in d
	assert "_id" in d
	assert not "b1" in d
	drop_table(table)

def test_mongo_map_reduce():
	table = 'sta'
	drop_table(table)
	
	for i in range(10):
		request = {'type':i,'html_phone':''}
		insert(table, request)
		
	mapfun = "function(){emit(this.type,1);}"
	reducefun = "function(key,values){return Array.sum(values);}"
	map_reduce('sta',mapfun,reducefun,"results")
	ds = find("results")
	k = 0
	while ds.next():
		assert ds["_id"] == k
		assert ds["value"] == 1
		k = k+1
		
	drop_table("results")
	ds = map_reduce('sta',mapfun,reducefun)
	k = 0
	for d in ds:
		assert d["_id"] == k
		assert d["value"] == 1
		k = k+1
	
def test_static_table():
	drop_table("c_test1")
	drop_table("u_test1")
	drop_table("u_main")
	insert_many("c_test1",[{"_id":1,"v":"a"},{"_id":2,"v":"b"},{"_id":3,"v":"c"}])
	insert_many("u_test1",[{"_id":1,"v":"a"},{"_id":2,"v":"b"},{"_id":3,"v":"c"}])
	insert_many("u_main",[{"vv":1},{"vv":2},{"vv":3}])
	ds = find("u_main").leftjoin("vv","c_test1") 
	ds2 = find("u_main").leftjoin("vv","u_test1",selectColumn=["v"])
	dd = ds.list()
	assert dd[0]["c_test1._id"] == 1
	assert dd[0]["c_test1.v"] == "a"
	assert dd[0]["vv"] == 1 
	assert dd[2]["c_test1._id"] == 3
	assert dd[2]["c_test1.v"] == "c"
	assert dd[2]["vv"] == 3
	dd = ds2.list()
	assert "u_test1._id" not in dd[2] 
	assert dd[0]["u_test1.v"] == "a"
	assert dd[0]["vv"] == 1 
	assert "u_test1._id" not in dd[2] 
	assert dd[2]["u_test1.v"] == "c"
	assert dd[2]["vv"] == 3
	assert 1 == len(dataset.static_tables)
	assert "c_test1" in dataset.static_tables
	
	delete_one("c_test1",{"v":"b"})
	delete_one("u_test1",{"v":"b"})
	
	ds = find("u_main").leftjoin("vv","c_test1")
	i = 0
	while ds.next():
		i = i + 1
		assert ds["c_test1.v"] in ["a","b","c"]
	assert 3 == i

	ds2 = find("u_main").leftjoin("vv","u_test1")	
	i = 0
	while ds2.next():
		i = i + 1
		assert ds2["u_test1.v"] in ["a",None,"c"]
	assert 3 == i
	
	drop_table("c_test1")
	drop_table("u_test1")
	drop_table("u_main")
	

def te1st_index():
	def get_ds_count(ds):
		i = 0
		while ds.next():
			i += 1
		return i
	
	ds = drop_index_by_table("a_test")
	i = get_ds_count(get_indexes("a_test"))
	assert i==0 or i == 1
	
	i1 = create_index("a_test",("aa","bb"))
	assert 2 == get_ds_count(get_indexes("a_test"))
	
	i2 = create_index("a_test",("aa"))
	assert 3 == get_ds_count(get_indexes("a_test"))
	
	drop_index("a_test",i1)
	assert 2 == get_ds_count(get_indexes("a_test"))
	
	drop_index("a_test",i2)
	assert 1 == get_ds_count(get_indexes("a_test"))
	
	drop_index_by_table("a_test")
	assert 1 == get_ds_count(get_indexes("a_test"))

def test_list():
	drop_table("u_ac")
	for i in range(10):
		d = {}
		d["_id"] = "a"+str(i)
		d["name"] = "n"+str(i)
		d["set"] = [1,2,3,4]
		insert("u_ac",d)
	ll = find("u_ac").list()
	assert 10 == len(ll)
	i = 0
	for l in ll:
		assert l["_id"] == "a"+str(i)
		assert l["name"] == "n"+str(i)
		assert l["set"] == [1,2,3,4]
		i = i+1
	
def test_perf():
	import mytimer
	t = mytimer.ticks()
	find("lalala")
	print((mytimer.ticks() - t)/1000.0)
	  
	t = mytimer.ticks()
	ds = find("r_ssid_stat").cursor
	v1 = 0
	v2 = 0
	for x in ds:
		v1 += x["txbytes"]
		v2 += x["rxbytes"]
	print((mytimer.ticks() - t)/1000.0)


	t = mytimer.ticks()
	ds = find("r_ssid_stat")
	v1 = 0
	v2 = 0
	while ds.next():
		v1 += ds["txbytes"]
		v2 += ds["rxbytes"]
		
	print((mytimer.ticks() - t)/1000.0)	

	
def test_sub_list():
	drop_table("r_system")
	
	data = []
	i = 0
	h = "testhost"
	for name in ["ntf","name","sta"]:
		i += 1
		a = {}
		a["pid"] = 10000+i
		a["seconds"] = 50000+i
		a["name"] = name
		a["status"] = "正常"
		data.append(a)
	update_one("r_system",{"_id":h},{"processes":data},update_or_insert=True)
	ds = find("r_system")
	i = 0
	while ds.next():
		assert len(ds["processes"]) == 3
		i = i+1
	assert i == 1
	
	i = 0
	update_one("r_system",{"_id":h+"2"},{"processes":data},update_or_insert=True)
	ds = find("r_system")
	while ds.next():
		assert len(ds["processes"]) == 3
		i = i+1
	assert i == 2
	
def test_update_set():
	table = 'test_db'
	drop_table(table)
	insert(table,{"_id":2, "value1":[]})
	
	update_set_add(table,{"_id":2},"value1",9)
	ds = find_one(table,{"_id":2})
	assert ds["value1"] == [9]
	assert ds["_id"] == 2
	
	update_set_add(table,{"_id":2},"value1",10)
	update_set_add(table,{"_id":2},"value1",11)
	update_set_add(table,{"_id":2},"value1",9)
	update_set_add(table,{"_id":2},"value1",9)
	ds = find_one(table,{"_id":2})
	assert ds["value1"] == [9,10,11]
	assert ds["_id"] == 2
	
	update_set_remove(table,{"_id":2},"value1",[9,10])
	ds = find_one(table,{"_id":2})
	assert ds["value1"] == [11]
	assert ds["_id"] == 2
	
	update_set_remove(table,{"_id":2},"value1",[11])
	ds = find_one(table,{"_id":2})
	assert ds["value1"] == []
	assert ds["_id"] == 2
	
	ds = find_one(table,{"_id":11012})
	assert not ds 
	
def test_update_array2():
	table = 'test_db'
	drop_table(table)
	insert(table,{"_id":2, "value1":[]})
	update_array_push(table,{"_id":2},"value1",9)
	update_array_push(table,{"_id":2},"value1",9)
	update_array_push(table,{"_id":2},"value1",9)
	ds = find_one(table,{"_id":2})
	assert ds["value1"] == [9,9,9]
	assert ds["_id"] == 2
	update_array_remove(table,{"_id":2},"value1",9)
	ds = find_one(table,{"_id":2})
	assert ds["value1"] == []
	assert ds["_id"] == 2
	
def test_update_array():
	table = 'test_db'
	drop_table(table)
	insert(table,{"_id":1, "value1":[1,2,3,4,5,6],"value2":["a1","b1"]})
	insert(table,{"_id":2, "value1":[],"value2":["a2","b2"]})
	
	update_array_push(table,{"_id":2},"value1",9)
	ds = find_one(table,{"_id":2})
	assert ds["value1"] == [9,]
	assert ds["_id"] == 2
	
	update_array_push(table,{},"value1",9,True)
	ds = find_one(table,{"_id":2})
	assert ds["value1"] == [9,9]
	assert ds["_id"] == 2
	ds = find_one(table,{"_id":1})
	assert ds["value1"] == [1,2,3,4,5,6,9]
	assert ds["_id"] == 1
	
	update_array_push(table,{"_id":1},"value1",(17,18))
	ds = find_one(table,{"_id":1})
	assert ds["value1"] == [1,2,3,4,5,6,9,17,18]
	assert ds["_id"] == 1
	
	update_array_remove(table,{"_id":1},"value1",[17,18])
	ds = find_one(table,{"_id":1})
	assert ds["value1"] == [1,2,3,4,5,6,9]
	assert ds["_id"] == 1
	
	update_array_remove(table,{},"value1",[9],True)
	ds = find_one(table,{"_id":1})
	assert ds["value1"] == [1,2,3,4,5,6]
	assert ds["_id"] == 1
	ds = find_one(table,{"_id":2})
	assert ds["value1"] == []
	assert ds["_id"] == 2
	
	drop_table(table)
	
	

def test_update2():
	table = 'test_db'
	drop_table(table)
	insert(table,{"_id":1, "value1":"value111" ,"value2":"value2222"})
	insert(table,{"_id":2, "value1":"value111" ,"value2":"value2233"})
	update_one(table,{"value1":"value111"},{"value1":"value1110000"})
	ds = find(table)
	assert ds.count == 2
	assert ds.next()
	assert ds["_id"] == 1
	assert ds["value1"] == "value1110000"
	assert ds["value2"] == "value2222"
	
	assert ds.next()
	assert ds["_id"] == 2
	assert ds["value1"] == "value111"
	assert ds["value2"] == "value2233"
	update_one(table,{"value1":"value111"},{"value1":"value1110000"})
	
	update_many(table,{"value1":"value1110000"},{"value1":"value11100011110"})
	ds = find(table)
	assert ds.count == 2
	assert ds.next()
	assert ds["_id"] == 1
	assert ds["value1"] == "value11100011110"
	assert ds["value2"] == "value2222"
	
	assert ds.next()
	assert ds["_id"] == 2
	assert ds["value1"] == "value11100011110"
	assert ds["value2"] == "value2233"
	
	update_one(table,{"value1":"value11188888"},{"value1":"valueggggggg"},True) 
	ds = find(table,{"value1":"valueggggggg"})
	assert ds.count == 1
	assert ds.next()
	assert ds["value1"] == "valueggggggg"
	update_many(table,{"value1":"value11188899"},{"value1":"valuegggggg22"},True)
	ds = find(table,{"value1":"valuegggggg22"})
	assert ds.next()
	assert ds["value1"] == "valuegggggg22"
	ds = find(table,{"value1":"value11100011110"})
	assert ds.count == 2
	
def test_del():
	table = 'test_db'
	drop_table(table)
	rr = []
	for i in range(100):
		rr.append({"_id":i, "value1":"value"+str(i),"value2":"value"+str(i*1000),"value3":1})
	insert_many(table,rr)	
	assert get_count(table) == 100
	delete_one(table,{"value3":1})
	assert get_count(table) == 99
	delete_one(table,{"value3":1})
	assert get_count(table) == 98
	delete_many(table,{"value3":1})
	assert get_count(table) == 0
	insert(table,{"_id":i, "value1":"value"+str(i),"value2":"value"+str(i*1000),"value3":1})
	drop_table(table)
	
def test_remove_field():
	table = 'test_db'
	drop_table(table)
	rr = []
	for i in range(10):
		rr.append({"_id":i, "value2":"value"+str(i*1000),"value3":1})
	insert_many(table,rr)
	remove_field(table,{"_id":0},"value2")
	ds = find_one(table,{"_id":0})
	assert len(ds) == 2
	assert ds["_id"] == 0
	assert ds["value3"] == 1
	
	remove_field(table,{"value3":1},["value2","value3"],True)
	ds = find(table)
	for x in ds.cursor:
		assert len(x) == 1
		assert "_id" in x
	drop_table(table)

def test_rename_field():
	table = 'test_db'
	drop_table(table)
	rr = []
	for i in range(10):
		rr.append({"_id":i, "value2":"value"+str(i*1000),"value3":1})
	insert_many(table,rr)
	rename_field(table,{"_id":0},{"value2":"value4"})
	ds = find_one(table,{"_id":0})
	assert len(ds) == 3
	assert ds["_id"] == 0
	assert ds["value3"] == 1
	assert ds["value4"] == "value0"
	
	rename_field(table,{"value3":1},{"value2":"value4"},True)
	ds = find(table)
	for x in ds.cursor:
		assert len(x) == 3
		assert "_id" in x
		assert "value3" in x
		assert "value4" in x
	drop_table(table)	
	
	
def test_left_join():
	table = 'test_db'
	table2 = "test_db2"
	table3 = "test_db3"
	drop_table(table)
	drop_table(table2)
	drop_table(table3)
	request = {}
	for i in range(10):
		request = {'name':'comba' + str(i),'type':'machine'+ str(i+100),"value":i,"value2":i+1000}
		insert(table, request)
	
	rr = []
	for i in range(4):
		request = {"_id":i, "value1":"value"+str(i),"value2":"value"+str(i*1000)}
		insert(table2, request)
		
	for i in range(100):
		request = {"myid":i+1000,"value333":"value"+str(i*1000)}
		rr.append(request)
	r = insert_many(table3, rr)
	assert 100 == get_count(table3)
		
	db = query(table).leftjoin("value",table2).leftjoin("value2",table3,"myid")
	assert 10 == db.count
	for i in range(4):
		assert db.next()
		assert db["no_exist"] == None
		assert db.get("no_exist") == None
		
		assert db["name"] == 'comba' + str(i)
		assert db["type"] == 'machine'+ str(i+100)
		assert db["value"] == i
		assert db.get("name") == 'comba' + str(i)
		assert db.get("test_db2._id") ==  i
		assert db.get("test_db2.value1") ==  "value"+str(i)
		assert db.get("test_db2.value2") ==  "value"+str(i*1000)
		assert db.get("test_db3.value333") ==  "value"+str(i*1000)
		assert db.get("test_db3.myid") ==  i+1000
		assert not db.get("test_db2.value3")
	
	for i in range(4,10):
		assert db.next()
		assert db["name"] == 'comba' + str(i)
		assert db["type"] == 'machine'+ str(i+100)
		assert db["value"] == i
		assert db.get("name") == 'comba' + str(i)
		assert db.get("test_db2.value1") ==  None
		assert db.get("test_db2.value2") ==  None
		assert db.get("test_db3.value333") ==  "value"+str(i*1000)
		assert db.get("test_db3.myid") ==  i+1000
		
		assert db.name == 'comba' + str(i)
		assert db.type == 'machine'+ str(i+100)
		assert db.value == i
		assert db.name == 'comba' + str(i)
		
def test_mongo_update():
	table = 'test_mongo_db'
	drop_table(table)
	condition = {'name':'comba'}
	request = {'type':'comnunicate'}
	update_many(table,condition,request,False)
	ret = get_count(table)
	assert ret == 0
	
	update_many(table,condition,request,True)
	ret = get_count(table)
	assert ret == 1 
	ds = query(table,condition)
	assert ds.next() is True
	assert ds.get('name') == 'comba'
	assert ds.get('type') == 'comnunicate'
	request = {'type':'company'}
	
	update_many(table,condition,request,False)
	ret = get_count(table)
	assert ret == 1
	ds = query(table,condition)
	assert ds.next() is True
	assert ds.get('name') == 'comba'
	assert ds.get('type') == 'company'
	drop_table(table)

def test_mongo_inc():
	table = 'test_mongo_db'
	drop_table(table)
	request = {"_id":1,'name':'comba','no1':1,"no2":1000000}
	insert(table, request)
	
	request.clear()
	request = {"_id":2,'name':'comba','no1':111110,"no2":10220}
	insert(table, request)
	
	condition = {'name':'comba'}
	request = {'no1':2,"no2":-9999}
	increase(table,condition,request)
	
	ds = query(table).sort("_id",ASCENDING)
	assert ds.next()
	assert ds._id == 1
	assert ds.get('name') == 'comba'
	assert ds.no1 == 3
	assert ds.no2 == 1000000 - 9999
	
	assert ds.next()
	assert ds._id == 2
	assert ds.get('name') == 'comba'
	assert ds.no1 == 111110
	assert ds.no2 == 10220
	
	request = {'no1':-10000}
	increase(table,condition,request,True)
	ds = query(table).sort("_id",ASCENDING)
	assert 2 == ds.count
	assert ds.next()  
	assert ds.get('name') == 'comba'
	assert ds.get('no1') == 3 -10000
	assert ds.get('no2') == 1000000 - 9999
	assert ds.next()  
	assert ds.get('name') == 'comba'
	assert ds.get('no1') == 111110 -10000
	assert ds.get('no2') == 10220
	drop_table(table)

	
def test_dataset():
	table = 'test_db'
	drop_table(table)
	request = {}
	for i in range(10):
		request = {'name':'comba' + str(i),'type':'machine'+ str(i+100),"value":i}
		insert(table, request)
	db = query(table)
	assert db.is_countable
	assert 10 == db.count
	for i in range(10):
		assert db.next()
		assert db["name"] == 'comba' + str(i)
		assert db["type"] == 'machine'+ str(i+100)
		assert db["value"] == i
		assert db.get("name") == 'comba' + str(i)
	assert not db.next()
	
	db.rewind()
	for i in range(10):
		assert db.next()
		assert db["name"] == 'comba' + str(i)
		assert db["type"] == 'machine'+ str(i+100)
		assert db["value"] == i
		assert db.get("name") == 'comba' + str(i)
	assert not db.next()
	
	match = {'$match':{'value':{'$gt':5}}}
	ds = aggregate(table,match)
	assert not ds.is_countable
	assert -1 == ds.count
	i = 6
	while ds.next():
		assert ds["name"] == 'comba' + str(i)
		assert ds["type"] == 'machine'+ str(i+100)
		assert ds["value"] == i
		i+=1
	assert i == 10	

def test_mongo_threads():
	print ('running test_mongo_threads')
	table = 'test_mongo_db'
	def thread1():
		now = utility.now()
		for i in range(20):
			key = 'comba%d' % int(i)
			value = 'machine%d' % int (i)
			request = {'name':key,'type':value}
			lock.sleep(0.01)
			insert(table,request)

	def thread2():
		for i in range(100):
			lock.sleep(0.01)
			ds = query(table,'')

	tt = []
	for i in range(10):
		tt.append(threading.Thread(target=thread1))
	for i in range(8):
		tt.append(threading.Thread(target=thread2))

	for t in tt:
		t.start()
	
	for t in tt:
		t.join()

	assert 200 == get_count(table)
	delete_many(table,'')
	assert 0 == get_count(table)
	print ('running test_mongo_threads finished')
	
def t1est_mongo_master_slave():	
	i = 0
	while i < 1000:		
		table = 'test_mongo_db'
		request = {'name':'comba','type':'machine'}
		insert(table, request)
		ret = get_count(table)
		assert ret == 1	
		condition = {'name':'comba'}
		ds = query(table,condition)
		assert ds.next() is True
		assert ds.get('name') == 'comba'
		assert ds.get('type') == 'machine'
		
		request = {'type':'comnunicate'}
		update(table,condition,request)
		ds = query(table,condition)
		assert ds.next() is True
		assert ds.get('name') == 'comba'
		assert ds.get('type') == 'comnunicate'
		delete(table, condition)
		ret = get_count(table)
		assert ret == 0
		i += 1


					 
def test_mongo_group():
	print ('running test_mongo_group')
	table = 'testbigdata'
	drop_table(table)
	request = {'mac_src':'00-00-00-00-00-00','html_phone':''}
	insert(table, request)
	request = {'mac_src':'00-00-00-00-00-01','html_phone':'huawei'}
	insert(table, request)
	request = {'mac_src':'00-00-00-00-00-01','html_phone':'huawei'}
	insert(table, request)
	request = {'mac_src':'00-00-00-00-00-02','html_phone':''}
	insert(table, request)
	request = {'mac_src':'00-00-00-00-00-02','html_phone':'xiaomi'}
	insert(table, request)
	request = {'mac_src':'00-00-00-00-00-02','html_phone':'xiaomi'}
	insert(table, request)
	request = {'mac_src':'00-00-00-00-00-02','html_phone':'xiaomi'}
	insert(table, request)
	request = {'mac_src':'00-00-00-00-00-03','html_phone':'xiaomi'}
	insert(table, request)
	ret = get_count(table)
	assert ret == 8
	key = {'html_phone':True}
	condition = None
	initial = {'phones':0,'mac_list':[]}
	reducefun = bson.code.Code("function(doc,prev)"
								"{"
								"if (prev.mac_list.indexOf(doc.mac_src) == -1)"
								"{prev.mac_list.push(doc.mac_src);prev.phones=prev.mac_list.length;}"
								"}")
	finalize = bson.code.Code("function(prev){delete prev.mac_list;}")
	result = group(table,key,condition,initial,reducefun,finalize)
	assert len(result) == 3
	for i in range(len(result)):
		if result[i]['html_phone'] == '':
			assert result[i]['phones'] == 2
		elif result[i]['html_phone'] == 'huawei':
			assert result[i]['phones'] == 1
		elif result[i]['html_phone'] == 'xiaomi':
			assert result[i]['phones'] == 2
	condition = {'html_phone':{'$ne':''}}
	result = group(table,key,condition,initial,reducefun,finalize)
	assert len(result) == 2
	for i in range(len(result)):
		if result[i]['html_phone'] == 'huawei':
			assert result[i]['phones'] == 1
		elif result[i]['html_phone'] == 'xiaomi':
			assert result[i]['phones'] == 2
	match = {'$match':{'html_phone':{'$nin':['',None]}}}
	group_pip1 = {'$group':{'_id':{'phone':'$html_phone','mac':'$mac_src'}}}
	group_pip2 = {'$group':{'_id':"$_id.phone",'count':{'$sum':1}}}
	pipline = [match,group_pip1,group_pip2]
	result = aggregate(table,pipline)
	assert result.next() is True
	assert result['_id'] == 'huawei'
	assert result['count'] == 1
	assert result.next() is True
	assert result['_id'] == 'xiaomi'
	assert result['count'] == 2
	drop_table(table)
	print ("finished")
	
def test_stat():
	drop_table("test_ycat")
	test_mongo_map_reduce()
	
	_get_mongodb().stat.stat.clear()
	data = [{ "_id" : 1, "item" : "f1", "type": "food", "quantity": 500 },
			{ "_id" : 2, "item" : "f2", "type": "food", "quantity": 100 },
			{ "_id" : 3, "item" : "p1", "type": "paper","quantity": 200 },
			{ "_id" : 4, "item" : "p2", "type": "paper","quantity": 150 },
			{ "_id" : 5, "item" : "f3", "type": "food", "quantity": 300 },
			{ "_id" : 6, "item" : "t1", "type": "toys", "quantity": 500 },
			{ "_id" : 7, "item" : "a1", "type": "apparel", "quantity": 250 },
			{ "_id" : 8, "item" : "a2", "type": "apparel", "quantity": 400 },
			{ "_id" : 9, "item" : "t2", "type": "toys", "quantity": 50 },
			{ "_id" : 10, "item" : "f4","type": "food", "quantity": 75 }]
	insert_many("test_ycat",data)
	_get_mongodb().stat.stat.clear()
	find("test_ycat", { "quantity": { "$gte": 100, "$lte": 200 }})
	assert 1 == len(_get_mongodb().stat.stat)
	findFlag = False
	for s in _get_mongodb().stat.stat:
		if s.find("find") == -1:
			continue
		findFlag = True
		s = _get_mongodb().stat.stat[s]
		assert s.bucket.count == 1
		assert s.successCount == 1
		assert s.failCount == 0
		assert s.totalExamDoc == 10
		assert s.totalKeyExamDoc == 0
		assert s.totalRetDoc == 3
		assert s.indexCount == 0
		break 
	assert findFlag
	findFlag = False
	create_index("test_ycat","quantity")
	ee = find("test_ycat", { "quantity": { "$gte": 100, "$lte": 200 }}).explain()
	assert 2 == len(_get_mongodb().stat.stat)
	for s in _get_mongodb().stat.stat: 
		if s.find("find") == -1:
			continue
		s = _get_mongodb().stat.stat[s]
		findFlag = True
		assert s.bucket.count == 2
		assert s.successCount == 2
		assert s.failCount == 0
		assert s.totalExamDoc == 13 
		assert s.totalKeyExamDoc == 3
		assert s.indexCount == 1
		assert s.totalRetDoc == 6
		break
	assert findFlag
	findFlag = False
	create_index("test_ycat", ["quantity","type"])
	find("test_ycat",{"quantity": { "$gte": 100, "$lte": 300 }, "type": "food" })
	assert 2 == len(_get_mongodb().stat.stat)
	for s in _get_mongodb().stat.stat:
		if s.find("find") == -1:
			continue
		findFlag = True
		s = _get_mongodb().stat.stat[s]
		assert s.bucket.count == 3
		assert s.successCount == 3
		assert s.failCount == 0
		assert s.totalExamDoc == 13 + 2 
		assert s.totalKeyExamDoc == 3 + 6
		assert s.indexCount == 2
		assert s.totalRetDoc == 6+2
		break
	assert findFlag
	drop_table("test_ycat")
	
if __name__== "__main__":
	utility.run_tests()
#	test_stat()
	
	
	