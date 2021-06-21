# coding=utf-8
# lzxs			2018-8-2	  create 
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
g_remoteioList = None
import alarm.aliveApi

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


D100 = 0x64
D101 = 0x65
D102 = 0x66
D103 = 0x67


D104 = 0x68
D105 = 0x69
D106 = 0x6A
D107 = 0x6B

M30 = 0x2040   #8256
M31 = 0x2041
M32 = 0x2042
M33 = 0x2043
M34 = 0x2044   #8256
M35 = 0x2045
M36 = 0x2046
M37 = 0x2047


IO_LENTH = 8
DO_LENTH = 2

def get(id):
	log.info(getList()[id])
	return getList()[id] 

def _loadRemoteioList(): 
	file = "/remoteio.json"
	with open(os.path.abspath(os.path.dirname(__file__)) + file, 'r') as f:
		remoteioList = json.load(f)
		ret = {}
		for remoteioId in remoteioList:
			if remoteioList[remoteioId]["enable"].lower() == "false":
				continue
			ip = remoteioList[remoteioId]["ip"]
			port = remoteioList[remoteioId]["port"] 
			remoteio = remoteioInfo(remoteioId, ip, port)
			ret[remoteioId] = remoteio
		return ret
 
def getList():
	global g_remoteioList  
	if g_remoteioList is None: 
		g_remoteioList = _loadRemoteioList()
	return g_remoteioList

def writeDO(id, index, value):
	remoteioInfo= get(id)
	remoteioInfo.writeDO(index,value)
	return {}

def writeStatusDO(id, index, value):
	remoteioInfo= get(id)
	remoteioInfo.writeStatusDO(index,value)
	return {}

def writeStatusD100(id, index, value):
	remoteioInfo= get(id)
	remoteioInfo.writeStatusD100(index,value)
	return {}

def writeStatusD104(id, index, value):
	remoteioInfo= get(id)
	remoteioInfo.writeStatusD104(index,value)
	return {}

def writeStatusDOList(id, values):
	remoteioInfo = get(id)
	remoteioInfo.writeStatusDOList(values)
	return {}
def writeStatusD100List(id, values):
	remoteioInfo = get(id)
	remoteioInfo.writeStatusD100List(values)
	return {}
def writeStatusD104List(id, values):
	remoteioInfo = get(id)
	remoteioInfo.writeStatusD104List(values)
	return {}

def writeDOList(id, values):
	remoteioInfo = get(id)
	remoteioInfo.writeDOList(values)
	return {}
	
def readDI(id, index):
	remoteioInfo = get(id)
	result=remoteioInfo.readDI(index)
	return {"status":result}


def readDO(id, index):
	remoteioInfo = get(id)
	result=remoteioInfo.readDO(index)
	return {"status":result}

def readStatusList(id):
	remoteioInfo = get(id)
	result=remoteioInfo.readStatusList()
	return {"status":result}

def readStatusListD100(id):
	remoteioInfo = get(id)
	result=remoteioInfo.readStatusListD100()
	return {"status":result}

def readStatusListD104(id):
	remoteioInfo = get(id)
	result=remoteioInfo.readStatusListD104()
	return {"status":result}


def readDIList(id):
	remoteioInfo = get(id)
	log.info('--------------------------------------')
	log.info(remoteioInfo)
	log.info('--------------------------------------')
	result=remoteioInfo.readDIList()
	return {"status":result}


def readDOList(id):
	remoteioInfo = get(id)
	result=remoteioInfo.readDOList()
	return {"status":result}
	
