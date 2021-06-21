# coding: utf-8
# author: pengshuqin
# date: 2019-10-16
# desc: 任务处理

import os
import sys
import time
import datetime
import threading
from queue import PriorityQueue 

import setup

if __name__ == '__main__':
	setup.setCurPath(__file__)
	
import log
import utility
import mytimer
import lock as lockImp
import mongodb as db
import taskMgr
import agvCtrl.agvApi as agvApi
import agvDevice.rollerApi as rollerApi
import remoteio.remoteioApi as ioApi


g_taskQueue = PriorityQueue()
g_taskIdDict = {}
g_init = None
g_lock = threading.RLock()

@lockImp.lock(g_lock)
def pushTask(device_name,type,unitId,unitValue,wId,rId,taskInfo):
	global g_taskQueue,g_init
	if g_init is None:
		g_init = "akmTask"
		agvApi.init("akmTask")
	task = akmTask(device_name,type,unitId,unitValue,wId,rId,taskInfo)
	g_taskQueue.put(task)
	g_taskIdDict[task.taskId] = task
	log.info('Got a task from akm %s:s %s'%(task.taskId, task))
	return task.taskId
	
r_count = 0
r_task = []
@mytimer.interval(5000) 
@lockImp.lock(g_lock)
def run():
	global g_taskQueue,g_taskIdDict,r_count,r_task
	while r_count < 1 and not g_taskQueue.empty():
		task = g_taskQueue.get()
		r_task.append(task.taskId)
		r_count = r_count + 1
		task.run()
	r = []
	for id in r_task:
		ret = taskMgr.get(id)
		assert ret is not None
		if ret["status"] in ["success","fail"]:
			r.append(id)
	for id in r:
		del g_taskIdDict[id]
		r_task.remove(id)
		r_count = r_count - 1
	
