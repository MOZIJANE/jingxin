#coding=utf-8 
# ycat			 2015/05/26      create
import os,time,sys
import zmq
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import utility
import log
import comm.mgr
from multiprocessing import Process

class ntf_client:
	def __init__(self):
		self.socket = comm.mgr.create_socket(zmq.SUB)
		self.addr = ""
		self.handles = {}
		self.handles_blur = [] #通配符 
		
	def connect(self,ip,port):
		self.addr = "tcp://" + ip + ":" + str(port)
		log.debug(self.addr + ": start connect ntf")
		self.socket.connect(self.addr)
		comm.mgr.register(self.socket,self._read_handle)
	
	#支持尾部带通配符的情况，但不支持头部带通配符 
	#例如 domain.* 可以接收 domain.1，domain.foo.foo等信息
	def register(self,typeid,func):	
		t = _add_border(typeid)
		if t[-3:] == ".*@":
			t=t[0:-2]
			self.handles_blur.append((t,func))
		if t == "@*@":
			t = "@"
			self.handles_blur.append(("",func))
		if utility.is_python3():
			t2 = t.encode()
		else:
			t2 = t

		#self.socket.setsockopt(zmq.SUBSCRIBE,"".encode()) #read all for test only 
		if t not in self.handles:
			self.socket.setsockopt(zmq.SUBSCRIBE,t2)
			self.handles[t] = []
		self.handles[t].append(func)	
	
	def _read_handle(self):
		msg = self.socket.recv_multipart()
		log.debug("ntf read:{0},{1}".format(*msg))
		m = comm.mgr._decode2(msg[1])
		if utility.is_python3():
			typeid = msg[0].decode()
		else:
			typeid = msg[0]
		if typeid in self.handles:
			for f in self.handles[typeid]:
				try:
					f(_trim_border(typeid),m)
				except Exception as e:	
					log.exception("ntf invoke handles error",e)
			
		for h in self.handles_blur:
			if h[0] == "" or typeid[0:len(h[0])] == h[0]:
				try:
					h[1](_trim_border(typeid),m)
				except Exception as e:
					log.exception("ntf invoke handles error",e)


class ntf_server:
	def __init__(self):
		self.socket = comm.mgr.create_socket(zmq.PUB)
		self.addr = ""
		
	def start(self,port):
		self.addr = "tcp://*:"+str(port)
		log.info(self.addr+": start ntf server... ")
		self.socket.bind(self.addr)
		log.info(self.addr+": start ntf server succeed")
	
	def send(self,typeid,obj):
		t = _add_border(typeid)
		if utility.is_python3():
			t = t.encode()
		self.socket.send_multipart((t,comm.mgr._encode2(obj)))


def _add_border(s):
	return "@"+str(s)+"@" 

def _trim_border(s):
	return s[1:len(s)-1]


################# unit test ###################
def test_run():
	assert _add_border("ssss") == "@ssss@"
	s = _trim_border("@ssss@")
	assert s == "ssss"
	utility.start()
	
	results = []
	results2 = []	
	def func1(typeid,obj):
		results.append((typeid,obj))
	
	c = ntf_client()
	c.connect("127.0.0.1",23001)
	c.register(1001,func1)
	c.register(1002,func1)
	
	s = ntf_server()
	s.start(23001)

	def func2(typeid,obj):
		results2.append((typeid,obj))
		
	c2 = ntf_client()	
	c2.connect("127.0.0.1",23001)
	c2.register(1001,func2)
	time.sleep(1)
	s.send(1001,"lala")
	time.sleep(1)
	assert 1 == len(results)
	assert results[0][0] == "1001"
	assert results[0][1] == "lala"
	assert 1 == len(results2)
	assert results2[0][0] == "1001"
	assert results2[0][1] == "lala"
	s.send(1002,"lala222222222")
	time.sleep(1)
	assert 2 == len(results)
	assert 1 == len(results2)
	assert results[1][0] == "1002"
	assert results[1][1] == "lala222222222"
	
	s.send(10020,"dfdf")
	time.sleep(1)
	assert 2 == len(results)		

	#测试通配符的语法
	results = []
	results2 = []
	c.register("domain.comba.*",func1)
	c.register("domain.comba.9001",func2)
	time.sleep(1)	
	s.send("domain.comba.9001","这是一个测试")
	time.sleep(1)
	assert len(results) == 1
	assert len(results) == len(results2)

	assert results[0][0] == "domain.comba.9001"
	assert results2[0][0] == "domain.comba.9001"
	assert results[0][1] == "这是一个测试"
	assert results2[0][1] == "这是一个测试"
	
	results = []
	results2 = []
	s.send("domain.comba.9009","这是一个测试222")
	time.sleep(1)
	assert len(results) == 1
	assert len(results2) == 0
	assert results[0][0] == "domain.comba.9009"
	assert results[0][1] == "这是一个测试222"
	
	s.send("domain2.comba.9009","这是一个测试222")
	s.send("s","这是一个")
	time.sleep(1)
	assert len(results) == 1
	assert len(results2) == 0
	
	results = []
	results2 = []
	c.register("*",func2)
	time.sleep(1)
	s.send("domain2.comba.9dfs009","这是一sfdfd个测试222")
	s.send("s","这是一dsfsdf个")
	time.sleep(1)
	assert len(results) == 0
	assert len(results2) == 2
	assert results2[0][0] == "domain2.comba.9dfs009"
	assert results2[0][1] == "这是一sfdfd个测试222"
	assert results2[1][0] == "s"
	assert results2[1][1] == "这是一dsfsdf个"
	
	utility.finish()
	print("test finish")

def run_server():
	time.sleep(2) #start client first 
	utility.start()
	n = ntf_server()
	n.start(90101)
	time.sleep(2)
	n.send("10001","hi,ycat")
	utility.finish()
	
_t = None
_r = None
def run_client():
	utility.start()

	def func1(typeid,value):
		global _r,_t
		_t = typeid
		_r = value
		
	n = ntf_client()
	n.connect("127.0.0.1",90101)
	n.register("10001",func1)
	for i in range(12):
		time.sleep(0.5)
		if _r is not None:
			break
	assert _t == "10001"
	assert _r == "hi,ycat"
	utility.finish() 
	 
def start_process_test():
	p = Process(target=run_server)
	p.start()
	run_client()
	p.join()
	
if __name__ == '__main__':
	start_process_test()
	test_run()
	#test_run() 
			
