#coding=utf-8 
# ycat			 2015/04/10	  create
import sys,os
import getopt
import hashlib,datetime,time
import traceback
import _utility
import platform
import time
import random as rand
from random import Random
import math
import numpy as np

class empty_class:
	pass

def enum(**enums):
	return type('Enum', (), enums)

#取出相应的模块名称 
app_name = _utility.app_name

#设置模块名字，因为在common目录里取不出来  
set_app_name = _utility.set_app_name

g_version = "0.0.1"

def get_version():
	global g_version
	return g_version

def set_test():
	os.environ["is_test"] =  "True"

def is_test():
	if "test" in sys.argv:
		return True
	if "is_test" in os.environ:
		return os.environ["is_test"] == "True"
	return False

def is_win64():
	# python 64
	return platform.architecture()[0] == "64bit"
	
def is_win32():
	# python 32
	return platform.architecture()[0] == "32bit"

g_isRos = None

def is_ros():
	global g_isRos
	if g_isRos is None:
		g_isRos = 'ROS_ROOT' in os.environ
	return g_isRos
	
	
#下面两句判断是否为win64	
#def is_win64():	
#	return 'PROGRAMFILES(X86)' in os.environ
	
#def is_win32():
#	return not is_win64()	
	
def is_win():
	return sys.platform == "win32"

def set_is_test(value):
	global __test_now
	os.environ["is_test"] = str(value)
	if not value:
		__test_now = None

def md5(value):
	return hashlib.md5(value.encode("utf-8")).hexdigest()

def md5b(value):
	return hashlib.md5(value).hexdigest()

__test_now = None

def now():
	global __test_now
	if __test_now:
		return __test_now
	return datetime.datetime.now()

def now_str(hasMillisecond = False):
	return str_datetime(now(),hasMillisecond)
	
def timespan_str(time):
	s = time.total_seconds()
	ss = "%02d:%02d:%02d.%03d"%(s%86400/3600,s%3600/60,s%60,math.modf(s)[0])
	if time.days:
		return str(time.days)+" days,"+ss
	return ss

g_start_time = now()

def date2str(date):		
	import datetime
	if isinstance(date,datetime.datetime):
		return datetime.datetime.strftime(date,'%Y-%m-%d %H:%M:%S')
	else:
		assert isinstance(date,datetime.timedelta)
		ss = int(date.total_seconds())
		h,next = divmod(ss,3600)
		m,s = divmod(next,60)
		return "%02d:%02d:%02d"%(h,m,s)

def str2date(strdate):
	from datetime import datetime	
	return datetime.strptime(strdate,'%Y-%m-%d %H:%M:%S')

def datetime_add(dt, seconds):
	from datetime import timedelta
	dt += timedelta(seconds=seconds)
	return dt

def is_datetime(s):
	try:
		time.strptime(s,'%Y-%m-%d %H:%M:%S')
		return True
	except:
		return False

def set_now(dateTime):
	global __test_now
	__test_now = dateTime

def assert_datetime(d1,d2,diffsecond):
	assert abs(d2 - d1).total_seconds() <= diffsecond
	return True

def assert_array_noorder(a1,a2):
	#不管顺序的数组比较
	assert a1
	assert a2
	assert len(a1) == len(a2)
	assert cmp_list(a1,a2) == 0
	return True

def ticks():
	return int(time.time()*1000) 			
	

#实现虚函数的修饰符
def abstract(func):
	def __call(*p):
		c = func.__module__ + "." + str(func.__class__)
		if len(p) > 0:
			c = p[0].__class__
		raise NotImplementedError("Can't invoke abstract method `%s.%s`"%
			(c,func.__name__))
	__call.__name__ = func.__name__
	return __call

#自动处理异常的修饰符
#用法 @catch 
def catch(func):
	def __call(*p,**pp):
		import log
		import bottle
		try:
			return func(*p,**pp)
		except bottle.HTTPResponse as httperror:
			log.info(httperror)
			raise
		except Exception as e:
			log.exception("invoke "+str(func),e)
			return None
	__call.__name__ = func.__name__
	return __call

def str_class(item):
	s = "<" + item.__class__.__name__ + ">{ "
	if is_test():
		ll = list(item.__dict__.keys())
		ll.sort()
	else:
		ll = item.__dict__.keys()
	for k in ll:
		s += "%s=`%s`, " % (str(k),str_obj(item.__dict__[k]))
	return s.strip(", ") + "}"

def str_list(d1):
	if len(d1) == 0:
		return "[<list len=0>]"
	s = "[<list len=" + str(len(d1)) + "> "
	for d in d1:
		s += str_obj(d) + ","
	return s.strip(", ") + "]"
	   		
