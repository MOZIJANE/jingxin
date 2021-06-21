# coding: utf-8
# author: pengshuqin
# date: 2019-10-16
# desc: 上料机对接

#import bottle
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import meta as m
import webutility
import scadaUtility
import runTasks01
import agvCtrl.mapMgr
import threading
import feedMgr
import locMgr
from dao import taskMgrDao as taskMgr

#g_lock = threading.RLock()


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


# @scadaUtility.post('/api/agv/feed')
# def urlFeed():
# 	# proName = local.get("project","name")
# 	param = {
# 		"seat1": webutility.get_param("source"),
# 		"seat2": webutility.get_param("target")
# 	}
#
# 	return {"taskId": runTasks.feedTask(param)}
#
#
# @scadaUtility.post('/api/agv/tasklist')
# def scadaTaskList():
# 	return feedMgr.getTaskList()
#
#
# @scadaUtility.get('/api/agv/seat')
# def getSeat():
# 	return feedMgr.getSeat()
#
#
# @scadaUtility.get('/api/scada/clearLoc')
# def setLoc():
# 	locId = webutility.get_param("locId"),
# 	status = webutility.get_param("status"),
# 	return feedMgr.setLoc(locId, status)
#
#
# @scadaUtility.get('/api/scada/cancelTask')
# def setLoc():
# 	taskId = webutility.get_param("taskId")
# 	return runTasks.cancel(taskId)
#
#
# @scadaUtility.get('/api/scada/fail')  # 任务失败
# def urlCancelTask():
# 	taskId = webutility.get_param("taskId")
# 	return runTasks.failTask(taskId)
#
#
# @scadaUtility.get('/api/scada/finish')  # 任务成功
# def urlFinishTask():
# 	taskId = webutility.get_param("taskId")
# 	return runTasks.finishTask(taskId)
#
#
# @scadaUtility.get('/api/scada/getTaskStatus')  #
# def urlGetTaskStatus():
# 	return {"status": runTasks.getTaskStatus()}
#
# @scadaUtility.get('/api/scada/test01')  #
# def urlGetTaskStatus():
# 	print("return data")
# 	return {"status": "done"}

# 可以进入下一个节点
@scadaUtility.post('/api/scada/nextNode')
def urlMove2NextNode():
	return {"list": taskMgr.getTaskList2()}


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
	return runTasks01.allowTask(taskId, locId)


@scadaUtility.get('/api/scada/activeAlarm')
def urlActiveAlarm():
	return {"alarmList": locMgr.getAlarm()}

@scadaUtility.post('/api/scada/setLoc')
def urlSetLoc():
	locId = webutility.get_param("locId")
	payloadId = webutility.get_param("payloadId")
	return locMgr.setLoc(locId, payloadId)

@scadaUtility.get('/api/scada/getLoc')
def urlGetLoc():
	return {"locList": locMgr.getLoc()}

@scadaUtility.get('/api/scada/fail')# 任务失败
def urlCancelTask():
	taskId = webutility.get_param("taskId")
	return runTasks01.failTask(taskId)

@scadaUtility.get('/api/scada/finish')# 任务成功
def urlFinishTask():
	taskId = webutility.get_param("taskId")
	return runTasks01.finishTask(taskId)

# @scadaUtility.post('/api/scada/addTaskByPad')
@scadaUtility.post('/api/scada/addTask')
def urlAddTask():
	source = webutility.get_param("source")
	target = webutility.get_param("target")
	# payloadId = webutility.get_param("payloadId")
	# priority = webutility.get_param_int("priority")
	payloadId = None
	priority = 1
	return {"taskId" : runTasks01.addTaskByPad(source,target,payloadId,priority,taskKind = "load")}

# @scadaUtility.get('/api/scada/cancelTask')# 转人工
# def urlSwithchMode():
# 	taskId = webutility.get_param("taskId")
# 	return runTasks01.switchMode(taskId)

@scadaUtility.get('/api/scada/cancelTask')  # 转人工
def urlSwithchMode():
	taskId = webutility.get_param("taskId")
	return runTasks01.switchMode(taskId)

@scadaUtility.get('/api/scada/getTaskStatus')  #
def urlGetTaskStatus():
	return {"status": runTasks01.getTaskStatus()}

# for uwsgi
#app = application = bottle.default_app()

# if __name__ == '__main__':
# 	webutility.run()
# else:
# 	pass