# coding: utf-8
# author: pengshuqin
# date: 2019-05-08
# desc: 任务处理
import os
import sys
import time
import datetime
import threading
import socket
from queue import PriorityQueue 
import json as json2 
import setup

if __name__ == '__main__':
	setup.setCurPath(__file__)
import counter
import log
import enhance
import utility
import mytimer
import lock as lockImp
import mongodb as db
import taskMgr
import agvApi

import agvDevice.jackApi as jackApi
import agvDevice.pgvApi as pgvApi
import agvDevice.rotationApi as rotationApi
import json_codec as json 
import local 


# proName = "fastprint"
proName = "KLCity"


def _loadAgvList():
	file = "/../agvCtrl/projects/"+proName+"/" + local.get("project","agvcfg")
	with open(os.path.abspath(os.path.dirname(__file__) + file), 'r') as f:		
		agvList = {}
		aa = json2.load(f)
		for a in aa:
			if aa[a]["enable"].lower() == "false":
				continue
			agvList[a] = aa[a]
		return agvList
g_agvList = _loadAgvList()


def _getAgvType(agvId):
	type_ = g_agvList[agvId]["type"]
	return g_agvType[type_]

def _loadAgvType():
	proName = local.get("project","name") 
	file = "/../agvCtrl/projects/"+proName+"/" + local.get("project","agvType")  
	with open(os.path.abspath(os.path.dirname(__file__) + file), 'r') as f:		
		agvTypeDict = {}
		aa = json2.load(f)
		for a in aa:
			agvTypeDict[a] = aa[a]
		return agvTypeDict
g_agvType = _loadAgvType()

MAX_AGV_NUM = 3
g_taskQueue = []		#数字越小，优先级越高

MAX_INSIDE_AGV_NUM = 1
g_taskInsideQueue = []	#内围任务 

g_lock = lockImp.create("runTasks.g_lock")
g_init = False
g_taskMgr = None
#g_relese_agvs = set()				


@lockImp.lock(g_lock)
def addTask(source,target,payloadId,priority):
	global g_taskQueue,g_taskInsideQueue
	log.info(f'Scada send a task to the server from { source } to { target } payloadId: { payloadId }')
	task = scadaTask(source,target,payloadId,int(priority))
	g_taskMgr.add(task)
	log.info('task cmd: got a task from scada',task)
	return task.taskId
	
c_task = []
@lockImp.lock(g_lock)
def failTask(taskId):
	log.warning('task cmd: fail task',taskId)
	t = g_taskMgr.getTask(taskId)
	lockImp.release(g_lock)
	if t is not None:
		t.forceReleaseAgv = True
		t.pda = False
		t.stop()
	taskMgr.fail(taskId,failMsg="task fail by PDA")
	
@lockImp.lock(g_lock)
def finishTask(taskId):
	log.warning('task cmd: finish task',taskId)
	t = g_taskMgr.getTask(taskId)
	lockImp.release(g_lock)
	if t is not None:
		t.forceReleaseAgv = True
		t.pda = False
		t.stop()
	taskMgr.finish(taskId,step="finish")
	
@lockImp.lock(g_lock)
def switchMode(taskId):
	global r_task,c_task
	log.warning('task cmd: switch to pda mode',taskId)
	msg1 = taskMgr.get(taskId)['failMsg']
	t = g_taskMgr.getTask(taskId)
	if t is not None:
		g_taskMgr.cancelTasks.add(taskId)
		if t.isRunning:
			if t.agvId:
				agvApi.cancelTask(t.agvId)
			t.pda = True
			g_taskMgr.save()
			lockImp.release(g_lock)
			t.stop()
		msg = "task canceled - " + str(msg1)
		taskMgr.error(taskId,failMsg=msg)

@lockImp.lock(g_lock)
def allowTask(taskId,locId):
	log.info('task cmd: allow task',taskId,locId)
	t = g_taskMgr.getTask(taskId)
	if t is None:
		log.error("allowTask: can't find taskId %s"%taskId)
		return
		#raise Exception("allowTask: can't find taskId %s"%taskId)
	t.allowTask(locId)

@lockImp.lock(g_lock)
def getTaskStatus():
	return g_taskMgr.getTaskStatus()

@mytimer.interval(2000) 
@lockImp.lock(g_lock)
def run():
	global g_taskQueue,g_taskInsideQueue,g_init
	if not g_init:
		g_init = True
		agvApi.init("scadaTask")
	g_taskMgr.recover()
	
	while g_taskMgr.runningCount(isInside=True) < MAX_INSIDE_AGV_NUM and len(g_taskInsideQueue) > 0:
			t = g_taskInsideQueue.pop(0)
			if not g_taskMgr.isCancelTask(t.taskId):
				t.start()
	
	while g_taskMgr.runningCount(isInside=False) < MAX_AGV_NUM and len(g_taskQueue) > 0:
		findTask = None
		for t in g_taskQueue:
			if g_taskMgr.isCancelTask(t.taskId):
				log.warning(t,"is cancel task")
				findTask = t
				break
			if not g_taskMgr.checkTask(t):
				continue
			if not g_taskMgr.isCancelTask(t.taskId):
				t.start()
			else:
				log.warning(t,"is cancel task2")
			findTask = t
			break
		if findTask:
			g_taskQueue.remove(findTask)
		else:
			break
		time.sleep(1)
	
	g_taskMgr.removeFinishTask()
	
#	#完全没任务了，才让小车回home点  
#	agvs = g_relese_agvs - g_taskMgr.agvs()	#差集
#	g_relese_agvs.clear()
#	for a in agvs:
#		log.info("let",a,"gohome")
#		agvApi.goHome(a,force=False)

@utility.fini()
def stopSave():
	#防止退出时损坏
	if g_taskMgr:
		g_taskMgr.stopSave()
	log.warning("runTask:stop save file")
	 
