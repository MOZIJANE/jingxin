# coding=utf-8
# ycat			2018-8-2	  create
# seerAgv的API封装 
import sys, os
import threading
import socket
import time
from queue import Queue
import setup 

if __name__ == '__main__':
	setup.setCurPath(__file__)
import json
import buffer
import log
import utility
import local
import lock as lockImp
import tcpSocket
import tcpSocketLong
# import driver.seerAgv.agvApi as agvApi

API_PORT_STATE = 19204
API_PORT_CTRL = 19205
API_PORT_TASK = 19206
API_PORT_CONFIG = 19207
API_PORT_KERNEL = 19208
API_PORT_OTHER = 19210
API_PORT_PERPHERIAL = 19214

#server： 每个端口链接的ping包类型
g_pingType = {
	API_PORT_STATE:	[1707,"lock_status"],
	API_PORT_CTRL:	[2707,"lock_ctrl"],
	API_PORT_TASK:	[3707,"lock_task"],
	API_PORT_CONFIG:[4707,"lock_conf"],
	API_PORT_KERNEL:[5707,"lock_core"],
	API_PORT_OTHER:	[6707,"lock_other"],
	API_PORT_PERPHERIAL:[7707,"lock_perpherial"]
}

g_server = {}
def startServer():
	ports = [API_PORT_STATE, API_PORT_CTRL, API_PORT_TASK, API_PORT_CONFIG,API_PORT_KERNEL, API_PORT_OTHER,API_PORT_PERPHERIAL]
	for p in ports:
		if not isOpen(p):
			time.sleep(0.5) #isOpen会占用端口
			ser = tcpSocket.server('0.0.0.0',p,connectLen=-1,acceptCallback=_setClient)
			ser.start()
			g_server[p] = ser
	r_thread1 = threading.Thread(target=_checkRegister)
	# r_thread2 = threading.Thread(target=_checkClient)
	r_thread1.start()
	# r_thread2.start()

g_client = Queue()
def _setClient(ser,client):
	g_client.put([ser,client,utility.ticks()])

def getClient(agvId,ip,port):
	key = getKey(agvId,port)
	if key in g_registerAgv:
		_,client,oldTicks = g_registerAgv[key]
		if utility.ticks() - oldTicks < 2*60*1000:
			if not client.isConnected:
				delClient(agvId,ip,port)
				return None
			return client
		else:
			delClient(agvId,ip,port)
	return None
	
def send(agvId,ip, port, buf):
	client = getClient(agvId,ip,port)
	
	if client:
		try:
			result = client.send(buf)
			return result
		except socket.timeout as e:
			raise e
		except Exception as e:
			delClient(agvId,ip,port) #TODO
			raise e
	else:
		msg = "%s: %s-%s : agv is not connected"%(agvId,ip,str(port))
		raise Exception(msg)
			
def recv(agvId,ip, port, len):
	client = getClient(agvId,ip,port)
	if client:
		try:
			result = client.recv(len)
			return result
		except socket.timeout as e:
			raise e
		except Exception as e:
			delClient(agvId,ip,port)#TODO
			raise e
	else:
		msg = "%s: %s-%s : agv is not connected"%(agvId,ip,str(port))
		raise Exception(msg)

def getKey(agvId,port):
	return agvId + ":" + str(port)

def updateClient(agvId,ip,port):
	key = getKey(agvId,port)
	if key in g_registerAgv:
		g_registerAgv[key][2] = utility.ticks()
	
# def _checkClient():
	# while True:
		# for key in g_registerAgv:
			# agvId,port = key.split(":")
			# ser,client,oldTicks = g_registerAgv[key]
			# try:
				# while True:
					# headData = recv(agvId,ip, port, 2)
					# if headData[0] == 0x5A and headData[1] == 0x01:
						# break
				# headData = recv(agvId,ip, port, 14)
				# bodylen,retType = getDataLen('', headData, '' ,port, '') 
				# if str(retType)[1:] == str(g_pingType[port][0]):
					# pingBuf = getSendingBuffer(agvId,None,g_pingType[port][0])
					# updateClient(agvId, ip, port)
					# send(agvId,ip,port,pingBuf.buf)
					# continue
			# except Exception as e:
				# ser.closeClient(client)
				# log.exception("wait connecting error: ",e)
				# time.sleep(2)
				# continue
		# time.sleep(2)
		# continue
	
