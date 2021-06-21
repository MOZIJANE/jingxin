#coding=utf-8 
# ycat			 2015/04/10      create
# 数据库管理类
#设计目标：支持mysql,sqlite，支持py2.x和py3.x
import sys,os
import config
import utility
import mytimer
import threading
import lock

g_db = None 
 
def _get_db():
	global g_db
	if g_db is None:
		t = config.get("db","default")
		g_db = database(t)
	return g_db
	
def close():
	global g_db
	if g_db:
		g_db.close()
	g_db = None

def execute(sql,*params):
	return _get_db().execute(sql,*params)


def commit():
	return _get_db().commit()


def rollback():
	return _get_db().rollback()

#直接返回dataset
def query(sql,*params):
	return _get_db().query(sql,*params)

#直接返回一个单值
def query_single(sql,*params):
	return _get_db().query_single(sql,*params)

#判断表是否存在
def is_table_exist(tablename):
	return _get_db().is_table_exist(tablename)

#删除表 
def drop_table(tablename):
	return _get_db().drop_table(tablename)

#数据库进行转义
def escape(s):
	return _get_db().escape(s)

class database():
	def __init__(self,cfg_name):
		assert config.has_section(cfg_name)
		assert config.has_key(cfg_name,"type")
		
		self.db = None
		self.cfg_name = cfg_name
	
	def execute(self,sql,*params):
		s = self._format(sql,*params)
		#utility.logger().debug(s)
		return self._get_db().execute(s)
	
	def commit(self):
		self._get_db().commit()
	
	def rollback(self):
		self._get_db().rollback()
	
	def close(self):
		if self.db:
			self.db.close()
	
	#直接返回dataset 
	def query(self,sql,*params):
		s = self._format(sql,*params)
		#utility.logger().debug(s)
		c = self._get_cursor()
		c.execute(s)
		return dataset(c)
	
	#直接返回一个单值
	def query_single(self,sql,*params):
		ds = self.query(sql,*params)
		assert ds.next()
		return ds[0]

	def escape(self,s):
		if s is None:
			return "NULL"
		import datetime
		if isinstance(s,float):
			return "%f"%s
		if isinstance(s,datetime.datetime):
			return "'"+utility.str_datetime(s,False)+"'"
		if isinstance(s,str):
			return "'"+self._get_db().escape_string(s)+"'"
		if not utility.is_python3():
			if isinstance(s,unicode):
				return "'"+self._get_db().escape_string(s.encode("utf-8"))+"'"
		return str(s)	

	def _format(self,sql,*params):
		if len(params) == 0:
			return sql
		p = [self.escape(x) for x in params]
		return sql.format(*p)

	def _get_db(self):
		if self.db is not None:
			if not utility.is_sae():
				return self.db
			
			if mytimer.ticks() - self.db.lasttime < 2000:
				return self.db
			try:
				self.db.ping()
				self.db.lasttime = mytimer.ticks()
				return self.db
			except Exception as err:
				self.db = None
		
		if utility.is_sae():
			import sae.saeutility
			import MySQLdb as mysqldb
			self.db = mysqldb.connect(**sae.saeutility.get_mysql_params())
			database.__set_mysql(self.db)		
		else:
			assert config.has_section(self.cfg_name)
			t = config.get(self.cfg_name,"type")
			if t == "sqlite":
				n = config.get(self.cfg_name,"db")
				pp = config.get(self.cfg_name,"path")
				log =""
				for p in pp.split(";"):
					curpath = os.path.join(p,n)
					if os.path.exists(curpath):
						import sqlite3
						self.db = sqlite3.connect(n)
						self.db.text_factory = str
						return self.db
					log += curpath + ";"
				s = "_get_db():sqlite db `%s` isn't existed, current path %s"%(log,os.getcwd())
				logger().error(s)
				raise AttributeError(s)
				
			elif t == "mysql":
				if utility.is_win():
					import MySQLdb as mysqldb
				else:
					import mysql.connector as mysqldb
				self.db = mysqldb.connect(host=config.get(self.cfg_name,"host"),
						       user=config.get(self.cfg_name,"user"),
						       passwd=config.get(self.cfg_name,"pwd"),
						       db=config.get(self.cfg_name,"db"),
						       port=config.getint(self.cfg_name,"port",3306),
						       charset='utf8')
				database.__set_mysql(self.db)
			else:
				s = "_get_db():Unknow db type %s, file %s, cfg_name %s"%(t,config.filename(),self.cfg_name)
				utility.logger().error(s)
				raise AttributeError(s)
		self.db.lasttime = mytimer.ticks()
		return self.db
	
	@staticmethod
	def __set_mysql(db):
		if utility.is_win():
			import MySQLdb as mysqldb
			db.autocommit(True)
			db.escape_string = mysqldb.escape_string
		else:
			import mysql.connector as mysqldb
			db.autocommit = True
			db.coversion = mysqldb.conversion.MySQLConverter()
			db.escape_string = db.coversion.escape
		db.execute = db.cursor().execute
		
	def _get_cursor(self):
		return self._get_db().cursor()		
		
	@property	
	def tables(self):
		if config.get(self.cfg_name,"type") != "mysql":
			return []
		db=config.get(self.cfg_name,"db")
		sql = "select table_name from information_schema.tables where table_schema='%s'"%db
		ds = self.query(sql)
		
		r = []
		while ds.next():
			r.append(ds[0])
		return r	
		
	def is_table_exist(self,tablename):
		sql = "select count(*) from information_schema.tables where `table_schema`='%s' and `TABLE_NAME`='%s'"%(config.get(self.cfg_name,"db"),tablename)
		return self.query_single(sql) == 1
	
	def drop_table(self,tablename):
		sql = "DROP TABLE IF EXISTS " + tablename
		return self.execute(sql)	
		
