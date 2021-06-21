#coding=utf-8
#lizhenwei		2017-08-04		create
import os,sys
from PyQt5.QtCore import (QCoreApplication,QTimer, QEventLoop)
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)	
		
import qtutility
import driver.motion.motionConfig
from driver.motion import smcApi

class ioOutCtrl:
	def __init__(self,ioName=None,ioAddr=None):
		if ioAddr is not None:
			self.ioCfg = driver.motion.motionConfig.cfg().ioOutputConfigByAddr(ioAddr)
		elif ioName is not None:
			# 读取该端口的配置
			self.ioCfg = driver.motion.motionConfig.cfg().ioOutputConfigByName(ioName)
		else:
			assert 0
		#	self.ioCfg = None			
	
	def enable(self,tdelayMs=0):
		return self.writeState(self.ioCfg["enLogic"],tdelayMs)
	
	def disable(self):
		return self.writeState(self.ioCfg["enLogic"]^1)
	
	def reverseState(self):
		'电平反转'
		if self.isEnable():
			return self.disable()
		else:
			return self.enable()
		return True
		
	def isEnable(self):
		return self.ioCfg["enLogic"] == self.readState()
		
	def writeState(self,state=0, tdelayMs=0):
		'写端口电平，延时tdelayMs'
		if not self.ioCfg:
			return
		if not self.writeBitState(self.ioCfg["addr"],state):
			return
		if 0 >= tdelayMs:
			return True
		else:
			if not qtutility.qtSleep(tdelayMs):
				return
			return self.writeBitState(self.ioCfg["addr"],(state&0x01)^1)
		
	def readState(self):
		'读取状态'
		if self.ioCfg is None:
			return None
		return smcApi.readOutbit(self.ioCfg["addr"])	

	@staticmethod
	def readAll(portno=0):
		return smcApi.readOutPort(portno)
			
	@staticmethod
	def writeAll(portno=0,portval=0):
		return 0 == smcApi.writeOutPort(portno,portval)
	
	@staticmethod
	def writeAllHigh(portno=0):
		return ioOutCtrl.writeAll(portno,0xFFFFFFFF)
	
	@staticmethod
	def writeAllLow(portno=0):
		return ioOutCtrl.writeAll(portno, 0)
	
	@staticmethod
	def writeBitState(bitno, state):
		return 0 == smcApi.writeOutbit(bitno,state)
		

class ioInCtrl:
	def __init__(self,ioName=None,ioAddr=None):
		if ioAddr is not None:
			self.ioCfg = driver.motion.motionConfig.cfg().ioInputConfigByAddr(ioAddr)
		elif ioName is not None:
			# 读取该端口的配置
			self.ioCfg = driver.motion.motionConfig.cfg().ioInputConfigByName(ioName)
		else:
			assert 0
			self.ioCfg = None	
					
	def isEnable(self):
		'状态是否使能态'
		return self.ioCfg["enLogic"]==self.readState()
		
	def waitForEnable(self,toutMs=0):
		return self.waitForState(self.ioCfg["enLogic"], toutMs)
		
	def readState(self):
		'读取状态'
		if self.ioCfg is None:
			return None
		return smcApi.readInbit(self.ioCfg["addr"])

	def waitForState(self,state,toutMs=0):
		'等待状态为state，toutMs内'
		if self.ioCfg is None:
			return False
		#TODO 原来iterMs=50
		iterMs = 10
		if 0 >= toutMs:
			# 无限等待
			while state != self.readState():
				QCoreApplication.processEvents()
				# pass
				# if not qtutility.qtSleep(iterMs):
					# return
		else:
			# 超时等待
			tcnt = 0
			while (tcnt < toutMs) and (state != self.readState()):
				if not qtutility.qtSleep(iterMs):
					return
				tcnt += iterMs	
		return state == self.readState()
				
	@staticmethod
	def readAll(portno=0):
		'读取通用端口的bit状态'
		return smcApi.readInport(portno)
	
	@staticmethod	
	def readBitState(bitno):
		'读取'
		return smcApi.readInbit(bitno)
		
	@staticmethod
	def readAxisIOStatus(axis):
		'读取轴IO信号'
		return smcApi.readAxisIO(axis)
	

g_ironAirCtrl = None # 烙铁上的气缸输出控制
g_ironAirInDown = None # 烙铁上的气缸输入下降
g_ironAirInUp = None 	 # 烙铁上的气缸输入上升
g_cleanAirCtrl = None
g_camLightCtrl = None
g_blockWire = None
g_lackWire = None

def ironAirCtrl():
	global g_ironAirCtrl
	if not g_ironAirCtrl:
		g_ironAirCtrl = ioOutCtrl("ironAir")
	return g_ironAirCtrl

def ironAirInDown():
	global g_ironAirInDown
	if not g_ironAirInDown:
		g_ironAirInDown = ioInCtrl("airDown")
	return g_ironAirInDown

def ironAirInUp():
	global g_ironAirInUp
	if not g_ironAirInUp:
		g_ironAirInUp = ioInCtrl("airUp")
	return g_ironAirInUp
	
def cleanAirCtrl():
	global g_cleanAirCtrl
	if not g_cleanAirCtrl:
		g_cleanAirCtrl = ioOutCtrl("cleanAir")
	return g_cleanAirCtrl

def camLightCtrl():
	global g_camLightCtrl
	if not g_camLightCtrl:
		g_camLightCtrl = ioOutCtrl("cameraLight")
	return g_camLightCtrl
	
def blockWire():
	global g_blockWire
	if not g_blockWire:
		g_blockWire = ioInCtrl("blockWire")
	return g_blockWire

def lackWire():
	global g_lackWire
	if not g_lackWire:
		g_lackWire = ioInCtrl("lackWire")
	return g_lackWire
	
def resetIOOut():
	ioOutCtrl.writeAll(0, 0xFFFFFFFF)
	
def test_iooutCtrl():
	# 1.ioName=cameraLight
	rt = smcApi.connectServer()
	assert 0==rt
	
	outCtrl = ioOutCtrl(ioName="cameraLight")
	
	outCtrl.enable()
	assert outCtrl.isEnable()
	qtutility.qtSleep(1000)
	outCtrl.disable()
	assert not outCtrl.isEnable()
		
	outCtrl.writeState(0,1000)
	assert 1==outCtrl.readState()
	
	
	# 2.addr=0
	outCtrl = ioOutCtrl(ioAddr=0)
	outCtrl.enable()
	assert outCtrl.isEnable()
	
	qtutility.qtSleep(1000)
	outCtrl.disable()
	assert not outCtrl.isEnable()
	
	outCtrl.writeState(0,1000)
	assert 1==outCtrl.readState()
	
	rt = smcApi.disConnectServer()
	assert 0==rt
	
def test_ioinCtrl():
	rt = smcApi.connectServer()
	assert 0==rt
	
	# 1.ioName=keyStart
	inCtrl = ioInCtrl(ioName="keyStart")
	
	rt = inCtrl.isEnable()
	assert rt==False
	
	rstate = inCtrl.readState()
	assert rstate==1
	
	rt = inCtrl.waitForState(0,1000)
	assert rt==False
	
	# 2.addr=0
	inCtrl = ioInCtrl(ioAddr=0)
	rt = inCtrl.isEnable()
	assert rt==False
	
	rstate = inCtrl.readState()
	assert rstate==1
	
	rt = inCtrl.waitForState(0,1000)
	assert rt==False
	
	rt = smcApi.disConnectServer()
	assert 0==rt

	
if __name__=="__main__":
	# test_iooutCtrl()
	test_ioinCtrl()