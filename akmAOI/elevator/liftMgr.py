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
import local


import modbusapi
import log
import time
import modbus_tk.defines as mdef
import lock as lockImp
import local
# from elevator import elevatorControl0622 as elevatorInfo

D0 = 0
D1 = 1
D2 = 2
D3 = 3
D4 = 4
D5 = 5
D6 = 6
D7 = 7

# D10 = 10  # 0 01/05 1 号 DO 值 读写
D00 = 00  # 0 01/05 1 号 DO 值 读写
D10 = 10  # 0 01/05 1 号 DO 值 读写
D20 = 20  # 0 01/05 1 号 DO 值 读写
D11 = 11  # 1 01/05 2 号 DO 值 读写
D12 = 12  # 2 01/05 3 号 DO 值 读写
D13 = 13  # 3 01/05 4 号 DO 值 读写
D14 = 14  # 4 01/05 5 号 DO 值 读写
D15 = 15  # 5 01/05 6 号 DO 值 读写
D16 = 16  # 6 01/05 7 号 DO 值 读写
D17 = 17  # 7 01/05 8 号 DO 值 读写
D18 = 18  # 7 01/05 8 号 DO 值 读写

IO_LENTH = 8

DOOR_OPEN_VALUE = 1

DOOR_CLOSE_VALUE = 2

FLOOR_STATUS = D00
FLOOR_TARGET = D20
RUNING_STATUS = D12
ALARM_STATUS = D13
ONE_DOOR_STATUS = D14
SEC_DOOR_STATUS = D15
DOOR1_ACTIVE = D16
DOOR2_ACTIVE = D17
IS_OCCUPY = D18

slaverId = 1





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


# g_cur_path = __file__


# def _loadElevatorList():
	# global g_cur_path
	# proName = local.get("project","name")
	# if utility.is_test():
	# 	proName = "test"
	# file = os.path.abspath(os.path.dirname(__file__)) +"/../agvCtrl/projects/"+proName+"/elevator.json"
	# file = os.path.abspath(os.path.dirname(__file__)) + "/elevator.json"
	# print("++++++file",file)
	# with open(file, 'r') as f:
	# 	elevatorList = json.load(f)
	# 	ret = {}
	# 	for elevatorId in elevatorList:
	# 		if elevatorList[elevatorId]["enable"].lower() == "false":
	# 			continue
	# 		ip = elevatorList[elevatorId]["ip"]
	# 		port = elevatorList[elevatorId]["port"]
	# 		# mapId = elevatorList[elevatorId]["mapId"]
	# 		floor = elevatorList[elevatorId]["floor"]

		# swich = elevatorInfo(elevatorId = "ELEVATOR01", ip = "172.20.13.94", port = 6000)
		# ret["ELEVATOR01"] = swich
		# return ret




def _loadElevatorList():
	# global g_cur_path
	file = os.path.abspath(os.path.dirname(__file__)) + "/elevator.json"
	# file = os.path.abspath(os.path.dirname(__file__)) + "/../agvCtrl/projects/" + proName + "/elevator.json"
	with open(file,'r') as f:
		elevatorList = json.load(f)
		ret = {}
		for elevatorId in elevatorList:
			if elevatorList[elevatorId]["enable"].lower() == "false":
				continue
			ip = elevatorList[elevatorId]["ip"]
			port = elevatorList[elevatorId]["port"]
			swich = elevatorInfo(elevatorId, ip, port)
			# log.info(swich.__dict__)
			ret[elevatorId] = swich
		return ret




#
# def removeElevator(elevatorId):
# 	global g_elevatorList
# 	if elevatorId in g_elevatorList:
# 		del g_elevatorList[elevatorId]

def getElevatorList():
	global g_elevatorList
	if g_elevatorList is None:
		g_elevatorList = _loadElevatorList()
	return g_elevatorList


def openDoor(elevatorId = "ELEVATOR01"):
	global g_elevatorList
	lift = getElevator(elevatorId)
	return lift.open()


def closeDoor(elevatorId = "ELEVATOR01"):
	global g_elevatorList
	lift = getElevator(elevatorId)
	return lift.close()

def goFloor(floor,elevatorId = None):
	global g_elevatorList
	# log.info(floor)
	lift = getElevator(elevatorId)
	return lift.gofloor(floor)


def getStatus(elevatorId = None):
	global g_elevatorList
	lift = getElevator(elevatorId)
	return lift.status()

def isLock(elevatorId = "ELEVATOR01"):
	global g_elevatorList
	lift = getElevator(elevatorId)
	return lift.isLock()


def Lock(elevatorId = "ELEVATOR01"):
	global g_elevatorList
	lift = getElevator(elevatorId)
	lift.lock()

def UnLock(elevatorId = "ELEVATOR01"):
	global g_elevatorList
	lift = getElevator(elevatorId)
	lift.unlock()