def str_dict(d1):
	if len(d1) == 0:
		return "[empty]"
	
	s = "{"
	a = [k for k in d1]
	for k in a:
		s = s + "`"+str_obj(k) + "`:`" + str_obj(d1.get(k)) +"`, "
	return s.strip(", ") + "}"

def str_datetime(d1,has_millisecond):
	if has_millisecond:
		return d1.strftime("%Y-%m-%d %H:%M:%S.") + "%03d" %(d1.microsecond/1000)
	else:
		return d1.strftime("%Y-%m-%d %H:%M:%S")

g_no_print = []
#增加不需要打印的类的修饰符 
def no_print():
	def __call(cls):
		global g_no_print
		g_no_print.append(cls)
		return cls 
	return __call	
	
def str_obj(p):
	if hasattr(p,'__call__'):
		return str(p)
	if p is None:
		return "<None>"
	if not is_python3() and isinstance(p,long):
		return str(p)
	if isinstance(p,(int,str,float,bool)):
			return str(p)
	if isinstance(p,datetime.time):
		return p.strftime("%H:%M:%S")	
	if isinstance(p,datetime.datetime):
		return str_datetime(p,True)	
	if isinstance(p,(tuple,list,set)):
		return str_list(p)
	if isinstance(p,dict):
		return str_dict(p)
	if isinstance(p,dict):
		return str_dict(p)
	global g_no_print
	if isinstance(p,tuple(g_no_print)):
		return "no_printable"
	return str_class(p)	

def print_obj(*params):
	s = []
	for p in params:
		s.append(str_obj(p))
	import pprint
	pprint.pprint(s)

def is_python3():
	return _utility.is_python3()

def cmp_dict(o1,o2,floatDiff=0.0,dateDiffSecond=0,debug=False):
	if not isinstance(o1,dict):
		if debug:
			print("compare dicts, but obj1 is %s"%str(type(o1)));					
		return -1
	if not isinstance(o2,dict):
		if debug:
			print("compare dicts, but obj2 is %s"%str(type(o2)));	
		return -1
	if len(o1) != len(o2):
		if debug:
			print("dict's len is diff,%d != %d"%(len(o1),len(o2)));							
		return -1
	for k in o1:
		if k not in o2:
			if debug:
				print("dict is diff at key %s, object2 hasn't this key"%str(k));
			return -1	
		r = cmp(o1[k],o2[k],floatDiff,dateDiffSecond,debug) 
		if r != 0:
			if debug:
				print("dict is diff at key %s, %s != %s"%(str_obj(k),str_obj(o1[k]),str_obj(o2[k])));			
			return r
	return 0	

def cmp_set(o1,o2,floatDiff=0.0,dateDiffSecond=0,debug=False):
	if len(o1) != len(o2):
		if debug:
			print("set len don't match, %s != %s"%(str_obj(o1),str_obj(o1)));
		return _utility.os_cmp(len(o1),len(o2))
	for a in o1:
		if a not in o2:
			return -1
	return 0	

def cmp_list(o1,o2,floatDiff=0.0,dateDiffSecond=0,debug=False):
	#不管顺序的数组比较
	if len(o1) != len(o2):
		if debug:
			print("list len don't match, %s != %s"%(str_obj(o1),str_obj(o1)));
		return -1
	
	def find_list(obj,ll):
		for l in ll:
			if cmp(obj,l,floatDiff,dateDiffSecond,debug) == 0:
				return True
		return False	

	s1 = list(o1)
	s2 = list(o2)
	for index,a in enumerate(s1):
		if not find_list(a,s2):
			if debug:
				print("list is diff at index %d, can't find %s in list2"%(index,str_obj(a)));
				return -1
	return 0


def rand_list(obj,create_func):
	if not create_func:
		return []
	ll = []
	for i in range(rand.randint(5,20)):
		ll.append(random(create_func()))
	return ll
	
def rand_dict(obj,create_key_func,create_val_func):
	if not create_key_func:
		return {}
	if not create_val_func:
		return {}
	rr = {}
	for i in range(rand.randint(5,20)):
		rr[random(create_key_func())] = random(create_val_func())
	return rr	


#自动生成测试数据 
def random(obj,create_func=None,create_key_func=None,create_val_func=None):
	if obj is None:
		return obj
	if isinstance(obj,bool):
		obj = rand.choice((True,False))
		return obj	
	if isinstance(obj,int):
		obj = rand.randint(-10000,10000)
		return obj
	if isinstance(obj,datetime.datetime):
		obj = now() + datetime.timedelta(hours=rand.randint(-10,10))
		return obj
	if isinstance(obj,float):
		obj = rand.random() * rand.randint(-10000,10000 )
		return obj
	if isinstance(obj,str):
		obj = "unit_test_"+"姚"+"1"*rand.randint(0,8)
		return obj
	if isinstance(obj,tuple):
		return rand_list(obj,create_func)	
	if isinstance(obj,list):
		return rand_list(obj,create_func)
	if isinstance(obj,dict):
		return rand_dict(obj,create_key_func,create_val_func)			
	for k1 in obj.__dict__:
		o = getattr(obj,k1)
		setattr(obj,k1,random(o))
	return obj	

