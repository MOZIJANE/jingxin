#coding=utf-8 
# ycat			2017-08-25	  create
import sys,os

if __name__ == '__main__':
	p = os.path.dirname(__file__)
	if p != "":
		os.chdir(p)
if "../../" not in sys.path:
	sys.path.append("../../")	 
if "../../common" not in sys.path:
	sys.path.append("../../common")

import json_codec	
import utility
	
class solderCfg:
	def __init__(self):
		self.tempValue = 0				#设置温度
		self.sleep	   = 0				#休眠时间
		self.protectCurrent = 0 		#保护电流
		self.powerFactor=0				#功率因素,改不了的 
		self.compensationFactor = 0		#补偿因子 
		self.PID_Kp =0					#PID-Kp
		self.PID_Ki =0					#PID-Ki
		self.PID_Kd =0					#PID-Kd
		self.maxTempValue = 0		#最高温度
	
	@staticmethod
	def load(filename = "solder.cfg"):
		p = os.path.dirname(__file__)
		return json_codec.load_file(p+"/"+filename,tmpclass=solderCfg())
		
	def save(self,filename = "solder.cfg"):
		p = os.path.dirname(__file__)
		json_codec.dump_file(p+"/"+filename,self,add_classname=False)
	
	def __str__(self):
		return utility.str_obj(self)

def testCfg():
	s = solderCfg()
	utility.random(s)
	s.save("test1.cfg")
	s2 = solderCfg.load("test1.cfg")  
	assert utility.equal(s,s2)
	os.remove(p+"/"+"test1.cfg")
			
if __name__ == '__main__':
	testCfg()