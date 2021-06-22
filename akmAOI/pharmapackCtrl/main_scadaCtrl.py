# coding: utf-8
# author: pengshuqin
# date: 2019-05-08
# desc: scada对接

import os
import sys
import bottle
import datetime
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
	
import webutility
import scadaUtility
import locMgr
import pharmapackCtrl.taskMgr as taskMgr
import pharmapackCtrl.runTasks as runTasks
import lock as lockImp
import meta as m 
import dbQuery.bigTable as bigTable
import threading
import log
import local
import socket
import tcpSocket
import mytimer
import pharmapackCtrl.taskMgr as taskMgr

ip = '0.0.0.0'
port = local.getint("button", "port",10001)
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
	# socket.setdefaulttimeout(30)
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
	# param = {
	# 	"seat1": "",
	# 	"location1": "",
	# 	"floorId1":"",
	# 	"direction1": "",
	# 	"seat2": "",
	# 	"location2": "",
	# 	"floorId2": "",
	# 	"direction2": ""
	# }

	type, source, target = getButtonInfo(devID, keyID)
	print(devID,keyID,source,target)
	# if not g_locInfo:
	# 	g_locInfo = feedMgr.getSeat()["info"]
	# 	print(g_locInfo)
	# for loc in g_locInfo:
	# 	if source == loc["id"]:
	# 		param["seat1"] = loc["id"]
	# 		param["location1"] = loc["location"]
	# 		param["floorId1"] = loc["floorId"]
	# 		param["location1"] = loc["direction"]
	# 	if target == loc["id"]:
	# 		param["seat2"] = loc["id"]
	# 		param["location2"] = loc["location"]
	# 		param["floorId2"] = loc["floorId"]
	# 		param["location2"] = loc["direction"]
	payloadId = None
	priority = 1
	if type == "move":
		if g_taskMgr[devID][keyID]:
			return
		else:
			g_taskMgr[devID][keyID] = runTasks.addTask(source,target,payloadId,priority)



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
				ret = taskMgr.get(id)
				if ret is None or ret["step"] in ["success", "fail"]:
					g_taskMgr[devID][keyID] = None

def getFeedStatus(s):
	s = int(s)
	if s == -2:
		return "fail"
	elif s == -1:
		return "error"
	elif s == 1:
		return "working"
	elif s == 0:
		return "finished"
	elif s == 2:
		return "waiting"
	else:
		return ""

bigTable.install("agvCtrl")
@bigTable.table("u_agv_task","PDA任务列表",domain=False,dateRangeField="starttime",defaultSortId="starttime",defaultSortDir="desc")
@bigTable.field(id="_id",name="任务ID",sortable=False,searchable=True)
@bigTable.field("taskName","任务名称",sortable=False,)
@bigTable.field("agvId","AGV",sortable=False,searchable=True)
@bigTable.field("status","任务状态",sortable=False,formatFunc=getFeedStatus,searchable=True)
@bigTable.field("starttime","开始时间",sortable=True,searchable=False)
@bigTable.field("endtime","结束时间",searchable=False)
@bigTable.field("msg","信息",sortable=False,searchable=False)
class pdaManager(bigTable.manager):
	def __init__(self):
		pass

@bigTable.table("u_scada_task","SCADA任务列表",domain=False,dateRangeField="createTime",defaultSortId="createTime",defaultSortDir="desc")
@bigTable.field(id="_id",name="任务ID",sortable=False,searchable=True)
@bigTable.field("taskName","任务名称",sortable=False,)
@bigTable.field("source","源位置",sortable=False,searchable=True)
@bigTable.field("target","目标位置",sortable=False,searchable=True)
@bigTable.field("payloadId","货架",sortable=False,searchable=True)
@bigTable.field("agvId","AGV",sortable=False,searchable=True)
@bigTable.field("status","任务状态",sortable=False,searchable=True)
@bigTable.field("step","任务步骤",sortable=False,searchable=True)
@bigTable.field("createTime","创建时间",sortable=True,searchable=False)
@bigTable.field("startTime","开始时间",searchable=False)
@bigTable.field("endTime","结束时间",searchable=False)
@bigTable.field("failMsg","信息",sortable=False,searchable=False)
class scadaManager(bigTable.manager):
	def __init__(self):
		pass



@scadaUtility.post('/api/scada/addTask')
def urlAddTask():
	source = webutility.get_param("source")
	target = webutility.get_param("target")
	# payloadId = webutility.get_param("payloadId")
	# priority = webutility.get_param_int("priority")
	payloadId = None
	priority = 1
	return {"taskId" : runTasks.addTask(source,target,payloadId,priority)}
  
@scadaUtility.post('/api/scada/getTask')
def urlGetTask():
	taskList = webutility.get_param("taskList")
	if taskList != None and type(taskList) is str:
		taskList = eval(taskList)
	return {"taskList": taskMgr.getTaskList(taskList)}
	
@scadaUtility.post('/api/scada/getTask2')
def urlGetTask2():
	return {"list": taskMgr.getTaskList2()}
	
@scadaUtility.post('/api/scada/allowTask')
def urlAllowTask():
	taskId = webutility.get_param("taskId")
	locId = webutility.get_param("locId")
	return runTasks.allowTask(taskId,locId)
	
@scadaUtility.get('/api/scada/activeAlarm')
def urlActiveAlarm():
	return {"alarmList": locMgr.getAlarm()}
	
@scadaUtility.post('/api/scada/setLoc')
def urlSetLoc():
	locId = webutility.get_param("locId")
	payloadId = webutility.get_param("payloadId")
	return locMgr.setLoc(locId,payloadId)
	
@scadaUtility.get('/api/scada/getLoc')
def urlGetLoc():
	return {"locList" : locMgr.getLoc()}
	
@scadaUtility.get('/api/scada/fail')# 任务失败
def urlCancelTask():	
	taskId = webutility.get_param("taskId")
	return runTasks.failTask(taskId)

@scadaUtility.get('/api/scada/finish')# 任务成功
def urlFinishTask():
	taskId = webutility.get_param("taskId")
	return runTasks.finishTask(taskId)
	
@scadaUtility.get('/api/scada/cancelTask')# 转人工
def urlSwithchMode():
	taskId = webutility.get_param("taskId")
	return runTasks.switchMode(taskId)
	
@scadaUtility.get('/api/scada/getTaskStatus')# 
def urlGetTaskStatus():
	return {"status": runTasks.getTaskStatus()}
	
#for uwsgi 
app = application = bottle.default_app()
webutility.add_ignore('/scada/getTask')
webutility.add_ignore('/scada/getTaskStatus')
main()
if __name__ == '__main__':
	webutility.run()
else:
	pass