# coding: utf-8
# author: ives
# date: 2017-11-08
# desc: dashboard interface

import sys
import os
import json
import time
import threading


if "../../common" not in sys.path:
	sys.path.append("../../common")

if __name__ == '__main__':
	currentPath = os.path.dirname(__file__)
	if currentPath != "":
		os.chdir(currentPath)

import log
import config
import mqtt
import utility
import lock


g_dashboardObj = None


class dashboardApi:
	def __init__(self):
		self.__commonInfo = {'sender' : 'scada'}

	def initMqtt(self):
		svrIp = config.get("mqtt", "server_ip", "127.0.0.1")
		log.info("dashboardApi: init MQTT %s start." %svrIp)
		mqtt.initMqttObj(svrIp)
		log.info("dashboardApi: init MQTT %s finish." %svrIp)

	def sendMsg(self, topic, infoDic):
		infoDic.update(self.__commonInfo)
		mqtt.mqttObjSend(topic, infoDic)

	
# dashboard对象
def _dashboardObj():
	global g_dashboardObj
	if g_dashboardObj:
		return g_dashboardObj
	else:
		g_dashboardObj = dashboardApi()
		g_dashboardObj.initMqtt()
		return g_dashboardObj


# 增加sn
g_msgSn = 0
def _addMsgSn2(msgDic):
	global g_msgSn
	g_msgSn = g_msgSn + 1
	msgDic['sn'] = g_msgSn

def _addMsgSn(msgDic):
	msgDic['sn'] = utility.now_str(hasMillisecond = True)


#增加时间
def _addMsgTime(msgDic):
	msgDic['time'] = time.strftime('%H:%M:%S')


# ========================== 对 外 接 口 ==========================================
# AGV小车位置信息上报
def reportAgvLoc(agvId, x,y,a,w):
	msgDic = {'eventId': 1002, 'subId' : 0, 'moid' : agvId, "text": ('%f,%f,%f,%f' %(x, y, a, w))}
	_addMsgSn2(msgDic)
	_dashboardObj().sendMsg('scada/msg/1002', msgDic)


# 设备故障上报
def reportDeviceAlarm(deviceType, deviceId, errorCode, errorMsg):
	msgDic = {'deviceType' : deviceType, 'deviceId' : str(deviceId), 'errorCode' : str(errorCode), 'errorMsg' : errorMsg, \
		'status' : 'report'}
	_addMsgSn(msgDic)
	_addMsgTime(msgDic)
	_dashboardObj().sendMsg('scada/device/alarm', msgDic)
	_dashboardObj().sendMsg('scada/deviceAlarm', msgDic)


def reportDevAlarm(devId, errorNo, errorMsg):
	msgDic = {'eventId': 1005, 'subId' : str(errorNo), 'moid' : devId, 'text' : errorMsg}
	_addMsgSn(msgDic)
	_dashboardObj().sendMsg('scada/msg/1005', msgDic)


def clearDevAlarm(devId, errorNo):
	msgDic = {'eventId': 1006, 'subId' : str(errorNo), 'moid' : devId, 'text' : ''}
	_addMsgSn(msgDic)
	_dashboardObj().sendMsg('scada/msg/1006', msgDic)


# 设备故障清除
def clearDeviceAlarm(deviceType, deviceId, errorCode, errorMsg):
	msgDic = {'deviceType' : deviceType, 'deviceId' : str(deviceId), 'errorCode' : str(errorCode), 'errorMsg' : errorMsg, \
		'status' : 'clear'}
	_addMsgSn(msgDic)
	_addMsgTime(msgDic)
	_dashboardObj().sendMsg('scada/device/alarm', msgDic)
	_dashboardObj().sendMsg('scada/deviceAlarm', msgDic)


# ATS状态上报
def reportAtsStatus(seatId, status):
	msgDic = {'seatId' : seatId, 'status' : status}
	_addMsgSn(msgDic)
	_addMsgTime(msgDic)
	_dashboardObj().sendMsg('scada/ats/state', msgDic)
	_dashboardObj().sendMsg('scada/atsStatus', msgDic)


# 刷新作业单信息
def refreshJob(jobId, line):
	if line not in ['assemble1', 'assemble2', 'assemble3', 'test', 'pack', 'assemble401', 'assemble402', 'assemble403']:
		log.warning('[dashboardApi: refreshJob] ', 'invalid param: line %s' %(line))
		return
	msgDic = {'eventId': 1001, 'subId' : 0, 'moid' : jobId, "text": line}
	_addMsgSn2(msgDic)
	_dashboardObj().sendMsg('scada/msg/1001', msgDic)


# 产品信息上报
# dataDic 字典，包含: productId,job,areaName,seatId,status,errorCode,errorMsg,userId,userName
def reportProductInfo(dataDic):
	if len(dataDic) != 9:
		log.warning('[reportProductInfo] ', 'invalid params len %d' %(len(dataDic)))
		return
	key = ['productId','job','areaName','seatId','status','errorCode','errorMsg','userId','userName']
	for it in key:
		if it not in dataDic:
			log.warning('[reportProductInfo] ', 'can not find param %s' %(it))
			return
	
	msgDic = dataDic.copy()
	msgDic['errorCode'] = str(msgDic['errorCode'])
	_addMsgSn(msgDic)
	_addMsgTime(msgDic)
	_dashboardObj().sendMsg('scada/product/info', msgDic)


# 作业单变更通知: jobId为空，表示多个作业单
def changeJob(jobId):
	msgDic = {'job' : jobId}
	_addMsgSn(msgDic)
	_dashboardObj().sendMsg('scada/job/changed', msgDic)


#========================================== unit test ==========================================
def test_addMsg():
	msgDic = {}
	_addMsgSn(msgDic)
	print(msgDic)
	_addMsgTime(msgDic)
	print(msgDic)


def test_reportAgvLoc():
	reportAgvLoc('agv1', 1.0,2.1,3.2,4.3)
	reportAgvLoc('agv2', 1,2,3,4)


def test_deviceAlarm():
	reportDeviceAlarm('agv', '2000-01-11-3002505', 11, 'no power')
	reportDeviceAlarm('agv', '2000-01-11-3003274', 11, 'no power')
	reportDeviceAlarm('agv', '2000-01-11-3002504', 11, 'no power')
	time.sleep(3)
	clearDeviceAlarm('agv', '2000-01-11-3002505', 11, 'no power')


def test_reportAtsStatus():
	reportAtsStatus('seat37', 'running')
	time.sleep(1)

	reportAtsStatus('seat55', 'stop')
	time.sleep(1)

	reportAtsStatus('seat56', 'stop')
	time.sleep(3)


def test_reportProductInfo():
	key = ['productId','job','areaName','seatId','status','errorCode','errorMsg','userId','userName']
	dataDic = {}
	for it in key:
		dataDic[it + '2'] = it + '1'
		reportProductInfo(dataDic)

	dataDic.clear()
	for it in key:
		dataDic[it] = it + '1'
		reportProductInfo(dataDic)


def test_reportProductInfo2():
	dataDic = {'productId' : "AA17C0002217", 'job' : "300040744", "areaName" : "pack", 'seatId' : "seat1", \
		'status' : "finish",'errorCode' : "0",'errorMsg' : "",'userId' : "wangjian",'userName' : "王健"}


if __name__ == '__main__':
	pass
	# test_reportAgvLoc()
	test_reportAtsStatus()
	test_deviceAlarm()
	#test_deviceAlarm()
	#test_reportAtsStatus()
	#test_reportProductInfo2()



