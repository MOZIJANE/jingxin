import socket
import time
import struct
import threading

import setup
if __name__ == '__main__':
	setup.setCurPath(__file__) 
	
import log
import utility

# socket.setdefaulttimeout(10)

# connectLen=-1 不限制连接数
class server:
	def __init__(self,serverIP, port,connectLen=-1,acceptCallback=None):
		self.serverIP = serverIP
		self.port = port
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		if utility.is_win():
				self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
				self._socket.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 1500, 250))
				# self._socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 10)
		else:
			def set_keepalive(sock, after_idle_sec=5, interval_sec=3.0, max_fails=5.0):
				sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
				sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, after_idle_sec)
				sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec)
				sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails)
			set_keepalive(self._socket,5,5,5)
		self._addr = (serverIP, port)
		self._socket.bind(self._addr)
		self._isExist = False
		self._connectLen = connectLen
		self._connectedLen = 0
		self.acceptCallback = acceptCallback
		
	def start(self):
		self._isExist = False
		self._socket.listen()
		self._listenThread = threading.Thread(target=self._acceptThread,name="tcplisten.port_"+str(self.port))
		self._listenThread.start()
		
	def close(self):
		self._isExist = True
		self._socket.close()
		self._listenThread.join() 
		self._listenThread = None
		
	@property
	def desc(self):
		return "tcp server [%s][%s] ,connectedLen: %s,"%(self.serverIP,self.port,self._connectedLen)
		
	def closeClient(self,clientsocket):
		log.info(self.desc,"disconnect: ",clientsocket.desc)
		clientsocket.doDisconnect()
		self._connectedLen = self._connectedLen - 1

	def _acceptThread(self):
		while not self._isExist:
			if self._connectLen == -1 or self._connectedLen < self._connectLen:
				try:
					sock,addr = self._socket.accept()
				except Exception as e:
					if self._isExist:
						return
					else:
						continue
				self._connectedLen = self._connectedLen + 1
				ci = client(self.serverIP,self.port,sock=sock)
				log.info(self.desc,"tcp connected",ci.desc)
				if self.acceptCallback:
					try:
						self.acceptCallback(self,ci)
					except Exception as e:
						log.exception(self.desc+" acceptCallback error:",e)

class client:
	def __init__(self, serverIP, port,localIP=None,localPort=0,sock=None):
		self._addr = (serverIP, port)
		self._local = (localIP,localPort)
		self.serverIP = serverIP
		self.port = port
		self.peerIP    = serverIP
		self.peerPort  = port
		self.localIP   = localIP
		self.localPort = localPort
		self.isConnected = False
		self.canConnected = False #指定sock的不可以重连
		if sock != None:
			self._socket = sock
			self.isConnected = True
		else:
			self.canConnected = True
			self.doConnect()
		self.setSocket()
		
	@property
	def desc(self):
		ll = ''
		if self.localIP:
			ll = str(self.localIP)
			if self.localPort != 0:
				ll = ll +':'+str(self.localPort)
			ll = ll +' <--> '
		return ll+str(self.peerIP)+':'+str(self.peerPort)
	
	def setSocket(self):
		if self.isConnected:
			if utility.is_win():
				self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
				self._socket.ioctl(socket.SIO_KEEPALIVE_VALS, (1, 1500, 250))
			else:
				def set_keepalive(sock, after_idle_sec=5, interval_sec=3.0, max_fails=5.0):
					sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
					sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, after_idle_sec)
					sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec)
					sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails)
				set_keepalive(self._socket,5,5,5)
			timeout = 10
			self._socket.settimeout(timeout)   
			self._socket.setsockopt(socket.SOL_SOCKET,socket.SO_SNDTIMEO,struct.pack('LL', timeout, 0))
			self._socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVTIMEO,struct.pack('LL', timeout, 0))
			self.localIP,self.localPort = self._socket.getsockname()
			self.peerIP,self.peerPort = self._socket.getpeername()
			
	def doConnect(self):
		try:
			if not self.canConnected:
				raise Exception("socket can't be connected")
			self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			if self._local[0] is not None:
				self._socket.bind(self._local)
			self._socket.connect(self._addr)
			self.isConnected = True
			self.setSocket()
			log.info(self.desc,"connected")
			return True
		except Exception as es:
			log.error('connect',self.desc,'failed',es.__str__())
			if self._socket is not None:
				self._socket.close()
			self._socket = None 
			return False
			
	def doDisconnect(self):
		try:
			log.warning('disconnect',self.desc)
			self.isConnected = False
			if self._socket is not None:
				self._socket.close()
			self._socket = None 
		except Exception as es:
			log.error('disconnection failed',self.desc,es.__str__())
			

	def send(self, sendData):
		assert self.isConnected
		assert len(sendData)
		if isinstance(sendData, str):
			sendData = sendData.encode("utf-8")
		# self._socket.sendall(sendData)
		dataLen = len(sendData)
		sendLen = 0
		while sendLen != dataLen:
			sendLen = sendLen + self._socket.send(sendData[sendLen:])
	
	def recv(self, dataLen):
		assert self.isConnected
		data_body = bytes()
		bufferLen = 4096
		
		while len(data_body) < dataLen:
			remainLen = dataLen - len(data_body)
			recvdata = self._socket.recv(bufferLen if remainLen > bufferLen else remainLen)
			if recvdata == b'':
				raise Exception(self.desc+" tcp recv closed")
			else:
				data_body += recvdata
		return data_body


