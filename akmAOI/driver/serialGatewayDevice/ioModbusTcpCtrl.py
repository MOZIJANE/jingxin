# coding=utf-8
import time
import threading
import setup

if __name__ == '__main__':
	setup.setCurPath(__file__)
import modbusapi
import modbus_tk.defines as mdef
import functools

tcpMaster = None

# 适用于zlan 8进8出io网关
IO_LENTH = 8
IS_USING_COILS = True


D0 = 0x0000
D1 = 0x0001
D2 = 0x0002
D3 = 0x0003
D4 = 0x0004
D5 = 0x0005
D6 = 0x0006
D7 = 0x0007

D10 = 0x0010  # 0 01/05 1 号 DO 值 读写
D11 = 0x0011  # 1 01/05 2 号 DO 值 读写
D12 = 0x0012  # 2 01/05 3 号 DO 值 读写
D13 = 0x0013  # 3 01/05 4 号 DO 值 读写
D14 = 0x0014  # 4 01/05 5 号 DO 值 读写
D15 = 0x0015  # 5 01/05 6 号 DO 值 读写
D16 = 0x0016  # 6 01/05 7 号 DO 值 读写
D17 = 0x0017  # 7 01/05 8 号 DO 值 读写

slaverId = 1


def reconnect():
	global tcpMaster
	tcpMaster.close()
	tcpMaster.open()


# 查询状态，并且更新开始位置
def _status(addr):
	global tcpMaster
	result = None
	try:
		result = tcpMaster.read(mdef.READ_COILS, addr, 1)
	except:
		reconnect()
	return result[0]


# 查询状态，并且更新开始位置
def _statusList(addr, len):
	global tcpMaster
	result = None
	try:
		result = tcpMaster.read(mdef.READ_COILS, addr, len)
	except:
		reconnect()
	return result


def _cfg_status(addr):
	global tcpMaster
	result = None
	try:
		result = tcpMaster.read(mdef.READ_HOLDING_REGISTERS, addr, 1)
	except:
		reconnect()
	return result[0]


def _cfg_statusList(addr, len):
	global tcpMaster
	result = None
	try:
		result = tcpMaster.read(mdef.READ_HOLDING_REGISTERS, addr, len)
	except:
		reconnect()
	return result


def _set(addr, value=1):
	global tcpMaster
	try:
		tcpMaster.write(mdef.WRITE_SINGLE_COIL, addr, value)
	except:
		reconnect()


def _setList(addr, value, len):
	global tcpMaster
	try:
		tcpMaster.write(mdef.WRITE_MULTIPLE_COILS, addr, value, len)
	except:
		reconnect()


def _cfg_set(addr, value):
	global tcpMaster
	try:
		tcpMaster.write(mdef.WRITE_SINGLE_REGISTER, addr, value)
	except:
		reconnect()


def _cfg_setList(addr, value, len):
	global tcpMaster
	try:
		tcpMaster.write(mdef.WRITE_MULTIPLE_REGISTERS, addr, value, len)
	except:
		reconnect()


def run(ip, port):
	global tcpMaster
	global slaverId
	tcpMaster = modbusapi.tcpMaster(slaverId, ip)
	time.sleep(0.5)


def end():
	if tcpMaster is not None:
		tcpMaster.close()


def setValue(ip, port, addr, value):
	run(ip, port)
	if IS_USING_COILS:
		_set(addr, value)
	else:
		_cfg_set(addr, value)
	end()


def setValues(ip, port, addr, value, len):
	run(ip, port)
	if IS_USING_COILS:
		_setList(addr, value, len)
	else:
		_cfg_setList(addr, value, len)
	end()


def readValue(ip, port, addr):
	run(ip, port)
	if IS_USING_COILS:
		currentStatus = _status(addr)
	else:
		currentStatus = _cfg_status(addr)
	end()
	return currentStatus


def readValues(ip, port, addr, len):
	run(ip, port)
	if IS_USING_COILS:
		currentStatus = _statusList(addr, len)
	else:
		currentStatus = _cfg_statusList(addr, len)
	end()
	print('------------',currentStatus)
	return currentStatus


if __name__ == '__main__':
	pass
