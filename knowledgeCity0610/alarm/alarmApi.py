#coding=utf-8 
# ycat        2016/03/29      create
import sys,os
import datetime
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
	
import utility
if utility.is_run_all():
	import main_alarm
import mongodb as db
import log
import enhance
import mytimer
import lock
import time
import threading
import auth.authApi  

alarmEvent = enhance.event()
clearEvent = enhance.event()

#区别moid和name的告警接口 
def alarm(moid,typeId,desc,domain=None):
	if not db.isConnect():
		return
	ds = {}
	ds["createTime"] = utility.now()
	ds["moid"] = moid 
	ds["typeId"] = typeId
	ds["desc"] = desc
	if domain is None:
		ds["domain"] = auth.authApi.getDomain()
	else:
		ds["domain"] = domain
	global g_delayAlarm,g_delayClear
	key = _makeKey(ds["domain"],ds["moid"],ds["typeId"])
	if key in g_delayClear:
		del g_delayClear[key]
	
	if _getDelay(typeId) == 0:
		_alarm(ds)
	else:
		if key not in g_delayAlarm:
			g_delayAlarm[key] = ds	
	
	
def _alarm(ds):
	import mqtt
	global g_alarm
	key = _makeKey(ds["domain"],ds["moid"],ds["typeId"])
	if key in g_alarm:
		if g_alarm[key][0] != None :
			return 
	g_alarm[key] = (ds["desc"],utility.ticks())
	
	f = {"moid":ds["moid"],"typeId":ds["typeId"]}
	ret = db.update_one("r_alarm",f,ds,update_or_insert=True)
	alarmEvent.emit(ds["moid"],ds["typeId"],ds["desc"])
	mqtt.send("alarm/raise/"+str(ds["typeId"]),ds)
	#ycat: ret.upserted_id有时候为None
	if ret.upserted_id is None:
		log.error("raise alarm obj=%s, typeId=%d, desc=%s"%(ds["moid"],ds["typeId"],ds["desc"]))
	else:
		log.error("raise alarm obj=%s, typeId=%d, desc=%s, id=%s"%(ds["moid"],ds["typeId"],ds["desc"],str(ret.upserted_id)))
		
		
#清除告警 
def clear(moid,typeId,domain=None):
	global g_delayAlarm,g_delayClear
	if not db.isConnect():
		return
	ds={}
	ds["moid"] = moid
	ds["typeId"] = typeId
	ds["clearTime"] = utility.now()
	if domain is None:
		ds["domain"] = auth.authApi.getDomain()
	else:
		ds["domain"] = domain
	key = _makeKey(ds["domain"],ds["moid"],ds["typeId"])
	if key in g_delayAlarm:
		del g_delayAlarm[key]
	if _getDelay(typeId,isClear=True) == 0:
		_clear(ds)
	else:
		if key not in g_delayClear:
			g_delayClear[key] = ds
	
def getAlarmRange(moid,typeIds,domain):
	if not db.isConnect():
		return []
	ret = []
	ds = db.find("r_alarm",{"moid":moid,"typeId":{"$in":list(typeIds)},"domain":domain})
	while ds.next():
		ret.append(ds["typeId"])
	return ret
		
#批量判断是否有未清告警，一般用于初始化中 
def clearRange(moid,typeIds,domain,force=False):
	if not typeIds:
		return
	#for t in typeIds:
	#	key = _makeKey(domain,moid,t)
	ids = getAlarmRange(moid,typeIds,domain)
	for i in ids:
		clear(moid,i,domain)
	#	if force or key in g_alarm:
	#		clear(moid,t,domain)
	
def _clear(clearDs): 
	import mqtt
	global g_alarm
	key = _makeKey(clearDs["domain"],clearDs["moid"],clearDs["typeId"])
	if key in g_alarm:
		if g_alarm[key][0] == None:
			return
			#pass
	g_alarm[key] = (None,utility.ticks())
	
	if not db.isConnect():
		return
	
	ds = db.find("r_alarm",{"moid":clearDs["moid"],"typeId":clearDs["typeId"],"domain":clearDs["domain"]})
	while ds.next():
		db.delete_one("r_alarm",{"_id":ds["_id"]})
		dd = {}
		dd["createTime"] = ds["createTime"] 
		dd["moid"] = ds["moid"] 
		dd["typeId"] = ds["typeId"]
		dd["desc"] = ds["desc"]
		dd["clearTime"] = clearDs["clearTime"]
		dd["domain"] = clearDs["domain"]
		db.insert("r_alarm_history",dd)
		clearEvent.emit(clearDs["moid"],clearDs["typeId"]) 
		mqtt.send("alarm/clear/"+str(dd["typeId"]),dd)
		log.warning("clear alarm obj=%s, typeId=%d, id=%s"%(clearDs["moid"],clearDs["typeId"],str(ds["_id"])))
		
		
