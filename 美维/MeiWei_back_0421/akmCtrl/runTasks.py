# coding: utf-8
# author: pengshuqin
# date: 2019-10-16
# desc: 任务处理
import socket
import threading
import time

import local
import setup

if __name__ == '__main__':
	setup.setCurPath(__file__)

#import log
#import enhance
import utility
import mytimer
import lock as lockImp
import mongodb as db
import taskMgr
import agvCtrl.agvApi as agvApi
# import agvDevice.rollerApi as rollerApi
import agvDevice.rollerPlusApi as rollerPlusApi
import agvDevice.audioApi as audioApi
import remoteio.remoteioApi as ioApi

from beans import scadaTaskBean

# OUT1 = 1
# OUT2 = 2
# IN1 = 0
# IN2 = 1
# IN3 = 2
# IN4 = 3
# FLOOR1 = 1
# FLOOR2 = 2
# MAX_LINE_AGV_NUM = 1
# g_taskType = {
# 	"load": {"sName": "sName", "tName": "tName", "source": "loc1", "target": "loc2", "s_io": "io1", "t_io": "io2",
# 			 "floor": FLOOR1, "startSignal": IN1, "finishSignal": IN2, "arrivedSignal": IN3, "overSignal": IN4},
# }
#
# g_taskDict = {}
# g_lastType = {}
# g_init = None
# g_lock = threading.RLock()
# g_slock = threading.RLock()
# g_ioStatus = {}
# g_first = True

@lockImp.lock(g_slock)
def onStatusChanged(io, values):
	global g_ioStatus
	g_ioStatus[io] = values


@lockImp.lock(g_slock)
def getStatus(io):
	global g_ioStatus
	if io in g_ioStatus:
		return g_ioStatus[io]


@lockImp.lock(g_lock)
def addTask(line, taskType, taskInfo):
	global g_init
	task = akmTask(line, taskType, taskInfo)
	g_taskMgr.add(task)
	# log.info('%s Got a task %s: %s'%(line,task.taskId, task))
	return task.taskId


@lockImp.lock(g_lock)
def addTaskByPad(source,target,payloadId,priority):
	global g_taskQueue,g_taskInsideQueue
	log.info(f'Scada send a task to the server from { source } to { target } payloadId: { payloadId }')
	task = scadaTaskBean.scadaTask(source,target,payloadId,int(priority))
	g_taskMgr.add(task)
	log.info('task cmd: got a task from scada',task)
	return task.taskId


@lockImp.lock(g_lock)
def failTask(taskId):
	log.warning('task cmd: fail task', taskId)
	t = g_taskMgr.getTask(taskId)
	lockImp.release(g_lock)
	if t is not None:
		t.canReleaseAgv = True
		t.stop()
	taskMgr.fail(taskId, failMsg="task fail by PDA")


@lockImp.lock(g_lock)
def finishTask(taskId):
	log.warning('task cmd: finish task', taskId)
	t = g_taskMgr.getTask(taskId)
	lockImp.release(g_lock)
	if t is not None:
		t.canReleaseAgv = True
		t.stop()
	taskMgr.finish(taskId, step="finish")

def cancel(taskId):
	t = g_taskMgr.getTask(taskId)
	if t is not None:
		g_taskMgr.cancelTasks.add(taskId)
		if t.isRunning:
			if t.agvId:
				agvApi.cancelTask(t.agvId)
			t.stop()


@lockImp.lock(g_lock)
def getTaskStatus():
	return g_taskMgr.getTaskStatus()



# 无任务时取下一个任务
# @lockImp.lock(g_lock)
# def getTask1():
# global g_taskQueue,r_task
# if g_taskQueue == []:
# return
# for task in g_taskQueue:
# agvList = agvApi.getAgvStatusList(task.map)["list"]
# for id in agvList:
# if agvList[id]["isActive"]:#and not agvList[id]["charging"]:
# isAgvRight = task.filterFuncB(id, None, None,None, taskType=task.type, isOther=True)
# if isAgvRight:
# r_task.append(task)
# g_taskQueue.remove(task)
# return

# True为回Home点，False不回
@lockImp.lock(g_lock)
def checkLineTask(line):
	global g_taskDict
	if g_taskDict:
		if g_taskDict[line]:
			return False
		else:
			return True
	return True
