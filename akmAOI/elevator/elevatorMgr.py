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
import elevator.elevatorControl as elevatorControl
import local
import modbusapi
import modbus_tk.defines as mdef

# 参数: elevatorId
#rebootEvent = enhance.event()

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

#
# class elevatorInfo:
# 	def __init__(self, elevatorId, ip, port, floor):
# 		self.elevatorId = elevatorId
# 		self.ip = ip
# 		self.port = port
# 		# self.map = mapId
# 		self.floor = floor
# 		self._isLock = False
#
# 	def isAvailable(self):
# 		if self.isLock():
# 			return "locked"
# 		return ""
#
#
# 	@lockImp.lock(g_lock)
# 	def lock(self):
# 		if self._isLock:
# 			raise Exception(self.elevatorId + "上锁失败" )
# 		log.debug("lock: ", self.elevatorId)
# 		self._isLock = True
#
# 	@lockImp.lock(g_lock)
# 	def unlock(self):
# 		self._isLock = False
# 		log.debug("unlock:", self.elevatorId)
#
# 	@lockImp.lock(g_lock)
# 	def isLock(self):
# 		return self._isLock
#
#
#
# 	def gofloor(self,floor):
# 		return elevatorControl.goFloor(self.ip,self.port,id=0,floor=floor)
#
# 	def status(self):
# 		return elevatorControl.getStatus(self.ip,self.port,id=0)
#
#
# 	def open(self):
# 		return elevatorControl.open(self.ip,port=self.port,id=0)
#
# 	def close(self):
# 		return elevatorControl.close(self.ip,port=self.port,id=0)



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
			elif floor == 6:
				floor = 64
			return self._writeStatus(FLOOR_TARGET, floor)
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
			self.master = modbusapi.tcpMaster(self.slave, self.ip,self.port)
			self.master.open()
			time.sleep(0.5)
		if length:
			s = self.master.write(mdef.WRITE_MULTIPLE_REGISTERS,addr, value, length)
			# log.info('*****',s)
		else:
			s = self.master.write(mdef.WRITE_SINGLE_REGISTER,addr,value)
		return s




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

