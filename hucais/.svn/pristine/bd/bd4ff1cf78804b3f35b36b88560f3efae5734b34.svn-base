# coding: utf-8
# author: pengshuqin
# date: 2019-04-22
# desc: 数据保存与查询

import os
import sys
import time
import json
import datetime
import setup

if __name__ == "__main__":
	setup.setCurPath(__file__)
	
import config
import utility
import querySet
import mongodb as db
import local 

from runTaskHucais import g_workPlaceNone,g_workPlaceEmpty,g_workPlaceFull


def setLoc(locId,status):
	s = [str(i) for i in status][0]
	loc = [str(i) for i in locId][0]
	data = {"status":s}
	print('setLoc ---------->', s,loc,data)
	db.update_one("u_loc_info",{"_id": loc},data)
	if locId in g_workPlaceNone:
		g_workPlaceNone.remove(locId)
	elif locId in g_workPlaceEmpty:
		g_workPlaceEmpty.remove(locId)
	elif locId in g_workPlaceFull:
		g_workPlaceFull.remove(locId)
	
	if int(s)==0:
		g_workPlaceNone.append(loc)
	elif int(s)==1:
		g_workPlaceEmpty.append(loc)
	elif int(s)==2:
		g_workPlaceFull.append(loc)

	return {"errorno":0, "errormsg":"set loc %s -> %s succeed"%(s,loc)}

def getSeat():
	ds = db.find("u_loc_info")
	ret = []
	if local.get("project","name") == "hucais":
		while ds.next():
			d = {}
			d["id"] = ds["_id"]
			d["floorId"] = ds["floorId"]
			d["location"] = ds["location"]
			d["direction"] = ds["direction"]
			d["status"]=ds["status"]
			ret.append(d)
		return {"info": ret}
	while ds.next():
		d = {}
		d["id"] = ds["_id"]
		d["floorId"] = ds["floorId"]
		d["location"] = ds["location"]
		d["direction"] = ds["direction"]
		ret.append(d)
	return {"info": ret}
	 
def getTaskList(taskList=None):
	ds = db.find("u_agv_task").sort('starttime', db.DESCENDING)
	if local.get("project","name") == 'hucais':
		if taskList is None or not taskList:
			t = datetime.datetime.now()
			t = t - datetime.timedelta(days=1)
			ds = db.find("u_agv_task", {"starttime": {"$gte": t}})
		else :
			t = []
			for id in taskList:
				t.append(db.ObjectId(id))
			ds = db.find("u_agv_task",{"_id": {"$in": t}})

	ret = []
	while ds.next():
		d = {}
		d["taskId"] = ds["_id"]
		d["taskName"] = ds["taskName"]
		d["taskType"] = ds["taskType"]
		d["starttime"] = ds["starttime"]
		d["status"] = ds["status"]
		d["msg"] = ds["msg"]
		d["updatetime"] = ds["updatetime"]
		d["agvId"] = ds["agvId"]
		d["endtime"] = ds["endtime"]
		start_til_now = utility.now() - ds["starttime"]
		if ds["endtime"] is None and start_til_now > datetime.timedelta(minutes=30):
			d["endtime"] = utility.now()
			d["status"] = -2
		ret.append(d)
	return {"list":ret}
	
def getTaskStatus(taskId):
	ds = db.find_one("u_agv_task",{"_id": db.ObjectId(taskId)})
	d = {}
	d["taskId"] = ds["_id"]
	d["taskName"] = ds["taskName"]
	d["taskType"] = ds["taskType"]
	d["starttime"] = ds["starttime"]
	d["status"] = ds["status"]
	d["msg"] = ds["msg"]
	d["updatetime"] = ds["updatetime"]
	d["agvId"] = ds["agvId"]
	d["endtime"] = ds["endtime"]
	return {"info":d}
	
