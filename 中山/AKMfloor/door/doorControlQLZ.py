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
import tcpSocketLong as tcpSocketLong
import config



def _request(ip,port,startflag, addr, addrEndFlag, ctrl, l, flag, data, cs, endflag, timeout):
	buf = getSendingBuffer(startflag, addr, addrEndFlag, ctrl, l, flag, data, cs, endflag,timeout)
	result = GetDataShort(buf,ip,port)
	log.debug('read from door module:%s, values:%s'%(ip, result))
	result.getBuf(1)

def GetDataShort(buf,ip,port):
	timeout = 10  # 10 seconds
	with tcpSocket.client(ip, port, timeout) as client:
		client.send(buf.buf)
		log.debug('send to door module:%s, values:%s'%(ip, buf))
		recData = client.recv(1024)
		inBuf = buffer.inBuffer(recData)
		return inBuf

def getSendingBuffer(startflag, addr, addrEndFlag, ctrl, l, flag,data, cs, endflag, timeout):
	buf = buffer.outBuffer()
	buf.setByte(startflag)
	buf.setByte(addr)
	buf.setByte(addr)
	buf.setByte(addr)
	buf.setByte(addr)
	buf.setByte(addrEndFlag)
	buf.setByte(ctrl)
	buf.setByte(l)
	buf.setByte(flag)
	buf.setByte(data)
	buf.setByte(data)
	buf.setByte(data)
	buf.setByte(data)
	buf.setByte(timeout)
	buf.setByte(cs)
	buf.setByte(endflag)
	return buf


# 远程复位（标识码：08H）
# 55 aa aa aa aa aa 01 05 08 00 00 00 00
# 55 |aa aa aa aa| aa |01 |05| 08| 00 00 00 00

def resetDoorModule(ip,port):
	try:
		buf = buffer.outBuffer()
		buf.setByte(0x55)
		buf.setByte(0xAA)
		buf.setByte(0xAA)
		buf.setByte(0xAA)
		buf.setByte(0xAA)
		buf.setByte(0xAA)
		buf.setByte(0x01)  # ctrl
		buf.setByte(0x05)  # 数据区字节长度
		buf.setByte(0x08)  # 标识码
		buf.setByte(0x00)
		buf.setByte(0x00)
		buf.setByte(0x00)
		buf.setByte(0x00)
		log.info('reset door module: %s'%ip)
		GetDataShort(buf,ip,port)
	except Exception as e:
		log.info('reset door module Exception:',e, ip, port)


# 读全部状态（当前开关量输入和当前继电器输出）（标识码：2FH）
# 55| 00 00 00 00| AA |00 |01| 2F 2F 16
# 返回值
# 55 |00 00 00 00 |AA| 80| 05| 2F |04 00 04 0F |CA |16

def readStatus(ip,port):
	try:
		buf = buffer.outBuffer()
		buf.setByte(0x55)
		buf.setByte(0x00)
		buf.setByte(0x00)
		buf.setByte(0x00)
		buf.setByte(0x00)
		buf.setByte(0xAA)
		buf.setByte(0x00)  
		buf.setByte(0x01)  
		buf.setByte(0x2F)  
		buf.setByte(0x2F)
		buf.setByte(0x16)
		
		status = GetDataShort(buf,ip,port)
		log.info('read from door module: %s, values:%s'%(ip,status))
		return status

	except Exception as e:
		log.info('the contact with the door module:%s is closed!'%ip)
		resetDoorModule(ip,port)
		time.sleep(20)

		return  None

# 单路开启（标识码：80H-8BH）
# 55 00 00 00 00 AA 03 06 80 00 00 00 00 00 88 16
# 03 为下行控制，06 数据区字节长度，80 为标识码，00 00 00 00 为控制密码 00 延时单位 00 表示立即开 启 ，大于 0 则开启后延时自动关闭，类似与点动功能。
# 返回值  55| 00 00 00 00| AA| 83 |03| 80| 1B 00| 2E| 16

def open(ip, port):
	port=int(port)
	startflag = 0x55
	addr = 0x00
	addrEndFlag = 0xAA
	ctrl = 0x03
	l = 0x06
	flag = 0x80
	data = 0x00
	cs = 0x88   # 校验
	endflag = 0x16
	timeout = 0x00
	log.info("The signal to open the door has been sent, " + " doorIP:" + ip)
	try:
		_request(ip,port,startflag, addr, addrEndFlag, ctrl, l, flag,data, cs, endflag, timeout)
	except Exception as ex:
		log.debug("网络连接错误",ex)
		raise Exception("网络连接错误")



# 单路关闭（标识码：90H-9BH）
# 55 00 00 00 00 AA 03 06 90 00 00 00 00 00 98 16
# 03 为下行控制，06 数据区字节长度，90 为标识码，00 00 00 00 为控制密码 00 延时单位 00 表示立即关 闭 ，大于 0 则延时后自动关闭。
# 返回： 55 00 00 00 00 AA 83 03 90 1B 00 2E 16

def close(ip, port):
	port=int(port)
	startflag = 0x55
	addr = 0x00
	addrEndFlag = 0xAA
	ctrl = 0x03
	l = 0x06
	flag = 0x90
	data = 0x00
	cs = 0x98   # 校验
	endflag = 0x16
	timeout = 0x00
	log.info("The signal to close the door has been sent, " + " doorIP:" + ip)
	try:
		_request(ip,port,startflag, addr, addrEndFlag, ctrl, l, flag,data, cs, endflag, timeout)
	except Exception as ex:
		log.debug("网络连接错误",ex)
		raise Exception("网络连接错误")

# ------------------for test--------------------

def test():
	import random
	# 模块作为客户端
	ip='192.168.128.18'
	port=8899
	
	while True:
		span = random.randint(5, 10)
		time.sleep(2)

		open(ip,port)
		time.sleep(2)

		status = readStatus(ip,port)
		if status:
			s = str(status).split()[1:]
			s1 = s[9:13][::-1]
			b1 = '0x' + ''.join(s1[0:1])
			b2 = '0x' + ''.join(s1[2:3])
			b1 = bin(eval(b1))
			b2 = bin(eval(b2))
			print('继电器输出状态位:',b1, '开关量输入状态位:', b2)
		# else:
		# 	resetDoorModule(ip,port)
		# 	time.sleep(20)

		
		# time.sleep(span*10)
		time.sleep(span)

		close(ip,port)
		# time.sleep(span*10)
		time.sleep(span)


if __name__ == '__main__':

	test()
