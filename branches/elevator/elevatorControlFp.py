import sys, os
import threading
import json
import setup

if __name__ == '__main__':
setup.setCurPath(__file__)
import utility
# import remoteio.remoteioControl as remoteioControl
import modbusapi
import log
import time
import modbus_tk.defines as mdef
import lock as lockImp
import local

D0 = 0
D1 = 1
D2 = 2
D3 = 3
D4 = 4
D5 = 5
D6 = 6
D7 = 7

D10 = 10  # 0 01/05 1 号 DO 值 读写
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

FLOOR_STATUS = D10
FLOOR_TARGET = D11
RUNING_STATUS = D12
ALARM_STATUS = D13
ONE_DOOR_STATUS = D14
SEC_DOOR_STATUS = D15
DOOR1_ACTIVE = D16
DOOR2_ACTIVE = D17
IS_OCCUPY = D18

slaverId = 1


def _status(tcpMaster, addr):
	result = None
	try:
		result = tcpMaster.read(mdef.READ_COILS, addr, 1)
		print('!!!!!!!!!已读取PLC，地址：{0}, 值{1}!!!!!!!!!!'.format(str(addr), str(result)))

	except Exception as e:
		print('!!!!!!!!!读取异常，地址：{0}, 值{1}!!!!!!!!!!'.format(str(addr), ''))

		tcpMaster.close()
		raise e

	return result[0]


def _cfg_status(tcpMaster, addr):
	result = None
	try:
		result = tcpMaster.read(mdef.READ_HOLDING_REGISTERS, addr, 1)
	except Exception as e:
		tcpMaster.close()
		raise e
	return result[0]


def _set(tcpMaster, addr, value=1):
	try:
		tcpMaster.write(mdef.WRITE_SINGLE_COIL, addr, value)
		print('!!!!!!!!!已写入PLC，地址：{0}, 值{1}!!!!!!!!!!'.format(str(addr), str(value)))
	except Exception as e:
		print('!!!!!!!!!写入异常，地址：{0}, 值{1}!!!!!!!!!!'.format(str(addr), str(value)))
		tcpMaster.close()
		raise e


def _cfg_set(tcpMaster, addr, value):
	try:
		tcpMaster.write(mdef.WRITE_SINGLE_REGISTER, addr, value)
	except Exception as e:
		tcpMaster.close()
		raise e


# 清除所有IO
def _clearIO(ip, port):
	modbusTcpServer = modbusapi.tcpMaster(slaverId, ip, port)
	_cfg_set(modbusTcpServer, D10, 0)
	_cfg_set(modbusTcpServer, D11, 0)
	_cfg_set(modbusTcpServer, D12, 0)
	_cfg_set(modbusTcpServer, D13, 0)
	_cfg_set(modbusTcpServer, D14, 0)
	_cfg_set(modbusTcpServer, D15, 0)
	_cfg_set(modbusTcpServer, D16, 0)
	_cfg_set(modbusTcpServer, D17, 0)
	modbusTcpServer.close()


def openDoor(ip, port, frontDoor=1, backDoor=0):
	modbusTcpServer = modbusapi.tcpMaster(slaverId, ip, port)
	floorStatus = _cfg_status(modbusTcpServer, FLOOR_STATUS)
	if floorStatus == 1:
		ret = _cfg_set(modbusTcpServer, DOOR1_ACTIVE, DOOR_OPEN_VALUE)
	elif floorStatus == 2:
		ret = _cfg_set(modbusTcpServer, DOOR2_ACTIVE, DOOR_OPEN_VALUE)
	modbusTcpServer.close()


def closeDoor(ip, port, frontDoor=1, backDoor=0):
	modbusTcpServer = modbusapi.tcpMaster(slaverId, ip, port)
	floorStatus = _cfg_status(modbusTcpServer, FLOOR_STATUS)
	if floorStatus == 1:
		ret = _cfg_set(modbusTcpServer, DOOR1_ACTIVE, DOOR_CLOSE_VALUE)
	elif floorStatus == 2:
		ret = _cfg_set(modbusTcpServer, DOOR2_ACTIVE, DOOR_CLOSE_VALUE)
	modbusTcpServer.close()

def cancel(ip, port):
	pass


def goFloor(ip, port, floor, frontDoor=1, backDoor=0):
	modbusTcpServer = modbusapi.tcpMaster(slaverId, ip, port)
	if floor == 1 or floor == 2:
		ret = _cfg_set(modbusTcpServer, FLOOR_TARGET, floor)
	modbusTcpServer.close()


def getStatus(ip, port):
	modbusTcpServer = modbusapi.tcpMaster(slaverId, ip, port)
	f1doorstatus = _cfg_status(modbusTcpServer, ONE_DOOR_STATUS)
	f2doorstatus = _cfg_status(modbusTcpServer, SEC_DOOR_STATUS)
	floorstatus = _cfg_status(modbusTcpServer, FLOOR_STATUS)
	alarmstatus = _cfg_status(modbusTcpServer, ALARM_STATUS)
	runingstatus = _cfg_status(modbusTcpServer, RUNING_STATUS)
	isOccupy = _cfg_status(modbusTcpServer, IS_OCCUPY)
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
		isOpening = True
	elif f1doorstatus == 0 and f2doorstatus == 0:
		isOpening = False
	ret_dict = {
		'isMaintain': 'normal',
		'isOpening': isOpening,
		'isClosing': not isOpening,
		'isFinishOpen': None,
		'inFloor': floorstatus,
		'isRunning': opstatus,
		'reachFloorStatus': None,
		'openDoorStatus': None,
		'cancelStatus': None,
		"gofloorRet": None,
		'downStatus': downstatus,
		'upStatus': upstatus,
		'alarm': alarmstatus,
		'isOccupy': isOccupy
	}
	modbusTcpServer.close()

	return ret_dict
