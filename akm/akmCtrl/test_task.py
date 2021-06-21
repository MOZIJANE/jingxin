import os 
import sys
import time
import setup

if __name__ == '__main__':
	setup.setCurPath(__file__)
	
import log
import webutility
import utility

import agvDevice.rollerApi as rollerApi

import remoteio.remoteioApi as ioApi


def test_task1():
	#顺序： 工位1上料-》工位2上料 -》工位1下料 -》工位2下料
	# INT1叫料-->OUT1到达信号-->INT2完成信号
	# INT3出料-->OUT2到达信号-->INT4完成信号
	
	agvId = "AGV01"
	#io、type、叫料、到达、完成
	testTasks = [["ZLAN01","load",0,1,1],["ZLAN02","load",0,1,1],["ZLAN01","unload",2,2,3],["ZLAN02","unload",2,2,3]]
	
	for task in testTasks:
		id = task[0]
		if task[1] == "unload": #类型
			rollerApi.rollerFrontUnload(agvId,2)
		else:
			rollerApi.rollerFrontLoad(agvId,1)
		
		ioApi.writePeerIo(id,task[2],0) #叫料信号
		time.sleep(1)
		ioApi.writePeerIo(id,task[2],1) #叫料信号
		
		while True:
			device_status = ioApi.readPeerIo(id)["status"]
			if device_status[task[3]]:  #到达信号
				ioApi.writePeerIo(id,task[2],0) #清除叫料信号
				break
			time.sleep(1)
		time.sleep(1)
		ioApi.writePeerIo(id,task[4],1) #完成信号
		time.sleep(4)
		ioApi.writePeerIo(id,task[4],0) ##清除完成信号
		
def test_task24():
	# INT1叫料-->OUT1到达信号-->INT2完成信号 一层
	#         -->OUT2到达信号-->INT4完成信号 二层
	
	agvId = "AGV01"
	id = "ZLAN03"
	rollerApi.rollerFrontLoad(agvId,1)
	rollerApi.rollerFrontUnload(agvId,2)
	
	ioApi.writePeerIo(id,0,1) #叫料信号 INT1
	
	while True:
		device_status = ioApi.readPeerIo(id)["status"]
		if device_status[1] and device_status[2]:  #到达信号
			ioApi.writePeerIo(id,0,0) #清除叫料信号
			break
		time.sleep(1)
	time.sleep(1)
	ioApi.writePeerIo(id,1,1) #INT2完成信号
	ioApi.writePeerIo(id,3,1) #INT4完成信号
	time.sleep(4)
	ioApi.writePeerIo(id,1,0) ##清除完成信号
	ioApi.writePeerIo(id,3,0)
	
