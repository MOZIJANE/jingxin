#coding=utf-8
#lizhenwei		2017-08-03		create
import os,sys

import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)			
from driver.motion import smcApi
import driver.motion.motorAxis
import driver.motion.motionConfig
import utility,enhance,qtutility
import log

class motorCtrl(object):
	def __init__(self):
		'由多轴的配置，进行初始化'
		# 1.连接控制器
		self.isConnectServer = driver.motion.motorAxis.motorAxis.connectServer()
		self._isEmgStop = False
		self._vectorSpd = -1			
		# 2.创建各个轴
		self.xAxis = driver.motion.motorAxis.motorAxis('axisX')
		self.yAxis = driver.motion.motorAxis.motorAxis('axisY')
		self.zAxis = driver.motion.motorAxis.motorAxis('axisZ')
		self.rAxis = driver.motion.motorAxis.motorAxis('axisR')
		self.dAxis = driver.motion.motorAxis.motorAxis('axisD')
		self.locationEvent = enhance.event()
	
	def isEmgStop(self):
		return self._isEmgStop
	
	def close(self):
		driver.motion.motorAxis.motorAxis.disConnectServer()
		
	def goHome(self):
		'联动gohome'
		if (not self.isConnectServer) or self._isEmgStop:
			return False
		if not self.zAxis.goHome(isWait=False):
			return
		if not self.xAxis.goHome(isWait=False):
			return
		if not self.yAxis.goHome(isWait=False):
			return
		if not self.rAxis.goHome(isWait=False):
			return
		if not self.zAxis.waitForHomeResult():
			return
		if not self.xAxis.waitForHomeResult():
			return
		if not self.yAxis.waitForHomeResult():
			return
		if not self.rAxis.waitForHomeResult():
			return
		if not self.waitForIdleZ():
			return
		if not self.waitForIdleX():
			return
		if not self.waitForIdleY():
			return
		return self.waitForIdleR()
		
	def goHomeFast(self,xn=10,yn=10,zn=10,rn=10):
		'快速归零'
		if (not self.isConnectServer) or self._isEmgStop:
			log.warning("goHomeFast() setAutoVel flag return")
			return
		if not self.setAutoVel():
			log.warning("goHomeFast() setAutoVel failed")
			return
		#z先回零,xyr联动回零
		x,y,z,r = self.getCurrentPos()
		if z>zn:
			self.goTargetZ(zn)
		if x > xn:
			if not self.goTargetX(xn,isWait=False):
				return
		if y > yn:
			if not self.goTargetY(yn, isWait=False):
				return
		if r > rn:
			if not self.goTargetR(rn, isWait=False):
				return
		elif r < -rn:
			if not self.goTargetR(-rn, isWait=False):
				return
		if not self.waitForIdle():
			return
		return self.goHome()
		
	def goTargetXY(self,x,y,isWait=True,isAbsolute=True):
		'xy联动'
		if (not self.isConnectServer) or self._isEmgStop:
			return False
		if not self.goTargetX(x,False,isAbsolute):
			return
		if not self.goTargetY(y,False,isAbsolute):
			return
		if not isWait:
			return True
		if not self.waitForIdleX():
			return
		return self.waitForIdleY()
	
	def goTargetXYZ(self,x,y,z,isWait=True,isAbsolute=True):
		'xyz联动'
		if (not self.isConnectServer) or self._isEmgStop:
			return False
		if not self.goTargetX(x,False,isAbsolute):
			return
		if not self.goTargetY(y,False,isAbsolute):
			return
		if not self.goTargetZ(z,False,isAbsolute):
			return
		if not isWait:
			return True
		if not self.waitForIdleX():
			return
		if not self.waitForIdleY():
			return
		return self.waitForIdleZ()
		
	def goTargetXYR(self,x,y,r,isWait=True,isAbsolute=True):
		'xyr联动'
		if (not self.isConnectServer) or self._isEmgStop:
			return False
		if not self.goTargetX(x,False,isAbsolute):
			return
		if not self.goTargetY(y,False,isAbsolute):
			return
		if not self.goTargetR(r,False,isAbsolute):
			return
		if not isWait:
			return True
		if not self.waitForIdleX():
			return
		if not self.waitForIdleY():
			return
		return self.waitForIdleR()
		
	def goTargetXYZR(self,x,y,z,r,isAbsolute=True):
		'z先归零，x,y,r联动，z下降'
		if (not self.isConnectServer) or self._isEmgStop:
			return False
		if not self.waitForIdleZ():
			return
		if not self.goTargetZ(0.0):
			return
		if not self.goTargetXYR(x,y,r,isWait = True):
			return
		return self.goTargetZ(z,isWait = True)
	
	def equCurSpd(self,spd):
		return abs(self._vectorSpd - spd) < 0.1
		
	def moveLineXY(self,x,y,spd,isWait=True, isAbsolute=True):
		if (not self.isConnectServer) or self._isEmgStop:
			return False
		if not self.equCurSpd(spd):
			self.setVectorSpd(spd)
		mmPerUnit = 0.005
		axisList = [self.xAxis.addr, self.yAxis.addr]
		posList = [x/mmPerUnit,y/mmPerUnit]
		rt = smcApi.lineUnit(0,2,axisList,posList,int(isAbsolute))
		if 0!=rt:
			return False
		if not isWait:
			return True
		if not self.vectorWaitForIdle():
			return False
		return True
	
	def moveLineXYZ(self,x,y,z,spd,isWait=True, isAbsolute=True):
		if (not self.isConnectServer) or self._isEmgStop:
			return False
		if not self.equCurSpd(spd):
			self.setVectorSpd(spd)
		mmPerUnit = 0.005
		axisList = [self.xAxis.addr, self.yAxis.addr, self.zAxis.addr]
		posList = [x/mmPerUnit,y/mmPerUnit,z/mmPerUnit]
		rt = smcApi.lineUnit(0,len(axisList),axisList,posList,int(isAbsolute))
		if 0!=rt:
			return False
		if not isWait:
			return True
		if not self.vectorWaitForIdle():
			return False
		return True
	
	def setVectorSpd(self,spd):
		'设置插补速度'
		if (not self.isConnectServer) or self._isEmgStop:
			return False
		mmPerUnit = 0.005
		minvel = 0
		maxvel = spd / mmPerUnit
		tAcc = 0.2
		tDec = 0.2
		stopvel = 0
		sparm = 0.1
		stoptime = 0.2
		if 0 != smcApi.setVectorProfileUnit(0,minvel,maxvel,tAcc,tDec,stopvel):
			return False
		if 0 != smcApi.setVectorSProfile(0,sparm):
			return False
		if 0 != smcApi.setVectorDecStopTime(0,stoptime):
			return False
		return True
		
	def vectorWaitForIdle(self,toutMs=0):
		if self._isEmgStop:
			return False
		elif not self.isConnectServer:
			return True
		iterMs = 10
		if toutMs <= 0:
			while not self.isVectorIdle():
				if not qtutility.qtSleep(0):
					return False
		else:
			tcnt = 0
			while (not self.isVectorIdle()) and (tcnt < toutMs):
				if not qtutility.qtSleep(iterMs):
					return False
				tcnt += iterMs
		return self.isVectorIdle()
	
	def isVectorIdle(self):
		'插补轴是否空闲'
		if self._isEmgStop:
			return False
		elif not self.isConnectServer:
			return True
		#0正在运行，1已经停止	
		rt = smcApi.checkDoneMulticoor(0)
		return 1 == rt
	
	def getCurrentPos(self):
		'获取当前坐标'
		if (not self.isConnectServer) or self._isEmgStop:
			self.locationEvent.emit(0,0,0,0)
			return 0,0,0,0
		x = self.xAxis.getCurrentPos()
		y = self.yAxis.getCurrentPos()
		z = self.zAxis.getCurrentPos()
		r = self.rAxis.getCurrentPos()
		self.locationEvent.emit(x,y,z,r)
		return x,y,z,r
	
	def decStop(self):
		'所有轴减速停止'
		if (not self.isConnectServer) or self._isEmgStop:
			return True
		if not self.xAxis.decStop():
			return
		if not self.yAxis.decStop():
			return
		if not self.zAxis.decStop():
			return
		if not self.rAxis.decStop():
			return
		return self.dAxis.decStop()
				
	def imtStop(self):
		'所有轴立即停止'
		if (not self.isConnectServer) or self._isEmgStop:
			return True
		if not self.xAxis.imtStop():
			return
		if not self.yAxis.imtStop():
			return
		if not self.zAxis.imtStop():
			return
		if not self.rAxis.imtStop():
			return
		return self.dAxis.imtStop()
		
	def emgStop(self):
		'紧急停止'
		# 1.运动控制器紧急停止
		if 0 != smcApi.emgStop():
			return
		self._isEmgStop = True
		# 2.各个轴设置紧急标志
		if not self.xAxis.emgStop():
			return
		if not self.yAxis.emgStop():
			return
		if not self.zAxis.emgStop():
			return
		if not self.rAxis.emgStop():
			return
		return self.dAxis.emgStop()
		
	def resume(self):
		'从紧急态恢复，先恢复单轴的同时有停止动作'
		self._isEmgStop = False
		if not self.xAxis.resume():
			return
		if not self.yAxis.resume():
			return
		if not self.zAxis.resume():
			return
		if not self.rAxis.resume():
			return
		return self.dAxis.resume()
				
	def waitForIdle(self, toutMs=0):
		'等待至空闲态'
		if self._isEmgStop or not self.isConnectServer:
			return
		if not self.waitForIdleX(toutMs):
			return
		if not self.waitForIdleY(toutMs):
			return
		if not self.waitForIdleZ(toutMs):
			return
		if not self.waitForIdleR(toutMs):
			return
		return self.waitForIdleD(toutMs)
	
	def waitForIdleX(self, toutMs=0):
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.xAxis.waitForIdle(toutMs)
		
	def waitForIdleY(self, toutMs=0):
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.yAxis.waitForIdle(toutMs)
		
	def waitForIdleZ(self, toutMs=0):
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.zAxis.waitForIdle(toutMs)

	def waitForIdleR(self, toutMs=0):
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.rAxis.waitForIdle(toutMs)

	def waitForIdleD(self, toutMs=0):
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.dAxis.waitForIdle(toutMs)		
	
	# 单轴回零
	def goHomeAxisX(self,isWait=True,toutMs=0):
		'axisIdx对应的轴回零'
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.xAxis.goHome(isWait, toutMs)
			
	def goHomeAxisY(self,isWait=True,toutMs=0):
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.yAxis.goHome(isWait,toutMs)
	
	def goHomeAxisZ(self,isWait=True,toutMs=0):
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.zAxis.goHome(isWait,toutMs)
	
	def goHomeAxisR(self,isWait=True,toutMs=0):
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.rAxis.goHome(isWait,toutMs)
		
	def goHomeFastX(self,n=10):
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.xAxis.goHomeFast(n)
		
	def goHomeFastY(self,n=10):
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.yAxis.goHomeFast(n)
		
	def goHomeFastZ(self,n=10):
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.zAxis.goHomeFast(n)
		
	def goHomeFastR(self,n=10):
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.rAxis.goHomeFast(n)
		
	# 单轴定长运动
	def goTargetX(self,pos,isWait=True,isAbsolute=True):
		'单轴运动至目的坐标'
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.xAxis.goTarget(pos,isWait,isAbsolute)
		
	def goTargetY(self,pos,isWait=True,isAbsolute=True):
		'单轴运动至目的坐标'
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.yAxis.goTarget(pos,isWait,isAbsolute)
	
	def goTargetZ(self,pos,isWait=True,isAbsolute=True):
		'单轴运动至目的坐标'
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.zAxis.goTarget(pos,isWait,isAbsolute)
	
	def goTargetR(self,pos,isWait=True,isAbsolute=True):
		'单轴运动至目的坐标'
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.rAxis.goTarget(pos,isWait,isAbsolute)
	
	def goTargetD(self,pos,isWait=True,isAbsolute=True):
		'单轴运动至目的坐标'
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.dAxis.goTarget(pos,isWait,isAbsolute)

	# 单轴恒速运动
	def goConstanVelX(self,isPositive=True):
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.xAxis.goConstanVel(isPositive)
	
	def goConstanVelY(self,isPositive=True):
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.yAxis.goConstanVel(isPositive)
	
	def goConstanVelZ(self,isPositive=True):
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.zAxis.goConstanVel(isPositive)
	
	def goConstanVelR(self,isPositive=True):
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.rAxis.goConstanVel(isPositive)
	
	def goConstanVelD(self,isPositive=True):
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.dAxis.goConstanVel(isPositive)
	
	#单轴立即停止	
	def imtStopX(self):
		return self.xAxis.imtStop()
	
	def imtStopY(self):
		return self.yAxis.imtStop()
	
	def imtStopZ(self):
		return self.zAxis.imtStop()
	
	def imtStopR(self):
		return self.rAxis.imtStop()
	
	def imtStopD(self):
		return self.dAxis.imtStop()
	
	def setAutoVel(self):
		'设置自动速度'
		if self._isEmgStop or not self.isConnectServer:
			return
		if not self.waitForIdle():
			return
		if not self.xAxis.setAutoVel():
			return
		if not self.yAxis.setAutoVel():
			return
		if not self.zAxis.setAutoVel():
			return
		if not self.rAxis.setAutoVel():
			return
		return self.dAxis.setAutoVel()
		
	def setAutoVelX(self):
		if self._isEmgStop or not self.isConnectServer:
			return False
		if not self.waitForIdleX():
			return False
		return self.xAxis.setAutoVel()
		
	def setAutoVelY(self):
		if self._isEmgStop or not self.isConnectServer:
			return False
		if not self.waitForIdleY():
			return False
		return self.yAxis.setAutoVel()
	
	def setAutoVelZ(self):
		if self._isEmgStop or not self.isConnectServer:
			return False
		if not self.waitForIdleZ():
			return False
		return self.zAxis.setAutoVel()
	
	def setAutoVelR(self):
		if self._isEmgStop or not self.isConnectServer:
			return False
		if not self.waitForIdleR():
			return False
		return self.rAxis.setAutoVel()
	
	def setAutoVelD(self):
		if self._isEmgStop or not self.isConnectServer:
			return False
		if not self.waitForIdleD():
			return False
		return self.dAxis.setAutoVel()		
		
	#单轴设置速度
	def setVelX(self, vel):
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.xAxis.setVel(vel)
		
	def setVelY(self, vel):
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.yAxis.setVel(vel)
	
	def setVelZ(self, vel):
		if self._isEmgStop or not self.isConnectServer:
			return	
		return self.zAxis.setVel(vel)
	
	def setVelR(self, vel):
		if self._isEmgStop or not self.isConnectServer:
			return	
		return self.rAxis.setVel(vel)
	
	def setVelD(self, vel):
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.dAxis.setVel(vel)
		
	#单轴设置行程
	def setTravelRangeX(self, low, up):
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.xAxis.setTravelRange(low, up)
	
	def setTravelRangeY(self, low, up):
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.yAxis.setTravelRange(low, up)
		
	def setTravelRangeZ(self, low, up):
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.zAxis.setTravelRange(low, up)
		
	def setTravelRangeR(self, low, up):
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.rAxis.setTravelRange(low, up)
		
	def setTravelRangeD(self, low, up):
		if self._isEmgStop or not self.isConnectServer:
			return
		return self.dAxis.setTravelRange(low, up)
			 
