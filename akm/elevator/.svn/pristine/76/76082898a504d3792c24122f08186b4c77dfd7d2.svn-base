
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
import modbusapi
from crcmod import * 
from binascii import * 

# def crc16(x, invert):
#     a = 0xFFFF
#     b = 0xA001
#     for byte in x:
#         a ^= ord(byte)
#         for i in range(8):
#             last = a % 2
#             a >>= 1
#             if last == 1:
#                 a ^= b
#     s = hex(a).upper()
    
#     return s[4:6]+s[2:4] if invert == True else s[2:4]+s[4:6]

def crc16(read):
    crc16 =crcmod.mkCrcFun(0x18005,rev=True,initCrc=0xFFFF,xorOut=0x0000)
    data = read.replace(" ","")
    readcrcout=hex(crc16(unhexlify(data))).upper()
    str_list = list(readcrcout)
    if len(str_list) == 5:
        str_list.insert(2,'0')      # 位数不足补0
    crc_data = "".join(str_list)
    # print(crc_data)
    read = read.strip()+' '+crc_data[4:]+' '+crc_data[2:4]
    CRC = crc_data[4:]+' '+crc_data[2:4]
    print('CRC16校验:',CRC)
    print('增加Modbus CRC16校验：>>>',read)
    return read, CRC


def parse51(result):
    bit0 = result[0]
    bit1 = result[1]
    bit2 = result[2]
    
    isUpwardReady = 1 if not bit2 and not bit1 and bit0 else 0
    isUpward = 1 if not bit2 and bit1 and not bit0 else 0
    isDownward = 1 if not bit2 and bit1 and bit0 else 0
    isDownwardReady = 1 if bit2 and not bit1 and not bit0 else 0

    isOpening = 1 if result[3] else 0
    isClosing = 1 if result[4] else 0
    isParking = 1 if result[5] else 0   # 柏悌???unsure
    unAuto = 1 if result[7] else 0 

    isMaintain = 1 if result[8] else 0
    isError = 1 if result[9] else 0
    isOverload = 1 if result[10] else 0
    isFireMode = 1 if result[11] else 0
    isParking2 = 1 if result[12] else 0  # ??
    isFullload = 1 if result[13] else 0
    isSpecial = 1 if result[14] else 0
    isDriverMode = 1 if result[15] else 0
    data = {
        "isUpwardReady":isUpwardReady,
        "isUpward":isUpward,
        "isDownward":isDownward,
        "isDownwardReady":isDownwardReady,
        "isOpening":isOpening,
        "isClosing":isClosing,
        "isParking":isParking,
        "unAuto":unAuto,
        "isMaintain":isMaintain,
        "isError":isError,
        "isOverload":isOverload,
        "isFireMode":isFireMode,
        "isParking2":isParking2,
        "isFullload":isFullload,
        "isSpecial":isSpecial,
        "isDriverMode":isDriverMode
    }
    return data


def parse52(result):
    inFloor = int(result)
    return {"inFloor":inFloor}

def parse54(result):
    errorCode = hex(result[:8])
    isDoorLock = 1 if result[8] else 0
    isFinishOpen = 1 if result[9] else 0
    isFinishClosed = 1 if result[10] else 0

    data = {
        "errorCode":errorCode,
        "isDoorLock":isDoorLock,
        "isFinishOpen":isFinishOpen,
        "isFinishClosed":isFinishClosed
    }
    return data

def parse55(result):
    isUpward = 1 if result[0] else 0
    isDownward = 1 if result[1] else 0
    upWardStatus = 1 if result[2] else 0
    downWardStatus = 1 if result[3] else 0
    data = {
        "isUpward":isUpward,
        "isDownward":isDownward,
        "upWardStatus":upWardStatus,
        "downWardStatus":downWardStatus
    }
    return data


# def getStatus(ip,port):
#     tcpConnect = modbusapi.baseMaster(ip, port)
#     tcpConnect.conn()

