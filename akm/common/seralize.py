#coding=utf-8 
# ycat			 2015/03/10      create
# 数据库管理类
#设计目标：支持mysql,sqlite，支持py2.x和py3.x
import sys,os,datetime
import utility
import uuid
import memcache
import db
from functools import partial
import json_codec
#TODO:在多进程并发时，memcache和database不一定一致，这时需要考虑使用分存式进程锁
#TODO: data_cache为什么不在update时更新，是因为多进程并发时，可能带来不一致性，所以还是重load数据库可靠 

#修饰符
#用于标识数据库表名和主键,params为多主键的情况
#注意主键是数据库的主健，不是类的成员变量名 
def table(table_name,primary,*params):
	def __call(cls):
		c = _get_cfg(cls)
		assert c.table == ""
		c.table = table_name
		c.classname = utility.classname(cls)
		c.primary.append(primary)
		c.primary += params
		return cls
	return __call	

#修饰符
#用于标识数据库中的自增列
def auto_increase(field_name):
	def __call(cls):
		assert _get_cfg(cls).increase_field is None #只能有一个递增列
		_get_cfg(cls).increase_field = field_name
		return cls
	return __call	

#修饰符 
#用于标注成员变量和数据库列的对应关系
#如果没有该修饰符，则表示成员变量和数据列名一一映射 
def field(attr_name,filed_name):
	def __call(cls):
		a = attr_name
		f = filed_name
		if (a is None) or (a == ""):
			a = filed_name
		elif (f is None) or (f == ""):
			f = attr_name
		_get_cfg(cls).mapping[f] = a
		return cls
	return __call	

#修饰符
#用于标识该成员变量无需序列化，不要和field一起使用 
def ignore(attr_name):
	def __call(cls):
		_get_cfg(cls).ignore.add(attr_name)
		return cls
	return __call	

#修饰符
#用于标识数据库中的列，但这个列是由函数生成的 
def dynamic_field(func_name,filed_name):
	def __call(cls):
		_get_cfg(cls).dynamic[filed_name] = func_name
		return cls
	return __call	

#支持可序列化的类管理 		
class manager:	
	def __init__(self, classtype):
		self.cfg = _get_cfg_by_class(classtype)
		if self.cfg.increase_field:
			assert self.cfg.increase_field in self.cfg.primary  #递增列，必须是主键之一  
		self.data_cache = None
		self.data_cache_seed = None #用于判断数据有没有被其它进程修改
		o = utility.create_obj(self.cfg.classname)
		self.cfg._create_table(o)
	
	def get_all_data(self):
		if self._is_seed_change():
			self.data_cache = {}
			sql = "SELECT * FROM " + self.cfg.table
			ds = db.query(sql)
			while ds.next():
				o = utility.create_obj(self.cfg.classname)
				if self.cfg._load(ds,o):
					memcache.set(self.cfg.key(o),o)
					self.data_cache[self.cfg.key(o)]=o
		return self.data_cache.values()
	
	def get(self,*primary_keys):
		return memcache.get(self.cfg.make_key(*primary_keys),partial(self._load_data,primary_keys))
	
	def is_exist(self,*primary_keys):
		return self.get(*primary_keys) is not None
		
	def save(self,obj): 
		self.cfg._save(obj,True)
		memcache.set(self.cfg.key(obj),obj)
		self._update_seed()
		return obj
		
	def update(self,obj,cols=None):
		self.cfg._update(obj,cols)
		if cols is None:
			memcache.set(self.cfg.key(obj),obj)
		else:
			memcache.delete(self.cfg.key(obj))
		self._update_seed()
		return obj
		
	def delete(self,*primary_keys):
		self._delete(self.get(*primary_keys),True)
	
	def print_all(self):
		#需重load数据库，速度慢 
		for x in self.get_all_data():
			utility.print_obj(x)
	
	@property	
	def count(self):
		#需重load数据库，速度慢 
		return len(self.get_all_data())
		
	#filer_func为过滤的函数，原型为filer_func(obj)
	#如果需要传参数，则需要使用from functools import partial的技术
	#需重load数据库，速度慢 		
	def delete_all(self,filer_func=None):
		r = []
		for o in self.get_all_data():
			if filer_func and not filer_func(m[o]):
				continue
			r.append(o)
			
		for o in r:
			self._delete(o,False)
		db.commit()
		self._update_seed()
			
	def _load_data(self,params,key):
		o = utility.create_obj(self.cfg.classname)
		return self.cfg._load_data(o,*params) 
	
	def _is_seed_change(self):
		if not utility.is_test():
			return True
		#TODO:没开memcache，所以永远为True
		v = memcache.get(self.cfg.make_seed())
		if v is None:
			self.data_cache_seed = None
			return True
		if v != self.data_cache_seed:
			self.data_cache_seed = v
			return True
		return False
	
	def _update_seed(self):
		u =uuid.uuid1()
		memcache.set(self.cfg.make_seed(),u)
		
	def _delete(self,obj,commit=True):
		if obj is not None:
			memcache.delete(self.cfg.key(obj))
			self.cfg._delete(obj,commit)
			if commit:
				self._update_seed()	