g_lockPrepoint = {}					#前置点控制,key=mapId.loc,value=taskId
g_lockp = lockImp.create("runTasks.pre_lock")		 #锁住前置点
	
#格式化地图上的点  
def formatLoc(mapId,loc):
	if mapId and loc.find(".") == -1:
		return mapId + "." + loc
	return loc
	 

class scadaTask:
	def __init__(self,source,target,payloadId,priority):
		self.isRecoverTask = False
		self.recoverState = "none"
		self.forceReleaseAgv = False#是否强制释放小车
		self.m_lock = threading.RLock() #用后面这个每次都会泄露 lockImp.create("scadaTask.lock")
		if source is None:
			return
		self.createTime = utility.now()
		self.source = source.strip()
		self.target = target.strip()
		if payloadId is not None:
			#修改
			#self.payloadId = payloadId.strip()
			self.payloadId = "" #也不判断货架，因为逻辑不需要
		else:
			self.payloadId = "" #不判断货架 
		self.agvId = ""
		self.priority = priority
		self.waitLoc = None		#等待允许进入的点信号 
		self.scadaLoc = None	#等待scada允许进入的点信号 
		self.s_info = None		#源信息
		self.t_info = None		#目的信息
		self.param = None
		# name = "从%s运送货架%s到%s"%(source,payloadId,target)
		name = "从%s运送货架到%s" % (source, target)
		self.taskId = taskMgr.add(taskName=name,type="scadaTask",source=source,target=target,payloadId=payloadId,priority=priority)
		log.info()
		self._load()
		self._taskThread = None
		self.isRunning = False
		self.taskStep = "waiting"
		self.canReleaseAgv = False	#是否可以直接释放小车 
		self.forceReleaseAgv = False 
		self.pda = False			#转pda状态
		self.needRelease = False	#是否需要release 
		log.info(self,"is inside",self.isInside)
		#self.waitTaskId = None
		
	def getSaveInfo(self):
		info = {}
		info["taskId"] = self.taskId
		info["taskStep"] = self.taskStep 
		info["source"] = self.source
		info["target"] = self.target
		info["agvId"] = self.agvId
		info["payloadId"] = self.payloadId
		info["waitLoc"] = self.waitLoc
		info["scadaLoc"] = self.scadaLoc 
		info["param"] = self.param
		info["canReleaseAgv"] = self.canReleaseAgv 
		info["pda"] = self.pda
		info["createTime"] = self.createTime
		info["needRelease"] = self.needRelease
		return info
		
	def load(self,info):
		self.taskStep = info["taskStep"]
		self.taskId = info["taskId"]
		self.source = info["source"]
		self.target = info["target"]
		self.payloadId = info["payloadId"]
		self.agvId = info["agvId"]
		self.priority = 0
		self.waitLoc = info["waitLoc"]
		self.scadaLoc = info["scadaLoc"]
		self._load()
		self.param = info["param"]
		self._taskThread = None
		self.isRunning = False
		self.canReleaseAgv = info["canReleaseAgv"]
		self.pda = info["pda"]
		self.createTime = utility.str2date(info["createTime"])
		self.needRelease = False #info["needRelease"]
		self.isRecoverTask = True
		if self.taskStep == "waiting":
			return
		if self.canReleaseAgv:
			log.info("recover can release agv",self)
			self.agvId = ""
			self.taskStep = "waiting"
			return
		elif self.taskStep == "moveSource":
			self.taskStep = "startMovePreSrc"
		elif self.taskStep == "loadPlayload":
			self.taskStep = "startMoveJackup"
		elif self.taskStep == "movePreSourceStep" or self.taskStep == "moveTarget" :
			self.taskStep = "movePreSource"
		elif self.taskStep == "dropPayload":
			self.taskStep = "dropPayloadMove"
		return
		
		
	def __str__(self):
		a = self.agvId
		if not a:
			a = "-"
		s = "task[%s][%s] %s(%s) -> %s(%s) [%s]"%(self.taskId,a,self.s_info["location"],self.s_info["prepoint"],self.t_info["location"],self.t_info["prepoint"],self.taskStep)
		if self.isRecoverTask:
			return "*"+s
		return s
		
		
	def __lt__(self,other): 
		# 取出权重小的
		if self.priority == other.priority:
			return self.createTime < other.createTime
		return self.priority < other.priority
		
	@property
	def isInside(self):
		return self.s_info["floorId"] == "fp-neiwei"
		
	@property
	def sPrepoint(self):
		return formatLoc(self.s_info["floorId"],self.s_info["prepoint"])
		
	@property
	def tPrepoint(self):
		return formatLoc(self.t_info["floorId"],self.t_info["prepoint"])
		
	def _load(self):
		import counter
		log.info(self.target,self.source)
		ds = db.find("u_loc_info",{"_id": {"$in": [self.source,self.target]}})
		while ds.next():
			if ds["_id"] == self.source:
				self.s_info = {
						"prepoint": ds["prepoint"].strip(),
						"location": ds["location"].strip(),
						"floorId": ds["floorId"].strip(),
						"direction": ds["direction"],
						"payloadId": ds["payloadId"],
						"p_direction": ds["p_direction"],	#货架方向
						"WorkPlace": ds["isWorkPlace"]
					}
			elif ds["_id"] == self.target:
				self.t_info = {
						"prepoint": ds["prepoint"].strip(),
						"location": ds["location"].strip(),
						"floorId": ds["floorId"].strip(),
						"direction": ds["direction"],
						"payloadId": ds["payloadId"],
						"p_direction": ds["p_direction"]
					}
		if self.s_info is None and self.t_info is None:
			msg = "can't find source-%s and target-%s info"%(self.source,self.target)
			taskMgr.fail(self.taskId,failMsg=msg)
		elif self.s_info is None:
			msg = "can't find source-%s info"%self.source
			taskMgr.fail(self.taskId,failMsg=msg)
		elif self.t_info is None:
			msg = "can't find target-%s info"%(self.target)
			taskMgr.fail(self.taskId,failMsg=msg)
			
		
	@lockImp.lock(g_lockp)
	def islocAvailable(self,floorId,loc):
		return formatLoc(floorId,loc) not in g_lockPrepoint

	def isPreLocIdle(self,agvId,start,end):
		return agvApi.checkLineIdle(agvId,start,end)["result"]

	@lockImp.lock(g_lockp)
	def lockLoc(self,taskId,floorId,loc):
		key = formatLoc(floorId,loc)

		if key not in g_lockPrepoint:
			log.info("task: prepoint locked ",self.taskId,key)
			g_lockPrepoint[key] = taskId
			return True
		else:
			if g_lockPrepoint[key] == taskId:
				log.info("task: same prepoint",self.taskId,key)
				return True
			log.warning("task: prepoint locked",self.taskId,key,"failed, lock by",g_lockPrepoint[key])
			return False
			
	@lockImp.lock(g_lockp)
	def unlockLoc(self,floorId,loc): 
		key = formatLoc(floorId,loc)
		if key in g_lockPrepoint :
			log.info("task: prepoint released ",self.taskId,key)
			del g_lockPrepoint[key]
		
	@lockImp.lock(g_lockp)
	def clearLoc(self):
		rr = []
		for key in g_lockPrepoint:
			if g_lockPrepoint[key] == self.taskId:
				log.info("task: prepoint released2 ",self.taskId,key)
				rr.append(key)
		for k in rr:
			del g_lockPrepoint[k]
			
		
	def allowTask(self,locId):
		self.scadaLoc = locId
		log.info(self,"allow task",locId)
		
	def start(self):
		if not self.isRunning:
			#recover 
			if self.agvId:
				self.recoverState = "start"
					
			self.isRunning = True
			self._taskThread = threading.Thread(target=self._taskFunc,name="scada."+self.taskId)
			if self.taskStep == "waiting":
				taskMgr.start(self.taskId,failMsg="任务等待执行")
			self._taskThread.start()
		
	def stop(self):	 
		log.info(self,"stop thread, running ",self.isRunning)
		self.isRunning = False
		if self._taskThread != None:
			self._taskThread.join()
		self._taskThread = None 
		self._release()
		
	# 格式为 stepCallback(paramObj,status),status为getTaskStatus()返回的值 
	@lockImp.lock(None)
	def stepCallback(self,obj,status):
		if self.taskStep != "movePreSourceStep":
			return 
		log.info("task: move step callback",self)
		pp = status["unfinishPaths"].split(",")
		if pp:
			if self.s_info["prepoint"] not in pp: 
				taskMgr.update(self.taskId,step="moveTarget") 
				if self.s_info["prepoint"] != self.t_info["prepoint"]:
					self.unlockLoc(self.s_info["floorId"],self.s_info["prepoint"])
				self.taskStep = "moveTarget" 
		
	#def checkFinish(self):
	#	if not self.waitTaskId:
	#		return
	#	taskId = self.waitTaskId
	#	status = agvApi.getTaskStatus(taskId)
	#	log.info("get taskId status",taskId,self,status)
	#	
	#	if taskId not in status:
	#		log.warning("can't get taskId status",taskId,self)
	#		return
	#	
	#	s = status[taskId]
	#	obj = {}
	#	if "status" not in s:
	#		return
	#	if s["status"] == "finish": 
	#		self.waitTaskId = None
	#		obj["result"] = s["success"]
	#		obj["resultDesc"] = s["exception"] 
	#		self.onFinish(obj)
	#	
	#def onFinishNull(self,obj):
	#	log.info("task: move onFinishNull callback",self,obj)
	#	


	@lockImp.lock(None)
	def onFinish(self,obj):
		log.info("task: move finish callback",self)
		if not obj["result"]:
			self.needRelease = True
			taskMgr.error(self.taskId,failMsg=obj["resultDesc"])
			return
		if self.taskStep == "moveSource" or self.taskStep == "startMovePreSrc": 
			self.taskStep = "waitSource"
			self.waitLoc = self.source
			taskMgr.update(self.taskId,step="waitSource",failMsg="等待scada允许进入源信号")
			return  
		elif self.taskStep == "loadPlayload" or self.taskStep == "waitSource":
			self.taskStep = "loadPlayload_readqr"
			taskMgr.update(self.taskId,failMsg="AGV顶升")
			return
		elif self.taskStep == "movePreSourceStep":
			self.taskStep ="movePreSourceStepTimeout"
			return
		elif self.taskStep == "moveTarget":
			taskMgr.update(self.taskId,step="waitTarget",failMsg="等待scada允许进入目标信号")
			self.taskStep ="waitTarget"
			self.waitLoc = self.target 
			return
		elif self.taskStep == "dropPayload":
			self.taskStep = "dropPayloadJackdown"
			taskMgr.update(self.taskId,failMsg="放下货架，旋转顶升机构初始化")
			return
	
	def handleRecover(self):
		if not self.isRecoverTask:
			return True
		if self.recoverState == "none":
			return True
		if self.agvId:
			try:
				if not agvApi.isAvailable(self.agvId):
					log.warning("recover "+str(self),"no available",self.recoverState)
					return False
				agvApi.lock(self.agvId,self.taskId)
				#log.warning("recover "+str(self),"end lock",self.recoverState)
				self.recoverState = "none"
			except Exception as e:
				self.recoverState = "none"
				log.exception("recover "+str(self),e)
				taskMgr.fail(self.taskId,failMsg="recover can't lock "+self.agvId)
				return False
			log.info(self,"recover lock",self.agvId)
			return True
	
	@lockImp.lock(None)
	def handle(self):
		log.info('this is taskStep=============>'+self.taskStep)
		if self.taskStep == "waiting":
			# if not self.islocAvailable(self.s_info["floorId"],self.s_info["prepoint"]):
			# 	return False
			self.taskStep = "waitForAgv"
			taskMgr.update(self.taskId,failMsg="等待分配小车")
			return True
		elif self.taskStep == "waitForAgv":
			self.param = {
				"taskId": self.taskId,
				# "location": self.s_info["prepoint"],
				"location": self.s_info["location"],
				"floorId": self.s_info["floorId"],
				"taskType": "scadaTask",
				"WorkPlace": self.s_info["WorkPlace"]
				}
				
			agvId = self._applyAgv()
			if agvId is None:
				time.sleep(5)
				return False
				