def test_task28():
	#下板机ZLAN01 INT1出料 OUT1到达信号--INT2完成信号
	#上板机ZLAN02 INT1叫料 OUT1到达信号--INT2完成信号
	#			  INT3出框 OUT2到达信号--INT4完成信号
	#下板机ZLAN01 INT3叫框 OUT2到达信号--INT4完成信号
	
	agvId = "AGV02"
	id1 = "ZLAN02"
	id2 = "ZLAN01"
	# rollerApi.rollerFrontLoad(agvId,1)
	# rollerApi.rollerFrontUnload(agvId,2)
	# 下板机 出料
	# ioApi.writePeerIo(id1,0,1) #出料信号 INT1
	# ioApi.writePeerIo(id2,0,1) #叫料信号 INT1
	# ioApi.writePeerIo(id1,2,1) #叫框信号 INT3
	# time.sleep(1)
	# ioApi.writePeerIo(id2,2,1) #出框信号 INT3
	# time.sleep(1)
	# ioApi.writePeerIo(id1,0,1) #出料信号 INT1
	# return
	# ioApi.writePeerIo(id1,0,1) #出料信号 INT1
	# while True:
		# device_status = ioApi.readPeerIo(id1)["status"]
		# if device_status[1]:  #到达信号
			# ioApi.writePeerIo(id1,0,0) #清除出料信号
			# break
		# time.sleep(1)
	# time.sleep(1)
	# ioApi.writePeerIo(id1,1,1) #INT2完成信号
	# time.sleep(4)
	# ioApi.writePeerIo(id1,1,0) ##清除完成信号
	# return
	
	# 上板机 叫料
	# ioApi.writePeerIo(id2,0,1) #叫料信号 INT1
	# while True:
		# device_status = ioApi.readPeerIo(id2)["status"]
		# if device_status[1]:  #到达信号
			# ioApi.writePeerIo(id2,0,0) #清除叫料信号
			# break
		# time.sleep(1)
	# time.sleep(1)
	# ioApi.writePeerIo(id2,1,1) #INT2完成信号
	# time.sleep(4)
	# ioApi.writePeerIo(id2,1,0) #清除完成信号
	# return
	# 上板机 出框
	# ioApi.writePeerIo(id2,2,1) #出框信号 INT3
	# while True:
		# device_status = ioApi.readPeerIo(id2)["status"]
		# if device_status[2]:  #到达信号 OUT2
			# ioApi.writePeerIo(id2,2,0) #清除出框信号
			# break
		# time.sleep(1)
	# time.sleep(1)
	# ioApi.writePeerIo(id2,3,1) #INT4完成信号
	# time.sleep(4)
	# ioApi.writePeerIo(id2,3,0) #清除完成信号
	# return
	# 下板机 叫框
	# ioApi.writePeerIo(id1,2,1) #叫框信号 INT3
	while True:
		device_status = ioApi.readPeerIo(id1)["status"]
		if device_status[2]:  #到达信号 OUT2
			# ioApi.writePeerIo(id1,2,0) #清除叫框信号
			break
		time.sleep(1)
	time.sleep(1)
	ioApi.writePeerIo(id1,3,1) #INT4完成信号
	time.sleep(4)
	ioApi.writePeerIo(id1,3,0) #清除完成信号
	
def test_tasks():
	# 测试添加任务 无AGV可用
	id1 = "ZLAN02"
	id2 = "ZLAN01"
	ioApi.writePeerIo(id1,0,1) #出料信号 INT1
	# ioApi.writePeerIo(id1,2,1) #叫框信号 INT3
	# ioApi.writePeerIo(id2,2,1) #出框信号 INT3
	# ioApi.writePeerIo(id2,0,1) #叫料信号 INT1
	# time.sleep(12)
	# ioApi.writePeerIo(id1,0,0) #出料信号 INT1
	# ioApi.writePeerIo(id1,2,0) #叫框信号 INT3
	# ioApi.writePeerIo(id2,2,0) #出框信号 INT3
	# ioApi.writePeerIo(id2,0,0) #叫料信号 INT1
	
def test_agv():
	import time
	
	ioList = ["load001","unload001"]
	for io in ioList:
		ioApi.writeDIList(io,'1,0,1,0,0,0,0,0')
	time.sleep(1)
	a = {
		"load001": {"isFinish1": False,"isFinish2": False},
		"unload001": {"isFinish1": False,"isFinish2": False}
	}
	while True:
		for io in ioList:
			if a[io]["isFinish1"] and a[io]["isFinish2"]:
				continue
			s = ioApi.readDOList(io)["status"]
			if not a[io]["isFinish1"] and s[1] == 1:
				ioApi.writeDI(io,1,1)
				a[io]["isFinish1"] = True
				time.sleep(4)
				ioApi.writeDI(io,1,0)
			if not a[io]["isFinish2"] and s[2] == 1:
				a[io]["isFinish2"] = True
				ioApi.writeDI(io,3,1)
				time.sleep(4)
				ioApi.writeDI(io,3,0)
	
if __name__ == "__main__":
	# test_task28()
	test_agv()
	
