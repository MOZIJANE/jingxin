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
import enhance
import utility
import mytimer
import lock as lockImp
import mongodb as db
import taskMgr
import agvCtrl.agvApi as agvApi
import agvDevice.rollerApi as rollerApi
# import remoteio.remoteioApi as ioApi
# native方式调度io
import remoteio.remoteioMgr as remoteioMgr

TASKLEN = 4
OUT1 = 1
OUT2 = 2
INT2 = 1
INT4 = 3
FLOOR1 = 1
FLOOR2 = 2
g_taskType = {
	"load_1": {"type": "unload","floor": FLOOR1,"isNone": 0,"arrivedSignal": OUT1,"finishSignal": INT2},
	"load_2": {"type": "load","floor": FLOOR2,"isNone": 1,"arrivedSignal": OUT2,"finishSignal": INT4},
	"unload_1": {"type": "load","floor": FLOOR1,"isNone": 1,"arrivedSignal": OUT1,"finishSignal": INT2},
	"unload_2": {"type": "unload","floor": FLOOR2,"isNone": 0,"arrivedSignal": OUT2,"finishSignal": INT4},
	}

g_taskQueue = [] 
g_init = None
g_lock = threading.RLock()
g_slock = threading.RLock()
g_ioStatus = {}

@lockImp.lock(g_slock)
def onStatusChanged(io,values):
	global g_ioStatus
	g_ioStatus[io] = values
	
@lockImp.lock(g_slock)
def getStatus(io):
	global g_ioStatus
	if io in g_ioStatus:
		return g_ioStatus[io]

@lockImp.lock(g_lock)
def pushTask(device_name,taskType,taskInfo):
	global g_taskQueue,g_init
	if g_init is None:
		g_init = "akmTask"
		agvApi.init("akmTask")
		db.delete_many("u_agv_payload",'')
	task = akmTask(device_name,taskType,taskInfo)
	g_taskQueue.append(task)
	log.info('Got a task from akm %s:s %s'%(task.taskId, task))
	return task.taskId
	
#无任务时取下一个任务
@lockImp.lock(g_lock)
def getTask1():
	global g_taskQueue,r_task
	if g_taskQueue == []:
		return 
	for task in g_taskQueue:
		agvList = agvApi.getAgvStatusList(task.map)["list"]
		for id in agvList:
			if agvList[id]["isActive"]:#and not agvList[id]["charging"]:
				isAgvRight = task.filterFuncB(id, None, None, None, taskType=task.type,isOther=True)
				if isAgvRight:
					r_task.append(task)
					g_taskQueue.remove(task)
					return
	
#True为回Home点，False不回
@lockImp.lock(g_lock)
def getTask2(preId,preTask):
	global g_taskQueue,r_task
	if g_taskQueue == []:
		return True
	agvId = preTask.agvId
	for task in g_taskQueue:
		isAgvRight = task.filterFuncB(agvId, None,  None, None,taskType=task.type,isOther=True)
		if isAgvRight and task.line == preTask.line and task.loc1 == preTask.loc1:
			task.agvId = preTask.agvId
			r_task.append(task)
			g_taskQueue.remove(task)
			return False
	return True
	
r_count = 0 #正在执行任务数
r_task = [] #任务执行队列
r_taskId = []#正在执行任务id
@mytimer.interval(500) 
@lockImp.lock(g_lock)
def run():
	global g_taskQueue,r_count,r_task,r_taskId
	if r_count == 0 :
		getTask1()
	rTask = []
	for task in r_task:
		task.run()
		r_taskId.append(task.taskId)
		r_count = r_count + 1
	r_task = []
	rId = []
	for id in r_taskId:
		ret = taskMgr.get(id)
		if ret is None or ret["status"] in ["success","fail"]:
			rId.append(id)
	for id in rId:
		r_taskId.remove(id)
		r_count = r_count - 1
	
	