class remoteioInfo:
	def __init__(self, remoteioId, ip, port,slaverId=1):
		self.id = remoteioId
		self.ip = ip
		self.port = port 
		self.slaverId = 1
		self.m_lock = threading.RLock()
		self.master = modbusapi.tcpMaster(self.slaverId, self.ip)

	def writeStatusDO(self, index, value):
		try:
			ioAddr = getWoAddr(index)
			self._writeStatus(ioAddr, value)
		except Exception as ex:
			self.master.close()
			self.master = None
			log.exception("%s writeDO fail" % self.id, ex)
			raise

	def writeStatusD100(self, index, value):
		try:
			ioAddr = getD100Addr(index)
			self._writeStatus(ioAddr, value)
		except Exception as ex:
			self.master.close()
			self.master = None
			log.exception("%s writeDO fail" % self.id, ex)
			raise

	def writeStatusD104(self, index, value):
		try:
			ioAddr = getD104Addr(index)
			self._writeStatus(ioAddr, value)
		except Exception as ex:
			self.master.close()
			self.master = None
			log.exception("%s writeDO fail" % self.id, ex)
			raise
		# DO操作
	def writeDO(self,index,value):
		try:
			ioAddr = getDoAddr(index)
			self._write(ioAddr, value)
		except Exception as ex:
			self.master.close()
			self.master = None
			log.exception("%s writeDO fail"%self.id,ex)
			raise 
		
	def writeStatusDOList(self,value):
		try:
			l = list(map(lambda x: int(x), value.split(',')))
			self._writeStatus(D0,l,DO_LENTH)
		except Exception as ex:
			self.master.close()
			self.master = None
			log.exception("%s writeDOList fail"%self.id,ex)
			raise
	def writeStatusD10OList(self,value):
		try:
			l = list(map(lambda x: int(x), value.split(',')))
			self._writeStatus(D102,l,DO_LENTH)
		except Exception as ex:
			self.master.close()
			self.master = None
			log.exception("%s writeDOList fail"%self.id,ex)
			raise
	def writeStatusD104List(self,value):
		try:
			l = list(map(lambda x: int(x), value.split(',')))
			self._writeStatus(D106,l,DO_LENTH)
		except Exception as ex:
			self.master.close()
			self.master = None
			log.exception("%s writeDOList fail"%self.id,ex)
			raise

	def writeDOList(self,value):
		try:
			l = list(map(lambda x: int(x), value.split(',')))
			self._write(M32,l,DO_LENTH)
			self._write(M36,l,DO_LENTH)
		except Exception as ex:
			self.master.close()
			self.master = None
			log.exception("%s writeDOList fail"%self.id,ex)
			raise


	def readDI(self,index):
		try:
			ioAddr = getDiAddr(index)
			return self._read(ioAddr)
		except Exception as ex:
			self.master.close()
			self.master = None
			log.exception("%s readDI fail"%self.id,ex)
			raise 

	def readDOList(self):
		try:
			return self._read(M30, IO_LENTH)
		except Exception as ex:
			self.master.close()
			self.master = None
			log.exception("%s readDIList fail"%self.id,ex)
			raise
	
	# DI操作
	def readDO(self,index):
		try:
			ioAddr = getDoAddr(index)
			return self._read(ioAddr)
		except Exception as ex:
			self.master.close()
			self.master = None
			log.exception("%s readDO fail"%self.id,ex)
			raise


	def readStatusList(self):
		try:
			return self._readStatus(D0, IO_LENTH)
		except Exception as ex:
			self.master.close()
			self.master = None
			log.exception("%s readDOList fail"%self.id,ex)
			raise
	def readStatusListD100(self):
		try:
			return self._readStatus(D100, IO_LENTH)
		except Exception as ex:
			self.master.close()
			self.master = None
			log.exception("%s readDOList fail"%self.id,ex)
			raise

	def readStatusListD104(self):
		try:
			return self._readStatus(D104, IO_LENTH)
		except Exception as ex:
			self.master.close()
			self.master = None
			log.exception("%s readDOList fail"%self.id,ex)
			raise

	@lockImp.lock(None)
	def _read(self,addr,length=None):
		if self.master is None:
			self.master = modbusapi.tcpMaster(self.slaverId, self.ip)
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
			self.master = modbusapi.tcpMaster(self.slaverId, self.ip)
			self.master.open()
			time.sleep(0.5)
		if length:
			s = self.master.read(mdef.READ_HOLDING_REGISTERS, addr, length)
		else:
			s = self.master.read(mdef.READ_HOLDING_REGISTERS, addr, 1)[0]
		return s

	@lockImp.lock(None)
	def _write(self,addr,value,length=None):
		if self.master is None:
			self.master = modbusapi.tcpMaster(self.slaverId, self.ip)
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
			self.master = modbusapi.tcpMaster(self.slaverId, self.ip)
			self.master.open()
			time.sleep(0.5)
		if length:
			s = self.master.write(mdef.WRITE_MULTIPLE_REGISTERS,addr, value, length)
		else:
			s = self.master.write(mdef.WRITE_SINGLE_REGISTER,addr,value)
		return s

