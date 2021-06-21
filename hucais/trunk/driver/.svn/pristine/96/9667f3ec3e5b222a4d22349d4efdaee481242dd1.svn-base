# coding: utf-8
# author: ives
# date: 2017-11-08
# desc: MES interface

import sys
import os
import datetime
import json
from suds.client import Client


if "../../common" not in sys.path:
	sys.path.append("../../common")


if __name__ == '__main__':
	currentPath = os.path.dirname(__file__)
	if currentPath != "":
		os.chdir(currentPath)


import log
import config
import webutility

#全局变量：MES地址头
g_mesUrlHeader = config.get("urlInfo", "mes_url", "http://127.0.0.1/IQCInterface/MesService.asmx?wsdl")


#获取作业单对应的产品列表
def loadProductsByJob(job):
	global g_mesUrlHeader

	retList = []
	
	clt = Client(g_mesUrlHeader)
	log.info("[mesApi: loadProductsByJob] ", "start, job=%s" %(job))
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

	log.info("[mesApi: loadProduct] ", "job:%s, product size: %d." %(job, len(retList)))
	return retList


#获取作业单对应的产品列表2
def loadProductsByJob2(job):
	global g_mesUrlHeader

	retList = []
	clt = Client(g_mesUrlHeader)
	ws = clt.service.GetOrderList(job)
	if (len(ws["diffgram"]) < 1) or (len(ws["diffgram"][0]) < 1) or \
		(len(ws["diffgram"][0][0]) < 1) or (len(ws["diffgram"][0][0][0]) < 1) or \
		(len(ws["diffgram"][0][0][0][0]) < 1):
		return retList

	for item in ws["diffgram"][0][0][0][0]:
		retList.append(item["productID"][0])
	return retList


#获取作业单对应的产品列表
def loadProductsBySN(productId):
	global g_mesUrlHeader

	retList = []
	
	clt = Client(g_mesUrlHeader)
	log.info("[mesApi: loadProductsBySN] ", "start, productId=%s" %(productId))
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

	log.info("[mesApi: loadProductsBySN] ", "job:%s, product size: %d." %(pro["job"], len(retList)))
	return retList


#获取过站的产品列表
def loadAssembleProducts(job):
	global g_mesUrlHeader

	retList = []
	pidDic = {}
	clt = Client(g_mesUrlHeader)
	log.info("[mesApi: loadAssembleProducts] ", "start, job=%s" %(job))
	ws = clt.service.GetAssembleList(job)
	if (len(ws["diffgram"]) < 1) or (len(ws["diffgram"][0]) < 1) or \
		(len(ws["diffgram"][0][0]) < 1) or (len(ws["diffgram"][0][0][0]) < 1) or \
		(len(ws["diffgram"][0][0][0][0]) < 1):
		return retList

	for item in ws["diffgram"][0][0][0][0]:
		pid = item["productID"][0]
		if pid not in pidDic:
			pro = {"operationDate": item["operationDate"][0], "productID": pid}
			pidDic[pid] = 1
			retList.append(pro)

	log.info("[mesApi: loadPostProduct] ", "job:%s, product size: %d." %(job, len(retList)))
	return retList


#获取作业单信息
def loadJobInfo(jobId):
	global g_mesUrlHeader

	retDic = {}

	clt = Client(g_mesUrlHeader)
	log.info("[mesApi: loadJobInfo] ", "start, job=%s" %(jobId))
	ws = clt.service.GetOrderInfo(jobId)
	if (len(ws["diffgram"]) < 1) or (len(ws["diffgram"][0]) < 1) or \
		(len(ws["diffgram"][0][0]) < 1) or (len(ws["diffgram"][0][0][0]) < 1) or \
		(len(ws["diffgram"][0][0][0][0]) < 1):
		log.warning("[mesApi: loadJobInfo] ", "load job:%s failed." %(jobId))
		return retDic

	for item in ws["diffgram"][0][0][0][0]:
		retDic["sapId"] = item["productTypeID"][0]
		retDic["productName"] = item["productTypeDesc"][0]
		retDic["planNum"] = item["quantity"][0]
	
		tmStr = item["sapPlanStartDate"][0]
		tmStr = tmStr[0:19]
		dt = datetime.datetime.strptime(tmStr, "%Y-%m-%dT%H:%M:%S")
		retDic["sapPlanStartDate"] = dt #dt.strftime('%Y-%m-%d %H:%M:%S')

		tmStr = item["sapPlanEndDate"][0]
		tmStr = tmStr[0:19]
		dt = datetime.datetime.strptime(tmStr, "%Y-%m-%dT%H:%M:%S")
		retDic["sapPlanEndDate"] = dt #dt.strftime('%Y-%m-%d %H:%M:%S')

	log.info("[mesApi: loadJobInfo] ", "load job:%s finish." %(jobId))
	return retDic


