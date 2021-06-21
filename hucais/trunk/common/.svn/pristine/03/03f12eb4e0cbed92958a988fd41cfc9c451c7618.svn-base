#coding=utf-8 
# ycat			 2015/01/30      create
#   支持#注释，但通过api修改会丢失注释 
#   支持#include xxxx.cfg 文件操作 
#	[section1]
#	key1 = value1
#	key2 = value2
#	key3 = value3
#	可以用{变量}和setParam来控制变量
import sys,os
import _utility
import dict_obj

if _utility.is_python3():
	import configparser  
else:
	import ConfigParser as configparser
import threading
import codecs
import re 

g_params = {}

def setParam(key,value):
	global g_params
	g_params[key] = str(value)
	
def clearParam():
	global g_params
	g_params.clear()
	

class config:
	def __init__(self,filename):
		if isinstance(filename,dict):
			self.sections = filename
		else:
			if not os.path.exists(filename):
				raise IOError("config file not found! '%s'" % filename)
			self.load(filename)
	
	def _updateParam(self,s,pp):
		global g_params
		pp.update(g_params)
		for p in pp:
			s = s.replace("{{%s}}"%p,pp[p])
		for e in os.environ:
			s = s.replace("{{%s}}"%e,os.environ[e])
		return s
		
	def _getParam(self,s):
		pp = {}
		aa = re.compile("#param\s.+=*.",re.M).findall(s)
		for a in aa:	
			m = re.search("#param\s+(.+)\s*=\s*(.+)",a)
			assert m
			pp[m.group(1).strip()] = m.group(2).strip()
		return pp
		
	
	def load(self,filename):
		def getIncludeCfg(s,ret): #取出#include xxxx的cfg列表
			aa = re.compile("#include\s+.*\.cfg",re.M).findall(s) 
			for a in aa:
				m = re.search("#include\s+(.*\.cfg)",a)
				assert m
				if not os.path.isabs(m.group(1)):
					name = os.path.dirname(os.path.abspath(filename)) + "/" + m.group(1)
				else:
					name = m.group(1)
				if name != filename:
					c = config(name)
					ret.update(c.sections)
			return ret
			
		self.filename = filename
		self.cfg = configparser.ConfigParser() 
		sub = {}
		with codecs.open(filename,encoding='utf-8') as file:
			s = file.read() 
			pp = self._getParam(s)
			s = self._updateParam(s,pp)
			sub = getIncludeCfg(s,sub)
			s = re.sub("#.*","",s)  
			if s and s[0] == "\ufeff":
				s = s[1:]
			try:
				self.cfg.read_string(s)	
			except configparser.DuplicateSectionError as e:
				print(s)
				raise e
		self.sections = {}
		for s in self.cfg.sections():
			d = {}
			try:
				for rr in self.cfg.items(s):
					d[rr[0].lower()] = rr[1]
			except configparser.InterpolationMissingOptionError as e:
				print("config sesstion " + s +" error")
			self.sections[s.lower()] = d
		for s in sub:
			if s not in self.sections:
				self.cfg.add_section(s.lower())
			for d in sub[s]:
				self.cfg.set(s.lower(),str(d),str(sub[s][d]))
		self.sections.update(sub)
	
	def __str__(self):
		ret = ""
		for s in self.sections:
			ret += "[" + s + "]\n"
			vv = self.sections[s]
			for v in vv:
				ret += "\t" + str(v) + " = " + str(vv[v]) + "\n"
		return ret
		
	def addCfg(self,filename):
		c = config(filename)
		#for k in c.sections:
		#	if k in self.sections:
		#		raise KeyError("repeat config sesstion:"+k+",file:"+filename)
		self.sections.update(c.sections)
	
	def has_section(self,section): 
		return section.lower() in self.sections
	
	#def sections(self):
	#	return list(self.sections.keys())

	def has_key(self,section,key):  
		if not self.has_section(section.lower()):
			return False 
		return key.lower() in self.sections[section.lower()]

	def get_obj(self,section):
		if not self.has_section(section):
			return None
		return dict_obj.dictObj(self.items(section))
 
	def get(self,section,key,default=None):
		if self.has_key(section,key):
			return self.sections[section.lower()][key.lower()]  
		return default
	 
	def getint(self,section,key,default=None):
		if default is not None:
			assert isinstance(default,int)
		r = self.get(section,key,default)
		if r is not None:
			return int(r)
		return None
	 
	def getfloat(self,section,key,default=None):
		if default is not None:
			assert isinstance(default,(float,int))
		r = self.get(section,key,default)
		if r is not None:
			return float(r)
		return None
	 
	def getbool(self,section,key,default=None):
		if default is not None:
			assert isinstance(default,bool)
		r = str(self.get(section,key,default)).lower()
		if r == "1" or r == "true":
			return True
		if r == "0" or r == "false":
			return False
		raise ValueError(bool,r)
	
	
	def getlist(self,section,key,split=","):
		ret = self.get(section,key,default="")
		ret = [ s.strip() for s in ret.split(split) ]
		if ret == [""]:
			return []
		return ret
	
	
	def save(self,filename):
		self.cfg.write(open(filename, "w"))
	
	#TODO: 设置后，注释会丢失 
	def set(self,section,key,value,update=True):
		if not self.has_section(section):
			self.cfg.add_section(section.lower())
			self.sections[section.lower()] = {} 
		self.sections[section.lower()][key.lower()] = str(value) 
		if update:
			self.cfg.set(section,str(key),str(value))
			self.save(self.filename)
			self.load(self.filename)
	 
	def remove(self,section,key=None,update=True):
		if not self.has_section(section):
			return
		if key is None:
			self.cfg.remove_section(section)
			if section.lower() in self.sections:
				del self.sections[section.lower()]
		else:
			self.cfg.remove_option(section,key)
			if section.lower() in self.sections:
				if key.lower() in self.sections[section.lower()]:
					del self.sections[section.lower()][key.lower()]
		if update:
			self.save(self.filename)
			self.load(self.filename)
			
	def items(self,section):
		if not self.has_section(section):
			return None
		return self.sections[section]
		

