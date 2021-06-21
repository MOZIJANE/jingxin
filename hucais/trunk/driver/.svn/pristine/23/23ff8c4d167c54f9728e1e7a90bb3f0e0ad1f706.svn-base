#coding=utf-8
# ycat			2017-08-16	  create
# 模拟设备控制
import os,sys
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)	
import driver.motion.mockMotorAxis
import enhance
			
class mockMotorCtrl(object):
	def __init__(self):
		self.locationEvent = enhance.event()
		self.xAxis = driver.motion.mockMotorAxis.motorAxis('axisX')
		self.yAxis = driver.motion.mockMotorAxis.motorAxis('axisY')
		self.zAxis = driver.motion.mockMotorAxis.motorAxis('axisZ')
		self.rAxis = driver.motion.mockMotorAxis.motorAxis('axisR')
		self.dAxis = driver.motion.mockMotorAxis.motorAxis('axisD')
	
	def isEmgStop(self):
		return False
	
	def close(self):
		pass
		
	def goHome(self,isWait=True,toutMs=0):
		return True
	
	def goHomeFast(self,xn=10,yn=10,zn=10,rn=10):
		return True
		
	def goTargetXY(self,x,y,isWait=True,isAbsolute=True):
		return True
	
	def goTargetXYZ(self,x,y,z,isWait=True,isAbsolute=True):
		return True
		
	def goTargetXYR(self,x,y,r,isWait=True,isAbsolute=True):
		return True
		
	def goTargetXYZR(self,x,y,z,r,isWait=True,isAbsolute=True):
		return True
	
	def getCurrentPos(self):
		import random as rand
		x = rand.randint(0,500) + rand.random()
		y = rand.randint(0,500)+ rand.random()
		z = rand.randint(0,100)+ rand.random()
		r = rand.randint(-150,150)+ rand.random()
		self.locationEvent.emit(x,y,z,r)
		return x,y,z,r 
	
	def decStop(self):
		pass
				
	def imtStop(self):
		pass
		
	def emgStop(self):
		pass
		
	def resume():
		pass
	
	def waitForIdle(toutMs=0):
		pass
	 
	# 单轴回零
	def goHomeAxisX(self,isWait=True,toutMs=0):
		return True
		
	def goHomeAxisY(self,isWait=True,toutMs=0):
		return True
	
	def goHomeAxisZ(self,isWait=True,toutMs=0):
		return True
	
	def goHomeAxisR(self,isWait=True,toutMs=0):
		return True
		 
	def goTargetX(self,pos,isWait=True,isAbsolute=True):
		return True
		
	def goTargetY(self,pos,isWait=True,isAbsolute=True):
		return True
	
	def goTargetZ(self,pos,isWait=True,isAbsolute=True):
		return True
	
	def goTargetR(self,pos,isWait=True,isAbsolute=True):
		return True
	
	def goTargetD(self,pos,isWait=True,isAbsolute=True):
		return True
	
	# 单轴恒速运动
	def goConstanVelX(self,isPositive=True):
		return True
	
	def goConstanVelX(self,isPositive=True):
		return True
	
	def goConstanVelX(self,isPositive=True):
		return True
	
	def goConstanVelX(self,isPositive=True):
		return True
	
	def goConstanVelX(self,isPositive=True):
		return True 
		
	#单轴设置速度
	def setVelX(self, vel):
		pass
		
	def setVelY(self, vel):
		pass
	
	def setVelZ(self, vel):
		pass
	
	def setVelR(self, vel):
		pass
	
	def setVelD(self, vel):
		pass