#告警过滤 
g_alarm = {} 
g_delayAlarm = {} #key=key,value=ds
g_delayClear = {} #key=key,value=ds

def _makeKey(domain,moid,typeId):
	return domain + "@@" + str(moid)+"@@"+str(typeId)
	
		
g_delayInfo = None

def _loadDelay():
	global g_delayInfo
	if g_delayInfo is not None:
		return g_delayInfo
	g_delayInfo = {}
	if not db.isConnect():
		return g_delayInfo
	ds = db.find("c_alarm_type")
	while ds.next():
		a = ds.get("raiseWait")
		c = ds.get("clearWait")
		if a is None:
			a = 0
		if c is None:
			c = 0
		g_delayInfo[ds["_id"]] = (a,c)	
	return g_delayInfo
	
	
def _getDelay(typeId,isClear=False):
	data = _loadDelay()
	if typeId in data:
		if isClear:
			return data[typeId][1]
		else:
			return data[typeId][0]
	return 0
		
		
#用于单元测试
def check_alarm(moid,typeId): 
	ds = db.find("r_alarm",{"moid":moid,"typeId":typeId}) 
	return ds.count == 1
	
@mytimer.interval(timeoutMs=5000)	 
def checkDelay():
	global g_delayClear,g_delayAlarm 
	remove = []
	now = utility.now()
	for a in g_delayAlarm:
		alarm = g_delayAlarm[a]
		if (now - alarm["createTime"]) > datetime.timedelta(seconds=_getDelay(alarm["typeId"])):
			_alarm(alarm) 
			remove.append(a)
			
	for r in remove:
		del g_delayAlarm[r]
	remove.clear()
	
	for a in g_delayClear:	
		alarm = g_delayClear[a]
		if now - alarm["clearTime"] > datetime.timedelta(seconds=_getDelay(alarm["typeId"],isClear=True)):
			_clear(alarm)
			remove.append(a)
	for r in remove:
		del g_delayClear[r]	 

#############################	unit test	########################### 
	
def test_delay():
	import re
	now = utility.now()
	utility.set_now(now)
	id = -798654654 
	db.delete_many("r_alarm",{"moid":re.compile("^test")}) 
	db.delete_many("r_alarm_history",{"moid":re.compile("^test")}) 
	db.delete_one("c_alarm_type",{"_id":id})  
	db.insert("c_alarm_type",{"_id":id,"value":"testalarmtype","raiseWait":20,"clearWait":10,"level":"critical"}) 
	global g_delayInfo 
	g_delayInfo = None
	data = _loadDelay()
	assert len(data)  
	assert data[2001][0] == 0
	assert data[2001][1] == 0
	assert data[2005][0] == 0
	assert data[2005][1] == 0
	assert data[id][0] == 20
	assert data[id][1] == 10
	alarm("testdelay",id,"this is a test")
	assert not check_alarm("testdelay",id)
	now = now+datetime.timedelta(seconds=15)
	mytimer.set_pass_ticks(15000)
	utility.set_now(now)
	time.sleep(1.5)
	
	assert not check_alarm("testdelay",id)
	alarm("testdelay",id,"this is a test")
	now = now+datetime.timedelta(seconds=15)
	utility.set_now(now) 
	mytimer.set_pass_ticks(15000)
	time.sleep(1.5)
	assert check_alarm("testdelay",id)
	
	alarm("testdelay",id,"this is a test")
	mytimer.set_pass_ticks(1000)
	time.sleep(1.5)
	assert check_alarm("testdelay",id)
	
	clear("testdelay",id)
	now = now+datetime.timedelta(seconds=5)
	mytimer.set_pass_ticks(5000)
	utility.set_now(now) 
	time.sleep(1.5)
	assert not db.find_one("r_alarm_history",{"moid":"testdelay","typeId":id})
	assert db.find_one("r_alarm",{"moid":"testdelay","typeId":id})
	
	clear("testdelay",id)
	now = now+datetime.timedelta(seconds=8)
	mytimer.set_pass_ticks(8000)
	utility.set_now(now) 
	time.sleep(1.5)
	assert db.find_one("r_alarm_history",{"moid":"testdelay","typeId":id})
	assert not db.find_one("r_alarm",{"moid":"testdelay","typeId":id})
	
	alarm("testdelay",id,"this is a test")
	clear("testdelay",id)
	now = now+datetime.timedelta(seconds=12)
	mytimer.set_pass_ticks(12000)
	utility.set_now(now) 
	time.sleep(1.5)
	assert db.find_one("r_alarm_history",{"moid":"testdelay","typeId":id})
	assert not db.find_one("r_alarm",{"moid":"testdelay","typeId":id})
	
	db.delete_one("c_alarm_type",{"_id":id})  
	db.delete_many("r_alarm",{"moid":re.compile("^test")}) 
	db.delete_many("r_alarm_history",{"moid":re.compile("^test")}) 
	utility.set_now(None)
	

	
