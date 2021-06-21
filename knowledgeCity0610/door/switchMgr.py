# coding=utf-8
# ycat			2018-8-2	  create
# AGV管理  
import sys, os
import threading
import json
import setup

if __name__ == '__main__':
	setup.setCurPath(__file__)
import utility
import lock as lockImp
import local
import time
import log
import enhance
import door.switchControl as switchControl
import door.doorControl as doorControl
import door.doorControlQLZ as doorControlQLZ
# 位置信息事件
# 参数：swichId,x,y,angle
locationEvent = enhance.event()

# 位置信息事件
# 参数: swichId,targetName
targetLocEvent = enhance.event()

# 电池电量事件
# 参数: swichId
# level: [0,1]是电量范围
# ischarging: True正在充电，False未充电
batteryEvent = enhance.event()

# swich重启事件
# 参数: swichId
#rebootEvent = enhance.event()

g_lock = lockImp.create("door.lock")
g_swichList = None

def getDoor(swichId):
	return getDoorList()[swichId]

def getDoorByMapId(mapId):
	swichList = getDoorList()
	result = {}
	for switch in swichList:
		if swichList[switch].map==mapId:
			result[switch] = swichList[switch]
	return  result


g_cur_path = __file__


def _loadDoorList():
	global g_cur_path
	
	proName = local.get("project","name")
	if utility.is_test():
		proName = "test" 
	file = os.path.abspath(os.path.dirname(__file__)+"/..") + "/agvCtrl/projects/"+proName+"/door.json"
	 
	with open(file, 'r') as f:
		swichList = json.load(f)
		ret = {}
		for swichId in swichList:
			if swichList[swichId]["enable"].lower() == "false":
				continue
			ip = swichList[swichId]["ip"]
			port = swichList[swichId]["port"]
			type = int(swichList[swichId]["type"]) if "type" in swichList[swichId] else 1
			mapId = swichList[swichId]["mapId"]
			point1 = swichList[swichId]["point1"]
			point2 = swichList[swichId]["point2"]
			swich = swichInfo(swichId, ip, port, type, mapId, point1, point2)
			ret[swichId] = swich
		return ret

def removeDoor(swichId):
	global g_swichList
	if swichId in g_swichList:
		del g_swichList[swichId]

@utility.init()	
@lockImp.lock(g_lock)
def getDoorList():
	global g_swichList  
	if g_swichList is None: 
		g_swichList = _loadDoorList()
	return g_swichList


class swichInfo:
	def __init__(self, swichId, ip, port, type, mapId, point1, point2):
		self.swichId = swichId
		self.ip = ip
		self.port = port
		self.type = type
		self.map = mapId
		self.point1 = point1
		self.point2 = point2
		self._isLock = False

	def isAvailable(self):
		if self.isLock():
			return "locked"
		return ""


	@lockImp.lock(g_lock)
	def lock(self):
		if self._isLock:
			raise Exception(self.swichId + "上锁失败" )
		log.debug("lock: ", self.swichId)
		self._isLock = True

	@lockImp.lock(g_lock)
	def unlock(self):
		self._isLock = False
		log.debug("unlock:", self.swichId)

	@lockImp.lock(g_lock)
	def isLock(self):
		return self._isLock



	def open(self):
		if self.type == 1: # 海联科
			switchControl.setSwitch(self.ip,self.port,0,isOpen=True)
		elif self.type == 2: # 安信可
			doorControl.open(self.ip)
		elif self.type == 3:
			doorControlQLZ.open(self.ip, self.port)

	def close(self):
		if self.type == 1: # 海联科
			switchControl.setSwitch(self.ip, self.port, 0, isOpen=False)
		elif self.type == 2: # 安信可
			doorControl.close(self.ip)
		elif self.type == 3:
			doorControlQLZ.close(self.ip, self.port)

################ test ##################
def setTimer():
	import switchControl2
	doorList = getDoorList()
	for k in doorList:
		d = doorList[k]
		d.ip = "192.168.3.143"
		t = switchControl2.getTimer(d.ip,2)
		openTime= t["open"]
		switchControl2.removeTimer(d.ip,2,openTime)
		t = ["3:30","7:50","12:10","17:10","21:00"]
		switchControl2.setTimer(d.ip,2,t)
		return
	
if __name__ == '__main__':
	setTimer()