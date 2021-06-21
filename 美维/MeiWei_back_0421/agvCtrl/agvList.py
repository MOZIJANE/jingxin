# coding=utf-8
# ycat			2018-8-2	  create
# AGV管理  
import sys, os
import threading
import json,math
import socket
import setup

if __name__ == '__main__':
	setup.setCurPath(__file__)
import utility 
import alarm.aliveApi
import mytimer
import lock as lockImp
import time
import log
import local
import enhance
import mapMgr 
import counter
import agvType
import shelveInfo
import agvDevice.rotationApi as rotationApi

if utility.is_test(): 
	import driver.seerAgv_0427.mockAgvCtrl as agvCtrl
else:
	import driver.seerAgv_0427.agvCtrl as agvCtrl

# 位置信息事件
# 参数：agvId,x,y,angle
locationEvent = enhance.event()

# 位置信息事件
# 参数: agvId,targetName
targetLocEvent = enhance.event()

# 电池电量事件
# 参数: agvId
# level: [0,1]是电量范围
# ischarging: True正在充电，False未充电
batteryEvent = enhance.event()

# agv重启事件
# 参数: agvId
#rebootEvent = enhance.event()
projectName = local.get("project","name")
g_waitStopTime = local.getint("ctrl","waitStopTime",30)

g_agvList = None
g_mapIdList = set()
g_agvLock = lockImp.create("agvList.g_agvLock")

@lockImp.lock(g_agvLock)
def hasAgv(agvId):
	if g_agvList is None:
		return False
	return agvId in g_agvList

def getAgv(agvId): 
	return getAgvList()[agvId]


@lockImp.lock(g_agvLock)
def clear():
	assert utility.is_test()
	global g_agvList
	if g_agvList is None:
		return
	aa = g_agvList.values()
	g_agvList = None
	lockImp.release(g_agvLock)
	for a in aa:
		a.stop()

g_cur_path = __file__
def _loadAgvList():
	global g_cur_path,g_mapIdList
	g_mapIdList.clear()
	proName = local.get("project","name")
	if utility.is_test():
		proName = "test"
	file = "projects/"+proName+"/" + local.get("project","agvcfg")  #agv.cfg增加perpherialIP为外挂工控机IP地址，用于driver.seerAgv.agvApi
	file = os.path.abspath(os.path.dirname(g_cur_path)) + "/" + file
	log.info("load agv file:",file) 
	
	with open(file, 'r') as f:
		agvList = json.load(f)
		ret = {} 
		for agvId in agvList:
			if agvList[agvId]["enable"].lower() == "false":
				continue
			homeLoc = agvList[agvId]["homeLoc"]
			mapId = agvList[agvId]["map"]
			if mapId:
				g_mapIdList.add(mapId)   
			agv = agvInfo(agvId=agvId, mapId=mapId, homeLoc=homeLoc) 
			agv.type = agvList[agvId]["type"]
			agv.width = agvType.getFloat(agv.type,"width")
			agv.height = agvType.getFloat(agv.type,"height")
			agv.shelfId = agvType.get(agv.type,"shelve")
			ret[agvId] = agv
			if utility.is_test() and mapId and homeLoc: 
				agv.createMock(mapId,homeLoc) 
		return ret

@lockImp.lock(g_agvLock)
def removeAgv(agvId):
	global g_agvList
	if agvId in g_agvList:
		agv = g_agvList[agvId]
		del g_agvList[agvId]
		lockImp.release(g_agvLock)
		agv.stop()
		
		
		
def resetLock(appName): 
	aa = getAgvList()
	for agvId in aa:
		aa[agvId].resetLock(appName)
		

@utility.init()	
@lockImp.lock(g_agvLock)
def getAgvList():
	global g_agvList
	if g_agvList is None: 
		g_agvList = _loadAgvList() 
	return g_agvList 
	

def maxWidth():
	aa = getAgvList()
	return max([aa[a].width for a in aa])
	
def maxHeight():
	aa = getAgvList()
	return max([aa[a].height for a in aa])
	
	
g_alarmId = None
@lockImp.lock(g_agvLock)
def getAlarmId():
	global g_alarmId
	if g_alarmId is None:
		g_alarmId = []
		import json
		file = os.path.join(os.path.abspath(os.path.dirname(__file__)), "alarm.json")
		with open(file, 'r',encoding="utf_8") as f:
			ret = json.load(f)
			for r in ret:
				g_alarmId.append(int(r))
	return g_alarmId