class akmTask:
	def __init__(self,device_name,type,unitId,unitValue,wId,rId,taskInfo):
		self.device_name = device_name
		self.type = type
		self.unitId = unitId
		self.unitValue = unitValue
		self.wId = wId
		self.rId = rId
		self.loc1 = taskInfo["loc1"]
		self.loc2 = taskInfo["loc2"]
		self.home = taskInfo["home"]
		self.map = taskInfo["map"]
		self.s_lock = threading.RLock() # self.status
		self.taskId = taskMgr.add("%s工位%s,执行任务%s"%(self.device_name,self.loc1,type),type,unitId=unitId,wId=wId,rId=rId)
		self._taskThread = None
		self.taskRunning = False
		self.status = 0
		self.restartN = 0
		
	def run(self):
		self._taskThread = threading.Thread(target=self._taskFunc)
		self._taskThread.start()
		
	def _taskFunc(self):
		self.taskRunning = True
		self.restartN = 0
		
		taskMgr.start(self.taskId)
		self.param = {
			"taskId": self.taskId,
			"location": self.loc1,
			"floorId": self.map,
			"taskType": self.type
		}
		def filterFunc(agvId, floorId, taskType, loc, payload):
			if self.getUnitStatus(agvId,1) != 1 or self.getUnitStatus(agvId,2) != 0:
				return False
			return True
			
		self.agvId = self._callAgv(filterFunc=filterFunc)
		taskMgr.update(self.taskId,agvId=self.agvId)
		
		self.param["location"] = self.loc1
		self.param["taskId"] = self.taskId+"_1"
		self._moveAgv()
		taskMgr.update(self.taskId,step="moveLoc")
		self._writeIO(2,0)
		self._writeIO(1,0)
		while self.taskRunning :
			try:
				self.s_lock.acquire()
				if self.status == 1:
					self.status = 0
					self.s_lock.release()
					self.onHandle1()
					continue
				elif self.status == 2:
					self.status = 0
					self.s_lock.release()
					self.onHandle2()
					continue
				self.s_lock.release()
				time.sleep(0.2)
			except Exception as e:
				self._writeIO(1,0)
				self._writeIO(2,0)
				log.exception("akmTask",e)
	
	def onFinish(self,obj):
		self.s_lock.acquire()
		if obj["location"] == self.home:
			self.status = 2
		elif obj["location"] == self.loc1 or obj["location"] == self.loc2:
			self.status = 1
		self.s_lock.release()
		self.param = obj
		
	def onHandle1(self):
		if self.param["result"] is not True:
			if self.restartN < 3:
				self._moveAgv()
				taskMgr.update(self.taskId,step="moveLoc",msg="moveLocAgain")
				self.restartN = self.restartN + 1
				return
			self._deal(self.param["resultDesc"])
			return
		self.restartN = 0
		taskMgr.update(self.taskId,step="wait"+self.type)
		self._writeIO(1,1)
		self.rollerFrontUnload(1) #一层出料

		while True:
			d_status = self._readIO() #INT2进料完成  INT4出料完成
			if d_status[1] :
				break
			time.sleep(0.1)
		self._writeIO(1,0)
		
		self.rollerStop()
		
		g_unload = False
		for i in range(3):
			if self._readIO()[2] == 1:
				g_unload = True
				break
			time.sleep(0.1)
			
		if g_unload:
			self._writeIO(2,1)
			self.rollerFrontLoad(2)	#二层进框
			while True:
				d_status = self._readIO() #INT2进料完成  INT4出料完成
				if d_status[3] :
					break
				time.sleep(0.1)
			self._writeIO(2,0)
			self.rollerStop()
		
			
		taskMgr.update(self.taskId,step=self.type+"finish")
		self.param["location"] = self.home
		self.param["taskId"] = self.taskId+"_2"
		self._moveAgv()
		taskMgr.update(self.taskId,step="moveHome")
	
	def onHandle2(self):
		if self.param["result"] is not True:
			if self.restartN < 3:
				self._moveAgv()
				taskMgr.update(self.taskId,step="moveHome",msg="moveHomeAgain")
				self.restartN = self.restartN + 1
				return
			self._deal(self.param["resultDesc"])
			return
		taskMgr.finish(self.taskId)
		self._release()
		self.taskRunning = False
		self.taskId = None
		self.param = None
		
	def _goHome(self):
		agvApi.goHome(self.agvId)
		
	def _release(self):
		agvApi.release(self.agvId, self.taskId)
		
	def _callAgv(self,filterFunc=None,timeOut=600):
		msg = None
		for i in range(0,timeOut+1):
			try:
				agvId = agvApi.apply(loc=self.param["location"], mapId=self.param["floorId"], taskId=self.param["taskId"],filterFunc=filterFunc)
				return agvId
			except Exception as e:
				time.sleep(0.1)
				msg = e
				log.warning("taskId[%s] apply agv %s failed: %s"%(self.taskId,i,str(e)))
		if str(msg) == "":
			msg = Exception("taskId[%s] apply agv failed"%self.taskId)
		taskMgr.fail(self.taskId,failMsg=str(msg))
		raise msg
	
	def _moveAgv(self, timeOut=1200):
		try:
			self.param["timeoutSec"] = timeOut
			agvApi.move(self.agvId, self.param["location"], self.onFinish, self.param)
			return True
		except Exception as e:
			self._deal(str(e))
			raise e
	
	def _readIO(self):
		for i in range(3):
			try:
				return ioApi.readIo(self.device_name)["status"]
			except Exception as e:
				if i == 2:
					self._deal(str(e))
					raise e
				time.sleep(0.2)
		
	def _writeIO(self,id,value):
		for i in range(3):
			try:
				return ioApi.writeIo(self.device_name,id,value)
			except Exception as e:
				if i == 2:
					self._deal(str(e))
					raise e
				time.sleep(0.2)
		
	def getUnitStatus(self,agvId,unitId):
		try:
			return rollerApi.unitStatus(agvId,unitId)["status"]
		except Exception as e:
			self._deal(str(e))
			raise e
		
	def rollerFrontLoad(self,unitId):
		try:
			rollerApi.rollerFrontLoad(self.agvId,unitId)
		except Exception as e:
			self._deal(str(e))
			raise e
			
	def rollerFrontUnload(self,unitId):
		try:
			rollerApi.rollerFrontUnload(self.agvId,unitId)
		except Exception as e:
			self._deal(str(e))
			raise e
		
	def rollerStop(self):
		try:
			rollerApi.rollerStop(self.agvId)
		except Exception as e:
			self._deal(str(e))
			raise e
		
	def _deal(self,failMsg):
		taskMgr.fail(self.taskId,failMsg=failMsg)
		self._release()
		self._goHome()
		self.taskRunning = False
		self.taskId = None
		self.param = None
		
################ UNIT TEST ###########

	
if __name__ == "__main__":
	utility.start()
	
