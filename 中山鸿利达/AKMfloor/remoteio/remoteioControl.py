# coding=utf-8
# ycat			2018-8-2	  create
# seerAgv的API封装
import sys, os
import threading
import time
import setup

if __name__ == '__main__':
	setup.setCurPath(__file__)
import driver.serialGatewayDevice.ioModbusTcpCtrl as ioModbusTcpCtrl
import log
import lock

g_lock = threading.RLock()


@lock.lock(g_lock)
def setDO(ip, port, addr, value):
	addr = int(addr)
	port = int(port)
	try:
		if addr == 1:
			ioAddr = ioModbusTcpCtrl.D10
		elif addr == 2:
			ioAddr = ioModbusTcpCtrl.D11
		elif addr == 3:
			ioAddr = ioModbusTcpCtrl.D12
		elif addr == 4:
			ioAddr = ioModbusTcpCtrl.D13
		elif addr == 5:
			ioAddr = ioModbusTcpCtrl.D14
		elif addr == 6:
			ioAddr = ioModbusTcpCtrl.D15
		elif addr == 7:
			ioAddr = ioModbusTcpCtrl.D16
		elif addr == 8:
			ioAddr = ioModbusTcpCtrl.D17
		else:
			raise Exception("参数错误")

		ioModbusTcpCtrl.setValue(ip, port, ioAddr, value)
	except Exception as ex:
		log.debug(ex)
		raise Exception("网络连接错误")


@lock.lock(g_lock)
def setDOs(ip, port, value):
	port = int(port)
	try:
		l = list(map(lambda x: int(x), value.split(',')))
		ioModbusTcpCtrl.setValues(ip, port, ioModbusTcpCtrl.D10,l,ioModbusTcpCtrl.IO_LENTH)
	except Exception as ex:
		log.debug(ex)
		raise Exception("网络连接错误")


@lock.lock(g_lock)
def readDI(ip, port, addr):
	addr = int(addr)
	port = int(port)
	try:

		if addr == 1:
			ioAddr = ioModbusTcpCtrl.D0
		elif addr == 2:
			ioAddr = ioModbusTcpCtrl.D1
		elif addr == 3:
			ioAddr = ioModbusTcpCtrl.D2
		elif addr == 4:
			ioAddr = ioModbusTcpCtrl.D3
		elif addr == 5:
			ioAddr = ioModbusTcpCtrl.D4
		elif addr == 6:
			ioAddr = ioModbusTcpCtrl.D5
		elif addr == 7:
			ioAddr = ioModbusTcpCtrl.D6
		elif addr == 8:
			ioAddr = ioModbusTcpCtrl.D7
		else:
			raise Exception("参数错误")
		return ioModbusTcpCtrl.readValue(ip, port, ioAddr)
	except Exception as ex:
		log.debug(ex)
		raise Exception("网络连接错误")


@lock.lock(g_lock)
def readDIs(ip, port):
	port = int(port)
	try:
		return ioModbusTcpCtrl.readValues(ip, port, ioModbusTcpCtrl.D0, ioModbusTcpCtrl.IO_LENTH)
	except Exception as ex:
		log.debug(ex)
		raise Exception("网络连接错误")


@lock.lock(g_lock)
def readDO(ip, port, addr):
	addr = int(addr)
	port = int(port)
	try:
		if addr == 1:
			ioAddr = ioModbusTcpCtrl.D10
		elif addr == 2:
			ioAddr = ioModbusTcpCtrl.D11
		elif addr == 3:
			ioAddr = ioModbusTcpCtrl.D12
		elif addr == 4:
			ioAddr = ioModbusTcpCtrl.D13
		elif addr == 5:
			ioAddr = ioModbusTcpCtrl.D14
		elif addr == 6:
			ioAddr = ioModbusTcpCtrl.D15
		elif addr == 7:
			ioAddr = ioModbusTcpCtrl.D16
		elif addr == 8:
			ioAddr = ioModbusTcpCtrl.D17
		else:
			raise Exception("参数错误")
		return ioModbusTcpCtrl.readValue(ip, port, ioAddr)
	except Exception as ex:
		log.debug(ex)
		raise Exception("网络连接错误")


@lock.lock(g_lock)
def readDOs(ip, port):
	port = int(port)
	try:
		return ioModbusTcpCtrl.readValues(ip, port, ioModbusTcpCtrl.D10, ioModbusTcpCtrl.IO_LENTH)
	except Exception as ex:
		log.debug(ex)
		raise Exception("网络连接错误")


# ------------------for test--------------------

def test_setRemoteio():
	ip = '192.168.1.178'
	port = 8080
	while True:
		span = 0.5
		time.sleep(span)
		setRemoteio(ip, port, 0, isOpen=True)
		time.sleep(span)
		setRemoteio(ip, port, 2, isOpen=True)
		time.sleep(span)
		setRemoteio(ip, port, 0, isOpen=False)
		time.sleep(span)
		setRemoteio(ip, port, 2, isOpen=False)


if __name__ == '__main__':
	# import utility
	# utility.run_tests(__file__)
	test_setRemoteio()
