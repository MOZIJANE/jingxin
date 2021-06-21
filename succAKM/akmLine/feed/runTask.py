# coding: utf-8
# author: pengshuqin
# date: 2019-04-15
# desc: agv调度

import os
import sys
import time
import json
import threading

import setup
if __name__ == "__main__":
	setup.setCurPath(__file__)
	
import log
import taskApi
import agvCtrl.agvApi as agvApi
import agvDevice.jackApi as jackApi
import agvDevice.rotationApi as rotationApi
import enhance
import mongodb as db
import lock as lockImp
import socket
import local

proName = local.get("project","name")

def _loadAgvList():
	file = "/../agvCtrl/projects/"+proName+"/" + local.get("project","agvcfg")  
	with open(os.path.abspath(os.path.dirname(__file__) + file), 'r') as f:		
		agvList = {}
		aa = json.load(f)
		for a in aa:
			if aa[a]["enable"].lower() == "false":
				continue
			agvList[a] = aa[a]
		return agvList
g_agvList = _loadAgvList()

# 先移动至LM1,执行顶升，移动至LM2,执行下降，回home点
# param 
# "source": "LM1", 
# "target": "LM2", 
# "floorId": "test",
# "taskName": "在地图floorId中，从source点运送material到target点",
# "taskType": "feed"
finishEvent = enhance.event()
g_init = None
def _init():
	global g_init 
	if g_init is None:
		g_init = "feed"
		agvApi.init("scadaTask")
	
def feedTask(param):
	_init()
	t_task = feed(param)
	t_task.run()
	log.info('Got a task from feed %s:s %s'%(t_task.taskId, t_task))
	return t_task.taskId


#格式化地图上的点
def formatLoc(mapId,loc):
	if mapId and loc.find(".") == -1:
		return mapId + "." + loc
	return loc

