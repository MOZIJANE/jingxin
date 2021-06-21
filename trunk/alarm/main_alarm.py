#coding=utf-8 
# ycat			 2018/07/20      create
import sys,os,bottle
import pytest
import platform 
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import alarmApi 
import alarmMgr
import alarmForward
import alarmThreshold
import utility
import webutility
import scadaUtility 
import dbQuery.bigTable as bigTable
import mongodb as db
import meta as m
import config

def getLevel(level):
	if level == "critical":
		return "严重告警"
	elif level == "major":
		return "重要告警"
	elif level == "minor":
		return "轻微告警"
	elif level == "warning":
		return "警告"
	return "一般告警"
	
@bigTable.table("r_alarm","活动告警",dateRangeField="createTime",defaultSortId="createTime",defaultSortDir="desc")
@bigTable.leftjoin(table="c_alarm_type",selectColumn=["value","level"],localField="typeId",foreignField="_id")
@bigTable.field("moid","告警对象",searchable=True)
@bigTable.field("c_alarm_type.level","告警级别",searchable=False,formatFunc=getLevel)	#leftjoin出来的字段，是无法进行过滤的  
@bigTable.field("c_alarm_type.value","告警类型",searchable=False)	#leftjoin出来的字段，是无法进行过滤的  
@bigTable.field("desc","告警描述",searchable=True)
@bigTable.field("createTime","告警时间",searchable=False)
class r_alarm(bigTable.manager):
	def __init__(self):
		pass 
	
@bigTable.table("r_alarm_history","历史告警",dateRangeField="createTime",defaultSortId="createTime",defaultSortDir="desc")
@bigTable.leftjoin(table="c_alarm_type",selectColumn=["value","level"],localField="typeId",foreignField="_id")
@bigTable.field("moid","告警对象",searchable=True)
@bigTable.field("c_alarm_type.level","告警级别",searchable=False,formatFunc=getLevel)
@bigTable.field("c_alarm_type.value","告警类型",searchable=False)
@bigTable.field("desc","告警描述",searchable=True)
@bigTable.field("createTime","告警时间",searchable=False)
@bigTable.field("clearTime","清除时间",searchable=False)
class r_alarm_history(bigTable.manager):
	def __init__(self):
		pass 
		
typeSel = m.select(tableName="c_alarm_type",nameField="value")

tySel = m.select()
tySel.add("greater", "大于")
tySel.add("less", "小于")

@m.table("c_alarm_threshold","告警门限设置",domain=False)
@m.field(id="_id",name="id",visible=False,readonly=True)
@m.field(id="topic",name="mqtt主题", type=str,rules=[m.require()])
@m.field(id="moidpath",name="告警对象ID", type=str,rules=[m.require()])
@m.field(id="datapath",name="数据来源", type=str,rules=[m.require()])
@m.field(id="threshold",name="告警门限",type=float,rules=[m.require()])
@m.field(id="op",name="门限类别",type=str,editCtrl=tySel,rules=[m.require()])
@m.field(id="alarmTypeId",name="告警类型",type=str,editCtrl=typeSel)
class c_alarmthreshold(m.manager):
	def __init__(self):
		pass
		
tSel = m.select()
if config.getbool("mongo","enable",True):
	ds = db.find("c_alarm_type",{"visible": True})
	while ds.next():
		tSel.add(ds["_id"],ds["value"])
	
@m.table("u_alarm_forward","告警转发设置")
@m.field(id="_id",name="id",type=str,editCtrl=tSel,rules=[m.require()])
@m.field(id="isAlarm",name="告警转发", type=bool,default=True,rules=[m.require()])
@m.field(id="isClear",name="清除转发", type=bool,default=False,rules=[m.require()])
class u_alarmforward(m.manager):
	def __init__(self):
		pass
	
@scadaUtility.get('/api/alarm/count') 	
def urlAlarmCount():
	return {"data": {"alarmInfo": alarmMgr.getAlarmCount()}}
	
@scadaUtility.get('/api/alarm/levelInfo') 	
def urlAlarmLevelInfo():
	level = webutility.get_param("level")
	return {"data": {"alarms": alarmMgr.getAlarmInfo(level)}} 
	
@scadaUtility.get('/api/alarm/activeAlarm',cacheSecond=5)
def urlActiveAlarm():
	return {"alarmList": alarmMgr.getAlarm()}
	
#for uwsgi 
app = application = bottle.default_app()
webutility.add_ignore("alarm/count")
webutility.add_ignore("scada/activeAlarm")

if __name__ == '__main__':
	if webutility.is_bottle():
		utility.start()
	webutility.run()
else:
	utility.start()


