#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @Time : 2021/4/20 10:01
# @Author : XiongLue Xie
# @File : scadaTaskMgrBean.py
import os

from dao import taskMgrDao as taskMgr
from utils import toolsUtil
import log
from common import json_codec as json
from agvCtrl import agvApi

import lock as lockImp
import time

g_lock = toolsUtil.getG_lock()
g_taskQueue = toolsUtil.getG_taskQueue()

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

	# 这个g_taskQueue独立出来其实干嘛的，已经有任务管理类，且每个任务都对应好了id
	def add(self,task):
		self.tasks[task.taskId] = task
		g_taskQueue.append(task)

	# def add(self, task):
	# 	self.tasks[task.taskId] = task
	# 	if task.isInside:
	# 		g_taskInsideQueue.append(task)
	# 	else:
	# 		g_taskQueue.append(task)

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
			#if t.isRunning and t.isInside == task.isInside and t.sPrepoint == task.tPrepoint and t.tPrepoint == task.sPrepoint:
			if t.isRunning and t.sPrepoint == task.tPrepoint and t.tPrepoint == task.sPrepoint:
				log.info(task, "loop with", t)
				return False
		log.info(task.s_info)
		ret = task.islocAvailable(task.s_info["floorId"], task.s_info["prepoint"])
		if not ret:
			log.info(task, "prepoint lock")
		return ret

	def runningCount(self):
		ret = 0
		for t in self.tasks.values():
			if t.isRunning:
				ret += 1
		return ret

	# def runningCount(self, isInside):
	# 	ret = 0
	# 	for t in self.tasks.values():
	# 		if t.isRunning and t.isInside == isInside:
	# 			ret += 1
	# 	return ret

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

	# def findTask(id):
	# 	for d in ds:
	# 		if id == str(d["_id"]):
	# 			return True
	# 	return False
	# if os.path.exists(self.filename):
	#
	# 	try:
	# 		infos = json.load_file(self.filename)
	# 		for info in infos:
	# 			t = scadaTask(None,None,"",0)
	# 			t.load(info)
	# 			if info["taskStep"] == "finish":
	# 				continue
	# 			if info["taskStep"] == "failed":
	# 				continue
	# 			if not findTask(t.taskId):
	# 				log.error("load task: can't find task",t)
	# 				continue
	# 			if t.pda:
	# 				log.warning("load task: handle with pda",t)
	# 				continue
	# 			log.info("load task:",t)
	# 			#self.add(t)
	# 			self.tasks[t.taskId] = t
	# 	except Exception as e:
	# 		log.error("load", self.filename, "failed ", e)

	def recover(self):
		if self.hasRecover:
			return
		self.hasRecover = True
		for t in self.tasks.values():
			if t.taskStep == "waiting":
				self.add(t)  # 加入队列
				log.info('task recover: add task', t)
				continue
			print("回复任务，",t.name)
			t.start()
		time.sleep(3)
		agvApi.startCharge()