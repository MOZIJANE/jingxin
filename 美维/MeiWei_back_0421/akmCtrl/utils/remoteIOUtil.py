#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @Time : 2021/4/22 15:28
# @Author : XiongLue Xie
# @File : remoteIOUtil.py

import remoteioControl as ctl

def checkBoxStatus(ip = "192.168.252.110",port=502):
	values = ctl.readDOs(ip, port)
	return values

def setBoxStatus(ip = "192.168.252.110",port=502,values = "0,0,0,0,0,0,0,0"):

	return
