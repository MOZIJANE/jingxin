# coding: utf-8
# author: pengshuqin
# date: 2018-07-24
# desc: 界面告警显示
import sys,os
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
	
import utility
import mongodb as db
import auth.authApi  


def getAlarmCount(domain=None):
	if domain is None:
		domain = auth.authApi.getDomain()
	ds = db.find("r_alarm",{"domain":domain},["typeId"])
	ds.leftjoin("typeId","c_alarm_type","_id",["level"])
	redata = {"critical":0,"major":0,"minor":0,"warning":0}
	while ds.next():
		level = ds["c_alarm_type.level"]
		if level in redata:
			redata[level] = redata[level] + 1
	data = []
	for level in redata:
		data.append({"level":level,"count":redata[level]})
	return data
	
def getAlarmInfo(level,domain=None):
	if domain is None:
		domain = auth.authApi.getDomain()
	ds = db.find("r_alarm",{"domain":domain})
	ds.leftjoin("typeId","c_alarm_type","_id",["value","level"])
	reinfo = []
	while ds.next():
		if level == ds["c_alarm_type.level"]:
			reinfo.append({"moid": ds["moid"],"type": ds["c_alarm_type.value"],"desc": ds["desc"],"createTime": ds["createTime"]})
	return reinfo
	
def getAlarm():
	# ds = db.find("r_alarm",{"domain": "agv"})
	ds = db.find("r_alarm")
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
	
#############################	unit test	########################### 
def test_getAlarmCount():
	now = utility.now()
	db.delete_many("r_alarm",{"moid":"ppppsss"})
	db.delete_many("r_alarm",{"moid" : "pssq"})
	id1 = db.insert("r_alarm",{"moid" : "ppppsss", "typeId" : 2001, "createTime" : now, "desc" : "告警--------", "domain" : "pppsq"}).inserted_id
	id2 = db.insert("r_alarm",{"moid" : "pssq", "typeId" : 2004, "createTime" : now, "desc" : " alarm======", "domain" : "pppsq"}).inserted_id
	info = getAlarmCount("pppsq")
	assert len(info) >= 2
	count = 0
	for i in range(len(info)):
		if info[i]["level"] == "major":
			assert info[i]["count"] >= 1
			count = count + 1
		elif info[i]["level"] == "critical":
			assert info[i]["count"] >= 1
			count = count + 1
		else:
			pass
	assert count == 2
	db.delete_many("r_alarm",{"moid":"ppppsss"})
	db.delete_many("r_alarm",{"moid" : "pssq"})
	
def test_getAlarmInfo():
	now = utility.now()
	db.delete_many("r_alarm",{"moid":"ppppsss"})
	db.delete_many("r_alarm",{"moid" : "pssq"})
	id1 = db.insert("r_alarm",{"moid" : "ppppsss", "typeId" : 2001, "createTime" : now, "desc" : "告警--------", "domain" : "pppsq"}).inserted_id
	id2 = db.insert("r_alarm",{"moid" : "pssq", "typeId" : 2004, "createTime" : now, "desc" : "alarm======", "domain" : "pppsq"}).inserted_id
	info = getAlarmInfo("major","pppsq")
	assert len(info) >= 1
	count = 0
	for i in range(len(info)):
		if info[i]["moid"] == "ppppsss" and info[i]["desc"] == "告警--------":
			assert info[i]["type"] == "CPU告警"
			assert info[i]["createTime"] is not None
			count = count + 1
		else:
			pass
	assert count == 1
	info = getAlarmInfo("critical","pppsq")
	assert len(info) >= 1
	for i in range(len(info)):
		if info[i]["moid"] == "pssq" and info[i]["desc"] == "alarm======":
			assert info[i]["type"] == "进程告警"
			assert info[i]["createTime"] is not None
			count = count + 1
		else:
			pass
	assert count == 2
	db.delete_many("r_alarm",{"moid":"ppppsss"})
	db.delete_many("r_alarm",{"moid" : "pssq"}) 
	
if __name__ == '__main__': 
	#utility.start()
	# auth.authApi.g_domain = "ycat"
	utility.run_tests()
	# utility.finish()
	
	
		