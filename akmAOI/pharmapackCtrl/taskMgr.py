# coding: utf-8
# author: pengshuqin
# date: 2019-05-09
# desc: scada任务管理
import os
import sys
import enum
import datetime
import time
import threading

import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)

import mongodb as db
import utility
import log
import lock
import mqtt

# status:
# waiting 任务等待调度
# running 任务执行
# error 任务异常等待处理？
# success 任务完成
# fail 任务完成且失败

# step:
# waiting
# moveSource
# waitSource
# loadPlayload
# moveTarget
# waitTarget
# dropPayload
# finish

g_workPlaceNone = []
g_workPlaceEmpty = []
g_workPlaceFull = []
def setLoc(locId, status):
	s = [str(i) for i in status][0]
	loc = [str(i) for i in locId][0]
	data = {"status": s}
	print('setLoc ---------->', s, loc, data)
	db.update_one("u_loc_info", {"_id": loc}, data)
	if locId in g_workPlaceNone:
		g_workPlaceNone.remove(locId)
	elif locId in g_workPlaceEmpty:
		g_workPlaceEmpty.remove(locId)
	elif locId in g_workPlaceFull:
		g_workPlaceFull.remove(locId)

	if int(s) == 0:
		g_workPlaceNone.append(loc)
	elif int(s) == 1:
		g_workPlaceEmpty.append(loc)
	elif int(s) == 2:
		g_workPlaceFull.append(loc)

	return {"errorno": 0, "errormsg": "set loc %s -> %s succeed" % (s, loc)}


def getSeat():
	ds = db.find("u_loc_info")
	ret = []
	while ds.next():
		d = {}
		d["id"] = ds["_id"]
		d["floorId"] = ds["floorId"]
		d["location"] = ds["location"]
		d["direction"] = ds["direction"]
		ret.append(d)
	return {"info": ret}


def add(taskName,type,**data):
	data["type"] = type
	data["taskName"] = taskName
	now = utility.now()
	data["createTime"] = now
	data["updateTime"] = now
	data["startTime"] = None
	data["endTime"] = None
	data["status"] = "waiting"
	data["step"] = "waiting"
	data["failMsg"] = None
	data["history"] = []
	ret = db.insert("u_scada_task",data)
	taskId = str(ret.inserted_id)
	log.info("create task[%s]:"%taskId,"type=",data["type"],",",taskName,data)
	return taskId

def getUnfinishTask():
	t = datetime.datetime.now()
	t = t - datetime.timedelta(hours=8)
	return db.find("u_scada_task", {"status": {"$nin": ["finish","fail"]},"createTime": {"$gte": t}}).list()
	
def updateFailTask():
	t = datetime.datetime.now()
	t = t - datetime.timedelta(days=8)
	ds = db.find("u_scada_task", {"status": {"$in": ["waiting","running","error"]},"createTime": {"$gte": t}})
	
	while ds.next():
		if ds["endTime"] is None:
			fail(ds["_id"],failMsg="AGV服务异常重启")
		s.append(t)
	return 
	

def start(taskId,**data):
	now = utility.now()
	data["startTime"] = now
	data["updateTime"] = now
	data["status"] = "running"
	db.update_one("u_scada_task",{"_id": db.ObjectId(taskId)},data)
	log.info("task[%s]:"%taskId," start",data)

def finish(taskId, **data):
	data["endTime"] = utility.now()
	data["status"] = "success"
	data["step"] = "finish"
	db.update_one("u_scada_task",{"_id": db.ObjectId(taskId)},data)
	log.info("task[%s]:"%taskId," successed",data)

def fail(taskId, **data):
	data["endTime"] = utility.now()
	data["status"] = "fail"
	db.update_one("u_scada_task",{"_id": db.ObjectId(taskId)},data)
	log.warning("task[%s]:"%taskId,"failed,",data)

def error(taskId, **data):
	data["endTime"] = utility.now()
	data["status"] = "error"
	db.update_one("u_scada_task",{"_id": db.ObjectId(taskId)},data)
	log.warning("task[%s]:"%taskId, " error",data)

def update(taskId, **data):
	data["updateTime"] = utility.now()
	if "status" in data and data["status"] in ["fail","success"] :
		data["endTime"] = data["updateTime"]
	db.update_one("u_scada_task",{"_id": db.ObjectId(taskId)},data)
	if "history" in data:
		del data["history"]
	log.info("task[%s] update info: %s"%(taskId, data))