class elevatorInfo:
	def __init__(self, elevatorId, ip, port):
		self.elevatorId = elevatorId
		self.slave = 1
		self.ip = ip
		self.port = port
		# self.map = mapId
		self.floor = 1
		self._isLock = False
		self.m_lock = threading.RLock()
		self.master = modbusapi.tcpMaster(self.slave, self.ip,self.port)

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
		try:
			if floor == 1:
				floor = 1
			elif floor == 2:
				floor = 2
			elif floor == 3:
				floor =8
			elif floor ==  4:
				floor = 16   #电梯第四层实际为物理层第五层
			elif floor == 5:
				floor = 32
			# elif floor == 6:
			# 	floor = 64
			s = self._writeStatus(FLOOR_TARGET, floor)
			log.info('shit is s')
			log.info(s)
			log.info('-----------')
			return s
			log.info("go floor %s"%floor)
		except Exception as ex:
			self.master.close()
			self.master = None
			log.exception("readDOList fail")
			raise ex


	def status(self):
		try:
			# log.info("lift statuslist:")
			# log.info(FLOOR_STATUS)
			statuslist = self._readStatus(FLOOR_STATUS,10)
			log.info('******',statuslist)
			f1doorstatus = statuslist[4]
			f2doorstatus = statuslist[5]
			floorstatus = statuslist[0]
			alarmstatus = statuslist[3]
			runingstatus = statuslist[2]
			isOccupy = statuslist[8]

			upstatus = False
			downstatus = False
			opstatus = False
			if runingstatus == 0:
				upstatus = False
				opstatus = True
				downstatus = True
			elif runingstatus == 1:
				upstatus = True
				opstatus = True
				downstatus = False
			elif runingstatus == 2:
				pass

			isOpening = False
			if f1doorstatus == 1 or f2doorstatus == 1:
				isFinishOpen = True
			elif f1doorstatus == 0 and f2doorstatus == 0:
				isFinishOpen = False
			ret_dict = {
				'isMaintain': 'normal',
				'isOpening': None,
				'isClosing': None,
				'isFinishOpen': isFinishOpen,
				'inFloor': floorstatus,
				'isRunning': opstatus,
				'reachFloorStatus': None,
				'openDoorStatus': None,
				'cancelStatus': None,
				"gofloorRet": None,
				'downStatus': downstatus,
				'upStatus': upstatus,
				'alarm': alarmstatus,
				'isOccupy': isOccupy      #占有，电梯里面有物料
			}
			return ret_dict
		except Exception as ex:
			self.master.close()
			self.master = None
			log.info("statuslist getstatus ELEVATOR01 fail")
			log.exception("getstatus ELEVATOR01 fail")
			raise

	def open(self):
		try:
			floorStatus = self._readStatus(FLOOR_STATUS)
			if floorStatus == 1:
				ret = self._writeStatus( DOOR1_ACTIVE, DOOR_OPEN_VALUE)
			elif floorStatus == 2:
				ret = self._writeStatus(DOOR2_ACTIVE, DOOR_OPEN_VALUE)
			log.info("open door %s"%floorStatus)
		except Exception as ex:
			self.master.close()
			self.master = None
			log.exception("open ELEVATOR01 fail")
			raise

	def close(self):
		try:
			floorStatus = self._readStatus(FLOOR_STATUS)
			if floorStatus == 1:
				ret = self._writeStatus( DOOR1_ACTIVE, DOOR_CLOSE_VALUE)
			elif floorStatus == 2:
				ret = self._writeStatus(DOOR2_ACTIVE, DOOR_CLOSE_VALUE)
			log.info("close door %s" % floorStatus)
		except Exception as ex:
			self.master.close()
			self.master = None
			log.exception("close ELEVATOR01 fail")
			raise



	@lockImp.lock(None)
	def _read(self,addr,length=None):
		if self.master is None:
			self.master = modbusapi.tcpMaster(self.slave, self.ip,self.port)
			self.master.open()
			time.sleep(0.5)
		if length:
			s = self.master.read(mdef.READ_COILS,addr, length)
		else:
			s = self.master.read(mdef.READ_COILS,addr,1)[0]
		return s


	@lockImp.lock(None)
	def _readStatus(self, addr, length=None):
		if self.master is None:
			self.master = modbusapi.tcpMaster(self.slave, self.ip,self.port)
			self.master.open()
			time.sleep(0.5)
		if length:
			s = self.master.read(mdef.READ_HOLDING_REGISTERS, addr, length)
		else:
			s = self.master.read(mdef.READ_HOLDING_REGISTERS, addr, 2)[0]
		return s

	@lockImp.lock(None)
	def _write(self,addr,value,length=None):
		if self.master is None:
			self.master = modbusapi.tcpMaster(self.slave, self.ip,self.port)
			self.master.open()
			time.sleep(0.5)
		if length:
			s = self.master.write(mdef.WRITE_MULTIPLE_COILS,addr, value, length)
		else:
			s = self.master.write(mdef.WRITE_SINGLE_COIL,addr,value)
		return s

	@lockImp.lock(None)
	def _writeStatus(self,addr,value,length=None):
		if self.master is None:
			log.info('is none')
			self.master = modbusapi.tcpMaster(self.slave, self.ip,self.port)
			self.master.open()
			time.sleep(0.5)
		if length:
			log.info('is length')
			s = self.master.write(mdef.WRITE_MULTIPLE_REGISTERS,addr, value, length)
			# log.info('*****',s)
		else:
			log.info('is else')
			s = self.master.write(mdef.WRITE_SINGLE_REGISTER,addr,value)
		return s


	# def parseResult(result):
	# 	# log.info("result:",result)
	# 	ret = bytes(result.getBuf(result._len))
	# 	reachFloorStatus = None
	# 	isFinishOpen = None
	# 	inFloor = None
	# 	openDoorStatus = None
	# 	cancelStatus = None
	# 	reachTargetFloor = None
	# 	isRunning = None
	# 	downStatus = 0
	# 	upStatus = 0
	#
	# 	ttt = {
	# 		'isMaintain': 'normal',
	# 		'isOpening': 0,
	# 		'isClosing': 0,
	# 		'isFinishOpen': None,
	# 		'inFloor': None,
	# 		'isRunning': None,
	# 		'reachFloorStatus': None,
	# 		'openDoorStatus': None,
	# 		'cancelStatus': None,
	# 		"reachTargetFloor": None,
	# 		'downStatus': None,
	# 		'upStatus': None
	# 	}
	# 	if len(ret) < 6:
	# 		return ttt
	# 	if ret[5] == RET_STATUS:
	#
	# 		tempstr = bin(ret[6])
	# 		inFloor = int(ret[7])
	# 		print("++++++return inFloor:", inFloor)
	# 		if inFloor == 3:
	# 			inFloor = 9
	# 		if inFloor > 2:
	# 			inFloor = inFloor - 1
	# 		print("++++++inFloor:", inFloor)
	# 		downStatus = int(tempstr[7])  # 1:down 0 :unavailable
	# 		upStatus = int(tempstr[8])  # 1:up   0 :unavailable
	# 		if int(tempstr[4]) == 0:
	# 			isFinishOpen = 1
	#
	#
	# 	elif ret[5] == RET_GOFLOOR:
	# 		pass
	# 	elif ret[5] == RET_OPENDOOR:
	# 		pass
	# 	elif ret[5] == RET_CLOSEDOOR:
	# 		pass
	# 	elif ret[5] == RET_CANCEL:
	# 		pass
	# 	ret_dict = {
	# 		'isMaintain': 'normal',
	# 		'isOpening': 0,
	# 		'isClosing': 0,
	# 		'isFinishOpen': isFinishOpen,
	# 		'inFloor': inFloor,
	# 		'isRunning': isRunning,
	# 		'reachFloorStatus': reachFloorStatus,
	# 		'openDoorStatus': openDoorStatus,
	# 		'cancelStatus': cancelStatus,
	# 		"reachTargetFloor": reachTargetFloor,
	# 		'downStatus': downStatus,
	# 		'upStatus': upStatus
	# 	}
	# 	return ret_dict

