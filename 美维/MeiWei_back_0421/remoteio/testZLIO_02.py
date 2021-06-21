#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @Time : 2021/4/22 16:35
# @Author : XiongLue Xie
# @File : testZLIO.py

import remoteioMgr,remoteioControl
from utils import toolsUtil
import time

#values = "0,1,1,0,0,0,0,0"
values = "0,0,0,0,0,0,0,0"
# a = remoteioControl.readDOs("192.168.8.122",502)
# print(a)
data = remoteioMgr.writeDOList("ZLAN01",values)
print(data)