def equal(o1,o2,floatDiff=0.0,dateDiffSecond=0,debug=False):
	return cmp(o1,o2,floatDiff,dateDiffSecond,debug) == 0

	
def near(v1,v2,diff=0.1):
	if isinstance(v1,datetime.datetime):
		return abs((v1 - v2).total_seconds()) <= diff
	return abs(v1-v2)<diff
	
	
#用简单类型去判断，而不是指针,floatDiff为float判断的误差,dateDiffMilli为时间的判断误差(秒)
def cmp(o1,o2,floatDiff=0.0,dateDiffSecond=0,debug=False):
	if id(o1) == id(o2):
		return 0
	if o1 is None:
		if  o2 is None:
			return 0
		else:
			if debug:
				print("utility.cmp obj1 is None")			
			return 1
	if  o2 is None:
		if debug:
			print("utility.cmp obj2 is None")					
		return -1
	
	if not is_python3() and isinstance(o1,unicode):
		return _utility.os_cmp(o1,o2)
	if not is_python3() and isinstance(o1,long):
		return _utility.os_cmp(o1,o2)
	if isinstance(o1,(int,str,bool,np.int32)):
		return _utility.os_cmp(o1,o2)
		
	if isinstance(o1,datetime.datetime):
		datetime.timedelta.microseconds
		if abs((o1 - o2).total_seconds()) <= dateDiffSecond:
			return 0
		else:
			return _utility.os_cmp(o1,o2)	
		
	if isinstance(o1,float):
		if abs(o1 - o2) <= floatDiff:
			return 0
		else:
			return _utility.os_cmp(o1,o2)
	if isinstance(o1,(tuple,list,type({}.values()))):
		return cmp_list(o1,o2,floatDiff,dateDiffSecond,debug)
	if isinstance(o1,set):
		return cmp_set(o1,o2,floatDiff,dateDiffSecond,debug)	
	if isinstance(o1,dict):
		return cmp_dict(o1,o2,floatDiff,dateDiffSecond,debug)		
	
	if not isinstance(o1,type(o2)):
		if debug:
			print("utility.cmp() wrong Type, %s != %s"%(type(o1),type(o2)))
			return -1
	
	if len(o1.__dict__) != len(o2.__dict__):
		if debug:
			print("utility.cmp() __dict__ error : %d != %d"%(len(o1.__dict__),len(o2.__dict__)))
			print("obj1",o1.__class__,o1.__dict__)
			print("obj2",o2.__class__,o2.__dict__)
		return _utility.os_cmp(len(o1.__dict__),len(o2.__dict__))
	try:
		for k1 in o1.__dict__:
			r = cmp(getattr(o1,k1),getattr(o2,k1),floatDiff,dateDiffSecond,debug)
			if debug and r != 0:
				print("utility.cmp diff at %s, %s != %s"%(k1,str_obj(getattr(o1,k1)),str_obj(getattr(o2,k1))))
			if r != 0:
				return r
		return r
	except KeyError as e:
		if debug:
			print("utility.cmp(): %s != %s"%(str_obj(o1),str_obj(o2)))
		return -1
	

def clone(obj):
	import copy
	return copy.deepcopy(obj)
 

def random_str(randomlen=32):
	result = ''  
	chars = 'ABCDEFGHIJKLMN0987654321OPQRSTUVWXYZ'
	length = len(chars) - 1
	random = rand.Random()
	for i in range(randomlen):
		result += chars[random.randint(0,length)]
	return result

def ip2mask_bit(mask):
	return 32 - sum(bin(int(i)).count('1') for i in mask.split('.'))

g_uptime = 0
	
def get_uptime():
	result = 0
	if("Linux" == platform.system()):
		f = open("/proc/uptime")
		try:
			tmp = f.read().split()
			result = tmp[0]
		finally:
			f.close()
	else:
		result = g_uptime
	return float(result)

def singleton(cls, *args, **kw):
	instances = {}
	def _singleton(*args, **kw):
		if cls not in instances:
			instances[cls] = cls(*args, **kw)
		return instances[cls]
	return _singleton

g_init_funcs = []
g_fini_funcs = []

#注册自动调用函数 
def init():
	def __call(func):
		import log
