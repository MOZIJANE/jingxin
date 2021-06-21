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
import taskMgr
import runTasks

import meta as m 
import dbQuery.bigTable as bigTable


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

if __name__ == '__main__':
	webutility.run()
else:
	pass