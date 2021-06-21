# coding: utf-8
# author: pengshuqin
# date: 2019-05-08
# desc: 

import os
import sys
import bottle
import datetime
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
	
import utility
import mongodb as db

def setLoc(locId,payloadId):
	db.update_one("u_loc_info",{"_id": locId},{"payloadId": payloadId})

def getLoc():
	ds = db.find("u_loc_info")
	ret = []
	while ds.next():
		d = {}
		d["_id"] = ds["_id"]
		d["floorId"] = ds["floorId"]
		d["location"] = ds["location"]
		d["direction"] = ds["direction"]
		ret.append(d)
	return  ret
	
def getAlarm():
	ds = db.find("r_alarm",{"domain": "agv"})
	ds.leftjoin("typeId","c_alarm_type","_id",["value","level"])
	alarmList = []
	while ds.next():
		a = {}
		a["alarmId"] = ds["moid"]
		a["desc"] = ds["desc"]
		a["time"] = ds["createTime"]
		a["level"] = ds["c_alarm_type.level"]
		a["type"] = ds["c_alarm_type.value"]
		alarmList.append(a)
	return alarmList
	
#################################### UNIT TEST #######################

def test_loc():
	db.delete_many("u_loc_info", {"domain": "test"})
	for i in range(100):
		db.insert("u_loc_info",{"_id": "AA00%s"%i, "payloadId": "","domain": "test"})
	l = getLoc()
	assert l == []
	for i in range(50):
		setLoc("AA00%s"%i,"CC090%s"%i)
	l = getLoc()
	assert len(l) == 50
	count = 0
	for i in range(50):
		if l[i]["locId"] == "AA00%s"%i:
			assert l[i]["payloadId"] == "CC090%s"%i
			count = count + 1
	assert count == 50
	db.delete_many("u_loc_info", {"domain": "test"})
	
if __name__ == "__main__":
	utility.run_tests()