def _update_cfg(cfg):
	if len(cfg.mapping) == 0:
		obj = utility.create_obj(cfg.classname)
		for x in obj.__dict__:
			if x in cfg.ignore:
				continue
			if x[0] == "_":
				continue
			cfg.mapping[x] = x
			

def _get_cfg_by_table_name(table_name):
	global _g__seralize_cfg
	for c in _g__seralize_cfg:
		if _g__seralize_cfg[c].table == table_name:
			cfg = _g__seralize_cfg[c]
			_update_cfg(cfg)
			return cfg
	return None	

def _get_cfg_by_class(obj):
	global _g__seralize_cfg
	t = obj
	if not isinstance(obj,type):
		t = type(obj)
	if t in _g__seralize_cfg:
		cfg = _g__seralize_cfg[t]
		_update_cfg(cfg)
		return cfg
	return None

#配置database和object的映射关系
class _seralize_cfg:
	@staticmethod
	def _default_handle(*param):
		return True

	def __init__(self):
		self._check_table = False	#是否已经检查表存在情况 
		self.mapping = {}		#数据库字段和字段的映射key=db.column,value=class.member
		self.primary = [] 		#数据库的主键
		self.dynamic = {}		#动态的列名和对应函数名
		self.table = ""  		#数据库表名
		self.classname = ""		#需要映射的类名
		self.ignore = set()		#忽略的类字段名 
		self.increase_field = None	#自增列
		
		#数据库操作事件,before_xxx返回False代表终止操作
		self.before_insert = _seralize_cfg._default_handle
		self.after_insert = _seralize_cfg._default_handle
		
		self.before_update = _seralize_cfg._default_handle
		self.after_update = _seralize_cfg._default_handle
		
		self.before_del = _seralize_cfg._default_handle
		self.after_del = _seralize_cfg._default_handle
		
		self.before_load = _seralize_cfg._default_handle
		self.after_load = _seralize_cfg._default_handle
		
			
	def has_primary(self,cols):
		for c in cols:
			if self.is_primary_col(c):
				return True
		return False

	def is_primary_col(self,col):
		for c in self.primary:
			if c == col:
				return True
		return False	
		
	def get_noprimary_cols(self):
		r = []
		for c in self.mapping:
			if not self.is_primary_col(c):
				r.append(c)	
		return r

		
	@staticmethod
	def _make_key(values):
		if not isinstance(values,(list,tuple)):
			return str(values)
		if len(values) == 1:
			return _seralize_cfg._make_key(values[0])
		s = ""
		first = True
		for v in values:
			if not first:
				s += "@@"
			first = False
			s += str(v)
		return s	 

	def make_key(self, *param):
		return self.classname + "." + _seralize_cfg._make_key(param)

	def make_seed(self):
		return self.classname + "." + "cacheseed"

	def get_primary_sql(self,values):
		cond = ""
		f = True
		if not isinstance(values,(tuple,list)):
			assert len(self.primary) == 1
			return " %s=%s " % (self.primary[0],db.escape(values))
		
		assert len(values) == len(self.primary)
		for index,k in enumerate(self.primary):
			if not f:
				cond += "AND"
			f = False
			
			a = values[index]
			cond += " %s=%s " % (k,db.escape(a))
		return cond
		
	def key(self,obj):
		if hasattr(obj,"_seralize_key") and obj._seralize_key:
			return obj._seralize_key
		v = []
		for p in self.primary:
			c = self._get_attr(p)
			v.append(self._get_attr_val(obj,c))
		obj._seralize_key =  self.make_key(v)
		return obj._seralize_key

	def _load_data(self,obj,*params):
		ds = db.query("SELECT * FROM " + self.table + " WHERE " + self.get_primary_sql(params))
		if ds.next():
			if obj is None:
				obj = utility.create_obj(self.classname)
			if self._load(ds,obj):
				return obj
		return None
	
	#根据主键，重读数据库的数据 
	def _reload(self,obj):
		return self._load_data(obj,*self._get_primary_values(obj))	

	def _load(self,ds,obj):
		r = self.before_load(obj,ds)
		assert r is not None
		if not r:
			return False
		for col in ds.cols:
			if col in self.mapping:
				if self._is_bool(obj,col):
					if ds[col]:
						self._set_val(obj,col,True)
					else:
						self._set_val(obj,col,False)
				else:		
					self._set_val(obj,col,ds[col])
		r = self.after_load(obj,ds)
		assert r is not None
		return r
	
	def _save(self,obj,check_exist=False):
		if check_exist and self.increase_field is None and self._is_exist(obj):
			#判断是否已经存在
			self._update(obj)
			return False
		
		r = self.before_insert(obj)
		assert r is not None
		if not r:
			return False
		
		vv = ""
		for x in self.mapping:
			v = self._get_attr(x)
			if len(vv) != 0:
				vv += ", "
			if v == self.increase_field:
				vv += "NULL"
				continue 
			if not hasattr(obj,v): #配置的列，必需存在于类属性中
				raise Exception("{0} hasn't attribute {1}".format(obj,v))
			vv += db.escape(self._get_attr_val(obj,v))
		
		if len(self.dynamic):
			for x in self.dynamic:
				if len(vv) != 0:
					vv += ", "
				vv += db.escape(getattr(obj, self.dynamic[x])())	
		sql = "INSERT INTO %s(%s)VALUES(%s)"%(self.table,",".join(list(self.mapping.keys())+list(self.dynamic.keys())),vv)
		db.execute(sql)
		
		if self.increase_field is not None:
			v = db.query_single("SELECT LAST_INSERT_ID()")
			self._set_val(obj,self.increase_field,v)
		
		r = self.after_insert(obj)
		assert r is not None
		if not r:
			return False
		
		db.commit()
		return True

	def _delete(self,obj,commit=True):
		r = self.before_del(obj)
		assert r is not None
		if not r:
			return False		
		sql = "DELETE FROM " + self.table + " WHERE " + self._get_primary_sql(obj)
		db.execute(sql)
		
		r = self.after_del(obj)
		assert r is not None
		if not r:
			return False
		if commit:
			db.commit()
		return True

	#主键是不可以更新的 
	#cols为需要更新的列，主键不能更新，否则为全部更新，cond为需要更新附加条件  
	def _update(self,obj,cols=None):
		r = self.before_update()
		assert r is not None
		if not r:
			return False
		if cols is None:
			cols = self.get_noprimary_cols()
		assert not self.has_primary(cols)
		if len(cols) == 0:
			return False
		
		sql = "UPDATE " + self.table + " SET "
		first = True
		for c in cols:
			if not first:
				sql += ","
			first = False
			c2 = self._get_attr(c)
			assert c2 #更新列找不到
			sql += c + "=" + db.escape(self._get_attr_val(obj,c2))
			
		if len(self.dynamic):
			for c in self.dynamic:
				if not first:
					sql += ","
				first = False
				r = getattr(obj, self.dynamic[c])()  		
				sql += c + "=" + db.escape(r)
			
		sql += " WHERE "+self._get_primary_sql(obj)
		db.execute(sql)
		r = self.after_update()
		assert r is not None
		if not r:
			return False
		db.commit()
		return True

	def _get_attr_val(self,obj,col):
		if hasattr(obj,col):
			return getattr(obj,col)
		return "Null"

	def _get_attr(self,col):
		return self.mapping[col]

	def _set_val(self,obj,col,val):
		a = self._get_attr(col)
		if self._is_bool(obj,a):
			if val:
				setattr(obj,a,True)
			else:
				setattr(obj,a,False)
		else:
			setattr(obj,a,val)
	
	def _is_bool(self,obj,a):
		if not hasattr(obj,a):
			return False
		return isinstance(getattr(obj,a),bool)

	def _get_primary_values(self,obj):
		values = []
		for k in self.primary:
			a = self._get_attr(k)
			assert hasattr(obj,a) #主键必需有值
			values.append(getattr(obj,a))
		return values	

	def _get_primary_sql(self,obj):
		return self.get_primary_sql(self._get_primary_values(obj))

	def _is_exist(self,obj):
		return db.query_single("SELECT COUNT(*) FROM " + self.table + " WHERE " + self._get_primary_sql(obj))	

	def _get_column_typestr(self,p,col):
		if isinstance(p,str):
			if col in self.primary: #mysql主键不能太长 
				return "varchar(255) DEFAULT '' NOT NULL"	
			else:
				return "varchar(512) DEFAULT '' NOT NULL"	
		if isinstance(p,datetime.datetime):
			return "datetime NOT NULL"	
		if not utility.is_python3() and isinstance(p,long):
			if self.increase_field != col:
				return "int(11) DEFAULT 0  NOT NULL"
			else:
				return "int(11) NOT NULL AUTO_INCREMENT"
		if isinstance(p,(int,bool)):
			if self.increase_field != col:
				return "int(11) DEFAULT 0  NOT NULL"
			else:
				return "int(11) NOT NULL AUTO_INCREMENT"
		if col in self.primary: #mysql主键不能太长 
			return "varchar(255) DEFAULT '' NOT NULL"		
		return "varchar(512) DEFAULT '' NOT NULL"	

	def _create_table(self,obj):
		if self._check_table:
			return
		if db.is_table_exist(self.table):
			self._check_table = True
			return
		self._check_table = True		
		sql = "CREATE TABLE IF NOT EXISTS %s("%self.table
		for m in self.mapping:
			v = getattr(obj, self.mapping[m])
			sql += "`%s` %s" % (m,self._get_column_typestr(v,m)) + ","
		for x in self.dynamic:
			v = getattr(obj, self.dynamic[x])()
			sql += "`%s` %s" % (x,self._get_column_typestr(v,x)) + ","
		sql += " PRIMARY KEY(" + ",".join(self.primary)
		sql += ")) ENGINE=MyISAM DEFAULT CHARSET=utf8;"
		db.execute(sql)		
	
