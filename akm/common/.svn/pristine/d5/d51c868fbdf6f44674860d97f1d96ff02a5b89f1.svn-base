import sys,os
import config
import inspect

set_type = set
g_visisted_module = set()
g_cfg = None

def _add(dirName):
	global g_cfg,g_visisted_module
	if dirName in g_visisted_module:
		return
	g_visisted_module.add(dirName)
	p = os.path.abspath(dirName+"/local.cfg")
	if os.path.exists(p):
		#print("add local.cfg:",p)
		if g_cfg is None:
			g_cfg = config.config(p) 
		else:
			g_cfg.addCfg(p)

def _loadStackFiles():
	for s in inspect.stack():
		fileName = s[1]
		if len(fileName) and fileName[0] == "<":
			continue
		dirName = os.path.dirname(fileName)
		_add(dirName)
	_add(".")
	
g_cur_path = os.path.abspath(os.path.dirname(__file__))

#注意:外部引用时，需要多加一句 
def loadCur():
	_loadStackFiles()
		
def _get_cfg():
	#_loadCurLocal()
	if g_cfg is None:
		_loadStackFiles()
	return g_cfg
 
def reload():
	global g_cfg,g_visisted_module
	g_cfg = None
	g_visisted_module = set_type()
	_get_cfg()

def has_section(sect):
	return _get_cfg().has_section(sect)

def has_key(section,key):
	return _get_cfg().has_key(section,key)

def set(section,key,value,update=False):
	_get_cfg().set(section,key,value,update=update)

def get(section,key,default=None): 
	return _get_cfg().get(section,key,default)

def getint(section,key,default=None):
	return _get_cfg().getint(section,key,default)

def getfloat(section,key,default=None):
	return _get_cfg().getfloat(section,key,default)

def getbool(section,key,default=None):
	return _get_cfg().getbool(section,key,default)

def getlist(sesion,key,split=","):
	return _get_cfg().getlist(sesion,key,split)
 
def remove(section,key=None):
	return _get_cfg().remove(section,key,update=False)

def filename():
	return _get_cfg().filename

def sections():
	return _get_cfg().sections

def items(section):
	return _get_cfg().items(section)

def get_obj(section):
	return _get_cfg().get_obj(section)
 
def text():
	return str(_get_cfg())
	
def setParam(key,value):
	_get_cfg().setParam(key,value)
	
def clearParam():
	_get_cfg().clearParam()
	
	

	
############## unit test ############## 
	
def test_has():
	import utility 
	assert has_section("handlers")
	assert has_key("handlers","keys")
	assert not has_section("handlers1")
	assert not has_key("handlers","keys1")
	assert not has_key("handlers1","keys")
	assert filename().find("local.cfg") != -1
	
	r = items("loggers")
	assert len(r) == 9
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
	assert utility.cmp_dict(r,r2,debug=True) == 0
	assert items("no_existed") is None
	s = sections()
	assert "loggers" in s
	assert "logger_root" in s 
	
	assert None == get_obj("loggers334343")
	o = get_obj("loggers")
	assert o.keys == "root"
	assert o.bkey1 == "True"
	assert o.intkey2 == "-33356"
	
	
def test_get():
	assert get("handlers","keys") == "consoleHandler"
	assert get("logger_root","level") == "NOTSET"
	assert get("logger_root","no_exit") == None
	assert get("logger_root","no_exit","NoneNone") == "NoneNone"
	assert get("no_exit","level") == None
	assert get("no_exit","level","") == ""
	assert get("logger_root","handlers") == "(levelname)s(name)s(filename)s:(lineno)s (asctime)s: (message)s"
	
def test_getint():
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
	
	set("testsection2","key1","123456")
	assert getint("testsection2","key1") == 123456
	
	assert has_key("testsection1","key1")
	assert has_key("testsection2","key1")
		
if __name__ == '__main__':
	import utility   
	assert "96440" == get("uwbId","id_01") 
	test_set()
	utility.run_tests()
	
	