# getElevatorList()


############### unit test ###############
def test():
	for i in range(10):
		try:
			print(getStatus(elevatorId="ELEVATOR01"))
			goFloor(2, elevatorId="ELEVATOR01")
			while True:
				goFloor(2, elevatorId="ELEVATOR01")
				s =	getStatus(elevatorId="ELEVATOR01")
				print(s)
				if s["inFloor"] == 2:
					break
				time.sleep(4)
			print(getStatus(elevatorId = "ELEVATOR01"))
			openDoor(elevatorId="ELEVATOR01")
			time.sleep(10)
			print(getStatus(elevatorId = "ELEVATOR01"))
			closeDoor(elevatorId="ELEVATOR01")
			time.sleep(10)
			print(getStatus(elevatorId = "ELEVATOR01"))


			print(getStatus(elevatorId="ELEVATOR01"))
			goFloor(1, elevatorId="ELEVATOR01")
			while True:
				goFloor(1, elevatorId="ELEVATOR01")
				s =	getStatus(elevatorId="ELEVATOR01")
				print(s)
				if s["inFloor"] == 1:
					break
				time.sleep(4)
			print(getStatus(elevatorId = "ELEVATOR01"))
			openDoor(elevatorId="ELEVATOR01")
			time.sleep(10)
			print(getStatus(elevatorId = "ELEVATOR01"))
			closeDoor(elevatorId="ELEVATOR01")
			time.sleep(10)
			print(getStatus(elevatorId = "ELEVATOR01"))



		except Exception as xe:
			# raise e
			# print("e"*100)
			print("ELEVATOR01 error ",xe)



def test2():
	Lock(elevatorId="ELEVATOR01")
	# print("+++++++",isLock(elevatorId="ELEVATOR01"))
	# print('-------------')
	# print(getStatus(elevatorId="ELEVATOR01"))
	print(goFloor(5,elevatorId="ELEVATOR01"))
	# print('-------------')
	# closeDoor(elevatorId="ELEVATOR01")
	# openDoor(elevatorId="ELEVATOR01")

if __name__ == '__main__':
	test2()
