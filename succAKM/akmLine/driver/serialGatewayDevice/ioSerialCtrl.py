# coding=utf-8
import time
import threading
import setup

if __name__ == '__main__':
	setup.setCurPath(__file__)
import modbusapi
import modbus_tk.defines as mdef

tcpMaster = None
slaverId = 0x01
baud = 115200
port = 'COM1'


def reconnect():
	global tcpMaster
	tcpMaster.close()
	tcpMaster.open()


# 查询状态，并且更新开始位置
def _do_status(addr):
	global tcpMaster
	result = None
	try:
		result = tcpMaster.read(mdef.READ_COILS, addr, 1)[0]
	except:
		reconnect()
	return result


def _di_status(addr):
	global tcpMaster
	result = None
	try:
		result = tcpMaster.read(mdef.READ_DISCRETE_INPUTS, addr, 1)[0]
	except:
		reconnect()
	return result


def _do_set(addr, value=1):
	global tcpMaster
	try:
		tcpMaster.write(mdef.WRITE_SINGLE_COIL, addr, value)
	except:
		reconnect()


def run():
	global tcpMaster
	global port
	global baud
	global slaverId
	if tcpMaster is not None:
		return
	tcpMaster = modbusapi.rtuMaster(slaverId, port, baud)
	time.sleep(3)
	# jackIniti()


def end():
	global tcpMaster
	if tcpMaster is None:
		return
	tcpMaster.close()


def test_run():
	global tcpMaster
	if tcpMaster is not None:
		return
	tcpMaster = modbusapi.rtuMaster(slaverId, port, baud)
	while True:
		data = _di_status(0)
		print(data)
		time.sleep(0.1)


##################### unit test #####################
if __name__ == '__main__':
	test_run()
