#coding=utf-8
#lizhenwei		2017-08-01		create
import os,sys,platform
import ctypes
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
	
import driver.motion.motionConfig

# 0.读取控制服务器配置
serverCfg = driver.motion.motionConfig.cfg().motionServerCfg

# 1.load dll
if "32bit" == platform.architecture()[0]:
	dllpath = os.path.dirname(__file__)+"/dll/win32/LTSMC.dll"
else:
	dllpath = os.path.dirname(__file__)+"/dll/win64/LTSMC.dll"
g_smcdll = ctypes.windll.LoadLibrary(dllpath)
assert(g_smcdll)
g_isConnect = False
# 2.motionserver var
connectNo = ctypes.c_int(serverCfg["connectNo"])
connectType = ctypes.c_int(serverCfg["connectType"])
connectIp = ctypes.c_char_p(serverCfg["connectIp"].encode('utf-8'))
connectBaud = ctypes.c_ushort(serverCfg["connectBaud"])

def setConnectTimeout(ms=1000):
	global g_smcdll
	return g_smcdll.smc_set_connect_timeout(ms)
	
def connectServer():
	global g_smcdll,connectNo,connectType,connectIp,connectBaud,g_isConnect
	rt = g_smcdll.smc_board_init(connectNo,connectType,connectIp,connectBaud)
	if 0 == rt:
		g_isConnect = True
	return rt
	
def disConnectServer():
	global g_smcdll,connectNo,g_isConnect
	g_isConnect = False
	return g_smcdll.smc_board_close(connectNo)
	
def writeServonPin(axis,logic):
	'控制指定轴的伺服使能端口的输出'
	global g_smcdll,connectNo,g_isConnect
	# axis: int
	# logic: int,0低电平，1高电平
	# smc_write_sevon_pin(WORD ConnectNo,WORD axis,WORD on_off)
	if not g_isConnect:
		return
	return g_smcdll.smc_write_sevon_pin(connectNo,axis,logic)
	
def setPulseOutmode(axis,outmode):
	'设置指定轴的脉冲输出模式'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	return g_smcdll.smc_set_pulse_outmode(connectNo,axis,outmode)
	
def setEquiv(axis,equiv):
	'设置脉冲当量'
	#equiv:double
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	equiv = ctypes.c_double(equiv)
	return g_smcdll.smc_set_equiv(connectNo,axis,equiv)
	
def setBacklash(axis,backlash):
	'设置反向间隙'
	#backlash:double
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	backlash = ctypes.c_double(backlash)
	return g_smcdll.smc_set_backlash_unit(connectNo,axis,backlash)
		
def setProfileUnit(axis,minVel,maxVel,tAcc,tDec,stopVel):
	'设置单轴运动速度曲线'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	# WORD ConnectNo,WORD axis,double Min_Vel,double Max_Vel,double Tacc,double Tdec,double Stop_Vel
	minVel = ctypes.c_double(minVel)
	maxVel = ctypes.c_double(maxVel)
	tAcc = ctypes.c_double(tAcc)
	tDec = ctypes.c_double(tDec)
	stopVel = ctypes.c_double(stopVel)
	return g_smcdll.smc_set_profile_unit(connectNo,axis,minVel,maxVel,tAcc,tDec,stopVel)
	
def setSprofile(axis,sPara):
	'设置单轴速度曲线S段平滑时间参数'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	#smc_set_s_profile(WORD ConnectNo,WORD axis,WORD s_mode,double s_para)
	sPara = ctypes.c_double(sPara)
	return g_smcdll.smc_set_s_profile(connectNo,axis,0,sPara)
	
def setDecStopTime(axis,sec):
	'设置定长运动减速停止时间'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	# smc_set_dec_stop_time(WORD ConnectNo,WORD axis,double time)
	sec = ctypes.c_double(sec)
	return g_smcdll.smc_set_dec_stop_time(connectNo,axis,sec)
	
def changeSpeedUnit(axis,newVel,tAccDec):
	'在线改变指定轴的当前运动速度'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	# smc_change_speed_unit(WORD ConnectNo,WORD axis, double New_Vel,double Taccdec)
	newVel = ctypes.c_double(newVel)
	tAccDec = ctypes.c_double(tAccDec)
	return g_smcdll.smc_change_speed_unit(connectNo,axis,newVel,tAccDec)