#使用方法
#ds = query("SELECT * FROM test_db")
#while(ds.next()):
#	ds.get(1) or ds.get("columnName") or ds.columnName
class dataset():
	default_codec = "utf-8"
	
	def __init__(self,cursor):
		self.cols = []
		for d in cursor.description:
			self.cols.append(d[0])
		self._rows = cursor.fetchall()
		self._rowindex = -1
		self._row_count = cursor.rowcount
		
	@property	
	def row_count(self):
		return self._row_count
	
	@property
	def col_count(self):
		return len(self.cols)

	@property
	def columns(self):
		return self.cols

	def next(self):
		if self._rowindex < self.row_count - 1:
			self._rowindex += 1
			return True
		else:
			self._rowindex = -1
			return False
		
	def row(self,rowindex):
		assert rowindex >= 0
		assert rowindex < self._row_count
		self._rowindex = rowindex
		return self
		
	def get(self, col):
		assert(self._rowindex != -1)
		if isinstance(col,str):
			i = 0
			for c in self.cols:
				if c == col:
					break
				else:
					i+=1
			else:
				raise LookupError("dataset:cant' find columns `%s`"%col)
			col = i
		
		data = self._rows[self._rowindex][col]
		if not utility.is_python3():
			if isinstance(data,unicode):
				return data.encode(dataset.default_codec)
		return data
	
	def get_bool(self,col):
		if self.get():
			return True
		else:
			return False
		
	def __getattr__(self, key):
		return self[key]
		
	def __getitem__(self, key):
		return self.get(key)
	
	def to_list(self):
		l = []
		while self.next():
			row = {}
			for c in range(self.col_count):
				row[self.cols[c]] = self[c]
			l.append(row)
		return l
	
