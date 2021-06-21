import time
import sys,os
import datetime
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import enhance
import utility
import config
import log 
import mqtt
import mytimer
import mongodb as db
import auth.authApi 
import alarm.alarmApi


def receiveTopic(topic,data):
	moid = utility.get_attr(data,_loadInfo()[topic]["moidpath"])
	domain = utility.get_attr(data,"domain")
	if moid is None :
		return
	_getAlarm(moid,data,_loadInfo()[topic]["condition"],domain)

def _getAlarm(moid,data,condition,domain):
	lenth = len(condition)
	desc = None
	for i in range(lenth):
		param = utility.get_attr(data,condition[i]["datapath"])
		alarmId = condition[i]["alarmTypeId"]
		threshold = condition[i]["threshold"]
		op = condition[i]["op"]
		if op == "greater":
			if param > threshold:
				desc = "参数%s值为%s，超过门限值%s"%(condition[i]["datapath"],param,threshold)
				alarm.alarmApi.alarm(moid,alarmId,desc,domain)
			else:
				alarm.alarmApi.clear(moid,alarmId,domain)
		if op == "less":
			if param < threshold:
				desc = "参数%s值为%s，低于门限值%s"%(condition[i]["datapath"],param,threshold)
				alarm.alarmApi.alarm(moid,alarmId,desc,domain)
			else:
				alarm.alarmApi.clear(moid,alarmId,domain)
	
g_info=None
def _loadInfo():
	global g_info
	if g_info is not None:
		return g_info
	g_info = {}
	if not config.getbool("mongo","enable",True):
		return g_info
	ds = db.find("c_alarm_threshold") 
	while ds.next():
		condition = {"datapath": ds["datapath"],"threshold": ds["threshold"],"alarmTypeId": ds["alarmTypeId"],"op": ds["op"]}
		if ds["topic"] in g_info:
			g_info[ds["topic"]]["condition"].append(condition)
		else:
			g_info[ds["topic"]] = {"moidpath": ds["moidpath"],"condition": [condition]}
	return g_info
	
@mytimer.interval(timeoutMs=5000)
def msubscribe():
	global g_info
	info = g_info
	g_info = None
	for key in _loadInfo():
		if info is None or key not in info:
			mqtt.subscribe(key,receiveTopic)
	
#############################	unit test	########################### 
def test_listen():
	db.delete_many("c_alarm_threshold",{"alarmTypeId": {"$in": [9999,9998]}})
	db.delete_many("c_alarm_type",{"_id":{"$in": [9999,9998]}}) 
	db.delete_many("r_alarm",{"typeId": {"$in": [9999,9998]}})
	db.delete_many("r_alarm_history",{"typeId": {"$in": [9999,9998]}})
	
	db.insert("c_alarm_type",{"_id":9999,"value":"testalarmtype","level":"critical"}) 
	db.insert("c_alarm_type",{"_id":9998,"value":"testalarmtype","level":"critical"})
	db.insert("c_alarm_threshold",{"topic": "test/22/testt","datapath": "current","moidpath": "moid","threshold": 9,"op": "greater","alarmTypeId": 9999})
	db.insert("c_alarm_threshold",{"topic": "test/22/testt","datapath": "current","moidpath": "moid","threshold": -3,"op": "less","alarmTypeId": 9998})
	db.insert("c_alarm_threshold",{"topic": "test/4/testt","datapath": "current.1","moidpath": "moid","threshold": 4,"op": "less","alarmTypeId": 9999})
	global count
	count = 0
	def rec(topic,data):
		global count
		count = count + 1
	mqtt.subscribe("alarm/raise/9999",rec)
	mqtt.subscribe("alarm/raise/9998",rec)
	time.sleep(5)
	mqtt.send("test/22/testt",{"current": 8,"moid": "水表1","domain": "kkk"})
	mqtt.send("test/4/testt",{"current": [1,-5],"moid": "水表5","domain": "kkk"})
	mqtt.send("test/22/testt",{"current": 33,"moid": "水表1"})
	
	time.sleep(1)
	assert count == 2
	
	mqtt.send("test/22/testt",{"current": -9,"moid": "水表1"})
	time.sleep(1)
	assert count == 3
	db.delete_many("c_alarm_threshold",{"alarmTypeId": {"$in": [9999,9998]}})
	db.delete_many("c_alarm_type",{"_id":{"$in": [9999,9998]}}) 
	db.delete_many("r_alarm",{"typeId": {"$in": [9999,9998]}})
	db.delete_many("r_alarm_history",{"typeId": {"$in": [9999,9998]}})
	
if __name__ == '__main__':
	auth.authApi.g_domain = "fff"
	utility.run_tests()
	
	