# coding=utf-8
# ycat			2018-8-2	  create
# seerAgv的API封装
import sys, os
import threading
import time
import setup

if __name__ == '__main__':
	setup.setCurPath(__file__)
import enhance
import json
import buffer
import mytimer
import log
# 短连接方式
import tcpSocketAdvanced as tcpSocket
import config

# PORT=8080
PORT=8899

BUTTON_OPEN=0x0f #按钮开关
BUTTON_CLOSE=0x10
OPEN_VALUE=0x01
CLOSE_VALUE=0x02
BUTTON_STATUS=0x0c

DATE_STATUS=0x1f
BUTTON_TYPE=0x26 #设置点动或者定时模式
TIME_OPEN = 0x21 #设置定时
TIME_CLOSE = 0x23
TIME_ROPEN = 0x28
TIME_RCLOSE = 0x2a

TIME_STATUS = 0x2d #查询定时和点动时间

def open(ip,addr=0):
	log.info("open the door",ip)
	return _request(ip=ip,type=BUTTON_OPEN,addr=addr,data=OPEN_VALUE)
	
def close(ip,addr=0):
	log.info("close the door",ip)
	return _request(ip=ip,type=BUTTON_OPEN,addr=int(addr),data=CLOSE_VALUE)

#点动：0x01  定时：0x02 非点动和定时，0x03 
def setActionType(ip,addr,type=0x02):
	log.info("set action type",ip,addr,type)
	return _request(ip=ip,type=BUTTON_TYPE,addr=int(addr),data=type)
	
#设置定时 timeList=["19:20","19:20","19:20"]
# actionType 1: open 0 :close
def setTimer(ip,addr,timeList,actionType=1):
	assert len(timeList) <= 5
	le = len(timeList)
	if actionType == 1:
		type = TIME_OPEN
	else:
		type = TIME_CLOSE
	if setActionType(ip,addr,2):
		for i in range(le):
			t = timeList[i].split(":")
			_request(ip,type=type,addr=int(addr),hour=int(t[0]),minute=int(t[1]),week=0xff,location=i)
	log.info(ip,"set timer on ",addr,"timer: ",timeList)
	
def getTimer(ip,addr):
	return _request(ip,type=TIME_STATUS,addr=int(addr))
	
# timeDict = {1: "2:30"}
def removeTimer(ip,addr,timeDict,actionType=1):
	if actionType == 1:
		type = TIME_ROPEN
	else:
		type = TIME_RCLOSE
	for k in timeDict:
		t = timeDict[k].split(":")
		_request(ip,type=type,addr=int(addr),hour=int(t[0]),minute=int(t[1]),week=0xff,location=int(k))
	
def _request(ip,type,addr=None,**data):
	buf = getSendingBuffer(type,addr, data)
	result = GetDataShort(buf,ip,PORT)
	return parseResult(ip,type,result)
	
# data = {"name": value}
def getSendingBuffer(type,addr,data):
	buf = buffer.outBuffer()
	buf.setBytes(b"\xaa")
	buf.setByte(type)
	if addr is not None:
		buf.setByte(addr)
	for p in data:
		buf.setByte(data[p])
	buf.setBytes([0x0] * (19-buf.len))
	buf.setBytes(b"\xbb")
	return buf

def GetDataShort(buf,ip,port):
	timeout = 10  # 10 seconds
	with tcpSocket.client(ip, port, timeout) as client:
		client.send(buf.buf)
		recData = client.recv()
		inBuf = buffer.inBuffer(recData)
		return inBuf

def parseResult(ip,type,result):
	result.getBuf(1)
	if type == TIME_STATUS:
		return parseTimer(result)
	rtype = result.getInt8()
	if type == BUTTON_OPEN and rtype == 0x11: #按钮开关成功
		return True
	elif type == BUTTON_TYPE and rtype == 0x27: # 设置点动或者定时模式成功
		return True
	elif type == TIME_OPEN or type == TIME_CLOSE: #设置定时器
		if rtype == 0x25:
			log.error(ip,"set time failed,timer has full,please remove")
			return False
		return True # rtype = 0x21 0x24
	elif type == TIME_ROPEN or type == TIME_RCLOSE: #删除定时器
		if rtype == 0x2c:
			log.error(ip,"remove time failed,time is not right")
			return False
		return True # rtype = 0x29 0x2b
	elif rtype == BUTTON_STATUS:
		parseStatus(result,ip)
	elif rtype == DATE_STATUS:
		parseDate(result,ip)
	
# 0x2e,返回按钮所有定时开时间,返回时间格式如下表格
# 0x2f,返回按钮所有定时关时间，返回时间格式如下表格
# 0x14,点动时间，返回格式如协议5
# 0x1b,点动或定时标志，返回格式如协议7
def parseTimer(result):
	ret = {}
	while result.remainLen >= 20:
		type = result.getInt8()
		if type == 0x2e or type == 0x2f:
			addr = result.getInt8()
			timeDict = {}
			for i in range(5):
				h = result.getInt8()
				m = result.getInt8()
				w = result.getInt8()
				if w != 0:
					timeDict[i] = "%d:%d"%(h,m)
			result.getBuf(2)
			if type == 0x2e:
				key = "open"
			elif type == 0x2f:
				key = "close"
			ret[key] = timeDict
		elif type == 0x14 or type == 0x1b:
			result.getBuf(18)
	return ret
	
def parseStatus(inBuf,ip):
	try:
		relay1 = '1' if inBuf.getInt8() == 0x02 else '0'
		relay2 = '1' if inBuf.getInt8() == 0x02 else '0'
		relay3 = '1' if inBuf.getInt8() == 0x02 else '0'
		relay4 = '1' if inBuf.getInt8() == 0x02 else '0'
		relay5 = '1' if inBuf.getInt8() == 0x02 else '0'
		relay6 = '1' if inBuf.getInt8() == 0x02 else '0'
		statusStr = "{0} {1} {2} {3} {4} {5}".format(relay1, relay2, relay3, relay4, relay5, relay6)
		log.debug('The door has received the signal, ip:'+ str(ip)  +' ,status:'+statusStr)
	except:
		raise Exception("协议解析错误")

def parseDate(inBuf,ip):
	try:
		yy = inBuf.getInt8()
		mm = inBuf.getInt8()
		dd = inBuf.getInt8()
		hh = inBuf.getInt8()
		MM = inBuf.getInt8()
		ss = inBuf.getInt8()
		statusStr= "{0}-{1}-{2} {3}:{4}:{5}".format(yy, mm, dd, hh, MM, ss)
		log.debug('The door has received the signal, ip:'+ str(ip)  +' ,time:'+statusStr)
	except:
		raise Exception("协议解析错误")

# ------------------for test--------------------
def test_action():
	ip='192.168.252.195'
	# port=8080
	port=8899
	while True:
		try:
			open(ip,0)
			time.sleep(3)
			close(ip,0)
			time.sleep(10)
		except Exception as e:
			log.exception("setSwitch",e)
			time.sleep(2)

if __name__ == '__main__':
	import utility
	utility.start()
	e=test_action()
