#coding=utf-8
# ycat			2018-12-10	  create
# TCP的服务端封装  
import socket
import time 
import threading
import setup 
if __name__ == '__main__':
	setup.setCurPath(__file__) 
import log
import tcpSocketAdvanced as tcpSocket


def read(socket): 
	data = bytes()
	data_body=bytes() 
	partlen=0
	while True:
		part_body = socket.recv(1024)
		data_body += part_body
		cutlen = len(part_body)
		partlen += cutlen
		time.sleep(0.5)
		if cutlen < 1024:
			break
	#对端关闭会返回0 len(data) == 0 
	return data_body
	
	
def send(socket,data):
	assert len(data)
	if isinstance(data,str):
		data = data.encode("utf-8") 
	return socket.send(data)
		
def checkPort(ip,port):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
		if not ip:
			ip = "0.0.0.0"
		s.bind((ip,port))
		return True
	except OSError as e:
		return False
	finally:
		s.close()
		
class server:
	def __init__(self,acceptCallback=None):
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
		self._isExist = False
		self.acceptCallback = acceptCallback
		self._listenThread = None
		
	def start(self,serverIP, port):
		self._addr = (serverIP, port)
		self._socket.bind(self._addr)
		self._socket.listen()
		self._listenThread = threading.Thread(target=self._acceptThread)
		self._listenThread.start()
		
		
	def close(self):
		self._isExist = True
		self._socket.close()
		if self._listenThread:
			self._listenThread.join() 

	def _acceptThread(self):
		while not self._isExist:
			try:
				client,addr = self._socket.accept()
			except Exception as e:
				if self._isExist:
					return
				else:
					raise
			log.info("Tcp client connected",str(addr))
			client.settimeout(1) #5 seconds 
			client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
			if self.acceptCallback:
				self.acceptCallback(client)
		
	 
		 
################## unit test ##################  
def test_server(): 
	import utility
	import threading
	assert checkPort(9001)
	s = server()
	s.start("0.0.0.0",9001)
	assert not checkPort(9001)
	assert not checkPort(9001)
	s.close()
	assert checkPort(9001)
	
	def acceptCB(client):
		send(client,"hello ycat")
		time.sleep(1)
		client.close()
		
	s = server(acceptCB)
	s.start("0.0.0.0",19001)
	time.sleep(2)
	with tcpSocket.client("127.0.0.1",19001) as c:
		data = read(c._socket)
		assert "hello ycat" == data.decode("utf-8") 
	time.sleep(2)
	s.close()
		  
 
if __name__ == '__main__':  
	test_server()
	import utility
	utility.run_tests()

