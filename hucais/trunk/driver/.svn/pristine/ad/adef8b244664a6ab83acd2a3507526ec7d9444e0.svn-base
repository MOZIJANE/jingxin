#coding=utf-8
#lizhenwei		2017-08-04		create
import os,sys

from PyQt5.QtCore import(QCoreApplication,QThread,pyqtSignal,pyqtSlot)
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)	
import utility,qtutility
import time
from driver.motion import motionConfig
from driver.motion import smcApi
from driver.motion import ioCtrl 
import log
g_emgStop = False
# g_emgIgnoreKeys = ["keyStart", "keyStop", "keyReset"]
# 急停下只监测按键
g_emgKeepMonitorKeys = ["keyEmgStop"]

def emgStop():
	global g_emgStop
	g_emgStop = True

def resume():
	global g_emgStop
	g_emgStop = False
	
def isEmgStop():
	global g_emgStop
	return g_emgStop

g_axisIOBitDef = {"ALM":(0,"伺服报警"), 
				"EL+":(1,"正硬限位"), "EL-":(2,"负硬限位"), 
				"ORG":(4,"原点"),"SL+":(6,"正软限位"),"SL-":(7,"负软限位")}
g_axisWarnTypes = None
def axisWarnTypes():
	global g_axisWarnTypes, g_axisIOBitDef
	if not g_axisWarnTypes:
		tk = [k for k in g_axisIOBitDef.keys()]
		axisCnt = motionConfig.g_motionCfg.axisCnt
		rt = []
		for i in range(axisCnt):
			for k in tk:
				if k == "ORG":
					continue
				rt.append(k+str(i))
		g_axisWarnTypes = rt
	return g_axisWarnTypes
	
class ioInputScanThd(QThread):
	'IO输入端扫描线程'
	# 某个bit的状态按下，释放，单击，改变
	sgBitPressed = pyqtSignal(dict)
	sgBitReleased = pyqtSignal(dict)
	sgBitClicked = pyqtSignal(dict)
	sgBitChanged = pyqtSignal(dict)
	# 加入轴状态监控: ORG EL+ EL- SL+ SL- ALM
	
	def __init__(self):
		super(ioInputScanThd, self).__init__()
		if not utility.is_test():
			smcApi.connectServer()
		super(ioInputScanThd,self).__init__()
		self.ioCfg = motionConfig.g_motionCfg.ioInCfgList
		self.axisCfg = motionConfig.g_motionCfg.axisCfgList
		self.pinCnt = len(self.ioCfg)
		self.axisCnt = len(self.axisCfg)
		self.isStop = False
		self.curBitPressed = [False]*self.pinCnt
	
	def __del__(self):
		self.stopThd()
		self.wait()
		self.quit()
	
	def startThd(self):
		self.isStop = False
		self.start()
		
	def stopThd(self):
		self.isStop = True
		self.wait()
	
	def readAxisStateList(self):
		st = []
		for i in range(self.axisCnt):
			st.append(smcApi.readAxisIOStatus(i))
		return st
	
	def processGpIO(self, preState, curState):
		'通用IO处理'
		if curState is None:
			return
		if curState == preState:
			return
		for i in range(self.pinCnt):
			if preState is not None:
				prebit = ((preState&(1<<i))>>i)
			else:
				prebit = None
			curbit = ((curState&(1<<i))>>i)
			if prebit == curbit:
				continue
			#读取该地址对应的io配置
			cfg = motionConfig.g_motionCfg.ioInputConfigByAddr(i)
			cfg["state"] = curbit
			ioname = cfg["name"]
			ioType = cfg["type"]
			if isEmgStop() and ioType not in g_emgKeepMonitorKeys:
				continue
			# 这个状态改变的信号是个
			self.sgBitChanged.emit(cfg)				
			if (1==prebit or prebit is None) and 0==curbit:
				self.curBitPressed[i] = True
				# 按下信号
				self.sgBitPressed.emit(cfg)
			elif 0==prebit and 1==curbit:
				# 释放信号
				self.sgBitReleased.emit(cfg)
				if self.curBitPressed[i]:
					self.curBitPressed[i] = False
					# 单击信号
					self.sgBitClicked.emit(cfg)
	
	def processAxisIOList(self, prelist, curlist):
		if len(prelist)!=self.axisCnt or len(curlist)!=self.axisCnt:
			return
		for i in range(self.axisCnt):
			acfg = motionConfig.g_motionCfg.axisConfigByAddr(i)
			if acfg["type"] == "axisD":
				continue
			self.processOneAxisIO(acfg,prelist[i],curlist[i])
		
	def processOneAxisIO(self,axisCfg, preState,curState):
		if curState is None:
			return
		if curState == preState:
			return
		global g_axisIOBitDef
		for k,v in g_axisIOBitDef.items():
			bitType = k
			bitId = v[0]
			bitName = v[1]
			if preState is None:
				prebit = None
			else:
				prebit = ((preState & (1 << bitId)) >> bitId)
			curbit = ((curState & (1 << bitId)) >> bitId)
			if prebit == curbit:
				continue
			
			straddr = str(axisCfg["addr"])
			axisName = axisCfg["name"]
			cfg = {"type":bitType + straddr, "name": axisName + bitName}
			self.sgBitChanged.emit(cfg)
			# 轴上的专用IO是 高电平触发，release时为告警
			if (1 == prebit or prebit is None) and 0 == curbit:
				self.sgBitPressed.emit(cfg)
			elif 0 == prebit and 1 == curbit:
				self.sgBitReleased.emit(cfg)
			
	def run(self):		
		curState = 0
		# preState = ioCtrl.ioInCtrl.readAll()
		# preState = 0XFFFFFF
		preState = None
		preAxisStateList = [None]*self.axisCnt
		while not self.isStop:
#			qtutility.qtSleep(5)
			time.sleep(0.1)
			curState = ioCtrl.ioInCtrl.readAll()
			curAxisStateList = self.readAxisStateList()
			self.processGpIO(preState,curState)
			self.processAxisIOList(preAxisStateList, curAxisStateList)
			preState = curState
			preAxisStateList = curAxisStateList[:]
		else:
			self.isStop = False
					
def test():
	app = QCoreApplication(sys.argv)
	t = ioInputScanThd()
	t.start()
	t.stop()
	t.wait()
	
if __name__ == "__main__":
	test()
		
	