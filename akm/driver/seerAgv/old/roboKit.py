import socket
import time
import threading
import json
import struct
import driver.seerAgv.roboModel as roboModel
import setup

if __name__ == '__main__':
	setup.setCurPath(__file__)
import config

# g_addr = config.get("agv","servers")


basedata = roboModel.baseResultData(0, "success").getdict()

demoDict = dict()
demoDict['11000'] = dict(basedata, **roboModel.t1000)
demoDict['11002'] = dict(basedata, **roboModel.t1002)
demoDict['11003'] = dict(basedata, **roboModel.t1003)
demoDict['11004'] = dict(basedata, **roboModel.t1004)
demoDict['11005'] = dict(basedata, **roboModel.t1005)
demoDict['11006'] = dict(basedata, **roboModel.t1006)
demoDict['12000'] = dict(basedata)
demoDict['12002'] = dict(basedata)
demoDict['12003'] = dict(basedata)
demoDict['12001'] = dict(basedata)
demoDict['13051'] = dict(basedata)
demoDict['13052'] = dict(basedata)
demoDict['13058'] = dict(basedata)
demoDict['13059'] = dict(basedata)
demoDict['13060'] = dict(basedata)
demoDict['13057'] = dict(basedata)
demoDict['11100'] = dict(basedata, **roboModel.t1100)

def action(index, bodyResult):
	print('using function type is:%s' % index)
	print('deling with params of:%s' % bodyResult)


class robotServer:
	def __init__(self, IP, port):
		self.address = IP
		self.port = port
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	def dataHandler(self, client,addr, getSendData):
		try:
			while True:
				client.settimeout(10)
				recvData = client.recv(1024)
				# print("recvData: ", recvData)
				if len(recvData) < 16:
					return
				headerRaw = recvData[0:16]
				bodyResult = recvData[16:]
				header = None
				headerResult = struct.unpack('>BBHIHIH', headerRaw)
				
				index = 0
				data = None
				if len(headerResult) >= 6:
					m_sync = headerResult[0]
					m_version = headerResult[1]
					m_number = headerResult[2]
					m_length = headerResult[3]
					m_type = headerResult[4]
					m_reserved = headerResult[5]
					m_reserved2 = headerResult[6]
					header = roboModel.protocolHeader(m_sync, m_version, m_number, m_length, m_type, m_reserved,
					                                  m_reserved2)
					
					index = "1" + m_type.__str__()
					
					# data = demoDict[index]
					data = getSendData(index, bodyResult)

					action(index, bodyResult)

				if data is not None:
					jsonData = json.dumps(data)
					jsonLen = len(jsonData)
					bodyData = jsonData.encode("GBK")
					header.m_length = jsonLen
					header.m_type = int(index)
					headerData = header.getsturct()
					result = headerData + bodyData
					client.send(result)
					print('data has been sent')
				
				else:
					print('no data has been sent')
		except socket.timeout:
			print("socket time out")
			client.close()
		except socket.error:
			print("socket error")
			client.close()
		except Exception as exc:
			print("other error occur ", exc)
			client.close()
	
	def start(self,getSendData):
		
		self.sock.bind((self.address, self.port))
		self.sock.listen(50)
		while True:
			client, address = self.sock.accept()
			thread = threading.Thread(target=self.dataHandler, args=(client, address, getSendData))
			thread.start()
			print('server started!')
	
	def end(self):
		self.sock.close()
		print('server ended!')


class robotClient:
	def __init__(self, server=None, port=None):
		self.tcpClientSocket = None
		self.serverAddr = (server, port)
	
	def __enter__(self):
		self.__connect(self.serverAddr)
		return self
	
	def __exit__(self, exc_type, exc_val, exc_tb):
		self.disconnect()
	
	def __connect(self, serverAddr):
		while True:
			try:
				if serverAddr is None:
					return
				self.tcpClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				print('socket---%s' % self.tcpClientSocket)
				# 链接服务器
				self.tcpClientSocket.connect(serverAddr)
				print('connect success!')
				return
			except socket.error:
				print(serverAddr,"socket error,do reconnect ")
				time.sleep(3)
				self.__connect(self.serverAddr)
	
	def connect(self, server, port):
		self.serverAddr = (server, port)
		self.__connect(self.serverAddr)
	
	def send(self, sendData):
		while True:
			try:
				if len(sendData) > 0:
					self.tcpClientSocket.send(sendData)
				else:
					return
				# 接收数据
				self.tcpClientSocket.settimeout(10)
				data_body = bytes()
				partlen = 0
				while True:
					part_body = self.tcpClientSocket.recv(1024)
					data_body += part_body
					cutlen = len(part_body)
					partlen += cutlen
					# 要加个sleep否则数据会出错，不知道为什么╮(╯▽╰)╭
					time.sleep(0.2)
					if cutlen < 1024:
						break
				recvData = data_body
				totallen = len(recvData)
				
				headerData = recvData[0:16]
				headerResult = struct.unpack('>BBHIHIH', headerData)
				reflen = headerResult[3]
				bodyData = recvData[16:]
				if len(bodyData) == reflen:
					print("package lenth verifing: ", totallen, partlen, reflen)
				else:
					raise Exception("数据长度验证未通过")
				return bodyData
			
			except socket.timeout:
				print("socket time out,do reconnect ")
				# self.tcpClientSocket.close()
				# self.__connect(self.serverAddr)
				return -1
			
			except socket.error as err:
				print("socket error,do reconnect ")
				time.sleep(3)
				print(err)
				self.__connect(self.serverAddr)
				return -2
			
			except Exception as exc:
				print("other error occur ", exc)
				time.sleep(3)
				return -3
	
	def disconnect(self):
		# 关闭套接字
		self.tcpClientSocket.close()
		print('close socket!')


def test_protocolHeader():
	t1 = {"x": 10.0, "y": 3.0, "angle": 0}
	dataLen = len(t1)
	m_version = 1
	m_number = 0
	m_sync = 90
	m_type = 1000
	m_reserved = 0
	m_reserved2 = 0
	bodyData = json.dumps(t1).encode("GBK")
	dataLen = int(dataLen)
	sendObj = roboModel.protocolHeader(m_sync, m_version, m_number, dataLen, m_type, m_reserved, m_reserved2)
	result = sendObj.getsturct()
	assert result
	unpacked = struct.unpack('>BBHIHIH', result)
	assert m_sync == unpacked[0]
	assert m_version == unpacked[1]
	assert m_number == unpacked[2]
	assert dataLen == unpacked[3]
	assert m_type == unpacked[4]
	assert m_reserved == unpacked[5]
	assert m_reserved2 == unpacked[6]
	assert sendObj


def test_robotserver():
	def getSendDataState(index, bodyResult):
		data = demoDict['11100']
		return data
	global g_addr
	server = robotServer(g_addr, 19205)
	server.start(getSendDataState)


def test_robotclient():
	global g_addr
	client1 = robotClient()
	client1.connect(g_addr, 19205)
	
	data = {"x": 10.0, "y": 3.0, "angle": 0}  # 发送数据
	sendData = json.dumps(data).encode()
	client1.send(sendData)
	client1.disconnect()


if __name__ == '__main__':
	thread1 = threading.Thread(target=test_robotserver)
	thread1.start()
	test_protocolHeader()
# while(True):
#
# 	thread2 = threading.Thread(target=test_robotclient)
# 	thread2.start()
#
# 	time.sleep(3)
