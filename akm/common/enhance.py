#coding=utf-8 
# ycat			2016-10-11      create
#取当前模块的方法 sys.modules[__name__]
import sys,os
import inspect
import threading
import traceback
import functools
if "common" not in sys.path:
	sys.path.append("common")
import _utility

#偏函数的使用 
def bind(func,*param,**params):
	return functools.partial(func,*param,**params)
	
#实现虚函数的修饰符
def abstract(func):
	def __call(*p):
		c = func.__module__ + "." + str(func.__class__)
		if len(p) > 0:
			c = p[0].__class__
		raise NotImplementedError("Can't invoke abstract method `%s.%s`"%
			(c,func.__name__))
	return __call


#检查函数参数列表 
#用法:  
#@check(a=int,b=(int,float))
#func(a,b)
def check(**types):
	#http://www.cnblogs.com/huxi/archive/2011/01/02/1924317.html 
	def check_accepts(func):
		info = inspect.getargspec(func)
		for t in types:
			assert t in info.args
			
		def raise_exception(funcName,argName,checkType,actualType):
			s = str(checkType)
			if isinstance(checkType,tuple):
				s = " or ".join(["'"+str(c)+"'" for c in checkType])
			msg = "TypeError: '%s.%s' argument must be %s, not '%s'"%(funcName,argName,s,str(actualType))
			raise TypeError(msg) 
		
		def _isinstance(value,t):
			if t == type(float): #支持默认类型转换 
				return isinstance(value,(float,int))
			else:
				return isinstance(value,t)
		
		def _check(func,key,value):
			if key not in types:
				return
			c = types[key]
			if isinstance(c,(tuple,list)) and len(c)!=0:
				find = False
				for c1 in c: 
					if _isinstance(value,c1):
						find = True
						break
				if not find:
					raise_exception(funcname(func,",".join(info.args)),key,c,type(value))
			else:
				if not _isinstance(value,c):
					raise_exception(funcname(func,",".join(info.args)),key,c,type(value))
			
		def new_func(*args, **kwds):
			assert len(info.args) >= len(args)
			for i,a in enumerate(args):
				k = info.args[i]
				_check(func,k,a)
				
			for k in kwds:
				_check(func,k,kwds[k])
			return func(*args, **kwds)
			
		new_func.__name__ = func.__name__
		return new_func
	return check_accepts
	

#自动处理异常的修饰符
#用法 @catch 
def catch(func):
	def __call(*p,**pp):
		try:
			return func(*p,**pp)
		except Exception as e:
			import log
			log.exception("invoke "+str(func),e)
			return None
	return __call	
	
#提供单例机制 	
def singleton(cls, *args, **kw):
	instances = {}
	def _singleton(*args, **kw):
		if cls not in instances:
			instances[cls] = cls(*args, **kw)
		return instances[cls]
	return _singleton

#提供自动打印机制
def printable(cls, *args, **kw): 
	def printData(obj):
		import utility 
		return utility.str_obj(obj) 
	setattr(cls,"__str__",printData)  
	return cls
#	return __call	

#注册和回调机制 
class event:
	def __init__(self,showDebug = False):
		self.funcs = {} 
#		self.m_lock = threading.RLock()
		self.showDebug = showDebug
		
#	@_utility.lock(None)
	def connect(self,func):
		self.funcs[func] = func
		return id(func)
	
#	@_utility.lock(None)
	def disconnect(self,func):
		if func in self.funcs:
			del self.funcs[func]
	
#	@_utility.lock(None)
	def emit(self, *args, **kwargs):
		ff = list(self.funcs.values())
#		self.m_lock.release()
		for f in ff:
			if f is None:
				continue
			if self.showDebug:
				import utility
				import log
				log.debug("emit event: ",self,utility.str_obj(args),utility.str_obj(kwargs))
			f(*args,**kwargs)
		
#	@_utility.lock(None)
	def count(self):
		return len(self.funcs)

#只支持普通函数，不支持成员变量 		
def connect(sig):
	def __call(func):
		sig.connect(func)
		return func
	return __call		
	
def is_callable(obj):	
	return hasattr(obj,"__call__")

#取函数信息，会受修饰符影响。。。
def funcname(func,argsList=None):
	co = func.__code__
	if argsList:
		return "%s:%d: %s(%s)"%(os.path.basename(co.co_filename),co.co_firstlineno,co.co_name,argsList)
	return "%s:%d: %s()"%(os.path.basename(co.co_filename),co.co_firstlineno,func.__name__)#co.co_name)

def classname(obj):
	if obj is None:
		return ""
	if isinstance(obj,type):
		return obj.__module__ + "." + obj.__name__
	else:
		return obj.__module__ + "." + obj.__class__.__name__

#根据类型名取类型 
def getType(class_name):
	rr = str(class_name).rsplit('.', 1)
	if len(rr) == 2:
		(module_name, class_name) = rr[0],rr[1]
		module_meta = __import__(module_name, globals(), locals(), [class_name])
		return getattr(module_meta, class_name)
	if isinstance(__builtins__,dict) and class_name in __builtins__:
		return __builtins__[class_name]
	return getattr(__builtins__,class_name)
	
