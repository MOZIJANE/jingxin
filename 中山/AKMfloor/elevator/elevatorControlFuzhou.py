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

STX = b"\xab\x66"
BNK = 0x00
NOD = 0x00
EXT = 0x03

CMD_STATUS = 0x01
CMD_GOFLOOR = 0x02
CMD_OPENDOOR = 0x03
CMD_CLOSEDOOR = 0x04
CMD_CANCEL = 0x05

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
	checksum = 0x00
	i = 1
	for datitem in dat.buf:
		if i > 2:
			checksum += datitem
		i += 1
	checksum -=1
	checksum = (~checksum)&0xff
	return checksum


def getSendBuffer(BNK, NOD, data):
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
			# log.info("+++type:",type(x))
			buf.setByte(x)
	sum_ = checksum_calc(buf)
	buf.setByte(sum_)
	buf.setByte(EXT)
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

	if len(ret) < 8:
		return ttt
	if ret[5] == RET_STATUS:
		# id_ = ret[1]
		# sus3 = ret[2]
		inFloor = ret[8]
		tempstr = bin(ret[9])[2:]
		temp = "00000"+tempstr
		reachFloorStatus = int(temp[-3])  # 0:reach   1:not reach
		downStatus = int(temp[-1])  # 1:down 0 :unavailable
		upStatus = int(temp[-2])  # 1:up   0 :unavailable
		isFinishOpen = int(temp[-4])
	elif ret[5] == RET_GOFLOOR:
		pass
	elif ret[5] == RET_OPENDOOR:
		inFloor = ret[8]
		tempstr = bin(ret[9])[2:]
		temp = "00000" + tempstr
		reachFloorStatus = int(temp[-3])  # 0:reach   1:not reach
		downStatus = int(temp[-1])  # 1:down 0 :unavailable
		upStatus = int(temp[-2])  # 1:up   0 :unavailable
		isFinishOpen = int(temp[-4])
	elif ret[5] == RET_CLOSEDOOR:
		pass
	elif ret[5] == RET_CANCEL:
		id_ = ret[1]
		sus3 = ret[2]
		inFloor = bin(ret[3])[1:]
		temp = bin(ret[4])
		cancelStatus = temp[5]
		downStatus = temp[6]
		upStatus = temp[7]
		if downStatus and upStatus:
			isFinishOpen = 1

	if upStatus==1 or downStatus==1:
		isRunning = 1
	else:
		isRunning = 0
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
	# data = b'\x01' + id + b'\xFF'
	data = []
	data.append(b'\x01')
	data.append(id)
	data.append(b'\xFF')
	buf = getSendBuffer(BNK, NOD, data)
	res = sendData(ip, port, buf)
	log.info("lift status:",res)
	return res


def goFloor(ip, port, id, floor, frontDoor=1, backDoor=0):
	if frontDoor:
		d1 = 0x00
	elif backDoor:
		d1 = 0x01
	d2 = int(floor)
	data = []
	data.append(b'\x02')
	data.append(b'\x00')
	# data.append(id)
	data.append(b'\x00')
	# data.append(d1)
	data.append(d2)

	buf = getSendBuffer(BNK, NOD, data)
	res = sendData(ip, port, buf)
	return res


def open(ip, port, id, frontDoor=1, backDoor=0):
	if frontDoor and backDoor:
		c1 = b'\x30'
	elif frontDoor and not backDoor:
		c1 = b'\x10'
	elif backDoor and not frontDoor:
		c1 = b'\x20'
	elif not frontDoor and not backDoor:
		c1 = b'\x00'

	data = []
	data.append(b'\x03')
	data.append(id)
	data.append(c1)

	buf = getSendBuffer(BNK, NOD, data)
	res = sendData(ip, port, buf)
	return res


def close(ip, port, id, frontDoor=1, backDoor=0):
	# if exitSpecial:
	# 	if frontDoor and backDoor:
	# 		c1 = b'\x31'
	# 	elif frontDoor and not backDoor:
	# 		c1 = b'\x11'
	# 	elif backDoor and not frontDoor:
	# 		c1 = b'\x21'
	# 	elif not frontDoor and not backDoor:
	# 		c1 = b'\x01'
	# else:
	# if frontDoor and backDoor:
	# 	c1 = b'\x30'
	# elif frontDoor and not backDoor:
	# 	c1 = b'\x10'
	# elif backDoor and not frontDoor:
	# 	c1 = b'\x20'
	# elif not frontDoor and not backDoor:
	# 	c1 = b'\x00'
	c1 = b'\x00'
	data = []
	data.append(CMD_CLOSEDOOR)
	data.append(id)
	data.append(c1)
	buf = getSendBuffer(BNK, NOD, data)
	res = sendData(ip, port, buf)
	return res


def cancel(ip, port, id):
	data = b'\x05' + id + b'\x00'
	buf = getSendBuffer(BNK, NOD, data)
	res = sendData(ip, port, buf)
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
