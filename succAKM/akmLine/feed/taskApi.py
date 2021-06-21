#coding=utf-8
# 任务管理
import os
import sys
import enum
import datetime
import threading

import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
	
import mongodb as db
import utility
import log
import lock
import auth.authApi as authApi 


g_lock = lock.create("feedTask.g_lock")
g_taskList = set()

class taskStatus(enum.Enum):
	fail = -2
	error = -1
	working = 1
	finished = 0
	waiting = 2

@lock.lock(g_lock)
def _addList(taskId):
	global g_taskList
	g_taskList.add(taskId)
	
@lock.lock(g_lock)
def _removeList(taskId):
	global g_taskList
	if taskId in g_taskList:
		g_taskList.remove(taskId)

@lock.lock(g_lock)	
def _checkList(taskId):
	global g_taskList
	return taskId in g_taskList
	
@lock.lock(g_lock)
def add(taskName,taskType,**data):
	data["taskType"] = taskType
	data["taskName"] = taskName
	data["starttime"] = utility.now()
	data["endtime"] = None
	data["status"] = taskStatus.waiting.value
	data["history"] = []
	ret = db.insert("u_agv_task",data) 
	taskId = str(ret.inserted_id)
	log.info("create task[%s]:"%taskId,", taskName: %s, taskType: %s"%(taskName,taskType))
	_addList(taskId)
	return taskId
	
def finish(taskId, **data):
	data["endtime"] = utility.now()
	data["status"] = taskStatus.finished.value
	_updateHistory(taskId,data)
	db.update_one("u_agv_task",{"_id": db.ObjectId(taskId)},data)
	log.info("task[%s]:"%taskId," successed")
	_removeList(taskId)
	
def fail(taskId, **data):
	data["endtime"] = utility.now()
	data["status"] = taskStatus.fail.value
	_updateHistory(taskId,data)
	db.update_one("u_agv_task",{"_id": db.ObjectId(taskId)},data)
	log.warning("task[%s]:"%taskId, " failed")
	_removeList(taskId)
	
def update(taskId, **data):
	data["updatetime"] = utility.now()
	if "status" in data and data["status"] == taskStatus.finished.value:
		data["endtime"] = data["updatetime"]
	_updateHistory(taskId,data)
	db.update_one("u_agv_task",{"_id": db.ObjectId(taskId)},data)
	if "history" in data:
		del data["history"]
	log.info("task[%s] update info %s"%(taskId, data))
	
def get(taskId):
	ret = db.find_one("u_agv_task",{"_id": db.ObjectId(taskId)}) 
	if ret is None:
		return None
	_update(ret)
	return ret

def _update(data):
	data["taskId"] = str(data["_id"])
	if data["endtime"]:
		data["isFinished"] = True
	else:
		data["isFinished"] = False
		if not _checkList(str(data["_id"])):
			fail(data["_id"],msg="AGV服务异常重启pda1")
			msg = "AGV服务异常重启pda2"
			data["isFinished"] = True
			data["msg"] = msg
			data["endtime"] = utility.now()
	return data
	
def _updateHistory(taskId,data):
	ds = db.find_one("u_agv_task",{"_id": db.ObjectId(taskId)},["status","msg","starttime","updatetime","history"])
	d = {}
	d["status"] = ds["status"]
	d["msg"] = ds["msg"] if "msg" in ds else None
	d["updatetime"] = ds["updatetime"] if "updatetime" in ds else ds["starttime"]
	data["history"] = ds["history"]
	data["history"].append(d)

######### unit test #########
def test_add():
	db.delete_many("u_agv_task",{"taskType":"testhhh"})
	id = add(taskName="测试程序",taskType="testhhh",agvId="agv1")
	data = get(id)
	assert data["taskId"] == id
	assert data["taskType"] == "testhhh"
	assert data["taskName"] == "测试程序"
	assert data["agvId"] == "agv1"
	assert data["status"] == taskStatus.waiting.value
	assert data["starttime"] != None
	assert data["endtime"] == None
	assert data["history"] == []
	assert not data["isFinished"] 
	
	finish(id,agvId="agv2")
	data = get(id)
	assert data["taskId"] == id
	assert data["taskType"] == "testhhh"
	assert data["taskName"] == "测试程序"
	assert data["agvId"] == "agv2"
	assert data["status"] == taskStatus.finished.value
	assert data["starttime"] != None
	assert data["endtime"] != None
	assert data["history"][0]["status"] == taskStatus.waiting.value
	assert data["history"][0]["msg"] == None
	assert data["history"][0]["updatetime"] != None
	assert data["isFinished"] 
	
	id3 = add(taskName="测试程序3",taskType="testhhh")
	data = get(id3)
	assert data["taskId"] == id3
	assert data["taskType"] == "testhhh"
	assert data["taskName"] == "测试程序3"
	assert data["status"] == taskStatus.waiting.value
	assert data["starttime"] != None
	assert data["endtime"] == None
	assert data["history"] == []
	assert not data["isFinished"]
	update(id3,status=taskStatus.working.value, msg="ycat测试",agvId="agv9")
	data = get(id3)
	assert data["taskId"] == id3
	assert data["taskType"] == "testhhh"
	assert data["taskName"] == "测试程序3"
	assert data["msg"] == "ycat测试"
	assert data["status"] == taskStatus.working.value
	assert data["agvId"] == "agv9"
	assert data["starttime"] != None
	assert data["updatetime"] != None
	assert data["endtime"] == None
	assert data["history"][0]["status"] == taskStatus.waiting.value
	assert data["history"][0]["msg"] == None
	assert data["history"][0]["updatetime"] != None
	assert not data["isFinished"] 
 
	update(id3,status=taskStatus.finished.value,msg="成功",agvId="agv2")
	data = get(id3)
	assert data["taskId"] == id3
	assert data["taskType"] == "testhhh"
	assert data["taskName"] == "测试程序3"
	assert data["msg"] == "成功"
	assert data["status"] == taskStatus.finished.value
	assert data["agvId"] == "agv2"
	assert data["starttime"] != None
	assert data["updatetime"] != None
	assert data["endtime"] != None
	assert data["history"][0]["status"] == taskStatus.waiting.value
	assert data["history"][0]["msg"] == None
	assert data["history"][0]["updatetime"] != None
	assert data["history"][1]["status"] == taskStatus.working.value
	assert data["history"][1]["msg"] == "ycat测试"
	assert data["history"][1]["updatetime"] != None
	assert data["isFinished"] 
	
	id2 = add(taskName="测试程序2",taskType="testhhh")
	data = get(id2)
	assert data["taskId"] == id2
	assert data["taskType"] == "testhhh"
	assert data["taskName"] == "测试程序2"
	assert data["status"] == taskStatus.waiting.value
	assert data["starttime"] != None
	assert data["endtime"] == None
	assert data["history"] == []
	assert not data["isFinished"]
	
	fail(id2,msg="执行失败",agvId="agv04")
	data = get(id2)
	assert data["taskId"] == id2
	assert data["taskType"] == "testhhh"
	assert data["taskName"] == "测试程序2"
	assert data["status"] == taskStatus.error.value
	assert data["starttime"] != None
	assert data["endtime"] != None
	assert data["msg"] == "执行失败"
	assert data["history"][0]["status"] == taskStatus.waiting.value
	assert data["history"][0]["msg"] == None
	assert data["history"][0]["updatetime"] != None
	assert data["isFinished"]
	
	db.delete_many("u_agv_task",{"taskType":"testhhh"})
	
if __name__ == '__main__':
	utility.run_tests()