_g__seralize_cfg = {}
def _get_cfg(cls):
	global _g__seralize_cfg
	if cls in _g__seralize_cfg:
		return _g__seralize_cfg[cls]
	c = _seralize_cfg()
	_g__seralize_cfg[cls] = c
	return c

#############################	unit test	###########################
@table("test_create_table","a1","a2")
@auto_increase("a1")
@dynamic_field("a8_func","a8")
class tttt3:
	def __init__(self, ):
		self.a1 = 11
		self.a2 = "abc"
		self.a3 = "abc3434"
		self.a4 = 256.25
		self.a5 = True
		self.a6 = utility.now()
		self.a7 = 0
	def a8_func(self):
		return "lalala"
		
def xxtest_create_table():
	db.drop_table("test_create_table")	
	assert not db.is_table_exist("test_create_table")
	m = manager(tttt3)
	t1 = tttt3()
	t1.a3 = "dfdfdf"
	m.save(t1)
	assert m.get(t1.a1,t1.a2).a3 == "dfdfdf"
	assert db.is_table_exist("test_create_table")
	db.drop_table("test_create_table")	

def xxtest_cfg_decorator():
	@table("u_ggg2","field1") #单主键
	@field("a1","field1")
	class gggg2:
		def __init__(self):
			self.a1 = 1
			
	c = _get_cfg_by_class(gggg2())
	utility.assert_array_noorder(c.primary,["a1"])
	assert utility.equal(c.mapping,{"field1":"a1"})
	assert c.classname == "common.seralize.gggg2"
	assert id(c) == id(_get_cfg_by_table_name("u_ggg2"))
	assert c.get_primary_sql("aaa") == " field1='aaa' "
	assert c.is_primary_col("field1")
	
	@table("u_ggg","field1","field2","field3") #多主键
	@field("a1","field1")
	@field("a2","field2")
	@field("a3","field3")
	@field("b1","fieldb1")
	@field("b2","fieldb2")
	class gggg:
		def __init__(self):
			self.a1 = 1
			self.a2 = "abc"
			self.a3 = "abc3434"
			self.b1 = 411
			self.b2 = 256.25
	g = gggg()
	c = _get_cfg_by_class(g)
	assert c.table == "u_ggg"
	utility.assert_array_noorder(c.primary,["a1","a2","a3"])
	assert utility.equal(c.mapping,{"field1":"a1","field2":"a2","field3":"a3","fieldb1":"b1","fieldb2":"b2"},debug=True)
	assert c.classname == "common.seralize.gggg"
	assert id(c) == id(_get_cfg_by_table_name("u_ggg"))
	
	assert c.get_primary_sql((1,2,3)) == " field1=1 AND field2=2 AND field3=3 "
	assert c.get_primary_sql(("1","2","3")) == " field1='1' AND field2='2' AND field3='3' "
	assert c.is_primary_col("field1")
	assert c.is_primary_col("field2")
	assert c.is_primary_col("field3")
	assert not c.is_primary_col("fieldb2")