_g_cfg = None
 
def _get_default():
	p = os.path.dirname(__file__)
	return os.path.abspath(p+"/../config.cfg")  

def reload():
	if _g_cfg:
		filename = _g_cfg.filename
	else:
		filename = None
	return init(filename)

def init(filename = None):
	global _g_cfg
	if filename is None:
		filename = _get_default()  
	_g_cfg = config(filename) 
 
def _get_cfg():
	global _g_cfg
	if _g_cfg is None:
		init()
	return 	_g_cfg

def has_section(sect):
	return _get_cfg().has_section(sect)

def has_key(section,key):
	return _get_cfg().has_key(section,key)

def get(section,key,default=None):
	return _get_cfg().get(section,key,default)

def getint(section,key,default=None):
	return _get_cfg().getint(section,key,default)

def getfloat(section,key,default=None):
	return _get_cfg().getfloat(section,key,default)

def getbool(section,key,default=None):
	return _get_cfg().getbool(section,key,default)


def getlist(section,key,split=","):
	return _get_cfg().getlist(section,key,split)


def set(section,key,value,update=True):
	return _get_cfg().set(section,key,value,update=update)

def remove(section,key=None,update=True):
	return _get_cfg().remove(section,key,update=update)

def filename():
	return _get_cfg().filename

def getData():
	return _get_cfg().sections
	 
def loadData(ss):
	init(filename = ss)

def sections():
	return list(_get_cfg().sections.keys())

def items(section):
	return _get_cfg().items(section)

def get_obj(section):
	return _get_cfg().get_obj(section)
	
def text():
	return str(_get_cfg())

def save(filename):
	_get_cfg().save(filename)

#############################	unit test	###########################  
def test_include():
	init("./test/test_config1.cfg")
	assert has_section("handlers")
	assert has_key("handlers","keys")
	assert not has_section("handlers1")
	assert not has_key("handlers","keys1")
	assert not has_key("handlers1","keys")
	assert get("ycat","keys") == "root"
	assert get("logger_root","level") == "NOTSET"
	
	assert getlist("ycat","list1") == ["aaa","bbb","333"]
	assert getlist("ycat","list2") == []

	
