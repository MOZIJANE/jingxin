#coding=utf-8 
# ycat			2017-08-25	  create
import sys,os
import serial 
import threading

if __name__ == '__main__':
	p = os.path.dirname(__file__)
	if p != "":
		os.chdir(p)
if "../../" not in sys.path:
	sys.path.append("../../")	 
if "../../common" not in sys.path:
	sys.path.append("../../common")
	
import buffer
import log
import utility
import random as rand
import time
import driver.solder.solderCfg
import qtutility

g_comm = None
g_lastSetTemp = 400

def waitTemp(timeout):
	if utility.is_test():
		return True
	global g_comm
	if g_comm is None:
		log.error("焊台连接失败")
		return False
	t = readSetTemp()
	start = utility.ticks() 
	t2 = 0
	while utility.ticks() - start < timeout:
		t2 = readTemp()
		if t2 is None:	
			log.error("焊台连接失败2")
			return False
		if abs(t2 - t) < 5:
			log.info("焊台等待温度成功,read=%d,set=%d"%(t2,t))
			return True
	log.error("焊台等待温度失败,read=%d,set=%d"%(t2,t))
	return False
	

def isConnected():
	global g_comm
	return g_comm is not None

def readCommThread(): 
	global g_existed,g_comm
	while not g_existed:
		if g_comm is None:
			_getActiveComm()
			time.sleep(1)
		else:
			time.sleep(3)

g_existed = False
g_thread = threading.Thread(target=readCommThread)

def Open():
	global g_thread,g_existed
	g_existed = False
	g_thread.start()
	
def close():
	global g_thread,g_existed
	g_existed = True
	#g_thread.join()

def setTemp(value):
	global g_lastSetTemp
	global g_comm
	g_lastSetTemp = value
	if utility.is_test():
		return
	if g_comm is None:
		return 
	try:
		g_comm.setTemp(value)
	except:
		if g_comm:
			g_comm.close()
		log.warning("焊盘异常")
		g_comm = None	
		return None 

def readTemp():
	global g_lastSetTemp
	if utility.is_test():
		if g_lastSetTemp is None:
			g_lastSetTemp = 400
		return g_lastSetTemp + rand.randint(-5,5)
	global g_comm
	if g_comm is None:
		return None
	try:
		r = g_comm.readTemp()	
		if r is None:
			g_comm = None
			log.warning("焊盘异常")
		return r
	except:
		if g_comm:
			g_comm.close()
		log.warning("焊盘异常")
		g_comm = None	
		return None

def readSetTemp():
	global g_lastSetTemp
	if utility.is_test():
		return g_test_value
	r = readCfg()
	if r:
		g_lastSetTemp = r.tempValue
		return r.tempValue
	else:
		return g_lastSetTemp

def readCfg():
	global g_comm
	if g_comm is None:
		return None
	try:
		r = g_comm.readCfg()	
		if r is None:
			g_comm = None
			log.warning("焊盘异常")
		return r
	except:
		if g_comm:
			g_comm.close()
		log.warning("焊盘异常")
		g_comm = None	
		return None	
		
def portName():		
	if utility.is_test():
		return "TestComm"
	global g_comm
	if g_comm is None:
		return None
	return g_comm.portName
	 
