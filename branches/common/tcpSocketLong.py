# coding=utf-8
# ycat			2018-8-2	  create
# TCP封装
import socket
import time
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__) 
import log
import utility

socket.setdefaulttimeout(10)

class client:
	def __init__(self,name, serverIP, port,timeout):
		self._addr = (serverIP, port)
		self.serverIP = serverIP
		self.port = port
		self.isConnected = False
		self.timeout = timeout
		self.doConnect(name)

	def doConnect(self,name):
		try:
			log.debug('try connect %s %s:%d'%(name,self.serverIP,self.port))
			self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self._socket.connect(self._addr)
			timeout = self.timeout
			self._socket.settimeout(timeout)   
			self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
			if utility.is_win():
				self._socket.setsockopt(socket.SOL_SOCKET,socket.SO_SNDTIMEO,timeout)
				self._socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVTIMEO,timeout)
				self._socket.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 1500, 250))
		#	
		#	if utility.is_win():
		#		
		#		# self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 10)
		#
		#	else:
		#		def set_keepalive(sock, after_idle_sec=1.0, interval_sec=3.0, max_fails=5.0):
		#			sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
		#			sock.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 1500, 250))
		#			sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, after_idle_sec)
		#			sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec)
		#			sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails)
		#		set_keepalive(self._socket,1.5,0.25,10)
			self.isConnected = True
			log.info(name,"connected",self.serverIP,self.port)
			return True
		except Exception as es:
			log.error('connect',name,'failed',es.__str__())
			if self._socket is not None:
				self._socket.close()
			self._socket = None 
			return False
	
	def close(self,name):
		try:
			self.isConnected = False
			if self._socket:
				self._socket.close()
			self._socket = None 
		except Exception as es:
			log.error('close failed',name,es.__str__())
			
	def doDisconnect(self,name):
		self.isConnected = False
		log.warning('disconnect',name,self.serverIP,self.port)
		self.close(name)
			

	def send(self, sendData):
		assert self.isConnected
		assert len(sendData)
		if isinstance(sendData, str):
			sendData = sendData.encode("utf-8")
		self._socket.send(sendData)
	
	def recv(self, dataLen):
		assert self.isConnected
		data_body = bytes()
		bufferLen = 4096
		
		while len(data_body) < dataLen:
			remainLen = dataLen - len(data_body)
			if remainLen > bufferLen:
				recvdata = self._socket.recv(bufferLen)
			else:
				recvdata = self._socket.recv(remainLen)
			if recvdata == b'':
				raise Exception("%s: %s tcp recv closed"%(self.serverIP,self.port))
			else:
				data_body += recvdata
		return data_body


	def clear(self):
		if utility.is_win():
			return
		import fcntl,termios,struct
		try:
			data = fcntl.ioctl(self._socket.fileno(),termios.FIONREAD,"\0\0\0\0")
			c = struct.unpack("i",data)[0]
			if c == 0:
				return
			log.warning(self.port,",tcp clear data",c)
			self.recv(c)
		except Exception as e:
			log.exception("tcp clear",e)


g_clients = {}

def _getKey(ip,port):
	return ip+":"+str(port)

def _getClient(name, ip, port, timeout=10):
	global g_clients
	k = _getKey(ip,port)
	if k not in g_clients:
		c = client(name=name,serverIP=ip, port=port, timeout=timeout)
		g_clients[k] = c
	c = g_clients[k]
	if not c.isConnected:
		if not c.doConnect(name):
			return None
	return c


def send(name,ip, port, sendData, timeout=10):
	c = _getClient(name, ip, port, timeout=timeout)
	if c is None:
		e = IOError("send failed,"+name+" is unconnected, port="+str(port))
		e.noprint = True
		raise e
	if c._socket is None:
		e = IOError("send failed2,"+name+" is unconnected, port="+str(port))
		e.noprint = True
		raise e
	try:
		c.send(sendData)
	except socket.timeout as e:
		raise e
	except Exception as e:
		c.doDisconnect(name)
		raise e


def recv(name,ip, port, len, timeout=10):
	c = _getClient(name, ip, port, timeout=timeout)
	if c is None:
		e = IOError("recv failed,"+name+" is unconnected")
		e.noprint = True
		raise e
	if c._socket is None:
		e = IOError("recv2 failed,"+name+" is unconnected")
		e.noprint = True
		raise e
	try:
		return c.recv(len)
	except socket.timeout as e:
		raise e
	except Exception as e:
		c.doDisconnect(name)
		raise e

def close(name,ip, port): 
	global g_clients
	k = _getKey(ip,port)
	if k not in g_clients:
		return
	c = g_clients[k]
	if c.isConnected:
		c.close(name)
	del g_clients[k]


################## unit test ##################
def testkeep():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1.3)
	s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1.5)
	s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3.6)
	s.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5.6)

def test_robotclient():
	import utility
	import threading
	def runFunc(server):
		client, address = server.accept()
		for i in range(10):
			data = client.recv(4096)
			assert len(data) == 4000
			client.send(data)
		time.sleep(20)

	ip = "127.0.0.1"
	port = 19205

	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind((ip, port))
	server.listen(19205)
	t = threading.Thread(target=runFunc, args=(server,))
	t.start()
	time.sleep(1)

	for i in range(10):
		send("test",ip, port, "0" * 4000,timeout=5)
		data = recv("test",ip, port,4000)
		assert b'0' * 4000 == data
	tick = utility.ticks()
	try:
		data = recv("test",ip, port,10)
		print(data)
	except socket.timeout:
		print('超时测试异常')
	close("test",ip, port)
	assert utility.ticks() - tick >= 4800
	server.close()
	t.join()


if __name__ == '__main__':	
	testkeep()
	# import utility
	#
	# utility.run_tests(__file__)

	test_robotclient()
