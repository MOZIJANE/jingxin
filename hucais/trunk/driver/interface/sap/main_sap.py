# coding: utf-8
# author: ives
# date: 2018-02-26
# desc: SAP服务

import sys
import os
import bottle
import time

def setCurPath(filename):
	currentPath = os.path.dirname(filename)
	if currentPath != "":
		os.chdir(currentPath)

if __name__ == '__main__':
	setCurPath(__file__)

import log
import sapApi
import webutility


# 作业单对应的装配工时数据,取不到默认返回10,单位:分钟
@webutility.get('/scada/api/sap/getAssembleManhour')
def urlGetAssembleManhour():
	jobId = webutility.get_param("jobId")
	return {'manhour' : sapApi.loadFromSap(jobId)}


if __name__ == '__main__':
	webutility.run(9120)


