import os
import sys
import time

import setup

if __name__ == "__main__":
	setup.setCurPath(__file__)

import utility
import log

if utility.is_test():
	import driver.seerAgv.mockAgvCtrl as agvCtrl
else:
	import driver.seerAgv.agvCtrl as agvCtrl


"""
台达PLC扩展IO与SCR2000对照表
X0  一层前进端感应  DI17 
X1  一层出料端感应  DI18 
X2  二层前进端感应  DI19 
X3  二层出料端感应  DI20 

Y0  一层进料正转    DO8
Y1  一层出料反转    DO9
Y2  一层出料正转    DO10
Y3  一层出料反转    DO11
"""


def rollerSetInit(agvId):
	data = [{"id":16,"status":False},{"id":17,"status":False},{"id":20,"status":False},{"id":21,"status":False}]
	agvCtrl.setDO(agvId, data)


def rollerRobotLoad(agvId, unitId):
	floor = int(unitId)
	log.info(agvId,"rollerRobotLoad unitId:",unitId)
	if floor == 1:
		data = [{"id":16,"status":False},{"id":20,"status":True}]
	if floor == 2:
		data = [{"id": 17, "status": False}, {"id": 21, "status": True}]
	try:
		agvCtrl.setDO(agvId, data)
	except Exception as e:
		log.exception(agvId,"rollerRobotLoad failed", e)
		# return {"status": None}

def rollerRobotUnLoad(agvId, unitId):
	floor = int(unitId)
	log.info(agvId,"rollerRobotUnLoad unitId:",unitId)
	if floor == 1:
		data = [{"id": 16, "status": True}, {"id": 20, "status": False}]
	if floor == 2:
		data = [{"id": 17, "status": True}, {"id": 21, "status": False}]
	try:
		agvCtrl.setDO(agvId, data)
	except Exception as e:
		log.exception(agvId, "rollerRobotUnLoad failed", e)
		# return {"status": None}



def rollerRobotStop(agvId):
	data = [{"id":16,"status":False},{"id":17,"status":False},{"id":20,"status":False},{"id":21,"status":False},{"id":39,"status":False}]
	try:
		agvCtrl.setDO(agvId, data)
	except Exception as e:
		log.exception(agvId, "rollerRobotStop failed", e)
		# return {"status": None}
"""
def rollerFinishStatus(status, action):
	DI_list = status["DI"]
	# DO_list = status["DO"]
	if action == "FirstLoad":
		for di in 	DI_list:
			if di['id'] == 17 and di["status"]:
				return True
	elif action == "FirstUnload":
		backSennor = False
		frontSennor = False
		for di in 	DI_list:
			if di['id'] == 17 and not di["status"]:
				backSennor = True
			if di['id'] == 18 and not di["status"]:
				frontSennor = True
			if backSennor and frontSennor:
				return True
	elif action == "SecondLoad":
		for di in 	DI_list:
			if di['id'] == 19 and di["status"]:
				return True
	elif action == "SecondUnload":
		backSennor = False
		frontSennor = False
		for di in 	DI_list:
			if di['id'] == 19 and not di["status"]:
				backSennor = True
			if di['id'] == 20 and not di["status"]:
				frontSennor = True
			if backSennor and frontSennor:
				return True
	return False

"""

def checkUnitStatus(agvId, unitId):
	try:
		status = agvCtrl.readIOs(agvId)
	except Exception as e:
		log.exception(agvId,"checkUnitStatus failed", e)
		return {"status": None}
	log.info(agvId, "checkUnitStatus unitId:", unitId)
	DI_list = status["DI"]
	floor = int(unitId)
	if floor == 1:
		for di in 	DI_list:
			if di['id'] == 17 and di["status"]:
				return {"status":1}
			elif di['id'] == 18 and di["status"]:
				return {"status":1}
		return {"status": 0}
	if floor == 2:
		for di in DI_list:
			if di['id'] == 19 and di["status"]:
				return {"status": 1}
			elif di['id'] == 20 and di["status"]:
				return {"status": 1}
		return {"status": 0}



def rollerRes(agvId):
	data = {"id":39,"status":False}
	agvCtrl.setDO(agvId, data)



def rollerEmergency(agvId):
	status = agvCtrl.checkEmergency(agvId)
	if status:
		return status


# def _roller(agvId, timeout, action):
# 	for i in range(int(timeout)):
# 		time.sleep(1)
# 		status = agvCtrl.readIOs(agvId)
# 		if rollerFinishStatus(status,action):
# 			# if action == 'FirstLoad' or action == 'FirstUnload':
# 			# 	rollerFirstStop(agvId)
# 			# if action == 'SecondLoad' or action == 'SecondUnload':
# 			# 	rollerSecondStop(agvId)
# 			# log.info(agvId, "roller %s status:success." % action)
# 			return {}
# 	else:
# 		agvCtrl.cancelTask(agvId) # 自研车体不需要
# 		rollerFirstStop(agvId)
# 		rollerSecondStop(agvId)
# 		error = agvId + "roller" + " action：" + action + ",timeout=" + timeout
# 		raise Exception(error)
