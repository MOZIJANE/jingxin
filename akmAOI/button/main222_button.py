import sys, os
import bottle
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import log
import utility
import webutility
import threading
import socket

class button:
	def __init__(self,maxClient=100):
		self.addr = self.get_host_ip()
		self.port = 1001
		self.maxClient = maxClient
		self.threadread = threading.Thread(target=self.received)
		self.threadread.start()
	
	def received(self):
		try:
			tcp_server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			#本地信息
			address = (self.addr,self.port)
			tcp_server_socket.bind(address)
			tcp_server_socket.listen(self.maxClient)#最大连接数
			client_socket,client_addr = tcp_server_socket.accept()
		except Exception as e:
			print(e)
		
		while True:
			try:
				recv_data = client_socket.recv(5)
				self.parseData(recv_data)
			except socket.timeout:
				print("timeout")

	def get_host_ip(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		try:
			s.connect(('8.8.8.8', 80))
			ip = s.getsockname()[0]
		finally:
			s.close()		
		return ip

	def parseData(self,data):
		assert len(data) is 5
		devID = data[2];
		keyID = data[3];
		print("devID:",devID,"keyID:",keyID)
		####todo#########

button()