def typeName(cls):
	if not isinstance(cls,type) and not is_callable(cls):
		cls = type(cls)
	if hasattr(cls,"__module__"):
		if cls.__module__ == "builtins":
			return cls.__name__
		return cls.__module__+"."+cls.__name__
	return str(cls)

#本类用来动态创建类的实例
def create_obj(class_name, *args, **kwargs): 
	'''动态创建类的实例。 
	[Parameter] 
	class_name - 类的全名（包括模块名） 
	*args - 类构造器所需要的参数(list) 
	*kwargs - 类构造器所需要的参数(dict) 
	[Return] 
	动态创建的类的实例 
	[Example] 
	class_name = 'knightmade.logging.Logger' 
	logger = create_obj(class_name, 'logname') 
	'''
	try:
		class_meta = getType(class_name)
	except AttributeError as e:
		import log
		log.exception("create %s.%s"%(module_name,class_name),e)
		raise
	return class_meta(*args, **kwargs) 	
	
#通过反射运行函数
#import xxx.bbb
# ccc()
#这样调用 invoke_func("xxx.bbb","bbb","ccc")
#import xxx
# ccc()
#这样调用 invoke_func("xxx","","ccc")
def invoke_func(import_name,module_name,func_name,*args,**kwargs):
	module = __import__(import_name)
	if module_name == "":
		func = getattr(module, func_name)
		return func(*args, **kwargs)
	else:
		mm = getattr(module, module_name)
		func = getattr(mm, func_name)
		return func(*args, **kwargs)	
	

	
def getThreadStack(id=None):
	def _get_thread(tid):
		for t in threading.enumerate():
			if t.ident == tid:
				return t
		return None
	
	info = ""
	for tid,stack in sys._current_frames().items():
		if id and id != tid:
			continue
		t = _get_thread(tid)
		if t is None:
			continue
		info += 'name=%s, pid=%d, tid=%d\n' % (t.name,os.getpid(),tid)
		try:
			ss = traceback.extract_stack(stack)
		except Exception as e:
			print(e)
		index = 0
		for filename, lineno, func, line in ss:
			if func == "_bootstrap":
				continue
			if func == "_bootstrap_inner":
				continue	
			
			info += '[%02d] File "%s", line %d, in %s() \n'%(index+1,filename.replace("\\","/"),lineno,func)
			index += 1
		info += "\n"
	return info


def getTrace(showAll=False):
	if showAll:
		return getThreadStack()
	else:
		return getThreadStack(threading.currentThread().ident)
		
	#import inspect,threading
	#r = "Show Trace : name=%s, pid=%d, ppid=%d, tid=%d\n"%(threading.currentThread().name,os.getpid(),os.getppid(),threading.currentThread().ident)
	#s = inspect.stack()[1:]
	#index = 0
	#for i,ss in enumerate(s): 
	#	if ss[1] == "<frozen importlib._bootstrap>":
	#		continue
	#	if ss[1] == "<frozen importlib._bootstrap_external>":
	#		continue
	#	if ss[3] == "_bootstrap":
	#		continue
	#	if ss[3] == "_bootstrap_inner":
	#		continue	
	#	#[05] File "c:\python3\lib\threading.py", line 885, in _bootstrap 
	#	r += '[%02d] File "%s", line %d, in %s \n'%(index+1,ss[1],ss[2],ss[3])
	#	index += 1
	#return r
	
def showTrace(showAll=False):
	s = getTrace(showAll = showAll)  
	print(s)
	return s
	
def fileInfo():
	import inspect
	s = inspect.stack()[1:][1] 
	i = s[1].rfind("\\")
	if i == -1:
		i = s[1].rfind("/")
	if i == -1:
		f = s[1]
	else:
		f = s[1][i+1:]  
	return s[3]+"() at " + f + ":" + str(s[2])  
	 
	 
class empty_class:
	pass
	
def empty_func(*param,**params):
	pass
	
	
#查出调用者 
def parent():
	import traceback
	s = traceback.extract_stack()
	return s[-3][2]
	
	
def isIterable(value):
	import collections.abc
	return isinstance(value,collections.abc.Iterable)

	

#objgraph能够通过图的形式展示对象之间的引用情况:
#需下载graphviz用gvedit.exe打开查看 
#下载地址：https://graphviz.gitlab.io/_pages/Download/Download_windows.html
#把C:\Program Files (x86)\Graphviz2.38\bin配置到环境变量中 
def showRef(obj):
	import objgraph	#sudo apt-get install xdot;pip install objgraph
	objgraph.show_refs(obj, filename='ref_topo.png')


#######################################
def testfileInfo():
	def foo():  
		return fileInfo() 
	assert foo() == "enhance.py+254 testfileInfo()" 
	