class agvInfo:
	def __init__(self, agvId, mapId, homeLoc): 
		self.m_lock = lockImp.create("agvList."+agvId+".lock")
		self.isThreadRunning = True
		self.initAlarm = False #是否已经初始化数据库告警
		self.thread = threading.Thread(target=self.run,name="agvThread."+agvId)
		self.thread2 = threading.Thread(target=self.run2,name="agvThread2."+agvId)
		
		self.lastUpdateClocks = None #时钟同步时间
		self.lostTicks = 0  #丢位置时间 
		self.idleTicks = 0 	#闲置时间 
		self.lockTicks = 0	#上锁时间
		self.unlockTicks = 0#解锁时间
		self._ticks = None
		self.agvId = agvId
		self.homeLoc = mapMgr.formatLoc(mapId,homeLoc)
		self.status = None
		self.inited=0
		self.mapId = None
		self.hasShelve = False #是否带有货架  
		self.lockApp = None	  #当锁的应用名   
		self.lockTaskId = None #当前上锁的任务id 
		self._curTarget = ""  # 当前位置名，默认都是从home点启动
		self.isLinked = True	#TCP是否可以连上
		self.isCharge = False
		self._isEmergency = False
		self._isBlocked = False
		self._hasAlarm = False
		timeout = local.getint("ctrl","activeTimeout",300)
		self._alarmObj = alarm.aliveApi.aliveObj(moid=agvId, typeId=49999, desc="AGV离线异常", timeoutSecond=timeout,
		                                         domain="agv")
		self._allAlarmId = set()  # 已产生的告警的ID列表，用于做告警清除

		self._initState = 2  # 初始化状态：2正在初始化，1成功，0初始化失败
		self.readIOArray = [False] * 16
		self.writeIOArray = [False] * 16
		self.batteryLevel = 1 
		self._taskInfo = None	#任务对象 
		self._taskTick = 0		#任务启动时间   
		self._inHandle = False
		self.canCharge = True	#是否可以充电 
		self.pauseState = False #是否暂停处理
		self.thread.start()
		self.thread2.start()
		
	def stop(self):
		log.error("agvList: stop",self.agvId)
		self.isThreadRunning = False
		self.thread.join()
		self.thread2.join()
		
	#agv正在执行的任务名 
	@property
	def nextTarget(self):
		if not self.status:
			return ""
		if "target_id" not in self.status:
			return ""
		return self.status["target_id"]
		
		
	#开始充电门限 
	@property
	def start_charge_level(self):
		return agvType.getFloat(self.type,"start_charge_level")
		
	#充电门可用门限 
	@property
	def available_charge_level(self):
		return agvType.getFloat(self.type,"available_charge_level")
		
	#充满门限 
	@property
	def full_charge_level(self):
		return agvType.getFloat(self.type,"full_charge_level")
		
	def get(self,key):
		return agvType.get(self.type,key)
		
	def __str__(self):
		s = f"[{self.agvId}] map={str(self.mapId)}.{str(self._curTarget)},battery={self.batteryLevel},"
		s += f"task_status={self.task_status},lock={self.lockApp}.{self.lockTaskId},"
		s += f"shelf={self.hasShelve},linked={self.isLinked},canCharge={self.canCharge},"
		s += f"emergency={self._isEmergency},alarm={self._hasAlarm},available={self.isAvailable()},"
		s += f"target={self.targetPosName},init={self._initState},"
		if self.status:
			try:
				s += f"loadmap_status={self.status['loadmap_status']},reloc={self.status['reloc_status']},"
			except Exception as e:
				log.exception(self.agvId,e)
		e = self.agvElement
		if e:
			s += f"checkFailed={e.checkFailed},block={e.isBlocked},isDeadlock={e.isDeadlock},"
		s += f"tick={self._ticks}"
		return s
	
	@property
	def action(self):
		if self.params is not None and "status" in self.params:
			return self.params["status"]
		else:
			return "none"
		
	@property
	def map(self): 
		if self.mapId is None:
			return None
		return mapMgr.getMap(self.mapId)
		
	@property
	def agvElement(self):
		if self.mapId is None:
			return None
		return self.map.getAgv(self.agvId)
		
	@property
	def targetPosName(self):
		try:
			pp = self.agvElement.targetList
		except Exception:
			return None
		if pp:
			return pp[-1]
		return None
	
	@property
	def shelf(self):
		return shelveInfo.get(self.shelfId)
	
	@property
	def confidence(self):
		if not self.status:
			return 0
		if "confidence" not in self.status:
			return 0
		if self.status["confidence"] is None:
			return 0
		return self.status["confidence"]
	
	# 取当前位置
	@property
	def curTarget(self):
		return self._curTarget
	
	@property
	def x(self):
		if not self.status:
			log.error(self.agvId,"status is None")
			return -1000
		if "x" not in self.status:
			return -1000
			#assert 0
		return self.status['x']

	@property
	def y(self):
		if not self.status:
			log.error(self.agvId,"status is None")
			return -1000
		if "y" not in self.status:
			return -1000
		return self.status['y']
		
	@property
	def angle(self):
		if not self.status:
			log.error(self.agvId,"status is None")
			return 0
		if "angle" not in self.status:
			return 0
		return self.status['angle']
	
	@property
	def isActive(self):
		return self._alarmObj.isActive()
	
	#状态最后更新时间 
	@property
	def ticks(self):
		return self._ticks
	
	@property
	def isChargeTask(self):
		if self.isCharge:
			return True
		if self.isAtChargePos:
			return True
		pos = self.targetPosName 
		if pos is None:
			return False
		return self.map.getPos(pos).isChargePoint
		
	
	@property
	def isHomeTask(self):
		pos = self.targetPosName
		if pos is None:
			return False
		return mapMgr.formatLoc(self.mapId,pos) == self.homeLoc
		
	@property
	def isAtHome(self):
		return self.homeLoc == mapMgr.formatLoc(self.mapId,self.curTarget)
	
	@property
	def isAtChargePos(self):
		pos = self.curTarget 
		if not pos:
			return False
		return self.map.getPos(pos).isChargePoint
		
		
	#是否为人工充电
	@property
	def isHandCharge(self):
		if not self.isCharge:
			return False
		return not self.isAtChargePos
		
	@property
	def isBlocked(self):
		return self._isBlocked
	
	def isChargeAvailable(self):
		if not self.isLinked:
			return "disconnect"
		if self.status is None:
			return "no_status"
		if self._initState != 1:
			return "no_init_"+str(self._initState)
		if "loadmap_status" in self.status and self.status["loadmap_status"] != 1:
			return "no_loadmap"
		if "reloc_status" in self.status and self.status["reloc_status"] != 1:
			return "no_reloc"
		if self._isEmergency:
			return "emergency"
		if self.mapId is None:
			return "no_mapId"
		#if not mapMgr.isActived(agvs[a].mapId):
		#	continue
		if not self.curTarget:
			return "no_curTarget"			
		if self.isLock():
			return "isLocked"			
		if self.hasShelve:
			return "hasShelve"	
		if not self.canCharge:
			return "can't_charge"
		if self.isMoving():
			return "moving"
		s = self.idleSeconds
		if s < 10:
			return "no_idle_"+str(s)
		return ""
	
	def isAvailable(self):
		if not self.isLinked:
			return "disconnect"
		if self.mapId is None:
			return "no map"
		if self._initState != 1:
			return "no init"
		if self.isLock():
			if self.lockTaskId:
				return "locked["+str(self.lockTaskId)+"]"
			else:
				return "locked2["+str(self.lockApp)+"]"
		if not self.isActive:
			return "inactive"
		if self._hasAlarm:
			return "alarm"
		if self._isBlocked:
			return "blocked"
		if self._isEmergency:
			return "emergency"
		if not self._curTarget:
			return "no curPos"
		if self.status:
			#if self.status["mode"] == 0:  # 0 表示手动模式, 1 表示自动模式
			#	return False
			# 0 = FAILED(载入地图失败), 1 = SUCCESS(载入地图成功), 2= LOADING(正在载入地图)
			if "loadmap_status" in self.status and self.status["loadmap_status"] != 1:
				return "loadmap_err:"+str(self.status["loadmap_status"])
			# 0 = FAILED(重定位失败), 1 = SUCCESS(重定位正确), 2 = RELOCING(正在重定位), 3=COMPLETED(重定位完成)
			if "reloc_status" in self.status and self.status["reloc_status"] != 1:
				return "reloc_err:"+str(self.status["reloc_status"])
		return ""

	# 重定位，必须要到home点进行重定位
	def _relocHome(self):
		return
		self.requireControl()
		if self.isSeerRobot():
			agvCtrl.reloc(self.agvId)
		else:
			if self.homeLoc:
				_,loc = mapMgr.decodeLoc(self.homeLoc)
				agvCtrl.reloc2(self.agvId,loc=loc)

	def requireControl(self):
		if self.isSeerRobot():
			return
		if self.status["cmd_status"] == 1:
			return
		log.info(self.agvId,"require control")
		agvCtrl.requireControl(self.agvId)
		
	def _confirmReloc(self):
		self.requireControl()
		agvCtrl.confirmReloc(self.agvId)
		pos = mapMgr.getMap(self.mapId).getPosByPoint(self.x, self.y)
		if pos:
			self._curTarget = pos.name
			log.info(self.agvId,"set reloc",mapMgr.formatLoc(self.mapId,pos.name),"(",self.x, self.y,")")
		else:
			log.info(self.agvId,"set reloc",self.mapId,"(",self.x, self.y,")")


	@lockImp.lock(None)
	def resetLock(self,appName):
		if self.lockApp == appName:
			self.lockApp = None
			self.lockTaskId = None
			log.info("reset agv",self.agvId,"lock",appName,"taskId",self.lockTaskId)
	
	@lockImp.lock(None)
	def lock(self,taskId,appName,force):
		assert taskId
		if self.lockTaskId is not None and not force:
			if taskId != self.lockTaskId:
				raise Exception(self.agvId + "上锁失败"+",taskId:",taskId + ", occupy task:"+str(self.lockTaskId))
		self.requireControl()
		log.debug("lock: ",self.agvId,"taskId",taskId,"app",appName)
		self.lockApp = appName
		self.lockTaskId = taskId
		self.lockTicks = utility.ticks()
		self.unlockTicks = 0
 
	@lockImp.lock(None)
	def unlock(self,taskId,force=True):
		if not force:
			if self.lockTaskId and taskId != self.lockTaskId:
				if self.lockApp is not None:
					log.info("unlock failed(no force)",self.agvId,"taskIdUnlock",taskId,"taskIdLock",self.lockTaskId,"app",self.lockApp)
					raise Exception('解锁异常')
				else:
					log.debug("unlock(no force)",self.agvId,"taskId",taskId)
				return
		log.debug("unlock:",self.agvId,"taskId",self.lockTaskId,"app",self.lockApp,"force",force)
		self.lockApp = None
		self.lockTaskId = None
		self.unlockTicks= utility.ticks()
		self.lockTicks = 0
	
	@lockImp.lock(None)
	def isLockByTask(self,taskId):
		return self.taskId == taskId

	@lockImp.lock(None)
	def isLock(self):
		return self.lockApp is not None

	def isDeadLock(self):
		return self.agvElement.isBlocked or self.agvElement.isDeadlock or self.agvElement.checkFailed


	@property
	def params(self):
		if self._taskInfo is None:
			return {}
		return self._taskInfo.params
		
	@property
	def taskId(self):
		if "taskId" in self.params:
			return self.params["taskId"]
		return ""
		
	@property
	def idleSeconds(self):
		if self.idleTicks == 0:
			return 0
		return (utility.ticks() - self.idleTicks)/1000.
		
	@property
	def lockSeconds(self):
		if self.lockTicks == 0:
			return 0
		return (utility.ticks() - self.lockTicks)/1000.

	@property
	def unlockSeconds(self):
		if self.unlockTicks == 0:
			return 0
		return (utility.ticks() - self.unlockTicks)/1000.

	@property
	def taskSeconds(self):
		if self._taskTick == 0:
			return 0
		return (utility.ticks() - self._taskTick)/1000.
		
	def pause(self):
		self.pauseState = True
	
	def resume(self):
		self.pauseState = False
	
	def run(self):
		i = 0
		log.info(self.agvId,"start agvList run thread")
		while self.isThreadRunning and not utility.is_exited():
			try:
				self.isLinked = agvCtrl.checkLink(self.agvId)
				if not self.isLinked:
					# 	# if not self.isActive:
					# 	if self.agvElement is not None and self.agvElement.targetList:
					# 		self.agvElement.clear()
					# 		log.warning(self.agvId,"inactive, clear data")
					time.sleep(2)
					continue
				self.readStatus1()
				if i%10 ==0 and projectName == "fastprint":
					self.readDeviceStatus()
				i += 1
				
				# if self.pauseState:
					# time.sleep(2)
					# continue
				# self.handle()
			except Exception as e:
				log.exception(self.agvId+" thread",e)
			time.sleep(0.5)
			
	def run2(self):
		log.info(self.agvId,"start agvList run2 thread")
		while self.isThreadRunning and not utility.is_exited():
			try:
				if not self.isLinked or self.pauseState:
					time.sleep(2)
					continue
				self.handle()
			except Exception as e:
				log.exception(self.agvId+" thread2",e)
			time.sleep(0.5)
	
	def handle(self):
		if self._taskInfo is None:
			if self.idleTicks == 0:
				self.idleTicks = utility.ticks()
			self._taskTick = 0
			return 
		if self.idleTicks != 0:
			self.idleTicks = 0
		self._inHandle = True
		obj = self._taskInfo 
		if self._taskTick == 0:
			self._taskTick = utility.ticks()
		if obj.timeout and utility.ticks() - self._taskTick > int(obj.timeout)*1000.0:
			self.clearTask()
			error = self.agvId + " movePath " + "->".join(obj.params["paths"]) + "timeout, timeout=" + str(obj.timeout)+",taskId:"+obj.params['taskId']
			obj.params["exception"] = error
			obj.finishCallback(False,obj.params) 
			self._inHandle = False	
			return

		try:
			ret = obj.callback(obj.params) 
			if ret == True:  
				self._taskInfo = None
				obj.finishCallback(True,obj.params)
				self._inHandle = False	
				return 
			if ret == False: 
				log.error(self.agvId,"handle callback return false")
				self.clearTask()
				obj.finishCallback(False,obj.params)
				self._inHandle = False	
				return

			if ret is None:
				pass
		except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e1:
			msg = "handle "+self.agvId+",error:"+str(e1)
			log.exception(msg,e1) 
		except Exception as e:	 
			self.clearTask()
			log.exception("agv thread",e)
			obj.params["exception"] = str(e)
			obj.finishCallback(False,obj.params)
		self._inHandle = False	
			
	def clearTask(self,showLog=True,sendCallback=False):
		@lockImp.lock(self.m_lock)
		def clearTask1():
			#取消后，finishcallback是没有回调的
			#在unlock都会产生取消动作 
			if showLog and self.params:
				log.warning(self.agvId,"clear task,taskId=",self.taskId,"map=",self.mapId,"paths=",mapMgr.strPaths(self.agvElement.targetList),"task_status=",self.task_status)
			if self._taskInfo and self.lockTaskId and self.taskId == self.lockTaskId:
				log.warning(self.agvId,"clearTask: reset lockTaskId",self.lockTaskId,"app",self.lockApp)
				self.lockTaskId = None
			self._taskInfo = None 
			
			if obj and sendCallback:
				obj.params["exception"] = "task cancel,"+obj.params["taskId"]
				obj.finishCallback(False,obj.params) 
		
		@lockImp.lock(self.m_lock)
		def clearTask2():
			self.agvElement.clear()
			if showLog:
				log.warning(self.agvId,"clear task finish, cur=",mapMgr.formatLoc(self.mapId,self.curTarget),"task_status=",self.task_status)
			return True  
		obj = self._taskInfo
		clearTask1() 
		if not self._waitStop(g_waitStopTime): 
			if obj:
				log.error(self.agvId,"clear task failed, taskId=",obj.params["taskId"],"task_status=",self.task_status,"taskObj=",str(self._taskInfo))
			else:
				log.error(self.agvId,"clear task failed")
			#return False
		ret = clearTask2()
		self.map.unblock(self.agvId)
		return ret
		
	#是否有任务处理中 
	@lockImp.lock(None)
	def isRunning(self):
		if self._taskInfo is not None:
			return True
		return self.isMoving()
	
	#是否正在运行中 
	#@lockImp.lock(None)
	def isMoving(self): 
		# 0 = NONE, 1 = WAITING, 2 = RUNNING, 3 = SUSPENDED, 4 = COMPLETED, 5 = FAILED, 6 = CANCELED
		return self.task_status == 2 
		
	@property
	def task_status(self):
		if self.status is None:
			return -1
		if "task_status" not in self.status:
			return -1
		return self.status["task_status"]
		
	
	#等待小车停下来 
	def _waitStop(self,timeout):
		ticks = self.ticks
		for i in range(timeout):
			if not self.isLinked:
				log.warning(self.agvId,"is disconnected")
				return True 
			if not self.isActive:
				log.warning("wait stop",self.agvId,"is inactived")
				return True 
			if self.ticks != ticks and not self.isRunning(): 
				return True
			if self._isEmergency:
				agvCtrl.cancelTask(self.agvId)
			time.sleep(1)
		return not self.isRunning()
		
	@lockImp.lock(None)
	def movePath(self,timeout,checkCallback,finishCallback,params):
		assert "timeout" in params
		assert "taskId" in params
		assert "paths" in params 	
		obj = enhance.empty_class()
		obj.params = params
		obj.timeout = timeout
		obj.callback = checkCallback
		obj.finishCallback = finishCallback
		self._taskInfo = obj
		#self.agvElement.setTargetList(params["paths"])
		#if len(params["paths"]) == 1:
		#	self.agvElement.nextTargetPosName =  params["paths"][0]
		#else:
		#	self.agvElement.nextTargetPosName =  params["paths"][1]
		
		
	def move(self, loc, timeout, taskId,ignoreAngle=False):
		assert loc
		if self.curTarget == loc:
			return 
		log.debug("agvInfo:",self.agvId,mapMgr.formatLoc(self.mapId,self.curTarget),"move to",mapMgr.formatLoc(self.mapId,loc),",taskId",taskId)
		self.status["task_status"] = 2 #主动配置这个值，这样更新速度最快
		self.status["target_id"] = loc
		if self.isSeerRobot():
			agvCtrl.move(self.agvId, loc)
		else:
			agvCtrl.move(self.agvId, loc,ignoreAngle=ignoreAngle)

	def moveJackup(self, loc, timeout, taskId, use_pgv=False,ignoreAngle=False,pgv_type=1,recognize=False):
		log.info("------------------------根据agvControl中的_func来到agvList中的moveJackup---------------999-------- ")
		assert loc
		log.debug("agvInfo:",self.agvId,mapMgr.formatLoc(self.mapId,self.curTarget),"move jackup to",mapMgr.formatLoc(self.mapId,loc),",taskId",taskId)
		self.status["task_status"] = 2
		self.status["target_id"] = loc

		# use_pgv = False
		# agvCtrl-----> driver[seerAgv](agvCtrl)
		if self.isSeerRobot():
			agvCtrl.goTargetAndDoWork(self.agvId, loc, operation="JackLoad",recognize=recognize,use_pgv=use_pgv,pgv_type=pgv_type)
		else:
			agvCtrl.goTargetAndDoWork(self.agvId, loc, operation="JackLoad",recognize=recognize,use_pgv=use_pgv,ignoreAngle=ignoreAngle,pgv_type=pgv_type)

	def moveJackdown(self, loc, timeout, taskId,ignoreAngle=False):
		log.info("------------------------根据agvControl中的_func来到agvList中的moveJackdown---------------999-------- ")
		assert loc
		log.debug("agvInfo:",self.agvId,mapMgr.formatLoc(self.mapId,self.curTarget),"move jackdown to",mapMgr.formatLoc(self.mapId,loc),",taskId",taskId)
		self.status["task_status"] = 2
		self.status["target_id"] = loc
		# agvCtrl-----> driver[seerAgv](agvCtrl)
		if self.isSeerRobot():
			agvCtrl.goTargetAndDoWork(self.agvId, loc, operation="JackUnload",recognize=False,use_pgv=False)
		else:
			agvCtrl.goTargetAndDoWork(self.agvId, loc, operation="JackUnload",recognize=False,use_pgv=False,ignoreAngle=ignoreAngle)
			
	def cancelTask(self):
		return agvCtrl.cancelTask(self.agvId)
	
	# IO管理
	def readIO(self):
		return agvCtrl.readIO(self.agvId)

		
	def clearIO(self):
		agvCtrl.clearIO(self.agvId)

		
	def writeIO(self, id, status):
		agvCtrl.writeIO(self.agvId, id, status)

	def getPgv(self):
		try:
			s = agvCtrl.statusPgv(self.agvId)["pgvs"]
			if not s or len(s) == 0:
				return None
			data = s[0]
			return {"tag_value": data["tag_value"], "tag_diff_angle": data["tag_diff_angle"]}
		except (ConnectionResetError,ConnectionAbortedError,socket.timeout,IOError) as e:
			raise
		except Exception as e:
			log.exception(str(self)+' getPgv',e)
			return None

	def readDeviceStatus(self):
		status = agvCtrl.rotationDistanceStatus(self.agvId)
		if status != None:
			#查询角度 status["distance"]
			if "isRotationALarm" in status and status["isRotationALarm"] != 0:
				msg = "rotation device has alarm"
				alarm.alarmApi.alarm(moid=self.agvId, typeId=49995, desc=msg, domain="agv")
			else:
				alarm.alarmApi.clear(moid=self.agvId, typeId=49995, domain="agv")
		
		status = agvCtrl.jackDownStatus(self.agvId)
		if status != None:
			if "isJackAlarm" in status and status["isJackAlarm"] != 0:
				msg = "jack device has alarm"
				alarm.alarmApi.alarm(moid=self.agvId, typeId=49996, desc=msg, domain="agv")
				#raise Exception(msg+",action:"+self.action)
			else:
				alarm.alarmApi.clear(moid=self.agvId, typeId=49996, domain="agv")
			if "status" in status:
				if status["status"] == 1:
					if self.hasShelve:
						log.warning(self.agvId,"jack device is down")
						self.hasShelve = False
				else:
					if not self.hasShelve:
						log.warning(self.agvId,"jack device is up")
						self.hasShelve = True
	
	
	def _readStatus1(self):
		try:
			self.requireControl()
			param = None
			# if not self.isSeerRobot():
				# if self.lastUpdateClocks is None or utility.ticks() - self.lastUpdateClocks > 5*1000:
					# self.lastUpdateClocks = utility.ticks()
					# param = {"updateClock": utility.now_str()}
			status = agvCtrl.readStatus1(self.agvId,param) 
			if status:
				if "confidence" not in status or status["confidence"] is None:
					status["confidence"] = 0
				return status
		except:
			self.isLinked = False
		return None
		
	# 状态管理
	def readStatus1(self): 
		try: 
			if self._initState != 1:
				old = self._initState
				self._initState = agvCtrl.checkInit(self.agvId)
				self._alarmObj.check()
				if self._initState != 1:
					log.error("agv check init error", self._initState)
					return
			self.checkMap()
			status =self._readStatus1()  
			if not status:
				self.inited = 0
				return 
			self._alarmObj.check()
			if self.status is None: 
				log.info(self.agvId,"is online")
			self._checkLocation(status) 
			self._ticks = utility.ticks()
			
			self._checkReloc()
			self._checkAlarm()
			self._checkBattery()
			self._checkIO()
		except Exception as e: 
			if utility.is_test():
				raise e
			log.exception("readStatus1, agvId:"+self.agvId, e)

	def isSeerRobot(self):
		if self.status is None:
			return True
		return "cmd_status" not in self.status 
		
	def _checkReloc(self):
		if self.status["reloc_status"] == 0:
			log.warning(self.agvId, "relocate failed")
			self._relocHome()
		elif self.status["reloc_status"] == 3: 
			if self.inited == 0 and self.status["time"] <= 20000:
				log.info(self.agvId, "relocate finish")
				#self._reloc()
			else:
				# 此值为Home点置信度门限，需根据场景调整
				homeConfidence = 0.5
				if self.status["confidence"] < homeConfidence:
					log.warning(self.agvId, "relocate finish，confidence is low",self.status["confidence"])
					self._relocHome()
				else:
					log.info(self.agvId, "relocate successful，reloc_status " + str(self.status["reloc_status"]))
					self._confirmReloc()
					self.inited += 1
		elif self.status["reloc_status"] == 2:
			log.info(self.agvId, "is relocating")

	def _checkIO(self):
		if "DI" in self.status:
			self.readIOArray = self.status["DI"]
		if "DO" in self.status:
			self.writeIOArray = self.status["DO"]
			
	def _checkLocation(self,status):
		import mapMgr
		global locationEvent, targetLocEvent  
		#if self._curTarget:
		#	#判断x,y是否为当前点，这样判断是为了解决当前点和另一个点重合的问题 
		#	pos = mapMgr.getMap(self.mapId).getPos(self._curTarget)
		#	if pos.contains(self.x,self.y):
		#		#x,y为当前点，直接返回
		#		locationEvent.emit(self.agvId, self.x, self.y, self.status["angle"])
		#		return 
		#判断x,y所处的点位 
		if "x" not in status:
			return 
		if "y" not in status:
			return
		if "angle" not in status:
			return
		x = status["x"]
		y = status["y"]
		
		pos = mapMgr.getMap(self.mapId).getPosByPoint(x, y)
		if pos is not None and pos.name != self._curTarget: 
			if self._curTarget:
				log.debug(self.agvId,"set loc",mapMgr.formatLoc(self.mapId,pos.name),",old",self.curTarget,"(%0.2f,%0.2f)"%(x,y))
			
			lockImp.lock(self.m_lock)	
			self._curTarget = pos.name 
			self.status = status
			lockImp.release(self.m_lock)
			
			targetLocEvent.emit(self.agvId,pos.name)
		else:
			lockImp.lock(self.m_lock)	
			self.status = status
			lockImp.release(self.m_lock)

		locationEvent.emit(self.agvId, x, y, status["angle"])
		
		
	def _checkBattery(self):
		global batteryEvent
		if "charging" in self.status and self.status["charging"]:
			self.isCharge = True
		else:
			self.isCharge = False
		if "battery_level" in self.status:
			self.batteryLevel = self.status["battery_level"]
			batteryEvent.emit(self.agvId, self.status["battery_level"], self.isCharge)

			
	def _checkAlarm(self):
		def _sendAlarm(alarms, clearTypeIds):
			for a in alarms:
				for k in a:
					if k == "desc" or k == "times":
						continue 
					id = int(k)
					if id == 54018: #跳过这个告警，地图中的反光板数量不够 
						continue
					if id == 54901 or id == 54070:
						log.info("get 54901 warnings: %s"%self.agvId,alarms)
					alarm.alarmApi.alarm(moid=self.agvId, typeId=id, desc="AGV异常", domain="agv")
					if id in clearTypeIds:
						clearTypeIds.remove(id)
						if id in self._allAlarmId:
							self._allAlarmId.remove(id)
					else:
						self._allAlarmId.add(id)

		def _getBlockReason(data):
			if "block_reason" not in data:
				return "未知原因"
			code = data["block_reason"]
			if code == 0:
				return "超声检测到被阻挡"
			if code == 1:
				return "激光检测到被阻挡"
			if code == 2:
				return "防跌落传感器检测到被阻挡"
			if code == 3:
				return "碰撞传感器检测到被阻挡"
			if code == 4:
				return "红外传感器检测到被阻挡"
			if code == 5:
				return "锁车开关被触发"

		if self.status is None or not self.status:
			log.error(self.agvId,"status is None")
			return

		alarmCount = 0
		if not self.initAlarm:
			self.initAlarm = True
			clearTypeIds = getAlarmId()
		else:
			clearTypeIds = utility.clone(self._allAlarmId)
			
		if "fatals" in self.status:
			_sendAlarm(self.status["fatals"], clearTypeIds)
			alarmCount += len(self.status["fatals"])
		if "errors" in self.status:
			_sendAlarm(self.status["errors"], clearTypeIds)
			alarmCount += len(self.status["errors"])
		if "warnings" in self.status:
			_sendAlarm(self.status["warnings"], clearTypeIds)
		alarm.alarmApi.clearRange(self.agvId, clearTypeIds, "agv",force=True)
		if alarmCount == 0:
			self._hasAlarm = False
		else:
			self._hasAlarm = True

		#置信度过低报警
		if "confidence" in self.status and self.status["confidence"] is not None and self.status["confidence"]<=0.75:
			# 置信度过低超过5s，则会上报告警(alarmApi实现逻辑)
			alarm.alarmApi.alarm(moid=self.agvId, typeId=49997, desc="小车置信度小于最低阈值,当前值:" + str(self.status["confidence"]), domain="agv")
		else:
			alarm.alarmApi.clear(moid=self.agvId, typeId=49997, domain="agv")

		#障碍物报警
		if "blocked" in self.status and self.status["blocked"]:
			# 阻挡超过1分钟，则会上报告警(alarmApi实现逻辑)
			alarm.alarmApi.alarm(moid=self.agvId, typeId=49998, desc=_getBlockReason(self.status), domain="agv")
			self._isBlocked = True
		else:
			alarm.alarmApi.clear(moid=self.agvId, typeId=49998, domain="agv")
			self._isBlocked = False

		#急停报警
		if "emergency" in self.status and self.status["emergency"]:
			alarm.alarmApi.alarm(moid=self.agvId, typeId=4002, desc="急停按钮处于激活状态", domain="agv")
			self._isEmergency = True
		else:
			alarm.alarmApi.clear(moid=self.agvId, typeId=4002, domain="agv")
			self._isEmergency = False
	
	def switchMap(self,mapId,loc):
		log.warning(self.agvId,"switch map from",mapMgr.formatLoc(self.mapId,self.curTarget),"to",mapMgr.formatLoc(mapId,loc))
		#if mapId == self.mapId:
		#	return True
		agvCtrl.switchMap(self.agvId,mapId) 
		
		if not self.isSameMap(mapId):
			return False 
			
		#if utility.is_test():
		#	self.mapId = mapId
		#	self.reloc(mapId,loc) #实际运行会自动重定向 
		return True

	def reloc(self,mapId,loc):
		self.mapId = mapId
		_,loc = mapMgr.decodeLoc(loc)
		p = mapMgr.getMap(mapId).getPos(loc) 
		r = p.r
		if r is None:
			log.error("reloc error:",mapMgr.formatLoc(mapId,loc),"has no angle")
			r = 0
		log.info(self.agvId,"reloc at",loc,"(",p.x,p.y,math.degrees(r),")")
		if self.isSeerRobot():
			agvCtrl.reloc(self.agvId,pos=(p.x,p.y,r))
		else:
			self.requireControl()
			agvCtrl.reloc2(self.agvId,pos=(p.x,p.y,r))
		self._curTarget = loc
		self.readStatus1()
			
	def isSameMap(self,mapId):
		data = agvCtrl.getMapList(self.agvId)
		return mapId == data['current_map']
			
			
	def checkMap(self): 
		global g_mapIdList
		try:
			if self.mapId:
				return 
			data = agvCtrl.getMapList(self.agvId)
			mm = mapMgr.getMap(data['current_map']) #check map file
			self.mapId = data['current_map']
			if self.mapId not in g_mapIdList:
				g_mapIdList.add(self.mapId)
			log.info(self.agvId,"current map",self.mapId)
		except Exception as e:
			log.exception("checkMap "+self.agvId,e)
			
		#TODO:地图自动上传和下载未完成 
		#currentMap=data['current_map']
		#agvMaplist=data['maps'] 
		#if currentMap == self.mapId:
		#	rowData= mapMgr.getMapRawData(self.mapId)
		#	# todo:先知机器人开放MD5接口
		#	agvData= agvCtrl.downloadMap(self.agvId,currentMap)
		#	jsonStr= json.dumps(agvData)
		#	rowmd5= utility.md5(rowData)
		#	agvMd5=utility.md5(jsonStr)
		#	if rowmd5==agvMd5:
		#		log.info(self.agvId,"check map finish",self.mapId)
		#	else :
		#		log.warning(self.agvId,"sync map",self.mapId)
		#		agvCtrl.uploadMap(self.agvId,rowData)
		#else:
		#	if self.mapId in agvMaplist:
		#		agvCtrl.switchMap(self.agvId,self.mapId)
		#	else:
		#		rowData = mapMgr.getMapRawData(self.mapId)
		#		log.warning(self.agvId,"uploading map",self.mapId)
		#		agvCtrl.uploadMap(self.agvId,rowData)

	
	def createMock(self,mapId=None,startPos=None):
		assert utility.is_test()  
		if not mapId:
			mapId = self.mapId  
		assert mapId
		if 	not startPos:
			startPos = self.homeLoc 
		assert startPos
		import mapMgr 
		return agvCtrl.addAgv(self.agvId,mapMgr.getMap(mapId),startPos,self.width,self.height)
		
	def setPos(self,posName):
		import mapMgr 
		assert utility.is_test()
		self._curTarget = posName
		pos = self.map.getPos(posName)
		if not pos.ignoreDir:
			self.status["angle"] = pos.dir 
		self.status["x"] = pos.x
		self.status["y"] = pos.y
		if utility.is_test():
			agvCtrl.setPos(self.agvId,posName)
		 
	def setDI(self,id,valid):
		# log.info(f'{self.agvId} set DI {id} to {valid}')
		agvCtrl.setDI(self.agvId,id,valid)

	@lockImp.lock(None)
	def getStatus(self):
		pp = self.params
		if not pp:
			return None
		obj = {}
		obj["agvId"] = self.agvId
		obj["curTarget"] = self.curTarget
		obj["targetPosName"] = self.agvElement.targetPosName
		obj["nextTargetPosName"] = self.agvElement.nextTargetPosName
		obj["paths"] = pp["paths"]
		obj["mapId"] = pp["mapId"]
		obj["pathIndex"] = pp["pathIndex"]
		obj["pathsList"] = pp["pathsList"]
		return obj
	
	@lockImp.lock(mapMgr.g_lock)
	@lockImp.lock(None)	
	def loadStatus(self,obj):
		if obj is None:
			return False
		pp = self.params
		if not pp:
			return False
		if self.agvId != obj["agvId"]:
			return False
		pp["mapId"] = obj["mapId"]
		pp["paths"] = obj["paths"]
		pp["pathIndex"] = obj["pathIndex"]
		pp["pathsList"] = obj["pathsList"]
		self.agvElement.setTargetList(obj["paths"])
		self.agvElement.nextTargetPosName = obj["nextTargetPosName"]
		return True
		
	@lockImp.lock(None)	
	def clearStatus(self):
		self.agvElement.setTargetList(None)
		self.agvElement.nextTargetPosName = None
		pp = self.params
		if not pp:
			return
		pp["paths"] = []
		pp["pathIndex"] = 0
		pp["pathsList"] = []
		
	@lockImp.lock(mapMgr.g_lock)
	@lockImp.lock(None)	
	def updatePath(self,newPaths):
		if not newPaths:
			return False
		mapId = newPaths[0][0]
		obj = self.getStatus()
		obj = agvInfo.updateStatus(obj,mapId,newPaths)
		self.clearStatus()
		self.agvElement.unblock()
		self.loadStatus(obj)
		log.info(self.agvId,"taskId:",self.taskId,"update new path:",newPaths)
		return True
		
		
	@staticmethod
	def updateStatus(obj,mapId,newPaths):
		pp = []
		indexObj = obj["pathsList"][obj["pathIndex"]]
		indexMapId = obj["pathsList"][obj["pathIndex"]][0]
		addFlag = False
		for i,p in enumerate(obj["pathsList"]):
			if p[0] == mapId:
				if not addFlag:
					addFlag = True
					for n in newPaths:
						assert isinstance(n,(list,tuple))
						pp.append(n)
			else:
				pp.append(p)
		index = -1
		obj["pathsList"] = pp
		#for i,p in enumerate(obj["pathsList"]):
		#	if p == indexObj:
		#		index = i
		#		obj["pathIndex"] = i
		#		break
		#else:
		for i,p in enumerate(obj["pathsList"]):
			if p[0] == indexMapId:
				index = i
				obj["pathIndex"] = i
				break
		assert index != -1
		obj["paths"] = obj["pathsList"][index][1]
		obj["mapId"] = obj["pathsList"][index][0]			
		obj["nextTargetPosName"] = obj["paths"][1]			
		return obj
	
	def resetRotation(self):
		rotationApi.rotationReset(self.agvId)
		log.info(self.agvId," resetRotation")
	
	def rotationRight(self):
		rotationApi.rotationRight(self.agvId)
		log.info(self.agvId," rotationRight 90")
	
	def rotationLeft(self):
		rotationApi.rotationLeft(self.agvId,target=0)
		log.info(self.agvId," rotationLeft 90")



