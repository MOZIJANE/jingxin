#coding=utf-8
#lizhenwei		2017-08-02		create

import os,sys
import json

class motionConfig(object):
	'运动控制器的配置，包括服务器，轴，io输入，io输出'
	def __init__(self):
		# 1.加载本地配置文件json
		currentPath = os.path.dirname(__file__)	
		fpath = currentPath + "/motionConfig.cfg"
		try:
			f = open(fpath,"r")
			cfgObj = json.load(f)
			f.close()
			self.motionServerCfg = cfgObj["motionServer"]
			self.axisCfgList = cfgObj["axis"]
			self.ioInCfgList = cfgObj["ioInput"]
			self.ioOutCfgList = cfgObj["ioOutput"]
		except:
			self.configDefInit()
			self.writeConfig2file(fpath)			
		self.addType2cfg()
	
	def addType2cfg(self):
		'增加type字段'
		for k,v in self.axisCfgList.items():
				v["type"] = k
		for k,v in self.ioInCfgList.items():
			v["type"] = k
		for k,v in self.ioOutCfgList.items():
			v["type"] = k
	
	@property
	def axisCnt(self):
		return len(self.axisCfgList) 
		
	def axisConfigByAddr(self,axisAddr):
		'由轴地址获取轴的配置'
		for k,v in self.axisCfgList.items():
			if axisAddr == v["addr"]:
				return v
		
	def axisConfig(self,axisName):
		'获取某个轴的配置'
		# axisConfig("axisX") 获取x轴配置
		return self.axisCfgList[axisName]
		
	def ioInputConfigByName(self,ioName):
		'获取某个输入口的配置'
		# ioInputConfig("keyStart") 获取开始键的端口配置
		return self.ioInCfgList[ioName]
		
	def ioInputConfigByAddr(self,ioAddr):
		for ioName,cfg in self.ioInCfgList.items():
			if ioAddr != cfg["addr"]:
				continue
			return cfg
		else:
			return None
	
	def ioOutputConfigByName(self,ioName):
		'获取某个输出口的配置'
		# ioOutputConfig("cameraLight") 获取光源端口配置
		return self.ioOutCfgList[ioName]	
	
	def ioOutputConfigByAddr(self,ioAddr):
		for ioName,cfg in self.ioInCfgList.items():
			if ioAddr != cfg["addr"]:
				continue
			return cfg
		else:
			return None

	def ioOutputUnuseList(self):
		r = []
		for ioName,cfg in self.ioOutCfgList.items():
			if cfg["name"] == "未占用":
				r.append(cfg)
		return sorted(r,key=lambda x:x["addr"])
		
	def ioInputUnuseList(self):
		r = []
		for ioName,cfg in self.ioInCfgList.items():
			if cfg["name"] == "未占用":
				r.append(cfg)
		return sorted(r,key=lambda x:x["addr"])
	
	def configDefInit(self):
		'配置默认初始化'
		self.motionServerCfg = self._motionServerCfgDef()
		xcfg = self._xAxisConfigDef()
		ycfg = self._yAxisConfigDef()
		zcfg = self._zAxisConfigDef()
		rcfg = self._rAxisConfigDef()
		dcfg = self._dAxisConfigDef()
		self.axisCfgList = {"axisX":xcfg,"axisY":ycfg,\
								"axisZ":zcfg,"axisR":rcfg,"axisD":dcfg}
								
		self.ioInCfgList = self._ioInConfigDef()
		self.ioOutCfgList = self._ioOutConfigDef()
				
	def writeConfig2file(self,fpath):	
		cfgObj={}
		cfgObj["motionServer"] = self.motionServerCfg
		cfgObj["axis"] = self.axisCfgList
		cfgObj["ioInput"] = self.ioInCfgList
		cfgObj["ioOutput"] = self.ioOutCfgList
		
		f = open(fpath,"w")
		json.dump(cfgObj,f,indent=4,sort_keys=True, ensure_ascii=False)
		f.close()

	def _motionServerCfgDef(self):
		'运动控制器配置默认'
		cfg={}
		cfg["connectNo"] = 0
		cfg["connectIp"] = "192.168.5.11"
		cfg["connectType"] = 2
		cfg["connectBaud"] = 0	
		return cfg
	
	def _xAxisConfigDef(self):
		'X轴配置默认'
		cfg={}
		
		# **轴地址
		cfg["addr"] = 0
		
		# **名称
		cfg["name"] = "X轴"
		
		# 针对伺服的专用信号设置#
		#	使能信号 sevonLogic	#
		#	零相信号 EZ			#
		#	报警信号 alarm		#
		#	脉冲模式			#
		
		# 伺服专用
		cfg["sevonLogic"] = 0
		cfg["ezLogic"] = 1
		cfg["alarmEnable"] = 1
		cfg["alarmLogic"] = 1
				
		#**运动方向 positive 对应脉冲模式0，negative 对应脉冲模式2
		cfg["moveDirection"] = "negative"
		
		# **物理当量，1unit= 物理量
		cfg["physcisPerUnit"] = 0.005
		
		# 脉冲当量1
		cfg["equiv"] = 1.0
		# 反向间隙0
		cfg["backlash"] = 0
		
		# **速度曲线
		velCfg={}
		velCfg["minVel"] = 30.0
		velCfg["maxVel"] = 300.0
		velCfg["tAcc"] = 0.3
		velCfg["tDec"] = 0.3
		velCfg["stopVel"] = 0.0
		
		cfg["velConfig"] = velCfg
		
		# s段参数
		cfg["sPara"] = 0.1
		
		# **减速停止时间
		cfg["decStopTime"] = 0.1
		
		#回零
		homecfg={}
		# 原点电平0低电平
		homecfg["logic"] = 0
		# 回零方向，0负向，1正向
		homecfg["direction"] = 0
		# 回零模式：2次回零
		homecfg["mode"] = 2
		# 回零计数源：0指令计数
		homecfg["posSource"] = 0
		# **回零速度
		homecfg["lowVel"] = 30
		homecfg["highVel"] = 50
		homecfg["tAcc"] = 0.3
		homecfg["tDec"] = 0.3
		cfg["homeConfig"] = homecfg
		
		# **硬件限位
		elcfg={}
		elcfg["enable"] = 1
		elcfg["logic"] = 0
		elcfg["mode"] = 0
		cfg["elConfig"] = elcfg
		
		# **软件限位
		slcfg={}
		slcfg["enable"] = 1
		slcfg["sourceSel"] = 0
		slcfg["slAction"] = 0
		slcfg["nLimit"] = -10.0
		slcfg["pLimit"] = 500.0
		cfg["slConfig"] = slcfg
		return cfg
		
	def _yAxisConfigDef(self):
		'Y轴配置默认'
		cfg={}
		
		# 轴地址
		cfg["addr"] = 1
		
		# 名称
		cfg["name"] = "Y轴"
		
		# 伺服专用
		cfg["sevonLogic"] = 0
		cfg["ezLogic"] = 1
		cfg["alarmEnable"] = 1
		cfg["alarmLogic"] = 1
				
		#**运动方向 positive 对应脉冲模式0，negative 对应脉冲模式2
		cfg["moveDirection"] = "positive"
		
		# 物理当量，1unit=？物理量
		cfg["physcisPerUnit"] = 0.005
		
		# 脉冲当量1
		cfg["equiv"] = 1.0
		# 反向间隙0
		cfg["backlash"] = 0
		
		# 速度曲线
		velCfg={}
		velCfg["minVel"] = 50.0
		velCfg["maxVel"] = 300.0
		velCfg["tAcc"] = 0.3
		velCfg["tDec"] = 0.3
		velCfg["stopVel"] = 0.0
		
		cfg["velConfig"] = velCfg
		
		# s段参数
		cfg["sPara"] = 0.1
		
		# 减速停止时间
		cfg["decStopTime"] = 0.1
		
		#回零
		homecfg={}
		# 原点电平0低电平
		homecfg["logic"] = 0
		# 回零方向，0负向，1正向
		homecfg["direction"] = 0
		# 回零模式：2次回零
		homecfg["mode"] = 2
		# 回零计数源：0指令计数
		homecfg["posSource"] = 0
		homecfg["lowVel"] = 30
		homecfg["highVel"] = 50
		homecfg["tAcc"] = 0.3
		homecfg["tDec"] = 0.3
		cfg["homeConfig"] = homecfg
		
		# 硬件限位
		elcfg={}
		elcfg["enable"] = 1
		elcfg["logic"] = 0
		elcfg["mode"] = 0
		cfg["elConfig"] = elcfg
		
		# 软件限位
		slcfg={}
		slcfg["enable"] = 1
		slcfg["sourceSel"] = 0
		slcfg["slAction"] = 0
		slcfg["nLimit"] = -10.0
		slcfg["pLimit"] = 500.0
		cfg["slConfig"] = slcfg
		return cfg

	def _zAxisConfigDef(self):
		'Z轴配置默认'
		cfg={}
		
		# 轴地址
		cfg["addr"] = 2
		
		# 名称
		cfg["name"] = "Z轴"
		
		# 伺服专用
		cfg["sevonLogic"] = 0
		cfg["ezLogic"] = 1
		cfg["alarmEnable"] = 1
		cfg["alarmLogic"] = 1
		
		#**运动方向 positive 对应脉冲模式0，negative 对应脉冲模式2
		cfg["moveDirection"] = "negative"
		
		# 物理当量，1unit=？物理量
		cfg["physcisPerUnit"] = 0.005
		
		# 脉冲当量1
		cfg["equiv"] = 1.0
		# 反向间隙0
		cfg["backlash"] = 0
		
		# 速度曲线
		velCfg={}
		velCfg["minVel"] = 10.0
		velCfg["maxVel"] = 100.0
		velCfg["tAcc"] = 0.3
		velCfg["tDec"] = 0.3
		velCfg["stopVel"] = 0.0
		
		cfg["velConfig"] = velCfg
		
		# s段参数
		cfg["sPara"] = 0.1
		
		# 减速停止时间
		cfg["decStopTime"] = 0.1
		
		#回零
		homecfg={}
		# 原点电平0低电平
		homecfg["logic"] = 0
		# 回零方向，0负向，1正向
		homecfg["direction"] = 0
		# 回零模式：2次回零
		homecfg["mode"] = 2
		# 回零计数源：0指令计数
		homecfg["posSource"] = 0
		homecfg["lowVel"] = 10
		homecfg["highVel"] = 30
		homecfg["tAcc"] = 0.3
		homecfg["tDec"] = 0.3
		cfg["homeConfig"] = homecfg
		
		# 硬件限位
		elcfg={}
		elcfg["enable"] = 1
		elcfg["logic"] = 0
		elcfg["mode"] = 0
		cfg["elConfig"] = elcfg
		
		# 软件限位
		slcfg={}
		slcfg["enable"] = 1
		slcfg["sourceSel"] = 0
		slcfg["slAction"] = 0
		slcfg["nLimit"] = -10.0
		slcfg["pLimit"] = 100.0
		cfg["slConfig"] = slcfg
		return  cfg
			
	def _rAxisConfigDef(self):
		'R轴配置默认'
		cfg={}
		
		# 轴地址
		cfg["addr"] = 3
		
		# 名称
		cfg["name"] = "R轴"
		
		# 伺服专用
		cfg["sevonLogic"] = None
		cfg["ezLogic"] = None
		cfg["alarmEnable"] = None
		cfg["alarmLogic"] = None
		
		#**运动方向 positive 对应脉冲模式0，negative 对应脉冲模式2
		cfg["moveDirection"] = "negative"
		
		# 物理当量，1unit=？物理量
		# 每个unit代表的物理量, 6400个脉冲转360度
		cfg["physcisPerUnit"] = 360.0/6400.0
		
		# 脉冲当量1
		cfg["equiv"] = 1.0
		# 反向间隙0
		cfg["backlash"] = 0
		
		# 速度曲线
		velCfg={}
		velCfg["minVel"] = 10.0
		velCfg["maxVel"] = 90.0
		velCfg["tAcc"] = 0.3
		velCfg["tDec"] = 0.3
		velCfg["stopVel"] = 0.0
		
		cfg["velConfig"] = velCfg
		
		# s段参数
		cfg["sPara"] = 0.1
		
		# 减速停止时间
		cfg["decStopTime"] = 0.1
		
		#回零
		homecfg={}
		# 原点电平0低电平
		homecfg["logic"] = 0
		# 回零方向，0负向，1正向
		homecfg["direction"] = 1
		# 回零模式：2次回零
		homecfg["mode"] = 2
		# 回零计数源：0指令计数
		homecfg["posSource"] = 0
		homecfg["lowVel"] = 10
		homecfg["highVel"] = 30
		homecfg["tAcc"] = 0.3
		homecfg["tDec"] = 0.3
		cfg["homeConfig"] = homecfg
		
		# 硬件限位
		elcfg={}
		elcfg["enable"] = 1
		elcfg["logic"] = 0
		elcfg["mode"] = 0
		cfg["elConfig"] = elcfg
		
		# 软件限位
		slcfg={}
		slcfg["enable"] = 1
		slcfg["sourceSel"] = 0
		slcfg["slAction"] = 0
		slcfg["nLimit"] = -175
		slcfg["pLimit"] = 175.0
		cfg["slConfig"] = slcfg
		return cfg
		
	def _dAxisConfigDef(self):
		'D轴（送锡轴）配置默认'
		cfg={}
		
		# 轴地址
		cfg["addr"] = 4
		
		# 名称
		cfg["name"] = "送锡轴"
		
		# 伺服专用
		cfg["sevonLogic"] = None
		cfg["ezLogic"] = None
		cfg["alarmEnable"] = None
		cfg["alarmLogic"] = None
		
		#**运动方向 positive 对应脉冲模式0，negative 对应脉冲模式2
		cfg["moveDirection"] = "negative"
		
		# 物理当量，1unit=？物理量
		# //直径13mm， 1600 unit
		cfg["physcisPerUnit"] = 3.1415926*13/1600.0
		
		# 脉冲当量1
		cfg["equiv"] = 1.0
		# 反向间隙0
		cfg["backlash"] = 0
		
		# 速度曲线
		velCfg={}
		velCfg["minVel"] = 10.0
		velCfg["maxVel"] = 50.0
		velCfg["tAcc"] = 0.3
		velCfg["tDec"] = 0.3
		velCfg["stopVel"] = 0.0
		
		cfg["velConfig"] = velCfg
		
		# s段参数
		cfg["sPara"] = 0.1
		
		# 减速停止时间
		cfg["decStopTime"] = 0.1
		
		#回零
		homecfg={}
		# 原点电平0低电平
		homecfg["logic"] = 0
		# 回零方向，0负向，1正向
		homecfg["direction"] = 0
		# 回零模式：2次回零
		homecfg["mode"] = 2
		# 回零计数源：0指令计数
		homecfg["posSource"] = 0
		homecfg["lowVel"] = 30
		homecfg["highVel"] = 50
		homecfg["tAcc"] = 0.3
		homecfg["tDec"] = 0.3
		cfg["homeConfig"] = homecfg
		
		# 硬件限位
		#>>>>>>>>>>不限制
		elcfg={}
		elcfg["enable"] = 0
		elcfg["logic"] = 0
		elcfg["mode"] = 0
		cfg["elConfig"] = elcfg
		
		# 软件限位
		#>>>>>>>>>不限制
		slcfg={}
		slcfg["enable"] = 0
		slcfg["sourceSel"] = 0
		slcfg["slAction"] = 0
		slcfg["nLimit"] = 0.0
		slcfg["pLimit"] = 500.0
		cfg["slConfig"] = slcfg
		
		return cfg
		
	def _ioInConfigDef(self):
		'io input config def '
		'''
			端口的配置定义：
			addr：地址
			name：名字
			mode：0输入，1输出
			enLogic：有效电平，0或1
			state: 当前状态 0或1（mode=0时，只读；mode=1时读写）
		'''
		
		ioInCnt = 24
		
		keyStartCfg = {"addr":2,"name":"开始","mode":0,"enLogic":0,"state":1}
		keyStopCfg = {"addr":1,"name":"停止","mode":0,"enLogic":0,"state":1}
		keyResetCfg = {"addr":0,"name":"复位","mode":0,"enLogic":0,"state":1}
		keyEmgStopCfg = {"addr":3,"name":"急停","mode":0,"enLogic":0,"state":1}
		cfg = {"keyStart":keyStartCfg,"keyStop":keyStopCfg,"keyReset":keyResetCfg,"keyEmgStop":keyEmgStopCfg}
		
		for i in range(4,12):
			idname = "user_%d"%(i)
			tcfg = {"addr":i,"name":"未占用","mode":0,"enLogic":0,"state":1}
			cfg[idname] = tcfg
		
		airUpCfg = {"addr":12,"name":"气缸上","mode":0,"enLogic":0,"state":0}
		airDownCfg={"addr":13,"name":"气缸下","mode":0,"enLogic":0,"state":1}
		
		collisionCfg={"addr":14,"name":"撞击告警","mode":0,"enLogic":0,"state":1}
		
		lackWireCfg={"addr":15,"name":"缺锡","mode":0,"enLogic":0,"state":1}
		blockWireCfg={"addr":16,"name":"堵锡","mode":0,"enLogic":0,"state":1}
		
		cfg["airUp"] = airUpCfg
		cfg["airUp"] = airUpCfg
		cfg["airDown"] = airDownCfg
		cfg["collision"] = collisionCfg
		cfg["lackWire"] = lackWireCfg
		cfg["blockWire"] = blockWireCfg
				
		for i in range(17,ioInCnt):
			idname = "user_%d"%(i)
			tcfg = {"addr":i,"name":"未占用","mode":0,"enLogic":0,"state":1}
			cfg[idname] = tcfg
		
		return cfg
	
	def _ioOutConfigDef(self):
		'io out config def '
		
		ioOutCnt = 18
		cameraLight = {"addr":0, "name":"光源", "mode":1, "enLogic":0, "state":1}
		# 烙铁头上的气缸
		ironAir = {"addr":1, "name":"气缸", "mode":1, "enLogic":0, "state":1}
		# 吹气，用于清洗
		cleanAir = {"addr":2, "name":"吹气", "mode":1, "enLogic":0, "state":1}
		
		cfg = {"cameraLight":cameraLight, "ironAir":ironAir, "cleanAir":cleanAir}

		for i in range(3,ioOutCnt):
			idname = "user_%d"%(i)
			tcfg = {"addr":i,"name":"未占用","mode":1,"enLogic":0,"state":1}
			cfg[idname] = tcfg
				
		return cfg
	
g_motionCfg = None

def cfg():
	global g_motionCfg
	if not g_motionCfg:
		g_motionCfg = motionConfig()
	return g_motionCfg


def test_config():
	xcfg = g_motionCfg.axisConfig("axisX")
	assert(xcfg!=None)
	
	
if __name__=="__main__":
	test_config()
