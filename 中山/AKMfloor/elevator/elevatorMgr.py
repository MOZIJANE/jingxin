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
import time
import log
import enhance
import elevator.elevatorControlFuzhou as elevatorControl
import local

# 参数: elevatorId
#rebootEvent = enhance.event()

g_lock = lockImp.create("elevatorApi.g_lock")
g_elevatorList = None

def getElevator(elevatorId):
	return getElevatorList()[elevatorId]

# def getElevatorByMapId(mapId):
# 	elevatorList = getElevatorList()
# 	result = {}
# 	for switch in elevatorList:
# 		if elevatorList[switch].map==mapId:
# 			result[switch] = elevatorList[switch]
# 	return  result


g_cur_path = __file__


def _loadElevatorList():
	global g_cur_path

	proName = local.get("project","name")
	if utility.is_test():
		proName = "test"
	file = os.path.abspath(os.path.dirname(__file__)) +"/../agvCtrl/projects/"+proName+"/elevator.json"

	with open(file, 'r') as f:
		elevatorList = json.load(f)
		ret = {}
		for elevatorId in elevatorList:
			if elevatorList[elevatorId]["enable"].lower() == "false":
				continue
			ip = elevatorList[elevatorId]["ip"]
			port = elevatorList[elevatorId]["port"]
			# mapId = elevatorList[elevatorId]["mapId"]
			floor = elevatorList[elevatorId]["floor"]

			swich = elevatorInfo(elevatorId, ip, port, floor)
			ret[elevatorId] = swich
		return ret

def removeElevator(elevatorId):
	global g_elevatorList
	if elevatorId in g_elevatorList:
		del g_elevatorList[elevatorId]

@utility.init()
@lockImp.lock(g_lock)
def getElevatorList():
	global g_elevatorList
	if g_elevatorList is None:
		g_elevatorList = _loadElevatorList()
	return g_elevatorList


class elevatorInfo:
	def __init__(self, elevatorId, ip, port, floor):
		self.elevatorId = elevatorId
		self.ip = ip
		self.port = port
		# self.map = mapId
		self.floor = floor
		self._isLock = False

	def isAvailable(self):
		if self.isLock():
			return "locked"
		return ""


	@lockImp.lock(g_lock)
	def lock(self):
		if self._isLock:
			raise Exception(self.elevatorId + "上锁失败" )
		log.debug("lock: ", self.elevatorId)
		self._isLock = True

	@lockImp.lock(g_lock)
	def unlock(self):
		self._isLock = False
		log.debug("unlock:", self.elevatorId)

	@lockImp.lock(g_lock)
	def isLock(self):
		return self._isLock



	def gofloor(self,floor):
		return elevatorControl.goFloor(self.ip,self.port,id=0,floor=floor)

	def status(self):
		return elevatorControl.getStatus(self.ip,self.port,id=0)


	def open(self):
		return elevatorControl.open(self.ip,port=self.port,id=0)

	def close(self):
		return elevatorControl.close(self.ip,port=self.port,id=0)


############### unit test ###############
def test():
	import time
	e = getElevator("ELEVATOR01")
	for i in range(10):
		try:
			print(e.status())
			e.gofloor(2)
			while True:
				e.goFloor(2)
				s = e.status()
				print(s)
				if s["inFloor"] == 2:
					break
				time.sleep(4)
			print(e.status())
			e.open()
			time.sleep(10)
			e.close()
			time.sleep(5)
			print(e.status())
			e.gofloor(3)
			while True:
				e.goFloor(3)
				s = e.status()
				print(s)
				if s["inFloor"] == 2:
					break
				time.sleep(4)
			print(e.status())
			e.open()
			time.sleep(10)
			e.close()
		except Exception as xe:
			print("ELEVATOR01 error ",xe)

def test2():
	import time
	e = getElevator("ELEVATOR01")
	print(e.status())
	# time.sleep(3)
	# print(e.open())
	# time.sleep(3)
	# print(e.open())
	# time.sleep(3)
	# print(e.open())
	# time.sleep(3)
	# print(e.open())
	# time.sleep(6)
	# print(e.qclose())

	e.gofloor(4)

if __name__ == '__main__':
	test2()