######### unit test #########
def testupdatestatus():
	obj = {}
	obj["agvId"] = "agv01"
	obj["curTarget"] = "1"
	obj["nextTargetPosName"] = "2"
	obj["paths"] = ["1","2","3","4"]
	obj["mapId"] = "a1"
	obj["pathIndex"] = 0
	obj["pathsList"] = [["a1",["1","2","3","4"],0],["a1",["11","22","33","44"],0],["a2",["31","32","33","34"],0],["a2",["21","22","23","24"],0]]
	agvInfo.updateStatus(obj,"a2",[["a2",["a1","a2","a3","a4"],0],]) 
	assert obj == {'agvId': 'agv01', 'curTarget': '1', 'nextTargetPosName': '2', 'paths': ['1', '2', '3', '4'], 'mapId': 'a1', 'pathIndex': 0, 'pathsList': [['a1', ['1', '2', '3', '4'], 0], ['a1', ['11', '22', '33', '44'], 0], ['a2', ['a1', 'a2', 'a3', 'a4'], 0]]}
	agvInfo.updateStatus(obj,"a1",[["a1",["b1","b2","b3","b4"],0],["a1",["c1","c2","c3"],0]])
	assert obj == {'agvId': 'agv01', 'curTarget': '1', 'nextTargetPosName': 'b2', 'paths': ['b1', 'b2', 'b3', 'b4'], 'mapId': 'a1', 'pathIndex': 0, 'pathsList': [['a1', ['b1', 'b2', 'b3', 'b4'], 0], ['a1', ['c1', 'c2', 'c3'], 0], ['a2', ['a1', 'a2', 'a3', 'a4'], 0]]}
	obj["pathIndex"] = 1
	agvInfo.updateStatus(obj,"a1",[["a1",["1","2","3","4"],0]])
	assert obj == {'agvId': 'agv01', 'curTarget': '1', 'nextTargetPosName': '2', 'paths': ['1', '2', '3', '4'], 'mapId': 'a1', 'pathIndex': 0, 'pathsList': [['a1', ['1', '2', '3', '4'], 0], ['a2', ['a1', 'a2', 'a3', 'a4'], 0]]}
	obj["pathIndex"] = 1
	agvInfo.updateStatus(obj,"a2",[["a2",["b1","b2","b3","b4"],0],["a2",["c1","c2","c3"],0]])
	assert obj == {'agvId': 'agv01', 'curTarget': '1', 'nextTargetPosName': 'b2', 'paths': ['b1', 'b2', 'b3', 'b4'], 'mapId': 'a2', 'pathIndex': 1, 'pathsList': [['a1', ['1', '2', '3', '4'], 0], ['a2', ['b1', 'b2', 'b3', 'b4'], 0], ['a2', ['c1', 'c2', 'c3'], 0]]}
	
	obj["pathIndex"] = 1
	obj["pathsList"] = [('fp20190712-1', ['LM840', 'LM841'], 8.887330578256924), ('fp20190712-1', ['LM841', 'LM840', 'LM7', 'LM87', 'CP86'], 1.2643305782569259)]
	obj["paths"] = ['LM841', 'LM840', 'LM7', 'LM87', 'CP86']
	obj2 = agvInfo.updateStatus(obj,"fp20190712-1", [('fp20190712-1', ['LM840', 'LM841'], 8.887330578256924), ('fp20190712-1', ['LM841', 'LM840', 'LM7', 'LM87', 'CP86'], 1.2643305782569259)])
	assert obj2 == {'agvId': 'agv01', 'curTarget': '1', 'nextTargetPosName': 'LM841', 'paths': ['LM840', 'LM841'], 'mapId': 'fp20190712-1', 'pathIndex': 0, 'pathsList': [('fp20190712-1', ['LM840', 'LM841'], 8.887330578256924), ('fp20190712-1', ['LM841', 'LM840', 'LM7', 'LM87', 'CP86'], 1.2643305782569259)]}
	
	
