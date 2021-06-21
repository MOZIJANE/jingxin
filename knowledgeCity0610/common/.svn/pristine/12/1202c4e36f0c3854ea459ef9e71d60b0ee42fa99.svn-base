#coding=utf-8 
# ycat			 2015/05/27      create
import os,time,sys
import zmq
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import log	
import utility
import comm.mgr
from multiprocessing import Process

#可以单向接收数据，但不能发送 
class pull_client:
	def __init__(self):
		self.socket = comm.mgr.create_socket(zmq.PULL)
		self.addr = ""
		self.func = None
	
	#func格式为 def func(typeid,obj):		
	def connect(self,ip,port,func):
		self.func = func
		self.addr = "tcp://" + ip + ":" + str(port)
		self.socket.connect(self.addr)
		comm.mgr.register(self.socket,self._read_handle)

	def _read_handle(self):
		assert self.func
		msg = self.socket.recv_multipart()
		m = comm.mgr._decode(*msg)
		
		if m[0] == comm.mgr.KILL_SIGNAL:
			log.warning(self.addr + ": recv quit signal from client")
			comm.mgr._close(False)
			return -1
		
		self.func(m[0],m[1])
		
	def close(self):
		self.socket.close()		
		log.debug(self.addr + ": close")
		

#可以单向发送数据，但不能接收 
class pull_server:
	def __init__(self):
		self.socket = comm.mgr.create_socket(zmq.PUSH)
		self.addr = ""
		
	#func格式为 def func(typeid,obj):	
	def start(self,port):
		self.addr = "tcp://*:"+str(port)
		self.socket.bind(self.addr)
	
	def send(self,typeid,obj):
		self.socket.send_multipart(comm.mgr._encode(typeid,obj))

	def close(self):
		comm.mgr.close_socket(self.socket)
		log.warning(self.addr + ": close")

################# unit test ###################
def test_run():
	results = []
	def func(typeid,obj):
		results.append((typeid,obj))
		
	results2 = []
	def func2(typeid,obj):
		results2.append((typeid,obj))	
		
	utility.start()
	c = pull_client()
	c.connect("127.0.0.1",21001,func)
	
	c2 = pull_client()
	c2.connect("127.0.0.1",21001,func2)
		
	s = pull_server()
	s.start(21001)
	
	s.send(1001,"lalalala")
	time.sleep(1)
	assert (1 == len(results)) or (1 == len(results2))
	if 1 == len(results):
		assert results[0][0] == 1001
		assert results[0][1] == "lalalala"
	else:
		assert results2[0][0] == 1001
		assert results2[0][1] == "lalalala"

	utility.finish()
	s.close()
	c.close()
	print("test finish")
	 
if __name__ == '__main__':
	test_run()		
			
