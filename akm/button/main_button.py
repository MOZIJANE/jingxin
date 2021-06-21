# coding: utf-8
# author: pengshuqin
# date: 2020-04-24
# desc: 

import os
import sys
import time
import socket
import bottle
import uuid 


import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import log
import local
import lock as lockImp
import utility
import webutility
import threading
import tcpSocket
# import agvCtrl.agvApi as agvApi


g_lock = threading.RLock()

ip = '0.0.0.0'
port = 10001#local.getint("button","port",10001)

def reponse(ser,client):
	print ("=====================",client)
	r_thread = threading.Thread(target=_handle,args=(ser,client,))
	r_thread.start()
	
def _handle(ser,client):
	while True:
		try:
			data = client.recv(5)
			devID = data[2]
			keyID = data[3]
			if devID is None or keyID is None:
				continue
			addTask(str(devID),str(keyID))
		except socket.timeout:
			log.exception(client.desc+" time out",client)
			ser.closeClient(client)
			return
		except socket.error:
			log.exception(client.desc+" socket error",client)
			ser.closeClient(client)
			return
		except Exception as e:
			log.exception(client.desc+" error: ",e)
			ser.closeClient(client)
			return

def main():
	buttonSer = tcpSocket.server("0.0.0.0",10001,connectLen=100,acceptCallback=reponse)
	buttonSer.start()
	print ("=============")
	

g_taskMgr = {}
@lockImp.lock(g_lock)
def addTask(devID,keyID):
	global g_taskMgr
	if devID not in g_taskMgr:
		g_taskMgr[devID] = None
	type,map,loc,agv = getButtonInfo(devID,keyID)
	print (type,map,loc,agv)
	if type == "move":
		if g_taskMgr[devID]:
			return 
		else:
			g_taskMgr[devID] = move(agv,loc,devID)
			# move()
	elif type == "release":
		result = release(agv)
	

@lockImp.lock(g_lock)
def onFinish(obj):
	g_taskMgr[obj["devID"]] = False
	
def move(agv,loc,devID):
	agvTaskId = getAgvTaskId(agv)
	init()
	try:
		d = agvApi.isLocked(agv, agvTaskId)
		if not d["isLocked"]:
			# if agvApi.isAvailable(agvId):
			agvApi.lock(agv,agvTaskId)
		param = {}
		param["taskId"] = utility.now_str() + agv
		param["devID"] = devID
		agvApi.move(agv,loc,onFinish,param)
		return True
	except Exception as e:
		log.exception("%s move to %s fail"%(agv,loc),e)
		return False

def release(agv):
	init()
	agvTaskId = getAgvTaskId(agv)
	try:
		agvApi.release(agv, agvTaskId)
		if agvApi.isLocked(agv, agvTaskId):
			agvApi.goHome(agv)
		return True
	except Exception as e:
		log.exception("release %s fail"%agv,e)
		return False
	
g_isInit = None
def init():
	global g_isInit
	if g_isInit is None:
		agvApi.init("button") 
		g_isInit = "button"
	return g_isInit
		
g_agvTaskId = {}
def getAgvTaskId(agv):
	if agv not in g_agvTaskId:
		g_agvTaskId[agv] = agv + str(uuid.uuid4())
	return g_agvTaskId[agv]
	
#return type,map,loc,agv
def getButtonInfo(devID,keyID):
	map = local.get(devID,"map")
	agvId = local.get(devID,"agv")
	type,loc = local.get(devID,keyID).split(",")
	return type,map,loc,agvId
	
main()
#for uwsgi 
app = application = bottle.default_app()

if __name__ == '__main__': 
	webutility.run()
else:
	pass
	