# type:
# load_1    上板机一层叫料
# load_2    上板机二层出空框
# unload_1  下板机一层出料
# unload_2  下板机二层进空框
class akmTask:
	def __init__(self,device_name,taskType,taskInfo):
		self.device_name = device_name
		self.type = taskType
		self.taskName = "%s执行任务%s"%(device_name,taskType)
		self.device_id = taskInfo["io"]
		self.loc1 = taskInfo["loc1"]
		self.loc2 = taskInfo["loc2"]
		self.map = taskInfo["map"]
		self.line = taskInfo["line"]
		self.task_io = g_taskType[self.type]
		self.s_lock = threading.RLock() # self.status
		self.taskId = taskMgr.add(self.taskName,taskType,loc1=self.loc1,loc2=self.loc2,device_id=self.device_id,line=self.line)
		self._taskThread = None
		self.taskRunning = False
		self.status = 0
		self.restartN = 0
		self.agvId = None
		
	def run(self):
		d_status = self._readIO(self.device_id)
		if self.type == "unload_2" or self.type == "load_2":
			if d_status[2] == 0:
				self._deal(failMsg="task cancel",isRelease=True)
				return
		if self.type == "unload_1" or self.type == "load_1":
			if d_status[0] == 0:
				self._deal(failMsg="task cancel",isRelease=True)
				return
		self._taskThread = threading.Thread(target=self._taskFunc)
		self._taskThread.start()
		
	def _taskFunc(self):
		self.taskRunning = True
		self.restartN = 0
		# self._writeIO(self.device_id,self.task_io["arrivedSignal"],0)
		taskMgr.start(self.taskId)
		self.param = {
			"taskId": self.taskId,
			"location": self.loc1,
			"floorId": self.map,
			"taskType": self.type
		}
		if self.agvId is None:
			self.agvId = self._callAgv(filterFunc=self.filterFuncB)
		taskMgr.update(self.taskId,agvId=self.agvId)
		self.param["location"] = self.loc1
		self.param["taskId"] = self.taskId+"_1"
		self._moveAgv()
		taskMgr.update(self.taskId,step="moveLoc1")
		while self.taskRunning :
			try:
				self.s_lock.acquire()
				if self.status == 1:
					self.status = 0
					self.s_lock.release()
					self.onHandle1()
					continue
				# elif self.status == 2:
					# self.status = 0
					# self.s_lock.release()
					# self.onHandle2()
					# continue
				self.s_lock.release()
				time.sleep(0.2)
			except Exception as e:
				log.exception("akmTask",e)
				self._writeIO(self.device_id,self.task_io["arrivedSignal"],0)
		
	def filterFuncB(self,agvId, floorId,  loc, payload,taskType=None,isOther=False):
		if taskType is None:
			taskType = self.type
		f = "floor%s"%taskType[-1]
		s = self.getAgvPayload(agvId)[f]
		s_1 = self.getUnitStatus(agvId,1,isOther=isOther)
		s_2 = self.getUnitStatus(agvId,2,isOther=isOther)
		log.warning(s,s_1,s_2)
		if taskType == "load_1" :
			if s == self.line and s_1 == 1:
				return True
		elif taskType == "load_2":
			if s is None and s_2 == 0:
				return True
		elif taskType == "unload_1":
			if s is None and s_1 == 0:
				return True
		elif taskType == "unload_2":
			if s == self.line and s_2 == 1:
				return True
		return False
		
	def onFinish(self,obj):
		self.s_lock.acquire()
		if obj["taskId"] == self.taskId+'_1':
			self.status = 1
		elif obj["taskId"] == self.taskId+'_2':
			self.status = 2
		self.s_lock.release()
		self.param = obj
		
	def onHandle1(self):
		if self.param["result"] is not True:
			if self.restartN < 3:
				self._moveAgv()
				taskMgr.update(self.taskId,step="moveLoc1",msg="moveLoc1Again")
				self.restartN = self.restartN + 1
				return
			self._deal(self.param["resultDesc"])
			return
		self.restartN = 0
		d_status = self._readIO(self.device_id)
		if self.type == "unload_2" or self.type == "load_2":
			if d_status[2] == 0:
				self._deal("task cancel",isRelease=True)
				return
		if self.type == "unload_1" or self.type == "load_1":
			if d_status[0] == 0:
				self._deal("task cancel",isRelease=True)
				return
		
		taskMgr.update(self.taskId,step="working")
		
		#有延迟，如果是load，滚筒先动作
		if self.task_io["type"] == "load":
			self.rollerFrontLoad(self.task_io["floor"]) 
		self._writeIO(self.device_id,self.task_io["arrivedSignal"],1) #到达信号
		if self.task_io["type"] == "unload":
			self.rollerFrontUnload(self.task_io["floor"]) 
		isFinish = False
		for i in range(600):
			d_status = self._readIO(self.device_id) #完成信号
			if d_status[self.task_io["finishSignal"]] and self.getUnitStatus(self.agvId,self.task_io["floor"]) == self.task_io["isNone"]:
				time.sleep(2)
				d_status = self._readIO(self.device_id) #完成信号
				if d_status[self.task_io["finishSignal"]] and self.getUnitStatus(self.agvId,self.task_io["floor"]) == self.task_io["isNone"]:
					self.updateAgvPayload()
					isFinish = True
					break
			time.sleep(0.5)
		self._writeIO(self.device_id,self.task_io["arrivedSignal"],0)
		time.sleep(5)
		self.rollerStop()
		if isFinish:
			taskMgr.update(self.taskId,step="workFinish")
			taskMgr.finish(self.taskId)
		else:
			taskMgr.update(self.taskId,step="work not finish")
			taskMgr.fail(self.taskId)
		
		if isFinish and getTask2(self.taskId,self):
			self._release()
			self._goHome()
		
		self.taskRunning = False
		self.taskId = None
		self.param = None
		
	def _checkCharge(self):
		s = self.getAgvPayload(self.agvId)
		try:
			if s["floor1"] or s["floor2"]:
				agvApi.setChargeState(self.agvId,False)
			else:
				agvApi.setChargeState(self.agvId,True)
		except Exception as e:
			log.exception("setChargeState failed",str(e))
		
	def _goHome(self):
		try:
			agvApi.goHome(self.agvId)
		except Exception as e:
			self._deal(str(e))
			raise e
		
	def _release(self):
		self._checkCharge()
		try:
			agvApi.release(self.agvId, self.taskId)
		except Exception as e:
			self._deal(str(e))
			raise e
		
	def _callAgv(self,filterFunc=None,timeOut=600):
		msg = None
		for i in range(0,timeOut+1):
			try:
				agvId = agvApi.apply(taskId=self.param["taskId"],mapId=self.param["floorId"],loc=self.param["location"],  filterFunc=filterFunc)
				return agvId
			except Exception as e:
				time.sleep(0.1)
				msg = e
				log.exception("taskId[%s] apply agv "%self.taskId,e)
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
	
	def _readIO1(self,io):
		for i in range(4):
			try:
				s = self._nativeReadDI(io)
				if s is None:
					raise Exception("task: ",self.taskId,"readIo failed ")
				return s
			except Exception as e:
				log.exception("readIo",e)
				if i == 2:
					self._deal(str(e))
					raise e
			time.sleep(0.1)
			
	def _readIO(self,io):
		for i in range(10):
			try:
				s = getStatus(io)
				if s is None:
					raise Exception("task: ",self.taskId,"readIo failed ")
				log.info(self.taskId,self.device_id,"readIo get status",s)
				return s
			except Exception as e:
				log.exception("readIo",e)
				if i == 9:
					self._deal(str(e))
					raise e
			time.sleep(0.5)
			
	def _readDO(self,io):
		while True:
			try:
				s = self._nativeReadDO(io)
				if s is None:
					raise Exception("task: ",self.taskId,"readDo failed ")
				return s
			except Exception as e:
				log.exception("readDo",e)
			time.sleep(1)
		
	def _writeIO(self,io,id,value):
		while True:
			try:
				self._nativeWriteIo(io,id,value)
				time.sleep(1)
				s = self._readDO(io)
				if s[id-1] == value:
					break
				else:
					raise Exception("task: ",self.taskId,"writeIo failed ")
			except Exception as e:
				log.exception("writeIo",e)
			time.sleep(1)
		
	def getAgvPayload(self,agvId):
		ds = db.find_one("u_agv_payload",{"_id": agvId})
		if ds is None:
			return {"floor1": None,"floor2": None}
		return {"floor1": ds["floor1"] if "floor1" in ds else None,"floor2": ds["floor2"] if "floor2" in ds else None}
		
	def updateAgvPayload(self):
		f = "floor%s"%self.type[-1]
		# s_1 = self.getUnitStatus(agvId,1)
		# s_2 = self.getUnitStatus(agvId,2)
		if self.type == "load_1" :#and s_1 == 0:
			db.update_one("u_agv_payload",{"_id": self.agvId},{"floor1": None},update_or_insert=True)
		elif self.type == "load_2" :#and s_2:
			db.update_one("u_agv_payload",{"_id": self.agvId},{"floor2": self.line},update_or_insert=True)
		elif self.type == "unload_1" :#and s_1:
			db.update_one("u_agv_payload",{"_id": self.agvId},{"floor1": self.line},update_or_insert=True)
		elif self.type == "unload_2" :# and s_2 == 0:
			db.update_one("u_agv_payload",{"_id": self.agvId},{"floor2": None},update_or_insert=True)
		
	def getUnitStatus(self,agvId,unitId,isOther=False):
		try:
			return rollerApi.unitStatus(agvId,unitId)["status"]
		except Exception as e:
			if isOther:
				return -1
			self._deal(str(e))
			raise e
		
	def rollerFrontLoad(self,unitId):
		try:
			if self.agvId:
				rollerApi.rollerFrontLoad(self.agvId,unitId)
		except Exception as e:
			log.exception("%s %s rollerFrontLoad failed"%(self.agvId,self.taskId),str(e))
			self._deal(str(e))
			raise e
			
	def rollerFrontUnload(self,unitId):
		try:
			if self.agvId:
				rollerApi.rollerFrontUnload(self.agvId,unitId)
		except Exception as e:
			log.exception("%s %s rollerFrontUnload failed"%(self.agvId,self.taskId),str(e))
			self._deal(str(e))
			raise e
		
	def rollerStop(self,isOther=False):
		try:
			if self.agvId:
				rollerApi.rollerStop(self.agvId)
		except Exception as e:
			log.exception("%s %s rollerStop failed"%(self.agvId,self.taskId),str(e))
			if not isOther:
				self._deal(str(e))
				raise e
		
	def _deal(self,failMsg,isRelease=False):
		taskMgr.fail(self.taskId,failMsg=failMsg)
		try:
			self._writeIO(self.device_id,self.task_io["arrivedSignal"],0)
			self.rollerStop(isOther=True)
			if self.agvId and isRelease:
				self._release()
				self._goHome()
		except Exception as e:
			log.exception("%s deal error: "%self.taskId,str(e))
		self.taskRunning = False
		self.taskId = None
		self.param = None


	def _nativeReadDI(self, io):
		remoteioInfo = remoteioMgr.get(io)
		result = remoteioInfo.readDIList()
		return result

	def _nativeReadDO(self, io):
		remoteioInfo = remoteioMgr.get(io)
		result = remoteioInfo.readDOList()
		return result

	def	_nativeWriteIo(self,io, index, value):
		remoteioInfo = remoteioMgr.get(io)
		remoteioInfo.writeDO(index, value)
################ UNIT TEST ###########

	
if __name__ == "__main__":
	utility.start()
	
