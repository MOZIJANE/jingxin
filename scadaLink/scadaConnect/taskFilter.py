import os
import sys
import time
import datetime

import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)

import webutility
import lock as lockImp
import mongodb as db
import taskMgr
import config 
import locMgr 
import log
import json_codec as json
g_lock = lockImp.create("tastFilter.g_lock")

g_locInfo=None


inside_url = config.get("urlInfo","inside_url") 
outside_url = config.get("urlInfo","outside_url") 
print("inside_url",inside_url)
print("outside_url",outside_url)

def http_get(url,param,timeout=90):
	r = webutility.http_get(url, param,timeout=timeout)
	result = json.load(r)
	if result["errorno"] != 0: 
		raise IOError(result["errormsg"])
	return result


@lockImp.lock(g_lock)
def checkLocInside(source,target):
	global g_locInfo
	if g_locInfo is None:
		g_locInfo = locMgr.getLoc()
	source = source.strip()
	target = target.strip()
	for loc in g_locInfo:
		if loc["_id"] == source:
			if loc["floorId"].strip() == 'fp-neiwei':
				return True
		elif loc["_id"] == target:
			if loc["floorId"].strip() == 'fp-neiwei':
				return True
	return False

@lockImp.lock(g_lock)
def checkTaskInside(taskId):
	global g_locInfo
	if g_locInfo is None:
		g_locInfo = locMgr.getLoc()
	task = taskMgr.get(taskId)
	source = task["source"].strip()
	target = task["target"].strip()
	for loc in g_locInfo:
		if loc["_id"] == source:
			if loc["floorId"].strip() == 'fp-neiwei':
				return True
		elif loc["_id"] == target:
			if loc["floorId"].strip() == 'fp-neiwei':
				return True
	return False


def addTask(source,target,payloadId,priority):
	param ={}
	param['source'] = source
	param['target'] = target
	param['payloadId'] = payloadId
	param['priority'] = priority
	checkLocInside(source,target)
	if checkLocInside(source,target):
		return http_get(inside_url + '/api/scada/addTask',param)
	else:
		return http_get(outside_url + '/api/scada/addTask',param)
		



def failTask(taskId):
	param ={}
	param['taskId'] = taskId
	if checkTaskInside(taskId):
		return http_get(inside_url + '/api/scada/fail',param)
	else:
		return http_get(outside_url + '/api/scada/fail',param)
	

def finishTask(taskId):
	param ={}
	param['taskId'] = taskId
	if checkTaskInside(taskId):
		return http_get(inside_url + '/api/scada/finish',param)
	else:
		return http_get(outside_url + '/api/scada/finish',param)
	

def switchMode(taskId):
	param ={}
	param['taskId'] = taskId
	if checkTaskInside(taskId):
		return http_get(inside_url + '/api/scada/cancelTask',param)
	else:
		return http_get(outside_url + '/api/scada/cancelTask',param)
	

def allowTask(taskId,locId):
	param ={}
	param['taskId'] = taskId
	param['locId'] = locId
	if checkTaskInside(taskId):
		return http_get(inside_url + '/api/scada/allowTask',param)
	else:
		return http_get(outside_url + '/api/scada/allowTask',param)
	


def getTaskStatus():
	return {http_get(inside_url +'/api/scada/allowTask')["status"]+http_get(outside_url + '/api/scada/allowTask')["status"]}


def feed(param):
	if checkLocInside(param["seat1"].strip(),param["seat2"].strip()):
		return http_get(inside_url + '/api/manual/feed',param)
	else:
		return http_get(outside_url + '/api/manual/feed',param)


