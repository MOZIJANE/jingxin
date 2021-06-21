#coding=utf-8
# ycat			2018-8-2	  create
# TCP封装  
import socket
import time 
import setup 
if __name__ == '__main__':
	setup.setCurPath(__file__) 
		
class client:
	def __init__(self, serverIP, port, timeout=5):
		self._socket = None
		self._addr = (serverIP, port)
		self._timeout = timeout

	def __enter__(self):
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
		self._socket.connect(self._addr) 
		self._socket.settimeout(self._timeout) #5 seconds
		self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
		return self
	
	def __exit__(self, exc_type, exc_val, exc_tb):
		self._socket.close() 
		self._socket = None
	
	def send(self, sendData): 
		assert len(sendData)
		if isinstance(sendData,str):
			sendData = sendData.encode("utf-8") 
		self._socket.send(sendData)
		

	def recv(self,recvLen=1024):
		data = bytes()
		data_body=bytes()
		partlen=0
		while True:
			part_body = self._socket.recv(recvLen)
			data_body += part_body
			cutlen = len(part_body)
			partlen += cutlen
			#time.sleep(1)
			if cutlen < recvLen:
				break
			time.sleep(0.1)
		#对端关闭会返回0 len(data) == 0
		return data_body
		 
################## unit test ##################  
def test_robotclient(): 
	import utility
	import threading
	def runFunc(server):
		c, address = server.accept() 
		for i in range(10):
			data = c.recv(4000)
			assert len(data) == 4000
			c.send(data)
		time.sleep(8)
		
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
	server.bind(("127.0.0.1", 19205))
	server.listen(19205)
	t = threading.Thread(target=runFunc, args=(server,))
	t.start()
	time.sleep(2)
		 
	with client("127.0.0.1",19205) as c:
		for i in range(5):
			c.send("0"*4000)
			c.recv()  
		tick = utility.ticks() 
		try:
			data = c.recv() 
			assert 0
		except socket.timeout:
			pass
		assert utility.ticks() - tick >= 4800
	server.close()
	t.join() 
 
if __name__ == '__main__': 
	import utility
	utility.run_tests()

