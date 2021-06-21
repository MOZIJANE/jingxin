# coding: utf-8
# author: pengshuqin
# date: 2019-05-05
# desc: agv任务管理
import os
import sys
import time
import threading
import setup
if __name__ == "__main__":
	setup.setCurPath(__file__)

import lock as lockImp
import utility
import mytimer
import log

g_lock = lockImp.create("taskList.lock")
g_taskList = {}

@lockImp.lock(g_lock)
def add(taskId,agvId):
	global g_taskList
	g_taskList[taskId] = {
		"id":taskId,
		"ticks":mytimer.ticks(),#计算任务时长 
		"status":"begin",		#任务状态
		"exception":None,		#是否有异常
		"success":False,		#是否成功
		"createTime":utility.now(), 
		"agv":agvId,
		"target":"",			#任务目标点
		"start":"",				#任务开始点
		"map":"",				#当前移动的地图 
		"action":"",			#任务动作：目前只有move
		"step":0,				#任务执行步骤，每做一个动作，step会+1 
		"paths":"",				#任务路径，多路径（电梯）只用当前这个路径 
		"unfinishPaths":""		#任务未完成路径
		}
	
@lockImp.lock(g_lock)
def finish(taskId,agvId,error=None):
	global g_taskList
	if taskId not in g_taskList:
		add(taskId,agvId) 
	g_taskList[taskId]["status"] = "finish"
	g_taskList[taskId]["exception"] = error
	g_taskList[taskId]["success"] = error is None
	if g_taskList[taskId]["success"]:
		g_taskList[taskId]["unfinishPaths"] = ""
	g_taskList[taskId]["finishTime"] = utility.now()
	
@lockImp.lock(g_lock)
def get(taskId):
	global g_taskList
	if taskId in g_taskList:
		return g_taskList[taskId]
	else:
		return None
		
@lockImp.lock(g_lock)
def getList(taskList):
	ret = {}
	for taskId in taskList:
		ret[taskId] = get(taskId)
	return ret
	
@lockImp.lock(g_lock)
def getAllList():
	global g_taskList
	return utility.clone(g_taskList)
	
@mytimer.interval(60000)
@lockImp.lock(g_lock)
def _check():
	global g_taskList
	r = []
	for id in g_taskList:
		if mytimer.ticks() - g_taskList[id]["ticks"] > 24*60*60*1000:
			r.append(id)
	for id in r:
		del g_taskList[id]
		
@lockImp.lock(g_lock)
def update(taskId,agvId,key,value):
	global g_taskList
	if taskId not in g_taskList:
		add(taskId,agvId)
	g_taskList[taskId][key] = value 
	
	
		
#####################################  UNIT TEST ################################
def test_taskList():
	for i in range(100):
		add(i)
	for i in range(100):
		s = get(i)
		assert s["status"] == "wait"
		assert s["ticks"] != None
		assert s["exception"] == None
		assert s["success"] == False
		
	for i in range(50):
		finish(i,"test%s"%i)
	for i in range(50,100):
		finish(i)
		
	for i in range(50):
		s = get(i)
		assert s["status"] == "finish"
		assert s["ticks"] != None
		assert s["exception"] == "test%s"%i
		assert s["success"] == False
		
	for i in range(50,100):
		s = get(i)
		assert s["status"] == "finish"
		assert s["ticks"] != None
		assert s["exception"] == None
		assert s["success"] == True
		
	mytimer.set_pass_ticks(8*60*60*1000)
	print ("wait... 61s")
	time.sleep(65)
	for i in range(100):
		s = get(i)
		assert s == None
	
if __name__ == "__main__":
	utility.start()
	utility.run_tests()
	