#			lockImp.acquire(g_lock)
#			if agvId in g_relese_agvs:
#				g_relese_agvs.remove(agvId)
#			lockImp.release(g_lock)
			
			log.info(self,"apply",agvId)
			self.canReleaseAgv = True
			self.agvId = agvId 
			self.taskStep = "initJackdown"
			self.param["agvId"] = self.agvId
			taskMgr.update(self.taskId,agvId=self.agvId,failMsg="成功分配小车%s,检测顶升下降"%self.agvId)
			return True
		elif self.taskStep == "initJackdown":
			self.param["taskId"] = self.taskId+"_1"
			self.param['isRotate'] = ''
			# if not self._jackDown():
			# 	return False
			# self.taskStep = "waitSrcPreLoc"
			# self.taskStep = "startMovePreSrc"
			self.taskStep = "startMoveJackup"
			# taskMgr.update(self.taskId,failMsg="等待%s前置点锁"%self.source)
			taskMgr.update(self.taskId,failMsg="前往%s工位点拉取货架"%self.source)
			return True
		# elif self.taskStep == "waitSrcPreLoc":
		# 	if not self.lockLoc(self.taskId,self.s_info["floorId"],self.s_info["prepoint"]):
		# 		return False
		# 	self.taskStep = "waitSrcPreLoc1"
		# 	taskMgr.update(self.taskId, failMsg="等待前置点%s与工位点%s处无小车"%(self.s_info["prepoint"],self.s_info["location"]))
		# 	return True
		# elif self.taskStep == "waitSrcPreLoc1":
		# 	if not self.isPreLocIdle(self.agvId,self.s_info["prepoint"],self.s_info["location"]):
		# 		time.sleep(3)
		# 		return False
		# 	self.taskStep = "startMovePreSrc"
		# 	taskMgr.update(self.taskId,failMsg="前往%s前置点"%self.source)
		# 	return True
		# elif self.taskStep == "startMovePreSrc":
		# 	if not self._moveAgv():
		# 		return False
		# 	taskMgr.update(self.taskId,step="moveSource")
		# 	self.taskStep = "moveSource"
		# 	self.canReleaseAgv = False
		# 	return True
		# elif self.taskStep == "waitSource": #这个通过onFinish跳转 moveSource -> waitSource
		# 	if self.payloadId and self.waitLoc != self.scadaLoc:
		# 		log.info(self,"scada allow task error",self.payloadId,self.waitLoc,"!=",self.scadaLoc)
		# 		return False
		# 	self.taskStep = "waitRotationClear"
		# 	self.scadaLoc = ""
		# 	log.info(self,"scada allow task",self.agvId,self.s_info['prepoint'],"->",self.source)
		# 	taskMgr.update(self.taskId,step="loadPlayload",failMsg="等待AGV旋转顶升初始化")
		# 	return True
		# elif self.taskStep == "waitRotationClear":
		# 	try:
		# 		log.info("clear rotation",self)
		# 		rotationApi.rotationClear(self.agvId)
		# 		# self._jackDown()
		# 	except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
		# 		raise
		# 	except Exception as e:
		# 		log.exception("rotationClear"+str(self),e)
		# 		return False
		# 	self.taskStep = "startMoveJackup"
		# 	taskMgr.update(self.taskId,failMsg="前往源位置%s"%self.source)
		# 	return True
		elif self.taskStep == "startMoveJackup":
			self.param["location"] = self.s_info["location"]
			self.param["floorId"] = self.s_info["floorId"]
			self.param["taskId"] = self.taskId+"_2"
			self.param["direction"] = self.s_info["direction"]
			self.param["p_direction"] = self.s_info["p_direction"]
			log.info("------------------------------执行到runTasks._moveJackup()-----------------000-----------------")
			self._moveJackup()
			self.taskStep ="loadPlayload"
			log.info("==============================runTasks._moveJackup()结束====================================")
			return True
		elif self.taskStep == "loadPlayload_readqr":  #这个通过onFinish跳转 loadPlayload -> loadPlayload_readqr
			if self.payloadId:	# 识别二维码
				p = self._getPgv()
				taskMgr.update(self.taskId, errorno=p['errorno'], errormsg=p['errormsg'])
				if p['errorno'] != 0 or p['tag_value'] == "":
					# 二维码失败就任务整个结束 
					self.taskStep = "failed"
					self.canReleaseAgv = True
					taskMgr.fail(self.taskId,failMsg=p['errormsg'])
					return False
			self.taskStep = "loadPlayload_jackup"
			return True
		elif self.taskStep == "loadPlayload_jackup": 
			self.canReleaseAgv = False
			if not self._jackUp():
				return False
			self.taskStep ="waitDestPreLoc"
			taskMgr.update(self.taskId,failMsg="等待%s工位点锁"%self.target)
			return True
		elif self.taskStep == "waitDestPreLoc":
			# if not self.lockLoc(self.taskId,self.t_info["floorId"],self.t_info["prepoint"]):
			if not self.lockLoc(self.taskId,self.t_info["floorId"],self.t_info["location"]):
				return False
			# self.taskStep = "waitDestPreLoc1"
			# self.taskStep = "movePreSource"
			self.taskStep = "dropPayloadMove"
			taskMgr.update(self.taskId,failMsg="前往%s工位点放下货架" % (self.t_info["location"]))
			return True
		# elif self.taskStep == "waitDestPreLoc1":
		# 	if not self.isPreLocIdle(self.agvId,self.t_info["prepoint"],self.t_info["location"]):
		# 		time.sleep(3)
		# 		return False
		# 	self.taskStep ="movePreSource"
		# 	taskMgr.update(self.taskId,step="movePreSource",failMsg="前往目标位置%s前置点"%self.target)
		# 	return True
		# elif self.taskStep == "movePreSource":
		# 	self.param["floorId"] = self.t_info["floorId"]
		# 	self.param["taskId"] = self.taskId+"_3"
		# 	self.param["location"] = self.t_info["prepoint"]
		# 	self.taskStep ="movePreSourceStep" #这个通过stepCallback跳转
		# 	self._moveAgv(stepCallback=self.stepCallback)
		# 	return True
		# elif self.taskStep == "movePreSourceStepTimeout":
		# 	#距离太短，导致stepCallback没回调，直接进入onfinish会进入这个状态
		# 	taskMgr.update(self.taskId,step="moveTarget")
		# 	if self.s_info["prepoint"] != self.t_info["prepoint"]:
		# 		self.unlockLoc(self.s_info["floorId"],self.s_info["prepoint"])
		# 	time.sleep(0.5)
		# 	# taskMgr.update(self.taskId,step="waitTarget",failMsg="等待scada允许进入目标信号")
		# 	taskMgr.update(self.taskId,step="waitTarget",failMsg="准备进入目标点")
		# 	self.taskStep ="waitTarget"
		# 	self.waitLoc = self.target
		# 	return True
		# elif self.taskStep == "waitTarget":
		# 	if self.payloadId and self.waitLoc != self.scadaLoc:
		# 		return False
		# 	log.info(self,"scada allow task",self.agvId,self.t_info['prepoint'],"->",self.target)
		# 	self.scadaLoc = ""
		# 	self.taskStep = "waitTargetTurn"
		# 	taskMgr.update(self.taskId,failMsg="调整方向进目标位置")
		# 	return True
		# elif self.taskStep == "waitTargetTurn":
		# 	if not self._rotation():
		# 		#self.needRelease = True
		# 		return False
		# 	self.taskStep ="dropPayloadMove"
		# 	taskMgr.update(self.taskId,failMsg="前往目标位置%s"%self.target)
		# 	return True
		elif self.taskStep == "dropPayloadMove":
			self.param["location"] = self.t_info["location"]
			self.param["floorId"] = self.t_info["floorId"]
			self.param["taskId"] = self.taskId+"_4"
			self.param["direction"] = self.t_info["direction"]
			self._moveJackdown()
			taskMgr.update(self.taskId,step="dropPayload")
			self.taskStep = "dropPayload"	#这个通过onFinish跳转 dropPayload -> dropPayloadJackdown
			return True 
		elif self.taskStep == "dropPayloadJackdown":
			if not self._jackDown():
				return False  
			self.taskStep = "dropPayloadReset" 
			return True

		elif self.taskStep == "dropPayloadReset":
			# if not self._rotationBack():
				#self.needRelease = True
				# return False
			# self._jackDown() #旋转会带有顶伸，所以还需要jackDown
			self.canReleaseAgv = True
			self.taskStep = "finish"
			taskMgr.finish(self.taskId,step="finish",failMsg="任务成功")
			return True
		else:
			#在onfinish跳转 
			return True
		
	@utility.catch
	def _taskFunc(self):
		log.info('task: start',self)
		isRelease = False
		
		while self.isRunning:
			if not self.handleRecover():  #流程会返回一个True
				time.sleep(2)
				continue
			
			old = self.taskStep
			try:
				if self.needRelease:  #onFinish异常失败，需要人工来处理
					self._release() 
					isRelease = True
					break
				elif self.taskStep == "failed": 
					agvId = self.agvId
					self._release()  
					isRelease = True
					break
				elif self.taskStep == "finish":
					agvId = self.agvId
					self._release() 
					isRelease = True
					break
				elif not self.handle(): 
					log.info(str(self),self.taskStep,"error")
					time.sleep(2)
					continue
				if old != self.taskStep:
					log.debug(str(self),old,"->",self.taskStep)
			except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
					log.exception("taskFunc:"+str(self),e)
					time.sleep(2)
					continue
			except Exception as e:
				log.exception("taskFunc2:"+str(self),e)
				taskMgr.error(self.taskId,failMsg=str(e)) 
				break
			g_taskMgr.save()
			time.sleep(0.3)
				 
		if not isRelease:
			self._release()
		self.isRunning = False
		log.info("task: stop",self)
		  
	@lockImp.lock(g_lock)
	def _release(self):
		try:
			if self.agvId:
				releaseFlag = self.canReleaseAgv
				if self.forceReleaseAgv:
					releaseFlag = True
				#log.info(self,self.agvId,"release task, release agv",releaseFlag)  
				log.info(self,self.agvId,"release task, release agv",releaseFlag,self.canReleaseAgv,self.forceReleaseAgv) 
				if releaseFlag:
					ret = agvApi.isLocked(self.agvId,self.taskId)
					agvApi.release(self.agvId, self.taskId,force=False)
					#g_relese_agvs.add(self.agvId)
					if ret:
						log.info(self,"let",self.agvId,"gohome")
						agvApi.goHome(self.agvId,force=False,timeout=60*60*3)
					else:
						log.info(self,self.agvId,"lock by other taskId, no gohome")
					self.agvId = ""
		except Exception as e:
			log.exception(str(self)+"task release",e)
		self.clearLoc()


	# 过滤某些工位 如果不是04车 agvapi那里加入exclude 
	def _filterFunc(self, agvId, mapId, loc, payload):
		L_RACK = ['fp20190712-1.AP286','fp20190712-1.AP287','fp20190712-1.AP266','fp20190712-1.AP268','fp20190712-1.AP270',
				'fp20190712-1.AP272','fp20190712-1.AP262','fp20190712-1.AP264','fp20190712-1.AP749','fp20190712-1.AP750',
				'fp20190712-1.AP753','fp20190712-1.AP291','fp20190712-1.AP290','fp20190712-1.AP756','fp20190712-1.AP757']#L_RACK工位
		oldAGV = ['AGV01',"AGV02",'AGV03',"AGV04","AGV05","AGV06"]   # 新装曲臂连杆的车不能进L_RACK工位
		t_loc = formatLoc(self.t_info["floorId"],self.t_info["location"])
		s_loc = formatLoc(self.s_info["floorId"],self.s_info["location"])
		if s_loc in L_RACK or t_loc in L_RACK:
			if agvId in oldAGV:
				return False
		else:
			if not agvId in oldAGV:
				return False


		return True


	#@lockImp.lock(g_lock)
	def _applyAgv(self): 
		try:
			return agvApi.apply(taskId=self.param["taskId"], mapId=self.param["floorId"],loc=self.param["location"], timeout=10) #filterFunc=self._filterFunc, 
		except Exception as e:
	#		lockImp.release(g_lock)
			log.warning("[%s] apply agv failed: %s"%(str(self),str(e)))
			# taskMgr.update(self.taskId, errormsg='waiting to apply AGV!', errorno=11)
			return None
	
	#@lockImp.lock(g_lock)
	def _moveAgv(self,stepCallback=None):
		try:
			self.param["timeoutSec"] = 86400
			if "seer_jackup" in self.param:
				del self.param["seer_jackup"]
			#self.waitTaskId = self.param["taskId"]
			agvApi.move(self.agvId, self.param["floorId"]+'.'+self.param["location"], self.onFinish, self.param, stepCallback=stepCallback)
			#agvCtrl下的agvApi.py
			return True
		except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
			raise
		except Exception as e:
			raise e
			taskMgr.error(self.taskId,failMsg=str(e)) 
			return False
	
	#@lockImp.lock(g_lock)
	def _moveJackup(self):
		log.info('----------------------------在runTasks.py的_moveJackup函数中-----------------111-------------')
		self.param["timeoutSec"] = 86400
		#self.waitTaskId = self.param["taskId"]
		if proName =='fastprint':
			if 'WorkPlace' in self.param and self.param['WorkPlace'] and self.param['WorkPlace']!='' and self.param['WorkPlace'].lower() == 'true':
				agvApi.moveJackup(self.agvId, self.param["floorId"]+'.'+self.param["location"], self.onFinish, self.param, use_pgv=False)
			else:
				if self.agvId in ["AGV07","AGV08"]:
					agvApi.moveJackup(self.agvId, self.param["floorId"]+'.'+self.param["location"], self.onFinish, self.param, use_pgv=True,pgv_type=4)
				else:
					agvApi.moveJackup(self.agvId, self.param["floorId"]+'.'+self.param["location"], self.onFinish, self.param, use_pgv=True,pgv_type=1)
		else:
			log.info('-----------------runTasks.py中的else，因为不是fastprint项目，走这里------------222-------------')
			agvApi.moveJackup(self.agvId, self.param["floorId"]+'.'+self.param["location"], self.onFinish, self.param)
			#跳转到
	#@lockImp.lock(g_lock)
	def _moveJackdown(self): 
		self.param["timeoutSec"] = 86400
		#self.waitTaskId = self.param["taskId"]
		agvApi.moveJackdown(self.agvId, self.param["floorId"]+'.'+self.param["location"], self.onFinish, self.param)
	
	#@lockImp.lock(g_lock)
	def _getPgv(self):
		try:
			for i in range(5):
				pgv_msg = pgvApi.getPgv(self.agvId)
				if pgv_msg is None: 
					time.sleep(1)
					continue
				if pgv_msg['tag_value'] == 0: 
					time.sleep(1)
					continue
				else:
					break

			lockImp.release(g_lock)
			
			if pgv_msg is None: 
				return {'tag_value':'', 'errorno':-1, 'errormsg':"read qrcode failed"}
			if pgv_msg['tag_value'] == 0: 
				return {'tag_value':'', 'errorno':-2, 'errormsg':'there is no payload'}
			
			ds = db.find_one("u_pgv_info", {"pgvId":str(pgv_msg['tag_value'])})			
			if ds is None:
				errormsg = 'The tag_value is %s but there is no match data'%str(pgv_msg['tag_value'])
				return {'tag_value':pgv_msg['tag_value'], 'errorno':-3, 'errormsg':errormsg}
				
			log.info('task: read qrcode:%s, payloadId:%s, db:%s'%(pgv_msg['tag_value'], self.payloadId, ds["payloadId"]))

			if str(ds["payloadId"]) == str(self.payloadId):
				return {'tag_value':ds["payloadId"], 'errorno':0, 'errormsg':""}
			else: 
				errormsg = 'Not match: the tag_value is %s but the payloadId is %s'%(ds["payloadId"], self.payloadId)
				return {'tag_value':ds["payloadId"], 'errorno':-4, 'errormsg':errormsg}
		except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
			raise
		except Exception as e:
			log.exception(str(self)+' getPgv',e)
			return {'tag_value':'', 'errorno':-1, 'errormsg':str(e)}
	
	def _rotationLeft(self,target=90):
		try:
			rotationApi.rotationLeft(self.agvId,target=target)
			return True
		except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
			raise	
		except Exception as e:
			taskMgr.update(self.taskId, errormsg='rotate left %d error'%target, errorno=51)
			log.exception(str(self)+' rotationLeft',e)			
			return False
	
	def _rotationRight(self,target=90):
		try:
			rotationApi.rotationRight(self.agvId,target=target)
			return True
		except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
			raise
		except Exception as e:
			taskMgr.update(self.taskId, errormsg='rotate right %d error'%target, errorno=52)
			log.exception(str(self)+' rotationRight',e)
			return False
		
	def _jackUp(self):
		try:
			log.info(self,"_jackUp")
			jackApi.jackUp(self.agvId, timeoutSec=90) 
			return True
		except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
			raise
		except Exception as e:
			log.exception(str(self)+' jackup',e)
			return False
		
	def _jackDown(self): 
		try:
			log.info(self,"_jackDown")
			#2021-03-29 15：43取消
			jackApi.jackDown(self.agvId, timeoutSec=90)
			return True 
		except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
			raise
		except Exception as e:
			log.exception(str(self)+' jackDown',e)
			return False
			   
	# 角度归位
	def _rotationBack(self):
		log.info(self,"rotationClear")
		return rotationApi.rotationClear(self.agvId)
	
	def _rotation(self):  
		# 转角度  
		log.debug(str(self),self.agvId,"rotate",self.s_info['p_direction'], "->",self.t_info['p_direction'])
		if self.s_info['p_direction'] == self.t_info['p_direction']: 
			return True
		angle = self.t_info['p_direction'] - self.s_info['p_direction']
		self.param["isRotate"] = str(angle)
		log.debug(self.agvId, 'Rotate:',self.param['isRotate']) 

		if _getAgvType(self.agvId)['jackType'].lower()=="io": 
			if abs(angle) == 180:
				return self._rotationRight(180)
			elif angle == -90:
				return self._rotationLeft(270)
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

