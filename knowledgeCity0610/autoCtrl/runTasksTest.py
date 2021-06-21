# coding: utf-8
# author: pengshuqin
# date: 2019-10-16
# desc: 任务处理

import threading
import time

import setup

if __name__ == '__main__':
	setup.setCurPath(__file__)
	
import log
import utility
import taskMgr
from agvDevice import agvCtrl as agvApi
import agvDevice.rollerApi as rollerApi
import remoteio.remoteioApi as ioApi

g_init = None
def pushTask(device_name,task_info):
	task = akmTask(device_name,task_info)
	task.run()
	
class akmTask:
	def __init__(self,device_name,task_info):
		self.device_name = device_name
		self.loc1 = task_info["loc1"]
		self.loc2 = task_info["loc2"]
		self.home = task_info["home"]
		self.map = task_info["map"]
		self.s_lock = threading.RLock() # self.status
		self._taskThread = None
		self.taskRunning = False
		self.status = 0
		self.restartN = 0
		
	def run(self):
		self._taskThread = threading.Thread(target=self._taskFunc)
		self._taskThread.start()
		
	def initAgv(self):
		global g_init
		if g_init is None:
			g_init = "akmTask"
			agvApi.init("akmTask")
		
	def _taskFunc(self):
		time.sleep(10)
		while True :
			try:
				if not self.taskRunning:
					self.process("load",self.loc1,1,1,1,1)
					# d_status = self._readIO()
					# if d_status[0]:
						# if self.getUnitStatus(1) == 1:
							# self.process("load",self.loc1,1,1,1,1)	
							# continue
					# elif d_status[1]:
						# self.process("load",self.loc2,1,1,1,3)
					# if d_status[2]:
						# if self.getUnitStatus(2) == 0:
							# self.process("unload",self.loc1,2,0,2,3)	
							# continue
					# elif d_status[5]:
						# self.process("unload",self.loc2,2,0,3,7)
					# time.sleep(1)
					# continue
				
				self.s_lock.acquire()
				if self.status == 1:
					self.status = 0
					self.s_lock.release()
					# time.sleep(2)
					self.onHandle1()
					continue
				elif self.status == 2:
					self.status = 0
					self.s_lock.release()
					# time.sleep(2)
					self.onHandle2()
					continue
				self.s_lock.release()
				time.sleep(0.2)
			except Exception as e:
				log.exception("akmTask",e)
		
	#type: load unload
	#loc: 工位
	#unitId、unitValue: 上料有货架，下料无货架 1,1 一层有货架 2,0 二层无货架
	def process(self,type,loc,unitId,unitValue,wId,rId):
		self.initAgv()
		self.taskRunning = True
		self.restartN = 0
		self.taskId = taskMgr.add("%s工位%s,执行任务%s"%(self.device_name,loc,type),type,unitId=unitId,wId=wId,rId=rId)
		taskMgr.start(self.taskId)
		self.param = {
			"taskId": self.taskId,
			"location": loc,
			"floorId": self.map,
			"taskType": type,
			"unitId": unitId,
			"wId": wId,
			"rId": rId
		}
		self.agvId = self._callAgv()
		taskMgr.update(self.taskId,agvId=self.agvId)
		# if self.getUnitStatus(unitId) != unitValue:
			# self._deal("roller shelf status is not right")
			# return
		
		self.param["location"] = loc
		self.param["taskId"] = self.taskId+"_1"
		self._moveAgv()
		taskMgr.update(self.taskId,step="moveLoc")
		
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
		taskMgr.update(self.taskId,step="wait"+self.param["taskType"])
		# self._writeIO(self.param["wId"],1)
		
		# if self.param["taskType"] == "load":
			# self.rollerFrontUnload(self.param["unitId"])
		# else:
			# self.rollerFrontLoad(self.param["unitId"])
		
		# while True:
			# d_status = self._readIO()
			# if d_status[self.param["rId"]]:
				# break
			# time.sleep(1)
		# self._writeIO(self.param["wId"],0)
		taskMgr.update(self.taskId,step=self.param["taskType"]+"finish")
		# self.rollerStop()
		
		# if self.param["taskType"] == "unload":
		self.param["location"] = self.home
		self.param["taskId"] = self.taskId+"_2"
		self._moveAgv()
		taskMgr.update(self.taskId,step="moveHome")
		# else:
			# taskMgr.finish(self.taskId)
			# self._release()
			# self._goHome()
			# self.taskRunning = False
			# self.taskId = None
			# self.param = None
	
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
		
	def _callAgv(self,timeOut=600):
		msg = None
		for i in range(0,timeOut+1):
			try:
				agvId = agvApi.apply(loc=self.param["location"], mapId=self.param["floorId"], taskId=self.param["taskId"])
				return agvId
			except Exception as e:
				time.sleep(1)
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
		d_status = ioApi.readIo(self.device_name)["status"]
		return d_status
		
	def _writeIO(self,id,value):
		ioApi.writeIo(self.device_name,id,value)
		
	def getUnitStatus(self,unitId):
		try:
			return rollerApi.unitStatus("AGV01",unitId)["status"]
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
		self._release()
		self._goHome()
		self.taskRunning = False
		self.taskId = None
		self.param = None
		
################ UNIT TEST ###########

	
if __name__ == "__main__":
	utility.start()
	
