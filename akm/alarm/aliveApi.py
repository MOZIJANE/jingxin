#coding=utf-8 
# ycat        2018/07/29      create
import sys,os
import datetime
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import enhance
import utility
import log 
import mytimer
import alarm.alarmApi

# 用于对象存活性判断，不存活的情况会自动发送告警 
class aliveObj:
	def __init__(self,moid,typeId,desc,timeoutSecond,domain=None):
		self.moid = moid
		self.typeId = typeId
		self.desc = desc
		self.domain = domain
		self.timeoutMillisecond = timeoutSecond*1000
		self.inactiveEvent = enhance.event() #对象变为非活动事件 
		self.activeEvent = enhance.event()   #对象变为活动的事件 
		self.lastCheck = utility.ticks()
		self.alarmState = -1
		self.timerId = mytimer.g_timer.setInterval(self._checkTimeout,5000)
		log.debug("create aliveObj",moid,desc,"timeout",timeoutSecond) 
	
	def __del__(self):
		if mytimer.g_timer and self.timerId:
			self.close()
		
	def close(self):
		mytimer.g_timer.remove(self.timerId)
	
	def isActive(self):
		return self.alarmState == 0
	
	def check(self): 
		self.lastCheck = utility.ticks()
		self._clear() 
	
	def _checkTimeout(self):
		if utility.ticks() - self.lastCheck > self.timeoutMillisecond:
			self._alarm()
		else:
			self._clear()
	
	def _clear(self):
		if self.alarmState == 0:
			return
		alarm.alarmApi.clear(moid=self.moid,typeId=self.typeId,domain=self.domain)
		self.activeEvent.emit(self.moid)
		self.alarmState = 0
		
	def _alarm(self):
		if self.alarmState == 1:
			return
		alarm.alarmApi.alarm(moid=self.moid,typeId=self.typeId,desc=self.desc,domain=self.domain)
		self.inactiveEvent.emit(self.moid)
		self.alarmState = 1
		#log.warning(self.moid,"is inactive")
	
	
#############################	unit test	########################### 
def test_alarm():
	import re,mongodb as db
	db.delete_many("r_alarm",{"moid":re.compile("^ycat_unittest")}) 
	db.delete_many("r_alarm_history",{"moid":re.compile("^ycat_unittest")}) 
	
	import time
	myMoid = enhance.empty_class()
	myMoid.count = 0
	def callback(myMoid,type,moid):
		myMoid.moid = moid
		myMoid.type = type
		myMoid.count += 1 
		
	o = aliveObj("ycat_unittest",20999,"姚舜的单元测试",timeoutSecond=3)
	o.activeEvent.connect(enhance.bind(callback,myMoid,"active"))
	o.inactiveEvent.connect(enhance.bind(callback,myMoid,"inactive"))
	o.check()
	assert myMoid.count == 1
	assert o.isActive()
	time.sleep(1)
	o.check()
	assert myMoid.count == 1
	time.sleep(6)
	assert myMoid.count == 2
	assert myMoid.type == "inactive"
	assert not o.isActive()
	assert alarm.alarmApi.check_alarm("ycat_unittest",20999) 
	o.check()
	assert myMoid.count == 3
	assert myMoid.type == "active"
	assert not alarm.alarmApi.check_alarm("ycat_unittest",20999) 
	assert o.isActive()
	for i in range(6):
		time.sleep(1)
		o.check()
	assert myMoid.count == 3
	assert not alarm.alarmApi.check_alarm("ycat_unittest",20999) 
	assert o.isActive()
	db.delete_many("r_alarm",{"moid":re.compile("^ycat_unittest")}) 
	db.delete_many("r_alarm_history",{"moid":re.compile("^ycat_unittest")}) 
	
if __name__ == '__main__': 
	import auth.authApi
	auth.authApi.g_domain = "ycat" 
	utility.run_tests()
	utility.finish()
	
	
	
		