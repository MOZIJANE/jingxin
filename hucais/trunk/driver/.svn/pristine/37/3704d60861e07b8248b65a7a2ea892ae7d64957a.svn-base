# coding: utf-8
# author: ives
# date: 2017-11-08
# desc: ATS interface

import sys
import os
import pymssql
import operator

if "../../common" not in sys.path:
	sys.path.append("../../common")


if __name__ == '__main__':
	currentPath = os.path.dirname(__file__)
	if currentPath != "":
		os.chdir(currentPath)


import log
import config

g_dbIp = '192.168.32.54'


# 解析测试项名称
def decodeCasesName(casesStr):
	retList = []
	str = casesStr

	if str.find("atsTable") == -1:
		return retList

	nPos = str.index("atsTable")
	str = str[nPos : -1]
	str = str.replace(' ', '')

	#逐行解析
	while (str.find('\n') != -1) or (str.find('\r') != -1):
		if (str.find('\n') != -1):
			nPos = str.index('\n')
		else:
			nPos = str.index('\r')
		val = str[0: nPos - 1]
		str = str[nPos + 1 : -1]

		if len(val) > 0:
			if val[0] == '}':
				break
			if (len(val) > 1) and (val[0:2] == '[\"') and (val.find('\"]') != -1):
				nPos = val.index('\"]')
				val = val[2 : nPos]
				if val != 'LinkFlag':
					retList.append(val)

	return retList


#获取产品对应的测试项
def loadCasesBySap(productTypeID):
	retList = []
	sapID = productTypeID
	sapID = sapID.replace('-', '')

	conn = pymssql.connect(g_dbIp, "autotest", "system", "ATS-TEST")
	cur = conn.cursor()
	cur.execute(r'''SELECT c.Code, c.Name 
		FROM Cases as c 
		LEFT JOIN ProductCase as p 
		ON c.CaseID = p.CaseID 
		WHERE p.SAPID = '%s' ''' %(sapID))

	if cur is not None:
		for row in cur:
			retList.extend(decodeCasesName(row[0]))
	cur.close()
	conn.close()
	log.info("[atsApi: loadCases] ", "SAP:%s, product size: %d." %(sapID, len(retList)))
	return retList


#获取指定工位下的经过Ats测试的产品
def getAtsProduct(hostName, dept):
	#从两套数据库查时间最新的记录
	proDic = {}
	proList = []

	dbName = 'ATS-TEST'
	if dept == 'WJ':
		dbName = 'ATS-MASELINK'
	conn = pymssql.connect(g_dbIp, "autotest", "system", dbName)
	cur = conn.cursor()
	cur.execute(r'''SELECT TOP 20 SeriesNumber FROM TestDataMaster 
		WHERE Station = '%s' ORDER BY TestTime DESC ''' %(hostName))

	if cur is not None:
		for row in cur:
			proDic[row[0].replace(' ', '')] = 1
	cur.close()
	conn.close()

	log.info('AtsApi:getAtsProduct', 'get product finish.')

	for key in proDic:
		proList.append(key)
	return proList


# 查询仪器状态
def getInstStatusByATS():
	instList = []
	conn = pymssql.connect(g_dbIp, "autotest", "system", "ATS-TEST")
	cur = conn.cursor()
	cur.execute(r'''SELECT InstrID,Status,UpdateTime,Remark,StationID FROM InstrStatus ''')
	if cur is not None:
		for row in cur:
			instList.append({'instID' : row[0], 'status' : row[1], 'uptime' : row[2], 'remark' : row[3]})
	cur.close()
	conn.close()

	#conn2 = pymssql.connect("10.10.32.54", "autotest", "system", "ATS-MASELINK")
	#cur2 = conn.cursor()
	#cur2.execute(r'''SELECT InstrID,Status,UpdateTime,Remark FROM InstrStatus ''')
	#if cur2 is not None:
	#	for row in cur2:
	#		instList.append({'instID' : row[0], 'status' : row[1], 'uptime' : row[2], 'remark' : row[3]})
	#cur2.close()
	#conn2.close()
	
	return instList


# 查询工位状态
def getSeatStatusByATS():
	seatList = []
	conn = pymssql.connect(g_dbIp, "autotest", "system", "ATS-TEST")
	cur = conn.cursor()
	cur.execute(r'''SELECT Station,Status,UpdateTime,UserName FROM StationStatus ''')
	if cur is not None:
		for row in cur:
			seatList.append({'hostName' : row[0], 'status' : row[1], 'uptime' : row[2], 'userName' : row[3]})
	cur.close()
	conn.close()

	#conn2 = pymssql.connect("10.10.32.54", "autotest", "system", "ATS-MASELINK")
	#cur2 = conn.cursor()
	#cur2.execute(r'''SELECT Station,Status,UpdateTime,UserName FROM StationStatus ''')
	#if cur2 is not None:
	#	for row in cur2:
	#		seatList.append({'hostName' : row[0], 'status' : row[1], 'uptime' : row[2], 'userName' : row[3]})
	#cur2.close()
	#conn2.close()
	
	return seatList


# 拆解成多条语句
def _splitMultiSql(cols, num, isChar):
	sqlList = []
	sql = ''
	cnt = 0
	seq = '\'' if isChar else ''
	for cl in cols:
		if len(sql) > 0:
			sql = sql + ',' + seq + str(cl) + seq
		else:
			sql = seq + str(cl) + seq
		cnt = cnt + 1
		if cnt >= num:
			sqlList.append(sql)
			cnt = 0
			sql = ''
	if len(sql) > 0:
		sqlList.append(sql)
	return sqlList