#############################	unit test	###########################
def xxtest_format():
	config.init("test/test_db.txt")
	config.set("mysql","type","mysql")
	s1 = "dsf"
	assert _get_db()._format("fdff") == "fdff"
	if utility.is_python3():
		s = _get_db()._format("VALUES({0},{1},{2},{3},{4},{5},{6})",s1,103330,False,"2015-06-01 16:39:10","l 您a好'lal "," dsfaf啦\"la舜f afd",-122.3)
		assert s == "VALUES('dsf',103330,False,'2015-06-01 16:39:10','l 您a好\\\'lal ',' dsfaf啦\\\"la舜f afd',-122.300000)"
		s = _get_db()._format("VALUES({},{},{},{},{},{},{})",s1,103330,False,"2015-06-01 16:39:10","l 您a好'lal "," dsfaf啦\"la舜f afd",-122.3)
		assert s == "VALUES('dsf',103330,False,'2015-06-01 16:39:10','l 您a好\\\'lal ',' dsfaf啦\\\"la舜f afd',-122.300000)"
	else:
		assert 0
	config.init("")

def xxtest_check_table():
	config.init("test/test_db.txt")
	config.set("mysql","type","mysql")
	global g_db
	t = "test_db_drop"
	_get_db().drop_table(t)
	assert not _get_db().is_table_exist(t)
	sql = """CREATE TABLE """+t+""" (
		number INT(11),
		name VARCHAR(255),
		birthday DATE
		);"""
	_get_db().execute(sql)
	assert _get_db().is_table_exist(t)
	_get_db().drop_table(t)
	assert not _get_db().is_table_exist(t)
	_get_db().drop_table(t)
	
def xxtest_mysql():
	config.init("test/test_db.txt")
	config.set("mysql","type","mysql")
	global g_db
	execute("DELETE FROM test_db")
	commit()
	n = utility.now_str()
	if utility.is_python3():
		s = "INSERT INTO test_db(intcol,boolcol,datetimecol,strcol,varstrcol,floatcol)VALUES({0},{1},{2},{3},{4},{5})"
	else:
		s = "INSERT INTO test_db(intcol,boolcol,datetimecol,strcol,varstrcol,floatcol)VALUES(%s,%s,%s,%s,%s,%s)"
	
	execute(s,100,True,n,"lalal姚","舜dsfa'flafafd",-222.4)
	execute(s,103330,False,n,"l发 alal姚","舜dsfaflaf雪afd",122.3)
	commit()
	
	if utility.is_python3():
		ds = query("SELECT * FROM test_db WHERE intcol={} OR intcol={}",100,103330)
	else:
		ds = query("SELECT * FROM test_db WHERE intcol=%s OR intcol=%s",100,103330)
	utility.assert_array_noorder(ds.columns,["intcol","intcol2","boolcol","datetimecol","strcol","varstrcol","floatcol"])
	assert 2 == ds.row_count
	assert 7 == ds.col_count
	
	assert ds.next()
	assert ds.get("intcol") == 100
	assert ds.get("boolcol") == True
	assert ds["datetimecol"].strftime("%Y-%m-%d %H:%M:%S") == n
	assert ds["strcol"]  == "lalal姚"
	assert ds["floatcol"] == -222.4
	assert ds["varstrcol"]  == "舜dsfa'flafafd"
	
	assert ds.next()
	assert ds["intcol"] == 103330
	assert ds[1] == False
	assert ds[2].strftime("%Y-%m-%d %H:%M:%S") == n
	assert ds[3] == "l发 alal姚"
	assert ds[4] == "舜dsfaflaf雪afd"
	assert ds[5] == 122.3
	
	assert not ds.next() 
	assert ds._rowindex == -1
	
	assert ds.row(0).intcol == 100
	assert ds.intcol == 100
	assert ds.row(1).intcol == 103330
	assert ds.intcol == 103330
	
	assert query_single("SELECT COUNT(*) FROM test_db") == 2
	execute("DELETE FROM test_db")
	commit()	
	assert """'sdf\\\\s/d姚\\\'d\\"fs'""" == escape("""sdf\s/d姚'd"fs""")
	assert g_db.cfg_name == "mysql"
	
	t = g_db.tables
	assert len(t) > 0
	assert "test_db" in t
	config.init("")
	