def xxtest_cfg_get_primary_sql():
	cfg = _seralize_cfg()
	cfg.classname = "db.sss"
	cfg.primary.append("col1")
	cfg.primary.append("col2")
	cfg.primary.append("col3")
	assert cfg.get_primary_sql((1,2,3)) == " col1=1 AND col2=2 AND col3=3 "
	assert cfg.get_primary_sql(("1","2","3")) == " col1='1' AND col2='2' AND col3='3' "
	
	cfg.primary = []
	cfg.primary.append("col1")
	assert cfg.get_primary_sql("aaa") == " col1='aaa' "
	
	
def xxtest_cfg_make_key():
	cfg = _seralize_cfg()
	cfg.classname = "db.sss"
	assert cfg.make_key(1000) == "db.sss.1000"
	assert cfg.make_key(1000,"a","b") == "db.sss.1000@@a@@b"
	assert cfg.make_key([1000,"a","b"]) == "db.sss.1000@@a@@b"
	assert cfg.make_key("aaa") == "db.sss.aaa"

def xxtest_cfg_primary_col():
	cfg = _seralize_cfg()
	cfg.table = "test_db"
	cfg.mapping["intcol"] = ""
	cfg.mapping["intcol2"] = ""
	cfg.mapping["boolcol"] = ""
	cfg.mapping["datetimecol"] = ""
	cfg.mapping["strcol"] = None
	cfg.primary.append("intcol")
	cfg.primary.append("intcol2")
	cfg.classname = "db.sss"
	assert cfg.is_primary_col("intcol")
	assert cfg.is_primary_col("intcol2")
	assert not cfg.is_primary_col("boolcol")
	assert not cfg.is_primary_col("noexist")
	assert cfg.has_primary(["intcol2","boolcol","datetimecol"])
	assert not cfg.has_primary(["strcol","boolcol","datetimecol"])
	utility.assert_array_noorder(cfg.get_noprimary_cols(),["boolcol","datetimecol","strcol"])


