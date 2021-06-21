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
import log
# 短连接方式
import tcpSocketAdvanced as tcpSocket
import config


def _request(ip,port,addr, type, data):
	buf = getSendingBuffer(addr, data, type)
	result = GetDataShort(buf,ip,port)
	result.getBuf(1)
	type = result.getInt8()
	if type == 0x0c:
		parseStatus(result,ip)
	elif type == 0x1f:
		parseTime(result,ip)


def GetDataShort(buf,ip,port):
	timeout = 5  # 10 seconds
	with tcpSocket.client(ip, port, timeout) as client:
		client.send(buf.buf)
		recData = client.recv(recvLen=4096)
		inBuf = buffer.inBuffer(recData)
		return inBuf


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


def parseTime(inBuf,ip):
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


def getSendingBuffer(addr, data, type):
	buf = buffer.outBuffer()
	buf.setBytes(b"\xaa")
	buf.setByte(type)
	buf.setByte(addr)
	buf.setByte(data)
	buf.setBytes([0x0] * 15)
	buf.setBytes(b"\xbb")
	return buf


def setSwitch(ip,port,addr, isOpen=True):
	addr=int(addr)
	port=int(port)
	if addr > 15:
		return
	operationType = 0x0f
	relayNo = addr
	if isOpen:
		operation = 0x01
		log.info("The signal to open the door has been sent, " + " doorIP:" + ip)
	else:
		operation = 0x02
		log.info("The signal to close the door has been sent, " + " doorIP:" + ip )
	try:
		_request(ip=ip,port=port,addr=relayNo,type= operationType,data= operation)
	except Exception as ex:
		log.debug(ex)
		raise Exception("网络连接错误")


# ------------------for test--------------------

def test_setSwitch():
	ip='192.168.1.110'
	port=8899
	while True:
		span = 1
		# time.sleep(span)
		setSwitch(ip,port,0, isOpen=True)
		time.sleep(span)
		# setSwitch(ip,port,2, isOpen=True)
		# time.sleep(span)
		setSwitch(ip,port,0, isOpen=False)
		time.sleep(span)
		# setSwitch(ip,port,2, isOpen=False)


if __name__ == '__main__':
	# import utility
	# utility.run_tests(__file__)
	test_setSwitch()
