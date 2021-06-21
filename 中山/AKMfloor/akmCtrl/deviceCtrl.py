# coding: utf-8
# author: pengshuqin
# date: 2019-10-16
# desc: 上料机对接

import os
import sys
import time
import bottle
import datetime
from functools import reduce

import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
	
import log
import local
import enhance
import mytimer
import mongodb as db
import akmCtrl.runTasks as runTasks
import akmCtrl.taskMgr as taskMgr
import utility
import remoteio.remoteioApi as ioApi
import lock as lockImp
utility.start()

s_lock = lockImp.create("IOAlarm.s_lock")
# INT1叫料-->OUT1到达信号-->INT2完成信号
# INT3出料-->OUT2到达信号-->INT4完成信号
#！叫料出料信号可能会一直存在


statusEvent = enhance.event()
statusEvent.connect(runTasks.onStatusChanged)

g_laststatus = {}
g_lastTask = {}
g_larmList = []
@mytimer.interval(500)
def _monitorDevices():
	global g_laststatus,g_lastTask,statusEvent
	# 查询设备上下两层有无未完成的任务
	for line in g_lastTask:
		for type in g_lastTask[line]:
			id = g_lastTask[line][type]
			if id:
				ret = taskMgr.get(id)
				if ret is None or ret["status"] in ["success","fail"]:
					g_lastTask[line][type] = None
	devices = _loadDevices()
	if not _checkInit(devices):
		return
	try:
		for d in devices:
			lockImp.acquire(s_lock)
			if devices[d]["isActive"] == 0 or devices[d]["io1"] in g_larmList or devices[d]["io2"] in g_larmList:
				lockImp.release(s_lock)
				time.sleep(0.1)
				continue
			lockImp.release(s_lock)
			try:
				s1 = ioApi.readDIList(devices[d]["io1"])["status"] #上板机
				if s1 is None:
					continue
				s2 = ioApi.readDIList(devices[d]["io2"])["status"] #下板机
				if s2 is None:
					continue
			except Exception as e:
				log.exception("readDIList error", e)
				continue
			s = [reduce(lambda x, y: x*y, t) for t in zip(s1,s2)]
			statusEvent.emit(devices[d]["io1"],s1)
			statusEvent.emit(devices[d]["io2"],s2)
			
			log.info(d,devices[d]["io1"],s1[0:4],devices[d]["io2"],s2[0:4])				 #线体
			if d not in g_laststatus:
				g_laststatus[d] = [] # [[0,0,0,0,0,0,0,0],[]]
				g_lastTask[d] = {"load": None,"unload": None}
			g_laststatus[d].append(s)
			if len(g_laststatus[d]) < 2:
				continue
			else:
				g_laststatus[d] = g_laststatus[d][-2:]
			
			if g_lastTask[d]["load"] and g_lastTask[d]["unload"]: 
				continue
			
			#连续三次有信号，代表一次任务
			ts = g_laststatus[d]
			st = [reduce(lambda x,y: x*y, t) for t in zip(*ts)]
			if st[0] and g_lastTask[d]["load"] is None:
				g_lastTask[d]["load"] = runTasks.addTask(d,"load",taskInfo=devices[d])
			if st[2] and g_lastTask[d]["unload"] is None:
				g_lastTask[d]["unload"] = runTasks.addTask(d,"unload",taskInfo=devices[d])
	except Exception as e:
		log.exception("monitor devices",e)
		
g_devices = None
def _loadDevices():
	global g_devices
	if g_devices:
		return g_devices
	ds = db.find("u_line_info")
	g_devices = {}
	while ds.next():
		g_devices[ds["_id"]] = {
			"loc1": ds["loc1"],
			"loc2": ds["loc2"],
			"io1": ds["io1"],
			"io2": ds["io2"],
			"line": ds["line"],
			"isActive": int(local.get("line",ds["_id"]).split(',')[0]),
			"map": ds["map"],
			"home": ds["home"],
			"type": ds["type"] #设备类型 load上板机  unload下板机
		}
	return g_devices


@mytimer.interval(10000)
def _loadDevicesAlarm():

	global g_larmList
	retAlarm = []
	ds = db.find("r_alarm", { "typeId": {"$in":[39998]}, "domain": "agv"})
	if ds:
		while ds.next():
			retAlarm.append(ds["moid"])
	lockImp.acquire(s_lock)
	g_larmList = retAlarm
	lockImp.release(s_lock)
	log.info("remoteio is alarm:",g_larmList)

#初始化所有IO
#TODO
g_init = None
def _checkInit(devices):
	global g_init
	if g_init:
		return True
	g_init = True
	for d in devices:
		if devices[d]["isActive"] == 0:
			continue

		for i in range(1, 3):
			try:
				ioId = "io%s" % i
				s = ioApi.readDOList(devices[d][ioId])["status"]
				if s is None:
					g_init = False
					continue
				if s[0] == 0 and s[1] == 0:
					continue
				time.sleep(1)
				s = ioApi.writeDOList(devices[d][ioId], "0,0")
				time.sleep(1)
				s = ioApi.readDOList(devices[d][ioId])["status"]

				if s is None:
					g_init = False
					continue
				if s[0] != 0 or s[1] != 0:
					g_init = False
			except Exception as e:
				log.exception("%s init failed" % devices[d][ioId], e)
				g_init = False
			time.sleep(1)
	g_init = True
	if g_init:
		log.info("init IO success")
	return g_init