def xxtest_seralize():
	import datetime
	
	@table("test_db","intcol","intcol2")
	@field("","intcol")
	@field("intcol2","")
	@field("boolcol",None)
	@field("","datetimecol")
	@field(None,"strcol")
	@field("varstrcol","varstrcol")
	@field("xxxx","floatcol")
	class sss:
		def __init__(self):
			self.xxxx = 0.0
			self.boolcol = True
	
	db.execute("DELETE FROM test_db")
	db.commit()
	
	s = sss()
	#assert s.cfg
	s.boolcol = False
	s.datetimecol = datetime.datetime(2015,7,4,12,45,41)
	s.strcol = "姚teswt"
	s.varstrcol = "sdfasdfd舜"
	s.xxxx = 334356.34
	s.intcol = 1001
	s.intcol2 = 1
	
	cfg = _get_cfg_by_class(s)
	
	assert not cfg._is_exist(s)
	cfg._save(s)
	assert "common.seralize.sss.1001@@1" == cfg.key(s)
	assert 0 == utility.cmp_list(cfg._get_primary_values(s),(1001,1))
	assert 1 == db.query_single("SELECT COUNT(*) FROM test_db")
	assert cfg._is_exist(s)
	
	s2 = sss()
	s2.intcol = 1001
	s2.intcol2 = 1
	assert "common.seralize.sss.1001@@1" == cfg.key(s2)
	assert 0 == utility.cmp_list(cfg._get_primary_values(s2),(1001,1))
	assert " intcol=1001 AND intcol2=1 " == cfg._get_primary_sql(s2)
	assert cfg._is_exist(s2)
	assert s2 == cfg._reload(s2)
	utility.print_obj(s)
	utility.print_obj(s2)
	assert utility.equal(s,s2,1,2,True)
	
	s3 = sss()
	cfg._load_data(s3,1001,1)
	assert "common.seralize.sss.1001@@1" == cfg.key(s3)
	assert utility.cmp(s,s3,1,1,True) == 0
	s3.strcol = "12dfdfs"
	s3.varstrcol = "12dfdf343434s"
	cfg._update(s3)
	cfg._reload(s)
	assert s.strcol == "12dfdfs"
	assert s.varstrcol == "12dfdf343434s"
	assert utility.cmp(s,s3,1,1,True) == 0
	s3.strcol = "fff"
	s3.varstrcol = ""
	cfg._update(s3,("strcol",))
	cfg._reload(s2)
	assert s2.strcol == "fff"
	assert s2.varstrcol == "12dfdf343434s"
	
	s2.strcol = "12dfdfdfsdfss"
	s2.varstrcol = "12dfdf343sdfsdfsf434s"
	cfg._save(s2,True)
	cfg._reload(s3)
	assert utility.cmp(s2,s3,1,1,True) == 0
	cfg._delete(s2)
	assert not cfg._is_exist(s)

