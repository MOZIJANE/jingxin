#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @Time : 2021/4/20 10:05
# @Author : XiongLue Xie
# @File : toolsUtil.py
# @description 获取一些常用的全局变量

from common import lock as lockImp
import os
import json as json2
import time

global g_lock
g_lock = lockImp.create("runTasks.g_lock")

global g_taskQueue
g_taskQueue = []


projectName = "AKMfloor"
# 存储project目录下配置文件的对象
g_agvList = {}
g_agvType = {}

g_taskPath = {}

def setTaskPath(tid,path):
	g_taskPath[tid] = path

def getTaskPath(tid):
	return g_taskPath[tid]

#清除过期的path释放空间
#定时调用或者执行完调用都可以
def clearTaskPath(tid):
	del g_taskPath[tid]

def getCurTime():
	curTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
	return curTime

def loadAgvList():
	file = "/../../agvCtrl/projects/"+projectName+"/" + "agv.cfg"
	with open(os.path.abspath(os.path.dirname(__file__) + file), 'r') as f:
		agvList = {}
		aa = json2.load(f)
		for a in aa:
			if aa[a]["enable"].lower() == "false":
				continue
			agvList[a] = aa[a]
		return agvList

def getAgvType(agvId):
	type_ = g_agvList[agvId]["type"]
	return g_agvType[type_]

def loadAgvType():
	file = "/../../agvCtrl/projects/"+projectName+"/" + "agvType.cfg"
	with open(os.path.abspath(os.path.dirname(__file__) + file), 'r') as f:
		agvTypeDict = {}
		aa = json2.load(f)
		for a in aa:
			agvTypeDict[a] = aa[a]
		return agvTypeDict

def getProjectName():
	return projectName

def getG_taskQueue():
	return g_taskQueue

def getG_lock():
	return g_lock

def setLock(name):
	lock = lockImp.create(name)
	return lock