#coding=utf-8
#lizhenwei		2017-08-02		create
import os,sys
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)	
from PyQt5.QtCore import (QCoreApplication,QTimer, QEventLoop)
import log
import qtutility 
import time
import driver.motion.motionConfig
from driver.motion import smcApi

class motorAxis:
	def __init__(self,axisKey):
		'单轴,由轴配置初始化'
		# 1.连接控制器
		rt = smcApi.connectServer()
		# 2.定义是否连接控制器，是否紧急停止标志
		self.isConnectServer = (0==rt)
		self._isEmgStop = False
		self.curVel = -1 # 轴的速度
		self._autoVel = 500 # 轴运动自动速度
		# 3.cfginit
		self.axisConfig = driver.motion.motionConfig.cfg().axisConfig(axisKey)
		self._cfgInit()
	
	def cfg(self):
		return self.axisConfig
	
	@property
	def addr(self):
		return self.axisAddr
	
	def _cfgInit(self):
		if not self.isConnectServer:
			return
		# 轴地址
		self.axisAddr = self.axisConfig["addr"]
		
		# 一个Unit代表的物理量
		self.phyPerUnit = self.axisConfig["physcisPerUnit"]
		
		# 针对伺服对应的设置：使能-EZ-ALARM
		# 设置轴的伺服使能端口输出电平,放在最前面，否则无法设置后续的
		svlogic = self.axisConfig["sevonLogic"]
		if svlogic is not None:
			rt = smcApi.writeServonPin(self.axisAddr,svlogic)
		
		# 设置EZ信号有效电平
		ezLogic = self.axisConfig["ezLogic"]
		if ezLogic is not None:
			rt = smcApi.setEZmode(self.axisAddr, ezLogic)
		
		# 设置ALARM信号
		alarmEnable = self.axisConfig["alarmEnable"]
		alarmLogic = self.axisConfig["alarmLogic"]
		if alarmEnable is not None and alarmLogic is not None:
			rt = smcApi.setAlarmMode(self.axisAddr, alarmEnable, alarmLogic)
		
		# 设置脉冲输出模式
		if self.axisConfig["moveDirection"] == "positive":
			rt = smcApi.setPulseOutmode(self.axisAddr,0)
		elif self.axisConfig["moveDirection"] == "negative":
			rt = smcApi.setPulseOutmode(self.axisAddr,2)
		
		# 设置脉冲当量，1
		rt = smcApi.setEquiv(self.axisAddr,self.axisConfig["equiv"])
		
		# 设置反向间隙补偿，
		rt = smcApi.setBacklash(self.axisAddr,self.axisConfig["backlash"])
					
		# 设置速度曲线
		rt = self._setVelCfg()	
		
		# 设置S段参数
		rt = smcApi.setSprofile(self.axisAddr,self.axisConfig["sPara"])
		
		# 设置减速停止时间
		rt = smcApi.setDecStopTime(self.axisAddr, self.axisConfig["decStopTime"]) 
		
		# 设置回原点信号
		rt = smcApi.setHomePinLogic(self.axisAddr,self.axisConfig["homeConfig"]["logic"])
		
		# 设置回原点模式
		homeDir = self.axisConfig["homeConfig"]["direction"]
		homeMode = self.axisConfig["homeConfig"]["mode"]
		homePosSource = self.axisConfig["homeConfig"]["posSource"]
		rt = smcApi.setHomeMode(self.axisAddr,homeDir,homeMode,homePosSource)
		
		# 设置回零后偏移位置，回零后，设置偏移为0
		rt = smcApi.setHomePositionUnit(self.axisAddr,2,0)
		
		# 设置回原点速度曲线
		homeLowVel = self.axisConfig["homeConfig"]["lowVel"]/self.phyPerUnit
		homeHighVel = self.axisConfig["homeConfig"]["highVel"]/self.phyPerUnit
		homeTacc = self.axisConfig["homeConfig"]["tAcc"]
		homeTdec = self.axisConfig["homeConfig"]["tDec"]
		rt = smcApi.setHomeProfileUnit(self.axisAddr,homeLowVel,homeHighVel,homeTacc,homeTdec)
										
		# 设置急停信号，不涉及
		# rt = smcApi.setEmgMode(self.axisAddr,\
								# self.axisConfig["emgEnable"],\
								# self.axisConfig["emgLogic"])
								
		# 硬件限位
		elEnable = self.axisConfig["elConfig"]["enable"]
		elLogic = self.axisConfig["elConfig"]["logic"]
		elMode = self.axisConfig["elConfig"]["mode"]
		rt = smcApi.setElMode(self.axisAddr,elEnable,elLogic,elMode)
								
		# 软件限位
		self._setSoftLimit()
	
	def _enableServon(self):
		return 0== smcApi.writeServonPin(self.axisAddr,0)
	
	def _disableServon(self):
		return 0== smcApi.writeServonPin(self.axisAddr,1)
	
	def _setVelCfg(self):
		minVel = self.axisConfig["velConfig"]["minVel"]/self.phyPerUnit
		self._autoVel = maxVel = self.axisConfig["velConfig"]["maxVel"]/self.phyPerUnit
		tAcc = self.axisConfig["velConfig"]["tAcc"]
		tDec = self.axisConfig["velConfig"]["tDec"]
		stopVel = self.axisConfig["velConfig"]["stopVel"]/self.phyPerUnit
		if self.equCurVel(maxVel):
			return True
		self.curVel = maxVel
		return 0 == smcApi.setProfileUnit(self.axisAddr,minVel,maxVel,tAcc,tDec,stopVel)
	
	def _setSoftLimit(self):
		slEnable = self.axisConfig["slConfig"]["enable"]
		slSourceSel = self.axisConfig["slConfig"]["sourceSel"]
		slAction = self.axisConfig["slConfig"]["slAction"]
		slNlimit = self.axisConfig["slConfig"]["nLimit"]/self.phyPerUnit
		slPlimit = self.axisConfig["slConfig"]["pLimit"]/self.phyPerUnit
		rt = smcApi.setSoftLimitUnit(self.axisAddr,slEnable,slSourceSel,slAction,slNlimit,slPlimit)
		return 0 == rt
		
	def setTravelRange(self, low, up):
		'设置行程'
		if (not self.isConnectServer) or self._isEmgStop:
			return
		if not self.isIdle():
			return
		self.axisConfig["slConfig"]["nLimit"] = low
		self.axisConfig["slConfig"]["pLimit"] = up
		return self._setSoftLimit()
		
	def equCurVel(self, vel):
		'vel 与 当前速度相等'
		return abs(self.curVel - vel)<0.1
	
	def setVel(self,vel):
		'设置速度'
		if (not self.isConnectServer) or self._isEmgStop:
			return False
		if vel < 1e-2:
			return False
		if self.equCurVel(vel):
			# print("no set curvel=%f ,setvel= %f"%(self.curVel,vel))
			return True
		self.curVel = vel
		if self.isIdle():
			# 设置速度曲线
			maxVelUnit = vel/self.phyPerUnit
			minVelUnit = 0
			tAcc = self.axisConfig["velConfig"]["tAcc"]
			tDec = self.axisConfig["velConfig"]["tDec"]
			stopUnit = 0
			rt = smcApi.setProfileUnit(self.axisAddr, minVelUnit, maxVelUnit, tAcc, tDec, stopUnit)
		else:
			# 在线变速，当以这个速度结束运动后，又恢复到之前的setProfileUnit对应的速度
			unitVel = vel/self.phyPerUnit
			rt = smcApi.changeSpeedUnit(self.axisAddr,unitVel,0.2)
		return rt == 0
				
	def setAutoVel(self):
		'设置自动运行速度'
		if (not self.isConnectServer) or self._isEmgStop:
			return False
		if self.equCurVel(self._autoVel):
			return True
		if not self.waitForIdle():
			return False
		return self._setVelCfg()
	
	@staticmethod
	def connectServer():
		return 0 == smcApi.connectServer()
	
	@staticmethod	
	def disConnectServer():
		return 0 == smcApi.disConnectServer()
	
	def goHome(self,isWait=True, toutMs=0):
		'''
		fun: 回零
		input:
			isWait: 等待True，不等待False
			toutMs: 超时时间，isWait=True有效
		return:
			成功True，失败False
		'''
		if (not self.isConnectServer) or self._isEmgStop:
			return
		if not self.isIdle():
			return
		if 0 != smcApi.homeMove(self.axisAddr):
			return
		if not isWait:
			return True
		if not self.waitForHomeResult(toutMs):
			return
		return self.waitForIdle()
	
	# 快速归零，先以最高速运动至nearPos，在调用回零函数
	def goHomeFast(self, nearPos=10):
		if (not self.isConnectServer) or self._isEmgStop:
			return
		if not self.isIdle():
			return
		if not self.setAutoVel():
			return False
		pos = self.getCurrentPos()
		if pos is None:
			return
		if pos > nearPos:
			if not self.goTarget(nearPos):
				return
		elif pos < (-nearPos):
			if not self.goTarget(-nearPos):
				return
		return self.goHome()
	
	def waitForHomeResult(self,toutMs=0):
		'等待为原点位置'
		if (not self.isConnectServer) or self._isEmgStop:
			return
		homeState = 0
		iterMs = 10
		if toutMs <= 0:
			# 无限循环等待
			while 1 != homeState:
				homeState = smcApi.getHomeResult(self.axisAddr)
				if not qtutility.qtSleep(0):
					return
		elif toutMs > 0:
			# 等待到超时
			tcnt = 0
			while (1 != homeState) and (tcnt < toutMs):
				homeState = smcApi.getHomeResult()
				if not qtutility.qtSleep(iterMs):
					return
				tcnt += iterMs				
		return 1 == homeState
				
	def goTarget(self,pos,isWait=True,isAbsolute=True):
		'''
		fun: 运动至目的位置
		input:
			pos: 目的坐标 mm
			isWait: 是否等待运动到目的坐标
			isAbsolute: 绝对坐标True，相对坐标False
		return:
			成功True，失败False
		'''
		if (not self.isConnectServer) or self._isEmgStop:
			return
		# 1.等待空闲
		if not self.waitForIdle():
			log.warning("motorAxis 等待空闲失败 %f"%pos)
			return False
		# 2.pmove
		unitPos = pos/self.phyPerUnit
		rt = smcApi.pmoveUnit(self.axisAddr,unitPos,int(isAbsolute))
		# 当到达限位点 会发生错误返回
		if 0!=rt:
			log.warning("smcApi.pmoveUnit error rt = %d, unitPos = %f"%(rt, unitPos))
			return False
		# 3.wait	
		if not isWait:
			return True
		return self.waitForIdle() 
	 
	def setCurrentPos(self,pos):
		'设置当前位置'
		if (not self.isConnectServer) or self._isEmgStop:
			return
		rt = smcApi.setPositionUnit(self.axisAddr,pos/self.phyPerUnit)
		return 0 == rt
	
	def getCurrentPos(self):
		'获取当前位置'
		if (not self.isConnectServer) or self._isEmgStop:
			return
		pos =  smcApi.getPositionUnit(self.axisAddr)
		return pos*self.phyPerUnit
	
	def decStop(self):
		'减速停止'
		if (not self.isConnectServer) or self._isEmgStop:
			return True
		if 0 != smcApi.stop(self.axisAddr, 0):
			return
		return self.waitForIdle()
	
	def imtStop(self):
		'立即停止'
		if (not self.isConnectServer) or self._isEmgStop:
			return True
		if 0 != smcApi.stop(self.axisAddr,1):
			return
		return self.waitForIdle()
 
	def goConstanVel(self,isPositive=True):
		'''
		fun:恒速运动
		input:
			isPositive: 正向True， 负向False
		return:
			成功True，失败False
		''' 
		if (not self.isConnectServer) or self._isEmgStop:
			return False
		if not self.isIdle():
			return False
		return 0 == smcApi.vmove(self.axisAddr, int(isPositive))
			
	def isIdle(self):
		'是否空闲'
		if self._isEmgStop:
			return False
		elif not self.isConnectServer:
			return True
		#0正在运行，1已经停止	
		rt = smcApi.checkDone(self.axisAddr)
		return 1==rt
	
	def waitForIdle(self,toutMs=0):
		
		'''
		fun: 等待一定时间，返回是否空闲
		input:
			ms: 超时
		return:
			空闲Tru，忙碌False
		'''
		if (not self.isConnectServer) or self._isEmgStop:
			return	
		iterMs = 10	
		if toutMs <= 0:
			while not self.isIdle():
				if not qtutility.qtSleep(0):
					return False
		else:
			tcnt = 0
			while (not self.isIdle()) and (tcnt < toutMs):
				if not qtutility.qtSleep(iterMs):
					return False
				tcnt += iterMs
		return self.isIdle()
	  
	def emgStop(self):
		rt = self.imtStop()
		self._disableServon()
		self._isEmgStop = True
		return rt
		
	def resume(self):
		self._isEmgStop = False
		self._enableServon()
		return self.imtStop()
	