def xxtest_seralize2():
	import datetime
	@table("test_db","intcol","intcol2")
	@field("intcol","")
	@field("intcol2","")
	@field("boolcol","")
	@field("datetimecol","")
	@field("strcol",None)
	@field("varstrcol",None)
	@field("xxxx","floatcol")
	class sss:
		def __init__(self):
			self.xxxx = 0.0
			self.boolcol = True

	cfg = _get_cfg_by_class(sss)
	assert cfg
	
	db.execute("DELETE FROM test_db")
	db.commit()
	
	s = sss()
	s.boolcol = False
	s.datetimecol = datetime.datetime(2015,7,4,12,45,41)
	s.strcol = "姚teswt"
	s.varstrcol = "sdfasdfd舜"
	s.xxxx = 334356.34
	s.intcol = 1001
	s.intcol2 = 1
	cfg._save(s)
	assert 1 == db.query_single("SELECT COUNT(*) FROM test_db")
	assert cfg._is_exist(s)
	
	s3 = sss()
	s3.boolcol = True
	s3.intcol2 = 23
	s3.datetimecol = datetime.datetime(2005,7,4,12,45,1)
	s3.strcol = "2323姚tes2wt"
	s3.varstrcol = "sd2312fasdfd舜"
	s3.xxxx = 3346.34
	s3.intcol = 10221
	assert not cfg._is_exist(s3)
	cfg._save(s3)
	assert 2 == db.query_single("SELECT COUNT(*) FROM test_db")
	assert cfg._is_exist(s3)
		
	s2 = sss()
	ds = db.query("SELECT * from test_db")
	assert ds.row_count == 2
	assert ds.next()
	cfg._load(ds,s2)
	assert utility.cmp(s2,s,1) == 0
	
	assert ds.next()
	s4 = sss()
	cfg._load(ds,s4)
	assert utility.cmp(s3,s4,1) == 0
	# test update
	s4.xxxx = 232.12
	s4.strcol = "sdfsdfl啦啦"
	cfg._update(s4)
	cfg._reload(s3)
	assert utility.cmp(s3,s4,1) == 0 
	
	s.boolcol = False
	s.datetimecol = datetime.datetime(2013,7,11,10,43,31)
	cfg._save(s,True)
	cfg._reload(s2)
	assert utility.cmp(s,s2,1) == 0 
	
	s3.boolcol = False
	s3.datetimecol = datetime.datetime(2013,7,11,10,43,31)
	cfg._update(s3,["boolcol","datetimecol","floatcol"])
	cfg._reload(s4)
	assert utility.cmp(s4,s3,1) == 0 
	
	# test delete 
	cfg._delete(s)
	assert 1 == db.query_single("SELECT COUNT(*) FROM test_db")
	assert cfg._is_exist(s3)
	assert not cfg._is_exist(s)
	cfg._delete(s4)
	assert 0 == db.query_single("SELECT COUNT(*) FROM test_db")
	assert not cfg._is_exist(s3) 

