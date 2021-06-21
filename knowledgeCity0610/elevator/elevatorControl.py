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
import tcpSocketLong 
import serialapi
import config
import lock as lockImp

EC_GOFLOOR_FIRST = b'1\x00'
EC_GOFLOOR_SECOND = b'2\x00'

EC_NUM = 1
EC_GROUPNUM = 1

EC_STATUS = b'3'
EC_STATUS_STATUS = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

EC_GOFLOOR = b'5'

EC_DOOROPENCTRL = b'6'
EC_DOORCLOSECTRL = b'7'
EC_DOORCTRL_MAIN = b"\xff\x00"
EC_DOORCTRL_SUB = b"\x00\xff"
EC_DOORCTRL_BOTH = b"\xff\xff"
EC_DOORCTRL_NONE = b"\x00\x00"
g_lock = lockImp.create("elevatorApi.tcp_lock")
g_tcp = None

def readHeader(client):
	recData = client.recv(recvLen=1)
	if recData[0] != 0x02:
		return False
	recData = client.recv(recvLen=1)
	if recData[0] != 0x01:
		return False	
	recData = client.recv(recvLen=1)
	if recData[0] != 0x4D:
		return False	
	return True
	
#@lockImp.lock(g_lock)
#def sendViaTcp(ip,port,buf,recLen):
#	last = None
#	with tcpSocket.client(ip, port,timeout=5) as client:
#		try:
#			client.send(buf)
#			#print("send:",str(buffer.inBuffer(buf)))
#			while True:
#				if readHeader(client):
#					break
#			recData = client.recv(recvLen=recvLen-3)
#			recData = bytes([0x02,0x01,0x4D]) + recData
#			#print(len(recData),"recv:",str(buffer.inBuffer(recData)))
#			return buffer.inBuffer(recData)
#		except Exception as e:
#			log.warning("elevator: error",str(e))
#			raise e

def sendViaTcp(ip,port,buf,recvLen):
	last = None
	with tcpSocket.client(ip, port,timeout=5) as client:
		try:
			client.send(buf)
			#print("send:",str(buffer.inBuffer(buf)))
			recData = client.recv(recvLen=1024)
			#print(len(recData),"recv:",str(buffer.inBuffer(recData)))
			return buffer.inBuffer(recData)
		except Exception as e:
			log.warning("elevator: error",str(e))
			raise e

def checksum_calc(dat):
	checksum = 0x00
	for datitem in dat.buf:
		checksum += datitem
	checksum = 0xff & checksum
	return checksum

def getSendingBuffer( addr, data, type):
	buf = buffer.outBuffer()
	buf.setBytes(b"\x02")
	buf.setByte(addr)
	buf.setBytes(b"\x4D")
	buf.setBytes(type)
	buf.setBytes(data)

	cksm = checksum_calc(buf)

	buf.setByte(cksm)

	buf.setBytes(b"\x03")
	#log.info("_request type " + str(type) + " " + str(addr) + " " + str(data) + " rawData " + str(buf))
	return buf.buf


def sendData(ip,port, buf,recLen):
	#def onRecived(result):
	#	return resultHandler(result) 
	result = sendViaTcp(ip,port,buf,recLen)
	return resultHandler(result)


