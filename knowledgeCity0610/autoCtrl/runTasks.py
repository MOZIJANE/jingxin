# coding: utf-8
# author: pengshuqin
# date: 2019-10-16
# desc: 任务处理
import socket
import threading
import time
import os
import json as json2

import local
import setup

if __name__ == '__main__':
	setup.setCurPath(__file__)

import json_codec as json
import log
#import enhance
import utility
import mytimer
import lock as lockImp
import mongodb as db
import taskMgr
import agvDevice.jackApi as jackApi
import agvCtrl.agvApi as agvApi
import remoteio.remoteioMgr_old as ioMgr

# import agvDevice.rollerApi as rollerApi
import agvDevice.rollerPlusApi as rollerPlusApi
import agvDevice.pgvApi as pgvApi
import agvDevice.audioApi as audioApi
import remoteio.remoteioApi as ioApi
import agvDevice.rotationApi as rotationApi


proName = 'KLC_guntong'

OUT1 = 1
OUT2 = 2
IN1 = 0
IN2 = 1
IN3 = 2
IN4 = 3
IN5 = 4
IN6 = 5
IN7 = 6
IN8 = 7
FLOOR1 = 1
FLOOR2 = 2
MAX_LINE_AGV_NUM = 1
g_taskType = {
	"load": {"sName": "上工序", "tName": "下工序", "source": "loc1", "target": "loc2", "s_io": "io1", "t_io": "io2",
			 "floor": FLOOR2, "startSignal": IN1, "finishSignal": IN2, "arrivedSignal": IN3, "overSignal": IN4},
	"unload": {"sName": "下工序", "tName": "上工序", "source": "loc2", "target": "loc1", "s_io": "io2", "t_io": "io1",
	         "floor": FLOOR1, "startSignal": IN5, "finishSignal": IN6, "arrivedSignal": IN7, "overSignal": IN8},
}

g_taskDict = {} 
g_lastType = {}
g_init = None
g_lock = threading.RLock()
g_slock = threading.RLock()
g_ioStatus = {}
g_first = True
g_taskQueue = []
MAX_AGV_NUM = 3
	#数字越小，优先级越高

MAX_INSIDE_AGV_NUM = 1
g_taskInsideQueue = []	#内围任务

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
def PdaAddTask(source,target,payloadId,priority):
	global g_taskQueue,g_taskInsideQueue
	log.info(f'Scada send a task to the server from { source } to { target } payloadId: { payloadId }')
	task = scadaTask(source,target,payloadId,int(priority))
	g_ScataskMgr.add(task)
	log.info('task cmd: got a task from scada',task)
	return task.taskId



@lockImp.lock(g_lock)
def failTask(taskId):
	log.warning('task cmd: fail task', taskId)
	#t = g_taskMgr.getTask(taskId)
	t = g_ScataskMgr.getTask(taskId)
	lockImp.release(g_lock)
	if t is not None:
		t.canReleaseAgv = True
		t.stop()
	taskMgr.fail(taskId, failMsg="task fail by PDA")


@lockImp.lock(g_lock)
def finishTask(taskId):
	log.warning('task cmd: finish task', taskId)
	#t = g_taskMgr.getTask(taskId)
	t = g_ScataskMgr.getTask(taskId)
	lockImp.release(g_lock)
	if t is not None:
		t.canReleaseAgv = True
		t.stop()
	taskMgr.finish(taskId, step="finish")


def cancel(taskId):
	#t = g_taskMgr.getTask(taskId)
	t = g_ScataskMgr.getTask(taskId)
	if t is not None:
		#g_taskMgr.cancelTasks.add(taskId)
		g_ScataskMgr.cancelTask.add(taskId)
		if t.isRunning:
			if t.agvId:
				agvApi.cancelTask(t.agvId)
			t.stop()


@lockImp.lock(g_lock)
def getTaskStatus():
	return g_taskMgr.getTaskStatus()


@lockImp.lock(g_lock)
def switchMode(taskId):
	#global r_task,c_task
	log.warning('task cmd: switch to pda mode',taskId)
	msg1 = taskMgr.get(taskId)['failMsg']
	t = g_ScataskMgr.getTask(taskId)
	if t is not None:
		g_ScataskMgr.cancelTasks.add(taskId)
		if t.isRunning:
			if t.agvId:
				agvApi.cancelTask(t.agvId)
			t.pda = True
			g_ScataskMgr.save()
			lockImp.release(g_lock)
			t.stop()
		msg = "task canceled - " +  str(msg1)
		taskMgr.error(taskId,failMsg=msg)

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



