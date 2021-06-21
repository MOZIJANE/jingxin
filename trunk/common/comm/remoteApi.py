#coding=utf-8
# ycat			2017-07-27	  create 
# 远程调用api，调用属性会变成函数 
import sys,os
import threading,time
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import enhance
import comm.cmd
import log
		 
class wrapper:
	def __init__(self,module,port):
		self.module = module
		self.port = port
		self.isExisted = False
		
	def create_client(self,ip="127.0.0.1",timeout=3000):
		return client(self.module,ip,self.port,timeout=timeout)
	
	def start_server(self):
		self.server = server(self.module,self.port)
		
			
	
class client:
	def __init__(self,module,ip,port,timeout = 3000):
		self.module = module
		self._comm = comm.cmd.cmd_client()
		self._comm.encode = comm.mgr._encode3
		self._comm.decode = comm.mgr._decode3
		self._comm.connect(ip,port)
		self._timeout = timeout
		
	#equal __init__
	def create(self,*param,**params):
		self._invoke("__init__",*param,**params)
		
	def __getattr__(self, attr): 
		if attr[0] == "_":
			return getattr(self,attr)
		return enhance.bind(self._invoke, attr)
		
	def _invoke(self,typeid,*param,**params):
		ret = self._comm.send(typeid,(param,params),timeout=self._timeout)
		return ret
		
	def send_quit(self):
		self._comm.send_quit()
		 

class server:
	def __init__(self,module,port):
		self.comm = comm.cmd.cmd_server()
		self.comm.encode = comm.mgr._encode3
		self.comm.decode = comm.mgr._decode3
		self.comm.handle = self.handle
		self.module = module
		self.obj = None
		log.info("start api service",module,"at port:",port,",pid=",os.getpid())
		self.comm.start(port)
		
	def handle(self,typeid,param): 
		try:
			args   = param[0]
			kwargs = param[1]
			if typeid == "__init__":
				self.obj = self.module(*args,**kwargs)	
				return True,None
				
			if self.obj is None:
				log.error(self.module,"isn't created")
				return False,enhance.classname(self.module)+" isn't created"
				
			func = getattr(self.obj,typeid)
			if enhance.is_callable(func):
				ret = func(*args,**kwargs)	
			else:
				ret = func
			return True,ret
		except Exception as e:
			raise 
			#log.exception("invoke remote "+enhance.classname(self.module)+"."+typeid+" failed",e)
			#return False, "invoke remote "+enhance.classname(self.module)+"."+typeid+" failed: " + str(e)
		
		
###################################
def testclient():	
	import utility
	class foo:
		def __init__(self,a):
			self.a = a
			
		def sum(self,a,b):
			return a+b
			
		@property
		def count(self):
			return self.a
			
		def set_a(self,v):
			self.a = v
			
		def error(self):
			raise Exception("this is a test")
			
	utility.start()
	w = wrapper(foo,10001)
	w.start_server()
	
	c = w.create_client()
	c.create(100)
	assert 100 == c.count()
	assert 1000 == c.sum(900,100)
	assert 1000 == c.sum(a=900,b=100)
	assert 1000 == c.sum(900,b=100)
	c.set_a(999)
	assert c.count() == 999
	
	ee = None
	try:
		print(c.error())
		assert 0
	except Exception as e:
		ee = e
	assert ee
	print("finish")
	utility.finish()
	
	
	
if __name__ == '__main__':
	testclient()

	
