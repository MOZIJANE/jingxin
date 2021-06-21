#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @Time : 2021/4/20 9:33
# @Author : XiongLue Xie
# @File : taskMgrDao.py


import datetime
import mongodb as db
import utility
import log



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

def add(taskName, type, **data):
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
	ret = db.insert("u_scada_task", data)
	taskId = str(ret.inserted_id)
	log.info("create task[%s]:" % taskId, "type=", data["type"], ",", taskName, data)
	return taskId


def getUnfinishTask():
	t = datetime.datetime.now()
	t = t - datetime.timedelta(hours=8)
	return db.find("u_scada_task", {"status": {"$nin": ["finish", "fail"]}, "createTime": {"$gte": t}}).list()


def updateFailTask():
	t = datetime.datetime.now()
	t = t - datetime.timedelta(days=8)
	ds = db.find("u_scada_task", {"status": {"$in": ["waiting", "running", "error"]}, "createTime": {"$gte": t}})

	while ds.next():
		if ds["endTime"] is None:
			fail(ds["_id"], failMsg="AGV服务异常重启")
		#s.append(t)
	return


def start(taskId, **data):
	now = utility.now()
	data["startTime"] = now
	data["updateTime"] = now
	data["status"] = "running"
	db.update_one("u_scada_task", {"_id": db.ObjectId(taskId)}, data)
	log.info("task[%s]:" % taskId, " start", data)


def finish(taskId, **data):
	data["endTime"] = utility.now()
	data["status"] = "success"
	data["step"] = "finish"
	db.update_one("u_scada_task", {"_id": db.ObjectId(taskId)}, data)
	log.info("task[%s]:" % taskId, " successed", data)


def fail(taskId, **data):
	data["endTime"] = utility.now()
	data["status"] = "fail"
	db.update_one("u_scada_task", {"_id": db.ObjectId(taskId)}, data)
	log.warning("task[%s]:" % taskId, "failed,", data)


def error(taskId, **data):
	data["endTime"] = utility.now()
	data["status"] = "error"
	db.update_one("u_scada_task", {"_id": db.ObjectId(taskId)}, data)
	log.warning("task[%s]:" % taskId, " error", data)


def update(taskId, **data):
	data["updateTime"] = utility.now()
	if "status" in data and data["status"] in ["fail", "success"]:
		data["endTime"] = data["updateTime"]
	db.update_one("u_scada_task", {"_id": db.ObjectId(taskId)}, data)
	if "history" in data:
		del data["history"]
	log.info("task[%s] update info: %s" % (taskId, data))


def get(taskId):
	ret = db.find_one("u_scada_task", {"_id": db.ObjectId(taskId)})
	if ret is None:
		return None
	_update(ret)
	return ret


def getTaskList(taskList):
	if taskList is None or not taskList:
		t = datetime.datetime.now()
		t = t - datetime.timedelta(days=1)
		ds = db.find("u_scada_task", {"status": {"$in": ["waiting", "running", "error"]}, "createTime": {"$gte": t}})
	else:
		t = []
		for id in taskList:
			t.append(db.ObjectId(id))
		ds = db.find("u_scada_task", {"_id": {"$in": t}})
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

if __name__ == '__main__':
	# utility.run_tests()
	# test_gettargetList()
	t = datetime.datetime.now()
	t = t - datetime.timedelta(hours=1)
	print(db.find("u_scada_task", {"status": {"$nin": ["finish", "fail"]}, "createTime": {"$gte": t}}).list())