_event_test_ret = ""
def test_event():
	global _event_test_ret
	class ggg:
		def __init__(self):
			pass
		def foo1(self,a,b,c):
			global _event_test_ret
			_event_test_ret += str(a)+str(b)+str(c)+ "foo1"
	
	def foo2(a,b,c):
		global _event_test_ret
		_event_test_ret += str(a)+str(b)+str(c)+ "foo2"
	
	g = ggg()
	s = event()
	s.connect(g.foo1)
	s.emit(1,2,3)
	assert _event_test_ret == "123foo1"
	_event_test_ret = ""
	assert 1 == s.count()
		
	s.connect(g.foo1)
	assert 1 == s.count()
	s.emit(a=4,b=5,c=6)
	assert _event_test_ret == "456foo1"
	_event_test_ret = ""
	
	s.connect(foo2)
	s.emit(a=7,b=8,c=9)
	assert _event_test_ret == "789foo1789foo2" or _event_test_ret == "789foo2789foo1"
	assert 2 == s.count()
	_event_test_ret = ""
	
	s.disconnect(g.foo1)
	assert 1 == s.count()
	s.emit(a=10,b=11,c=9)
	assert _event_test_ret == "10119foo2"
	_event_test_ret = ""
	
	s2 = event()
	@connect(s2)
	def foo3(a):
		global _event_test_ret
		_event_test_ret += str(a)+ "foo3"
	s2.emit(100)
	assert _event_test_ret == "100foo3"
	_event_test_ret = ""
	
	#只支持普通函数，不支持成员变量
	#class ggg2:
	#	def __init__(self):
	#		pass
	#	@connect(s2)
	#	def foo4(self,a):
	#		global _event_test_ret
	#		_event_test_ret += str(a)+ "foo4"
	#
	#assert _event_test_ret == "200foo3200foo4"	or _event_test_ret == "200foo4200foo3"		

def test_check():
	@check(a=list,b=int,c=str)
	def test2(b,c,a):
		pass
	test2(1,"",[])
	test2(b=1,c="",a=[])
	test2(1,"",a=[])
	try:
		test2("","",[])
		assert 0
	except TypeError:
		pass
	
	@check(b=int,c=(float,str))
	def test1(b,c,a):
		pass
	test1(1,"",0.0)
	test1(1,1.1,0)
	class aaa:
		def __init__(self):
			pass
			
		@check(a=list,b=int,c=str)
		def test2(self,a,b,c):
			pass
			
		@staticmethod
		@check(a=list,b=int,c=str)
		def test3(a,b,c):
			pass
	a = aaa()
	a.test2([],1,"")
	try:
		a.test2("aaa",1,"")
		assert 0
	except TypeError:
		pass
	aaa.test3([],1,"")
	@check(a=aaa)
	def test4(a):
		pass
	test4(aaa())

#python多线程，数据居然没有问题  
g_test_thread = 0
def testThreads():
	import threading,time
	global g_test_thread
	g_test_thread = 0
	def foo():
		global g_test_thread
		for k in range(30):
			g_test_thread += 1
			time.sleep(0)
			print(g_test_thread)
	tt = []
	for g in range(30):
		tt.append(threading.Thread(target=foo))
	for t in tt:
		t.start()
	for t in tt:
		t.join()
	assert g_test_thread == 30*30

def testPrintable():
	@printable
	class GGGG:
		def __init__(self):
			self.aaa = 1
			self.bbb = "fffff1"
	assert str(GGGG()) == "<GGGG>{ aaa=`1`, bbb=`fffff1`}" 
	
def testbind():
	def foo(a,b):
		return a,b
		
	assert bind(foo,"111")("222") == ("111","222")
	assert bind(foo,a="1111")(b="222") == ("1111","222")

def testshowtrace():
	def run():
		import time
		time.sleep(2)
		showTrace()
		showTrace(True)
	
	t1 = threading.Thread(target=run)
	t2 = threading.Thread(target=run)
	
	t1.start()
	t2.start()
	t1.join()
	
def testtype():
	assert "str" == typeName(str)
	assert str == getType("str")
	assert "float" == typeName(float)
	assert float == getType("float")

def testmultithread_lock():
	import time
	e = event()
	def foo1():
		for i in range(50):
			e.emit()
			print("foo1")
			time.sleep(0.1)
	
	class A:
		def foo3(self):
			time.sleep(0.2)
		
	def foo2():
		rr = []
		for i in range(50):
			a = A()
			e.connect(a.foo3)
			rr.append(a.foo3)
			time.sleep(0.1)
			print("foo2",e.count())
			
		for r in rr:
			e.disconnect(r)
			time.sleep(0.1)
			print("del foo2",e.count())
			
	t = threading.Thread(target=foo1)
	t2 = threading.Thread(target=foo1)
	t3 = threading.Thread(target=foo1)
	t4 = threading.Thread(target=foo2)
	t.start()
	t2.start()
	t3.start()
	t4.start()
	t.join()
	t2.join()


if __name__ == '__main__':
	test_event()
	testmultithread_lock()
	assert 0
	testtype()
	testshowtrace()
	assert 0
	import utility
	utility.run_tests()
	
	
	
	
	
	
	
	
	