def get(taskId):
	ret = db.find_one("u_scada_task",{"_id": db.ObjectId(taskId)})
	if ret is None:
		return None
	_update(ret)
	return ret

def getTaskList(taskList):
	if taskList is None or not taskList:
		t = datetime.datetime.now()
		t = t - datetime.timedelta(days=1)
		ds = db.find("u_scada_task", {"status": {"$in": ["waiting","running","error"]},"createTime": {"$gte": t}})
	else :
		t = []
		for id in taskList:
			t.append(db.ObjectId(id))
		ds = db.find("u_scada_task",{"_id": {"$in": t}})
	s = []
	while ds.next():
		t = {
			"taskId": str(ds["_id"]),
			"agvId": ds["agvId"],
			"source": ds["source"],
			"target": ds["target"],
			"payloadId": ds["payloadId"],
			"status": ds["status"],
			"startTime": ds["startTime"],
			"endTime": ds["endTime"],
			"step": ds["step"],
			"failMsg": ds["failMsg"],
			'errorno': ds['errorno'],
			'errormsg': ds['errormsg']
			}
		s.append(t)
	return s

g_status = {
		"fail": -2,
		"error": -1,
		"running": 1,
		"success": 0,
		"waiting": 2
	}

def getTaskList2():
	global g_status
	t = datetime.datetime.now()
	t = t - datetime.timedelta(days=7)
	ds = db.find("u_scada_task", {"createTime": {"$gte": t}}).sort('createTime', db.DESCENDING)
	s = []

	while ds.next():
		d = {}
		d["taskId"] = ds["_id"]
		d["taskName"] = ds["taskName"]
		d["taskType"] = ds["type"]
		d["starttime"] = ds["startTime"]
		d["status"] = g_status[ds["status"]]
		d["msg"] = ds["failMsg"]
		if ds["failMsg"] is not None and ds['errormsg'] is not None:
			d["msg"] = d["msg"] + '-' + ds['errormsg']
		elif ds["failMsg"] is None and ds['errormsg'] is not None:
			d["msg"] = ds['errormsg']
		d["updatetime"] = ds["updateTime"]
		d["agvId"] = ds["agvId"]
		d["endtime"] = ds["endTime"]
		s.append(d)
	return s

def _update(data):
	data["taskId"] = str(data["_id"])
	if data["endTime"]:
		data["isFinished"] = True
	else:
		data["isFinished"] = False
	return data

