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
print (lockImp.__file__)
import agvCtrl.agvApi as agvApi
import agvDevice.jackApi as jackApi
import agvDevice.rotationApi as rotationApi
# import driver.seerAgv.agvCtrl as jackApi

def test_agv4(mapId,target1):
	taskId = utility.now_str()
	agvId = agvApi.apply(taskId, mapId, target1)
	objCharge = agvApi.getAgvStatus(agvId)
	paramObj = {}
	paramObj["agv"] = agvId
	paramObj["loc"] = target1
	paramObj["result"] = 0
	paramObj["resultDesc"] = "success"
	paramObj["taskId"] = taskId + target1 
	paramObj["timeoutSec"] = 10000
	print(objCharge)
	
		
def test_agv55(map,target1,target2):
	import threading
	agvList = None
	result = None
	count = 0
	r_lock = threading.RLock()
	def finishCallback1(obj):
		print("finishCallback1")
		nonlocal running1,running2,result
		if obj["result"] :
			log.info(utility.now(),obj["agv"],"finish1  ----------------------------")
			result = 1
		else:
			log.warning(utility.now(),obj["agv"],"not finish1 ----------------------")
			result = -1
		r_lock.acquire()
		if obj["loc"] == target1:
			running1 = False
		else:
			running2 = False
		r_lock.release()
		
	while True:
		taskId = utility.now_str()
		agvId = None
		try:
			agvId = agvApi.apply(taskId, map, target1)
		except Exception as e:
			log.warning(str(e))
		paramObj = {}
		paramObj["agv"] = agvId
		paramObj["loc"] = target1
		paramObj["result"] = 0
		paramObj["resultDesc"] = "success"
		paramObj["taskId"] = taskId + target1 
		paramObj["timeoutSec"] = 10000
		
		running1 = True
		running2 = True
		try: 
			agvApi.move(agvId, target1, finishCallback1, paramObj)
		except Exception as e:
			# print("move fail")
			log.warning(str(e))
			agvApi.release(agvId,taskId)
			agvApi.goHome(agvId)
			time.sleep(2)
			continue
		while True:
			# print("wait running1")
			r_lock.acquire()
			if not running1:
				r_lock.release()
				break
			r_lock.release()
			log.info(agvId,"running1 +++++++++++++++++++++++++++++")
			time.sleep(1)
		if result == -1:
			agvApi.release(agvId,taskId)
			agvApi.goHome(agvId)
			time.sleep(2)
			continue
		
		paramObj["loc"] = target2
		paramObj["taskId"] =  taskId + target2
		log.info(paramObj)
		try:
			agvApi.move(agvId, target2, finishCallback1, paramObj)
		except Exception as e :
			log.warning(str(e))
			agvApi.release(agvId,taskId)
			agvApi.goHome(agvId)
			time.sleep(2)
			continue
		
		while True:
			r_lock.acquire()
			if not running2:
				r_lock.release()
				break
			r_lock.release()
			log.info(agvId,"running2 +++++++++++++++++++++++++++++")
			time.sleep(1)
		if agvId:
			agvApi.release(agvId,taskId)
		# agvApi.goHome(agvId)
		time.sleep(20)


	
		
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
	def filterFunC(agvId, mapId, loc, payload):
		if agvId == 'AGV03':
			return True
		else:
			return False
	
	while True:	

		taskId = map + ":" + utility.now_str()
		agvId = None
		try:
			agvId = agvApi.apply(taskId, map, "LM7",filterFunc=filterFunC)
		except Exception as e:
			log.exception("apply",e)
			time.sleep(5)
			continue
		if not agvId :
			time.sleep(5)
			continue
			
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
				elif operation == "JackUP":
					jackApi.jackUp(agvId,timeoutSec=90)
					running = False
				elif operation == "JackDown":
					jackApi.jackDown(agvId,timeoutSec=90)
					running = False
				elif operation == "rotationLeft":
					rotationApi.rotationLeft(agvId,target=90)
					running = False
				elif operation == "rotationRight":
					rotationApi.rotationRight(agvId,target=90)
					running = False
				elif operation == "rotationClear":
					rotationApi.rotationClear(agvId) 
					running = False
				else:
					agvApi.move(agvId, target, finishCallback1, paramObj)
				time.sleep(10)
			except Exception as e :
				log.exception("move",e)
				time.sleep(2)
				continue
			#	raise
			
			while True:
				r_lock.acquire()
				if not running:
					r_lock.release()
					break
				r_lock.release()
				log.info(agvId,target+" running+++++++++++++++++++++++++++++")
				time.sleep(2)	
			if result == -1:
				time.sleep(2)
				continue
				# raise Exception("fail")
			
			
		if agvId :
			agvApi.release(agvId,taskId)
		# agvApi.goHome(agvId)
		agvId = None
		# time.sleep(10)

		