def getCurrentSpeedUnit(axis):
	'读取轴当前速度'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	# smc_read_current_speed_unit(WORD ConnectNo,WORD axis, double *current_speed)
	curSpeed = ctypes.c_double(0)
	rt = g_smcdll.smc_read_current_speed_unit(connectNo, axis, ctypes.byref(curSpeed))	
	if 0 == rt:
		return abs(curSpeed.value)

def setHomePinLogic(axis,orgLogic):
	'设置ORG原点信号'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	# smc_set_home_pin_logic(WORD ConnectNo,WORD axis,WORD org_logic,double filter)
	fter = ctypes.c_double(0.0)
	return g_smcdll.smc_set_home_pin_logic(connectNo,axis,orgLogic,fter)

def setHomeMode(axis,homeDir,homeMode=2,posSource=0):
	'设置回原点模式'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	# smc_set_homemode(WORD ConnectNo,WORD axis,WORD home_dir,double vel_mode,WORD mode,WORD pos_source);
	# posSource回零计数源: 0：指令计数器，1：编码计数器
	velmode = ctypes.c_double(1.0)
	return g_smcdll.smc_set_homemode(connectNo, axis, homeDir,velmode,homeMode,posSource)

def setHomePositionUnit(axis,enable=2,position=0):
	'回零完成后设置位置'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	position = ctypes.c_double(0.0)
	# smc_set_home_position_unit(WORD ConnectNo,WORD axis,WORD enable,double position)
	# enable 使能参数 0：禁止。 1: 先清0，然后运动到指定位置（相对位置）。 2: 先运动到指定位置（相对位置），再清0
	# position 设置回原点位置
	return g_smcdll.smc_set_home_position_unit(connectNo, axis,enable,position)
	
def setHomeProfileUnit(axis,lowVel,highVel,tAcc,tDec):
	'设置回原点速度参数'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	# smc_set_home_profile_unit(WORD ConnectNo,WORD axis,double Low_Vel,double High_Vel,double Tacc,double Tdec)
	lowVel = ctypes.c_double(lowVel)
	highVel = ctypes.c_double(highVel)
	tAcc = ctypes.c_double(tAcc)
	tDec = ctypes.c_double(tDec)
	return g_smcdll.smc_set_home_profile_unit(connectNo,axis,lowVel,highVel,tAcc,tDec)
	
def setEmgMode(axis,enable,emgLogic):
	'设置EMG急停信号'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	# smc_set_emg_mode(WORD ConnectNo,WORD axis,WORD enable,WORD emg_logic)
	return g_smcdll.smc_set_emg_mode(connectNo,axis,enable,emgLogic)
	
def setElMode(axis,enable,elLogic,elMode):
	'设置EL限位信号，即硬件限位'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	# smc_set_el_mode(WORD ConnectNo,WORD axis,WORD enable,WORD el_logic,WORD el_mode)
	'''
		enable 0：正负限位禁止 1：正负限位允许 2：正限位禁止、负限位允许 3：正限位允许、负限位禁止
		elLogic 0：正负限位低电平有效 1：正负限位高电平有效 2：正限位低有效，负限位高有效 3：正限位高有效，负限位低有效
		elMode 0：正负限位立即停止 1：正负限位减速停止 2：正限位立即停止，负限位减速停止 3：正限位减速停止，负限位立即停止
	'''
	return g_smcdll.smc_set_el_mode(connectNo,axis,enable,elLogic,elMode)
	
def setSoftLimitUnit(axis,enable,sourceSel,slAction,nLimit,pLimit):
	'设置软限位'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return	
	# smc_set_softlimit_unit(WORD ConnectNo,WORD axis,WORD enable, WORD source_sel,WORD SL_action, double N_limit,double P_limit)
	'''
		enable 使能状态，0：禁止，1：允许
		sourceSel 计数器选择，0：指令位置计数器，1：编码器计数器
		slAction 限位停止方式，0：立即停止，1：减速停止
		nLimit 负限位位置，单位：unit
		pLimit 正限位位置，单位：unit
	'''
	nLimit = ctypes.c_double(nLimit)
	pLimit = ctypes.c_double(pLimit)
	return g_smcdll.smc_set_softlimit_unit(connectNo,axis,enable,sourceSel,slAction,nLimit,pLimit)
	
def homeMove(axis):
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	return g_smcdll.smc_home_move(connectNo,axis)
	