def xxtest_mysql2():
	config.init("test/test_db.txt")
	config.set("mysql","type","mysql")
	global g_db
	g_db = database("mysql2")
	execute("DELETE FROM test_db")
	commit()
	n = utility.now_str()
	if utility.is_python3():
		s = "INSERT INTO test_db(intcol,boolcol,datetimecol,strcol,varstrcol,floatcol)VALUES({},{},{},{},{},{})"
	else:
		s = "INSERT INTO test_db(intcol,boolcol,datetimecol,strcol,varstrcol,floatcol)VALUES(%s,%s,%s,%s,%s,%s)"
	execute(s,100,True,n,"lalal姚","舜dsfa'flafafd",-222.4)
	execute(s,103330,False,n,"l发 alal姚","舜dsfaflaf雪afd",122.3)
	commit()
	
	if utility.is_python3():
		ds = query("SELECT * FROM test_db WHERE intcol={0} OR intcol={1}",100,103330)
	else:
		ds = query("SELECT * FROM test_db WHERE intcol=%s OR intcol=%s",100,103330)
	assert 2 == ds.row_count
	assert 7 == ds.col_count
	
	assert ds.next()
	assert ds.intcol == 100
	assert ds.boolcol == True
	assert ds.datetimecol.strftime("%Y-%m-%d %H:%M:%S") == n
	assert ds.strcol  == "lalal姚"
	assert ds.floatcol == -222.4
	assert ds.varstrcol  == "舜dsfa'flafafd"
	
	assert ds.get("intcol") == 100
	assert ds.get("boolcol") == True
	assert ds["datetimecol"].strftime("%Y-%m-%d %H:%M:%S") == n
	assert ds["strcol"]  == "lalal姚"
	assert ds["floatcol"] == -222.4
	assert ds["varstrcol"]  == "舜dsfa'flafafd"
	
	
	assert ds.next()
	assert ds["intcol"] == 103330
	assert ds[1] == False
	assert ds[2].strftime("%Y-%m-%d %H:%M:%S") == n
	assert ds[3] == "l发 alal姚"
	assert ds[4] == "舜dsfaflaf雪afd"
	assert ds[5] == 122.3
	
	assert not ds.next() 
	assert ds._rowindex == -1
	assert query_single("SELECT COUNT(*) FROM test_db") == 2
	execute("DELETE FROM test_db")
	commit()
	assert g_db.cfg_name == "mysql2"
	assert """'sdf\\\\s/d姚\\\'d\\"fs'""" == escape("""sdf\s/d姚'd"fs""")	
	config.init("")
	
def xxtest_thread():
	config.init("test/test_db.txt")
	config.set("mysql","type","mysql")
	execute("DELETE FROM test_db")
	commit()
	def thread1():
		now = utility.now()
		for i in range(20):
			if utility.is_python3():
				s = "INSERT INTO test_db(intcol,intcol2,boolcol,datetimecol,strcol,varstrcol,floatcol)VALUES({},{},{},{},{},{},{})"
			else:
				s = "INSERT INTO test_db(intcol,intcol2,boolcol,datetimecol,strcol,varstrcol,floatcol)VALUES(%s,%s,%s,%s,%s,%s,%s)"
			execute(s,lock.get_thread_id()%100000 ,i,True,now,"lalal姚","舜dsfa'flafafd",-222.4)
			lock.sleep(0.1)
			commit()
			
	def thread2():
		for i in range(100):
			a = query("select * from test_db")
			lock.sleep(0.01)
	
	tt = []
	for i in range(10):
		tt.append(threading.Thread(target=thread1))
	for i in range(3):
		tt.append(threading.Thread(target=thread2))
	for t in tt:
		t.start()
	for t in tt:
		t.join()
	c = query_single("select count(*) from test_db")
	assert 200 == c
	execute("DELETE FROM test_db")
	commit()
	config.init("")
	
if __name__ == '__main__':
	#utility.run_tests()
	#print("test finish!")
	pass
		