# 	for task in g_taskQueue:
# 		isAgvRight = task.filterFuncB(agvId, None, None, None, taskType=task.type, isOther=True)
# 		if isAgvRight and task.line == preTask.line and task.loc1 == preTask.loc1:
# 			task.agvId = preTask.agvId
# 			r_task.append(task)
# 			g_taskQueue.remove(task)
# 			return False
# 	return True

#@mytimer.interval(500)
@lockImp.lock(g_lock)
def run():
	global g_taskDict, g_taskMgr, g_init, g_lastType, g_first
	# log.info("g_taskDict:",g_taskDict,"g_taskMgr:",g_taskMgr,"g_lastType:",g_lastType)
	print("标记位",g_init)
	if g_init is None:
		if g_first:
			time.sleep(5)
			g_first = False
		g_init = "akmTask"
		agvApi.init("akmTask")
		db.delete_many("u_agv_payload", '')
	for line in g_taskDict:
		while g_taskMgr.runningCount(line) < MAX_LINE_AGV_NUM and g_taskDict[line] != []:
			task = None
			for t in g_taskDict[line]:
				if t.type != g_lastType[line]: # 满空交换
					task = t
					break
			if task is None:
				task = g_taskDict[line].pop(0)
			else:
				g_taskDict[line].remove(task)
			if not g_taskMgr.isCancelTask(task.taskId):
				g_lastType[line] = task.type
				task.run()
			# TODO
			# 完全没任务了，才让小车回home点
			# if g_taskMgr.runningCount(line) == 0 and g_taskDict[line] == []:
			# 	agvId = g_relese_agvs[line]
			# 	if agvId:
			# 		log.info("let",agvId,"gohome")
			# 		agvApi.goHome(agvId,force=True)

	g_taskMgr.removeFinishTask()


class akmTaskMgr:
	def __init__(self):
		self.tasks = {}
		self.cancelTasks = set()

	def add(self, task):
		self.tasks[task.taskId] = task
		if task.line not in g_taskDict:
			g_taskDict[task.line] = []
			g_lastType[task.line] = None
		g_taskDict[task.line].append(task)

	def getTask(self, taskId):
		if taskId in self.tasks:
			return self.tasks[taskId]
		return None

	def runningCount(self, line):
		ret = 0
		for t in self.tasks.values():
			if t.isRunning and t.line == line:
				ret += 1
		return ret

	def removeFinishTask(self):
		rr = []
		for t in self.tasks.values():
			if not t.isRunning and t.step != "waiting":
				rr.append(t.taskId)

		for id in rr:
			log.debug("task: delete task", id)
			del self.tasks[id]
			if id in self.cancelTasks:
				self.cancelTasks.remove(id)

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


	def isCancelTask(self, taskId):
		return taskId in self.cancelTasks

	def cancel(self, taskId):
		if taskId not in self.cancelTasks:
			self.cancelTasks.add(taskId)

	def agvs(self):
		ret = set()
		for t in self.tasks.values():
			if t.agvId:
				ret.add(t.agvId)
		return ret


g_taskMgr = akmTaskMgr()