if utility.is_test():		
	import driver.motion.mockMotorCtrl
	g_motorCtrl = driver.motion.mockMotorCtrl.mockMotorCtrl()
else:
	g_motorCtrl = None
	
def ctrl():
	global g_motorCtrl
	if not g_motorCtrl:
		g_motorCtrl = motorCtrl()
	return g_motorCtrl

def ctrlInit():
	return ctrl().goHomeFast()	
	
def test_gohome():
	mv = ctrl()
	import time
	log.debug("测试回零")
	time.sleep(3)
	assert mv.goHomeFast()
	
	log.debug("测试X回零")
	time.sleep(3)
	assert mv.goTargetX(300)
	assert mv.goHomeFastX()
	
	log.debug("测试Y回零")
	time.sleep(3)
	assert mv.goTargetY(300)
	assert mv.goHomeFastY()
	
	log.debug("测试Z回零")
	time.sleep(3)
	assert mv.goTargetZ(80)
	assert mv.goHomeFastZ()
	
	log.debug("测试R回零")
	time.sleep(3)
	assert mv.goTargetR(90)
	assert mv.goHomeFastR()
	
	log.debug("测试XYZR联动与回零")
	time.sleep(3)
	assert mv.goTargetXYZR(200,400,50,-150)
	assert mv.goHomeFast()
	
