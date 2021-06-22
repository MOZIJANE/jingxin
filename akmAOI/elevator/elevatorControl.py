import setup

if __name__ == '__main__':
	setup.setCurPath(__file__)
import buffer
import log
# 短连接方式
import tcpSocketAdvanced as tcpSocket

# STX	报文头	2	0xAB 0x66
# BNK	组编号	1	1号群为0，2号群为1，依此类推
# NOD	设备编号	1	1号梯为0x00，2号梯为0x01，依此类推
# LEN	DATA字节数	1	根据数据内容确定
# DATA	数据内容	-	见后续数据内容说明
# SUM	CHECKSUM校验和	1	SUM= ~（BNK+NOD+LEN+DATA）+1
# ETX	报文尾，表示通讯数据结束	1	0x03

EC_NUM = 1
EC_GROUPNUM = 1

EC_STATUS = 1
EC_STATUS_STATUS = b"\x00\x00"

EC_GOFLOOR = 2
EC_GOFLOOR_FIRST = b"\x00\x01"
EC_GOFLOOR_SECOND = b"\x00\x02"
EC_GOFLOOR_THREE = b"\x00\x04"
EC_GOFLOOR_FOUR = b"\x00\x05"
EC_GOFLOOR_FIVE = b"\x00\x06"

EC_DOORCTRL = 3
EC_DOORCTRL_OPENMAIN = b"\x01\x00"
EC_DOORCTRL_OPENSUB = b"\x02\x00"
EC_DOORCTRL_OPENBOTH = b"\x03\x00"

RET_STATUS = 0x81
RET_GOFLOOR = 0x82
RET_OPENDOOR = 0x83
RET_CLOSEDOOR = 0x84
RET_CANCEL = 0x85


def sendViaTcp(ip, port, buf, recvLen):
	# last = None
	with tcpSocket.client(ip, port, timeout=5) as client:
		try:
			client.send(buf)
			recData = client.recv(recvLen)
			return buffer.inBuffer(recData)
		except Exception as e:
			log.warning("elevator: error", str(e))
			raise e



def checksum_calc(dat):
	dat = dat.buf
	le = len(dat)
	checksum = 0
	for i in range(0, int(le)):
		checksum = checksum + dat[i]
	checksum = 0xff & (~checksum) + 1
	return checksum


def getSendingBuffer(addr, data, type):
	buf = buffer.outBuffer()
	buf.setBytes(b"\x55\xAA")
	buf.setByte(8 + len(data))
	buf.setByte(1)
	buf.setByte(addr)
	buf.setByte(type)
	buf.setBytes(data)

	buftemp = buffer.outBuffer()
	buftemp.setByte(8 + len(data))
	buftemp.setByte(1)
	buftemp.setByte(addr)
	buftemp.setByte(type)
	buftemp.setBytes(data)
	cksm = checksum_calc(buftemp)

	buf.setByte(cksm)

	buf.setBytes(b"\xDD")
	#print("_request type " + str(type) + " " + str(addr) + " " + str(data) + " rawData " + str(buf))
	return buf.buf


def parseResult(result):
	# log.info("result:",result)
	ret = bytes(result.getBuf(result._len))
	reachFloorStatus = None
	isFinishOpen = None
	inFloor = None
	openDoorStatus = None
	cancelStatus = None
	reachTargetFloor = None
	isRunning = None
	downStatus = 0
	upStatus = 0

	ttt = {
		'isMaintain': 'normal',
		'isOpening': 0,
		'isClosing': 0,
		'isFinishOpen': None,
		'inFloor': None,
		'isRunning': None,
		'reachFloorStatus': None,
		'openDoorStatus': None,
		'cancelStatus': None,
		"reachTargetFloor": None,
		'downStatus': None,
		'upStatus': None
	}
	if len(ret) < 6:
		return ttt
	if ret[5] == RET_STATUS:

		tempstr = bin(ret[6])
		inFloor = int(ret[7])
		print("++++++return inFloor:",inFloor)
		if inFloor == 3:
			inFloor = 9
		if inFloor > 2:
			inFloor = inFloor-1
		print("++++++inFloor:",inFloor)
		downStatus = int(tempstr[7])  # 1:down 0 :unavailable
		upStatus = int(tempstr[8])  # 1:up   0 :unavailable
		if int(tempstr[4]) == 0:
			isFinishOpen = 1
			
			
	elif ret[5] == RET_GOFLOOR:
		pass
	elif ret[5] == RET_OPENDOOR:
		pass
	elif ret[5] == RET_CLOSEDOOR:
		pass
	elif ret[5] == RET_CANCEL:
		pass
	ret_dict = {
		'isMaintain': 'normal',
		'isOpening': 0,
		'isClosing': 0,
		'isFinishOpen': isFinishOpen,
		'inFloor': inFloor,
		'isRunning': isRunning,
		'reachFloorStatus': reachFloorStatus,
		'openDoorStatus': openDoorStatus,
		'cancelStatus': cancelStatus,
		"reachTargetFloor": reachTargetFloor,
		'downStatus': downStatus,
		'upStatus': upStatus
	}
	return ret_dict


