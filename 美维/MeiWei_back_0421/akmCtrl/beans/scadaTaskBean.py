#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @Time : 2021/4/20 9:11
# @Author : XiongLue Xie
# @File : scadaTaskBean.py

import threading
import mongodb as db
import time
import socket

from utils import toolsUtil,objectUtil,remoteIOUtil
from common import utility
from common import lock as lockImp
from dao import taskMgrDao as taskMgr
from agvCtrl import agvApi
from agvDevice import jackApi as jackApi
from agvDevice import jackMgr
from agvDevice import pgvApi as pgvApi
from agvDevice import rotationApi as rotationApi
import log
import remoteioMgr

g_taskMgr = objectUtil.getG_taskMgr()
g_allowNext = objectUtil.g_allowNext()
g_lock = toolsUtil.getG_lock()
g_lockPrepoint = {}					#前置点控制,key=mapId.loc,value=taskId
g_lockp = lockImp.create("runTasks.pre_lock")		 #锁住前置点

proName = toolsUtil.getProjectName()
zlan = objectUtil.getLan()                              #用哪一个卓蓝设备
checkTimes = objectUtil.getCheckTimes()                 #检测次数
taskTypeUnload = objectUtil.getTaskTypeUnload()         #任务类型，不同任务类型信号不同
zlanSignIterationInterval = objectUtil.getZlanSignIterationInterval()   #迭代时间间隔

#格式化地图上的点
def formatLoc(mapId,loc):
	if mapId and loc.find(".") == -1:
		return mapId + "." + loc
	return loc

