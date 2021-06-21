# coding: utf-8
# author: pengshuqin
# date: 2019-10-16
# desc: 上料机对接

import os
import sys
import time
import bottle
import datetime
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import log
import time
import utility

import lock as lockImp
# print (lockImp.__file__)
import agvCtrl.agvApi as agvApi
import agvDevice.jackApi as jackApi

		
def test_agv66(map,targetList):
	import threading
	agvList = None
	result = None
	count = 0
	r_lock = threading.RLock()
	isUp = False
	def finishCallback1(obj):
		print("finishCallback1")
		nonlocal running,result
		r_lock.acquire()
		if obj["result"] :
			log.info(utility.now(),obj["agv"],obj["loc"],"finish1  ----------------------------")
			running = False
			result = 1
		else:
			log.warning(utility.now(),obj["agv"],obj["loc"],"not finish1 ----------------------")
			running = False
			result = -1
		r_lock.release()
		
	while True:	

		taskId = map + ":" + utility.now_str()
		agvId = None
		try:
			agvId = agvApi.apply(taskId, map, "18")		
		except Exception as e:
			log.exception("apply",e)
			time.sleep(5)
			continue
		if not agvId :
			time.sleep(5)
			continue
		time.sleep(5)
		running = True		
		for task in targetList:
			target = task["id"]
			operation = task["operation"]
			paramObj = {}
			paramObj["agv"] = agvId
			paramObj["loc"] = target
			paramObj["result"] = 0
			paramObj["resultDesc"] = "success"
			paramObj["taskId"] = taskId +"----"+ target + "----"+ utility.now_str()
			paramObj["timeoutSec"] = 20*60	
			running = True
			log.info(paramObj,operation)
			try:
				if operation == "JackLoad":
					agvApi.moveJackup(agvId,target,finishCallback1,paramObj)
				elif operation == "JackUnload":
					agvApi.moveJackdown(agvId,target,finishCallback1,paramObj)
				else:
					agvApi.move(agvId, target, finishCallback1, paramObj)
				time.sleep(3)
			except Exception as e :
				log.exception("move",e)
				time.sleep(2)
				# continue
				raise
			
			while True:
				r_lock.acquire()
				if not running:
					r_lock.release()
					break
				r_lock.release()
				log.info(agvId,target+" running+++++++++++++++++++++++++++++")
				time.sleep(2)
			try:
				jackApi.jackUp(agvId)
				time.sleep(3)
				jackApi.jackDown(agvId)
				jackApi.jackDown(agvId)
			except Exception as e:
				log.exception("jack error:",e)
			if result == -1:
				time.sleep(2)
				continue
				raise Exception("fail")
			
			
		if agvId :
			agvApi.release(agvId,taskId)
		# agvApi.goHome(agvId)
		agvId = None
		# time.sleep(10)



if __name__ == '__main__':
	
	targetList6 = [
					{"id": "1","operation": ""},
					{"id": "4","operation": ""}
				]
	
	agvApi.init("feed3")
	test_agv66("test0305_2",targetList6)
	
	while True:
		time.sleep(1)
	