def sendData(ip, port, buf, recvLen=1024):
	result = sendViaTcp(ip, port, buf, recvLen)
	res = parseResult(result)
	return res


def getStatus(ip, port, id):
	buf = getSendingBuffer(EC_NUM, EC_STATUS_STATUS, EC_STATUS)
	res = sendData(ip, port, buf)
	#log.info("lift status:",res)
	return res


def goFloor(ip, port, id, floor, frontDoor=1, backDoor=0):
	gofloor = ""
	floor = int(floor)
	if floor == 1:
		gofloor = EC_GOFLOOR_FIRST
	elif floor == 2:
		gofloor = EC_GOFLOOR_SECOND
	elif floor == 3:
		gofloor = EC_GOFLOOR_THREE
	elif floor == 4:
		gofloor = EC_GOFLOOR_FOUR
	elif floor == 5:
		gofloor = EC_GOFLOOR_FIVE
	buf = getSendingBuffer(EC_NUM, gofloor, EC_GOFLOOR)
	res = sendData(ip, port, buf)
	return res


def open(ip, port, id, frontDoor=1, backDoor=0):
	buf = getSendingBuffer(EC_NUM, EC_DOORCTRL_OPENMAIN, EC_DOORCTRL)
	res = sendData(ip, port, buf)
	return res


def close(ip, port, id, frontDoor=1, backDoor=0):
	buf = getSendingBuffer(EC_NUM, EC_DOORCTRL_OPENSUB, EC_DOORCTRL)
	res = sendData(ip, port, buf)
	# log.info("lift status:",res)
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
		id = bytes(m.split(';')[2], encoding='utf8')
		getStatus(ip, port, id)
	elif n == '2':
		m = input('enter ip & port & id & floor, split by ; ')
		ip = m.split(';')[0]
		port = int(m.split(';')[1])
		id = bytes(m.split(';')[2], encoding='utf8')

		floor = int(m.split(';')[3])
		goFloor(ip, port, id, floor)
	elif n == '3':
		m = input('enter ip & port & id, split by ; ')
		ip = m.split(';')[0]
		port = int(m.split(';')[1])
		id = bytes(m.split(';')[2], encoding='utf8')
		open(ip, port, id)
	elif n == '4':
		m = input('enter ip & port & id, split by ; ')
		ip = m.split(';')[0]
		port = int(m.split(';')[1])
		id = bytes(m.split(';')[2], encoding='utf8')
		close(ip, port, id, 1)

	elif n == '5':
		m = input('enter ip & port & id, split by ; ')
		ip = m.split(';')[0]
		port = int(m.split(';')[1])
		id = bytes(m.split(';')[2], encoding='utf8')
		cancel(ip, port, id)

def test4():
	data = b"\x01\x00\xFF"
	buf = buffer.outBuffer()
	buf.setBytes(STX)
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
	sum_ = checksum_calc(buf)
	buf.setByte(sum_)
	buf.setByte(EXT)

def test5():
	data = b"\x04\x00\x00"
	buf = buffer.outBuffer()
	buf.setBytes(STX)
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
	sum_ = checksum_calc(buf)
	buf.setByte(sum_)
	buf.setByte(EXT)



if __name__ == "__main__":
	test4()