#检查卓兰信号并修改IO
def checkLampStatus():
	status = ioMgr.readDIList('3FElevarot')['status'][4]

	if status == 1:
		ioMgr.writeDO('3FLamp', 1, 1)
	elif status == 0:
		ioMgr.writeDO('3FLamp', 1, 0)

		
		
@mytimer.interval(500)
@lockImp.lock(g_lock)
def run():
	global g_taskDict, g_taskMgr, g_ScataskMgr, g_init, g_lastType, g_first, g_taskQueue,g_taskInsideQueue
	# log.info("g_taskDict:",g_taskDict,"g_taskMgr:",g_taskMgr,"g_lastType:",g_lastType)
	if g_init is None:
		if g_first:
			time.sleep(5)
			g_first = False
		g_init = "akmTask"
		agvApi.init("akmTask")
		db.delete_many("u_agv_payload", '')
	g_ScataskMgr.recover()

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

	#2021-04-21新增管理关于PAD的任务
	while g_ScataskMgr.runningCount(isInside=True) < MAX_INSIDE_AGV_NUM and len(g_taskInsideQueue) > 0:
		t = g_taskInsideQueue.pop(0)
		if not g_ScataskMgr.isCancelTask(t.taskId):
			t.start()

	while g_ScataskMgr.runningCount(isInside=False) < MAX_AGV_NUM and len(g_taskQueue) > 0:
		findTask = None
		for t in g_taskQueue:
			if g_ScataskMgr.isCancelTask(t.taskId):
				log.warning(t, "is cancel task")
				findTask = t
				break
			if not g_ScataskMgr.checkTask(t):
				continue
			if not g_ScataskMgr.isCancelTask(t.taskId):
				t.start()
			else:
				log.warning(t, "is cancel task2")
			findTask = t
			break
		if findTask:
			g_taskQueue.remove(findTask)
		else:
			break
		time.sleep(1)

	g_ScataskMgr.removeFinishTask()
	g_taskMgr.removeFinishTask()
	checkLampStatus()





g_lockPrepoint = {}					#前置点控制,key=mapId.loc,value=taskId
g_lockp = lockImp.create("runTasks.pre_lock")		 #锁住前置点

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



#格式化地图上的点
def formatLoc(mapId,loc):
	if mapId and loc.find(".") == -1:
		return mapId + "." + loc
	return loc