#		log.info("register init "+str(func))
		global g_init_funcs
		g_init_funcs.append(func)
		return func
	g_start_time = now()
	# __call.__name__ = func.__name__
	return __call

#注册自动退出调用函数 
def fini():
	def __call(func):
		import log
#		log.info("register fini "+str(func))
		global g_fini_funcs
		g_fini_funcs.append(func)
		return func
	# __call.__name__ = func.__name__
	return __call

def running_time():
	global g_start_time
	return now() - g_start_time

#注册自动退出的全局变量
#只要obj有init()或者fini，就会自动在启动或退出时候调用 
def auto_global(obj):
	if hasattr(obj,"init"):
		init()(obj.init)
	if hasattr(obj,"fini"):
		fini()(obj.fini)	

def is_run_all():
	return "runAll" in os.environ


g_has_register = False

#按ctrl+C也会触发这个回调 
def registerCloseEvent():
	global g_has_register
	if g_has_register:
		return
	g_has_register = True
	if not is_win():
		return 
	import win32api
	import log
	def on_console_close(sig):
		log.error('user close console window, system quit!')
		finish()
	win32api.SetConsoleCtrlHandler(on_console_close, True)

# registerCloseEvent()

def disableCloseButton():
	if not is_win():
		return
	import win32api
	import win32con
	import win32console
	import win32ui
	h = win32console.GetConsoleWindow()
	wnd = win32ui.CreateWindowFromHandle(h)
	menu = wnd.GetSystemMenu()
	menu.DeleteMenu(win32con.SC_CLOSE, win32con.MF_BYCOMMAND)

_g_is_start_invoke = False
def start(force=False):
	global g_init_funcs,_g_is_start_invoke
	if is_run_all() and not force:
		return
	if _g_is_start_invoke:
		return
	import log
	log.success("utility start, pid=%d, ppid=%d"%(os.getpid(),os.getppid()))
	for func in g_init_funcs:
		func()
	_g_is_start_invoke = True

def is_started():
	global _g_is_start_invoke
	return _g_is_start_invoke

g_exited = False

def is_exited():
	global g_exited
	return g_exited
	
def finish():
	import log
	global g_exited
	g_exited = True
	global g_fini_funcs,_g_is_start_invoke
	for func in g_fini_funcs:
		func()
	_g_is_start_invoke = False
	import log
	log.error("process exited, living " + str(running_time()) + " seconds")

g_last_ctrl_c_ticks = 0


import signal
def exit(signum, frame):
	import log
	global g_last_ctrl_c_ticks
	if signum == signal.SIGINT:
		old = g_last_ctrl_c_ticks
		g_last_ctrl_c_ticks = ticks()
		if is_win() and ticks() - old > 500:
			import enhance,lock
			ss = enhance.getTrace(showAll = True)
			log.info(ss)
			lock.show()
			log.error('user press Ctrl+C, print thread stack')
			return
		else:
			log.error('user press Ctrl+C, system quit!')
	else:
		log.error("system kill")
	finish()
	signal.signal(signum,  signal.SIG_DFL)
	os.kill(os.getpid(), signum)
	sys.exit(0)
	
def showAllTrace(signum, frame):
	import log
	import enhance
	if signal.SIGUSR1 == signum:
		log.error('recv USER1 signal, print thread stack')
	elif signal.SIGUSR2 == signum:
		log.error('recv USER2 signal, print thread stack')
	s = enhance.getTrace(showAll=True)
	log.info(s)

#如果出现下面错误，而记得在提前import utility 
#error from callback <bound method client._onError of <__main__.client object at 0x0000000002D80F28>>: signal only works in main thread	
signal.signal(signal.SIGINT, exit)
signal.signal(signal.SIGTERM, exit)
if not is_win():
	signal.signal(signal.SIGUSR1, showAllTrace)
	signal.signal(signal.SIGUSR2, showAllTrace)


#执行shell命令，并返回结果 
def run_cmd(cmd,showLog=True):
	import log
	import subprocess
	if showLog:
		log.debug("#" + cmd)
	proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	proc.wait()
	r = [proc.stdout.read(),proc.stderr.read()]
	if is_python3():
		if is_win():
			r[0] = r[0].decode("gb2312")
			r[1] = r[1].decode("gb2312")
		else:
			r[0] = r[0].decode("utf-8")
			r[1] = r[1].decode("utf-8")
	if len(r[0]):
		if showLog:
			log.debug(r[0])
	if len(r[1]):
		if showLog:
			log.warning(r[1])	
		if len(r[0]) == 0:
			r[0] = r[1]
	return r	

def is_ip_address(ip):
	if not isinstance(ip,str):
		return False
	import re
	s = "^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$"
	return re.compile(s).match(ip) is not None