def test_alarm_repeat():
	import re
	db.delete_many("r_alarm",{"moid":re.compile("^test")}) 
	db.delete_many("r_alarm_history",{"moid":re.compile("^test")}) 
	 
	for i in range(300): 
		alarm("testalarm.gggggg",2005,"test alarm2")
		assert check_alarm("testalarm.gggggg",2005)
	assert 1==db.find("r_alarm",{"moid":"testalarm.gggggg","typeId":2005}).count
	
	#描述是可以改的 
	alarm("testalarm.gggggg",2005,"test alarm3333")
	assert "test alarm3333" ==db.find_one("r_alarm",{"moid":"testalarm.gggggg","typeId":2005})["desc"]
	
	db.delete_many("r_alarm",{"moid":re.compile("^test")}) 
	db.delete_many("r_alarm_history",{"moid":re.compile("^test")}) 
	
def test_alarm():
	def getAlarm():
		ds = db.find("r_alarm")
		ds.leftjoin("typeId","c_alarm_type")
		return ds.list()
	
	
	def getHistory():
		ds = db.find("r_alarm_history")
		ds.leftjoin("typeId","c_alarm_type")
		return ds.list()
	
	import re
	db.delete_many("r_alarm",{"moid":re.compile("^test")}) 
	db.delete_many("r_alarm_history",{"moid":re.compile("^test")}) 
	
	alarm("testalarm",2004,"test alarm1")
	alarm("testalarm",2005,"test alarm2")
	
	count = 0
	data = getAlarm()	
	for a in data:
		if a["moid"] == "testalarm" and a["typeId"] == 2004:	
			assert a["desc"] == "test alarm1"
			count+=1
		if a["moid"] == "testalarm" and a["typeId"] == 2005:	
			assert a["desc"] == "test alarm2"
			count+=1
	assert count == 2
	
	assert check_alarm("testalarm",2004)
	assert check_alarm("testalarm",2005)
	assert not check_alarm("testalarm",2006) 
	clear("testalarm",2004)
	assert not check_alarm("testalarm",2004)
	assert check_alarm("testalarm",2005)
	assert db.find_one("r_alarm_history",{"moid":"testalarm","typeId":2004,"desc":"test alarm1"})
	assert not db.find_one("r_alarm_history",{"moid":"testalarm","typeId":2005,"desc":"test alarm2"})
	
	clear("testalarm",2005)
	assert not check_alarm("testalarm",2005)
	assert db.find_one("r_alarm_history",{"moid":"testalarm","typeId":2005,"desc":"test alarm2"})
	
	count = 0
	data = getAlarm()	
	for a in data:
		if a["moid"] == "testalarm" and a["typeId"] == 2004:	
			count+=1
		if a["moid"] == "testalarm" and a["typeId"] == 2005:	
			count+=1
		assert a["createTime"] is not None
		assert "clearTime" not in a
	assert count == 0
	
	count = 0
	data = getHistory()	
	 
	for a in data:
		if a["moid"] == "testalarm" and a["typeId"] == 2004:	
			assert a["desc"] == "test alarm1"
			count+=1
		if a["moid"] == "testalarm" and a["typeId"] == 2005:	
			assert a["desc"] == "test alarm2"
			count+=1
		assert a["createTime"] is not None
		assert a["clearTime"] is not None
	assert count == 2
	
	db.delete_many("r_alarm",{"moid":re.compile("^test")}) 
	db.delete_many("r_alarm_history",{"moid":re.compile("^test")}) 
	
if __name__ == '__main__': 
	#utility.start()
	auth.authApi.g_domain = "ycat"
	utility.run_tests()
	# utility.finish()
	
	
		