
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
import elevatorMgr


# STX	报文头	2	0xAB 0x66
# BNK	组编号	1	1号群为0，2号群为1，依此类推              这个是十六进制？？？
# NOD	设备编号	1	1号梯为0x00，2号梯为0x01，依此类推
# LEN	DATA字节数	1	根据数据内容确定
# DATA	数据内容	-	见后续数据内容说明
# SUM	CHECKSUM校验和	1	SUM= ~（BNK+NOD+LEN+DATA）+1
# ETX	报文尾，表示通讯数据结束	1	0x03

BNK = 0x01
NOD = 0x01

def sendViaTcp(ip,port,buf,recvLen):
	# last = None
	with tcpSocket.client(ip, port,timeout=5) as client:
		try:
			client.send(buf)
			recData = client.recv(recvLen)
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

def getSendBuffer(BNK,NOD,data):
    buf = buffer.outBuffer()
    buf.setBytes(b"\xAB")
    buf.setBytes(b"\x66")
    buf.setByte(BNK)
    buf.setByte(NOD)

    LEN = len(data)
    buf.setByte(LEN)

    # buf.setBytes(data)

    for x in data:
        if isinstance(x, bytes):
            buf.setBytes(x)
        else:
            buf.setByte(x)

    # print('555555555555', type(BNK), type(NOD), type(LEN), type(data), data)
    # sum_ = ~(BNK+NOD+LEN+data)+1  # unsure??
    sum_ = checksum_calc(buf)
    buf.setByte(sum_)
    buf.setBytes(b"\x03")
    return buf.buf

def parseResult(result):
    ret = bytes(result.getBuf(result._len))
    ret_dict = {
        'isMaintain':'normal',
        'isOpening':0,
        'isClosing':0,
        'isFinishOpen':0,
        'inFloor':1,
        'isRunning':0,
        'reachFloorStatus':0,
        'openDoorStatus':0,
        'cancelStatus':0,
        "reachTargetFloor":0,
        'downStatus':0,
        'upStatus':0
    }
    if ret[0]==0x81:
        id_ = ret[1]
        sus3 = ret[2]
        inFloor = bin(ret[3])[1:]
        temp = bin(ret[4])
        reachFloorStatus = temp[5]   # 0:reach   1:not reach
        downStatus = temp[6]   # 1:down 0 :unavailable
        upStatus = temp[7]     # 1:up   0 :unavailable
                                # downStatus & upStatus == 1 means stop status and the door is already opened -->> isFinishOpen
        if downStatus and upStatus:
            isFinishOpen = 1
    elif ret[0]==0x82:
        id_ = ret[1]
        temp = ret[2]
        reachTargetFloor = temp[7]
    elif ret[0]==0x83:
        id_ = ret[1]
        sus3 = ret[2]
        inFloor = bin(ret[3])[1:]
        temp = bin(ret[4])
        openDoorStatus = temp[5]
        downStatus = temp[6]
        upStatus = temp[7]
        if downStatus and upStatus:
            isFinishOpen = 1
    elif ret[0]==0x84:
        id_ = ret[1]
        sus3 = ret[2]
        inFloor = bin(ret[3])[1:]
        temp = bin(ret[4])
        downStatus = temp[6]
        upStatus = temp[7]
        if downStatus and upStatus:
            isFinishOpen = 1
    elif ret[0]==0x85:
        id_ = ret[1]
        sus3 = ret[2]
        inFloor = bin(ret[3])[1:]
        temp = bin(ret[4])
        cancelStatus = temp[5]
        downStatus = temp[6]
        upStatus = temp[7]
        if downStatus and upStatus:
            isFinishOpen = 1
    # ret_dict = {
    #     'id':id_,
    #     'floor':floor,
    #     'reachFloorStatus':reachFloorStatus,
    #     'downStatus':downStatus,
    #     'upStatus':upStatus,
    #     'reachTargetFloor':reachTargetFloor,
    #     'openDoorStatus':openDoorStatus,
    #     'cancelStatus':cancelStatus,
    # }
    if upStatus or downStatus:
        isRunning = 1
    else:
        isRunning = 0
    ret_dict = {
        'isMaintain':'normal',
        'isOpening':0,
        'isClosing':0,
        'isFinishOpen':isFinishOpen,
        'inFloor':inFloor,
        'isRunning':isRunning,
        'reachFloorStatus':reachFloorStatus,
        'openDoorStatus':openDoorStatus,
        'cancelStatus':cancelStatus,
        "reachTargetFloor":reachTargetFloor,
        'downStatus':downStatus,
        'upStatus':upStatus
    }
    return ret_dict


def sendData(ip,port,buf,recvLen=1024):
    result = sendViaTcp(ip,port,buf,recvLen)
    res = parseResult(result)
    return res

# change format 
base = [str(x) for x in range(10)] + [ chr(x) for x in range(ord('A'),ord('A')+6)]
def bin2hex(string_num):
    return dec2hex(bin2dec(string_num))

def dec2hex(string_num):
    num = int(string_num)
    mid = []
    while True:
        if num == 0: break
        num,rem = divmod(num, 16)
        mid.append(base[rem])
    return ''.join([str(x) for x in mid[::-1]])

