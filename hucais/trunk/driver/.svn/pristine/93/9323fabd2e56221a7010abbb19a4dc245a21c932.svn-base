# coding: utf-8
# author: ives
# date: 2017-11-08
# desc: MES interface

import sys
import os
import datetime
from suds.client import Client

if __name__ == '__main__':
	currentPath = os.path.dirname(__file__)
	if currentPath != "":
		os.chdir(currentPath)

#全局变量：MES地址头
g_mesUrlHeader = 'http://192.168.32.167/IQCInterface/MesService.asmx?wsdl'


#获取作业单对应的产品列表
def loadProductsByJob(job):
	global g_mesUrlHeader

	retList = []
	
	clt = Client(g_mesUrlHeader)
	ws = clt.service.GetOrderList(job)
	if (len(ws["diffgram"]) < 1) or (len(ws["diffgram"][0]) < 1) or \
		(len(ws["diffgram"][0][0]) < 1) or (len(ws["diffgram"][0][0][0]) < 1) or \
		(len(ws["diffgram"][0][0][0][0]) < 1):
		return retList

	for item in ws["diffgram"][0][0][0][0]:
		jobId = item["job"][0]
		jobId = jobId[-9:]
		pro = {"job": jobId, "productID": item["productID"][0]}
		retList.append(pro)

	return retList


#获取作业单对应的产品列表
def loadProductsBySN(productId):
	global g_mesUrlHeader

	retList = []
	
	clt = Client(g_mesUrlHeader)
	ws = clt.service.GetOrderListBySn(productId)
	if (len(ws["diffgram"]) < 1) or (len(ws["diffgram"][0]) < 1) or \
		(len(ws["diffgram"][0][0]) < 1) or (len(ws["diffgram"][0][0][0]) < 1) or \
		(len(ws["diffgram"][0][0][0][0]) < 1):
		return retList

	for item in ws["diffgram"][0][0][0][0]:
		jobId = item["job"][0]
		jobId = jobId[-9:]
		pro = {"job": jobId, "productID": item["productID"][0]}
		retList.append(pro)

	return retList


#获取作业单信息
def loadJobInfo(jobId):
	global g_mesUrlHeader

	retDic = {}

	clt = Client(g_mesUrlHeader)
	ws = clt.service.GetOrderInfo(jobId)
	if (len(ws["diffgram"]) < 1) or (len(ws["diffgram"][0]) < 1) or \
		(len(ws["diffgram"][0][0]) < 1) or (len(ws["diffgram"][0][0][0]) < 1) or \
		(len(ws["diffgram"][0][0][0][0]) < 1):
		print("[mesApi: loadJobInfo] ", "load job:%s failed." %(jobId))
		return retDic

	for item in ws["diffgram"][0][0][0][0]:
		retDic["sapId"] = item["productTypeID"][0]
		retDic["productName"] = item["productTypeDesc"][0]
		retDic["planNum"] = item["quantity"][0]
	
		tmStr = item["sapPlanStartDate"][0]
		tmStr = tmStr[0:19]
		dt = datetime.datetime.strptime(tmStr, "%Y-%m-%dT%H:%M:%S")
		retDic["sapPlanStartDate"] = dt.strftime('%Y-%m-%d %H:%M:%S')

		tmStr = item["sapPlanEndDate"][0]
		tmStr = tmStr[0:19]
		dt = datetime.datetime.strptime(tmStr, "%Y-%m-%dT%H:%M:%S")
		retDic["sapPlanEndDate"] = dt.strftime('%Y-%m-%d %H:%M:%S')

	return retDic


#========================================== unit test ==========================================


if __name__ == '__main__':
	pass



