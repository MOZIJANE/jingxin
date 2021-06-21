# coding: utf-8
# author: linxiao
# date: 2019-12-12
# desc: modbus 接口

import sys
import os
import serial
import modbus_tk.defines as mdef
import modbus_tk.modbus_rtu as mrtu
import modbus_tk.modbus_tcp as mtcp
import threading
import time

BLOCK_LEN = 16

if __name__ == '__main__':
	currentPath = os.path.dirname(__file__)
	if currentPath != "":
		os.chdir(currentPath)

import log


class baseMaster(object):
	def __init__(self, slaveId, name):
		self.name = name
		self.__salveId = slaveId
		self.master = None
		self.__readFcode = (mdef.READ_COILS, mdef.READ_DISCRETE_INPUTS, mdef.READ_HOLDING_REGISTERS, \
		                    mdef.READ_INPUT_REGISTERS)
		self.__writeFcode = (mdef.WRITE_SINGLE_COIL, mdef.WRITE_SINGLE_REGISTER, mdef.WRITE_MULTIPLE_COILS, \
		                     mdef.WRITE_MULTIPLE_REGISTERS)

	def __execute(self, fcode, start, num=0, value=0):
		try:
			data = self.master.execute(self.__salveId, fcode, start, quantity_of_x=num, output_value=value)
			return data
		except Exception as e:
			log.exception("[modbusApi: %s] execute fcode=%d, addr=%d exception: " % (self.name, fcode, start), e)
			raise

	def read(self, fcode, start, num=0):
		if fcode not in self.__readFcode:
			log.warning("[modbusApi: %s] read failed! invalid fcode=%d." % (self.name, fcode))
			return
		return self.__execute(fcode, start, num)

	def write(self, fcode, start, value, num=0):
		if fcode not in self.__writeFcode:
			log.warning("[modbusApi: %s] write failed! invalid fcode=%d." % (self.name, fcode))
			return
		return self.__execute(fcode, start, num, value)

	def readException(self):
		return self.__execute(mdef.READ_EXCEPTION_STATUS, 0)

	def close(self):
		self.master.close()

	def open(self):
		self.master.open()


# 设备端是从站
class rtuSlave(baseMaster):
	def __init__(self, slaveId, port, baud, stopBits=1, byteSize=8, parity="N"):
		super(rtuSlave, self).__init__(slaveId, port)
		ser = serial.Serial()
		ser.baudrate = baud
		ser.port = port
		ser.bytesize = byteSize
		ser.stopbits = stopBits
		ser.parity = parity
		ser.open()
		self.master = mrtu.RtuMaster(ser)
		self.master.set_timeout(3)
		self.master.set_verbose(True)


# 设备端是服务器
class tcpMaster(baseMaster):
	def __init__(self, slaveId, host, port=502, timeout=5.0):
		super(tcpMaster, self).__init__(slaveId, host)
		self.master = mtcp.TcpMaster(host, port, timeout)


registerA = set()
registerB = set()


class tcpServer:
	def __init__(self, host, port=502, timeout=5.0):
		self.server = mtcp.TcpServer(address=host, timeout_in_sec=timeout, port=port)
		self.slave_1 = None
		self.slave_2 = None

	def conn(self):
		self.server.start()
		self.slave_1 = self.server.add_slave(1)
		self.slave_2 = self.server.add_slave(2)
		# 创建寄存器，寄存器起始地址为0，寄存器个数为32
		self.slave_1.add_block('block1', mdef.HOLDING_REGISTERS, 0, BLOCK_LEN)

		self.slave_1.add_block('block2', mdef.HOLDING_REGISTERS, BLOCK_LEN, BLOCK_LEN)

		self.clearValue()

		aa = self.getValue()
		print(aa)

	def getValue(self):
		global registerB
		global registerA
		registerA = self.slave_1.get_values('block1', 0, 16)
		registerB = self.slave_1.get_values('block2', 16, 16)

		return (registerA, registerB)

	def setValue(self, addr, values):
		self.slave_1.set_values("block1", address=addr, values=values)
		self.getValue()

	def clearValue(self):
		self.slave_1.set_values('block1', 0, 16 * [0])

		self.slave_1.set_values('block2', 16, 16 * [0])

	def end(self):
		self.server.stop()


# ========================================== unit test ==========================================
def test_rtu():
	# 需要建立虚拟串口COM5和COM6,启动ModbusSlave.exe监听COM6,并且function选coils
	rtuObj = rtuSlave(0x01, 'COM5', 9600)
	data = rtuObj.read(1, 1, 16)
	print(data)


def test_tcp():
	# 需要启动ModbusSlave.exe监听TCP,并且function选coils
	tcpObj = tcpMaster(0x01, '127.0.0.1', 502)
	data = tcpObj.read(3, 0, 10)
	print(data)


tcpServ = None


def test_readRegister():
	global tcpServ
	while True:
		time.sleep(1)
		if tcpServ is None:
			continue
		tcpServ.getValue()
		print(registerA)
		print(registerB)

		# cnc上料成功
		if registerB[3] == 0:
			print('cnc上料成功')
			tcpServ.setValue(5, 0)


def test_setRegister():
	global tcpServ
	time.sleep(5)
	tcpServ.setValue(11, 12)
	tcpServ.setValue(7, 0)

	# cnc上料
	tcpServ.setValue(3, 0)


def test_tcpServer():
	global tcpServ
	tcpServ = tcpServer('127.0.0.1', 502)
	tcpServ.conn()


if __name__ == '__main__':
	# test_rtu()
	# test_tcp()
	t1 = threading.Thread(target=test_setRegister)
	t1.start()
	t = threading.Thread(target=test_readRegister)
	t.start()
	test_tcpServer()
	pass
