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

#可以单向发送数据，但不能收
#可以支持server重启，但不支持两个server之间相互备份，多个server会产生负荷分担的效果 
class push_client:
	def __init__(self):
		self.socket = comm.mgr.create_socket(zmq.PUSH)
		self.addr = ""
		
	def connect(self,ip,port):
		if port == 0:
			addr  = comm.mgr.get_names(ip)
		else:
			addr = "tcp://" + ip + ":" + str(port)
			
		self.socket.connect(addr)
		if self.addr == "":
			self.addr += addr
		else:
			self.addr += "," + addr
	
	def send(self,typeid,obj):
		self.socket.send_multipart(comm.mgr._encode(typeid,obj))
		if typeid == comm.mgr.KILL_SIGNAL:
			log.debug(self.addr + ": send: KILL_SIGNAL")
		else:	
			log.debug(self.addr + ": send: {}, {}".format(typeid,obj))
	
	def close(self):
		self.socket.close()
		

#可以单向接收数据，但不能发送 
class push_server:
	def __init__(self):
		self.socket = comm.mgr.create_socket(zmq.PULL)
		self.addr = ""
		self.func = None
		
	#func格式为 def func(typeid,obj):	
	def start(self,port,func):
		self.func = func
		self.addr = "tcp://*:"+str(port)
		self.socket.bind(self.addr)
		comm.mgr.register(self.socket,self._read_handle)
	
	def _read_handle(self):
		assert self.func
		msg = self.socket.recv_multipart()
		log.debug(self.addr + ": recv: {0},{1}".format(*msg))
		m = comm.mgr._decode(*msg)
		
		if m[0] == comm.mgr.KILL_SIGNAL:
			log.warning(self.addr + ": recv quit signal from client")
			comm.mgr._close(False)
			return -1
		
		self.func(m[0],m[1])

	def close(self):
		comm.mgr.close_socket(self.socket)
		log.warning(self.addr + ": close")

################# unit test ###################
#def test_run2():
#	utility.start()
#	c = push_client()
#	c.connect("127.0.0.1",20201)
#	
#	c2 = push_client()
#	c2.connect("127.0.0.1",20201)
#
#	results = []
#	results2 = []
#	def func(typeid,obj):
#		results.append((typeid,obj))
#		
#	def func2(typeid,obj):
#		results2.append((typeid,obj))	
#		
#	s = push_server()
#	s.start(20201,func)
#	
#	#s2 = push_server()
#	#s2.start(20202,func2)
#	time.sleep(1)
#	
#	for i in range(100):
#		c.send(1001,"lalalala_%d"%i)
#		c2.send(1002,"lalalala_%d"%i)
#		if i == 10:
#			time.sleep(1)
#			s.close()
#		
#		if i == 40:
#			s = push_server()
#			s.start(20202,func2)
#			time.sleep(2)
#			
#	time.sleep(2)
#	print(len(results), len(results2))
#	assert (len(results) + len(results2)) == 200
#
#	utility.finish()
#	print("test2 finish")
#	
#def test_run():
#	utility.start()
#	c = push_client()
#	c.connect("127.0.0.1",20201)
#	
#	c2 = push_client()
#	c2.connect("127.0.0.1",20201)
#	results = []
#	def func(typeid,obj):
#		results.append((typeid,obj))
#		
#	s = push_server()
#	s.start(20201,func)
#	
#	c.send(1001,"lalalala")
#	time.sleep(1)
#	assert 1 == len(results)
#	assert results[0][0] == 1001
#	assert results[0][1] == "lalalala"
#
#	utility.finish()
#	print("test finish")
	 
if __name__ == '__main__':
	pass
	#test_run2()
	#test_run()	
	
			