class scadaTaskMgr:
	def __init__(self):
		self.tasks = {}
		self.cancelTasks = set()
		self.stopSaveFlag = False
		self.filename = os.path.abspath(os.path.dirname(__file__)) + "/task_status.json"
		self.hasRecover = False
		self.load()
	
	@lockImp.lock(g_lock)
	def stopSave(self):
		self.stopSaveFlag = True
	
	def add(self,task):
		self.tasks[task.taskId] = task
		if task.isInside:
			g_taskInsideQueue.append(task)
		else:
			g_taskQueue.append(task)
	
	def getTask(self,taskId):
		if taskId in self.tasks:
			return self.tasks[taskId]
		return None
		
	def getTaskStatus(self):
		ret = []
		for id in self.tasks:
			ret.append({
				"id": id,
				"status": self.tasks[id].taskStep,
				"isRunning": self.tasks[id].isRunning,
				"agvId": self.tasks[id].agvId
				})
		return ret
	
	def checkTask(self,task):
		for t in self.tasks.values():
			if t.isRunning and t.isInside == task.isInside and t.sPrepoint == task.tPrepoint and t.tPrepoint == task.sPrepoint:
				log.info(task,"loop with",t)
				return False
		ret = task.islocAvailable(task.s_info["floorId"],task.s_info["prepoint"])
		if not ret:
			log.info(task,"prepoint lock")
		return ret
	
	def runningCount(self,isInside):
		ret = 0
		for t in self.tasks.values():
			if t.isRunning and t.isInside == isInside:
				ret += 1
		return ret
		
	def removeFinishTask(self):
		rr = []
		for t in self.tasks.values():
			if not t.isRunning and t.taskStep != "waiting":
				rr.append(t.taskId)
				
		for id in rr:
			if not self.tasks[id].needRelease:
				if not self.tasks[id].pda:
					#异常的任务还是留下来，保存到文件里，下次继续运行 
					log.debug("task: delete task",id)
					del self.tasks[id]
			if id in self.cancelTasks:
				self.cancelTasks.remove(id)
			
	def isCancelTask(self,taskId):
		return taskId in self.cancelTasks
		 
	def cancel(self,taskId):
		if taskId not in self.cancelTasks:
			self.cancelTasks.add(taskId)
			
	def agvs(self):
		ret = set()
		for t in self.tasks.values():
			if t.agvId:
				ret.add(t.agvId)
		return ret
		
	@lockImp.lock(g_lock)
	def save(self):
		if self.stopSaveFlag:
			return
		infos = []
		#时间倒序排序
		for t in self.tasks.values():
			infos.append(t.getSaveInfo())
		infos = sorted(infos, key=lambda v:v["createTime"], reverse = True)
		# if not os.path.exists(self.filename):
		json.dump_file(self.filename,infos)
			
			
	@lockImp.lock(g_lock)
	def load(self):	
		ds = taskMgr.getUnfinishTask()
		def findTask(id):
			for d in ds:
				if id == str(d["_id"]):
					return True
			return False
		if os.path.exists(self.filename):

			try:
				infos = json.load_file(self.filename)
				for info in infos:
					t = scadaTask(None,None,"",0)
					t.load(info)
					if info["taskStep"] == "finish":
						continue
					if info["taskStep"] == "failed":
						continue
					if not findTask(t.taskId): 
						log.error("load task: can't find task",t)
						continue
					if t.pda:
						log.warning("load task: handle with pda",t)
						continue
					log.info("load task:",t)
					#self.add(t)
					self.tasks[t.taskId] = t
			except Exception as e:
				log.error("load", self.filename, "failed ", e)

		
	def recover(self):
		if self.hasRecover:
			return
		self.hasRecover = True
		for t in self.tasks.values():
			if t.taskStep == "waiting":
				self.add(t)	#加入队列 
				log.info('task recover: add task',t)
				continue
			t.start()
		time.sleep(3)
		agvApi.startCharge()
		
		