#根据字符串取出对象的值 
#path例子:  obja.objd.objc 或 obja.1.objb
def _splitPath(path):
		i =  path.find(".")
		if i == -1:
			return (path,"")
		else: 
			return (path[0:i],path[i+1:])
	
#根据字符串取出对象的值 
#path例子:  obja.objd.objc 或 obja.1.objb	
def get_attr(obj,path):
	if path == "":
		return None
	pp = _splitPath(path)	 
	if isinstance(obj,dict):
		if path in obj:
			return obj[path]
		if pp[0] in obj:
			o = obj[pp[0]]
		else:
			return None
	elif isinstance(obj,(list,tuple)):
		assert pp[0].isdigit()
		i = int(pp[0])
		if i < len(obj):
			o = obj[i]
		else:
			return None
	else:
		if hasattr(obj,path):
			return getattr(obj,path)	
			
		if hasattr(obj,pp[0]):
			o = getattr(obj,pp[0])	
		else:
			return None 
			
	if pp[1] == "":
		return o
	else:
		return get_attr(o,pp[1])
	
#根据字符串设置对象的值 
#path例子:  obja.objd.objc 或 obja.1.objb	
def set_attr(obj,path,value):
	if path == "":
		return False
	pp = _splitPath(path)	 
	if isinstance(obj,dict):
		if path in obj:
			obj[path] = value
			return True
		if pp[1]:
			if pp[0] in obj:
				return set_attr(obj[pp[0]],pp[1],value)
			else:
				return False
		else:
			obj[pp[0]] = value
			return True
			
	elif isinstance(obj,(list,tuple)):
		assert pp[0].isdigit()
		i = int(pp[0])
		if i < len(obj):
			if pp[1]:
				return set_attr(obj[i],pp[1],value)
			else:
				obj[i] = value
				return True
		else:
			return False
	else: 
		if hasattr(obj,path):
			setattr(obj,path,value)	
			return True
		if pp[1]:
			if hasattr(obj,pp[0]):
				return set_attr(getattr(obj,pp[0]),pp[1],value)
			else:
				return False
		else:
			setattr(obj,pp[0],value)	
			return True
			

def byteStr(value):
	value = float(value)
	if value < 1024:
		return str(int(value))+"B"
	if value < 1024*1024:
		return  "%0.2f"%(value/1024.0)+"M"
	return "%0.2f"%(value/1024.0/1024.0)+"G"
	
	
def killThread(thread):
	def _async_raise(tid, exctype):
		"""raises the exception, performs cleanup if needed"""
		import inspect
		import ctypes
		tid = ctypes.c_long(tid)
		if not inspect.isclass(exctype):
			exctype = type(exctype)
		ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype)) 
	_async_raise(thread.ident, SystemExit)
	
g_load_modules = {}

def setModule(name):
	g_load_modules[name] = True

def waitModule(name):
	if name not in g_load_modules:
		return False
	return True
	
#############################	unit test	###########################
def testkillthread():
	def foo():
		import time
		while True:
			time.sleep(1)
	import threading	
	t1 = threading.Thread(target=foo)
	t2 = threading.Thread(target=foo)
	t3 = threading.Thread(target=foo)
	t1.start()
	t2.start()
	t3.start()
	time.sleep(2)
	killThread(t1)
	killThread(t2)
	killThread(t3)
	t1.join()
	t2.join()
	t3.join()
	
def testbyteStr():
	assert byteStr(999) == "999B"
	assert byteStr(1024*11.99) == "11.99M"
	assert byteStr(1024*1024*11.99) == "11.99G"
	