def testio():
	getAgvList()["agv1"] = agvInfo("agv1","testmap", "Y1")
	getAgv("agv1").clearIO()
	assert [False] * 16 == getAgv("agv1").readIO()
	getAgv("agv1").writeIO(10, True)
	getAgv("agv1").writeIO(10, False)
	assert [False] * 16 == agvCtrl.getAllDO("agv1")
	getAgv("agv1").writeIO(10, True)
	assert agvCtrl.getAllDO("agv1")[10]
	agvCtrl.setDI("agv1", 3, True)
	assert [False, False, False, True, False, False, False, False, False, False, False, False, False, False, False,
	        False] == getAgv("agv1").readIO()


def testalarm():
	a = agvInfo("agv1","testmap", "Y1")
	a.status = {"blocked": True, "block_reason": 1,
	            "fatals": [{"50000": 1497698400}, {"50100": 1497698400}, {"50102": 1497698400}],
	            "errors": [{"52201": 1497698402}, {"52118": 1497698404}],
	            "warnings": [{"54003": 1497698405}]}
	a._checkAlarm()
	# assert alarm.alarmApi.check_alarm("agv1",49998) #有60秒延时的，所以现在判断不出来
	assert alarm.alarmApi.check_alarm("agv1", 50000)
	assert alarm.alarmApi.check_alarm("agv1", 50100)
	assert alarm.alarmApi.check_alarm("agv1", 50102)
	assert alarm.alarmApi.check_alarm("agv1", 52201)
	assert alarm.alarmApi.check_alarm("agv1", 52118)
	assert alarm.alarmApi.check_alarm("agv1", 54003)

	a.status = {"warnings": [{"54003": 1497698405}]}
	a._checkAlarm()
	assert not alarm.alarmApi.check_alarm("agv1", 50000)
	assert not alarm.alarmApi.check_alarm("agv1", 50100)
	assert not alarm.alarmApi.check_alarm("agv1", 50102)
	assert not alarm.alarmApi.check_alarm("agv1", 52201)
	assert not alarm.alarmApi.check_alarm("agv1", 52118)
	assert alarm.alarmApi.check_alarm("agv1", 54003)
	assert not alarm.alarmApi.check_alarm("agv1", 49998)


if __name__ == '__main__': 	
	testupdatestatus()
	assert 0
	utility.run_tests()
