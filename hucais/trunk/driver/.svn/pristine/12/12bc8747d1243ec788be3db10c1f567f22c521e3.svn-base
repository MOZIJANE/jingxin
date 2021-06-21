#!/usr/bin/env python3.2
# -*- coding: utf-8 -*-
import pymongo
import threading
import sys
#import bson.code
import time
import json
import os
import configparser

#ObjectId = bson.objectid.ObjectId


class empty_class:
	pass


class mongodb(object):
	def __init__(self):
		self.db = None
		self.account = ''
		self.passwd = ''
		self.conn = None
		self.query = self.find
		self.query_one = self.find_one
		self.update_set_remove = self.update_array_remove
		self.dbIP = ''
		
	def disconnect(self):
		self.conn.close()	
		self.db = None
		
	def get_conn(self):
		if self.db is None:
			self._get_db()
		return self.conn
			
	def insert(self, table, request):
		return self._get_db()[table].insert_one(request)
		
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
		return dataset(self._get_db()[table].find(filter=filter,projection=columns))

	def find_one(self, table, filter = None, columns=None):
		return self._get_db()[table].find_one(filter=filter,projection=columns)

	def create_index(self, table, index):
		return self._get_db()[table].create_index(index)

	#index对象["index1","index2",...,"indexN"] 
	def create_indexs(self, table, index):
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
		if isinstance(pipeline,dict):
			return dataset(self._get_db()[table].aggregate([pipeline,], **kwargs))
		return dataset(self._get_db()[table].aggregate(pipeline, **kwargs))

	#如果out为inline时，返回list<dict<_id,value>>的字典
	#如果out不为inline，还需要调用map_reduce(), out.find())来取得dataset
	#可以使用query="xxx"等参数
	#If full_response is False (default) returns the result documents in a list,
	#Otherwise, returns the full response from the server to the map reduce command.
	def map_reduce(self,table, mapper,reducer,out={"inline":1},full_response=False,**kwargs):
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
				print('Connect mongodb error!')
				self.db = None
				self.conn.close()

		serverlist = self.dbIP #config.get("mongo","servers")
		dbname = 'scada2' #config.get("mongo","db")
		replica = 'comba' #config.get("mongo","replica")
		self.account = 'comba' #config.get("mongo","user")
		self.passwd = '123456' #config.get("mongo","pwd")
		assert dbname != ""
		assert serverlist != ""
		
		servers = str(serverlist).split(',')
		try:
			for ss in servers:
				server = ss.split(':')
				self.conn = pymongo.MongoClient(server[0],int(server[1]))
				time.sleep(3)
				
				#在终端下，发现is_primary是非阻塞，所以要sleep 3 秒等待判断返回
				if self.conn.is_primary:
					print("Connect to %s port %s" %(self.conn.address[0],self.conn.address[1]))
					break
				else:
					self.conn.close()
			
			self.db = pymongo.database.Database(self.conn,dbname)
			#ret = self._auth(self.account, self.passwd)
			if not ret:
				print('Config mongodb auth failed!')
				self.db = None
				self.conn.close()
		except (pymongo.errors.InvalidName,pymongo.errors.NetworkTimeout,pymongo.errors.ServerSelectionTimeoutError) as e:
			self.db = None
			self.conn.close()
			print('Connect mongodb error!')
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
		assert not self.isPrinted
		if self.cursor.alive and self.count != 0:
			if self.count != -1 and self.next_count >= self.count:
				return False
			try:
				self._row = self.cursor.next()
			except StopIteration as e:
				print('mongodb cursor error!')
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
	def leftjoin(self,col,join_table,join_col="_id"):
		d = empty_class()
		d.col = col
		d.join_col = join_col
		d.join_table = join_table
		
		data = dataset._get_static_table(join_table)
		if data is None:
			data = {}
			ds = find(join_table)
			for v in ds.cursor:
				data[str(v[join_col])] = v
			dataset._save_static_table(join_table,data)
		d.data = data
		self.lefts[join_table] = d
		return self
		
	def _left_join_info(self,col):
		for d in self.lefts:
			if col.find(d+".") == 0:
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
		#不支持leftjoin
		self.rewind()
		ret = []
		for x in self.cursor:
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
		fileName = './default.ini'
		if not os.path.exists(fileName):
			fileName = os.path.dirname(__file__) + '/default.ini'
			if not os.path.exists(fileName):
				print('can not find default.ini file!')
				exit(1)
		config = configparser.ConfigParser()
		config.read(fileName)
		g_mongodb.dbIP = str(config.get("database", "ip"))
	return g_mongodb

insert			  = _get_mongodb().insert
insert_many		 = _get_mongodb().insert_many

update_one		  = _get_mongodb().update_one
update_many		 = _get_mongodb().update_many

update_op_one		   = _get_mongodb().update_op_one
update_op_many		   = _get_mongodb().update_op_many

#删除doc的某个列 
remove_field	= _get_mongodb().remove_field

#修改某一列的名字
rename_field	= _get_mongodb().rename_field

#在队列中增加值  
update_array_push = _get_mongodb().update_array_push

#在队列中删除值 
update_array_remove = _get_mongodb().update_array_remove

#在集合中增加值 
update_set_add = _get_mongodb().update_set_add

#在集合中删除值 
update_set_remove = _get_mongodb().update_set_remove

#对doc的某些列做加减运算
increase			= _get_mongodb().increase

delete_many		 = _get_mongodb().delete_many
delete_one		  = _get_mongodb().delete_one

find				= _get_mongodb().find
find_one			= _get_mongodb().find_one

#给函数起个别名
query_one = find_one
query = find

get_count = _get_mongodb().get_count
get_table_name_list = _get_mongodb().get_table_name_list
create_index = _get_mongodb().create_index
create_indexs = _get_mongodb().create_indexs
create_index_op = _get_mongodb().create_index_op
get_indexes = _get_mongodb().get_indexes
drop_index = _get_mongodb().drop_index
drop_index_by_table = _get_mongodb().drop_index_by_table
drop_table = _get_mongodb().drop_table
group = _get_mongodb().group
aggregate = _get_mongodb().aggregate
map_reduce = _get_mongodb().map_reduce
disconnect = _get_mongodb().disconnect  


#############################	unit test	###########################

	
if __name__== "__main__":
	find('111', {'_id':'111'})
	pass
	