g_taskMgr = scadaTaskMgr()

################ UNIT TEST ###########
def test_task1(taskLen):
	taskList = []
	# locList = [{"source": "ZZ-AI-DG-02","target": "KL-PM-XG-01"},
	#			 {"source": "KL-DB-SG-01","target": "NC-QC-DG-01"},
	#			 {"source": "NC-TM-XG-01","target": "NC-BG-DG-01"},
	#			 {"source": "NC-XY-DG-01","target": "ZZ-AI-DG-02"},
	#			 {"source": "NA-ZX-DG-01","target": "KL-DB-SG-01"},
	#			 {"source": "NA-PT-SG-01","target": "NC-TM-XG-01"}]

	# locList = [
	#	 {"source": "TEST-01","target": "TEST-02"},
	#	 {"source": "TEST-03","target": "TEST-04"},
	#	 {"source": "TEST-05","target": "TEST-06"},
	#	 {"source": "TEST-07","target": "TEST-08"},
	#	 {"source": "TEST-09","target": "TEST-10"},
	#	 {"source": "TEST-011","target": "TEST-12"},
	# ]
	# for i in range(taskLen):
	#	 t = i%6
	#	 taskId = pushTask(locList[t]["source"],locList[t]["target"],"",i)
	#	 taskList.append(taskId)
	locList = [
		{"source": "NC-QC-SG-01","target": "NC-QC-DG-01", "payloadId":"CA-LRA-00028"},]
		# {"source": "ZZ-ZH-DG-01","target": "ZZ-ZH-DG-06", "payloadId":"CA-LRA-00029"},]
		# {"source": "TEST-12","target": "TEST-13", "payloadId":"CA-WCJ-00025"},
		
		# {"source": "TEST-15","target": "TEST-12", "payloadId":"CA-SCJ-00029"},
		# ]
	def test(locList):
		task2 = []
		for i in range(taskLen):
			print('test---->', locList[i]["source"],locList[i]["target"],locList[i]["payloadId"])
			taskId = addTask(locList[i]["source"],locList[i]["target"],'',1)
			taskList.append(taskId)
			t = g_taskMgr.getTask(taskId)
			t.start()
			task2.append(t)
			global g_taskQueue,g_taskInsideQueue,g_init
			if not g_init:
				g_init = True
				agvApi.init("scadaTask")

		while True:
			for t in task2:
				if t.taskStep=='waitSource':
					t.scadaLoc = t.param['location']
				elif t.taskStep=='waitTarget':
					t.scadaLoc = t.param['location']
					# print('waitForScadaSignal----->', t.param['location'])
		#	 statusList = taskMgr.getTaskList(taskList)
		#	 r = []
		#	 for s in statusList :
		#		 print (s["taskId"],s["status"],s["step"])
		#		 if s["status"] == "waiting":
		#			 if s["step"] == "waitSource" :
		#				 allowTask(s["taskId"],s["source"])
		#			 elif s["step"] == "waitTarget":
		#				 allowTask(s["taskId"],s["target"])
		#		 elif s["status"] == "fail" or s["status"] == "success":
		#			 r.append(s)
		#	 if len(r) == len(taskList):
		#		 break
		#	 time.sleep(3)
		LL = []
		dd = {}
		for i in range(taskLen):
			dd = {"source": locList[i]['target'],"target": locList[i]['source'], "payloadId":locList[i]['payloadId']},
			LL.append(dd)
		del locList[:]
		locList += LL
		print('do test another time')
		# test(locList)
	test(locList)
	