class scadaTask:
    def __init__(self, source, target, payloadId, priority):
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
            # 修改
            self.payloadId = ""  # 也不判断货架，因为逻辑不需要
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
        name = "从%s运送货架到%s" % (source, target)
        self.taskId = taskMgr.add(taskName=name, type="scadaTask", source=source, target=target, payloadId=payloadId,
                                  priority=priority)
        self._load()
        self._taskThread = None
        self.isRunning = False
        self.taskStep = "waiting"
        self.canReleaseAgv = False  # 是否可以直接释放小车
        self.forceReleaseAgv = False
        self.pda = False  # 转pda状态
        self.needRelease = False  # 是否需要release
        log.info(self, "is inside", self.isInside)

    # self.waitTaskId = None

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
        if not a:
            a = "-"
        s = "task[%s][%s] %s(%s) -> %s(%s) [%s]" % (
        self.taskId, a, self.s_info["location"], self.s_info["prepoint"], self.t_info["location"],
        self.t_info["prepoint"], self.taskStep)
        if self.isRecoverTask:
            return "*" + s
        return s

    def __lt__(self, other):
        # 取出权重小的
        if self.priority == other.priority:
            return self.createTime < other.createTime
        return self.priority < other.priority


    @property
    def isInside(self):
        return self.s_info["floorId"] == "fp-neiwei"

    @property
    def sPrepoint(self):
        return formatLoc(self.s_info["floorId"], self.s_info["prepoint"])

    @property
    def tPrepoint(self):
        return formatLoc(self.t_info["floorId"], self.t_info["prepoint"])

    def _load(self):
        import counter
        log.info(self.target, self.source)
        ds = db.find("u_loc_info2", {"_id": {"$in": [self.source, self.target]}})
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
            self._taskThread = threading.Thread(target=self._taskFunc, name="scada." + self.taskId)
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
        pp = status["unfinishPaths"].split(",")
        if pp:
            if self.s_info["prepoint"] not in pp:
                taskMgr.update(self.taskId, step="moveTarget")
                if self.s_info["prepoint"] != self.t_info["prepoint"]:
                    self.unlockLoc(self.s_info["floorId"], self.s_info["prepoint"])
                self.taskStep = "moveTarget"


    @lockImp.lock(None)
    def onFinish(self, obj):
        log.info("task: move finish callback", self)
        if not obj["result"]:
            self.needRelease = True
            taskMgr.error(self.taskId, failMsg=obj["resultDesc"])
            return
        if self.taskStep == "moveSource" or self.taskStep == "startMovePreSrc":
            self.taskStep = "waitSource"
            self.waitLoc = self.source
            taskMgr.update(self.taskId, step="waitSource", failMsg="等待scada允许进入源信号")
            return

        elif self.taskStep == "loadPlayload" or self.taskStep == "waitSource":
            self.taskStep = "loadPlayload_readqr"
            taskMgr.update(self.taskId, failMsg="AGV二层出料")
            return
        elif self.taskStep == "movePreSourceStep":
            self.taskStep = "movePreSourceStepTimeout"
            return
        elif self.taskStep == "moveTarget":
            taskMgr.update(self.taskId, step="waitTarget", failMsg="等待scada允许进入目标信号")
            self.taskStep = "waitTarget"
            self.waitLoc = self.target
            return
        elif self.taskStep == "dropPayload":
            self.taskStep = "dropPayloadJackdown"
            taskMgr.update(self.taskId, failMsg="放下货架，旋转顶升机构初始化")
            return

        elif self.taskStep == "dropPayload_lst":
            self.taskStep = "dropPayloadJackdown_lst"
            taskMgr.update(self.taskId, failMsg="放下货架，旋转顶升机构初始化")
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

    @lockImp.lock(None)
    def handle(self):
        log.info('this is handle taskStep=============>' + self.taskStep)
        if self.taskStep == "waiting":
            # if not self.islocAvailable(self.s_info["floorId"],self.s_info["prepoint"]):
            # 	return False
            self.taskStep = "waitForAgv"
            taskMgr.update(self.taskId, failMsg="等待分配小车")
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

            log.info(self, "apply", agvId)
            self.canReleaseAgv = True
            self.agvId = agvId
            self.taskStep = "initAGV"
            self.param["agvId"] = self.agvId
            taskMgr.update(self.taskId, agvId=self.agvId, failMsg="成功分配小车%s" % self.agvId)
            return True
        elif self.taskStep == "initAGV":
            self.param["taskId"] = self.taskId + "_1"
            self.param['isRotate'] = ''
            self.taskStep = "startMoveAGV"
            # taskMgr.update(self.taskId,failMsg="等待%s前置点锁"%self.source)
            taskMgr.update(self.taskId, failMsg="前往%s工位点" % self.source)
            return True

        elif self.taskStep == "startMoveAGV":
            self.param["location"] = self.s_info["location"]
            self.param["floorId"] = self.s_info["floorId"]
            self.param["taskId"] = self.taskId + "_2"
            self.param["direction"] = self.s_info["direction"]
            self.param["p_direction"] = self.s_info["p_direction"]
            if self.agvId == 'AGVchache':
                if not self._jackDown():
                    return False
                self._moveAgv()
                log.info('------------------------------------------------------Moveagv------------------')
            else:
                self._moveJackup()
                log.info('------------------------------------------------------Movejackup------------------')
            self.taskStep = "loadPlayload"
            return True

        elif self.taskStep == "loadPlayload_readqr":  ## 这个通过onFinish跳转 loadPlayload -> loadPlayload_readqr
            self.canReleaseAgv = False
            if self.agvId == 'AGVwuliao':
                log.info('--------------------------------------准备上料点二层进料')
                if not self.rollerFrontLoad(2): #这样写死了小车首先让二层滚筒进料
                    if self.count > 10:
                        self.taskStep = "failed"
                        taskMgr.update(self.taskId, failMsg="二层滚筒链接超时" % self.target)
                    self.count += 1
                    return False
                self.count = 0
                self.taskStep = "checkTwoLayerGoing"
                taskMgr.update(self.taskId, failMsg="二层滚筒进料%s" % self.target)
                return True
            
            elif self.agvId == 'AGVchache':
                self.taskStep = "loadPlayload_jackup"
                return True
            elif self.agvId == 'AGVdiniu':
                self.taskStep = "waitDestPreLoc"
                return True

        elif self.taskStep == "checkTwoLayerGoing":  # rollerFrontUnload -> checkTargetRollerFinish
            log.info('------------------------------------------检查二层进料状态')
            # TODO 检测AGV进料料框 self.floor
            successN = 0
            for i in range(300):
                #s = self.getUnitLoadStatus(self.agvId, 2)
                s = self.getUnitStatus(self.agvId, 2)
                if s == 0:
                    if i > 60 and self.count > 40:
                        self.taskStep = "failed"
                        taskMgr.update(self.taskId, failMsg="小车二层进料超时%s" % self.target)
                        self.count += 1
                        return False
                elif s is None or s != 0:
                    successN += 1
                    if successN >= 3:
                        break
                time.sleep(1)
            self.count = 0
            self.taskStep = "checkOneLayerFinish"
            taskMgr.update(self.taskId, step=self.taskStep, msg="检测2层设置进料完成信号")
            return True


        elif self.taskStep == "checkOneLayerFinish":  # rollerFrontUnload -> checkTargetRollerFinish
            log.info('--------------------------------------------检查一层出料状态')
            successN = 0
            # TODO 检测AGV出料料框 self.floor
            for i in range(300):
                #s = self.getUnitUnloadStatus(self.agvId, 1)
                s = self.getUnitStatus(self.agvId, 1)
                if s == 0:
                    successN += 1
                    if successN >= 3:
                        break
                elif s is None or s != 0:
                    if i > 60 and self.count > 40:
                        self.taskStep = "failed"
                        taskMgr.update(self.taskId, failMsg="小车一层出料超时%s" % self.target)
                        self.count += 1
                        return False
                time.sleep(1)
            self.count = 0
            self.taskStep = "waitDestPreLoc"
            taskMgr.update(self.taskId, step=self.taskStep, msg="检测一层设置出料完成信号")
            return True


        elif self.taskStep == "loadPlayload_jackup":
            self.canReleaseAgv = False
            if not self._jackUp():
                return False
            self.taskStep ="waitDestPreLoc"
            taskMgr.update(self.taskId,failMsg="等待%s工位点锁"%self.target)
            return True


        elif self.taskStep == "waitDestPreLoc":
            if not self.lockLoc(self.taskId, self.t_info["floorId"], self.t_info["location"]):
                return False
            self.taskStep = "dropPayloadMove"
            taskMgr.update(self.taskId, failMsg="前往%s工位点放下货架" % (self.t_info["location"]))
            return True








        #   movejackdown
        elif self.taskStep == "dropPayloadMove":
            if self.agvId == 'AGVdiniu' or self.agvId == 'AGVwuliao':
                self.param["location"] = self.t_info["location"]
                self.param["floorId"] = self.t_info["floorId"]
                self.param["taskId"] = self.taskId + "_4"
                self.param["direction"] = self.t_info["direction"]
                self._moveJackdown()
                log.info('----------------------------------------------movejackdown----------')
            else:
                self.param["location"] = self.t_info["location"]
                self.param["floorId"] = self.t_info["floorId"]
                self.param["taskId"] = self.taskId + "_3"
                self.param["direction"] = self.t_info["direction"]
                self._moveAgv()
                log.info('----------------------------------------------moveAGV---------------')
            taskMgr.update(self.taskId, step="dropPayload")
            self.taskStep = "dropPayload"  # 这个通过onFinish跳转 dropPayload -> dropPayloadJackdown
            return True


        #   movejackdown
        elif self.taskStep == "dropPayloadMove_lst":
            self.param["location"] = 'AP101'
            self.param["floorId"] = 'comba-ZSC-F1-F3'
            self.param["taskId"] = self.taskId + "_4"
            self.param["direction"] = self.t_info["direction"]
            self._moveAgv()
            log.info('----------------------------------------------moveAGV---------------')
            taskMgr.update(self.taskId, step="dropPayload_lst")
            self.taskStep = "dropPayload_lst"  # 这个通过onFinish跳转 dropPayload_lst -> dropPayloadJackdown_lst
            return True





        # 物料车开始动作
        elif self.taskStep == "WuliaoNext":
            log.info('------------------------------------到达目标点二层开始出料')
            self.canReleaseAgv = False
            if self.agvId == 'AGVwuliao':
                if not self.rollerFrontUnload(2): #这样写死了小车首先让二层滚筒出料
                    if self.count > 10:
                        self.taskStep = "failed"
                        taskMgr.update(self.taskId, failMsg="二层滚筒链接超时" % self.target)
                    self.count += 1
                    return False
                self.count = 0
            # taskMgr.update(self.taskId, step=self.taskStep, msg="发送%s AGV到达信号" % self.source)
                self.taskStep = "checkTwoLayerGoingSecond"
                taskMgr.update(self.taskId, failMsg="二层滚筒出料%s" % self.target)
                return True
            else:
                log.info('不是物料车')
                return False

        elif self.taskStep == "checkTwoLayerGoingSecond":  # rollerFrontUnload -> checkTargetRollerFinish
            log.info('------------------------------------到达目标点检查二层出料状态')
            # TODO 检测AGV出料料框 self.floor
            for i in range(2):
                s = self.getUnitUnloadStatus(self.agvId, 2)
                if s is None or s != 0:
                    if i == 0 and self.count > 20:
                        self.taskStep = "failed"
                        taskMgr.update(self.taskId, failMsg="小车二层出料超时%s" % self.target)
                        self.count += 1
                    return False
                time.sleep(2)
            self.count = 0
            self.taskStep = "checkTwoLayerFinish"
            taskMgr.update(self.taskId, step=self.taskStep, msg="检测2层设置出料完成信号")
            return True

        elif self.taskStep == "checkTwoLayerFinish":
            log.info('----------------------------------到达目标点一层开始进料')
            if not self.rollerFrontLoad(1): #小车一层开始进料
                if self.count > 10:
                    self.taskStep = "failed"
                    taskMgr.update(self.taskId, failMsg="一层滚筒进料超时%s" % self.target)
                self.count += 1
                return False
            self.count = 0
            # taskMgr.update(self.taskId, step=self.taskStep, msg="发送%s AGV到达信号" % self.source)
            self.taskStep = "waitPushrodPush"
            taskMgr.update(self.taskId, failMsg="一层滚筒进料%s" % self.target)
            return True

        elif self.taskStep == "waitPushrodPush":
            log.info('-------------------------------------到达目标点退岗推出')
            if not self.rollerRobotPush(): #推杆
                if self.count > 10:
                    self.taskStep = "failed"
                    taskMgr.update(self.taskId, failMsg="推杆链接超时%s" % self.target)
                self.count += 1
                return False
            self.count = 0
            # taskMgr.update(self.taskId, step=self.taskStep, msg="发送%s AGV到达信号" % self.source)
            self.taskStep = "RollerPushFinish"
            taskMgr.update(self.taskId, failMsg="推杆推出%s" % self.target)
            return True

        elif self.taskStep == "RollerPushFinish":  # rollerFrontUnload -> checkTargetRollerFinish
            # TODO 检测AGV出料料框 self.floor
            for i in range(2):
                s = self.getUnitLoadStatus(self.agvId, 1)
                if s is None or s != 0:
                    if i == 0 and self.count > 20:
                        self.taskStep = "failed"
                        taskMgr.update(self.taskId, failMsg="小车一层出料超时%s" % self.target)
                        self.count += 1
                    return False
                time.sleep(4.5)
            self.count = 0
            self.taskStep = "waitPushrodUnpush"
            taskMgr.update(self.taskId, step=self.taskStep, msg="检测一层设置出料完成信号")
            return True

        elif self.taskStep == "waitPushrodUnpush":
            if not self.rollerRobotUnPush(): #收杆
                if self.count > 10:
                    self.taskStep = "failed"
                    taskMgr.update(self.taskId, failMsg="收杆链接超时%s" % self.target)
                self.count += 1
                return False
            self.count = 0
            # taskMgr.update(self.taskId, step=self.taskStep, msg="发送%s AGV到达信号" % self.source)
            # self.taskStep = "dropPayloadJackdown"
            time.sleep(4)
            self.taskStep = "dropPayloadReset"
            log.info('------------------------------------------------结束物料车的任务，完成')
            taskMgr.update(self.taskId, failMsg="推杆收回%s" % self.target)
            return True











        elif self.taskStep == "dropPayloadJackdown":
            log.info(self.agvId)
            if self.agvId == 'AGVchache': #如果是叉车，到目标点后要下降、
                log.info('yes')
                while ioMgr.readDIList('1FElevarot')['status'][4]:
                    log.info(ioMgr.readDIList('1FElevarot')['status'][4])
                    time.sleep(5)
                    continue
                log.info(ioMgr.readDIList('1FElevarot')['status'][4])
                self.taskStep = "dropPayloadMove_lst"
                return True
            if self.agvId == 'AGVwuliao':
                self.taskStep = "WuliaoNext"
                return True
            else:
                self.taskStep = "dropPayloadReset"
                return True


        elif self.taskStep == "dropPayloadJackdown_lst":
            if self.agvId == 'AGVchache':
                if not self._jackDown():
                    return False
                self.taskStep = 'dropPayloadReset'
            return True


        elif self.taskStep == "dropPayloadReset":
            self.canReleaseAgv = True
            self.taskStep = "finish"
            taskMgr.finish(self.taskId, step="finish", failMsg="任务成功")
            return True
        else:
            # 在onfinish跳转
            return True
























    def rollerFrontLoad(self, unitId):
        try:
            ret = rollerPlusApi.rollerRobotLoad(self.agvId, unitId)
            if ret["ret_code"] == 0:
                return True
            else:
                return False
        except Exception as e:
            log.exception("task [%s] [%s] rollerFrontLoad failed" % (self.agvId, self.taskId), str(e))
            return False


    def rollerRobotPush(self,):
        try:
            ret = rollerPlusApi.rollerRobotPush(self.agvId)
            if ret["ret_code"] == 0:
                return True
            else:
                return False
        except Exception as e:
            log.exception("task [%s] [%s] rollerFrontLoad failed" % (self.agvId, self.taskId), str(e))
            return False


    def rollerRobotUnPush(self,):
        try:
            ret = rollerPlusApi.rollerRobotUnPush(self.agvId)
            if ret["ret_code"] == 0:
                return True
            else:
                return False
        except Exception as e:
            log.exception("task [%s] [%s] rollerFrontLoad failed" % (self.agvId, self.taskId), str(e))
            return False


    def getUnitLoadStatus(self, agvId, unitId):
        try:
            return rollerPlusApi.checkUnitloadStatus(agvId, unitId)["status"]
        # return rollerApi.unitStatus(agvId, unitId)["status"]
        except Exception as e:
            log.exception(self.taskId + "getUnitLoadStatus", e)
            return None

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

    def getUnitStatus(self, agvId, unitId):
        try:
            return rollerPlusApi.checkUnitStatus(agvId, unitId)["status"]
        # return rollerApi.unitStatus(agvId, unitId)["status"]
        except Exception as e:
            log.exception(self.taskId + "getUnitStatus", e)
            return None

    def getUnitUnloadStatus(self, agvId, unitId):
        try:
            return rollerPlusApi.checkUnitUnloadStatus(agvId, unitId)["status"]
        # return rollerApi.unitStatus(agvId, unitId)["status"]
        except Exception as e:
            log.exception(self.taskId + "getUnitUnloadStatus", e)
            return None

    def _jackUp(self):
        try:
            log.info(self, "_jackUp")
            jackApi.jackUp(self.agvId, timeoutSec=90)
            return True
        except (ConnectionResetError, ConnectionAbortedError, socket.timeout, IOError) as e:
            raise
        except Exception as e:
            log.exception(str(self) + ' jackup', e)
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

    @utility.catch
    def _taskFunc(self):
        log.info('task: start', self)
        isRelease = False
        self.count = 0

        while self.isRunning:
            if not self.handleRecover():  # 流程会返回一个True
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
            g_ScataskMgr.save()
            time.sleep(0.3)

        if not isRelease:
            self._release()
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
                    # g_relese_agvs.add(self.agvId)
                    if ret:
                        log.info(self, "let", self.agvId, "gohome")
                        agvApi.goHome(self.agvId, force=False, timeout=60 * 60 * 3)
                    else:
                        log.info(self, self.agvId, "lock by other taskId, no gohome")
                    self.agvId = ""
        except Exception as e:
            log.exception(str(self) + "task release", e)
        self.clearLoc()

    # 过滤某些工位 如果不是04车 agvapi那里加入exclude
    def _filterFunc(self, agvId, mapId, loc, payload):
        Wuliao_RACK = ['comba-ZXC-F3.AP22', 'comba-ZXC-F3.AP18', 'comba-ZXC-F3.AP25']  # L_RACK工位
        Diniu_RACK = ['comba-ZXC-3F.AP668', 'comba-ZXC-3F.AP666']  # L_RACK工位
        Chache_RACK = ['comba-ZSC-F1-F3.AP142', 'comba-ZSC-F1-F3.AP143', 'comba-ZSC-F1-F3.AP101']  # L_RACK工位
        oldAGV = ['AGVdiniu', "AGVwuliao", "AGVchache"]  # 新装曲臂连杆的车不能进L_RACK工位
        t_loc = formatLoc(self.t_info["floorId"], self.t_info["location"])
        s_loc = formatLoc(self.s_info["floorId"], self.s_info["location"])
        #判断使用哪一种类型的车
        log.info(s_loc,t_loc)
        log.info(agvId)
        log.info('判断类型')
        if s_loc in Diniu_RACK or t_loc in Diniu_RACK:
            if agvId == 'AGVdiniu':
                return True
        elif s_loc in Wuliao_RACK or t_loc in Wuliao_RACK:
            if agvId == 'AGVwuliao':
                return True
        elif s_loc in Chache_RACK or t_loc in Chache_RACK:
            if agvId == 'AGVchache':
                return True
        else:

            if not agvId in oldAGV:
                return False


    # @lockImp.lock(g_lock)
    def _applyAgv(self):
        try:
            log.info('叫车')
            return agvApi.apply(taskId=self.param["taskId"], mapId=self.param["floorId"], loc=self.param["location"], filterFunc=self._filterFunc, timeout=10)  # filterFunc=self._filterFunc,
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
            agvApi.move(self.agvId, self.param["floorId"] + '.' + self.param["location"], self.onFinish, self.param,
                        stepCallback=stepCallback)
            # agvCtrl下的agvApi.py
            return True
        except (ConnectionResetError, ConnectionAbortedError, socket.timeout, IOError) as e:
            raise
        except Exception as e:
            raise e
            taskMgr.error(self.taskId, failMsg=str(e))
            return False

    # @lockImp.lock(g_lock)
    def _moveJackup(self):
        # log.info('----------------------------在runTasks.py的_moveJackup函数中-----------------111-------------')
        self.param["timeoutSec"] = 86400
        # self.waitTaskId = self.param["taskId"]
        if proName == 'fastprint':
            if 'WorkPlace' in self.param and self.param['WorkPlace'] and self.param['WorkPlace'] != '' and self.param[
                'WorkPlace'].lower() == 'true':
                agvApi.moveJackup(self.agvId, self.param["floorId"] + '.' + self.param["location"], self.onFinish,
                                  self.param, use_pgv=False)
            else:
                if self.agvId in ["AGV07", "AGV08"]:
                    agvApi.moveJackup(self.agvId, self.param["floorId"] + '.' + self.param["location"], self.onFinish,
                                      self.param, use_pgv=True, pgv_type=4)
                else:
                    agvApi.moveJackup(self.agvId, self.param["floorId"] + '.' + self.param["location"], self.onFinish,
                                      self.param, use_pgv=True, pgv_type=1)
        else:

            agvApi.moveJackup(self.agvId, self.param["floorId"] + '.' + self.param["location"], self.onFinish,
                              self.param)

    # @lockImp.lock(g_lock)
    def _moveJackdown(self):
        self.param["timeoutSec"] = 86400
        # self.waitTaskId = self.param["taskId"]
        agvApi.moveJackdown(self.agvId, self.param["floorId"] + '.' + self.param["location"], self.onFinish, self.param)

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