def getHomeResult(axis):
	'读取回原点运动状态'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	# state：0-未完成，1-完成
	# smc_get_home_result(WORD ConnectNo,WORD axis,WORD* state)
	state = ctypes.c_ushort(0)
	g_smcdll.smc_get_home_result(connectNo,axis,ctypes.byref(state))
	return state.value
	
def setPositionUnit(axis,pos):
	'设置当前指令位置计数器值'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	# smc_set_position_unit(WORD ConnectNo,WORD axis, double pos
	tpos = ctypes.c_double(pos)
	return g_smcdll.smc_set_position_unit(connectNo,axis,tpos)
	
def getPositionUnit(axis):
	'读取当前指令位置计数器值'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	# smc_get_position_unit(WORD ConnectNo,WORD axis, double * pos)
	pos = ctypes.c_double(0)
	g_smcdll.smc_get_position_unit(connectNo,axis,ctypes.byref(pos))
	return pos.value
	
def pmoveUnit(axis,dist,posiMode):
	'定长运动'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	# smc_pmove_unit(WORD ConnectNo,WORD axis,double Dist,WORD posi_mode)
	dist = ctypes.c_double(dist)
	return g_smcdll.smc_pmove_unit(connectNo,axis,dist,posiMode)
	
def vmove(axis,dir):
	'恒速运动'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	# smc_vmove(WORD ConnectNo,WORD axis,WORD dir)
	return g_smcdll.smc_vmove(connectNo,axis,dir)

def checkDone(axis):
	'检测指定轴的运动状态'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	# smc_check_done(WORD ConnectNo,WORD axis)
	return g_smcdll.smc_check_done(connectNo,axis)
	
def emgStop():
	'紧急停止所有轴'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return	
	# smc_emg_stop(WORD ConnectNo)
	return g_smcdll.smc_emg_stop(connectNo)
	
def stop(axis,stopMode):
	'指定轴停止运动'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return	
	# 0：减速停止，1：立即停止
	# smc_stop(WORD ConnectNo,WORD axis,WORD stop_mode)
	return g_smcdll.smc_stop(connectNo, axis,stopMode)
		
def readOutbit(bitno):
	'读取指定控制器的某个输出端口的电平'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	# smc_read_outbit(WORD ConnectNo,WORD bitno)
	# bitno 输入端口号，取值范围： 0~控制器最大输入端口数-1
	return g_smcdll.smc_read_outbit(connectNo,bitno)
	
def writeOutbit(bitno,state):
	'设置指定控制器的某个输出端口的电平'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	# smc_write_outbit(WORD ConnectNo,WORD bitno,WORD on_off)
	# bitno 输入端口号，取值范围： 0~控制器最大输入端口数-1 on_off输出电平，0：低电平，1：高电平
	return g_smcdll.smc_write_outbit(connectNo,bitno,state)
		
def readOutPort(portno):
	'读取指定控制器的全部输出口的电平'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	# smc_read_outport(WORD ConnectNo,WORD portno)
	# portno IO组号，取值范围： SMC604A：0~1, 其它控制器为0
	# 返回值：各IO口的bit值
	# 注意：在IO口在32位内PORT号为0.超出32位PORT为1。返回值为10进制，转换为2进制后bit值对应各端口输出状态值。
	return g_smcdll.smc_read_outport(connectNo,portno)
	
def writeOutPort(portno,portval):
	'设置指定控制器的全部输出口的电平'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	# smc_write_outport(WORD ConnectNo,WORD portno,DWORD outport_val);
	# 参 数：
	# ConnectNo 指定链接号：0-7,默认值0 
	# portno IO组号，取值范围： SMC604A：0~1, 其它控制器为0 port_value 输入端口电平数值 
	# 返回值：错误代码
	return g_smcdll.smc_write_outport(connectNo,portno,portval)
	
def readInbit(bitno):
	'读取指定控制器的某个输入端口的电平'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	# smc_read_inbit(WORD ConnectNo,WORD bitno)
	return g_smcdll.smc_read_inbit(connectNo,bitno)
	
def readInport(portno):
	'读取指定控制器的全部输入端口的电平'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	# smc_read_inport(WORD ConnectNo,WORD portno)
	return g_smcdll.smc_read_inport(connectNo,portno)

def getStopReason(axis):
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	rn = ctypes.c_long(0)
	rt = g_smcdll.smc_get_stop_reason(connectNo,axis,ctypes.byref(rn))
	if 0==rt:
		return rn.value	
	