def test_task2(taskLen):
	taskList = []
	locList = 2*[{"source": "ZZ-AI-DG-02","target": "KL-PM-XG-01"},{"source": "KL-DB-SG-01","target": "NC-QC-DG-01"},{"source": "NC-TM-XG-01","target": "NC-BG-DG-01"}]
	for i in range(taskLen):
		t = i%6
		taskId = addTask(locList[t]["source"],locList[t]["target"],"",i)
		taskList.append(taskId)
	while True:
		statusList = taskMgr.getTaskList(taskList)
		r = []
		for s in statusList :
			print (s["taskId"],s["status"],s["step"])
			if s["status"] == "running" :
				if s["step"] == "waitSource" :
					allowTask(s["taskId"],s["source"])
				elif s["step"] == "waitTarget":
					allowTask(s["taskId"],s["target"])
			elif s["status"] == "fail" or s["status"] == "success":
				r.append(s)
		if len(r) == len(taskList):
			break
		time.sleep(3)
	
def test_task3(taskLen):
	taskList = []
	locList = taskLen*[{"source": "TEST-03","target": "TEST-01"},{"source": "ZZ-AI-DG-02","target": "NC-QC-DG-03"},{"source": "TEST-01","target": "TEST-03"}]
	for t in locList:
		taskId = addTask(t["source"],t["target"],"",1)
		taskList.append(taskId)
	while True:
		statusList = taskMgr.getTaskList(taskList)
		r = []
		for s in statusList :
			print (s["taskId"],s["status"],s["step"])
			# if s["status"] == "running" :
				# if s["step"] == "waitSource" :
					# allowTask(s["taskId"],s["source"])
				# elif s["step"] == "waitTarget":
					# allowTask(s["taskId"],s["target"])
			if s["status"] == "fail" or s["status"] == "success":
				r.append(s)
		if len(r) == len(taskList):
			break
		time.sleep(3)
	
	
def testsave():
	t1 = scadaTaskMgr()
	task = scadaTask("ZZ-ZH-DG-03","ZZ-ZH-DG-02","CA-SCJ-00002",1)
	t1.add(task)
	t1.save()
	t2 = scadaTaskMgr()
	task = scadaTask("ZZ-ZH-DG-03","ZZ-ZH-DG-02","CA-SCJ-00002",1)
	t2.add(task)
	t2.save()
	#print(t2)
	
	
if __name__ == "__main__":
	# utility.start()
	test_task1(2)
	


# 10 apply agv failed
# 11 waiting for apply agv 
# 12 apply agv failed timeout


# 30 agv move failed 
# 31 isEmergency stop
# 32 isBlocked stop
# 33 lowConfidence stop

# 40 agv jack error 
# 41 agv jackUp error 
# 42 agv jackDown error

# 50 agv rotate error 
# 51 agv rotate left error 
# 52 agv rotate right error  
