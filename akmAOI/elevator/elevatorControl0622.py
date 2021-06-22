# coding=utf-8

import lock as lockImp
import modbusapi
import log
import time
import modbus_tk.defines as mdef
import sys, os
import threading



D00 = 00  # 0 01/05 1 号 DO 值 读写
D10 = 10  # 0 01/05 1 号 DO 值 读写
D20 = 20  # 0 01/05 1 号 DO 值 读写
D16 = 16  # 6 01/05 7 号 DO 值 读写
D17 = 17  # 7 01/05 8 号 DO 值 读写


FLOOR_STATUS = D00
FLOOR_TARGET = D20
DOOR1_ACTIVE = D16
DOOR2_ACTIVE = D17

slaverId = 1
IO_LENTH = 8

DOOR_OPEN_VALUE = 1

DOOR_CLOSE_VALUE = 2

g_lock = lockImp.create("elevatorApi.g_lock")
g_elevatorList = None


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