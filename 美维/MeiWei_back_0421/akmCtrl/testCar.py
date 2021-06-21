#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @Time : 2021/4/25 14:07
# @Author : XiongLue Xie
# @File : testCar.py

import setup

if __name__ == '__main__':
	setup.setCurPath(__file__)
import log
import time
import utility

import agvCtrl.agvApi as agvApi



def test_agv66(map, targetList):
	import threading
	agvList = None
	result = None
	count = 0
	r_lock = threading.RLock()
	isUp = False

	def finishCallback1(obj):
		print("finishCallback1")
		nonlocal running, result
		r_lock.acquire()
		if obj["result"]:
			log.info(utility.now(), obj["agv"], obj["loc"], "finish1  ----------------------------")
			running = False
			result = 1
		else:
			log.warning(utility.now(), obj["agv"], obj["loc"], "not finish1 ----------------------")
			running = False
			result = -1
		r_lock.release()

	while True:

		taskId = map + ":" + utility.now_str()
		agvId = None
		try:
			utility.set_test()
			agvId = agvApi.apply(taskId, map, "18")
		except Exception as e:
			log.exception("apply", e)
			time.sleep(5)
			continue
		if not agvId:
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
			paramObj["taskId"] = taskId + "----" + target + "----" + utility.now_str()
			paramObj["timeoutSec"] = 20 * 60
			running = True
			log.info(paramObj, operation)
			try:
				if operation == "JackLoad":
					agvApi.moveJackup(agvId, target, finishCallback1, paramObj, use_pgv=True)
				elif operation == "JackUnload":
					agvApi.moveJackdown(agvId, target, finishCallback1, paramObj)
				else:
					agvApi.move(agvId, target, finishCallback1, paramObj)
				time.sleep(3)
			except Exception as e:
				log.exception("move", e)
				time.sleep(2)
				# continue
				raise

			while True:
				r_lock.acquire()
				if not running:
					r_lock.release()
					break
				r_lock.release()
				log.info(agvId, target + " running+++++++++++++++++++++++++++++")
				time.sleep(2)

			if result == -1:
				time.sleep(2)
				# continue
				raise Exception("fail")

		if agvId:
			agvApi.release(agvId, taskId)
		# agvApi.goHome(agvId)
		agvId = None


# time.sleep(10)


if __name__ == '__main__':

	targetList5 = [
		{"id": "1", "operation": "JackLoad"},
		{"id": "4", "operation": "JackUnload"},
		{"id": "6", "operation": ""},
		{"id": "4", "operation": "JackLoad"},
		{"id": "1", "operation": "JackUnload"},
		{"id": "6", "operation": ""}
	]

	agvApi.init("feed2")
	test_agv66("untitled_20210420032952", targetList5)

	while True:
		time.sleep(1)