def delClient(agvId,ip,port):
	key = getKey(agvId,port)
	if key in g_registerAgv:
		# 主动关闭？？
		ser,client,_ = g_registerAgv[key]
		try:
			ser.closeClient(client)
		except Exception as e:
			log.exception(key+" close old client error:",e)
		log.info(key,"is logout")
		del g_registerAgv[key]
	
g_registerAgv = {}
def _checkRegister():
	while True:
		if g_client.empty():
			time.sleep(2)
			continue
		ser,client,oldTicks = g_client.get()
		if utility.ticks() - oldTicks > 3*60*1000:
			ser.closeClient(client)
			continue
		try:
			headData = client.recv(2)
			if headData is None or headData[0] != 0x5A or headData[1] != 0x01:
				g_client.put([ser,client,oldTicks])
				continue
			headData = client.recv(14) 
			bodylen,retType = getDataLen('', headData, '' ,'', '') 
			if str(retType)[1:] == str(g_pingType[ser.port][0]) and bodylen != 0:
				recData = client.recv(bodylen)  
				inBuf = buffer.inBuffer(recData)
				recJsonData = inBuf.getStr(inBuf.remainLen)#.replace("'", "\"")
				obj = json.loads(recJsonData)
				result = _checkError('', g_pingType[ser.port][0], obj) 
				if "agvId" in result:
					agvId = result["agvId"]
					key = getKey(agvId,ser.port)
					delClient(agvId,'',ser.port)
					log.info(key,"is registered")
					g_registerAgv[key] = [ser,client,utility.ticks()]
					continue
			g_client.put([ser,client,oldTicks])
		except Exception as e:
			ser.closeClient(client)
			log.exception("wait connecting error: ",e)
			time.sleep(1)
			continue
		time.sleep(1)
	
def isOpen(port,ip=None):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
		if not ip:
			ip = "0.0.0.0"
		s.bind((ip,port))
		return False
	except OSError as e:
		return True
	finally:
		s.close()

def getSendingBuffer(agvId, data, type):
	def _getSn():
		global g_sn
		g_sn += 1
		if g_sn >= 65535:
			g_sn = 0
		return g_sn

	jsonData = ""
	if data:
		jsonData = json.dumps(data, separators=(',', ':'))
	buf = buffer.outBuffer()
	buf.setBytes(b"\x5A\x01")
	sn = _getSn()
	buf.setUInt16(sn)
	buf.setUInt32(len(jsonData))
	buf.setUInt16(type)
	buf.setBytes([0x0] * 6)
	buf.setStr(jsonData)
	# if type != 1100:
	# 	print("_request type " + str(type) + " " + agvId + " " + jsonData)
	return buf


def getDataLen(agvId, recData, ip ,port, raw):
	if recData is None:
		log.error(agvId, "agv head is none")
		raise IOError("AGV协议头为空")
	inBuf = buffer.inBuffer(recData)  
	sn= inBuf.getUInt16()
	len= inBuf.getUInt32() 
	retType = inBuf.getUInt16()
	if retType >= 60000:
		log.error(agvId, "decode error:", retType)
		raise IOError("AGV协议返回错误码" + str(retType)) 
	return len,retType


def _checkError(agvId, type, data):
	if "ret_code" not in data:
		return data
	code = data["ret_code"]
	if code == 0:
		return data
	msg = ""
	if "err_msg" in data:
		msg = data["err_msg"]
	raise IOError(agvId + "执行" + str(type) + "错误" + ",code=" + str(code) + ",msg=" + msg)

	
################## unit test ##################

if __name__ == '__main__':
	# import utility
	# utility.run_tests(__file__)
	pass
