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

IO_LENTH = 8

def get(id):
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


def readDIList(id):
	remoteioInfo = get(id)
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
		
	def writeDOList(self,value):
		try:
			l = list(map(lambda x: int(x), value.split(',')))
			self._write(D10,l,IO_LENTH)
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

	def readDIList(self):
		try:
			return self._read(D0, IO_LENTH)
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
	
	def readDOList(self):
		try:
			return self._read(D10, IO_LENTH)
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
            larm =alarm.aliveApi.aliveObj(moid=id, typeId=39998, desc="远程控制IO离线异常", timeoutSecond=60, domain="agv")
            remoteiolistalarm.update({id:larm})
            # log.info("++++++++remoteiolistalarm",larm, id,info.ip)

    while not utility.is_exited():
        for id in remoteiolist:
            info = get(id)
            if shell.ping(info.ip, showLog=False):
                remoteiolistalarm[id].check()
    time.sleep(5)

#
# checkThread = threading.Thread(target=remoteioCheck,name="remoteio.ping")
# checkThread.start()
	

if __name__ == '__main__':
	utility.run_tests()
