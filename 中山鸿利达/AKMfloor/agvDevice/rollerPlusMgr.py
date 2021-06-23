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


def getRollerType(agvId):
	agvType = agvCtrl._getAgvType(agvId)
	if "rollerType" in agvType:
		return agvType["rollerType"]
	else:
		return None
"""

rollerType类型：
old_tweLayer_oneWay    #AKM smt双成滚筒  一个方向出料
new_tweLayer_oneWay    #中新知识城双成滚筒  一个方向出料
new_oneLayer_tweWay    #一层滚筒 左右出料




AKM smt双成滚筒  
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
	agvCtrl.setDOs(agvId, data)


def rollerRobotPush(agvId):
	rollertype = getRollerType(agvId)
	if rollertype == "new_tweLayer_oneWay":
		data = [{"id": 27, "status": False}, {"id": 26, "status": True}]
	try:
		return agvCtrl.setDOs(agvId, data)
	except Exception as e:
		log.exception(agvId,"rollerRobotLoad failed", e)


def rollerRobotUnPush(agvId):
	rollertype = getRollerType(agvId)
	if rollertype == "new_tweLayer_oneWay":
		data = [{"id": 26, "status": False}, {"id": 27, "status": True}]
	try:
		return agvCtrl.setDOs(agvId, data)
	except Exception as e:
		log.exception(agvId,"rollerRobotLoad failed", e)


def rollerRobotLoad(agvId, unitId):
	rollertype = getRollerType(agvId)
	floor = int(unitId)
	log.info(agvId, "rollerRobotLoad unitId:", unitId)
	if rollertype == "new_oneLayer_tweWay":
		if floor == 1:
			data = [{"id":31,"status":False},{"id":29,"status":True},{"id":30,"status":False},{"id":28,"status":False}]
		if floor == 2:
			data = [{"id": 29, "status": False}, {"id": 31, "status": True},{"id":30,"status":False},{"id":28,"status":False}]
	elif rollertype == "new_tweLayer_oneWay":
		if floor == 1:
			data = [{"id":22,"status":False},{"id":20,"status":True}]
		if floor == 2:
			data = [{"id": 23, "status": False}, {"id": 21, "status": True}]
	try:
		return agvCtrl.setDOs(agvId, data)
	except Exception as e:
		log.exception(agvId,"rollerRobotLoad failed", e)
		# return {"status": None}


def rollerRobotUnLoad(agvId, unitId):
	rollertype = getRollerType(agvId)
	floor = int(unitId)
	log.info(agvId,"rollerRobotUnLoad unitId:",unitId)
	if rollertype == "new_oneLayer_tweWay":
		if floor == 1:
			data = [{"id": 28, "status": True}, {"id": 30, "status": False},{"id":31,"status":False},{"id":29,"status":False}]
		if floor == 2:
			data = [{"id": 30, "status": True}, {"id": 28, "status": False},{"id":31,"status":False},{"id":29,"status":False}]
	elif rollertype == "new_tweLayer_oneWay":
		if floor == 1:
			data = [{"id": 20, "status": False}, {"id": 22, "status": True}]
		if floor == 2:
			data = [{"id": 21, "status": False}, {"id": 23, "status": True}]

	try:
		return agvCtrl.setDOs(agvId, data)
	except Exception as e:
		log.exception(agvId, "rollerRobotUnLoad failed", e)
		# return {"status": None}


def rollerRobotBarUp(agvId, unitId):
	floor = int(unitId)
	log.info(agvId,"rollerRobotUnLoad unitId:",unitId)
	if floor == 1:
		data = [{"id": 33, "status": True}, {"id": 32, "status": False}]
	if floor == 2:
		data = [{"id": 38, "status": True}, {"id": 37, "status": False}]
	try:
		return agvCtrl.setDOs(agvId, data)
	except Exception as e:
		log.exception(agvId, "rollerRobotUnLoad failed", e)
		# return {"status": None}

def rollerRobotBarDown(agvId, unitId):
	floor = int(unitId)
	log.info(agvId,"rollerRobotUnLoad unitId:",unitId)
	if floor == 1:
		data = [{"id": 32, "status": True}, {"id": 33, "status": False}]
	if floor == 2:
		data = [{"id": 37, "status": True}, {"id": 38, "status": False}]
	try:
		return agvCtrl.setDOs(agvId, data)
	except Exception as e:
		log.exception(agvId, "rollerRobotUnLoad failed", e)
		# return {"status": None}



def checkBarUpStatus(agvId, unitId):
	try:
		status = agvCtrl.readIOs(agvId)
	except Exception as e:
		log.exception(agvId,"checkUnitStatus failed", e)
		return {"status": None}
	log.info(agvId, "checkUnitStatus unitId:", unitId)
	DI_list = status["DO"]
	floor = int(unitId)
	if floor == 1:
		for di in 	DI_list:
			if di['id'] == 43 and di["status"]:
				return {"status":1}
		return {"status": 0}
	if floor == 2:
		for di in DI_list:
			if di['id'] == 45 and di["status"]:
				return {"status": 1}
		return {"status": 0}


def checkBarDownStatus(agvId, unitId):
	try:
		status = agvCtrl.readIOs(agvId)
	except Exception as e:
		log.exception(agvId,"checkUnitStatus failed", e)
		return {"status": None}
	log.info(agvId, "checkUnitStatus unitId:", unitId)
	DI_list = status["DO"]
	floor = int(unitId)
	if floor == 1:
		for di in 	DI_list:
			if di['id'] == 42 and di["status"]:
				return {"status":1}
		return {"status": 0}
	if floor == 2:
		for di in DI_list:
			if di['id'] == 44 and di["status"]:
				return {"status": 1}
		return {"status": 0}



def rollerRobotStop(agvId):
	rollertype = getRollerType(agvId)
	if rollertype == "new_oneLayer_tweWay":
		data = [{"id": 24, "status": False}, {"id": 25, "status": False}, {"id": 26, "status": False},
		        {"id": 27, "status": False}, {"id": 39, "status": True}]
	elif rollertype == "new_tweLayer_oneWay":
		data = [{"id": 20, "status": False}, {"id": 21, "status": False}, {"id": 22, "status": False},
		        {"id": 23, "status": False}]
	try:
		return agvCtrl.setDOs(agvId, data)
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
	rollertype = getRollerType(agvId)
	try:
		status = agvCtrl.readIOs(agvId)
	except Exception as e:
		log.exception(agvId,"checkUnitStatus failed", e)
		return {"status": None}
	log.info(agvId, "checkUnitStatus unitId:", unitId)
	if rollertype == "new_oneLayer_tweWay":
		DI_list = status["DO"]
		floor = int(unitId)
		if floor == 1:
			for di in 	DI_list:
				if di['id'] == 48 and di["status"]:
					return {"status":1}
			return {"status": 0}
		if floor == 2:
			for di in DI_list:
				if di['id'] == 48 and di["status"]:
					return {"status": 1}
			return {"status": 0}
	elif rollertype == "new_tweLayer_oneWay":
		DI_list = status["DO"]
		floor = int(unitId)
		if floor == 1:
			for di in DI_list:
				if di['id'] == 35 and di["status"]:
					return {"status": 1}
			return {"status": 0}
		if floor == 2:
			for di in DI_list:
				if di['id'] == 36 and di["status"]:
					return {"status": 1}
			return {"status": 0}


def checkUnitloadStatus(agvId, unitId):
	rollertype = getRollerType(agvId)
	try:
		status = agvCtrl.readIOs(agvId)
	except Exception as e:
		log.exception(agvId,"checkUnitloadStatus failed", e)
		return {"status": None}
	floor = int(unitId)
	log.info(agvId, "checkUnitloadStatus unitId:", unitId)
	if rollertype == "new_oneLayer_tweWay":
		DI_list = status["DO"]
		if floor == 1:
			for di in 	DI_list:
				if di['id'] == 35 and di["status"]:
					return {"status":1}
			return {"status": 0}
		if floor == 2:
			for di in DI_list:
				if di['id'] == 35 and di["status"]:
					return {"status": 1}
			return {"status": 0}
	elif rollertype == "new_tweLayer_oneWay":
		DI_list = status["DO"]
		if floor == 1:
			for di in 	DI_list:
				if di['id'] == 28 and di["status"]:
					return {"status":1}
			return {"status": 0}
		if floor == 2:
			for di in DI_list:
				if di['id'] == 29 and di["status"]:
					return {"status": 1}
			return {"status": 0}




def checkUnitUnloadStatus(agvId, unitId):
	rollertype = getRollerType(agvId)
	try:
		status = agvCtrl.readIOs(agvId)
	except Exception as e:
		log.exception(agvId,"checkUnitUnloadStatus failed", e)
		return {"status": None}
	log.info(agvId, "checkUnitUnloadStatus unitId:", unitId)
	floor = int(unitId)
	if rollertype == "new_oneLayer_tweWay":
		DI_list = status["DO"]
		if floor == 1:
			for di in 	DI_list:
				if di['id'] == 34 and di["status"]:
					return {"status":1}
			return {"status": 0}
		if floor == 2:
			for di in DI_list:
				if di['id'] == 34 and di["status"]:
					return {"status": 1}
			return {"status": 0}
	elif rollertype == "new_tweLayer_oneWay":
		DI_list = status["DO"]
		if floor == 1:
			for di in 	DI_list:
				if di['id'] == 24 and di["status"]:
					return {"status":1}
			return {"status": 0}
		if floor == 2:
			for di in DI_list:
				if di['id'] == 25 and di["status"]:
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
