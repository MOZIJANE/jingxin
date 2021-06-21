import os
import sys
import bottle
import datetime
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)

import log
import meta as m
import webutility
import scadaUtility
import mongodb as db
# import runTask
import lock as lockImp
import runTasknanqu
import agvCtrl.mapMgr
import socket
import local
import threading
import tcpSocket
# import taskMgr
import feedMgr
import taskApi
import mytimer
g_lock = threading.RLock()

# ip = '127.0.0.1'
# ip = '192.168.47.102'
ip = '0.0.0.0'
port = local.getint("button", "port",8899)
g_lock = threading.RLock()


def reponse(ser, client):
	r_thread = threading.Thread(target=_handle, args=(ser, client,))
	r_thread.start()


def _handle(ser, client):
	while True:
		try:
			data = client.recv(6)
			devID = data[1]
			keyID = data[4]

			if devID is None or keyID is None or keyID  == 0:
				continue
			addTask(str(devID), str(keyID))
		except socket.timeout:
			log.exception(client.desc + " time out", client)
			ser.closeClient(client)
			return
		except socket.error:
			log.exception(client.desc + " socket error", client)
			ser.closeClient(client)
			return
		except Exception as e:
			log.exception(client.desc + " error: ", e)
			ser.closeClient(client)
			return


def main():
	log.info("IP:",ip,"port:",port)
	buttonSer = tcpSocket.server(ip, port, connectLen=100, acceptCallback=reponse)
	buttonSer.start()

g_locInfo ={}
g_taskMgr = {}
g_taskMgr["1"]={"1": None,"2": None,"3": None,"4": None}
g_taskMgr["2"]={"1": None,"2": None,"3": None,"4": None}
g_taskMgr["3"]={"1": None,"2": None,"3": None,"4": None}
g_taskMgr["4"]={"1": None,"2": None,"3": None,"4": None}
g_taskMgr["5"]={"1": None,"2": None,"3": None,"4": None}
g_taskMgr["6"]={"1": None,"2": None,"3": None,"4": None}

@lockImp.lock(g_lock)
def addTask(devID, keyID):
	global g_taskMgr,g_locInfo
	param = {
		"seat1": "",
		"location1": "",
		"floorId1":"",
		"direction1": "",
		"seat2": "",
		"location2": "",
		"floorId2": "",
		"direction2": ""
	}

	type, source, target = getButtonInfo(devID, keyID)
	print(devID,keyID,source,target)
	if not g_locInfo:
		g_locInfo = feedMgr.getSeat()["info"]
		print(g_locInfo)
	for loc in g_locInfo:
		if source == loc["id"]:
			param["seat1"] = loc["id"]
			param["location1"] = loc["location"]
			param["floorId1"] = loc["floorId"]
			param["location1"] = loc["direction"]
		if target == loc["id"]:
			param["seat2"] = loc["id"]
			param["location2"] = loc["location"]
			param["floorId2"] = loc["floorId"]
			param["location2"] = loc["direction"]
	if type == "move":
		if g_taskMgr[devID][keyID]:
			return
		else:
			g_taskMgr[devID][keyID] = runTasknanqu.feedTask(param)



#return type,map,loc,agv
def getButtonInfo(devID,keyID):
	type,source,target = local.get(devID,keyID).split(",")
	return type,source,target

@lockImp.lock(g_lock)
@mytimer.interval(3000)
def checktask():
	for devID in g_taskMgr:
		for keyID in g_taskMgr[devID]:
			id = g_taskMgr[devID][keyID]
			if id:
				ret = taskApi.get(id)
				if ret is None or ret["step"] in ["success", "fail"]:
					g_taskMgr[devID][keyID] = None



class mapSel(m.customSelect):
	def __init__(self):
		m.customSelect.__init__(self)
		
	def items(self, parentId):
		mapList = agvCtrl.mapMgr.getMapList()
		return [{"value": mapList[i]["id"], "label": mapList[i]["id"]} for i in range(len(mapList))]

@m.table("u_loc_info","工位信息",)
@m.field(id="_id",name="工位",unique=True, type=str, rules=[m.require()])
@m.field(id="floorId",name="地图", type=str, editCtrl=mapSel(), rules=[m.require()])
@m.field(id="location",name="点位", type=str, rules=[m.require()])
@m.field(id="location",name="前置点", type=str, rules=[m.require()])
@m.field(id="p_direction",name="方向", type=float, rules=[m.require()])
class seatManager(m.manager):
	def __init__(self):
		m.manager.__init__(self)


@scadaUtility.post('/api/agv/feed')
def urlFeed():
	# proName = local.get("project","name")
	param = {
		"seat1": webutility.get_param("source"),
		"seat2": webutility.get_param("target")
	}

	return {"taskId": runTasknanqu.feedTask(param)}
 
@scadaUtility.post('/api/agv/tasklist')
def scadaTaskList():
	return feedMgr.getTaskList()
	
@scadaUtility.get('/api/agv/seat')
def getSeat():
	return feedMgr.getSeat()

@scadaUtility.get('/api/scada/clearLoc')
def setLoc():
	locId = webutility.get_param("locId"),
	status = webutility.get_param("status"),
	return feedMgr.setLoc(locId,status)
	
#for uwsgi
main()
app = application = bottle.default_app()

if __name__ == '__main__':
	webutility.run()
else:
	pass