################# UNIT TEST ##################
def test_getSeat():
	db.delete_many("u_loc_info",{"domain": "psq"})
	param = {
		"_id": "cnc_test1",
		"floorId": "map_test1",
		"location": "LM1",
		"direction": 90,
		"domain": "psq"
	}
	db.insert("u_loc_info",param)
	param = {
		"_id": "cnc_test2",
		"floorId": "map_test2",
		"location": "LM2",
		"direction": 0,
		"domain": "psq"
	}
	db.insert("u_loc_info",param)
	param = {
		"_id": "cnc_test3",
		"floorId": "map_test3",
		"location": "LM3",
		"direction": 180,
		"domain": "psq"
	}
	db.insert("u_loc_info",param)
	re = getSeat()
	assert "info" in re
	re = re["info"]
	count = 0
	for i in range(len(re)):
		d = re[i]
		if d["id"] == "cnc_test1":
			assert d["floorId"] == "map_test1"
			assert d["location"] == "LM1"
			assert d["direction"] == 90
			count = count + 1
		elif d["id"] == "cnc_test2":
			assert d["floorId"] == "map_test2"
			assert d["location"] == "LM2"
			assert d["direction"] == 0
			count = count + 1
		elif d["id"] == "cnc_test3":
			assert d["floorId"] == "map_test3"
			assert d["location"] == "LM3"
			assert d["direction"] == 180
			count = count + 1
	assert count == 3
	db.delete_many("u_loc_info",{"domain": "psq"})
	
def test_getTaskList():
	db.delete_many("u_agv_task", {"taskType": "testdd"})
	param = {
		"_id": "psqq1",
		"taskName": "test move1",
		"taskType": "testdd",
		"agvId": "agv01",
		"starttime": utility.now(),
		"endtime": None,
		"status":-1,
	}
	db.insert("u_agv_task",param)
	param = {
		"_id": "psqq2",
		"taskName": "test move2",
		"taskType": "testdd",
		"agvId": "agv02",
		"starttime": utility.now(),
		"endtime": None,
		"updatetime": utility.now(),
		"status":1,
		"msg": "正在前往LM1",
	}
	db.insert("u_agv_task",param)
	param = {
		"_id": "psqq3",
		"taskName": "test move3",
		"taskType": "testdd",
		"agvId": "agv03",
		"starttime": utility.now(),
		"endtime": utility.now(),
		"updatetime": utility.now(),
		"status":0,
		"msg": "成功",
	}
	db.insert("u_agv_task",param)
	param = {
		"_id": "psqq4",
		"taskName": "test move4",
		"taskType": "testdd",
		"agvId": "agv04",
		"starttime": utility.now(),
		"endtime": utility.now(),
		"updatetime": utility.now(),
		"status":-2,
		"msg": "无可用agv",
	}
	db.insert("u_agv_task",param)
	re = getTaskList()
	assert "list" in re
	re = re["list"]
	count = 0
	for i in range(len(re)):
		d = re[i]
		if d["taskId"] == "psqq1":
			assert d["taskName"] == "test move1"
			assert d["taskType"] == "testdd"
			assert d["starttime"] != None
			assert d["status"] == -1
			assert d["msg"] == None
			assert d["updatetime"] == None
			assert d["agvId"] == "agv01"
			assert d["endtime"] == None
			count = count + 1
		elif d["taskId"] == "psqq2":
			assert d["taskName"] == "test move2"
			assert d["taskType"] == "testdd"
			assert d["starttime"] != None
			assert d["status"] == 1
			assert d["msg"] == "正在前往LM1"
			assert d["updatetime"] != None
			assert d["agvId"] == "agv02"
			assert d["endtime"] == None
			count = count + 1
		elif d["taskId"] == "psqq3":
			assert d["taskName"] == "test move3"
			assert d["taskType"] == "testdd"
			assert d["starttime"] != None
			assert d["status"] == 0
			assert d["msg"] == "成功"
			assert d["updatetime"] != None
			assert d["agvId"] == "agv03"
			assert d["endtime"] != None
			count = count + 1
		elif d["taskId"] == "psqq4":
			assert d["taskName"] == "test move4"
			assert d["taskType"] == "testdd"
			assert d["starttime"] != None
			assert d["status"] == -2
			assert d["msg"] == "无可用agv"
			assert d["updatetime"] != None
			assert d["agvId"] == "agv04"
			assert d["endtime"] != None
			count = count + 1
	assert count == 4
	db.delete_many("u_agv_task",{"taskType": "testdd"})
	
if __name__ == "__main__":
	utility.run_tests()