class scadaTask:
	def __init__(self, source, target, devID, payloadId, priority,btTag ,taskKind):
		#每个按钮盒子都有多个值，如有需要可以修改成直接初始化就绑定按钮盒子
		self.btns = {"btns":None}       #None代表不是按钮相关的任务，就没有值
		log.info('----------------------scadaTask----------------')
		self.devID = devID
		log.info(source,target,devID)
		self.taskKind = taskKind        #上料还是下料（unhold）
		log.info(self.taskKind)
		self.btTag = btTag              #是否为Pad触发的任务
		self.isRecoverTask = False
		self.recoverState = "none"
		self.forceReleaseAgv = False  # 是否强制释放小车
		self.m_lock = threading.RLock()  # 用后面这个每次都会泄露 lockImp.create("scadaTask.lock")
		if source is None:
			return
		self.createTime = utility.now()
		self.source = source.strip()
		self.target = target.strip()
		if payloadId is not None:
			self.payloadId = payloadId.strip()
		else:
			self.payloadId = ""  # 不判断货架
		self.agvId = ""
		self.priority = priority
		self.waitLoc = None  # 等待允许进入的点信号
		self.scadaLoc = None  # 等待scada允许进入的点信号
		self.s_info = None  # 源信息
		self.t_info = None  # 目的信息
		self.param = None
		# name = "从%s运送货架%s到%s"%(source,payloadId,target)
		self.name = "从%s运送货架到%s" % (source, target)
		# 任务入库
		self.taskId = taskMgr.add(taskName=self.name, type="scadaTask", source=source, target=target, payloadId=payloadId,priority=priority)
		log.info(self.taskId)
		self._load()
		self._taskThread = None
		self.isRunning = False
		self.taskStep = "waiting"
		self.canReleaseAgv = False  # 是否可以直接释放小车
		self.forceReleaseAgv = False
		self.pda = False  # 转pda状态
		self.needRelease = False  # 是否需要release

		# if self.btTag is True:
		# 	self.initBtnDefaults()

	# self.waitTaskId = None

	# 初始所有按钮的values值设置为零
	# 有多个按钮设备，每个设备有多个值
	def setBtns(self,btnValues):
		self.btns["btns"] = btnValues

	# 初始化按钮values
	# def initBtnDefaults(self):
	# 	if self.btns["btns"] is None:
	# 		prefix = objectUtil.getBtnPrefix()
	# 		btnMachineNumber = objectUtil.getBtnMachineNum()
	# 		btnValues = {}
	# 		for i in range(btnMachineNumber):
	# 			btnValuesList = [0,0,0]
	# 			btnValues[prefix+str(i+1)] = btnValuesList
	# 		self.setBtns(btnValues)

	# 修改按下的按钮值根据按钮设备码和按钮号
	def setBtnVluesById(self,machineId,btnNumber = 0):
		self.btns["btns"][machineId][btnNumber] = 1
		log.info("****************设置按钮值**************",self.btns)

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

	def load(self, info):
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
		self.needRelease = False  # info["needRelease"]
		self.isRecoverTask = True
		if self.taskStep == "waiting":
			return
		if self.canReleaseAgv:
			log.info("recover can release agv", self)
			self.agvId = ""
			self.taskStep = "waiting"
			return
		elif self.taskStep == "moveSource":
			self.taskStep = "startMovePreSrc"
		elif self.taskStep == "loadPlayload":
			self.taskStep = "startMoveJackup"
		elif self.taskStep == "movePreSourceStep" or self.taskStep == "moveTarget":
			self.taskStep = "movePreSource"
		elif self.taskStep == "dropPayload":
			self.taskStep = "dropPayloadMove"
		return

	def __str__(self):
		a = self.agvId
		# log.info('taskid',self.taskId)
		# log.info('s_loc',self.s_info["location"])
		# log.info('s_pre',self.s_info["prepoint"])
		# log.info('t_loc',self.t_info["location"])
		# log.info('t_pre',self.t_info["prepoint"])
		# log.info('step',self.taskStep)
		if not a:
			a = "-"
		s = "task[%s][%s] %s(%s) -> %s(%s) [%s]" % (
		self.taskId, a, self.s_info["location"], self.s_info["prepoint"], self.t_info["location"],self.t_info["prepoint"], self.taskStep)
		if self.isRecoverTask:
			return "*" + s
		return s

	def __lt__(self, other):
		# 取出权重小的
		if self.priority == other.priority:
			return self.createTime < other.createTime
		return self.priority < other.priority

	# @property
	# def isInside(self):
	# 	return self.s_info["floorId"] == "fp-neiwei"

	@property
	def sPrepoint(self):
		return formatLoc(self.s_info["floorId"], self.s_info["prepoint"])

	@property
	def tPrepoint(self):
		return formatLoc(self.t_info["floorId"], self.t_info["prepoint"])

	#检查所传入的点是否位于数据库据中
	def _load(self):
		ds = db.find("u_loc_info", {"_id": {"$in": [self.source, self.target]}})
		while ds.next():
			if ds["_id"] == self.source:
				self.s_info = {
					"prepoint": ds["prepoint"].strip(),
					"location": ds["location"].strip(),
					"floorId": ds["floorId"].strip(),
					"direction": ds["direction"],
					"payloadId": ds["payloadId"],
					"p_direction": ds["p_direction"],  # 货架方向
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
			msg = "can't find source-%s and target-%s info" % (self.source, self.target)
			taskMgr.fail(self.taskId, failMsg=msg)
		elif self.s_info is None:
			msg = "can't find source-%s info" % self.source
			taskMgr.fail(self.taskId, failMsg=msg)
		elif self.t_info is None:
			msg = "can't find target-%s info" % (self.target)
			taskMgr.fail(self.taskId, failMsg=msg)

	@lockImp.lock(g_lockp)
	def islocAvailable(self, floorId, loc):
		return formatLoc(floorId, loc) not in g_lockPrepoint

	def isPreLocIdle(self, agvId, start, end):
		return agvApi.checkLineIdle(agvId, start, end)["result"]

	@lockImp.lock(g_lockp)
	def lockLoc(self, taskId, floorId, loc):
		'''锁定前置点的交管代码？'''
		key = formatLoc(floorId, loc)

		if key not in g_lockPrepoint:
			log.info("task: prepoint locked ", self.taskId, key)
			g_lockPrepoint[key] = taskId
			return True
		else:
			if g_lockPrepoint[key] == taskId:
				log.info("task: same prepoint", self.taskId, key)
				return True
			log.warning("task: prepoint locked", self.taskId, key, "failed, lock by", g_lockPrepoint[key])
			return False

	@lockImp.lock(g_lockp)
	def unlockLoc(self, floorId, loc):
		key = formatLoc(floorId, loc)
		if key in g_lockPrepoint:
			log.info("task: prepoint released ", self.taskId, key)
			del g_lockPrepoint[key]

	@lockImp.lock(g_lockp)
	def clearLoc(self):
		rr = []
		for key in g_lockPrepoint:
			if g_lockPrepoint[key] == self.taskId:
				log.info("task: prepoint released2 ", self.taskId, key)
				rr.append(key)
		for k in rr:
			del g_lockPrepoint[k]

	def allowTask(self, locId):
		self.scadaLoc = locId
		log.info(self, "allow task", locId)

	def start(self):
		if not self.isRunning:
			# recover
			if self.agvId:
				self.recoverState = "start"

			self.isRunning = True
			self._taskThread = threading.Thread(target=self._taskFunc, name="scada."
			                                                                + self.taskId)
			if self.taskStep == "waiting":
				taskMgr.start(self.taskId, failMsg="任务等待执行")
			self._taskThread.start()

	def stop(self):
		log.info(self, "stop thread, running ", self.isRunning)
		self.isRunning = False
		if self._taskThread != None:
			self._taskThread.join()
		self._taskThread = None
		self._release()

	# 格式为 stepCallback(paramObj,status),status为getTaskStatus()返回的值
	@lockImp.lock(None)
	def stepCallback(self, obj, status):
		if self.taskStep != "movePreSourceStep":
			return
		log.info("task: move step callback", self)
		pp = status["unfinishPaths"].split(",")     #把还未经过的路径的点放到pp数组
		log.info("unfinishPath:",pp)
		if pp:
			if self.s_info["prepoint"] not in pp:
				taskMgr.update(self.taskId, step="moveTarget")
				if self.s_info["prepoint"] != self.t_info["prepoint"]:
					self.unlockLoc(self.s_info["floorId"], self.s_info["prepoint"])
				self.taskStep = "moveTarget"

		# def checkFinish(self):

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
	# def onFinishNull(self,obj):
	#	log.info("task: move onFinishNull callback",self,obj)
	#

	@lockImp.lock(None)
	def onFinish(self, obj):
		log.info("task: move finish callback", self)
		if not obj["result"]:
			self.needRelease = True
			taskMgr.error(self.taskId, failMsg=obj["resultDesc"])
			return
		if self.taskStep == "moveSource" or self.taskStep == "startMovePreSrc":
			self.taskStep = "startMoveJackup"
			self.waitLoc = self.source
			taskMgr.update(self.taskId, step="waitSource", failMsg="等待scada允许进入源信号")
			return
		elif self.taskStep == "loadPlayload" or self.taskStep == "waitSource":
			log.info("***************进入onFinish.loadPlayload**********************")
			self.taskStep = "loadPlayload_readqr"
			taskMgr.update(self.taskId, failMsg="AGV下降")
			# if self.taskKind == taskTypeUnload: #下料
			if self.taskKind == 'unload': #下料
				unloadArrivalSign = "0,0,1,0"
				#发送到位信号
				#tempValue = remoteioMgr.writeDOList(zlan,unloadArrivalSign)
				log.info("*********发送下料到位信号*********",unloadArrivalSign)

				#等待下料离开信号
				for i in range(checkTimes):     #这段代码改成一个function,共四处
					#values = remoteioMgr.readDIList(zlan)
					values = {"status":[0,0,0,1,0,0,0,0]}
					# values = objectUtil.getSimulationValuesOfZlan()
					log.info("当前信号：", values)
					if values["status"][3] == 1:  # 使用第四位,(0,0,1,0,0,0,0,0)
						log.info("*****尝试离开下料位时间:", toolsUtil.getCurTime())
						break
					else:
						log.info("无离开下料位信号，继续等待：", toolsUtil.getCurTime())
						account = i + 1
						log.info("等待次数:", str(account))
						if i >= checkTimes - 1:
							log.info("****等待%s次无离开信号****" % str(checkTimes))
							print("任务标记为失败")
							break
						time.sleep(0.5)
						# time.sleep(zlanSignIterationInterval)
						continue
			return
		elif self.taskStep == "movePreSourceStep":
			#log.info("***********目的地前置点的onFinish位置***********")
			#log.info("***********当前的任务是：***********",self.taskKind)

			if self.taskKind == 'unload':   #下料
				leadUnloadSign = "0,0,0,1"
				#tempValue = remoteioMgr.writeDOList(zlan,leadUnloadSign)
				log.info("*****发送完全离开了下料点的信号*****",leadUnloadSign)
				# log.info("*****三个工位点移动*****")
				# log.info("*****移动到下料工作站1*****")
				self.taskStep = "move2workstation1"

			#等待对接信号，有信号了就进去（还需要定位精度）
			#模拟等待接收信号
			else :  #上料
				log.info("************进入前置点等待上料*************")
				log.info("***********等待进入信号**************")
				for i in range(checkTimes):
					#values = remoteioMgr.readDIList(zlan)   #上料可以进，实际
					values = objectUtil.getSimulationValuesOfZlan()   #上料可以进，测试
					log.info("*****等待进入信号！",toolsUtil.getCurTime())
					print("当前信号：", values)
					if values["status"][0] == 1:  # 根据现场实际信号修改
						print("进入上料位置:", toolsUtil.getCurTime())
						break
					else:
						print("无进入信号，继续等待：", toolsUtil.getCurTime())
						account = i + 1
						print("等待次数:", account)

					if i >= 15 - 1:
						print("****等待%s次无进入****" % str(15))
						break
					time.sleep(zlanSignIterationInterval)
				self.taskStep = "dropPayloadMove"
			return

		elif self.taskStep == "move2workstation1_onfinish":
			log.info("****移动到下料工作站1****")
			# self.taskStep = "move2workstation2"
			self.taskStep = "dropPayloadMove"
			for i in range(checkTimes):
				#log.info("***工作站1等待放行信号，", toolsUtil.getCurTime(),objectUtil.getSeats(),"次数:",i)
				log.info("***工作站1等待放行信号，", self.btns["btns"], toolsUtil.getCurTime())
				#if objectUtil.getSeats()["bt_1"] != 1 :
				# self.btns = {"btns": None}
				# if self.btns["btns"]["bt_1"][0] != 1:      #假设是按钮
				log.info('读取按钮放行信号---------------->',g_allowNext[self.devID])
				if g_allowNext[self.devID] == 0:      #假设是按钮
					#log.info("***工作站1等待放行信号，", self.btns["btns"],toolsUtil.getCurTime())
					time.sleep(3)
				elif g_allowNext[self.devID] == 1:
					# g_allowNext.pop(self.devID,'404')
					log.info("***工作站1放行，", toolsUtil.getCurTime())
					log.info('查看按钮盒的信号情况是否被清空----------------->',g_allowNext)
					break
				elif g_allowNext[self.devID] == 2:
					g_allowNext.pop(self.devID,'404')
					log.info("***工作站1取消任务，", toolsUtil.getCurTime())
					log.info('查看按钮盒的信号情况是否被清空----------------->',g_allowNext)
					break
			return

		elif self.taskStep == "move2workstation2_onfinish":
			log.info("****移动到下料工作站2****")
			self.taskStep = "move2workstation3"
			for i in range(checkTimes):
				#log.info("***工作站2等待放行信号，", toolsUtil.getCurTime(),objectUtil.getSeats(),"次数:",i)
				#if objectUtil.getSeats()["bt_2"] != 1 :
				log.info("***工作站2等待放行信号，", self.btns["btns"], toolsUtil.getCurTime())
				if self.btns["btns"]["bt_1"][1] != 1:      #这里需要修改成self.btns["btns"]["bt_2"] !=1
					#log.info("***工作站1等待放行信号，", toolsUtil.getCurTime())
					time.sleep(1.5)
				else:
					log.info("***工作站2放行，", toolsUtil.getCurTime())
					break
			return

		elif self.taskStep == "move2workstation3_onfinish":
			log.info("****移动到下料工作站3****")
			self.taskStep = "dropPayloadMove"
			for i in range(checkTimes):
				# log.info("***工作站2等待放行信号，", toolsUtil.getCurTime(),objectUtil.getSeats(),"次数:",i)
				# if objectUtil.getSeats()["bt_3"] != 1 :
				log.info("***工作站3等待放行信号，", self.btns["btns"], toolsUtil.getCurTime())
				if self.btns["btns"]["bt_1"][2] != 1:  # 这里需要修改成self.btns["btns"]["bt_3"][2] !=1
					#log.info("***工作站1等待放行信号，", toolsUtil.getCurTime())
					time.sleep(1.5)
				else:
					log.info("***工作站3放行，", toolsUtil.getCurTime())
					break
			return

		elif self.taskStep == "moveToPreSrc_onfinish":
			# if self.taskStep == taskTypeUnload: #上料，相当于source前置点，这里约定人工放东西不交互
			if self.taskKind == 'load': #上料，相当于source前置点，这里约定人工放东西不交互
				log.info("***********上料，已到达source前置*************")
				#等待工人手动上料的时间
				#time.sleep(3)
				self.taskStep = "startMoveJackup"

			else : #下料，需要和机器交互，可能需要修改step,因为这里下一步一定要是架子下降的状态
				log.info("***********下料，到达source前置点，等待进入信号*************")
				#n = checkTimes
				for i in range(checkTimes):
					#values = remoteioMgr.readDIList(zlan)
					values = objectUtil.getSimulationValuesOfZlan()
					log.info("当前信号：", values)
					if values["status"][2] == 1:  # 使用第三位,(0,0,1,0,0,0,0,0)
						# log.info("尝试取料时间:", toolsUtil.getCurTime())
						log.info("准备进入目标点位取料:", toolsUtil.getCurTime())
						break
					else:
						log.info("无料，继续等待：", toolsUtil.getCurTime())
						account = i + 1
						log.info("等待次数:", str(account))
						if i >= checkTimes - 1:
							log.info("****等待%s次无料****" % str(checkTimes))
							print("任务标记为失败")
							break
						time.sleep(zlanSignIterationInterval)
						continue
				self.taskStep = "comeInUnloadPosition_jackdown"
			#可以进去上料位的逻辑（状态码）
			#self.taskStep = "startMoveJackup"
			return
		elif self.taskStep == "moveTarget":
			taskMgr.update(self.taskId, step="waitTarget", failMsg="等待scada允许进入目标信号")
			self.taskStep = "waitTarget"
			self.waitLoc = self.target
			return
		elif self.taskStep == "dropPayload":
			#if self.taskKind == "unload":   #下料
			# if self.taskKind == taskTypeUnload:   #下料
			if self.taskKind == 'unload':   #下料
				self.taskStep = "dropPayloadJackdown"
				return
			else:       #上料出来的时候需要跟机器交互
				log.info("******************进入上料位到位********************")
				#需要商量上升还是下降
				#self.taskStep = "dropPayloadJackdown"
				loadArrivalSign = "1,0,0,0"
				#loadArrivalSignReturn = remoteioMgr.writeDOList(zlan,loadArrivalSign)
				print("发送到达上料点信号：", loadArrivalSign)

				#上料到位等待可以离开的信号
				for i in range(checkTimes):
					#values = remoteioMgr.readDIList(zlan)
					values = objectUtil.getSimulationValuesOfZlan()
					print("当前信号：", values)
					if values["status"][1] == 1:  # 根据现场实际信号修改
						print("等待离开上料点的信号:", toolsUtil.getCurTime())
						break
					else:
						print("无离开上料点信号，继续等待：", toolsUtil.getCurTime())
						account = i + 1
						print("等待次数:", account)

						if i >= checkTimes - 1:
							print("****等待%s次无上料点离开信号，开走****" % str(checkTimes))
							# 是否标记为失败，还是正常走
							break
						time.sleep(zlanSignIterationInterval)
						continue
				self.taskStep = "moveoutFromLoadPoint"  # 从上料位出去
				#taskMgr.update(self.taskId, failMsg="放下货架，旋转顶升机构初始化")
				return

		# 从上料位出去完成
		elif self.taskStep == "moveoutFromLoadPoint_onfinish":
			self.taskStep = "dropPayloadJackdown"
			taskMgr.update(self.taskId, failMsg="放下货架，旋转顶升机构初始化")
			log.info("***************离开上料点***********")
			leaveSign = "0,1,0,0"
			#remoteioMgr.writeDOList(zlan,leaveSign)
			log.info("*************发送离开上料点信号***********",leaveSign)
			return

	def handleRecover(self):
		if not self.isRecoverTask:
			return True
		if self.recoverState == "none":
			return True
		if self.agvId:
			try:
				if not agvApi.isAvailable(self.agvId):
					log.warning("recover " + str(self), "no available", self.recoverState)
					return False
				agvApi.lock(self.agvId, self.taskId)
				# log.warning("recover "+str(self),"end lock",self.recoverState)
				self.recoverState = "none"
			except Exception as e:
				self.recoverState = "none"
				log.exception("recover " + str(self), e)
				taskMgr.fail(self.taskId, failMsg="recover can't lock " + self.agvId)
				return False
			log.info(self, "recover lock", self.agvId)
			return True

	def setSInfoMsg(self):
		'''上下料进入到source时候的信息设置,后期改成传参全部动态做高级抽象减少冗余，这里调用两次故最低级抽象出来'''
		self.param["location"] = self.s_info["location"]
		self.param["floorId"] = self.s_info["floorId"]
		self.param["taskId"] = self.taskId + "_3"
		self.param["direction"] = self.s_info["direction"]
		self.param["p_direction"] = self.s_info["p_direction"]
		return True

	@lockImp.lock(None)
	def handle(self):
		log.info('===========================>',self.taskStep)
		if self.taskStep == "waiting":
			if not self.islocAvailable(self.s_info["floorId"], self.s_info["prepoint"]):
				return False
			self.taskStep = "waitForAgv"
			taskMgr.update(self.taskId, failMsg="等待分配小车")
			return True
		elif self.taskStep == "waitForAgv":
			self.param = {
				"taskId": self.taskId,
				"location": self.s_info["prepoint"],
				# "location": self.s_info["location"],
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
			log.info(self, "apply", agvId)
			self.canReleaseAgv = True
			self.agvId = agvId
			self.taskStep = "initJackdown"
			self.param["agvId"] = self.agvId
			taskMgr.update(self.taskId, agvId=self.agvId, failMsg="成功分配小车%s,检测顶升下降" % self.agvId)
			return True
		elif self.taskStep == "initJackdown":
			self.param["taskId"] = self.taskId + "_1"
			self.param['isRotate'] = ''
			if not self._jackDown():
				return False
			log.info('初始化小车的顶升---执行self._jackdown----下降')
			# self.taskStep = "waitSrcPreLoc"
			# self.taskStep = "startMovePreSrc"
			#self.taskStep = "startMoveJackup"
			self.taskStep = "moveToPreSrc"
			# taskMgr.update(self.taskId,failMsg="等待%s前置点锁"%self.source)
			taskMgr.update(self.taskId, failMsg="前往%s工位点拉取货架" % self.source)
			#taskMgr.update(self.taskId, failMsg="前往%s工位点的前置点拉取货架" % self.source)
			return True

		elif self.taskStep == "moveToPreSrc":
			self.param["floorId"] = self.s_info["floorId"]
			self.param["taskId"] = self.taskId + "_2"
			self.param["location"] = self.s_info["prepoint"]
			self.taskStep = "moveToPreSrc_onfinish"  # 这个通过onfinish跳转
			self._moveAgv()
			log.info("移动到source的前置点",self.s_info["prepoint"])
			return True

		# 美维上料才用的，下料不用，顶升拉料
		elif self.taskStep == "startMoveJackup":
			self.setSInfoMsg()
			self.taskStep = "loadPlayload"
			self._moveJackup()
			#self.taskStep = "loadPlayload"
			log.info("==============================runTasks._moveJackup()结束====================================")
			log.info("****当前的状态为：",self.taskStep)
			return True


		elif self.taskStep == "comeInUnloadPosition_jackdown":
			self.canReleaseAgv = False
			if not self._jackDown():
				return False
			self.taskStep = "comeInUnloadPosition"
			taskMgr.update(self.taskId, failMsg="顶升下降，准备进入%s" % self.target)
			return True



		#下料进去，架子必须是降的状态
		elif self.taskStep == "comeInUnloadPosition":
			self.setSInfoMsg()
			self.taskStep = "loadPlayload"
			self._moveAgv()
			# log.info("==============================runTasks.comeInUnloadPosition结束====================================")
			log.info("****当前的状态为：", self.taskStep)

			return True

		elif self.taskStep == "loadPlayload_readqr":  # 这个通过onFinish跳转 loadPlayload -> loadPlayload_readqr
			if self.payloadId:  # 识别二维码
				p = self._getPgv()
				taskMgr.update(self.taskId, errorno=p['errorno'], errormsg=p['errormsg'])
				if p['errorno'] != 0 or p['tag_value'] == "":
					# 二维码失败就任务整个结束
					log.info("******二维码失败，任务置为失败*******")
					self.taskStep = "failed"
					self.canReleaseAgv = True
					taskMgr.fail(self.taskId, failMsg=p['errormsg'])
					return False
			self.taskStep = "loadPlayload_jackup"
			return True

		elif self.taskStep == "loadPlayload_jackup":
			self.canReleaseAgv = False
			#很多余的判定
			# if not self._jackUp():
			# 	return False
			self.taskStep = "waitDestPreLoc"
			taskMgr.update(self.taskId, failMsg="等待%s工位点锁" % self.target)
			return True

		elif self.taskStep == "waitDestPreLoc":
			# if not self.lockLoc(self.taskId,self.t_info["floorId"],self.t_info["prepoint"]):
			if not self.lockLoc(self.taskId, self.t_info["floorId"], self.t_info["location"]):
				return False
			#   self.taskStep = "waitDestPreLoc1"
			self.taskStep = "movePreSource"
			# self.taskStep = "dropPayloadMove"
			# if self.taskKind != objectUtil.getTaskTypeUnload():
			if self.taskKind != 'unload':
				log.info("*****上料，必须在到上料口之前就降下架子*****")
				if not self._jackDown():
					log.info("*****上料前降下架子失败，任务标记为失败*****",toolsUtil.getCurTime())
					return False
			taskMgr.update(self.taskId, failMsg="前往%s工位点放下货架" % (self.t_info["location"]))
			return True

		#实际是目的地前置点
		elif self.taskStep == "movePreSource":
			self.param["floorId"] = self.t_info["floorId"]
			self.param["taskId"] = self.taskId + "_4"
			self.param["location"] = self.t_info["prepoint"]
			#	self.taskStep = "dropPayloadMove"
			log.info("*************进入目的地的前置点***********")
			self.taskStep = "movePreSourceStep"  # 这个通过onfinish跳转
			self._moveAgv()

			return True

		# 去到目的地前置点跳到这步
		# 放行需要走多三个点，均在onFinish中接收信号放行
		# 这三个点写到配置文件中去,理论上最好是前后点自己建立关系，而不是靠人去记住来改，框架待优化
		elif self.taskStep == "move2workstation1":
			self.param["floorId"] = self.t_info["floorId"]
			self.param["taskId"] = self.taskId + "_5"
			self.param["location"] = "3"
			self.taskStep = "move2workstation1_onfinish"
			self._moveAgv()
			#log.info("工位1接收信息放行,当前任务状态:",self.taskStep)
			return True

		elif self.taskStep == "move2workstation2":
			log.info("进入move2workstation2")
			self.param["floorId"] = self.t_info["floorId"]
			self.param["taskId"] = self.taskId + "_5"
			self.param["location"] = "11"
			self.taskStep = "move2workstation2_onfinish"
			#log.info("工位2接收信息放行")
			self._moveAgv()

			return True

		elif self.taskStep == "move2workstation3":
			self.param["floorId"] = self.t_info["floorId"]
			self.param["taskId"] = self.taskId + "_6"
			self.param["location"] = "12"
			self.taskStep = "move2workstation3_onfinish"
			#log.info("工位3接收信息放行")
			self._moveAgv()
			return True


		elif self.taskStep == "dropPayloadMove":
			self.param["location"] = self.t_info["location"]
			self.param["floorId"] = self.t_info["floorId"]
			if self.taskKind == "unload":
				self.param["taskId"] = self.taskId + "_5"
			else:
				self.param["taskId"] = self.taskId + "_7"
			self.param["direction"] = self.t_info["direction"]
			#self.taskStep = "dropPayload"  # 这个通过onFinish跳转 dropPayload -> dropPayloadJackdown
			self.taskStep = "dropPayload"  # 这个通过onFinish跳转 dropPayload -> moveoutFromLoadPoint    dropPayloadJackdown
			#self._moveJackdown()
			self._moveAgv()
			taskMgr.update(self.taskId, step="dropPayload")
			#self.taskStep = "dropPayload"  # 这个通过onFinish跳转 dropPayload -> dropPayloadJackdown
			log.info("当前步骤：",self.taskStep)
			return True

		#上料用的，出来先到target前置点
		elif self.taskStep == "moveoutFromLoadPoint":
			self.param["location"] = self.t_info["prepoint"]
			self.param["floorId"] = self.t_info["floorId"]
			self.param["direction"] = self.t_info["direction"]
			if self.taskKind == "unload":
				self.param["taskId"] = self.taskId + "_6"
			else:
				self.param["taskId"] = self.taskId + "_8"
			self.taskStep = "moveoutFromLoadPoint_onfinish"
			#self._moveJackdown()
			self._moveAgv()
			return True
		elif self.taskStep == "dropPayloadJackdown":
			if not self._jackDown():
				return False
			self.taskStep = "dropPayloadReset"
			return True
		elif self.taskStep == "dropPayloadReset":
			# if not self._rotationBack():
			# 	# self.needRelease = True
			# 	return False
			# self._jackDown() #旋转会带有顶伸，所以还需要jackDown
			self.canReleaseAgv = True
			self.taskStep = "finish"
			taskMgr.finish(self.taskId, step="finish", failMsg="任务成功")
			return True
		else:
			# 在onfinish跳转
			return True

	@utility.catch
	def _taskFunc(self):
		log.info('task: start', self)
		isRelease = False

		while self.isRunning:
			if not self.handleRecover():
				time.sleep(2)
				continue

			old = self.taskStep
			try:
				if self.needRelease:  # onFinish异常失败，需要人工来处理
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
					log.info(str(self), self.taskStep, "error")
					time.sleep(2)
					continue
				if old != self.taskStep:
					log.debug(str(self), old, "->", self.taskStep)
			except (ConnectionResetError, ConnectionAbortedError, socket.timeout, IOError) as e:
				log.exception("taskFunc:" + str(self), e)
				time.sleep(2)
				continue
			except Exception as e:
				log.exception("taskFunc2:" + str(self), e)
				taskMgr.error(self.taskId, failMsg=str(e))
				break
			g_taskMgr.save()
			time.sleep(0.3)

		if not isRelease:
			self._release()
		if self.btTag:
			log.info("**********上一个按钮任务结束，重置状态，允许继续接受按钮任务************")
			objectUtil.setButtonTask(False)

		log.info("运行结束，重置running")
		self.isRunning = False
		log.info("task: stop", self)

	@lockImp.lock(g_lock)
	def _release(self):
		try:
			if self.agvId:
				releaseFlag = self.canReleaseAgv
				if self.forceReleaseAgv:
					releaseFlag = True
				# log.info(self,self.agvId,"release task, release agv",releaseFlag)
				log.info(self, self.agvId, "release task, release agv", releaseFlag, self.canReleaseAgv,
				         self.forceReleaseAgv)
				if releaseFlag:
					ret = agvApi.isLocked(self.agvId, self.taskId)
					agvApi.release(self.agvId, self.taskId, force=False)
					#g_relese_agvs.add(self.agvId)
					if ret:
						log.info(self, "let", self.agvId, "gohome")
						agvApi.goHome(self.agvId, force=False, timeout=60 * 60 * 3)
						#agvApi.goHome1(self.agvId, force=False, timeout=60 * 60 * 3)
					else:
						log.info(self, self.agvId, "lock by other taskId, no gohome")
					self.agvId = ""
		except Exception as e:
			log.exception(str(self) + "task release", e)
		self.clearLoc()

	# 过滤某些工位 如果不是04车 agvapi那里加入exclude
	def _filterFunc(self, agvId, mapId, loc, payload):
		if agvId in ["AGV30", "AGV31", "AGV32", "AGV33", "AGV34", "AGV35", "AGV36"]:
			return True
		else:
			return False

	# @lockImp.lock(g_lock)
	def _applyAgv(self):
		try:
			log.info('================叫车======================')
			return agvApi.apply(taskId=self.param["taskId"], mapId=self.param["floorId"], loc=self.param["location"],
			                    filterFunc=self._filterFunc, timeout=10)  # filterFunc=self._filterFunc,
		except Exception as e:
			#		lockImp.release(g_lock)
			log.warning("[%s] apply agv failed: %s" % (str(self), str(e)))
			# taskMgr.update(self.taskId, errormsg='waiting to apply AGV!', errorno=11)
			return None

	# @lockImp.lock(g_lock)
	def _moveAgv(self, stepCallback=None):
		try:
			self.param["timeoutSec"] = 86400
			if "seer_jackup" in self.param:
				del self.param["seer_jackup"]
			# self.waitTaskId = self.param["taskId"]
			# move这个方法设置了回调
			log.info("***************调用move方法")
			tempLoc = self.param["floorId"] + '.' + self.param["location"]
			#agvApi.move(self.agvId, tempLoc, self.onFinish, self.param, stepCallback=stepCallback)
			agvApi.move(self.agvId, tempLoc, self.onFinish, self.param)
			return True
		except (ConnectionResetError, ConnectionAbortedError, socket.timeout, IOError) as e:
			raise
		except Exception as e:
			raise e
			log.info("*********************什么报错啊",str(e))
			taskMgr.error(self.taskId, failMsg=str(e))
			return False

	# @lockImp.lock(g_lock)
	def _moveJackup(self):
		self.param["timeoutSec"] = 86400
		self.waitTaskId = self.param["taskId"]
		log.info("***************调用_moveJackup方法")
		tempLoc = self.param["floorId"] + '.' + self.param["location"]
		#agvApi.moveJackup(self.agvId, tempLoc, self.onFinish,self.param, self.stepCallback, use_pgv=False, pgv_type=1)
		#agvApi.moveJackup(self.agvId, tempLoc, self.onFinish,self.param, use_pgv=True)
		agvApi.moveJackup(self.agvId, tempLoc, self.onFinish,self.param)

	# @lockImp.lock(g_lock)
	def _moveJackdown(self):
		self.param["timeoutSec"] = 86400
		# self.waitTaskId = self.param["taskId"]
		log.info("***************调用_moveJackdown方法")
		tempLoc = self.param["floorId"] + '.' + self.param["location"]
		agvApi.moveJackdown(self.agvId, tempLoc, self.onFinish, self.param)

	# @lockImp.lock(g_lock)
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
				return {'tag_value': '', 'errorno': -1, 'errormsg': "read qrcode failed"}
			if pgv_msg['tag_value'] == 0:
				return {'tag_value': '', 'errorno': -2, 'errormsg': 'there is no payload'}

			ds = db.find_one("u_pgv_info", {"pgvId": str(pgv_msg['tag_value'])})
			if ds is None:
				errormsg = 'The tag_value is %s but there is no match data' % str(pgv_msg['tag_value'])
				return {'tag_value': pgv_msg['tag_value'], 'errorno': -3, 'errormsg': errormsg}

			log.info(
				'task: read qrcode:%s, payloadId:%s, db:%s' % (pgv_msg['tag_value'], self.payloadId, ds["payloadId"]))

			if str(ds["payloadId"]) == str(self.payloadId):
				return {'tag_value': ds["payloadId"], 'errorno': 0, 'errormsg': ""}
			else:
				errormsg = 'Not match: the tag_value is %s but the payloadId is %s' % (ds["payloadId"], self.payloadId)
				return {'tag_value': ds["payloadId"], 'errorno': -4, 'errormsg': errormsg}
		except (ConnectionResetError, ConnectionAbortedError, socket.timeout, IOError) as e:
			raise
		except Exception as e:
			log.exception(str(self) + ' getPgv', e)
			return {'tag_value': '', 'errorno': -1, 'errormsg': str(e)}

	def _rotationLeft(self, target=90):
		try:
			rotationApi.rotationLeft(self.agvId, target=target)
			return True
		except (ConnectionResetError, ConnectionAbortedError, socket.timeout, IOError) as e:
			raise
		except Exception as e:
			taskMgr.update(self.taskId, errormsg='rotate left %d error' % target, errorno=51)
			log.exception(str(self) + ' rotationLeft', e)
			return False

	def _rotationRight(self, target=90):
		try:
			rotationApi.rotationRight(self.agvId, target=target)
			return True
		except (ConnectionResetError, ConnectionAbortedError, socket.timeout, IOError) as e:
			raise
		except Exception as e:
			taskMgr.update(self.taskId, errormsg='rotate right %d error' % target, errorno=52)
			log.exception(str(self) + ' rotationRight', e)
			return False

	def _jackUp(self):
		try:
			log.info(self, "执行了------------------------->_jackUp")
			jackApi.jackUpOld(self.agvId, timeoutSec=90)
			#jackMgr.jackUpOld(self.agvId,90)
			return True
		except (ConnectionResetError, ConnectionAbortedError, socket.timeout, IOError) as e:
			raise
		except Exception as e:
			log.exception(str(self) + ' jackup', e)
			return False

	# 这个可能会有有问题，协议不匹配
	def _jackDown(self):
		try:
			log.info(self, "执行了------------------------->_jackDown")
			jackApi.jackDownOld(self.agvId, timeoutSec=90)
			#jackMgr.jackDownOld(self.agvId,  90)
			return True
		except (ConnectionResetError, ConnectionAbortedError, socket.timeout, IOError) as e:
			raise
		except Exception as e:
			log.exception(str(self) + ' jackDown', e)
			return False

	# 角度归位
	def _rotationBack(self):
		log.info(self, "rotationClear")
		return rotationApi.rotationClear(self.agvId)

	def _rotation(self):
		# 转角度
		log.debug(str(self), self.agvId, "rotate", self.s_info['p_direction'], "->", self.t_info['p_direction'])
		if self.s_info['p_direction'] == self.t_info['p_direction']:
			return True
		angle = self.t_info['p_direction'] - self.s_info['p_direction']
		self.param["isRotate"] = str(angle)
		log.debug(self.agvId, 'Rotate:', self.param['isRotate'])

		if toolsUtil.getAgvType(self.agvId)['jackType'].lower() == "io":
			if abs(angle) == 180:
				return self._rotationRight(180)
			elif angle == -90:
				return self._rotationLeft(270)
			elif angle == 270:
				return self._rotationRight(270)
			elif angle == -270 or angle == 90:
				return self._rotationRight(90)
			else:
				log.error("unknow angle", angle, self.agvId)
		else:
			if abs(angle) == 180:
				return self._rotationRight(180)
			elif angle == 270 or angle == -90:
				return self._rotationLeft(90)
			elif angle == -270 or angle == 90:
				return self._rotationRight(90)
			else:
				log.error("unknow angle", angle, self.agvId)