# type:
# load    从下板机一层运送满框到上板机一层
# unload  从上板机二层运送空框到下板机二层
class akmTask:
	def __init__(self, line, taskType, taskInfo):
		self.line = line
		self.type = taskType
		self.taskName = "%s执行任务%s" % (line, taskType)
		self.init(taskInfo)
		self.taskId = taskMgr.add(self.taskName, taskType, source=self.source, target=self.target, s_io=self.s_io, t_io=self.t_io, line=self.line)
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
		self.sName = d["sName"]
		self.tName = d["tName"]
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
			self.writeIO(self.s_io, self.aSignal, 0,self.sTypeIo)
			self.canReleaseAgv = True
			self.agvId = agvId
			self.step = "moveSource"
			self.param["agvId"] = self.agvId
			taskMgr.update(self.taskId, agvId=self.agvId, step=self.step, msg="检测挡块上升状态%s" % self.agvId)
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
			self.step = "rollerLoad"
			taskMgr.update(self.taskId, step=self.step, msg="滚筒动作")
			return True

		elif self.step == "rollerLoad":  # checkSourceSignal -> rollerLoad
			if not self.rollerFrontLoad(self.floor):
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
			self.step = "clearSourceIO"
			taskMgr.update(self.taskId, step=self.step,msg="%s 检测完成信号" % self.sName)
			return True
		#
		# elif self.step == "checkSourceFinish":  # checkTargetRollerFinish -> checkFinish
		# 	# 检测上下板机完成信号 self.fSignal
		# 	s = self._readIO(self.s_io,self.sTypeIo)
		# 	if s is None or s[self.fSignal] != 1:
		# 		if self.count > 50:
		# 			self.step = "fail"
		# 			self.msg = "检查%s[%s]进料完成信号超时" % (self.line, self.sName)
		# 			time.sleep(1)
		# 			self._audioPlay()
		# 		self.count += 1
		# 		return False
		# 	self.count = 0
		# 	self.step = "clearSourceIO"
		# 	taskMgr.update(self.taskId, step=self.step, msg="%s 清除小车到达信号" % self.sName)
		# 	return True

		elif self.step == "clearSourceIO":  # checkSourceRollerFinish -> clearSourceIO
			if not self.writeIO(self.s_io, self.aSignal, 0,self.sTypeIo) or not self.writeIO(self.s_io, self.fOverSignal, 0, self.sTypeIo):  # 到达信号
				if self.count > 15:
					self.step = "fail"
					self.msg = "检查%s[%s]清除到达超时" % (self.line, self.sName)
					self._audioPlay()
				self.count += 1
				return False
			self.count = 0
			self.step = "moveTarget"
			taskMgr.update(self.taskId, step=self.step,msg="%s 小车挡块上升" % self.sName)
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
			self.step = "arriveTarget"
			taskMgr.update(self.taskId, step=self.step, msg="发送%s AGV到达信号" % self.tName)
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
			if not self.rollerFrontUnload(self.floor):
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
			self.step = "finish"
			taskMgr.update(self.taskId, step=self.step, msg="出料完成设置挡块下降")
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
					self.writeIO(self.s_io, self.aSignal, 0,self.sTypeIo)
				if self.canReleaseAgv:
					ret = agvApi.isLocked(self.agvId, self.taskId)
					agvApi.release(self.agvId, self.taskId, force=False)
					# g_relese_agvs.add(self.agvId)
					if ret:
						if checkLineTask(self.line):
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
		except Exception as e:
			log.exception(self.taskId + "getUnitUnloadStatus", e)
			return None
	def checkBarDownStatus(self, agvId, unitId):
		try:
			return rollerPlusApi.checkBarDownStatus(agvId, unitId)["status"]
		# return rollerApi.unitStatus(agvId, unitId)["status"]
		except Exception as e:
			log.exception(self.taskId + "getUnitUnloadStatus", e)
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

    def add(self, task):
        self.tasks[task.taskId] = task
        if task.isInside:
            g_taskInsideQueue.append(task)
        else:
            g_taskQueue.append(task)

    def getTask(self, taskId):
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

    def checkTask(self, task):
        for t in self.tasks.values():
            if t.isRunning and t.isInside == task.isInside and t.sPrepoint == task.tPrepoint and t.tPrepoint == task.sPrepoint:
                log.info(task, "loop with", t)
                return False
        ret = task.islocAvailable(task.s_info["floorId"], task.s_info["prepoint"])
        if not ret:
            log.info(task, "prepoint lock")
        return ret

    def runningCount(self, isInside):
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
                    # 异常的任务还是留下来，保存到文件里，下次继续运行
                    log.debug("task: delete task", id)
                    del self.tasks[id]
            if id in self.cancelTasks:
                self.cancelTasks.remove(id)

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

    @lockImp.lock(g_lock)
    def save(self):
        if self.stopSaveFlag:
            return
        infos = []
        # 时间倒序排序
        for t in self.tasks.values():
            infos.append(t.getSaveInfo())
        infos = sorted(infos, key=lambda v: v["createTime"], reverse=True)
        # if not os.path.exists(self.filename):
        json.dump_file(self.filename, infos)

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
                    t = scadaTask(None, None, "", 0)
                    t.load(info)
                    if info["taskStep"] == "finish":
                        continue
                    if info["taskStep"] == "failed":
                        continue
                    if not findTask(t.taskId):
                        log.error("load task: can't find task", t)
                        continue
                    if t.pda:
                        log.warning("load task: handle with pda", t)
                        continue
                    log.info("load task:", t)
                    # self.add(t)
                    self.tasks[t.taskId] = t
            except Exception as e:
                log.error("load", self.filename, "failed ", e)

    def recover(self):
        if self.hasRecover:
            return
        self.hasRecover = True
        for t in self.tasks.values():
            if t.taskStep == "waiting":
                self.add(t)  # 加入队列
                log.info('task recover: add task', t)
                continue
            t.start()
        time.sleep(3)
        agvApi.startCharge()


g_ScataskMgr = scadaTaskMgr()

if __name__ == "__main__":
    utility.start()