def resultHandler(result):
	ret = bytes(result.getBuf(result._len))
	#log.info('resultHandler of elevator:', ret.hex()) 
	backData={
				'isOpening':0,
				'isClosing': 0,
				'isFinishOpen':0,
				'isRunning':0,
				'isMaintain': 'normal',
				'isUpward': 0,
				'isDownward': 0,
				'inFloor': 2,
				'frontDoorRegist': 0,
				'backDoorRegist': 0,
				'frontDoorRelease': 0,
				'backDoorRelease': 0
					}
					
	try:
		if ret[0] == 0x02 and ret[-1] == 0x03:
			fdoor = False
			rdoor = False
			if ret[3] == 0x33:
				tempstr = bin(ret[5])[2:]
				if len(tempstr) < 8:
					bvg = 8 - len(tempstr)
					for i in range(0, bvg):
						tempstr = "0" + tempstr
				baseStatus = tempstr[-3:]
				isUpward = 0
				isDownward = 0
				isRunning = 0
				#log.info("状态位:" + tempstr + ",运行位:" + baseStatus)
				if baseStatus == '000':
					isUpward = 0
					isDownward = 0
					isRunning = 0
				elif baseStatus == '001':
					isUpward = 1
					isDownward = 0
					isRunning = 0
				elif baseStatus == '010':
					isUpward = 1
					isDownward = 0
					isRunning = 1
				elif baseStatus == '011':
					isUpward = 0
					isDownward = 1
					isRunning = 1
				elif baseStatus == '100':
					isUpward = 0
					isDownward = 1
					isRunning = 0

				# isSubCloosed = -1
				isOpening = int(tempstr[-4])
				isClosing = int(tempstr[-5])
				isFinishOpen = int(tempstr[-7])
				isOutOfService = int(tempstr[-6])

				floor = ret[4]
				#log.info('isOpening', isOpening,'isClosing', isClosing,'isFinishOpen', isFinishOpen,'isRunning', isRunning,'isMaintain', 'maintaining' if isOutOfService == 1 else 'normal','isUpward', isUpward,'isDownward', isDownward,'inFloor', floor)

				# if isFinishOpen == 0 and isClosing == 0 and isOpening == 0:
				# 	doorStatus = 1
				# else:
				# 	doorStatus = 0
				
				dd={
					'isOpening': isOpening,
					'isClosing': isClosing,
					'isFinishOpen':isFinishOpen,
					'isRunning':isRunning,
					'isMaintain': 'maintaining' if isOutOfService == 1 else 'normal',
					'isUpward': isUpward,
					'isDownward': isDownward,
					'inFloor': floor
				}
				backData.update(dd)
 
			elif ret[3] == 0x35:
				if ret[4] == 0x01:
					fdoor = True
				else:
					fdoor = False
				if ret[5] == 0x01:
					rdoor = True
				else:
					rdoor = False
				#log.info("frontdoor regist {0}，backdoor regist {1}".format(('success' if fdoor else 'fail'), ('success' if rdoor else 'fail')))
				dd={
					'frontDoorRegist': 1 if fdoor else 0,
					'backDoorRegist': 1 if rdoor else 0
				}
				backData.update(dd)

			elif ret[3] == 0x36:
				if ret[4] == 0xff:
					fhold = True
				else:
					fhold = False
				if ret[5] == 0xff:
					rhold = True
				else:
					rhold = False
				#log.info("frontdoor open {0}，backdoor open {1}".format(('keep' if fhold else 'release'), ('keep' if rhold else 'release')))
				dd = {
					'isFinishOpen':1,
					'frontDoorRelease': 1 if fdoor else 0,
					'backDoorRelease': 1 if rdoor else 0
					}
				backData.update(dd)
				
			return backData
	except Exception as e:
		log.error("elevator",e)

#查询状态
def b3clicked(ip,port):
	buf = getSendingBuffer(EC_NUM, EC_STATUS_STATUS, EC_STATUS)
	ret = sendData(ip,port,buf,1024)
	#print("elevator",ret)
	return ret
  
#去楼层
def b4clicked(ip,port,floor):
	currentFloor = floor
	frontDoor = ord(str(currentFloor).encode('utf-8'))
	# rearDoor = ord(str(currentFloor).encode('utf-8'))
	rearDoor = 0x00

	floorData = bytes([frontDoor, rearDoor])
	buf = getSendingBuffer(EC_NUM, floorData, EC_GOFLOOR)
	return sendData(ip,port,buf,1024)
	#time.sleep(1)
	#return sendData(ip,port,buf)

#打开主门
def b6clicked(ip,port):
	buf = getSendingBuffer(EC_NUM, EC_DOORCTRL_MAIN, EC_DOOROPENCTRL)
	return sendData(ip,port,buf,1024)

#打开副门
def b7clicked(ip,port):
	buf = getSendingBuffer(EC_NUM, EC_DOORCTRL_SUB, EC_DOOROPENCTRL)
	return sendData(ip,port,buf,1024)

#打开主副门
def b8clicked(ip,port):
	buf = getSendingBuffer(EC_NUM, EC_DOORCTRL_BOTH, EC_DOOROPENCTRL)
	return sendData(ip,port,buf,1024)

def b9clicked(ip,port):
	buf = getSendingBuffer(EC_NUM, EC_DOORCTRL_BOTH, EC_DOORCLOSECTRL)
	return sendData(ip,port,buf,1024)