class feed:
	def __init__(self,param):
		param["taskType"] = "feed"
		self.param = param
		self.status = 0
		self.restartN = 0
		self.isRunning = False
		self.s_lock = lockImp.create("feed.s_lock")
		self.s_info = None
		self.t_info = None
		
		self._load(param)
		self.param["taskName"] = "PDA: 从%s运送货架%s到%s"%(self.param["seat1"],self.s_info["payloadId"],self.param["seat2"])
		self.taskId = taskApi.add(taskName=self.param["taskName"],taskType="feed",msg="创建任务：%s"%self.param["taskName"])
		
		self._taskThread = threading.Thread(target=self._taskFunc)
		# if param["seat1"]:
			# self._taskThread = threading.Thread(target=self._taskFunc)
		# else:
			# param["taskName"] = "运送货架到地图%s,%s工位"%(param["floorId2"],param["seat2"])
			# taskApi.update(self.taskId, taskName=param["taskName"])
			# self._taskThread = threading.Thread(target=self._taskFuncSingle)
		
	def _load(self,param):
		ds = db.find("u_loc_info",{"_id": {"$in": [param["seat1"],param["seat2"]]}})
		while ds.next():
			if ds["_id"] == param["seat1"]:
				self.s_info = {
						"prepoint": ds["prepoint"],
						"location": ds["location"],
						"floorId": ds["floorId"],
						"direction": ds["direction"],
						"payloadId": ds["payloadId"],
						"p_direction": ds["p_direction"]
					}
			elif ds["_id"] == param["seat2"]:
				self.t_info = {
						"prepoint": ds["prepoint"],
						"location": ds["location"],
						"floorId": ds["floorId"],
						"direction": ds["direction"],
						"payloadId": ds["payloadId"],
						"p_direction": ds["p_direction"]
					}
		if self.s_info is None and self.t_info is None:
			raise Exception("can't find source-%s and target-%s info"%(param["seat1"],param["seat2"]))
		elif self.s_info is None:
			raise Exception("can't find source-%s info"%param["seat1"])
		elif self.t_info is None:
			raise Exception("can't find target-%s info"%(param["seat2"]))
		
	def run(self):
		if not self.isRunning:
			self.restartN = 0
			self.isRunning = True
			self._taskThread.start()
		
	def _taskFunc(self):
		self.param["location"] = self.param["location1"]
		self.param["taskId"] = self.taskId
		self.agvId = self._callAgv()
		self.param["taskId"] = "P"+self.taskId + "_1"
		self.param['isRotate'] = ''
		# self.param["operation"] = "JackLoad"
		# self.param["recognize"] = False
		# check jackdown
		self._jackDown()
		self._rotationClear()
		self._moveJackup()
		taskApi.update(self.taskId, status=taskApi.taskStatus.working.value, msg=self.agvId + "前往起始点" + self.param["location1"])
		
		while self.isRunning:
			time.sleep(0.2)
			lockImp.acquire(self.s_lock)
			if self.status == 1:
				self.status = 0
				lockImp.release(self.s_lock)
				self.onHandle1()
				continue
			elif self.status == 2:
				self.status = 0
				lockImp.release(self.s_lock)
				self.onHandle2()
				continue
			elif self.status == 3:
				self.status = 0
				lockImp.release(self.s_lock)
				self.onHandle3()
				break
			lockImp.release(self.s_lock)
			time.sleep(0.2)
	
	def onFinish(self,obj):
		lockImp.acquire(self.s_lock)
		if obj["location"] == obj["location1"]:
			self.status = 1
		elif obj["location"] == self.t_info['prepoint']:
			self.status = 2
		elif obj["location"] == obj["location2"]:
			self.status = 3
		lockImp.release(self.s_lock)
		self.param = obj
		
	def onHandle1(self):
		if self.param["result"] is not True:
			self._deal2('前往起始点异常')
			return

		taskApi.update(self.taskId, status=taskApi.taskStatus.working.value, msg=self.agvId + "到达起始点" + self.param["location1"])
		self.param["direction"] = self.t_info["direction"]
		self.param["taskId"] = "P"+self.taskId + "_2"
		
		try:
			self.restartN = 0
			self._jackUp()
		except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
			while self.restartN < 5:
				self.restartN += 1
				if not self._jackUp():
					continue
				self.restartN = 0
				break


		# self._jackUp()
		self.param["location"] = self.t_info['prepoint']
		self.param["floorId"] = self.t_info["floorId"]
		self._moveAgv()
		taskApi.update(self.taskId, status=taskApi.taskStatus.working.value, msg=self.agvId + "前往目标前置点" + self.t_info['prepoint'])

	def onHandle2(self):
		if self.param["result"] is not True:
			self._deal2('前往目标前置点异常')
			return
		self.restartN = 0

		# 转角度 
		try:
			self._rotation()
		except Exception as e:
			log.debug(f'{self.agvId} rotate error in feed:',e)

		self.param["location"] = self.t_info['location']
		self.param["taskId"] = "P"+self.taskId + "_3"
		self._moveJackdown()
		taskApi.update(self.taskId, status=taskApi.taskStatus.working.value, msg=self.agvId + "前往目标点" + self.param["location2"])

	def onHandle3(self):
		if self.param["result"] is not True:
			self._deal('前往目标点异常')
			return
		
		taskApi.update(self.taskId, status=taskApi.taskStatus.working.value, msg=self.agvId + "到达目标点" + self.param["location2"])

		try:
			self.restartN = 0
			self._jackDown()
		except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
			while self.restartN < 5:
				self.restartN += 1
				if not self._jackUp():
					continue
				self.restartN = 0
				break
			
		# self._jackDown()
		# 角度归位
		try:
			rotationApi.rotationClear(self.agvId)
		except Exception as e:
			log.debug(f'{self.agvId} rotate reset error in feed:',e)

		taskApi.finish(self.taskId, msg="成功")
		self._release()
		self._goHome()
	
	def _rotation(self):  
		# 转角度  
		log.debug(str(self),self.agvId,"rotate",self.s_info['p_direction'], "->",self.t_info['p_direction'])
		if self.s_info['p_direction'] == self.t_info['p_direction']: 
			return True
		angle = self.t_info['p_direction'] - self.s_info['p_direction']
		self.param["isRotate"] = str(angle)
		log.debug(self.agvId, 'Rotate:',self.param['isRotate']) 

		if hasattr(g_agvList[self.agvId], 'io') and g_agvList[self.agvId].io == "True":
			if abs(angle) == 180:
				return self._rotationRight(180)
			elif angle == -90:
				return self._rotationLeft(90)
			elif angle == 270:
				return self._rotationRight(270)
			elif angle == -270 or angle == 90:
				return self._rotationRight(90)
			else:
				log.error("unknow angle",angle,self.agvId)
		else:
			if abs(angle) == 180:
				return self._rotationRight(180)
			elif angle == 270 or angle == -90:
				return self._rotationLeft(90)
			elif angle == -270 or angle == 90:
				return self._rotationRight(90)
			else:
				log.error("unknow angle",angle,self.agvId)
	
	# only target workplace logic 
	def _taskFuncSingle(self):
		self.param["location"] = self.t_info['prepoint']
		self.param["taskId"] = self.taskId
		self.agvId = self._callAgv()
		self.param["taskId"] = "P"+self.taskId + "_1"
		self.param['isRotate'] = ''
		self._jackDown()
		self._rotationClear()
		self._moveAgvSingle()
		taskApi.update(self.taskId, status=taskApi.taskStatus.working.value, msg=self.agvId + "前往起始点" + self.t_info['prepoint'])
		
		while self.isRunning:
			lockImp.acquire(self.s_lock)
			if self.status == 1:
				self.status = 0
				lockImp.release(self.s_lock)
				self.handle1()
				continue
			elif self.status == 2:
				self.status = 0
				lockImp.release(self.s_lock)
				self.handle2()
				break
			lockImp.release(self.s_lock)
			time.sleep(0.2)
	
	def onFinishSingle(self,obj):
		lockImp.acquire(self.s_lock)
		if obj["location"] == self.t_info['prepoint']:
			self.status = 1
		elif obj["location"] == obj["location2"]:
			self.status = 2
		lockImp.release(self.s_lock)
		self.param = obj
	
	def _moveAgvSingle(self, timeOut=1800):
		try:	
			self.param["timeoutSec"] = timeOut
			if "seer_jackup" in self.param:
				del self.param["seer_jackup"]
			agvApi.move(self.agvId, self.param["location"], self.onFinishSingle, self.param)
		except Exception as e:
			self._deal(str(e))
			raise e
			
	def _moveJackdownSingle(self, timeOut=1800):
		try:	
			self.param["timeoutSec"] = timeOut
			agvApi.moveJackdown(self.agvId, self.param["location"], self.onFinishSingle, self.param)
		except Exception as e:
			self._deal(str(e))
			raise e

	def handle1(self):
		if self.param["result"] is not True:
			self._deal2("前往起始点异常")
			return
		self.restartN = 0
	
		# 转角度 
		try:
			if self.param['direction'] == 90:
				self.param['isRotate'] = '90'
				self._rotationRight()  
			elif self.param['direction'] == -90:
				self.param['isRotate'] = '-90'
				self._rotationLeft() 
			elif self.param['direction'] == 180:
				self.param['isRotate'] = '180'
				self._rotationRight(180) 
			taskApi.update(self.taskId, status=taskApi.taskStatus.working.value, msg=self.agvId + "转角度" + self.param['isRotate'])
		except Exception as e:
			log.debug(f'{self.agvId} rotate error in feed:',e)

		self.param["location"] = self.t_info['location']
		self.param["taskId"] = "P"+self.taskId + "_2"
		self._moveJackdownSingle()
		taskApi.update(self.taskId, status=taskApi.taskStatus.working.value, msg=self.agvId + "前往目标点" + self.param["location2"])

	def handle2(self):
		if self.param["result"] is not True:
			self._deal("前往目标点异常")
			return
		
		taskApi.update(self.taskId, status=taskApi.taskStatus.working.value, msg=self.agvId + "到达目标点" + self.param["location2"])

		self._jackDown()
		# 角度归位
		try:
			rotationApi.rotationClear(self.agvId)
			taskApi.update(self.taskId, status=taskApi.taskStatus.working.value, msg=self.agvId + "角度归位" + self.param['isRotate'])
		except Exception as e:
			log.debug(f'{self.agvId} rotate reset error in feed:',e)
		
		taskApi.finish(self.taskId, msg="成功")
		self._release()
		self._goHome()
		
	def _callAgv(self,timeOut=300):
		msg = None
		for i in range(1,timeOut+1):
			try:
				self.agvId = agvApi.apply(taskId=self.taskId,mapId=self.param["floorId"],loc=self.param["location"], filterFunc=self._filterFunc)
				taskApi.update(self.taskId, agvId=self.agvId, msg="成功分配小车%s"%self.agvId)
				return self.agvId
			except Exception as e:
				time.sleep(1)
				msg = e
				log.warning("taskId[%s] apply agv %s failed: %s"%(self.taskId,i,str(e)))
		if str(msg) == "":
			msg = Exception("taskId[%s] apply agv failed"%self.taskId)
		taskApi.fail(self.taskId,msg=str(msg))
		raise msg



	# 过滤某些工位 如果不是04车 agvapi那里加入exclude
	def _filterFunc(self, agvId, mapId, loc, payload):
		L_RACK = ['fp20190712-1.AP286', 'fp20190712-1.AP287', 'fp20190712-1.AP1011', 'fp20190712-1.AP1080',
				  'fp20190712-1.AP1084', 'fp20190712-1.AP1078']   #L_RACK工位
		newAGV = ['AGV07',"AGV08",'AGV09',"AGV10"]   # 新装曲臂连杆的车不能进L_RACK工位
		t_loc = formatLoc(self.t_info["floorId"],self.t_info["location"])
		s_loc = formatLoc(mapId, loc)
		if s_loc in L_RACK or t_loc in L_RACK:
			if agvId in newAGV:
				return False
		return True

			
	def _moveAgv(self, timeOut=86400):
		try:	
			self.param["timeoutSec"] = timeOut
			if "seer_jackup" in self.param:
				del self.param["seer_jackup"]
			agvApi.move(self.agvId, self.param["floorId"]+'.'+self.param["location"], self.onFinish, self.param)
		except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
			# self._deal(str(e))
			raise e
	
	def _moveJackup(self, timeOut=86400):
		try:	
			self.param["timeoutSec"] = timeOut
			agvApi.moveJackup(self.agvId, self.param["floorId"]+'.'+self.param["location"], self.onFinish, self.param, use_pgv=False)
		except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
			# self._deal(str(e))
			raise e
			
	def _moveJackdown(self, timeOut=86400):
		try:	
			self.param["timeoutSec"] = timeOut
			agvApi.moveJackdown(self.agvId, self.param["floorId"]+'.'+self.param["location"], self.onFinish, self.param)
		except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
			# self._deal(str(e))
			raise e
	
	def _rotationReset(self):
		for i in range(3):
			try:
				rotationApi.rotationReset(self.agvId)
				return
			except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
				if i == 2:
					self._dealEx2(str(e))
					raise e
				time.sleep(1)
	
	def _rotationClear(self):
		try:
			rotationApi.rotationClear(self.agvId)
			return
		except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
			log.debug(f'{self.agvId} rotate clear error', e) 
			# self._dealEx2(str(e))
			raise e
			time.sleep(1)
	
	def _rotationLeft(self,target=90):
		try:
			rotationApi.rotationLeft(self.agvId,target=target)
			return
		except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
			log.debug(f'{self.agvId} rotate left {target} error', e) 
			# self._dealEx2(str(e))
			raise e
			time.sleep(1)
	
	def _rotationRight(self,target=90):
		try:
			rotationApi.rotationRight(self.agvId,target=target)
			return
		except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
			log.debug(f'{self.agvId} rotate right {target} error', e)
			# self._dealEx2(str(e))
			raise e
			time.sleep(1)
	
	def _jackUpOld(self,timeOut=5, delLoc=None):
		try:
			jackApi.jackUpOld(self.agvId, timeOut)
			return
		except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
			# self._deal(str(e))
			raise e

	def _goHome(self):
		#TODO
		# self._jackDown(self.param)
		agvApi.goHome(self.agvId,force=False,timeout=0)
		
	def _release(self):
		agvApi.release(self.agvId, self.taskId)
	
	def _jackUp(self,timeOut=1800):
		try:	
			jackApi.jackUp(self.agvId, timeOut)
			# LM point status upload 
			# jackApi.jackUpOldLM(self.agvId, timeOut)
			#TODO 
			#jackApi direction
			return True
		except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
			# self._deal(str(e))
			raise
		except Exception as e:
			log.exception('%s jackup error:'%self.agvId,e)
			return False
		
	def _jackDown(self, timeOut=1800):
		try:	
			jackApi.jackDown(self.agvId, timeOut)
			#TODO 
			#jackApi direction
			return True
		except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
			# self._deal(str(e))
			raise
		except Exception as e:
			log.exception('%s jackdown error:'%self.agvId,e)
			return False
		
	def _deal(self,msg):
		taskApi.fail(self.taskId,msg=msg)
		self.isRunning = False
		
	def _deal2(self,msg):
		taskApi.fail(self.taskId,msg=msg)
		self._release()
		self.isRunning = False
		
	def _dealEx2(self,msg):
		taskApi.fail(self.taskId,msg=msg)
		self.isRunning = False
	
