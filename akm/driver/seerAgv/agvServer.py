# coding=utf-8
# ycat			2018-8-2	  create
# seerAgv的API封装 
import sys, os
import threading
import socket
import time
import setup 
if __name__ == '__main__':
	setup.setCurPath(__file__)
import json
import buffer
import log
import utility
import lock as lockImp
import tcpSocket

API_PORT_STATE = 19204
g_server = None
g_port = API_PORT_STATE

g_lock = lockImp.create("agvserver")
g_agv_links =   {}	# <agvId,<port,{"client":client,"ticks":ticks,"thread":thread}> >
g_agvs 		= {}	# <agvId,{"data":{},"lock":lock>

PING_TYPE = 1707
TIME_OUT  = 60000

def start():
	global g_server
	g_server = tcpSocket.server("0.0.0.0",g_port,connectLen=-1,acceptCallback=_handleRegister)
	g_server.start()


def _getDataLen(recData):
	inBuf = buffer.inBuffer(recData)  
	sn = inBuf.getUInt16()
	len= inBuf.getUInt32() 
	retType = inBuf.getUInt16()
	return len,retType


def _checkError(data):
	if "ret_code" not in data:
		return data
	code = data["ret_code"]
	if code == 0:
		return data
	msg = ""
	if "err_msg" in data:
		msg = data["err_msg"]
	raise IOError("decode error,code=" + str(code) + ",msg=" + msg)


def readData(client,timeoutTicks):
	startTicks = utility.ticks()
	while utility.ticks() - startTicks < timeoutTicks:
		try:
			headData = client.recv(1)
			if headData[0] != 0x5A:
				continue
			headData = client.recv(1)
			if headData[0] != 0x01:
				continue
			headData = client.recv(14)
			bodylen,retType = _getDataLen(headData) 
			if bodylen == 0:
				return {},retType
			recData = client.recv(bodylen) 
			inBuf = buffer.inBuffer(recData)
			recJsonData = inBuf.getStr(inBuf.remainLen)#.replace("'", "\"")
			obj = json.loads(recJsonData)
			result = _checkError(obj) 
			return result,retType
		except socket.timeout as e:
			# log.error("read data timeout:"+client.peerIP,e)
			# log.exception("",e)
			pass
	log.error("read data timeout2:"+client.peerIP)
	return None,None
	
		
@lockImp.lock(g_lock)
def addClient(agvId,linkId,client):
	global g_agv_links,g_agvs
	if agvId not in g_agvs:
		lock = lockImp.create("client."+agvId+"."+str(linkId))
		g_agvs[agvId] = {"data": {},"lock": lock}
		
	delClient(agvId,linkId)
	t = threading.Thread(target=handleData,args=[agvId,client,linkId])
	t.start()
	if agvId not in g_agv_links:
		g_agv_links[agvId] = {}
	g_agv_links[agvId][linkId] = {"client":client,"ticks":utility.ticks(),"thread":t}

		
@lockImp.lock(g_lock)
def delClient(agvId,linkId):
	try:
		if agvId not in g_agv_links:
			return 
		if linkId not in g_agv_links[agvId]:
			return
		data = g_agv_links[agvId][linkId]
		data["client"].isConnected = False
		g_server.closeClient(data["client"])
		# data["thread"].join()
		
		del g_agv_links[agvId][linkId]
		log.warning("agv server del client:",agvId,linkId)
	except Exception as e:
		log.exception("agv server del client error:"+agvId+","+str(linkId),e)
		
@lockImp.lock(g_lock)
def getClient(agvId,ip,port):
	if agvId not in g_agv_links:
		return None
	if 0 in g_agv_links[agvId]:
		return g_agv_links[agvId][0]["client"]
	if 1 in g_agv_links[agvId]:
		return g_agv_links[agvId][1]["client"]
	return None
	

def _handleRegister(server,client):
	tick = utility.ticks()
	while client.isConnected:
		try:
			result,retType = readData(client,TIME_OUT)
		except Exception as e:
			log.exception(" _handleRegister error:",e)
			break
		if result is None:
			break
		if str(retType)[1:] != str(PING_TYPE):
			continue
		if "agvId" not in result:
			continue
		if "linkId" not in result:
			continue
		agvId = result["agvId"]
		linkId = int(result["linkId"])
		if linkId != 0 and linkId != 1:
			log.error("wrong linkId",linkId)
			continue
		addClient(agvId,linkId,client)
		log.info(agvId,"is registered, linkId",linkId)
		return True
	log.error("register failed, ip",client.peerIP)
	return False
	

def handleData(agvId,client,linkId):
	try:
		while client.isConnected:
			data,retType = readData(client,TIME_OUT)
			if data is None:
				break
			if str(retType)[1:] == str(PING_TYPE):
				sendPing(client,agvId)
				continue
			setData(agvId,str(retType)[1:],data)	#返回类型是发送类型+10000
	except Exception as e:
		log.exception("handleData:%s[%s]"%(agvId,linkId),e)
	delClient(agvId,linkId)
		 
g_sn = -1
def sendPing(client,agvId):
	def _getSn():
		global g_sn
		g_sn += 1
		if g_sn >= 65535:
			g_sn = 0
		return g_sn

	buf = buffer.outBuffer()
	buf.setBytes(b"\x5A\x01")
	sn = _getSn()
	buf.setUInt16(sn)
	buf.setUInt32(0)
	buf.setUInt16(PING_TYPE)
	buf.setBytes([0x0] * 6)
	client.send(buf.buf)

def sendCmd(agvId, buf, ip, port, type):
	c = getClient(agvId,ip,port)
	if c is None:
		raise Exception("can't find client",agvId)
	c.send(buf.buf)
	ticks = utility.ticks()
	while utility.ticks() - ticks < TIME_OUT:
		data = getData(agvId,type)
		if data is not None:
			return data
		time.sleep(0.1)
		
		
def getData(agvId,typeId):
	global g_agvs
	if agvId not in g_agvs:
		raise Exception("can't find data",agvId)
	agv = g_agvs[agvId]
	lockImp.acquire(agv["lock"])
	try:
		if str(typeId) not in agv["data"]:
			return None
		return agv["data"][str(typeId)]
	finally:
		lockImp.release(agv["lock"])
	
def setData(agvId,typeId,data):
	global g_agvs
	if agvId not in g_agvs:
		return
	agv = g_agvs[agvId]
	lockImp.acquire(agv["lock"])
	try:
		agv["data"][typeId] = data
	finally:
		lockImp.release(agv["lock"])
	
################## unit test ##################

if __name__ == '__main__':
	start()
	while True:
		time.sleep(2)