######### unit test #########
def test_add():
	db.delete_many("u_scada_task",{"type":"testhhh"})
	id = add(taskName="测试程序",type="testhhh",agvId="agv1")
	data = get(id)
	assert data["taskId"] == id
	assert data["type"] == "testhhh"
	assert data["taskName"] == "测试程序"
	assert data["agvId"] == "agv1"
	assert data["status"] == 'waiting'
	assert data["step"] == "waiting"
	assert data["createTime"] != None
	assert data["createTime"] == data["updateTime"]
	assert data["startTime"] == None
	assert data["endTime"] == None
	assert data["history"] == []
	assert not data["isFinished"]

	start(id,agvId="agv2")
	data = get(id)
	print (data)
	assert data["taskId"] == id
	assert data["type"] == "testhhh"
	assert data["taskName"] == "测试程序"
	assert data["agvId"] == "agv2"
	assert data["status"] == 'running'
	assert data["createTime"] != None
	assert data["startTime"] != None
	assert data["updateTime"] == data["startTime"]
	assert data["endTime"] == None
	assert data["history"][0]["status"] == 'waiting'
	assert data["history"][0]["step"] == "waiting"
	assert "msg" not in data["history"][0]
	assert "failMsg" not in data["history"][0]
	assert data["history"][0]["updateTime"] == data["createTime"]
	assert not data["isFinished"]

	finish(id)
	data = get(id)
	assert data["taskId"] == id
	assert data["type"] == "testhhh"
	assert data["taskName"] == "测试程序"
	assert data["agvId"] == "agv2"
	assert data["status"] == 'success'
	assert data["createTime"] != None
	assert data["updateTime"] != None
	assert data["startTime"] != None
	assert data["endTime"] != None
	assert data["history"][0]["status"] == 'waiting'
	assert data["history"][0]["step"] == "waiting"
	assert "msg" not in data["history"][0]
	assert "failMsg" not in data["history"][0]
	assert data["history"][0]["updateTime"] == data["createTime"]
	assert data["history"][1]["status"] == 'running'
	assert data["history"][1]["step"] == "waiting"
	assert "msg" not in data["history"][1]
	assert "failMsg" not in data["history"][1]
	assert data["history"][1]["updateTime"] == data["startTime"]
	assert data["isFinished"]

	id3 = add(taskName="测试程序3",type="testhhh")
	data = get(id3)
	assert data["taskId"] == id3
	assert data["type"] == "testhhh"
	assert data["taskName"] == "测试程序3"
	assert data["status"] == 'waiting'
	assert data["step"] == "waiting"
	assert data["createTime"] != None
	assert data["createTime"] == data["updateTime"]
	assert data["startTime"] == None
	assert data["endTime"] == None
	assert data["history"] == []
	assert not data["isFinished"]

	start(id3,step='moveSource', msg="ycat测试",agvId="agv9")
	data = get(id3)
	assert data["taskId"] == id3
	assert data["type"] == "testhhh"
	assert data["taskName"] == "测试程序3"
	assert data["msg"] == "ycat测试"
	assert data["status"] == 'running'
	assert data["step"] == "moveSource"
	assert data["agvId"] == "agv9"
	assert data["createTime"] != None
	assert data["startTime"] != None
	assert data["startTime"] == data["updateTime"]
	assert data["endTime"] == None
	assert data["history"][0]["status"] == 'waiting'
	assert data["history"][0]["step"] == "waiting"
	assert "msg" not in data["history"][0]
	assert "failMsg" not in data["history"][0]
	assert data["history"][0]["updateTime"] == data["createTime"]
	assert not data["isFinished"]

	update(id3,status='success',msg="成功",agvId="agv2")
	data = get(id3)
	assert data["taskId"] == id3
	assert data["type"] == "testhhh"
	assert data["taskName"] == "测试程序3"
	assert data["msg"] == "成功"
	assert data["status"] == 'success'
	assert data["agvId"] == "agv2"
	assert data["createTime"] != None
	assert data["startTime"] != None
	assert data["updateTime"] != None
	assert data["endTime"] != None
	assert data["history"][0]["status"] == 'waiting'
	assert data["history"][0]["step"] == "waiting"
	assert "msg" not in data["history"][0]
	assert "failMsg" not in data["history"][0]
	assert data["history"][0]["updateTime"] == data["createTime"]

	assert data["history"][1]["status"] == 'running'
	assert data["history"][1]["step"] == "moveSource"
	assert data["history"][1]["msg"] == "ycat测试"
	assert "failMsg" not in data["history"][1]
	assert data["history"][1]["updateTime"] == data["startTime"]
	assert data["isFinished"]

	id2 = add(taskName="测试程序2",type="testhhh")
	data = get(id2)
	assert data["taskId"] == id2
	assert data["type"] == "testhhh"
	assert data["taskName"] == "测试程序2"
	assert data["status"] == 'waiting'
	assert data["step"] == "waiting"
	assert data["createTime"] != None
	assert data["updateTime"] == data["createTime"]
	assert data["startTime"] == None
	assert data["endTime"] == None
	assert data["history"] == []
	assert not data["isFinished"]

	fail(id2,msg="执行失败",agvId="agv04")
	data = get(id2)
	assert data["taskId"] == id2
	assert data["type"] == "testhhh"
	assert data["taskName"] == "测试程序2"
	assert data["status"] == "fail"
	assert data["step"] == "waiting"
	assert data["createTime"] != None
	assert data["updateTime"] != None
	assert data["startTime"] == None
	assert data["endTime"] != None
	assert data["msg"] == "执行失败"
	assert data["history"][0]["status"] == 'waiting'
	assert data["history"][0]["step"] == "waiting"
	assert "msg" not in data["history"][0]
	assert data["history"][0]["updateTime"] == data["createTime"]
	assert data["isFinished"]

	db.delete_many("u_scada_task",{"type":"testhhh"})