def test_get_attr(): 
	obj = {}
	assert set_attr(obj,"a",1)
	assert set_attr(obj,"b",2)
	assert not set_attr(obj,"abc.1",1)	
	assert obj["a"] == 1
	assert obj["b"] == 2
	
	obj = empty_class()
	assert set_attr(obj,"a",1)
	assert set_attr(obj,"b",2)
	assert not set_attr(obj,"abc.1",1)	
	assert obj.a == 1
	assert obj.b == 2
	
	obj = [] 
	assert not set_attr(obj,"0",1)
	
	obj = [1,2,3,4]
	assert get_attr(obj,"0.") == 1
	assert get_attr(obj,"3") == 4

	assert set_attr(obj,"1",111)
	assert set_attr(obj,"3.",1115)
	assert get_attr(obj,"1") == 111
	assert get_attr(obj,"3") == 1115
	
	
	obj = {"aa":[1,2,3,4],"b":2}
	assert get_attr(obj,"aa.2") == 3
	assert get_attr(obj,"b") == 2
	assert set_attr(obj,"aa.1",1331)
	assert get_attr(obj,"aa.1") == 1331
	assert set_attr(obj,"b",17331)
	assert get_attr(obj,"b") == 17331
	
	
	class gggg:
		def __init__(self):
			self.g = 1111
			self.e = {"aa":[1,2,3,4],"b":2}
	
	p = "abc.eee.0.g"
	obj = {}
	obj["abc"] = {"eee":[gggg()]}
	obj["ab.c"] = "dddddddd"
	obj["abd.c"] = {"ee.e":33333}
	assert get_attr(obj,p) == 1111
	assert set_attr(obj,p,137331)
	assert get_attr(obj,p) == 137331
	
	assert get_attr(obj,"ab.c") == "dddddddd"
	assert set_attr(obj,"ab.c","r3ee")
	assert get_attr(obj,"ab.c") == "r3ee"
	
	#print(get_attr(obj,"abd.c.ee.e"),get_attr(obj,"abd.c"))
	#TODO:不支持这种连续打点的 
	#assert get_attr(obj,"abd.c.ee.e") ==  33333
	g = gggg()
	assert get_attr(g,"e.aa.2") == 3
	assert set_attr(g,"e.aa.2","r3ee3333")
	
	assert get_attr(g,"e.aa.2") == "r3ee3333"
	assert get_attr(g,"e.b") == 2
	assert set_attr(g,"e.b",3333333)
	assert get_attr(g,"e.b") == 3333333
	
	obj = {"a":{"c.d":111}}
	assert set_attr(obj,"a.c.d",999)
	assert get_attr(obj,"a.c.d") == 999
	  
def test_running_time():
	t = running_time()
	import lock
	lock.sleep(1)
	t2 = running_time()
	print(dir(t2))
	assert (t2.total_seconds() - t.total_seconds()) <1.1
	assert (t2.total_seconds() - t.total_seconds()) > 0.8
	
def test_set():
	assert is_test()
	set_is_test(False)
	assert not is_test()
	set_is_test(True)
	assert is_test()
	
def test_get_app_name():
	import enhance
	n = enhance.funcname(app_name)
	print(n)
	assert n.find("utility.py") != -1
	assert n.find("app_name()") != -1
	assert enhance.funcname(_utility.is_python3) == "_utility.pyc:6: is_python3()" or enhance.funcname(_utility.is_python3) == "_utility.py:6: is_python3()"
	assert "common" == app_name()

def test_is_ip_address():
	assert is_ip_address("0.0.0.0")
	assert is_ip_address("127.0.0.1")
	assert is_ip_address("255.255.255.255")
	assert not is_ip_address("255.255.255.255.")
	assert not is_ip_address("255.255.256.255")
	assert not is_ip_address("")
	assert not is_ip_address(None)

	
def test_run_cmd():
	if is_win():
		r = run_cmd("ping 127.0.0.1")
		assert r[0].find("127.0.0.1") != -1
	else:
		r = run_cmd("ping 127.0.0.1 -c 3")
		assert r[0].find("bytes from 127.0.0.1: icmp_seq=") != -1
	assert r[1] == ""
	
	r = run_cmd("wrong 127.0.0.1")
	if is_win():
		assert r[0].find("不是内部或外部命令") != -1
		assert r[1].find("不是内部或外部命令") != -1
	else:
		assert r[0].find("command not found") != -1
		assert r[1].find("command not found") != -1
	
	if not is_win():
		r = run_cmd("ping 127.0.0.1",False,5)
		assert r[3]
		
	
def test_init():
	global g_init_funcs,g_fini_funcs
	
	r1 = []
	@init()
	def init1():
		r1.append("1")
			
	@init()	
	def init2():
		r1.append("2")
		
	@fini()
	def fini1():
		r1.append("3")
		
		
	@fini()	
	def fini2():
		r1.append("4")
		
	start()
	assert equal(["1","2"],r1)
	finish()
	assert equal(["1","2","3","4"],r1)
	
	r2 = []
	class aa:
		def init(self):
			r2.append((id(self),1))
		def fini(self):
			r2.append((id(self),2))			
	a = aa()	
	auto_global(a)
	start()
	assert equal([(id(a),1)],r2)
	finish()
	assert equal([(id(a),1),(id(a),2)],r2)

	r3 = []
	class aa2:
		def fini(self):
			r3.append((id(self),1))			
	a2 = aa2()	
	auto_global(a2)
	start()
	assert equal([],r3)
	finish()
	assert equal([(id(a2),1)],r3)

class aaaa2:
	def __init__(self):
		self.i = 12323
		self.s = "fsds"
		self.d = now()
		self.e = {"a":bbbb(),"b":"34342sdf"}
	
	def af():
		pass
	
	def bf(self):
		pass
		
class bbbb:
	def __init__(self):
		self.l = [1,2,3,4]
		self.ll = {2,343}
		
