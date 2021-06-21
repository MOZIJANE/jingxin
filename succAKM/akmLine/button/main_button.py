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
import agvCtrl.agvApi as agvApi


g_lock = threading.RLock()

ip = '0.0.0.0'
port = local.getint("button","port",10001)

def reponse(ser,client):
	r_thread = threading.Thread(target=_handle,args=(ser,client,))
	r_thread.start()
	
def _handle(ser,client):
	while True:
		try:
			data = client.recv(6)
			log.info(data)
			devID = data[1]
			keyID = data[4]
			if devID is None or keyID is None or keyID == 0:
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
	buttonSer = tcpSocket.server(ip,port,connectLen=200,acceptCallback=reponse)
	buttonSer.start()
	

Current_loc = {}

g_taskMgr = {}
@lockImp.lock(g_lock)
def addTask(devID,keyID):
	global g_taskMgr
	global Current_loc
	if devID not in g_taskMgr:
		g_taskMgr[devID] = None
	type,map,loc,agv,now_loc = getButtonInfo(devID,keyID)
	#print (type,map,loc,agv)
	if type == "move":
		if g_taskMgr[devID]:
			return 
		else:
			g_taskMgr[devID] = move(agv,loc,devID)
			#记录move位置
			Current_loc['loc'] = loc
			
			# move()
	elif type == "release":
		#先获取当前位置
		if now_loc == Current_loc['loc']:
			result = release(agv)
		else:
			pass
	

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
	now_loc = local.get(devID,"now_loc")
	type,loc = local.get(devID,keyID).split(",")
	return type,map,loc,agvId,now_loc
	
main()
#for uwsgi 
app = application = bottle.default_app()

if __name__ == '__main__': 
	webutility.run()
else:
	pass
	