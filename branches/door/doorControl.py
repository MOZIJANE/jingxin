import os
import sys
import time
import socket
import threading

import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)

import log
import lock as lockImp
import buffer
import tcpSocket
import utility

ip = "0.0.0.0"
port = 6789
MAX_DOOR = 2

g_lock = lockImp.create("doorMgr.lock")

class doorMgr:
	def __init__(self,ip,port,connectLen=MAX_DOOR):
		self.doors = {}
		self.ser = tcpSocket.server(ip,port,connectLen,acceptCallback=self.add)
		self.ser.start()
		
	@lockImp.lock(g_lock)
	def add(self,ser,client):
		if client.peerIP in self.doors:
			self.ser.closeClient(self.doors[client.peerIP])
		self.doors[client.peerIP] = client
		
	@lockImp.lock(g_lock)
	def remove(self,ip):
		if ip in self.doors :
			del self.doors[ip]
	
	@lockImp.lock(g_lock)
	def get(self,ip):
		if ip in self.doors :
			return self.doors[ip]
		return None
	
	def send(self,ip,commd):
		for i in range(3):
			client = self.get(ip)
			if client:
				if self._send(client,commd):
					return True
				self.remove(ip)
			time.sleep(0.5)
		return False
		
	def _send(self,client,commd):
		try:
			client.send(commd)
			return True
		except socket.timeout:
			log.exception(client.desc+" time out",client)
		except socket.error:
			log.exception(client.desc+" socket error",client)
		except Exception as e:
			log.exception(client.desc+" error: ",e)
		self.ser.closeClient(client)
		return False
		
g_doorMgr = doorMgr(ip,port)
# open = b'\xA0\x01\x01\xA2'
# close = b'\xA0\x01\x00\xA1'
def open(doorIp):
	g_doorMgr.send(doorIp,b'\xA0\x01\x01\xA2')
	
def close(doorIp):
	g_doorMgr.send(doorIp,b'\xA0\x01\x00\xA1')
	
############################ UNIT TEST ###################
def test():
	def test_1(ip):
		while True:
			open(ip)
			print (ip,"open1")
			time.sleep(1)
			close(ip)
			print (ip,"close1")
			time.sleep(1)
	def test_2(ip):
		while True:
			close(ip)
			print (ip,"close2")
			time.sleep(300)
			open(ip)
			print (ip,"open2")
			time.sleep(2)
	# s1 = threading.Thread(target=test_1,args=("192.168.3.128",))
	# s1.start()
	s2 = threading.Thread(target=test_2,args=("192.168.3.127",))
	s2.start()
	# s3 = threading.Thread(target=test_1,args=("192.168.3.127",))
	# s3.start()
	
if __name__ == "__main__":
	utility.start()
	test()