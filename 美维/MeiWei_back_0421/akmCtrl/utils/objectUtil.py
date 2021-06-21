#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @Time : 2021/4/20 15:43
# @Author : XiongLue Xie
# @File : objectUtil.py
# @desciption : 获取一个单例的对象可以统一写到这里

from beans import scadaTaskMgrBean
import log


global G_allowNext
G_allowNext = {}

global g_taskMgr
g_taskMgr =  scadaTaskMgrBean.scadaTaskMgr()

global buttonTask
buttonTask = False

def setButtonTask(boolenValue):
	global buttonTask
	buttonTask = boolenValue

def getButtonTask():
	return buttonTask

#对应放行的工位点位置
global seats
seats = {"bt_1":0,"bt_2":0,"bt_3":0}    #单个按钮盒子（代表三个放行按键）时候用

btPrefix = "bt_"
zlan = "ZLAN01"     #修改成从remoteio.json中读取
checkTimes = 15   #检测zlan信号次数，用于与机器交互
taskTypeUnload = "unload"
zlanSignIterationInterval = 0.5
simulationValuesOfZlan = {"status":[0,0,1,0,0,0,0,0]}  #测试用的假返回值

btnMachineNum = 3

def getBtnMachineNum():
	'''获取按钮盒子的数量'''
	return btnMachineNum

def getBtnPrefix():
	'''获取按钮前缀'''
	return btPrefix

def getSimulationValuesOfZlan():
	return simulationValuesOfZlan

def getZlanSignIterationInterval():
	return zlanSignIterationInterval

def getTaskTypeUnload():
	return taskTypeUnload

def getCheckTimes():
	return  checkTimes

def getLan():
	return zlan

def getSeats():
	return seats

#按下按钮修改相应的位置1，其余全0
def setSeatsByBt(bt):
	try:
		btKey = btPrefix + bt
		for tempKey in seats.keys():
			if btKey == tempKey:
				seats[btKey] = 1
			else:
				seats[tempKey] = 0
		log.info("********按钮值********:", getSeats())
	except Exception  as e:
		log.info("按钮值:",btKey,"修改异常：",e)



def setAllownext(devID,sig):
	G_allowNext[devID] = sig



def g_allowNext():
	return G_allowNext

def getG_taskMgr():
	return g_taskMgr