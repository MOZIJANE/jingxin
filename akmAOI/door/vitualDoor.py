# coding: utf-8
# author: zaq
# date: 2021-02-23
# desc: 虚拟门

if __name__ == '__main__':
	setup.setCurPath(__file__)
import utility
import lock as lockImp
import local
import time
import log
import os
import json
import enhance
import door.switchControl as switchControl
import door.doorControl as doorControl
import door.doorControlQLZ as doorControlQLZ

# 位置信息事件
# 参数：swichId,x,y,angle
locationEvent = enhance.event()

# 位置信息事件
# 参数: swichId,targetName
targetLocEvent = enhance.event()

# 电池电量事件
# 参数: swichId
# level: [0,1]是电量范围
# ischarging: True正在充电，False未充电
batteryEvent = enhance.event()

# swich重启事件
# 参数: swichId
# rebootEvent = enhance.event()

g_lock = lockImp.create("door.lock")
g_swichList = None




def vitualDoorOpen(ip):
	if not g_swichList:
		getDoorList()
	g_swichList[ip].open()


def vitualDoorClose(ip):
	if not g_swichList:
		getDoorList()
	g_swichList[ip].close()

def vitualDoorIsLock(ip):
	if not g_swichList:
		getDoorList()
	return {"status":g_swichList[ip].isLock()}



g_cur_path = __file__


def _loadVitualDoorList():
	global g_cur_path
	proName = local.get("project", "name")
	if utility.is_test():
		proName = "test"
	file = os.path.abspath(os.path.dirname(__file__) + "/..") + "/agvCtrl/projects/" + proName + "/door.json"

	with open(file, 'r') as f:
		swichList = json.load(f)
		ret = {}
		for swichId in swichList:
			if swichList[swichId]["enable"].lower() == "false":
				continue
			ip = swichList[swichId]["ip"]
			port = swichList[swichId]["port"]
			type = int(swichList[swichId]["type"]) if "type" in swichList[swichId] else 1
			if type == 10:
				swich = vitualDoorInfo(ip)
				ret[ip] = swich
			else:
				continue
		return ret


@utility.init()
@lockImp.lock(g_lock)
def getDoorList():
	global g_swichList
	if g_swichList is None:
		g_swichList = _loadVitualDoorList()
	return g_swichList


class vitualDoorInfo:
	def __init__(self, ip):
		self.swichId = ip
		self._isLock = False

	def isAvailable(self):
		if self.isLock():
			return "locked"
		return ""

	@lockImp.lock(g_lock)
	def lock(self):
		if self._isLock:
			raise Exception(self.swichId + "上锁失败")
		log.debug("lock: ", self.swichId)
		self._isLock = True

	@lockImp.lock(g_lock)
	def unlock(self):
		self._isLock = False
		log.debug("unlock:", )

	@lockImp.lock(g_lock)
	def isLock(self):
		return self._isLock
	@lockImp.lock(g_lock)
	def open(self):
		if self._isLock:
			raise "%s虚拟门被锁"%self.swichId
		log.info("open vitualDoor %s"%self.swichId)
		self._isLock = True
	@lockImp.lock(g_lock)
	def close(self):
		log.info("close vitualDoor %s" % self.swichId)
		self._isLock = False



if __name__ == '__main__':
	pass