def test_classname():
	assert "" == classname(None)
	assert classname(aaaa2()) == "common.utility.aaaa2"
	a = create_obj(classname(aaaa2()))
	assert isinstance(a,aaaa2)
	
	import common.wx.wx_msg
	nn = "common.wx.wx_msg.text_msg"
	assert classname(common.wx.wx_msg.text_msg()) == nn
	assert classname(type(common.wx.wx_msg.text_msg())) == nn
	assert classname(common.wx.wx_msg.text_msg) == nn
	a = create_obj(classname(common.wx.wx_msg.text_msg()))
	print(type(a))
	assert isinstance(a,common.wx.wx_msg.text_msg)
		
def test_clone():
	import common.utility
	c = create_obj("common.utility.aaaa2")
	assert c.s == "fsds"
	a = aaaa2()
	b = clone(a)
	assert clone(None) is None
	assert id(a) != id(b)
	assert id(a.e) != id(b.e)
	assert id(a.e["a"]) != id(b.e["a"])
	assert cmp(a,b,0,0,True) == 0
	a.e = None
	b = clone(a)
	assert id(a) != id(b)
	assert b.e is None
	assert cmp(a,b,0,0,True) == 0
	assert equal(a,b) 
	
def test_str_obj():
	set_is_test(True)
	assert str_obj("a123") == "a123"
	assert str_obj(123) == "123"
	assert str_obj(-123.3) == "-123.3"
	assert str_obj(None) == "[None]"
	assert str_obj([]) == "[len=0]"
	assert str_obj({}) == "[len=0]"
	assert str_obj(set()) == "[len=0]"
	assert str_obj({1,2,3,4}) == "[len=4: 1,2,3,4]"
	assert str_obj(datetime.datetime(2015,7,4,12,45,41,951000)) == "2015-07-04 12:45:41.951"
	
	class ttt:
		def __init__(self):
			self.a = "a1"
			self.b = 1123
			
	class ttt2:
		def __init__(self):
			self.dddd = "a1"
			self.ffff = 1123
			self.t = ttt()
			
	assert str_obj(-123.3) == "-123.3"
	assert str_obj(ttt()) == "[ttt: a=`a1`, b=`1123`]"
	assert str_obj(ttt2()) == "[ttt2: dddd=`a1`, ffff=`1123`, t=`[ttt: a=`a1`, b=`1123`]`]"
	ll = (ttt2(),ttt(),ttt())
	dd = {"ddddddd":ttt(),"eeeee":ttt2()}
	assert str_obj(ll) == "[len=3: [ttt2: dddd=`a1`, ffff=`1123`, t=`[ttt: a=`a1`, b=`1123`]`],[ttt: a=`a1`, b=`1123`],[ttt: a=`a1`, b=`1123`]]"
	assert str_obj(list(ll)) == "[len=3: [ttt2: dddd=`a1`, ffff=`1123`, t=`[ttt: a=`a1`, b=`1123`]`],[ttt: a=`a1`, b=`1123`],[ttt: a=`a1`, b=`1123`]]"
	assert str_obj(dd) == "[`ddddddd`=`[ttt: a=`a1`, b=`1123`]`, `eeeee`=`[ttt2: dddd=`a1`, ffff=`1123`, t=`[ttt: a=`a1`, b=`1123`]`]`]"
	
	@no_print()
	class gggg:
		def __init__(self):
			self.aa = "dfdf"
			
	assert str_obj((1,gggg())) == "[len=2: 1,no_printable]"

def test_abstract():
	@abstract
	def test1():
		assert 0
		
	class test2():
		@abstract	
		def t():
			assert 0
	try:
		test1()
	except NotImplementedError as e:
		if is_python3():
			assert str(e) == "Can't invoke abstract method `common.utility.<class 'function'>.test1`"
		else:
			assert str(e) == "Can't invoke abstract method `common.utility.<type 'function'>.test1`"
		
	try:
		test2().t()
	except NotImplementedError as e:
		if is_python3():
			assert str(e).find("`<class 'common.utility.test") != -1 		
		else:
			assert str(e) == "Can't invoke abstract method `common.utility.test2.t`"		

def test_catch():
	@catch
	def test1(a,b):
		raise NotImplementedError("lalalal")
	test1(1,2)
	test1(a=1,b=2)
	
	@catch
	def test2(a1,a2,a3,a4):
		raise NotImplementedError("lalalal")
	test2(1,2,3,4)