def bin2dec(string_num):
    return str(int(string_num, 2))


def changeGoFloorData(d1, d2):
    r = d2
    rr = bin(r)
    t = int(rr[2:].zfill(7))
    t2 = d1 + t
    t4 = bin2hex(t2)
    t5 = bytes.fromhex(t4)
    return t5

# 200ms 
# 1	命令字：0x01
# 2	ID号：0x00～0xFF
# 3	0xFF
 
def getStatus(ip,port,id):
    # data = b'\x01' + id + b'\xFF'
    data = []
    data.append(b'\x01')
    data.append(id)
    data.append(b'\xFF')
    buf = getSendBuffer(BNK,NOD,data)
    res = sendData(ip,port,buf)
    return res

def goFloor(ip, port, id, floor, frontDoor=1, backDoor=0):
    if frontDoor:
        d1 = 0x00
    elif backDoor:
        d1 = 0x01
    d2 = floor
    # print('goFloor-------------', d1,d2)
    # c = changeGoFloorData(d1,d2)
    # data = b'\x02' + id + '\x00' + c
    data = []
    data.append(b'\x02')
    data.append(id)
    data.append(b'\x00')
    data.append(d1)
    data.append(d2)

    buf = getSendBuffer(BNK,NOD,data)
    res = sendData(ip,port,buf)
    return res

# 设备编号和id是同一个吗？？？组编号是int还是hex
def open(ip,port,id,frontDoor=1,backDoor=0):
    if frontDoor and backDoor:
        c1 = b'\x30'
    elif frontDoor and not backDoor:
        c1 = b'\x10'
    elif backDoor and not frontDoor:
        c1 = b'\x20'
    elif not frontDoor and not backDoor:
        c1 = b'\x00'

    # data = b'\x03' + id + c1
    # data = bytes([b'\x03', id, c1])

    data = []
    data.append(b'\x03')
    data.append(id)
    data.append(c1)

    buf = getSendBuffer(BNK,NOD,data)
    res = sendData(ip,port,buf)
    return res

def close(ip,port,id,exitSpecial,frontDoor=1,backDoor=0):
    if exitSpecial:
        if frontDoor and backDoor:
            c1 = b'\x31'
        elif frontDoor and not backDoor:
            c1 = b'\x11'
        elif backDoor and not frontDoor:
            c1 = b'\x21'
        elif not frontDoor and not backDoor:
            c1 = b'\x01'
    else:
        if frontDoor and backDoor:
            c1 = b'\x30'
        elif frontDoor and not backDoor:
            c1 = b'\x10'
        elif backDoor and not frontDoor:
            c1 = b'\x20'
        elif not frontDoor and not backDoor:
            c1 = b'\x00'

    data = b'\x04' + id + c1
    buf = getSendBuffer(BNK,NOD,data)
    res = sendData(ip,port,buf)
    return res

def cancel(ip,port,id):
    data = b'\x05' + id + b'\x00'
    buf = getSendBuffer(BNK,NOD,data)
    res = sendData(ip,port,buf)
    return res

def unitTest():
    print('1. get status')
    print('2. goto door')
    print('3. open door')
    print('4. close door')
    print('5. cancel')
    n = input('choose an option:')
    # print(n, type(n))
    if n == '1':
        m = input('enter ip & port & id, split by ; ')
        ip = m.split(';')[0]
        port = int(m.split(';')[1])
        id = bytes(m.split(';')[2],encoding='utf8')
        getStatus(ip,port,id)
    elif n=='2':
        m = input('enter ip & port & id & floor, split by ; ')
        ip = m.split(';')[0]
        port = int(m.split(';')[1])
        id = bytes(m.split(';')[2],encoding='utf8')
        
        floor = int(m.split(';')[3])
        goFloor(ip, port, id, floor)
    elif n=='3':
        m = input('enter ip & port & id, split by ; ')
        ip = m.split(';')[0]
        port = int(m.split(';')[1])
        id = bytes(m.split(';')[2],encoding='utf8')
        open(ip,port,id)
    elif n=='4':
        m = input('enter ip & port & id, split by ; ')
        ip = m.split(';')[0]
        port = int(m.split(';')[1])
        id = bytes(m.split(';')[2],encoding='utf8')
        close(ip,port,id,1)

    elif n=='5':
        m = input('enter ip & port & id, split by ; ')
        ip = m.split(';')[0]
        port = int(m.split(';')[1])
        id = bytes(m.split(';')[2],encoding='utf8')
        cancel(ip,port,id)



if __name__ == "__main__":
    # ip = ''
    # port = ''
    # id = ''
    # getStatus(ip,port,id)
    unitTest()

    # 0x02 0x01 0x4D 0x36 0xff 0x00 0x86 0x03
    # li = [0x02, 0x01, 0x4D, 0x36, 0xff, 0x00]
    # d = 0
    # for x in li:
    #     d+= x
    # if d>255:
    #     d = d - 255
    # print(hex(d))

    # a = '\x48'
    # print('aaa',a)
    # b = '\x45'
    # c = a+b
    # print('4444444444444',c)