def _getTestInfoEx(dbName, productList):
	conn = pymssql.connect(g_dbIp, "autotest", "system", dbName)
	cur = conn.cursor()
	data = {}
	masterList = []
	ref = {}
	sqlProduct = _splitMultiSql(productList, 100, True)
	for s1 in sqlProduct:
		cur.execute(r'''SELECT MasterID,SeriesNumber,TestTime,Result FROM TestDataMaster WHERE SeriesNumber in (%s) ''' %s1)
		if cur is not None:
			for row in cur:
				productId = row[1].upper().replace(' ', '')
				ret = row[3].upper().replace(' ', '')
				masterId = int(row[0])
				masterList.append(masterId)
				ref[masterId] = productId
				flag = False
				if operator.eq('PASS', ret):
					flag = True
				if productId not in data:
					data[productId] = {'result': flag, 'testTime': row[2], 'detail': {'pass': 0, 'fail': 0}}
				else:# 以最后一个的结果为准
					if row[2] > data[productId]['testTime']:
						data[productId] = {'result': flag, 'testTime': row[2], 'detail': {'pass': 0, 'fail': 0}}
	sqlMaster = _splitMultiSql(masterList, 100, False)
	for s2 in sqlMaster:
		cur.execute(r'''SELECT MasterID,Result FROM TestDataDetail WHERE MasterID in (%s) ''' %s2)
		if cur is not None:
			for row in cur:
				mastId = int(row[0])
				productId = ref[mastId]
				ret = row[1].upper().replace(' ', '')
				if operator.eq('PASS', ret):
					data[productId]['detail']['pass'] = data[productId]['detail']['pass'] + 1
				elif operator.eq('FAIL', ret):
					data[productId]['detail']['fail'] = data[productId]['detail']['fail'] + 1
				elif operator.eq('FALI', ret):
					data[productId]['detail']['fail'] = data[productId]['detail']['fail'] + 1
	cur.close()
	conn.close()
	return data


# 查询作业单测试信息
# 返回 {"AA182001": {'result': True, 'testTime': dt, 'detail': [True, True, False,...]}, ...}
def getTestInfo(productList):
	data = _getTestInfoEx("ATS-TEST", productList)
	if len(data) < 1:
		data = _getTestInfoEx("ATS-MASELINK", productList)
	return data


#========================================== unit test ==========================================
def test_getAtsProduct():
	proList = getAtsProduct('HNC-55000239', 'WY')
	print(proList)

def test_exportUser():
	import json
	conn = pymssql.connect("10.10.32.54", "autotest", "system", "ATS-TEST")
	cur = conn.cursor()
	cur.execute(r'''SELECT u.UserName, u.Password, u.ChineseName FROM UserName as u   ''')

	infoDic = {}
	infoList = []
	cnt = 0
	if cur is not None:
		for row in cur:
			userName = row[0]
			if userName in infoDic:
				cnt += 1
				print('%s is already exist.'%userName)
			infoList.append({"_id": userName, "password": row[1], "chineseName" : row[2], \
				"department": "", "photo": userName + ".jpg", "phone": "", "userGroup" : ""})
			infoDic[userName] = 1
	cur.close()
	conn.close()
	print(len(infoList))

	conn2 = pymssql.connect("10.10.32.54", "autotest", "system", "ATS-MASELINK")
	cur2 = conn2.cursor()
	cur2.execute(r'''SELECT u.UserName, u.Password FROM UserName as u   ''')

	if cur2 is not None:
		for row in cur2:
			userName = row[0]
			if userName in infoDic:
				cnt += 1
				print('++++ %s is already exist.'%userName)
				infoList.append({"repeat" : "++++++++++++++++++++", "_id": userName, "password": row[1], "chineseName" : "", \
					"department": "", "photo": userName + ".jpg", "phone": "", "userGroup" : ""})
			else:
				infoList.append({"_id": userName, "password": row[1], "chineseName" : "", \
					"department": "", "photo": userName + ".jpg", "phone": "", "userGroup" : ""})
			infoDic[userName] = 1
	cur2.close()
	conn2.close()
	fd = open("d:/u_user.json", "a+")
	str = json.dumps(infoList, ensure_ascii=False,indent=2)
	fd.write(str)
	fd.write("\n")
	fd.close()


def test_getInstStatus():
	instList = getInstStatusByATS()
	assert len(instList) > 0
	print(instList)

def test_splitMultiSql():
	arr1 = []
	arr2 = []
	for i in range(100):
		arr1.append(i)
		arr2.append('a' + str(i))
	sql = _splitMultiSql(arr1, 25, False)
	print(sql)
	sql = _splitMultiSql(arr2, 30, True)
	print(sql)

def test_getTestInfo():
	global g_dbIp
	g_dbIp = '10.10.32.54'
	jobId = '100228355'
	pids = []
	for i in range(200):
		pids.append('FA183000' + str(6982 + i))
	data = getTestInfo(pids)
	print(data)
	

if __name__ == '__main__':
	#test_loadProduct()
	#loadCasesBySap("6000030016370000")
	#test_exportUser()
	#test_getInstStatus()
	#test_splitMultiSql()
	test_getTestInfo()
	pass