# type:
# load    从下板机一层运送满框到上板机一层
# unload  从上板机二层运送空框到下板机二层
class akmTask:
	def __init__(self, line, taskType, taskInfo):
		self.line = line
		self.type = taskType
		self.taskName = "%s执行任务%s" % (line, taskType)
		self.init(taskInfo)

		self.taskId = taskMgr.add(self.taskName, taskType, source=self.source, target=self.target, s_io=self.s_io,
								  t_io=self.t_io, line=self.line)
		self._taskThread = None
		self.isRunning = False
		self.isInit = True
		self.step = "waiting"
		self.agvId = None

	def init(self, info):
		d = g_taskType[self.type]
		self.map = info["map"]
		self.source = info[d["source"]]
		self.target = info[d["target"]]
		self.s_io = info[d["s_io"]]
		self.t_io = info[d["t_io"]]
		self.sName = info[d["sName"]]
		self.tName = info[d["tName"]]
		self.sTypeIo = info["typeio1"]
		self.tTypeIo= info["typeio2"]
		self.sDirection = info["s_direction"]
		self.tDirection= info["t_direction"]
		self.floor = d["floor"]
		self.startS = d["startSignal"]        #IN1
		self.aSignal = d["arrivedSignal"]     #IN3
		self.fSignal = d["finishSignal"]      #IN2
		self.fOverSignal = d["overSignal"]    #IN4


	def __str__(self):
		return "从%s设备运送框至%s设备" % (self.sName, self.tName)

	def run(self):
		self._taskThread = threading.Thread(target=self._taskFunc)
		self._taskThread.start()

	def _taskFunc(self):
		self.count = 0
		self.isRunning = True
		self.step = "checkBeginSignal"
		self.msg = ''
		taskMgr.start(self.taskId, step=self.step)
		while self.isRunning:
			old = self.step
			try:
				if self.step == "fail":
					taskMgr.fail(self.taskId, step=self.step, msg=self.msg)
					self.rollerStop()
					self._release()
					break
				elif self.step == "finish":
					taskMgr.finish(self.taskId, step=self.step, msg="任务完成")
					self._release()
					break
				elif not self.handle():
					log.warning(str(self), self.step, "error")
					time.sleep(2)
					continue
				if old != self.step:
					log.debug(str(self), old, "->", self.step)
				time.sleep(0.5)
			except socket.timeout as e:
				log.exception("taskFunc:" + str(self), e)
				time.sleep(2)
				continue
			except Exception as e:
				log.exception("taskFunc2:" + str(self), e)
				taskMgr.fail(self.taskId, msg=str(e))
				break
		self.isRunning = False
		log.info("task: stop",self)
		
	def onFinish(self,obj):
		# log.info("task: move finish callback",self)
		# log.info("task: move finish callback self.step", self.step)
		if not obj["result"]:
			self.msg = str(self) + " %s %s fail" % (self.step, obj["location"])
			self.step = "fail"
			return
		if self.step == "moveSource" or self.step == "goSource":
			time.sleep(1)
			self.checkIo = self.s_io
			self.step = "checkSourceSignal"
			taskMgr.update(self.taskId, step=self.step, msg="checkSourceSignal")
			return
		elif self.step == "moveTarget" or self.step == "goTarget":
			self.checkIo = self.t_io
			self.step = "checkTargetSignal"
			taskMgr.update(self.taskId, step=self.step, msg="checkTargetSignal")
			return

	def handle(self):
		if self.step == "checkBeginSignal":  # waiting -> checkBeginSignal
			s = self._readIO(self.s_io,self.sTypeIo)
			if s is None or s[self.startS] != 1:
				self.step = "fail"
				self.msg = "检查%s[%s]信号丢失" % (self.line, self.sName)
				return False
			self.step = "waitForAgv"
			taskMgr.update(self.taskId, step=self.step, msg="等待分配小车")
			return True
		elif self.step == "waitForAgv":  # checkBeginSignal -> waitForAgv
			self.param = {
				"taskId": self.taskId,
				"location": self.source,
				"floorId": self.map,
				"taskType": self.type
			}

			agvId = self._callAgv()
			if agvId is None:
				time.sleep(5)
				if  self.count > 60:
					self.step = "fail"
					self.msg = "检查%s[%s]任务呼叫小车超时"%(self.line,self.type)
				self.count += 1
				return False
			self.count = 0
			log.info(self,"apply",agvId)
			self.writeIO(self.t_io, self.aSignal, 0,self.tTypeIo)    #更改为分配到小车就清除IO
			self.writeIO(self.t_io, self.fOverSignal, 0,self.tTypeIo)    #更改为分配到小车就清除IO
			self.writeIO(self.s_io, self.aSignal, 0,self.sTypeIo)
			self.writeIO(self.s_io, self.fOverSignal, 0,self.sTypeIo)
			self.canReleaseAgv = True
			self.agvId = agvId
			self.step = "checkleftBarUpStatus"
			self.param["agvId"] = self.agvId
			taskMgr.update(self.taskId, agvId=self.agvId, step=self.step, msg="检测挡块上升状态%s" % self.agvId)
			return True
		elif self.step == "checkleftBarUpStatus":
			if not self.checkBarUpStatus(self.agvId,"1"):
				self.rollerRobotBarUp("1")
				if self.count > 15:
					self.step = "fail"
					self.msg = "检查%s[%s]设置小车左挡块顶升超时" % (self.line, self.sName)
				self.count += 1
				time.sleep(5)
				return False
			self.count = 0
			self.step = "checkrightBarUpStatus"
			taskMgr.update(self.taskId, step=self.step, msg="检测挡块上升状态")
			return True
		elif self.step == "checkrightBarUpStatus":
			if not self.checkBarUpStatus(self.agvId,"2"):
				self.rollerRobotBarUp("2")
				if self.count > 15:
					self.step = "fail"
					self.msg = "检查%s[%s]设置小车右挡块顶升超时" % (self.line, self.sName)
				self.count += 1
				time.sleep(2)
				return False
			self.count = 0
			self.step = "moveSource"
			taskMgr.update(self.taskId, step="goSource", msg="前往%s,%s" % (self.line, self.sName))
			return True
		elif self.step == "moveSource":  # waitForAgv -> moveSource
			self.param["taskId"] = self.taskId + "_1"
			self.param["location"] = self.source
			if not self._moveAgv():
				return False
			self.step = "goSource"
			taskMgr.update(self.taskId, step="goSource", msg="检测%s,%s 叫车信号" % (self.line, self.sName))
			return True
		elif self.step == "checkSourceSignal":
			s = self._readIO(self.s_io,self.sTypeIo)
			if s is None or s[self.startS] != 1:
				self.step = "fail"
				self.msg = "检查%s[%s]信号丢失" % (self.line, self.sName)
				return False
			self.canReleaseAgv = False
			self.step = "checkBarINDownStatus"
			taskMgr.update(self.taskId, step=self.step, msg="设置挡块下降")
			return True
		elif self.step == "checkBarINDownStatus":
			if not self.checkBarDownStatus(self.agvId,self.sDirection):
				self.rollerRobotBarDown(self.sDirection)
				if self.count > 15:
					self.step = "fail"
					self.msg = "检查%s[%s]设置小车左挡块下降超时" % (self.line, self.sName)
				self.count += 1
				time.sleep(5)
				return False
			self.count = 0
			self.step = "rollerLoad"
			taskMgr.update(self.taskId, step=self.step, msg="滚筒开始动作进料")
			return True

		elif self.step == "rollerLoad":  # checkSourceSignal -> rollerLoad
			if not self.rollerFrontLoad(self.sDirection):
				if self.count > 10:
					self.step = "fail"
					self.msg = "检查%s[%s]设置小车进料信号超时" % (self.line, self.sName)
				self.count += 1
				return False
			self.count = 0
			self.step = "arriveSource"
			taskMgr.update(self.taskId, step=self.step, msg="发送%s AGV到达信号" % self.source)
			return True
		elif self.step == "arriveSource":  # rollerLoad -> arriveSource
			if not self.writeIO(self.s_io, self.aSignal, 1,self.sTypeIo):  # 到达信号
				if self.count > 15:
					self.step = "fail"
					self.msg = "检查%s[%s]到达信号超时" % (self.line, self.sName)
					self._audioPlay()
				self.count += 1
				return False
			self.count = 0
			self.step = "checkSourceRollerFinish"
			taskMgr.update(self.taskId, step=self.step, msg="检测料框是否到位")
			return True

		elif self.step == "checkSourceRollerFinish":  # arriveSource -> checkSourceRollerFinish
			# 检测滚筒上料框 self.floor  连续两次检测信号存在即成功
			for i in range(2):
				s = self.getUnitLoadStatus(self.agvId, self.floor)
				if s is None or s != 1:
					if i == 0 and self.count > 20:
						self.step = "fail"
						self.msg = "检查%s[%s]小车进料信号超时" % (self.line, self.sName)
						self._audioPlay()
					self.count += 1
					return False
				time.sleep(1)
			self.count = 0
			self.step = "setInputFinish"
			taskMgr.update(self.taskId, step="clearSourceIO", msg="%s IO 设置进料完成信号" % self.sName)
			return True

		elif self.step == "setInputFinish":  # checkSourceRollerFinish -> clearSourceIO
			if not self.writeIO(self.s_io, self.fOverSignal, 1, self.sTypeIo) :  # 到达信号
				if self.count > 15:
					self.step = "fail"
					self.msg = "%s[%s]设置到达信号超时" % (self.line, self.sName)
				self.count += 1
				return False
			self.count = 0
			self.step = "checkSourceFinish"
			taskMgr.update(self.taskId, step=self.step,msg="%s 检测完成信号" % self.sName)
			return True

		elif self.step == "checkSourceFinish":  # checkTargetRollerFinish -> checkFinish
			# 检测上下板机完成信号 self.fSignal
			s = self._readIO(self.s_io,self.sTypeIo)
			if s is None or s[self.fSignal] != 1:
				if self.count > 50:
					self.step = "fail"
					self.msg = "检查%s[%s]进料完成信号超时" % (self.line, self.sName)
					time.sleep(1)
					self._audioPlay()
				self.count += 1
				return False
			self.count = 0
			self.step = "clearSourceIO"
			taskMgr.update(self.taskId, step=self.step, msg="%s 清除小车到达信号" % self.sName)
			return True

		elif self.step == "clearSourceIO":  # checkSourceRollerFinish -> clearSourceIO
			if not self.writeIO(self.s_io, self.aSignal, 0,self.sTypeIo) or not self.writeIO(self.s_io, self.fOverSignal, 0, self.sTypeIo):  # 到达信号
				if self.count > 15:
					self.step = "fail"
					self.msg = "检查%s[%s]清除到达超时" % (self.line, self.sName)
					self._audioPlay()
				self.count += 1
				return False
			self.count = 0
			self.step = "checkBarINUPStatus"
			taskMgr.update(self.taskId, step=self.step,msg="%s 小车挡块上升" % self.sName)
			return True

		elif self.step == "checkBarINUPStatus":
			if not self.checkBarUpStatus(self.agvId,self.sDirection):
				self.rollerRobotBarUp(self.sDirection)
				if self.count > 15:
					self.step = "fail"
					self.msg = "检查%s[%s]设置小车挡块上升超时" % (self.line, self.sName)
					self._audioPlay()
				self.count += 1
				time.sleep(2)
				return False
			self.count = 0
			self.step = "moveTarget"
			taskMgr.update(self.taskId, step=self.step, msg="前往%s,%s" % (self.line, self.tName))
			return True

		elif self.step == "moveTarget":  # checkSourceRollerFinish -> moveTarget
			self.param["taskId"] = self.taskId + "_2"
			self.param["location"] = self.target
			if not self._moveAgv():
				return False
			self.step = "goTarget"
			taskMgr.update(self.taskId, step=self.step, msg="%s 检测出料信号" % ( self.tName))
			return True

		elif self.step == "checkTargetSignal":  # onFinish goTarget -> checkTargetSignal
			s = self._readIO(self.t_io,self.tTypeIo)
			if s is None or s[self.startS] != 1:
				if  self.count > 15:
					self.step = "fail"
					self.msg = "检查%s[%s]叫料信号超时"%(self.line,self.tName)
					self._audioPlay()
				self.count += 1
				return False
			self.count = 0
			self.step = "checkBarOUTDownStatus"
			taskMgr.update(self.taskId, step=self.step, msg="发送%s AGV到达信号" % self.tName)
			return True
		elif self.step == "checkBarOUTDownStatus":
			if not self.checkBarDownStatus(self.agvId,self.tDirection):
				self.rollerRobotBarDown(self.tDirection)
				if self.count > 15:
					self.step = "fail"
					self._audioPlay()
					self.msg = "检查%s[%s]设置小车挡块下降超时" % (self.line, self.tName)
				self.count += 1
				time.sleep(2)
				return False
			self.count = 0
			self.step = "arriveTarget"
			taskMgr.update(self.taskId, step=self.step, msg="滚筒开始出框")
			return True
		elif self.step == "arriveTarget":  # checkTargetSignal -> arriveTarget
			if not self.writeIO(self.t_io, self.aSignal, 1,self.tTypeIo):  # 到达信号
				if self.count > 20:
					self.step = "fail"
					self.msg = "检查%s[%s]设置AGV到位信号超时" % (self.line, self.tName)
					self._audioPlay()
				self.count += 1
				return False
			self.count = 0
			self.step = "rollerUnload"
			taskMgr.update(self.taskId, step=self.step, msg="出框挡块下降")
			return True
		elif self.step == "rollerUnload":  # arriveTarget -> rollerUnload
			if not self.rollerFrontUnload(self.tDirection):
				if self.count > 10:
					self.step = "fail"
					self.msg = "检查%s[%s]设置出料信号失败" % (self.line, self.tName)
					self._audioPlay()
				self.count += 1
				return False
			self.count = 0
			self.checkRoller = 0
			self.step = "checkTargetRollerFinish"
			taskMgr.update(self.taskId, step=self.step, msg="检测滚筒是否出框")
			return True
		elif self.step == "checkTargetRollerFinish":  # rollerFrontUnload -> checkTargetRollerFinish
			# TODO 检测AGV出料料框 self.floor
			for i in range(2):
				s = self.getUnitUnloadStatus(self.agvId, self.floor)
				if s is None or s != 0:
					if i == 0 and self.count > 20:
						self.step = "fail"
						self.msg = "检查%s[%s]小车出料超时" % (self.line, self.tName)
						self.count += 1
						self._audioPlay()
					return False
				time.sleep(1)
			self.count = 0
			self.step = "setOutputFinish"
			taskMgr.update(self.taskId, step=self.step, msg="检测%s设置出料完成信号" % self.tName)
			return True

		elif self.step == "setOutputFinish":  # checkFinish -> clearTargetIO
			if not self.writeIO(self.t_io, self.fOverSignal, 1, self.tTypeIo) :  # 到达信号
				if self.count > 15:
					self.step = "fail"
					self.msg = "检查%s[%s]设置出料完成信号" % (self.line, self.tName)
				self.count += 1
				return False
			self.count = 0
			self.step = "checkFinish"
			taskMgr.update(self.taskId, step=self.step, msg="检测%s完成信号" % self.tName)
			return True

		elif self.step == "checkFinish":  # checkTargetRollerFinish -> checkFinish
			# 检测上下板机完成信号 self.fSignal
			s = self._readIO(self.t_io,self.tTypeIo)
			if s is None or s[self.fSignal] != 1:
				if self.count > 50:
					self.step = "fail"
					self.msg = "检查%s[%s]完成信号超时" % (self.line, self.tName)
					time.sleep(1)
					self._audioPlay()
				self.count += 1
				return False
			self.count = 0
			self.step = "clearTargetIO"
			self.canReleaseAgv = True
			taskMgr.update(self.taskId, step=self.step, msg="%s 清除达到和完成信号" % self.tName)
			return True
		elif self.step == "clearTargetIO":  # checkFinish -> clearTargetIO
			if not self.writeIO(self.t_io, self.aSignal, 0, self.tTypeIo) or not self.writeIO(self.t_io, self.fOverSignal, 0, self.tTypeIo):  # 到达信号
				if self.count > 15:
					self.step = "fail"
					self.msg = "检查%s[%s]清除到达信号超时" % (self.line, self.tName)
					self._audioPlay()
				self.count += 1
				return False
			self.count = 0
			self.step = "checkBarOUTUpStatus"
			taskMgr.update(self.taskId, step=self.step, msg="出料完成设置挡块下降")

			return True
		elif self.step == "checkBarOUTUpStatus":
			if not self.checkBarUpStatus(self.agvId,self.tDirection):
				self.rollerRobotBarUp(self.tDirection)
				if self.count > 15:
					self.step = "fail"
					self.msg = "检查%s[%s]设置小车挡块上升超时" % (self.line, self.tName)
				self.count += 1
				time.sleep(2)
				return False
			self.count = 0
			self.step = "finish"
			return True

		else:
			# 在onfinish跳转
			return True

	def _goHome(self):
		if self.agvId:
			agvApi.goHome(self.agvId, self.taskId)

	def _release(self):
		if self.agvId:
			try:
				log.info(self, self.agvId, "release task, release agv", self.canReleaseAgv)
				if self.step == "fail":
					self.rollerStop()
					self.writeIO(self.t_io, self.aSignal, 0,self.tTypeIo)
					self.writeIO(self.t_io, self.fOverSignal, 0,self.tTypeIo)
					self.writeIO(self.s_io, self.aSignal, 0,self.sTypeIo)
					self.writeIO(self.s_io, self.fOverSignal, 0,self.sTypeIo)
				if self.canReleaseAgv:
					ret = agvApi.isLocked(self.agvId, self.taskId)
					agvApi.release(self.agvId, self.taskId, force=False)
					# g_relese_agvs.add(self.agvId)
					if ret:
						log.info("go home");
						agvApi.goHome(self.agvId, force=False)
					self.agvId = ""
			except Exception as e:
				log.exception(str(self) + "task release", e)

		
	def filterFuncB(self,agvId, mapId, loc, payload):
		if agvId != local.get("line", self.line).split(',')[1]:
			return False
		s = self.getUnitStatus(agvId,self.floor)
		if s == 0:
			return True
		log.warning("task: [%s] %s floor %s is not None" % (self.taskId, agvId, self.floor))
		return False

	def _callAgv(self):
		try:
			return agvApi.apply(taskId=self.taskId, mapId=self.map, loc=self.source, filterFunc=self.filterFuncB,
								timeout=10)
		except Exception as e:
			log.warning("[%s] apply agv failed: %s" % (str(self), str(e)))
			return None

	def _moveAgv(self):
		try:
			self.param["timeoutSec"] = 86400
			agvApi.move(self.agvId, self.param["location"], self.onFinish, self.param)
			return True
		except Exception as e:
			log.exception(self.taskId + " moveAgv", e)
			raise
	def _audioPlay(self):
		try:
			audioApi.playAudio(self.agvId, name = "feedingAlarm", loop = False)
			time.sleep(1)
			audioApi.playAudio(self.agvId, name = "feedingAlarm", loop = False)
		except Exception as e:
			log.exception(self.taskId + " playAudio", e)
			raise

	def _readIO(self, io,type):
		try:
			s = []
			if type == "PLCD100":
				s = ioApi.readStatusListD100(io)["status"]
			elif type == "PLCD104":
				s = ioApi.readStatusListD104(io)["status"]
			elif type == "PLCM30":
				s = ioApi.readDOList(io)["status"]
			elif type == "PLCXJ":
				s = ioApi.readXJDOList(io)["status"]
			return s
		except Exception as e:
			log.exception("task: [%s][%s] readIO status error" % (self.taskId, io), e)
			return None
			
	def _readDO(self, io,type):
		try:
			s = []
			if type == "PLCD100":
				s = ioApi.readStatusListD100(io)["status"]
			elif type == "PLCD104":
				s = ioApi.readStatusListD104(io)["status"]
			elif type == "PLCM30":
				s = ioApi.readDOList(io)["status"]
			elif type == "PLCXJ":
				s = ioApi.readXJDOList(io)["status"]
			log.info("task: [%s][%s] readDo status " % (self.taskId, io), s)
			return s
		except Exception as e:
			log.exception("task: [%s][%s] readDo status error" % (self.taskId, io), e)
			return None

	def writeIO(self, io, id, value,type):
		try:
			if type == "PLCD100":
				ioApi.writeStatusD100(io, id+1, value)
			elif type == "PLCD104":
				ioApi.writeStatusD104(io, id+1, value)
			elif type == "PLCM30":
				ioApi.writeDO(io, id+1, value)
			elif type == "PLCXJ":
				ioApi.writeXJDO(io, id+1, value)
			time.sleep(1)
			s = self._readDO(io,type)
			num = id
			if not utility.is_test():  # id-1实际是
				num = id
			if s is not None and s[num] == value:  # id-1实际是
				return True
			else:
				log.warning("task: [%s][%s] writeIo failed,index [%s] != %s" % (self.taskId, io, id, value))
				return False
		except Exception as e:
			log.exception("task: [%s][%s] writeIo error: " % (self.taskId, io), e)
			return False

	def getAgvPayload(self, agvId):
		ds = db.find_one("u_agv_payload", {"_id": agvId})
		if ds is None:
			return {"floor1": None, "floor2": None}
		return {"floor1": ds["floor1"] if "floor1" in ds else None, "floor2": ds["floor2"] if "floor2" in ds else None}

	def updateAgvPayload(self, payload=None):
		if self.type == "load":
			floor = "floor1"
		elif self.type == "unload":
			floor = "floor2"
		db.update_one("u_agv_payload", {"_id": self.agvId}, {floor: payload}, update_or_insert=True)



	def getUnitStatus(self, agvId, unitId):
		try:
			return rollerPlusApi.checkUnitStatus(agvId, unitId)["status"]
		# return rollerApi.unitStatus(agvId, unitId)["status"]
		except Exception as e:
			log.exception(self.taskId + "getUnitStatus", e)
			return None

	def getUnitLoadStatus(self, agvId, unitId):
		try:
			return rollerPlusApi.checkUnitloadStatus(agvId, unitId)["status"]
		# return rollerApi.unitStatus(agvId, unitId)["status"]
		except Exception as e:
			log.exception(self.taskId + "getUnitLoadStatus", e)
			return None

	def getUnitUnloadStatus(self, agvId, unitId):
		try:
			return rollerPlusApi.checkUnitUnloadStatus(agvId, unitId)["status"]
		# return rollerApi.unitStatus(agvId, unitId)["status"]
		except Exception as e:
			log.exception(self.taskId + "getUnitUnloadStatus", e)
			return None

	def rollerFrontLoad(self, unitId):
		try:
			ret = rollerPlusApi.rollerRobotLoad(self.agvId, unitId)
			# rollerApi.rollerFrontLoad(self.agvId,unitId)
			if ret["ret_code"] == 0:
				return True
			else:
				return False
		except Exception as e:
			log.exception("task [%s] [%s] rollerFrontLoad failed" % (self.agvId, self.taskId), str(e))
			return False

	def rollerFrontUnload(self, unitId):
		try:
			ret = rollerPlusApi.rollerRobotUnLoad(self.agvId, unitId)
			if ret["ret_code"] == 0:
				return True
			else:
				return False
			# rollerApi.rollerFrontUnload(self.agvId, unitId)
		except Exception as e:
			log.exception("task [%s] [%s] rollerFrontUnload failed" % (self.agvId, self.taskId), str(e))
			return False

	def rollerStop(self):
		try:
			ret = rollerPlusApi.rollerRobotStop(self.agvId)
			if ret["ret_code"] == 0:
				return True
			else:
				return False
			# rollerApi.rollerStop(self.agvId)

		except Exception as e:
			log.exception("task [%s] [%s] rollerStop failed" % (self.agvId, self.taskId), str(e))
			return False

	def rollerRobotBarUp(self, unitId):
		try:
			ret = rollerPlusApi.rollerRobotBarUp(self.agvId, unitId)
			# rollerApi.rollerFrontLoad(self.agvId,unitId)
			if ret["ret_code"] == 0:
				return True
			else:
				return False
		except Exception as e:
			log.exception("task [%s] [%s] rollerRobotBarUp failed" % (self.agvId, self.taskId), str(e))
			return False

	def rollerRobotBarDown(self, unitId):
		try:
			ret = rollerPlusApi.rollerRobotBarDown(self.agvId, unitId)
			# rollerApi.rollerFrontLoad(self.agvId,unitId)
			if ret["ret_code"] == 0:
				return True
			else:
				return False
		except Exception as e:
			log.exception("task [%s] [%s] rollerRobotBarDown failed" % (self.agvId, self.taskId), str(e))
			return False

	def checkBarUpStatus(self, agvId, unitId):
		try:
			return rollerPlusApi.checkBarUpStatus(agvId, unitId)["status"]
		# return rollerApi.unitStatus(agvId, unitId)["status"]
		except Exception as e:
			log.exception(self.taskId + "getUnitUnloadStatus", e)
			return None
	def checkBarDownStatus(self, agvId, unitId):
		try:
			return rollerPlusApi.checkBarDownStatus(agvId, unitId)["status"]
		# return rollerApi.unitStatus(agvId, unitId)["status"]
		except Exception as e:
			log.exception(self.taskId + "checkBarDownStatus", e)
			return None

		# def _deal(self,msg,isRelease=False):
		# taskMgr.fail(self.taskId,msg=msg)
		# try:
		# self._writeIO(self.device_id,self.task_io["arrivedSignal"],0)
		# self.rollerStop(isOther=True)
		# if self.agvId and isRelease:
		# self._release()
		# self._goHome()
		# except Exception as e:
		# log.exception("%s deal error: "%self.taskId,str(e))
		# self.isRunning = False
		# self.taskId = None
		# self.param = None

#
# if __name__ == "__main__":
# 	utility.start()

