#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @Time : 2021/4/22 16:35
# @Author : XiongLue Xie
# @File : testZLIO.py

import remoteioMgr
from utils import toolsUtil
import time


# data = remoteioMgr.readDOList("ZLAN01")
# print(data)
while True:
	n = 15
	for i in range(n):
		values = remoteioMgr.readDIList("ZLAN01")
		#values = remoteioMgr.readDOList("ZLAN01")
		print("当前信号：",values)
		if values["status"][1] == 2:  # 根据现场实际信号修改
			print("取料:", toolsUtil.getCurTime())
			break
		else:
			print("无料，继续等待：", toolsUtil.getCurTime())
			account = i + 1
			print("等待次数:", account)
			# if i == 2 :
			# 	temp = "0,1,0,0,0,0,0,0"
			# 	data = remoteioMgr.writeDOList("ZLAN01", temp)
			if i >= n-1:
				print("****等待%s次无料****" % str(n))
				break
			time.sleep(3)
			continue
	str = input("Enter your input: ")
	print("Received input is : ", str)
	if str == "999":
		print("退出")
		break