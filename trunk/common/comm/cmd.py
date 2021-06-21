#coding=utf-8 
# ycat			 2014/05/20      create
import os,time,sys
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import log	
import comm.mgr
import threading
from multiprocessing import Process
import time
import zmq
import utility
	
class RemoteException(Exception):
	def __init__(self,msg):
		Exception.__init__(self,msg)
	
#typeid可以为int或者字符串,返回值的typeid用户不可见，用于服务端返回错误码 	
class cmd_client:
	def __init__(self):
		self.socket = None
		self.poller = zmq.Poller()
		self.addr = ""
		self.is_connected = False
		self.encode = comm.mgr._encode
		self.decode = comm.mgr._decode
		
	def connect(self,ip,port=0):
		if port == 0:
			self.addr = ip
		elif utility.is_ip_address(ip):
			self.addr = "tcp://" + ip + ":" + str(port)
		else:
			#通过名字服务去解析 
			self.addr = ip
			assert port == 0
		return self._reconnect()
	
	def send(self,typeid,obj,timeout=3000,retry=3):
		if not self.is_connected:
			if not self._reconnect():
				raise Exception("Send cmd failed, can't connect %s"%self.addr) 
		data = self.encode(typeid,obj)
		
		#log.debug(self.addr + ": send: {}, {}".format(*data))
		for i in range(retry):
			self.socket.send_multipart(data)			
			socks = dict(self.poller.poll(timeout))
			if socks.get(self.socket) == zmq.POLLIN:
				return self._recv()
			else:
				log.warning(self.addr+": wait reply timeout, timeout=%d, try=%d"%(timeout,i+1))
				self.close()
				self.is_connected = False
				self._reconnect()
		raise Exception("Send cmd timeout %d ms retry %d"%(timeout,retry))
		
	def send_quit(self):
		log.error("send quit signal!",self.addr)
		self.send(comm.mgr.KILL_SIGNAL,"")
		
	def _recv(self):
		data = self.socket.recv_multipart()
		#log.debug(self.addr + ": recv: {}, {}".format(*data))
		
		rr = self.decode(*data)
		if rr[0] == comm.mgr.KILL_SIGNAL:
			return ""
		if rr[0] < 0:
			raise RemoteException(rr[1])
		return rr[1]
	
	def _reconnect(self):
		self.socket = comm.mgr.create_socket(zmq.REQ)
		log.debug(self.addr + ": start connect")
		n = comm.mgr.get_names(self.addr)
		if n is None:
			return False
		r = self.socket.connect(n)
		self.poller.register(self.socket,zmq.POLLIN)
		self.is_connected = True
		return True
		#log.debug(self.addr + ": connect succeed")		
	
	def close(self):
		if self.socket is None:
			return 
		self.socket.setsockopt(zmq.LINGER, 0)
		self.socket.close()
		self.poller.unregister(self.socket)
		
		
class cmd_server:
	def __init__(self):
		self.socket = comm.mgr.create_socket(zmq.REP)
		self.handler = {}
		self.encode = comm.mgr._encode
		self.decode = comm.mgr._decode
	
	def start(self,port):
		self.addr = "tcp://*:" + str(port)
		addr = self.addr
		log.info(addr+": start cmd server... ")
		try:
			self.socket.bind(addr)
		except Exception as e:
			log.exception("Bind the socket to %s"%addr,e)
			os._exit(0)
		comm.mgr.register(self.socket,self._read_handle)
		log.info(addr+": start cmd server succeed")
	
	def _read_handle(self):
		addr = self.addr
		msgs = self.socket.recv_multipart()
		#log.debug(addr + ": recv: {0},{1}".format(*msgs))
				
		try:
			r = self.decode(msgs[0],msgs[1])
		except Exception as e:
			self.socket.send_multipart(self.encode(-1,"decode error,"+ str(e)))
			log.exception(addr + ": client data decode error",e)
			return 0
				
		if r[0] == comm.mgr.KILL_SIGNAL:
			self.socket.send_multipart(self.encode(comm.mgr.KILL_SIGNAL,"recv quit signal from client"))
			log.warning(addr + ": recv quit signal from client")
			comm.mgr._close(False)
			return -1			
				
		try:
			result,ret = self.handle(r[0],r[1])
		except Exception as e: 
			self.socket.send_multipart(self.encode(-3,"handle exception cmd %s "%r[0]+ str(e)))
			log.exception(self.addr + ": handle exception cmd %s "%r[0],e)
			return 0		
			
		try:
			s = self.encode(0,ret)
		except Exception as e:
			self.socket.send_multipart(self.encode(-4,"encode handle exception cmd %s "%r[0]))
			log.exception(addr + ": encode handle exception cmd %s "%r[0],e)
			return 0
				
		self.socket.send_multipart(s)
		#log.debug(addr + ": send: {0},{1}".format(*s))
		return 0
		
			
	#可以重载 		
	def handle(self,typeid,param):
		if typeid not in self.handler:
			self.socket.send_multipart(self.encode(-2,"can't handle the cmd %s"%typeid))
			log.warning(self.addr + ": can't handle the cmd %s"%str(typeid))
			return False,None
		ret = self.handler[typeid](typeid,param)
		return True,ret
		
			
	def register(self,typeid,func):
		self.handler[typeid] = func


#实现命令处理函数的修饰符
def register(cmd,msg_type):
	def __call(func):
		cmd.register(msg_type,func)
		return func
	return __call		


################# unit test #####################
def _run_server():
	s = cmd_server()
	
	import logging
	log.set_level(logging.INFO)
	
	def handle1(typeid,msg):
		return msg*10
	
	@register(s,1002)
	def handle2(typeid,msg):
		return msg

	@register(s,1003)
	def handle3(typeid,msg):
		raise Exception("test exception")
		return msg

	s.register("a1001",handle1)
	s.start(10001)
	comm.mgr._start()
	comm.mgr.wait()

	
def _run_client(ip,port):
	import logging
	log.set_level(logging.INFO)
	
	r = cmd_client()
	r.connect(ip,port)
	
	rc = r.send("a1001","hello world")
	assert rc == "hello world"*10
	
	#test big data 
	for i in range(100):
		assert r.send(1002,"h"*4096) == "h"*4096
	assert r.send(1002,"h"*40960) == "h"*40960
	
	#test wrong type
	try:
		r.send(9002,"h")
	except Exception as e:
		assert str(e).find("can't handle the cmd 9002") != -1
	
	#test server assert
	try:
		r.send(1003,"h")
	except Exception as e:
		assert str(e).find("test exception") != -1
	
	r.send_quit()
	
	#test timeout
	r = cmd_client()
	r.connect("127.0.0.1",10002)
	try:
		r.send(1001,"hello world")
	except Exception as e:
		assert str(e).find("timeout") != -1	

def test_run():
	#test get name
	def get_name(addr):
		print("get name")
		if addr == "lala":
			return "tcp://127.0.0.1:10001"
		return "xxx"
	
	comm.mgr.set_names(get_name)
	
	#test use name
	p2 = threading.Thread(target=_run_client, args=("lala",0))
	p2.start()
	time.sleep(2)
	
	_run_server()
	
	#test use ip 
	
	p2 = threading.Thread(target=_run_client, args=("127.0.0.1",10001))
	p2.start()
	time.sleep(2)
	
	_run_server()
	#p = Process(target=_run_server, args=())
	#p.start()
	#p.join()
	p2.join()

	#test close server
	s = cmd_server()
	s.start(20401)
	utility.start()
	time.sleep(1)
	utility.finish()
	print("test finish!")
	
	
if __name__ == '__main__':
	#utility.run_tests()
	test_run()
			