def test_move():
	import time
	mv = ctrl()
	log.debug("回零")
	time.sleep(3)
	assert mv.goHomeFast()
	log.debug("XY联动")
	time.sleep(3)
	assert mv.goTargetXY(200,100)
	assert mv.goHomeFast()
	
	log.debug("XYR联动")
	time.sleep(3)
	assert mv.goTargetXYR(300,150,45)
	
	log.debug("Z定向运动")
	time.sleep(3)
	assert mv.goTargetZ(20)
	
	log.debug("R定向运动")
	time.sleep(3)
	assert mv.goTargetR(-60,isAbsolute=False)

	x,y,z,r = mv.getCurrentPos()
	assert abs(x-300)<0.1 and abs(y-150)<0.1 and abs(z-20)<0.1 and abs(r+15)<0.1
	assert mv.goHomeFast()
	
	log.debug("XYZR联动")
	time.sleep(3)
	assert mv.goTargetXYZR(400,400,90,160)
	assert mv.goHomeFast()
	
	#急停
	log.debug("立即停止")
	time.sleep(3)
	assert mv.setVelX(50)
	assert mv.setVelY(50)
	assert mv.setVelZ(20)
	assert mv.setVelR(20)
	assert mv.goConstanVelX()
	assert mv.goConstanVelY()
	assert mv.goConstanVelZ()
	assert mv.goConstanVelR()
	time.sleep(3)
	assert mv.imtStopX()
	assert mv.imtStopY()
	assert mv.imtStopZ()
	assert mv.imtStopR()
	
	log.debug("急停与恢复")
	time.sleep(3)
	assert mv.goConstanVelX(False)
	assert mv.goConstanVelY(False)
	assert mv.goConstanVelZ(False)
	assert mv.goConstanVelR(False)
	time.sleep(3)
	assert mv.emgStop()
	assert not mv.goTargetXYZR(400,400,90,160)
	assert mv.resume()
	assert mv.setAutoVel()
	assert mv.goTargetXYZR(400,400,90,160)
	
	log.debug("回零")
	time.sleep(3)
	assert mv.goHomeFast()