@table("test_db","intcol")
@field("intcol","")
@dynamic_field("make_intcol2","intcol2")
@field("boolcol","")
@field("datetimecol","")
@field("strcol",None)
@field("varstrcol",None)
@field("xxxx","floatcol")
class sss2:
	def __init__(self):
		self.xxxx = 0.0
	
	def make_intcol2(self):
		return self.intcol+10000
		
def xxtest_mgr():
	import datetime
	s = sss2()
	mgr = manager(sss2)	
	mgr2 = manager(type(s))
	mgr3 = manager(sss2)
	mgr.delete_all()
	memcache.mc.clear()
	assert 0 == mgr.count
	
	s = sss2()
	s.intcol = 10001
	s.boolcol = True
	s.datetimecol = datetime.datetime(2009,2,5,12,54,24)
	s.strcol = "djfdsfas发"
	s.varstrcol = "djfdsfas发2222"
	s.xxxx = 1234.3
	
	s2 = sss2()
	s2.intcol = 10002
	s2.boolcol = False
	s2.datetimecol = datetime.datetime(2019,2,5,12,54,24)
	s2.strcol = "d地jfdsfas发"
	s2.varstrcol = "dj地fdsfas发2222"
	s2.xxxx = 97434.3
	
	s3 = sss2()
	s3.intcol = 10003
	s3.boolcol = False
	s3.datetimecol = datetime.datetime(2019,2,5,12,54,24)
	s3.strcol = "d地jfdsfas发"
	s3.varstrcol = "dj地fdsfas发2222"
	s3.xxxx = 97434.3
	
	mgr.save(s)
#	assert utility.cmp(memcache.get(mgr.cfg.key(s)),s) == 0
	assert mgr.count == 1
	mgr.save(s2)
#	assert utility.cmp(memcache.get(mgr.cfg.key(s2)),s2) == 0
	assert mgr.count == 2
	mgr.save(s3)
