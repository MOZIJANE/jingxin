#!/usr/bin/python
# -*- coding: UTF-8 -*-
# @Time : 2021/4/20 15:55
# @Author : XiongLue Xie
# @File : testGrammar.py

from utils import toolsUtil

from common import local
a = local.get("project","name")
print(a)


toolsUtil.setTaskPath("b666","666")
toolsUtil.setTaskPath("a666","666")
toolsUtil.setTaskPath("c666","666")
toolsUtil.setTaskPath("d666","666")

s1 = "a66"
for i in toolsUtil.g_taskPath.keys():
	index1 = i.find(s1)
	print(index1)

# temp = toolsUtil.getTaskPath()
# print(temp)