def test_vectorMove():
	'测试线性插补'
	log.info("归零")
	assert ctrl().goHomeFast()
	log.info("线性XY运动-等待到位")
	assert ctrl().moveLineXY(100,20,10,isWait = True,isAbsolute = True)
	log.info("线性XYZ运动-不等待到位运行1s")
	assert ctrl().moveLineXYZ(200,50,40,20,isWait = False,isAbsolute = True)
	qtutility.qtSleep(1000)
	log.info("紧急停止")
	assert ctrl().imtStop()
	log.info("线性XY运动50,10")
	assert ctrl().moveLineXY(50,10,20,isWait = True)
	
def test_vel():
	'测试线性插补运动对单轴速度影响，结果不影响'
	log.info("归零")
	assert ctrl().goHomeFast()
	log.info("X轴速度100mm/s，移动至100mm")
	assert ctrl().setVelX(100)
	assert ctrl().goTargetX(100)
	qtutility.qtSleep(1000)
	log.info("线性插补速度10mm/s，移动至(200,0)")
	assert ctrl().moveLineXY(200,0,10,isWait = True,isAbsolute = True)
	qtutility.qtSleep(1000)
	log.info("X轴运动至0")
	assert ctrl().goTargetX(0)
	qtutility.qtSleep(1000)
	log.info("线性插补速度50mm/s，移动至(200,0)")
	assert ctrl().moveLineXY(200,0,50,isWait = True,isAbsolute = True)
	qtutility.qtSleep(1000)
	log.info("x单轴移动至0")
	assert ctrl().goTargetX(0)
	
if __name__ == "__main__":
	# test_gohome()
	# test_move()
	# test_vectorMove()
	test_vel()
	