def test_server():
	log.debug("测试控制器连接与断开")
	assert 0 == smcApi.connectServer()
	assert 0 == smcApi.disConnectServer()
	
def test_axis(axis, minRng, maxRng, lowvel, upvel):
	import time
	axisX = motorAxis(axis)
	assert axisX.imtStop()
	# 1.gohome
	log.debug("快速回零")
	time.sleep(3)
	assert axisX.goHomeFast()
	assert axisX.getCurrentPos()<0.05
	p_abs = maxRng/3 #绝对坐标
	p_relative = p_abs/2	 #相对坐标

	# 设置速度
	log.debug('在线变速与恢复自动速度')
	time.sleep(3)
	assert axisX.setVel(lowvel)
	assert axisX.goTarget(maxRng*0.9,isWait=False)
	time.sleep(3)
	assert axisX.setVel(upvel)
	assert not axisX.isIdle()
	assert not axisX.setAutoVel() #非空闲态无法设置速度
	assert axisX.waitForIdle()
	assert axisX.setAutoVel()
	
	# 设置行程
	log.debug("设置行程")
	time.sleep(3)
	assert axisX.goTarget(maxRng*0.4)
	assert axisX.setTravelRange(maxRng*0.2,maxRng*0.3)
	# 若当前停留的位置在范围之外，则无法移动的
	assert not axisX.goConstanVel()
	assert not axisX.goTarget(maxRng*0.6)
	assert axisX.setTravelRange(minRng, maxRng)
	
	# 2.goTarget
	# 2.1 等待，绝对坐标
	log.debug("等待绝对定长运动")
	time.sleep(3)
	assert axisX.goTarget(p_abs,True,True)
	assert axisX.getCurrentPos() < p_abs+0.05
	
	 
	# 2.2 等待，相对坐标
	log.debug("等待相对定长运动")
	time.sleep(3)
	assert axisX.goTarget(-p_relative,True,False)
	pos = axisX.getCurrentPos()
	assert abs(pos-p_relative) < 0.05
	
	# 2.3 不等待，绝对坐标
	log.debug("不等待绝对定长运动")
	time.sleep(3)
	assert axisX.goTarget(p_abs,False,True)
	assert axisX.waitForIdle()
	assert axisX.getCurrentPos() < p_abs + 0.05
	
	# 2.4 不等待，相对坐标
	log.debug("不等待相对定长运动")
	time.sleep(3)
	assert axisX.goTarget(p_relative,False,False)
	assert axisX.waitForIdle()
	assert axisX.getCurrentPos() < p_abs + p_relative + 0.05
	
	#3 恒速运动+减速停止
	log.debug("恒速运动并减速停止")
	time.sleep(3)
	assert axisX.goConstanVel()
	time.sleep(0.5)
	assert axisX.decStop()	
	assert axisX.isIdle()
	#4 反向恒速运动+立即停止
	log.debug("恒速运动并立即停止")
	time.sleep(3)
	assert axisX.goConstanVel(False)
	time.sleep(0.5)
	assert axisX.imtStop()
	assert axisX.isIdle()

	#5 紧急停止
	log.debug("紧急停止与恢复")
	time.sleep(3)
	assert axisX.goTarget(maxRng*0.9)
	assert axisX.emgStop()
	assert not axisX.goTarget(maxRng*0.9)
	assert axisX.resume()
	
	#快速归零
	log.debug("快速归零")
	time.sleep(3)
	assert axisX.goHomeFast()

def test_x():
	log.debug('测试X轴')
	test_axis("axisX",0,500,20,300)
	
def test_y():
	log.debug('测试Y轴')
	test_axis("axisY",0,500,20,300)
	
def test_z():
	log.debug('测试Z轴')
	test_axis("axisZ", 0,100,5,300)

def test_r():
	log.debug('测试R轴')
	test_axis("axisR", -175,175,5,45)
	
def test_d():
	'送锡轴无原点，始终是相对运动'
	import time
	log.debug('测试D轴')
	time.sleep(3)
	axisX = motorAxis("axisD")
	assert axisX.imtStop()
	assert axisX.setVel(1)
	assert axisX.goTarget(10, isWait=False, isAbsolute = False)
	qtutility.qtSleep(2000)
	assert axisX.setVel(100)
	assert axisX.waitForIdle()
	assert axisX.setAutoVel()
	assert axisX.goTarget(10, isWait=True, isAbsolute = False)
	
if __name__ == "__main__":
	test_server()
	# test_x()
	# test_y()
	# test_z()
	# test_r()
	# test_d()