if __name__ == "__main__":
	param = [
		{
			"floorId": "testscada",
			"seat1": "ZZ-AI-DG-02",
			"location1": "LM35",
			"floorId1": "testscada",
			"direction1": 90,
			"seat2": "NC-TM-XG-01",
			"location2": "LM32",
			"floorId2": "testscada",
			"direction2": 90
		},
		{
			"floorId": "testscada",
			"seat1": "KL-DB-SG-01",
			"location1": "LM36",
			"floorId1": "testscada",
			"direction1": 90,
			"seat2": "NC-QC-DG-01",
			"location2": "LM41",
			"floorId2": "testscada",
			"direction2": 90
		},
		{
			"floorId": "testscada",
			"seat1": "NA-PT-SG-01",
			"location1": "LM42",
			"floorId1": "testscada",
			"direction1": 90,
			"seat2": "ZZ-AI-DG-02",
			"location2": "LM35",
			"floorId2": "testscada",
			"direction2": 90
		},
		{
			"floorId": "testscada",
			"seat1": "KL-PM-XG-01",
			"location1": "LM43",
			"floorId1": "testscada",
			"direction1": 90,
			"seat2": "KL-DB-SG-01",
			"location2": "LM36",
			"floorId2": "testscada",
			"direction2": 90
		}
	]
	for p in param:
		feedTask(p)
		# break
	while True:
		import time
		time.sleep(2)