def test_has():
	import utility
	init("./test/test_config.cfg")
	assert has_section("handlers")
	assert has_key("handlers","keys")
	assert not has_section("handlers1")
	assert not has_key("handlers","keys1")
	assert not has_key("handlers1","keys")
	assert filename().find("test_config.cfg") != -1
	
	r = items("loggers")
	assert len(r) == 10
	r2  = {}
	r2["keys"] = "root"
	r2["intkey"] = "1356"
	r2["intkey2"] = "-33356"
	r2["bkey1"] = "True"
	r2["bkey2"] = "False"	
	r2["bkey3"] = "0"
	r2["bkey4"] = "1"
	r2["bkey5"] = "true"
	r2["bkey6"] = "false"
	r2["fkey"] = "0.0001"
	assert utility.cmp_dict(r,r2,debug=True) == 0
	assert items("no_existed") is None
	s = sections()
	assert "loggers" in s
	assert "logger_root" in s
#	assert "handler_consoleHandler" in s
	
	assert None == get_obj("loggers334343")
	o = get_obj("loggers")
	assert o.keys == "root"
	assert o.bkey1 == "True"
	assert o.intkey2 == "-33356"
	
	
def test_no_exist():
	e = None
	try:
		init("no_exist.cfg")
		assert 0
	except IOError as ee:
		e = ee
	assert e
	
def test_get():
	assert get("handlers","keys") == "consoleHandler"
	assert get("logger_root","level") == "NOTSET"
	assert get("logger_root","no_exit") == None
	assert get("logger_root","no_exit","NoneNone") == "NoneNone"
	assert get("no_exit","level") == None
	assert get("no_exit","level","") == ""
#	assert get("logger_root","handlers") == "(levelname)s(name)s(filename)s:(lineno)s (asctime)s: (message)s"
	
def test_getint():
	assert getfloat("loggers","fkey") == 0.0001
	assert getint("loggers","intkey") == 1356
	assert getint("loggers","intkey2") == -33356
	assert getint("loggers","no_exit") == None
	assert getint("loggers","no_exit",23232) == 23232
	e = None
	try:
		getint("logger_root","level")
		assert 0
	except ValueError as err:
		e = err
	assert e
		
def test_getbool():
	assert getbool("loggers","bkey1")
	assert not getbool("loggers","bkey2")
	assert not getbool("loggers","bkey3")
	assert getbool("loggers","bkey4")
	assert getbool("loggers","bkey5")
	assert not getbool("loggers","bkey6")
	try:
		getbool("logger_root","level")
		assert 0
	except ValueError as err:
		e = err
	assert e
	
def test_set():
	remove("testsection1")
	remove("testsection2","key1")
	remove("noexit")
	remove("testsection2","noexit")
	assert not has_key("testsection1","key1")
	assert not has_key("testsection2","key1")
	
	set("testsection1","key1","lala")
	assert get("testsection1","key1") == "lala"
	
	set("testsection1","key2","lala2")
	assert get("testsection1","key2") == "lala2"
	
	set("testsection2","key1",123456)
	assert getint("testsection2","key1") == 123456
	
	assert has_key("testsection1","key1")
	assert has_key("testsection2","key1")
	print(text())
	
def test_param():
	import setup
	setup.setCurPath(__file__)
	init("./test/test_param_config.cfg")
	setParam("testsection2","ycat1")
	setParam("aa","23123131")
	setParam("bb","ycat2222")
	
	assert 3 == len(g_params)
	reload()
	
	assert get("ycat1","y1") == "23123131"
	assert get("ycat1","key1") == "123456"
	
	assert get("testsection1","key1") == "ycat2222"
	assert get("testsection1","key2") == "lala2"
	
	assert get("testsection1","key3") == "ycattest"
	assert get("testsection1","key4") == "aaabbb"
	setParam("a","yca2222t23222")
	reload()
	assert get("testsection1","key3") == "ycattest"
	assert get("testsection1","key4") == "yca2222t23222"
	clearParam()
	assert not g_params
	
 		
if __name__ == '__main__':
	import utility
	utility.run_tests()
	
	