#     r1 = tcpConnect.read(fcode=3,start=800,num=16) # 从00开始到51 有16X50个bit在前面？ 那51从800开始
#     data1 = parse51(r1)

#     r2 = tcpConnect.read(fcode=3,start=816,num=16)
#     data2 = parse52(r2)

#     r4 = tcpConnect.read(fcode=3, start=848, num=16)
#     data4 = parse54(r4)

#     r5 = tcpConnect.read(fcode=3, start=864, num=16)
#     data5 = parse55(r5)

#     ret = {}
#     ret.update(data1)
#     ret.update(data2)
#     ret.update(data4)
#     ret.update(data5)
#     return ret

# def goFloor(ip, port, floor, addr=0x0075):
#     tcpConnect = modbusapi.baseMaster(ip, port)
#     tcpConnect.conn()
#     if isinstance(floor, int):
#         floor = hex(floor)

#     values = '01 10 00 75 00 01 02 %s 01'%floor
#     values = crc16(values)
#     tcpConnect.write(fcode=6,addr=addr, value=values, num=16)
#     return getStatus(ip,port)


# def open(ip,port,floor,addr=0x0075, frontDoor=1,backDoor=0):
#     tcpConnect = modbusapi.baseMaster(ip, port)
#     tcpConnect.conn()
#     if frontDoor and backDoor:
#         d1 = '00 06'
#     elif frontDoor and not backDoor:
#         d1 = '04 06'
#     elif not frontDoor and backDoor:
#         d1 = '02 06'

#     values = '01 10 00 75 00 01 02 %s'%d1
#     values = crc16(values)
#     tcpConnect.write(fcode=6,addr=addr, value=values, num=16)
#     return getStatus(ip,port)

# # 01 10 00 75 00 01 02 02 06 2C 57 
# def close(ip,port,floor,addr=0x0075, frontDoor=1,backDoor=0):
#     tcpConnect = modbusapi.baseMaster(ip, port)
#     tcpConnect.conn()
#     if frontDoor and backDoor:
#         d1 = '06 06'
#     elif frontDoor and not backDoor:
#         d1 = '04 06'
#     elif not frontDoor and backDoor:
#         d1 = '02 06'

#     values = '01 10 00 75 00 01 02 %s'%d1
#     values = crc16(values)
#     tcpConnect.write(fcode=6,addr=addr, value=values, num=16)
#     return getStatus(ip,port)


############################# tcpSocket ###########################################
def sendViaTcp(ip,port,buf,recvLen):
	with tcpSocket.client(ip, port,timeout=5) as client:
		try:
			client.send(buf)
			recData = client.recv(recvLen)
			return buffer.inBuffer(recData)
		except Exception as e:
			log.warning("elevator: error",str(e))
			raise e

def getSendBuffer(high,low):
    buf = buffer.outBuffer()
    buf.setBytes(b"\x01")
    buf.setBytes(b"\x10")   # 功能码  只有这个????
    buf.setBytes(b"\x00")
    buf.setBytes(b"\x75")

    buf.setBytes(b"\x00")
    buf.setBytes(b"\x01")
    buf.setBytes(b"\x02")

    # print()
    high = int(high)
    low = int(low)

    buf.setByte(high)
    buf.setByte(low)

    value = '01 10 00 75 00 01 02 %s %s'%(high, low)
    x, crc = crc16(value)

    a,b = crc.split(' ')
    a = bytes.fromhex(a)
    b = bytes.fromhex(b)

    # buf.setBytes(crc)
    buf.setBytes(a)
    buf.setBytes(b)
    print('sending buf------------>', buf)
    return buf.buf

def getSendBufferRead(addr):
    buf = buffer.outBuffer()
    buf.setBytes(b"\x01")
    buf.setBytes(b"\x03")

    buf.setBytes(b"\x00")
    buf.setByte(addr)

    buf.setBytes(b"\x00")
    buf.setBytes(b"\x11")

    value = '01 03 00 %s 00 11'%addr
    x, crc = crc16(value)

    a,b = crc.split(' ')
    a = bytes.fromhex(a)
    b = bytes.fromhex(b)

    # buf.setBytes(crc)
    buf.setBytes(a)
    buf.setBytes(b)
    print('sending buffff----', buf)
    return buf.buf


