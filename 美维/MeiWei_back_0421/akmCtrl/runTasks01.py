#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @Time : 2021/4/20 10:45
# @Author : XiongLue Xie
# @File : runTasks01.py
# @description : runTaks

from common import lock as lockImp
from common import mytimer, utility
from beans import scadaTaskBean
from utils import toolsUtil, objectUtil
from dao import taskMgrDao
from agvCtrl import agvApi
import log

import time

g_lock = toolsUtil.getG_lock()
g_taskQueue = toolsUtil.getG_taskQueue()
g_taskMgr = objectUtil.getG_taskMgr()
MAX_AGV_NUM = 3

proName = toolsUtil.getProjectName()
# fileName = "agv.cfg"

g_agvList = toolsUtil.loadAgvList()
g_agvType = toolsUtil.loadAgvType()


@utility.fini()
def stopSave():
	# 防止退出时损坏
	if g_taskMgr:
		g_taskMgr.stopSave()
	log.warning("runTask:stop save file")


g_init = False


@mytimer.interval(1000)
@lockImp.lock(g_lock)
def run():
	global g_init
	if not g_init:
		agvApi.init("MeiWeiTask")
		g_init = True
	g_taskMgr.recover()

	# rint("当前任务数目：",len(g_taskQueue))
	while g_taskMgr.runningCount() < MAX_AGV_NUM and len(g_taskQueue) > 0:
		findTask = None
		for t in g_taskQueue:
			if g_taskMgr.isCancelTask(t.taskId):
				log.warning(t, "is cancel task")
				findTask = t
				break
			if not g_taskMgr.checkTask(t):
				continue
			if not g_taskMgr.isCancelTask(t.taskId):
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

	g_taskMgr.removeFinishTask()


@lockImp.lock(g_lock)
def addTaskByPad(source, target, payloadId, priority,taskKind):
	# log.info(f'Scada send a task to the server from { source } to { target } payloadId: { payloadId }')
	log.info('----------------------------------addTaskByPad-----')
	task = scadaTaskBean.scadaTask(source, target, payloadId, int(priority),btTag=True,taskKind=taskKind)
	g_taskMgr.add(task)
	# log.info('task cmd: got a task from scada',task)
	return task.taskId

@lockImp.lock(g_lock)
def addTaskByButton(source, target, payloadId, priority,btTag,taskKind,devID):
	# log.info(f'Scada send a task to the server from { source } to { target } payloadId: { payloadId }')
	log.info('----------------------------------addTaskByButton-----')
	task = scadaTaskBean.scadaTask(source, target, devID, payloadId, int(priority),btTag,taskKind=taskKind)
	g_taskMgr.add(task)
	# log.info('task cmd: got a task from scada',task)
	return task.taskId


@lockImp.lock(g_lock)
def switchMode(taskId):
	global r_task, c_task
	log.warning('task cmd: switch to pda mode', taskId)
	msg1 = taskMgrDao.get(taskId)['failMsg']
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
		taskMgrDao.error(taskId, failMsg=msg)


@lockImp.lock(g_lock)
def failTask(taskId):
	log.warning('task cmd: fail task', taskId)
	t = g_taskMgr.getTask(taskId)
	lockImp.release(g_lock)
	if t is not None:
		t.canReleaseAgv = True
		t.stop()
	taskMgrDao.fail(taskId, failMsg="task fail by PDA")


@lockImp.lock(g_lock)
def finishTask(taskId):
	log.warning('task cmd: finish task', taskId)
	t = g_taskMgr.getTask(taskId)
	lockImp.release(g_lock)
	if t is not None:
		t.canReleaseAgv = True
		t.stop()
	taskMgrDao.finish(taskId, step="finish")