def clearStopReason(axis):
	global g_smcdll,connectNo
	return g_smcdll.smc_clear_stop_reason(connectNo,axis)
	
def setEZmode(axis, ezLogic):
	'设置指定轴的 EZ 信号电平'
	global g_smcdll,connectNo,g_isConnect
	if not g_isConnect:
		return
	filter = ctypes.c_double(0)
	return g_smcdll.smc_set_ez_mode(connectNo,axis,ezLogic,0,filter)
	
def setAlarmMode(axis, enable, logic):
	'设置指定轴的 ALM 信号'
	# smc_set_alm_mode(WORD ConnectNo,WORD axis,WORD enable,WORD alm_logic,WORD alm_action)
	global g_smcdll, connectNo,g_isConnect
	if not g_isConnect:
		return
	return g_smcdll.smc_set_alm_mode(connectNo, axis, enable, logic,0)
	
def readAxisIOStatus(axis):
	'读取指定轴有关运动信号的状态'
	# DWORD smc_axis_io_status(WORD ConnectNo,WORD axis)
	global g_smcdll, connectNo,g_isConnect
	if not g_isConnect:
		return
	return g_smcdll.smc_axis_io_status(connectNo, axis)
	
def setVectorProfileUnit(crd,minVel,maxVel,tAcc,tDec,stopVel):
	'设置插补运动速度参数'
	# smc_set_vector_profile_unit(WORD ConnectNo,WORD Crd,double Min_Vel,double Max_Vel,double Tacc,double Tdec,double Stop_Vel)
	# crd 为坐标系号
	global g_smcdll, connectNo, g_isConnect
	if not g_isConnect:
		return None
	minVel = ctypes.c_double(minVel)
	maxVel = ctypes.c_double(maxVel)
	tAcc = ctypes.c_double(tAcc)
	tDec = ctypes.c_double(tDec)
	stopVel = ctypes.c_double(stopVel)
	return g_smcdll.smc_set_vector_profile_unit(connectNo, crd, minVel, maxVel,tAcc,tDec,stopVel)
	
def setVectorSProfile(crd, sPara):
	'设置插补运动S段参数'
	# smc_set_vector_s_profile(WORD ConnectNo,WORD Crd,WORD s_mode,double s_para)
	global g_smcdll, connectNo, g_isConnect
	if not g_isConnect:
		return None
	sPara = ctypes.c_double(sPara)
	return g_smcdll.smc_set_s_profile(connectNo, crd,0,sPara)
	
def setVectorDecStopTime(crd,t):
	'设置插补运动减速停止时间'
	global g_smcdll, connectNo, g_isConnect
	if not g_isConnect:
		return None
	# smc_set_vector_dec_stop_time(WORD ConnectNo,WORD Crd,double time)
	t = ctypes.c_double(t)
	return g_smcdll.smc_set_vector_dec_stop_time(connectNo, crd, t)
	
def lineUnit(crd,axisCnt,axisList,posList,mode):
	'线性插补'
	# smc_line_unit(WORD ConnectNo,WORD Crd,WORD AxisNum,WORD* AxisList,double* Dist,WORD posi_mode)
	# mode=0: 相对坐标; mode=1：绝对坐标
	global g_smcdll, connectNo, g_isConnect
	if not g_isConnect:
		return None
	axis = (ctypes.c_ushort * axisCnt)()
	for i,a in enumerate(axisList):
		axis[i] = a
	pos = (ctypes.c_double*axisCnt)()
	for i,p in enumerate(posList):
		pos[i] = p
	return g_smcdll.smc_line_unit(connectNo,crd,axisCnt,axis,pos,mode)
	
def checkDoneMulticoor(crd):
	'检测连续插补运行状态'
	# smc_check_done_multicoor(WORD ConnectNo,WORD Crd)
	global g_smcdll, connectNo, g_isConnect
	if not g_isConnect:
		return None
	return g_smcdll.smc_check_done_multicoor(connectNo, crd)
	
def stopMulticoor(stopMode):
	'停止坐标系内所有轴的运动'
	# smc_stop_multicoor(WORD ConnectNo,WORD Crd,WORD stop_mode) #0减速停止，1加速停止
	global g_smcdll, connectNo, g_isConnect
	if not g_isConnect:
		return None
	return g_smcdll.smc_stop_multicoor(connectNo, crd, stopMode)