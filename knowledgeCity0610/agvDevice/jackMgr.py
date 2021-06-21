import os
import sys
import time

import setup

if __name__ == "__main__":
	setup.setCurPath(__file__)

import utility
import alarm.alarmApi
import log

if utility.is_test():
	import driver.seerAgv.mockAgvCtrl as agvCtrl
else:
	import driver.seerAgv.agvCtrl as agvCtrl


# 自研车体
# 运行状态, 0 = 上升中，1 = 上升到位
def jackUp(agvId, timeout=90,loc=None):
	ret = agvCtrl.jackUp(agvId,loc=loc)
	return _jack(agvId=agvId, timeout=timeout, action="up", successfulNum=1)


def jackDown(agvId, timeout=90,loc=None):
	agvCtrl.jackDown(agvId,loc=loc)
	return _jack(agvId=agvId, timeout=timeout, action="down", successfulNum=1)

##仙知车体顶升
# 运行状态, 0x00 = 上升中，0x01 = 上升到位，0x02 = 下降中，0x03 = 下降到位，0x04 = 停止，0xFF = 执行失败
def jackUpOld(agvId,timeout):
	ret = agvCtrl.jackUpOld(agvId)
	return _jackOld(agvId=agvId,timeout=timeout,action="上升",successfulNum=1)
#

def jackDownOld(agvId ,timeout):
	ret = agvCtrl.jackDownOld(agvId)
	return _jackOld(agvId=agvId,timeout=timeout,action="下降",successfulNum=3)


def _jackOld(agvId,timeout,action,successfulNum):
	for i in range(int(timeout)):
		status = agvCtrl.readStatus1(agvId)
		if "jack_state" in status:
			if status["jack_state"] == successfulNum:
				return {}
			elif status["jack_state"] == 0xff:
				error = agvId + "执行顶升机构" + " 动作：" + action + ",执行失败"
				break
		time.sleep(1)
		return None
	else:
		agvCtrl.cancelTask(agvId)
		error = agvId + "执行顶升机构" + " 动作：" + action + ",命令超时 timeout=" + timeout
	raise Exception(error)



def jackUpCattle(agvId):
	data = [{"id": 1, "status": True}, {"id": 2, "status": False}]
	return agvCtrl.setDOs(agvId, data)


def jackDownCattle(agvId):
	data = [{"id": 1, "status": False}, {"id": 2, "status": True}]
	return agvCtrl.setDOs(agvId, data)

def jackClearCattle(agvId):
	data = [{"id": 1, "status": False}, {"id": 2, "status": False}]   #每次顶升完或者下降完需要清0
	return agvCtrl.setDOs(agvId, data)


def jackStop(agvId):
	agvCtrl.jackStop(agvId)
	return {}

def jackUpStatus(agvId):
	ret=agvCtrl.jackUpStatus(agvId)
	return ret

def jackDownStatus(agvId):
	ret=agvCtrl.jackDownStatus(agvId)
	return ret

def jackDeviceInfo(agvId):
	ret=agvCtrl.jackDeviceInfo(agvId)
	return ret

def jackDistanceStatus(agvId):
	ret=agvCtrl.jackDistanceStatus(agvId)
	return ret
	
# {"status": 1,"isRotationALarm": 1,"isJackAlarm": 1}
def _jack(agvId, timeout, action, successfulNum):
	for i in range(int(timeout)):
		status = None
		if action == "up":
			status = agvCtrl.jackUpStatus(agvId)
		elif action == "down":
			status = agvCtrl.jackDownStatus(agvId)
		ios = agvCtrl.readIOs(agvId)
		#log.info('_jack in jackMgr:', agvId, action, ios['DO'])
		if status != None:
			if "isJackAlarm" in status and status["isJackAlarm"] != 0:
				msg = "jack device has alarm"
				alarm.alarmApi.alarm(moid=agvId, typeId=49996, desc=msg, domain="agv")
				raise Exception(msg+",action:"+action)
			else:
				alarm.alarmApi.clear(moid=agvId, typeId=49996, domain="agv")
			if "status" in status and status["status"] == successfulNum:
				log.info(agvId, 'jack %s status: ' % action, status['status'])
				return {}
		time.sleep(1)
	else:
		# agvCtrl.cancelTask(agvId) # 自研不需要
		error = agvId + "执行顶升机构" + " 动作：" + action + ",命令超时 timeout=" + str(timeout)
	raise Exception(error)

##仙知车体顶升
# 运行状态, 0x00 = 上升中，0x01 = 上升到位，0x02 = 下降中，0x03 = 下降到位，0x04 = 停止，0xFF = 执行失败
def jackUpOld(agvId,loc,timeout):
	ret = agvCtrl.jackUpOld(agvId)
	return _jackOld(agvId=agvId,timeout=timeout,action="上升",successfulNum=1)
#
# def jackUpOldLM(agvId,loc,timeout):
#	ret = agvCtrl.jackUpOldLM(agvId,loc)
#	return _jackOld(agvId=agvId,timeout=timeout,action="上升",successfulNum=1)
#
def jackDownOld(agvId,loc,timeout):
	agvCtrl.jackDownOld(agvId)
	return _jackOld(agvId=agvId,timeout=timeout,action="下降",successfulNum=3)
#	
# def jackStopOld(agvId ,timeout):
#	agvCtrl.jackStopOld(agvId)
#	return _jackOld(agvId=agvId,timeout=timeout,action="停止",successfulNum=4)
#	
def _jackOld(agvId,timeout,action,successfulNum):
	for i in range(int(timeout)):
		status = agvCtrl.readStatus1(agvId)
		if "jack_state" in status:
			if status["jack_state"] == successfulNum:
				return {}
			elif status["jack_state"] == 0xff:
				error = agvId + "执行顶升机构" + " 动作：" + action + ",执行失败"
				break
		time.sleep(1)
		return None
	else:
		agvCtrl.cancelTask(agvId)
		error = agvId + "执行顶升机构" + " 动作：" + action + ",命令超时 timeout=" + timeout 
	raise Exception(error)
