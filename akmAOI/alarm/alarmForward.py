import sys,os
import datetime
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import config
import utility
import mytimer
import log 
import mqtt
import mongodb as db

alarmType=config.get("alarmforward","type")
alarmCode=config.get("alarmforward","alarmcode")
clearCode=config.get("alarmforward","clearcode")

@mqtt.register("alarm/raise/+")
def receiveRaise(topic,data):
	global alarmCode
	topicList = topic.split("/")
	typeId = topicList[-1]
	domain = data["domain"]
	if domain in _loadInfo() and typeId in _loadInfo()[domain]: 
		if _loadInfo()[domain][typeId]["isAlarm"]:
			send(alarmCode,typeId,data,domain)
	
@mqtt.register("alarm/clear/+")
def receiveClear(topic,data):
	global clearCode
	topicList = topic.split("/")
	typeId = topicList[-1]
	domain = data["domain"]
	if domain in _loadInfo() and typeId in _loadInfo()[domain]: 
		if _loadInfo()[domain][typeId]["isClear"]:
			send(clearCode,typeId,data,domain)
	
def send(code,typeId,data,domain):
	global alarmType
	param = {"moid": data["moid"],"desc": data["desc"],"time": utility.now()}
	if alarmType == "sms":
		import sms.smsApi as smsApi
		smsApi.send(code,typeId,param,domain)
	
g_info = None
def _loadInfo():
	global g_info
	if g_info:
		return g_info
	return _load()

@mytimer.interval(timeoutMs=10000)
def _load():
	global g_info
	g_info = {}
	if not config.getbool("mongo","enable",True):
		return g_info
	ds = db.find("u_alarm_forward")
	while ds.next():
		if ds["domain"] not in g_info:
			g_info[ds["domain"]] = {}
		g_info[ds["domain"]][ds["_id"]] = {"isAlarm": ds["isAlarm"],"isClear": ds["isClear"]}
	return g_info
	
	
if __name__ == '__main__': 
	utility.run_tests()