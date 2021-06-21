#coding=utf-8
# ycat			2018-8-2	  create
# 对外提供AGV的业务  
import sys,os 
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import time
import threading

TASK_TIME = 2  # 任务运行时间(秒)

TASK_STATUS_NONE=0
TASK_STATUS_WAITING=1
TASK_STATUS_RUNNING=2
TASK_STATUS_SUSPENDED=3
TASK_STATUS_COMPLETED=4
TASK_STATUS_FAILED=5
TASK_STATUS_CANCELED=6

def defaultStatus():
	d = {}
	d["odo"] = 0
	d["time"] = 0
	d["total_time"] = 0
	d["battery_level"] = 0.8
	d["charging"] = False

	d["mode"] = 1
	d["x"] = 10
	d["y"] = 12
	d["angle"] = 0
	d["confidence"] = 1
	d["vx"] = 0
	d["vy"] = 0
	d["w"] = 0
	d["steer"] = 0
	d["blocked"] = False

	d["emergency"] = False
	d["DI"] = [False] * 16
	d["DO"] = [False] * 16
	d["DI_valid"] = ["True"] * 16

	d["task_status"] = 0
	d["task_type"] = 0
	d["reloc_status"] = 1
	d["loadmap_status"] = 1
	d["slam_status"] = 0

	d["fatals"] = []
	d["errors"] = []
	d["warnings"] = []
	d["ret_code"] = 0
	d["err_msg"] = ""
	d["mock"] = {}
	
	d["target_id"] = None
	return d

g_agvs = {}

def _getAgv(agvId):
	global g_agvs
	if agvId not in g_agvs:
		g_agvs[agvId] = defaultStatus()
	return g_agvs[agvId]

def setAgvStatus(agvId, key, value):
	s = _getAgv(agvId) 
	s[key] = value

def _taskFunc(agvId, status, func, paramObj):
	time.sleep(TASK_TIME)
	setAgvStatus(agvId, "task_status", status)
	func(paramObj)

def move(agvId,loc,finishCallback,paramObj):
	setAgvStatus(agvId, "target_id", loc)
	setAgvStatus(agvId, "task_status", TASK_STATUS_RUNNING) 
	t = threading.Thread(target=_taskFunc, args=(agvId, TASK_STATUS_COMPLETED, finishCallback, paramObj))
	t.start()
	t.join()

def apply(loc, mapId, taskId, filterFunc=None):
	if filterFunc("agv1",mapId, loc):
		return "agv1"
	return ""

def release(agvId):
	pass

def goHome(agvId):
	pass