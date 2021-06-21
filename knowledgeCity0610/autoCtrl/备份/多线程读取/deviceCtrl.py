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
import threading
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
	
import log
import local
import enhance
import mytimer

import mongodb as db
import runTasks
import taskMgr
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

@utility.init()
def monitor():
	devices = _loadDevices()
	time.sleep(10)
	for group in devices:
		thread = threading.Thread(target=monitorLine,args=(group,devices[group]))
		thread.start()
	
def monitorLine(group,devices):
	global statusEvent
	m_laststatus = {}
	m_lastTask = {}
	time.sleep(5)
	while True:
		for line in m_lastTask:
			for type in m_lastTask[line]:
				id = m_lastTask[line][type]
				if id:
					ret = taskMgr.get(id)
					if ret is None or ret["status"] in ["success","fail"]:
						m_lastTask[line][type] = None
		if not _checkInit(group,devices):
			return
		try:
			for d in devices:
				lockImp.acquire(s_lock)
				if devices[d]["isActive"] == 0 or devices[d]["io1"] in g_larmList or devices[d]["io2"] in g_larmList:
					lockImp.release(s_lock)
					time.sleep(1)
					continue
				lockImp.release(s_lock)
				s1 = ioApi.readDIList(devices[d]["io1"])["status"] #上板机 
				if s1 is None:
					continue
				s2 = ioApi.readDIList(devices[d]["io2"])["status"] #下板机 
				if s2 is None:
					continue
				s = [reduce(lambda x, y: x*y, t) for t in zip(s1,s2)]
				statusEvent.emit(devices[d]["io1"],s1)
				statusEvent.emit(devices[d]["io2"],s2)
				
				log.info(d,devices[d]["io1"],s1[0:4],devices[d]["io2"],s2[0:4])				 #线体
				if d not in m_laststatus:
					m_laststatus[d] = [] # [[0,0,0,0,0,0,0,0],[]]
					m_lastTask[d] = {"load": None,"unload": None}
				m_laststatus[d].append(s)
				if len(m_laststatus[d]) < 3:
					continue
				else:
					m_laststatus[d] = m_laststatus[d][-3:]
				
				if m_lastTask[d]["load"] and m_lastTask[d]["unload"]: 
					continue
				
				#连续三次有信号，代表一次任务
				ts = m_laststatus[d]
				st = [reduce(lambda x,y: x*y, t) for t in zip(*ts)]
				if st[0] and m_lastTask[d]["load"] is None:
					m_lastTask[d]["load"] = runTasks.addTask(d,"load",taskInfo=devices[d])
				if st[2] and m_lastTask[d]["unload"] is None:
					m_lastTask[d]["unload"] = runTasks.addTask(d,"unload",taskInfo=devices[d])
				time.sleep(0.5)
		except Exception as e:
			log.exception("readIo fail",e)
			time.sleep(1)
			continue

g_devices = None
# {"group1": {"line1": {...},"line1": {...}}}
def _loadDevices():
	global g_devices
	if g_devices:
		return g_devices
	ds = db.find("u_line_info")
	g_devices = {}
	while ds.next():
		temp = {
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
		if ds["group"] not in g_devices:
			g_devices[ds["group"]] = {}
		g_devices[ds["group"]][ds["_id"]] = temp
	return g_devices


@mytimer.interval(5000)
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
g_init = {}
def _checkInit(group,devices):
	global g_init
	if group in g_init and g_init[group]:
		return True
	g_init[group] = True
	for d in devices:
		if devices[d]["isActive"] == 0:
			continue
			
		for i in range(1,3):
			try:
				ioId = "io%s"%i
				s = ioApi.readDOList(devices[d][ioId])["status"]
				if s is None:
					g_init[group] = False 
					continue
				if s[0] == 0 and s[1] == 0:
					continue
				time.sleep(1)
				s = ioApi.writeDOList(devices[d][ioId],"0,0")
				time.sleep(1)
				s = ioApi.readDOList(devices[d][ioId])["status"]
				
				if s is None:
					g_init[group] = False 
					continue
				if s[0] != 0 or s[1] != 0:
					g_init[group] = False
			except Exception as e:
				log.exception("%s init failed"%devices[d][ioId],e)
				g_init[group] = False
			time.sleep(1)
		g_init[group] = True
	if g_init[group]:
		log.info("init IO success")
	return g_init[group]
	