def test_get():
	db.delete_many("u_scada_task",{"type": "testhhh"})
	id1 = add(taskName="test1",type="testhhh",source="test11",target="test12",payloadId="AC01")
	id2 = add(taskName="test2",type="testhhh",source="test21",target="test22",payloadId="AC02")
	id3 = add(taskName="test3",type="testhhh",source="test31",target="test32",payloadId="AC03")
	start(id2)
	ret = getTaskList([id1,id2,id3])
	assert len(ret) == 3
	count = 0
	for i in range(3):
		if ret[i]["taskId"] == id1:
			assert ret[i]["source"] == "test11"
			assert ret[i]["target"] == "test12"
			assert ret[i]["payloadId"] == "AC01"
			assert ret[i]["status"] == "fail"
			assert ret[i]["startTime"] == None
			assert ret[i]["endTime"] != None
			assert ret[i]["step"] == "waiting"
			assert ret[i]["failMsg"] == "AGV服务异常重启"
			count = count + 1
		elif ret[i]["taskId"] == id2:
			assert ret[i]["source"] == "test21"
			assert ret[i]["target"] == "test22"
			assert ret[i]["payloadId"] == "AC02"
			assert ret[i]["status"] == "running"
			assert ret[i]["startTime"] != None
			assert ret[i]["endTime"] == None
			assert ret[i]["step"] == "waiting"
			assert ret[i]["failMsg"] == None
			count = count + 1
		elif ret[i]["taskId"] == id3:
			assert ret[i]["source"] == "test31"
			assert ret[i]["target"] == "test32"
			assert ret[i]["payloadId"] == "AC03"
			assert ret[i]["status"] == "waiting"
			assert ret[i]["startTime"] == None
			assert ret[i]["endTime"] == None
			assert ret[i]["step"] == "waiting"
			assert ret[i]["failMsg"] == None
			count = count + 1
	assert count == 3
	update(id2,step="moveSource")
	start(id3)
	update(id3,step="waitSource")
	finish(id3,step="finish")
	ret = getTaskList([id1,id2,id3])
	assert len(ret) == 3
	count = 0
	for i in range(3):
		if ret[i]["taskId"] == id1:
			assert ret[i]["source"] == "test11"
			assert ret[i]["target"] == "test12"
			assert ret[i]["payloadId"] == "AC01"
			assert ret[i]["status"] == "fail"
			assert ret[i]["startTime"] == None
			assert ret[i]["endTime"] != None
			assert ret[i]["step"] == "waiting"
			assert ret[i]["failMsg"] == "AGV服务异常重启"
			count = count + 1
		elif ret[i]["taskId"] == id2:
			assert ret[i]["source"] == "test21"
			assert ret[i]["target"] == "test22"
			assert ret[i]["payloadId"] == "AC02"
			assert ret[i]["status"] == "running"
			assert ret[i]["startTime"] != None
			assert ret[i]["endTime"] == None
			assert ret[i]["step"] == "moveSource"
			assert ret[i]["failMsg"] == None
			count = count + 1
		elif ret[i]["taskId"] == id3:
			assert ret[i]["source"] == "test31"
			assert ret[i]["target"] == "test32"
			assert ret[i]["payloadId"] == "AC03"
			assert ret[i]["status"] == "success"
			assert ret[i]["startTime"] != None
			assert ret[i]["endTime"] != None
			assert ret[i]["step"] == "finish"
			assert ret[i]["failMsg"] == None
			count = count + 1
	assert count == 3
	ret = getTaskList(None)
	assert len(ret) == 1
	assert ret[0]["taskId"] == id2
	assert ret[0]["source"] == "test21"
	assert ret[0]["target"] == "test22"
	assert ret[0]["payloadId"] == "AC02"
	assert ret[0]["status"] == "running"
	assert ret[0]["startTime"] != None
	assert ret[0]["endTime"] == None
	assert ret[0]["step"] == "moveSource"
	assert ret[0]["failMsg"] == None

	db.delete_many("u_scada_task",{"type": "testhhh"})

def test_gettargetList():
	# s = None
	# getTaskList(s)
	getTaskList2()


if __name__ == '__main__':
	# utility.run_tests()
	# test_gettargetList()
	t = datetime.datetime.now()
	t = t - datetime.timedelta(hours=1)
	print (db.find("u_scada_task", {"status": {"$nin": ["finish","fail"]},"createTime": {"$gte": t}}).list())