def test_agv77(map,targetList,targetList2):
	import threading
	agvList = None
	result = None
	count = 0
	r_lock = threading.RLock()
	r_lock2 = threading.RLock()
	
	taskId = utility.now_str()
	taskId2 = utility.now_str()
	agvId = None
	
	agvId = agvApi.apply(taskId, map, "LM6")		
	agvId2 = agvApi.apply(taskId2, map, "LM6")	
	
	paramObj = {}
	paramObj["agv"] = agvId
	paramObj["loc"] = ""
	paramObj["result"] = 0
	paramObj["resultDesc"] = "success"
	paramObj["taskId"] = taskId 
	paramObj["timeoutSec"] = 10000	
	
	paramObj2 = {}
	paramObj2["agv"] = agvId2
	paramObj2["loc"] = ""
	paramObj2["result"] = 0
	paramObj2["resultDesc"] = "success"
	paramObj2["taskId"] = taskId2
	paramObj2["timeoutSec"] = 90000	
	
	def threading_agv():	
		while True:
			rollerFlag = 0
			rollerLoadFlag = True
			running = True
			for target in targetList:
				rollerFlag = rollerFlag+1
				paramObj["loc"] = target
				paramObj["taskId"] =  taskId + target
				running = True
				log.info(paramObj)
				try:
					agvApi.move(agvId, target, finishCallback1, paramObj)
				except Exception as e :
					log.warning(str(e))
					agvApi.release(agvId,taskId)
					agvApi.goHome(agvId)
					time.sleep(2)
					continue				
				while True:
					r_lock.acquire()
					if not running:
						r_lock.release()
						break
					r_lock.release()
					log.info(agvId,target+" running+++++++++++++++++++++++++++++")
					time.sleep(1)	
				while True:
					r_lock2.acquire()
					if not running2:
						r_lock2.release()
						break
					r_lock2.release()
					log.info(agvId2,target+" running2+++++++++++++++++++++++++++++")
					time.sleep(1)						
				if result == -1:
					agvApi.release(agvId,taskId)
					agvApi.goHome(agvId)
					time.sleep(2)
					continue
				if rollerFlag == 2:
					if rollerLoadFlag:
						rollerPlusApi.rollerRobotLoad(agvId,1)
						rollerPlusApi.rollerRobotLoad(agvId,2)	
					else:
						rollerPlusApi.rollerRobotUnLoad(agvId,1)
						rollerPlusApi.rollerRobotUnLoad(agvId,2)
					time.sleep(8)
			rollerLoadFlag = not rollerLoadFlag	
					
	
	def threading_agv2():	
		while True:
			rollerFlag = 0
			rollerLoadFlag = False
			running2 = True
			for target in targetList2:
				rollerFlag = rollerFlag+1
				paramObj2["loc"] = target
				paramObj2["taskId"] =  taskId2 + target
				running = True
				log.info(paramObj)
				try:
					agvApi.move(agvId2, target, finishCallback1, paramObj2)
				except Exception as e :
					log.warning(str(e))
					agvApi.release(agvId2,taskId)
					agvApi.goHome(agvId2)
					time.sleep(2)
					continue				
				while True:
					r_lock.acquire()
					if not running:
						r_lock.release()
						break
					r_lock.release()
					log.info(agvId,target+" running+++++++++++++++++++++++++++++")
					time.sleep(1)	
				while True:
					r_lock2.acquire()
					if not running2:
						r_lock2.release()
						break
					r_lock2.release()
					log.info(agvId2,target+" running2+++++++++++++++++++++++++++++")
					time.sleep(1)						
				if result == -1:
					agvApi.release(agvId2,taskId)
					agvApi.goHome(agvId2)
					time.sleep(2)
					continue
				if rollerFlag == 2:
					if rollerLoadFlag:
						rollerPlusApi.rollerRobotLoad(agvId2,1)
						rollerPlusApi.rollerRobotLoad(agvId2,2)	
					else:
						rollerPlusApi.rollerRobotUnLoad(agvId2,1)
						rollerPlusApi.rollerRobotUnLoad(agvId2,2)
					time.sleep(8)
			rollerLoadFlag = not rollerLoadFlag	
					
	t = threading.Thread(target=test_agv6)
	r = threading.Thread(target=test_agv5)
	t.start()
	r.start()
	
	if agvId :
		agvApi.release(agvId,taskId)
	if agvId2 :
		agvApi.release(agvId2,taskId)

		



if __name__ == '__main__':	
	targetList4 = [
					{"id": "LM7","operation": ""},
					{"id": "LM8","operation": ""}
				] 
				
				
	targetList5 = [
					{"id": "LM15","operation": ""},
					{"id": "LM15","operation": "JackUP"},
					{"id": "LM19","operation": ""},
					#{"id": "LM19","operation": "rotationLeft"},
					{"id": "LM15","operation": ""},
					{"id": "LM15","operation": "JackDown"},

					{"id": "LM18","operation": ""},
					{"id": "LM18","operation": "JackUP"},
					{"id": "LM19","operation": ""},
					#{"id": "LM19","operation": "rotationRight"},
					{"id": "LM18","operation": ""},
					{"id": "LM18","operation": "JackDown"},
					#{"id": "LM18","operation": "rotationClear"}
					
				] 

	# agvApi.init("feed1")
	# test_agv66("1116",targetList5)
	
	agvApi.init("feed2")
	test_agv66("AKM-TEST2",targetList4)
	
	while True:
		time.sleep(1)
	