def test_cmp_dict():
	a1 = {}
	a2 = {}
	a1[1] = "111"
	a1[2] = "222"
	a1[3] = "333"
	
	a2[1] = "111"
	a2[2] = "222"
	assert cmp_dict(a1,a2,0,0,True) != 0
	assert cmp(a1,a2,0,0,True) != 0
	
	a2[3] = "333"
	assert cmp_dict(a1,a2,0,0,True) == 0
	assert cmp(a1,a2,0,0,True) == 0
	
	a1 = {}
	a2 = {}
	a1[1] = "111"
	a1[2] = "222"
	a1[3] = "333"
	a2[1] = "111"
	a2[2] = "222"
	a2[3] = None
	assert cmp_dict(a1,a2,0,0,True) != 0
	
	
def test_cmp_list():
	a1 = [1,2,4,5,6]
	a2 = [1,2,4,5,6,5]
	assert cmp_list(a1,a2,0,0,True) != 0
	assert cmp(a1,a2,0,0,True) != 0
	
	a2 = [1,2,6,5,4]
	assert cmp_list(a1,a2,0,0,True) == 0
	assert cmp(a1,a2,0,0,True) == 0
	
	a1 = (2,1,4,5,6)
	a2 = (1,2,4,5,6,5)
	assert cmp_list(a1,a2,0,0,True) != 0
	assert cmp(a1,a2,0,0,True) != 0
	
	a2 = (1,2,6,5,4)
	assert cmp_list(a1,a2,0,0,True) == 0
	assert cmp(a1,a2,0,0,True) == 0
	
	assert cmp(None,None,0,0,True) == 0
	assert cmp(2.001,2.002,0.01,0,True) == 0
	assert cmp(2.001,2.002,0.0009,0,True) != 0
	assert cmp( datetime.datetime(1979,7,25,12,12,35), datetime.datetime(1979,7,25,12,12,36),0.0,2,True) == 0
	assert cmp( datetime.datetime(1979,7,25,12,12,35), datetime.datetime(1979,7,25,11,12,35),0.0,3601,True) == 0
	assert cmp( datetime.datetime(1979,7,25,12,12,35), datetime.datetime(1979,7,25,11,12,35),0.0,3599,True)
	
	assert cmp_set({1,2,3,4},{4,3,2,1}) == 0
	assert cmp_set({1,2,3,4},{4,3,1}) != 0

def test_create_obj():
	import datetime
	d = create_obj("datetime.datetime",1979,7,25,12,12,35)
	assert d == datetime.datetime(1979,7,25,12,12,35)
	
def test_random():
	a = {}
	assert {} == rand_dict(a,None,None)
	a = []
	assert [] == rand_list(a,None)
	a = 1
	print(random(a))
	a = 1.1
	print(random(a))
	a = ""
	print(random(a))
	def f():
		return 0
	b = f
	a = []
	print(random(a,f))
	a = {}
	print(random(a,None,f,f))
	class aaaa:
		def __init__(self):
			self.a = 1
			self.b = 1.0
	a = aaaa()
	print_obj(random(a))
	assert a.a != 1
	assert a.b!= 1.0
	a = datetime.datetime.min
	assert isinstance(a,datetime.datetime)
	
	a = True
	a = random(a)
	assert isinstance(a,bool)
		
def test_random_str():
	str = random_str()
	assert 32 == len(str)	
 
def run_tests():
	import inspect
	s = inspect.stack()[1:] 
	file = s[0][1]  
	
	import pytest
	set_is_test(True)
	if is_win():
		p = os.path.dirname(file)
		if p != "":
			os.chdir(p)
	if is_ros():
		import ros2.rosUtility
		ros2.rosUtility.init("unittest")
		
	if not os.path.isabs(file):
		pytest.main(["-vv","-x",file])				
	else:
		pytest.main(["-vv","-x",os.path.basename(file)])
		
	
def run_all_tests():
	import pytest
	set_is_test(True)
	if not is_test():
	   return
	
	for root, dirs, files in os.walk(os.getcwd()):
		for name in files:
			if name[-3:] == ".pyc":				
				pytest.main(r"-v -x " + name)

def change_stdout():
	#解决python3 UnicodeEncodeError: 'gbk' codec can't encode character '\xXX' in position XX问题 
	import io  
	import sys  
	import urllib.request  
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #改变标准输出的默认编码
	
def test_invoke_func():
	assert invoke_func("_utility","","is_python3") == True
	assert invoke_func("_utility","","os_cmp",1,2) != 0
	assert invoke_func("_utility","","os_cmp","1","1")  == 0


if __name__ == '__main__': 
	test_run_cmd()
	run_tests(__file__)
	#while True:
	#	log.debug("this is a test log %d %s",1323,"sss3")
	#	log.info("this is a test log %d %s",44,"sss2")
	#	log.warning("this is a test log %d %s",1,"sss4")
	#	log.error("this is a test log %d %s",1,"sss1")
	#	time.sleep(10)
	