#	assert utility.cmp(memcache.get(mgr.cfg.key(s3)),s3) == 0
	assert mgr.count == 3
	assert mgr.count == mgr2.count
	assert mgr.count == mgr3.count

	memcache.mc.clear()
	s._seralize_key  = None
	s2._seralize_key = None
	s3._seralize_key = None
	r = mgr.get(10001)
	r._seralize_key = None
	assert utility.equal(r, s,1,0,True)
	r = mgr.get(10002)
	r._seralize_key = None
	assert utility.equal(r, s2,1,0,True)
	
	r = mgr.get(10003)
	r._seralize_key = None
	assert utility.equal(r, s3,0.1)
	
	r = mgr2.get(10001)
	r._seralize_key = None
	assert utility.equal(r, s,0.1)
	
	r = mgr2.get(10002)
	r._seralize_key = None
	assert utility.equal(r, s2,0.1)
	
	r = mgr2.get(10003)
	r._seralize_key = None
	assert utility.equal(r, s3,0.1)  
	a =mgr3.get(10001)
	assert utility.equal(a, s,0.1)  
	a =mgr3.get(10002)
	assert utility.equal(a, s2,0.1)  
	a =mgr3.get(10003)
	assert utility.equal(a, s3,0.1)  
	
	#test update
	s.strcol = "3242342"
	mgr.update(s)
	s._seralize_key  = None
	
	r = mgr.get(10001)
	r._seralize_key = None
	assert utility.equal(r, s,0.1, True)
	r = mgr2.get(10001)
	r._seralize_key = None
	assert utility.equal(r, s,0.1, True)
	r = memcache.get(mgr.cfg.key(s))
	r._seralize_key = None
	assert utility.equal(r,s,debug=True) 
	
	#test delete
	mgr2.delete(10001)
	assert 2 == mgr2.count
	assert mgr.get(10001) == None
	assert mgr.get(10002) is not None
	assert mgr.get(10003) is not None
	assert mgr2.get(10001) == None
	assert mgr2.get(10002) is not None
	assert mgr2.get(10003) is not None
	assert not memcache.check_key(mgr.cfg.key(s))
	assert not memcache.check_key(mgr.cfg.key(s2))
	assert not memcache.check_key(mgr.cfg.key(s3))
	
	mgr.delete_all()
	assert not mgr2._load_data((10001,),"")
	assert not mgr2._load_data((10002,),"")
	assert not mgr2._load_data((10003,),"")
	assert 0 == mgr.count

	
@table("test_db","intcol")
@dynamic_field("make_intcol2","intcol2")
@ignore("ignore1")
@ignore("ignore2")
class sss3:
	def __init__(self):
		self.intcol = 0
		self.boolcol = False
		self.datetimecol = None
		self.strcol = ""
		self.varstrcol = ""
		self.floatcol = 0
		self.ignore1 = ""
		self.ignore2 = ""
		self._ignore3 = ""
	
	def make_intcol2(self):
		return self.intcol+10000	
	
def xxtest_get_all_datacache():
	return #TODO
	import datetime
	
	m = manager(sss3)
	
	s = sss3()
	s.intcol = 10001
	s.boolcol = True
	s.datetimecol = datetime.datetime(2009,2,5,12,54,24)
	s.strcol = "djfdsfas发"
	s.varstrcol = "djfdsfas发2222"
	s.floatcol = 1234.3
	m.save(s)
	
	s2 = sss3()
	s2.intcol = 10002
	s2.boolcol = False
	s2.datetimecol = datetime.datetime(2019,2,5,12,54,24)
	s2.strcol = "d地jfdsfas发"
	s2.varstrcol = "dj地fdsfas发2222"
	s2.floatcol = 97434.3
	m.save(s2)
	
	m2 = manager(type(s2))
	m2.data_cache = {1:2}
	assert utility.cmp(m2.get_all_data(),m.get_all_data()) == 0
	m2.data_cache = {1:2}
	assert utility.cmp(m2.get_all_data(),[2,]) == 0
	m.update(s2)
	assert utility.cmp(m2.get_all_data(),m.get_all_data()) == 0
	assert utility.cmp(m2.get_all_data(),[2,]) != 0
	
	m2.data_cache = {1:2}
	m.delete(s2.intcol)
	assert utility.cmp(m2.get_all_data(),m.get_all_data(),0,0,True) == 0
	
@table("test_db","intcol")
@auto_increase("intcol")
class sss4:
	def __init__(self):
		self.intcol = 0
		self.boolcol = False
		self.datetimecol = utility.now()
		self.strcol = ""
		self.varstrcol = ""
		self.floatcol = 0
		self.intcol2 = 0

def xxtest_auto_increase():		
	m =  manager(sss4)
	m.delete_all()
	for i in range(500):
		s = sss4()
		s.intcol2 = i+900000
		s.strcol = "abc" + str(i)
		m.save(s)
		if i == 0:
			first = s.intcol
			continue
		assert s.intcol == first+i		
	m.delete_all()	
	
if __name__ == '__main__':
	utility.run_tests()
		