def getDiAddr(addr):
	if addr == 1:
		ioAddr = D10
	elif addr == 2:
		ioAddr = D11
	elif addr == 3:
		ioAddr = D12
	elif addr == 4:
		ioAddr = D13
	elif addr == 5:
		ioAddr = D14
	elif addr == 6:
		ioAddr = D15
	elif addr == 7:
		ioAddr = D16
	elif addr == 8:
		ioAddr = D17
	else:
		raise Exception("参数错误")
	return ioAddr
	
def getDoAddr(addr):
	if addr == 1:
		ioAddr = M30
	elif addr == 2:
		ioAddr = M31
	elif addr == 3:
		ioAddr = M32
	elif addr == 4:
		ioAddr = M33
	elif addr == 5:
		ioAddr = M34
	elif addr == 6:
		ioAddr = M35
	elif addr == 7:
		ioAddr = M36
	elif addr == 8:
		ioAddr = M37
	else:
		raise Exception("参数错误")
	return ioAddr


def getWoAddr(addr):
	if addr == 1:
		ioAddr = W0
	elif addr == 2:
		ioAddr = W1
	elif addr == 3:
		ioAddr = W2
	elif addr == 4:
		ioAddr = W3
	elif addr == 5:
		ioAddr = W4
	elif addr == 6:
		ioAddr = W5
	elif addr == 7:
		ioAddr = W6
	elif addr == 8:
		ioAddr = W7
	else:
		raise Exception("参数错误")
	return ioAddr



def getD100Addr(addr):
	if addr == 1:
		ioAddr = D100
	elif addr == 2:
		ioAddr = D101
	elif addr == 3:
		ioAddr = D102
	elif addr == 4:
		ioAddr = D103
	else:
		raise Exception("参数错误")
	return ioAddr

def getD104Addr(addr):
	if addr == 1:
		ioAddr = D104
	elif addr == 2:
		ioAddr = D105
	elif addr == 3:
		ioAddr = D106
	elif addr == 4:
		ioAddr = D107
	else:
		raise Exception("参数错误")
	return ioAddr


def remoteioCheck():
	import shell
	checkCount = 0
	g_laststatus = {}
	remoteiolistalarm = {}
	remoteiolist = getList()
	if not remoteiolistalarm:
		for id in remoteiolist:
			info = get(id)
			g_laststatus.update({id:True})
			larm =alarm.aliveApi.aliveObj(moid=id, typeId=39998, desc="远程控制IO离线异常", timeoutSecond=120, domain="agv")
			remoteiolistalarm.update({id:larm})
			#log.info("++++++++remoteiolistalarm",larm, id,info.ip)
	while not utility.is_exited():
		try:
			for id in remoteiolist:
				info = get(id)
				if shell.ping(info.ip, showLog=False):
					remoteiolistalarm[id].check()
		except Exception as ex:
			log.debug(ex)
			raise Exception("远程控制IOping包异常")




checkThread = threading.Thread(target=remoteioCheck,name="remoteio.ping")
checkThread.start()
	

if __name__ == '__main__':
	utility.run_tests()