g_clients = {}

def getKey(ip,port,localIP=None,localPort=0):
	ss = ip+":"+str(port)
	ll = ''
	if localIP:
		ll = localIP
		if localPort != 0:
			ll = ll +":"+str(localPort)
		ll = ll + " --> "
	return ll + ss

def decodeKey(key):
	key = key.replace(" ",'')
	ss = key.split("-->")
	ll = None
	if len(ss) > 1:
		ll,ss = ss
	else:
		ss = ss[0]
	ip,port = ss.split(":")
	localIP = ll
	localPort = 0
	if ll:
		ll = ll.split(":")
		if len(ll)>1:
			localIP,localPort = ll
	return ip,int(port),localIP,int(localPort)
	
def _getClient(key):
	global g_clients
	if key not in g_clients:
		ip,port,localIP,localPort = decodeKey(key)
		c = client(serverIP=ip, port=port,localIP=localIP,localPort=localPort)
		g_clients[key] = c
	c = g_clients[key]
	if not c.isConnected:
		if not c.doConnect():
			return None
	return c

def send(key, sendData):
	c = _getClient(key)
	if c is None:
		e = Exception("send failed,"+key+" is unconnected")
		e.noprint = True
		raise e
	try:
		c.send(sendData)
	except socket.timeout as e:
		raise e
	except Exception as e:
		c.doDisconnect()
		raise e


def recv(key, length):
	c = _getClient(key)
	if c is None:
		e = Exception("recv failed,"+key+" is unconnected")
		e.noprint = True
		raise e
	try:
		return c.recv(length)
	except socket.timeout as e:
		raise e
	except Exception as e:
		c.doDisconnect()
		raise e

def close(key): 
	global g_clients
	if key not in g_clients:
		return
	c = g_clients[key]
	if c.isConnected:
		c.doDisconnect()
	del g_clients[key]

################## unit test ##################
def test_robotclient():
	import utility
	import threading
	def runFunc(server):
		client, address = server.accept()
		for i in range(10):
			dataLen = 4000
			data_body = bytes()
			bufferLen = 4096
			while len(data_body) < dataLen:
				remainLen = dataLen - len(data_body)
				if remainLen > bufferLen:
					data_body += client.recv(bufferLen)
				else:
					data_body += client.recv(remainLen)
			assert len(data_body) == 4000
			assert data_body.decode("utf-8") == '0'*4000
			client.send(data_body)
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
		send("agv1",ip, port, "0" * 4000)
		data = recv("agv1",ip, port,4000)
		assert data.decode("utf-8") == "0" * 4000
	tick = utility.ticks()
	while True:
		try:
			data = recv("agv1",ip, port,5)
		except socket.timeout:
			assert True
			break
		assert False
	assert utility.ticks() - tick >= 4800
	server.close()
	t.join()
	
def test_server():
	ip = "127.0.0.1"
	port = 19205
	ci = []
	def callback(ser,client):
		ci.append(client)
		client.send("client")
		time.sleep(2)
		data = client.recv(9)
		assert data.decode("utf-8") == '0'*9
	ser = server(ip,port,connectLen=10,acceptCallback=callback)
	ser.start()
	for i in range(10):
		c = client(i,ip,port)
		time.sleep(2)
		data = c.recv(6)
		assert data.decode("utf-8") == "client"
		c.send('0'*9)
	c = None
	while True:
		try:
			c = client('ff',ip,port)
			time.sleep(2)
			data = c.recv(6)
			assert data.decode("utf-8") == "client"
			c.send('0'*9)
		except socket.timeout:
			# c.doDisconnect("ff")
			break
		assert False
	ser.closeClient(ci[0])
	while True:
		try:
			time.sleep(1)
			data = c.recv(6)
			assert data.decode("utf-8") == "client"
			c.send('0'*9)
		except socket.timeout:
			assert False
		break
	ser.close()
	
	port = 19202
	ci = []
	def callback(ser,client):
		ci.append(client)
		client.send("client"*10240)
		time.sleep(2)
		data = client.recv(6*10240)
		assert data.decode("utf-8") == "client"*10240
	ser = server(ip,port,connectLen=10,acceptCallback=callback)
	ser.start()
	c = client('hh',ip,port)
	time.sleep(2)
	data = c.recv(6*10240)
	assert data.decode("utf-8") == "client"*10240
	c.send(data)
	ser.close()

def test_key():
	key = getKey("192.100",900)
	ip,port,localIP,localPort = decodeKey(key)
	assert ip == "192.100"
	assert port == 900
	assert localIP is None
	assert localPort == 0
	
	key = getKey("192.14400",9003,"192.1999")
	ip,port,localIP,localPort = decodeKey(key)
	assert ip == "192.14400"
	assert port == 9003
	assert localIP == "192.1999"
	assert localPort == 0
	
	key = getKey("192.120",9200,"192.13999",99)
	ip,port,localIP,localPort = decodeKey(key)
	assert ip == "192.120"
	assert port == 9200
	assert localIP == "192.13999"
	assert localPort == 99

if __name__ == '__main__':
	# import utility
	# if utility.is_test():
		# utility.run_tests()
	test_key()
