# coding: utf-8
# author: pengshuqin
# date: 2019-10-16
# desc: 上料机对接

import os
import sys
import time
import bottle
import datetime
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
	
import log
import local
import enhance
import mytimer
import utility
import webutility
import scadaUtility

import mongodb as db
import akmCtrl.runTasks as runTasks
import deviceCtrl
import remoteio.remoteioMgr as remoteioMgr
"""
# INT1叫料-->OUT1到达信号-->INT2完成信号
# INT3出料-->OUT2到达信号-->INT4完成信号
#！叫料出料信号可能会一直存在


statusEvent = enhance.event()
statusEvent.connect(runTasks.onStatusChanged)

def _nativeReadDI(io):
	remoteioInfo = remoteioMgr.get(io)
	result = remoteioInfo.readDIList()
	return result

def _nativeReadDO(io):
	remoteioInfo = remoteioMgr.get(io)
	result = remoteioInfo.readDOList()
	return result


def	_nativeWriteIo(io, index, value):
	remoteioInfo = remoteioMgr.get(io)
	remoteioInfo.writeIo(index, value)

g_laststatus = {}
g_lastTask = {}
@mytimer.interval(1000)
def _monitorDevices():
	global g_laststatus,g_lastTask,statusEvent
	# 查询设备上下两层有无未完成的任务
	for device in g_lastTask:
		for floor in g_lastTask[device]:
			id = g_lastTask[device][floor]
			if id:
				ret = taskMgr.get(id)
				if ret is None or ret["status"] in ["success","fail"]:
					g_lastTask[device][floor] = None
	devices = _loadDevices()
	if not _checkInit(devices):
		return
	try:
		for d in devices:
			if devices[d]["isActive"] == 0:
				continue
			s = _nativeReadDI(devices[d]["io"]) #上板机 一层IN1叫料 二层IN3出空框
			if s is None:
				continue
			statusEvent.emit(devices[d]["io"],s)
			log.info(devices[d]["io"],s)				 #下板机 一层IN1出料 二层IN3叫空框
			if d not in g_laststatus:
				g_laststatus[d] = [] # [[0,0,0,0,0,0,0,0],[]]
				g_lastTask[d] = {"floor1": None,"floor2": None}
			g_laststatus[d].append(s)
			if len(g_laststatus[d]) < 3:
				continue
			else:
				g_laststatus[d] = g_laststatus[d][-3:]
			if g_lastTask[d]["floor1"] and g_lastTask[d]["floor2"]: 
				continue
			#连续五次有信号，代表一次任务，设备无任务时可添加任务进去
			ts = g_laststatus[d]
			s = [x for x in zip(ts[0],ts[1],ts[2])]
			isOne = 1
			for x in s[0]: isOne = isOne*x
			isTwo = 1
			for x in s[2]: isTwo = isTwo*x
			if isOne and g_lastTask[d]["floor1"] is None:
				type = devices[d]["type"]+"_1"
				g_lastTask[d]["floor1"] = runTasks.addTask(d,type,taskInfo=devices[d])
			if isTwo and g_lastTask[d]["floor2"] is None:
				type = devices[d]["type"]+"_2"
				g_lastTask[d]["floor2"] = runTasks.addTask(d,type,taskInfo=devices[d])
	except Exception as e:
		log.exception("monitor devices",e)
		
		
		
g_devices = None
def _loadDevices():
	global g_devices
	if g_devices:
		return g_devices
	ds = db.find("u_loc_info")
	g_devices = {}
	while ds.next():
		g_devices[ds["_id"]] = {
			"loc1": ds["loc1"],
			"loc2": ds["loc2"],
			"io": ds["io"],
			"line": ds["line"],
			"isActive": local.getint("line",ds["line"],0),
			"map": ds["map"],
			"home": ds["home"],
			"type": ds["type"] #设备类型 load上板机  unload下板机
		}
	return g_devices
	
g_init = None
def _checkInit(devices):
	global g_init
	if g_init:
		return True
	g_init = True
	for d in devices:
		if devices[d]["isActive"] == 0:
			continue
		try:
			s = _nativeReadDO(devices[d]["io"]) 
			if s is None:
				g_init = False 
				continue
			if s[0] == 0 and s[1] == 0:
				continue
			time.sleep(1)
			if s[0] != 0:
				s = _nativeWriteIo(devices[d]["io"],1,0) 
				time.sleep(1)
			if s[1] != 0:
				s = _nativeWriteIo(devices[d]["io"],2,0) 
				time.sleep(1)
			s = _nativeReadDO(devices[d]["io"]) 
			if s is None:
				g_init = False 
				continue
			if s[0] != 0 or s[1] != 0:
				g_init = False
		except Exception as e:
			log.exception("%s init failed"%devices[d]["io"],e)
			g_init = False
		time.sleep(1)
	if g_init:
		log.info("init IO success")
	return g_init
"""
# utility.start()