def sendData(ip,port,buf,addr=None,recvLen=1024):
    result = sendViaTcp(ip,port,buf,recvLen)
    res = parseResult(result, addr)
    return res

def parseResult(result, addr):
    if addr==0x33:
        ret = parse51(result)
    elif addr==0x34:
        ret = parse52(result)
    elif addr==0x36:
        ret = parse54(result)
    elif addr==0x37:
        ret = parse55(result)
    return ret 

# 0x33 51
# 0x34 52 
# 0x36 54
# 0x37 55
def getStatus(ip,port):
    high = ''
    low = ''
    addr = 0x33
    buf = getSendBufferRead(addr)
    res = sendData(ip,port,buf,addr)
    return res

def goFloor(ip, port,floor):
    # if isinstance(floor, int):
        # floor = hex(floor)
        # floor = str(floor)

    high = floor
    low = '01'
    addr = 0x34 
    buf = getSendBuffer(high, low)
    res = sendData(ip,port,buf,addr)
    return res


def open(ip,port,floor, frontDoor=1,backDoor=0):
    if frontDoor and backDoor:
        high = '00'
        low = '06'
        # high = b"\x00"
        # low = b"\x06"
    elif frontDoor and not backDoor:
        # high = b"\x04"
        # low = b"\x06"
        high = '04'
        low = '06'
    elif not frontDoor and backDoor:
        # high = b"\x02"
        # low = b"\x06"
        high = '02'
        low = '06'

    buf = getSendBuffer(high, low)
    res = sendData(ip,port,buf)
    return res



def close(ip,port,floor, frontDoor=1,backDoor=0):
    if frontDoor and backDoor:
        # high = b"\x06"
        # low = b"\x06"
        high = '06'
        low = '06'
    elif frontDoor and not backDoor:
        # high = b"\x04"
        # low = b"\x06"
        high = '04'
        low = '06'
    elif not frontDoor and backDoor:
        # high = b"\x02"
        # low = b"\x06"
        high = '02'
        low = '06'

    buf = getSendBuffer(high, low)
    res = sendData(ip,port,buf)
    return res



################## unitTest ####################
def unitTest():
    print('1. get status')
    print('2. goto door')
    print('3. open door')
    print('4. close door')
    print('5. cancel')
    n = input('choose an option:')
    # print(n, type(n))
    if n == '1':
        m = input('enter ip & port, split by ; ')
        ip = m.split(';')[0]
        port = int(m.split(';')[1])
        getStatus(ip,port)
    elif n=='2':
        m = input('enter ip & port & floor, split by ; ')
        ip = m.split(';')[0]
        port = int(m.split(';')[1])
        floor = int(m.split(';')[2])
        goFloor(ip, port, floor)
    elif n=='3':
        m = input('enter ip & port & floor, split by ; ')
        ip = m.split(';')[0]
        port = int(m.split(';')[1])
        floor = int(m.split(';')[2])
        open(ip,port,floor)
    elif n=='4':
        m = input('enter ip & port & floor, split by ; ')
        ip = m.split(';')[0]
        port = int(m.split(';')[1])
        floor = int(m.split(';')[2])
        close(ip,port,floor)

    


if __name__ == "__main__":
    # ip = ''
    # port = ''
    # id = ''
    # getStatus(ip,port,id)
    unitTest()

    # print(crc16("012345678", True))
    
    # crc16("01 10 00 75 00 01 02 02 06")

    
    a = 'ef89'
    a_bytes = bytes.fromhex(a)
    print('fffffffff', a_bytes, type(a_bytes))
    aa = a_bytes.hex()
    print('cccccccccccc',type(aa), aa)