#获取SAP信息
def loadSapInfo(sapId):
	global g_mesUrlHeader

	productName = ''
	clt = Client(g_mesUrlHeader)
	log.info("[mesApi: loadSapInfo] ", "start, sap=%s" %(sapId))
	ws = clt.service.GetSAPInfo(sapId)
	if (len(ws["diffgram"]) < 1) or (len(ws["diffgram"][0]) < 1) or \
		(len(ws["diffgram"][0][0]) < 1) or (len(ws["diffgram"][0][0][0]) < 1) or \
		(len(ws["diffgram"][0][0][0][0]) < 1):
		log.warning("[mesApi: loadSapInfo] ", "load sap:%s failed." %(sapId))
		return productName

	for item in ws["diffgram"][0][0][0][0]:
		productName = item["Descript"][0]
		log.info("[mesApi: loadSapInfo] ", "load sap:%s finish." %(sapId))
	return productName

	
def getJobInfo2(job,isWyDept=True):
	def getList(data):
		r = []
		pp = data["WorkPassList"]
		for p in pp:
			r.append({"id":p["WorkOperation"],"name":p["Descript"],"count":int(p["PassCount"])})
		return r
		
	pre = "C000" if isWyDept else "W000"
	url = "http://192.168.32.167/Mes/api/OrderApi?orderId="+pre+job
	html = webutility.http_get(url,None,timeout=10,writelog=False)
	data = json.loads(html)
	if data["Msg"] != "查询成功！":
		raise Exception("查询"+job+"失败！"+data["Msg"])
	data = data["ResultData"]
	dd = {}
	dd["job"] = job
	dd["sap"] = data["DefID"]
	dd["productName"] = data["DefDescript"]
	dd["planNum"] = int(data["Quantity"])
	dd["process"] = getList(data)
	dd['planStartDate'] = datetime.datetime.strptime(data["PlanStartDate"], '%Y/%m/%d %H:%M:%S')
	dd['planEndDate'] = datetime.datetime.strptime(data["PlanEndDate"], '%Y/%m/%d %H:%M:%S')
	return dd
	
	
#ycat:返回作业单字典信息,isWyDept代表是否为无优的数据库 
#job:作业单ID
#sap:SAP码
#productName:物料描述
#planNum：计划数量 
#assembleNum:装配数量 
#testNum:调测数量 
#packNum:包装数量 
def getJobInfo(job,isWyDept=True):
	data = getJobInfo2(job,isWyDept)
	#工艺点配置 
	a = ["CWYZ-Assembly","CWJ-Assembly","CWYZ-Assembly","CGF-Assembly","CWC-Assembly"]
	t = ["CWYZ-Performance-QC","CWJ-Test"]
	p = ["CWYZ-Pack","CWJ-Pack"]
	types =  {"assembleNum":a,"testNum":t,"packNum":p}
	
	def getProcess(data,types):
		for p in data["process"]:
			if p["id"] in types:
				return p["count"]
		return 0
	
	dd = {}
	dd["job"] = data["job"]
	dd["sap"] = data["sap"]
	dd["planStartDate"] = data["planStartDate"]
	dd["planEndDate"] = data["planEndDate"]
	dd["productName"] = data["productName"]
	dd["planNum"] = int(data["planNum"])
	dd["assembleNum"] = getProcess(data,types["assembleNum"])
	dd["testNum"] = getProcess(data,types["testNum"])
	dd["packNum"] = getProcess(data,types["packNum"])
	return dd
	
	
#========================================== unit test ==========================================
def testgetJobInfo():
	d = getJobInfo("300039294")
	assert d["job"] == "300039294"
	assert d["productName"] == "DFR-3510DR,III2,F20P46S87A22RS"
	assert d["sap"] == "600003-001832-0000"
	assert d["planNum"] == 200
	assert d["assembleNum"] == 200
	assert d["testNum"] == 200
	assert d["packNum"] == 200
	d = getJobInfo("100221762")
	assert d["job"] == "100221762"
	assert d["productName"] == "ENB-3510,A04,H01H04Y02P24P23S80S42D12M16"
	assert d["sap"] == "610005-000042-0000"
	assert d["planNum"] == 200
	assert d["assembleNum"] == 200
	assert d["testNum"] == 200
	assert d["packNum"] == 199
	d = getJobInfo("300039118")
	assert d["job"] == "300039118"
	assert d["productName"] == "DFR-3210L,V4,F11P-5S26A22M04"
	assert d["sap"] == "600003-001856-0000"
	assert d["planNum"] == 100
	assert d["assembleNum"] == 100
	assert d["testNum"] == 97
	assert d["packNum"] == 96
	d = getJobInfo("300041550")
	assert d["planNum"] == 280
	assert d["assembleNum"] == 280
	assert d["testNum"] == 271
	assert d["packNum"] == 254	
		

def test_loadSapInfo():
	productName = loadSapInfo('')
	assert productName == ''
	productName = loadSapInfo('ives')
	assert productName == ''
	productName = loadSapInfo('600001-004844-5000')
	assert productName == 'RX1839-38V252P40S75A92M20'


if __name__ == '__main__':
	#testgetJobInfo()
	#test_loadProduct()
	#loadProductsByJob("200034608")
	#loadPostProducts("200034608")
	#loadJobInfo("200034608")
	#loadProductsBySN('AA17B0005329')
	#test_loadSapInfo()
	print(getJobInfo("300044382"))
	pass



