# coding: utf-8
# author: pengshuqin
# date: 2019-10-16
# desc: 上料机对接

import os
import sys
import time
import bottle
import datetime
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
	
import log
import local

import deviceCtrl

import log
import meta as m
import webutility
import scadaUtility
import mongodb as db
# import runTask
import lock as lockImp
import runTasks
import agvCtrl.mapMgr
import socket
import local
import threading
import tcpSocket
# import taskMgr
import feedMgr
import autoCtrl.taskMgr as taskMgr

g_lock = threading.RLock()


class mapSel(m.customSelect):
	def __init__(self):
		m.customSelect.__init__(self)

	def items(self, parentId):
		mapList = agvCtrl.mapMgr.getMapList()
		return [{"value": mapList[i]["id"], "label": mapList[i]["id"]} for i in range(len(mapList))]


@m.table("u_loc_info", "工位信息", )
@m.field(id="_id", name="工位", unique=True, type=str, rules=[m.require()])
@m.field(id="floorId", name="地图", type=str, editCtrl=mapSel(), rules=[m.require()])
@m.field(id="location", name="点位", type=str, rules=[m.require()])
@m.field(id="location", name="前置点", type=str, rules=[m.require()])
@m.field(id="p_direction", name="方向", type=float, rules=[m.require()])
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
	return {"taskId": runTasks.feedTask(param)}


@scadaUtility.post('/api/scada/addTask')
def urlAddTask():
	source = webutility.get_param("source")
	target = webutility.get_param("target")
	# payloadId = webutility.get_param("payloadId")
	# priority = webutility.get_param_int("priority")
	payloadId = None
	priority = 1
	return {"taskId" : runTasks.PdaAddTask(source,target,payloadId,priority)}



@scadaUtility.post('/api/agv/tasklist2')
def scadaTaskList():
	return feedMgr.getTaskList()

	
@scadaUtility.post('/api/scada/getTask')
def urlGetTask():
	log.info('-----------------------------------------------访问了api/scada/getTask------------------------------')
	taskList = webutility.get_param("taskList")
	if taskList != None and type(taskList) is str:
		taskList = eval(taskList)
	return {"taskList": taskMgr.getTaskList(taskList(taskList))}

	
@scadaUtility.post('/api/scada/getTask2')
def urlGetTask2():
	log.info('-----------------------------------------------访问了api/scada/getTask2------------------------------')
	return {"list": taskMgr.getTaskList2()}

	
@scadaUtility.get('/api/agv/seat')
def getSeat():
	return feedMgr.getSeat()


@scadaUtility.get('/api/scada/clearLoc')
def setLoc():
	locId = webutility.get_param("locId"),
	status = webutility.get_param("status"),
	return feedMgr.setLoc(locId, status)


@scadaUtility.get('/api/scada/cancelTask')
def setLoc():
	taskId = webutility.get_param("taskId")
	return runTasks.cancel(taskId)


@scadaUtility.get('/api/scada/fail')  # 任务失败
def urlCancelTask():
	taskId = webutility.get_param("taskId")
	return runTasks.failTask(taskId)


@scadaUtility.get('/api/scada/finish')  # 任务成功
def urlFinishTask():
	taskId = webutility.get_param("taskId")
	return runTasks.finishTask(taskId)


@scadaUtility.get('/api/scada/getTaskStatus')  #
def urlGetTaskStatus():
	return {"status": runTasks.getTaskStatus()}


# for uwsgi
app = application = bottle.default_app()

if __name__ == '__main__':
	webutility.run()
else:
	pass