#python串口读写例子 
#http://www.cnblogs.com/starspace/archive/2009/02/20/1394603.html 	
class solderCtrl:
	def __init__(self,commName):
		#19200, 8位，无校验，无硬件流
		self.comm = serial.Serial(commName,19200,timeout=1)
		self.cfg = driver.solder.solderCfg.solderCfg.load()
		
	def __del__(self):
		self.close()
	
	@property
	def portName(self):
		return self.comm.portstr
	
	def close(self):
		if not hasattr(self,"comm"):
			return
		if self.comm is None:
			return
		self.comm.close()
		self.comm = None
		
	#1，设置温度协议：
	#ff 55 06 31 HH LL Check
	#
	#ff 55为固定的数据头
	#温度高8位HH
	#温度低8位LL
	#Check为字节校验
	#Check = (06+31+HH+LL)&0xff	
	#buf[7] FF 55 06 31 00 64 9B
	def setTemp(self,value):
		self.cfg.tempValue = value
		self.setCfg(self.cfg)
		return 
		global g_lastSetTemp
		o = buffer.outBuffer()
		o.setBuf([0xff,0x55,0x06,0x31])
		o.setUInt16(value)
		sum = buffer.checksum(o.buf[2:],1)
		o.setByte(sum) 
		self.comm.write(o.buf)
		g_lastSetTemp = value
		
	#2，读取温度协议：
	#读取命令，7个字节：
	#ff 55 06 10 00 00 16
	#
	#收到的字符串共13个字节，16进制：
	#ff 55 0A 10 ** ** HH LL ** ** Check 0D 0A
	#
	#其中HH，LL为温度高8位于低8位
	#Check为字节校验，
	#Check=data[2]+...+data[9] = 0A + 10 + ... + Check的前1字节		 
	def readTemp(self,reTryCount=2):
		# self.setCfg()
		for x in range(reTryCount):
			o = buffer.outBuffer()
			o.setBuf([0xff,0x55,0x06,0x10,0x00,0x00,0x16])
			self.comm.write(o.buf)
			buf = self.comm.read(13)
			 
			if len(buf) != 13:
				continue
				
			i = buffer.inBuffer(buf) 
			i.getBuf(6)
			v = i.getUInt16()
			i.getBuf(2)
			cc = i.getByte()
			sum = buffer.checksum(i.buf[2:10],1)
			if cc == sum:
				return v
			else:
				print("solderCtrl: wrong checksum %x != %x"%(cc,sum))
		return None
		
	def readCfg(self,reTryCount=2):
		cfg = driver.solder.solderCfg.solderCfg()
		o = buffer.outBuffer()
		o.setBuf([0xFF, 0x55, 0x06, 0x30, 0x00, 0x00, 0x36])
		for x in range(reTryCount):
			self.comm.write(o.buf)
			buf = self.comm.read(29)
			i = buffer.inBuffer(buf) 
			if len(buf) < 28:
					continue
			i = buffer.inBuffer(buf) 
			i.getBuf(4)
			cfg.tempValue = i.getUInt16()
			cfg.sleep = i.getUInt16()
			cfg.protectCurrent = i.getUInt16()
			cfg.powerFactor = i.getUInt16()
			cfg.compensationFactor = i.getUInt16()
			cfg.maxTempValue = i.getUInt16()
			cfg.PID_Kp = i.getUInt16()
			cfg.PID_Ki = i.getUInt16()
			cfg.PID_Kd = i.getUInt16() 
			return cfg
		return None	
	
	#Tx: FF 55 19 31 00 64 00 00 03 20 00 FA 02 FD 02 58 02 29 00 FA 00 DC 0D 03 01 36
	def setCfg(self,cfg):
		global g_lastSetTemp
		o = buffer.outBuffer()
		o.setBuf([0xFF, 0x55, 0x19, 0x31])
		o.setUInt16(cfg.tempValue)
		o.setUInt16(cfg.sleep)
		o.setUInt16(cfg.protectCurrent)
		o.setUInt16(cfg.powerFactor)
		o.setUInt16(cfg.compensationFactor)
		o.setUInt16(cfg.maxTempValue)
		o.setUInt16(cfg.PID_Kp)
		o.setUInt16(cfg.PID_Ki)
		o.setUInt16(cfg.PID_Kd)
		o.setBuf([0x0D, 0x03, 0x01]) #不知道是神马的 
		sum = buffer.checksum(o.buf[2:],1)
		o.setByte(sum) 
		g_lastSetTemp = cfg.tempValue
		self.comm.write(o.buf)
	
	#模拟对端发数据 buf[13] FF 55 0A 10 00 00 00 64 00 00 7E 0D 0A 
	def peerSendTemp(self,value):
		o = buffer.outBuffer()
		o.setBuf([0xff,0x55,0x0A,0x10,0x00,0x00])
		o.setUInt16(value)
		o.setBuf([0x00,0x00])
		sum = buffer.checksum(o.buf[2:10],1)
		o.setByte(sum)
		o.setBuf([0x0D,0x0A])
		self.comm.write(o.buf)
	
def _readCommCfg():
	p = os.path.dirname(__file__)
	if not os.path.exists(p+"/"+"port.txt"):
		return None
	f = open(p+"/"+"port.txt","r")
	r = f.read()
	f.close()
	return r
	
def _writeCommCfg(commName):
	p = os.path.dirname(__file__)
	f = open(p+"/"+"port.txt","w")
	f.write(commName)
	f.close()  
	
#自动查找可用的串口 
def _getActiveComm():
	if utility.is_test():
		return None
		
	global g_comm
	if g_comm:
		return g_comm
		
	def _getAllCom():
		ret = []
		for i in range(20):
			try:
				s = serial.Serial("COM"+str(i))
				s.close()
				ret.append(s.portstr)
			except serial.serialutil.SerialException:
				pass
		return ret
	
	ports = []
	lastPort = _readCommCfg()
	if lastPort:
		ports.append(lastPort)
	ports += _getAllCom()
	
	for c in ports:
		try:
			s = solderCtrl(c)
			if s.readTemp(reTryCount=1) is not None: 
				log.info("打开焊盘成功, %s",s.portName)
				_writeCommCfg(s.portName)
				#s.setCfg(driver.solder.solderCfg.solderCfg.load())
				g_comm = s 
				return g_comm
		except serial.serialutil.SerialException:
				pass
	return None
	
def test_comm(CONNECT_COMM): 
	assert portName() == CONNECT_COMM
	global g_comm
	assert g_comm
	c = g_comm
	assert c.portName == CONNECT_COMM

	v = 100+ rand.randint(-10,10)
	c.setTemp(v	)
	cfg = c.readCfg()
	assert cfg.tempValue == v
	a = c.readTemp()
	
	cfg = driver.solder.solderCfg.solderCfg()
	cfg.tempValue = 98	+ rand.randint(-10,10)			
	cfg.sleep	   = 4				+ rand.randint(0,20)			
	cfg.protectCurrent = 798 		+ rand.randint(-10,10)			
	cfg.powerFactor= 250			
	cfg.compensationFactor = 704	+ rand.randint(-10,10)			
	cfg.PID_Kp = 502		+ rand.randint(-10,10)			
	cfg.PID_Ki = 252		+ rand.randint(-10,10)			
	cfg.PID_Kd = 222		+ rand.randint(-10,10)			
	cfg.maxTempValue = 568+ rand.randint(-10,10)			
	c.setCfg(cfg) 
	
	cfg2 = c.readCfg() 
	import utility
	assert utility.equal(cfg,cfg2,debug=True)

if __name__ == '__main__': 
	test_comm(CONNECT_COMM = "COM10")	
	
	
	
	
	
	
	
	