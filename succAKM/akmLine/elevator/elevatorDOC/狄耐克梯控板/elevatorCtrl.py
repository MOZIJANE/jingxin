from PyQt5.QtWidgets import *
import time
import threading
import setup

if __name__ == '__main__':
	setup.setCurPath(__file__)
import serialapi
import buffer
import frame.driver.seerAgv.tcpSocket as tcpSocket

EC_NUM = 1
EC_GROUPNUM = 1

EC_STATUS = 1
EC_STATUS_STATUS = b"\x00\x00"

EC_GOFLOOR = 2
EC_GOFLOOR_FIRST = b"\x00\x01"
EC_GOFLOOR_SECOND = b"\x00\x02"

EC_DOORCTRL = 3
EC_DOORCTRL_OPENMAIN = b"\x01\x00"
EC_DOORCTRL_OPENSUB = b"\x02\x00"
EC_DOORCTRL_OPENBOTH = b"\x03\x00"

g_port = 8080
g_addr = '192.168.1.254'
g_com = 'COM5'
g_isViaTcp = True


class Window(QWidget):
	def __init__(self):
		global g_com
		global g_isViaTcp
		super(Window, self).__init__()
		self.setFixedWidth(200)
		self.isViaTcp = g_isViaTcp
		self.m = serialapi.master(g_com)
		self.m.run()
		b = QPushButton('开始不断发送')
		b.clicked.connect(self.b1clicked)
		b2 = QPushButton('测试')
		b2.clicked.connect(self.b2clicked)

		b3 = QPushButton('查询状态')
		b3.clicked.connect(self.b3clicked)

		b4 = QPushButton('去1楼')
		b4.clicked.connect(self.b4clicked)

		b5 = QPushButton('去2楼')
		b5.clicked.connect(self.b5clicked)

		b6 = QPushButton('打开主门')
		b6.clicked.connect(self.b6clicked)

		b7 = QPushButton('打开副门')
		b7.clicked.connect(self.b7clicked)

		b8 = QPushButton('打开主副门')
		b8.clicked.connect(self.b8clicked)

		self.mainLayout = QVBoxLayout()
		self.mainLayout.addWidget(b)
		self.mainLayout.addWidget(b2)
		self.mainLayout.addWidget(b3)
		self.mainLayout.addWidget(b4)
		self.mainLayout.addWidget(b5)
		self.mainLayout.addWidget(b6)
		self.mainLayout.addWidget(b7)
		self.mainLayout.addWidget(b8)
		self.setLayout(self.mainLayout)

	def sendViaTcp(self, buf):
		global g_addr
		global g_port
		ip = g_addr
		port = g_port
		with tcpSocket.client(ip, port) as client:
			client.send(buf)
			recData = client.recv()
			inBuf = buffer.inBuffer(recData)
			return inBuf

	def checksum_calc(self, dat):
		dat = dat.buf
		le = len(dat)
		checksum = 0
		for i in range(0, int(le)):
			checksum = checksum + dat[i]
		checksum = 0xff & (~checksum) + 1
		return checksum

	def getSendingBuffer(self, addr, data, type):
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
		cksm = self.checksum_calc(buftemp)

		buf.setByte(cksm)

		buf.setBytes(b"\xDD")
		print("_request type " + str(type) + " " + str(addr) + " " + str(data) + " rawData " + str(buf))
		return buf.buf

	def b1clicked(self):
		self.clearthread = threading.Thread(target=self.sendAction)
		self.clearthread.start()

	def b2clicked(self):
		buf = self.getSendingBuffer(EC_NUM, EC_STATUS_STATUS, EC_STATUS)
		self.sendData(buf)

	def sendData(self, buf):
		def onRecived(result):
			self.resultHandler(result)

		if self.isViaTcp:
			result = self.sendViaTcp(buf)
			self.resultHandler(result)
		else:
			self.m.onRecived = onRecived
			self.m.send(buf)

	def resultHandler(self, result):
		# result.getBuf(10)
		print("从TCP返回" if self.isViaTcp else "从串口485返回")

		if self.isViaTcp:
			ret = bytes(result.getBuf(10))

			if ret[0] == 0x55 and ret[9] == 0xDD:
				if ret[5] == 0x81:
					tempstr = bin(ret[6])
					isSubCloosed = tempstr[2]
					isMainCloosed = tempstr[4]
					isWG = tempstr[5]
					isOL = tempstr[6]
					isDownward = tempstr[7]
					isUpward = tempstr[8]

					floor = ret[7]
					print('主门是否关闭', isMainCloosed)
					print('副门是否关闭', isSubCloosed)
					print('运行状态', '正常' if isWG == '0' else '不正常')
					print('是否超载', '无超载' if isOL == '0' else '有超载')
					print('上行', isUpward)
					print('下行', isDownward)
					print('物理楼层', floor)

	def b3clicked(self):
		buf = self.getSendingBuffer(EC_NUM, EC_STATUS_STATUS, EC_STATUS)
		self.sendData(buf)

	def b4clicked(self):
		buf = self.getSendingBuffer(EC_NUM, EC_GOFLOOR_FIRST, EC_GOFLOOR)
		self.sendData(buf)

	def b5clicked(self):
		buf = self.getSendingBuffer(EC_NUM, EC_GOFLOOR_SECOND, EC_GOFLOOR)
		self.sendData(buf)

	def b6clicked(self):
		buf = self.getSendingBuffer(EC_NUM, EC_DOORCTRL_OPENMAIN, EC_DOORCTRL)
		self.sendData(buf)

	def b7clicked(self):
		buf = self.getSendingBuffer(EC_NUM, EC_DOORCTRL_OPENSUB, EC_DOORCTRL)
		self.sendData(buf)

	def b8clicked(self):
		buf = self.getSendingBuffer(EC_NUM, EC_DOORCTRL_OPENBOTH, EC_DOORCTRL)
		self.sendData(buf)

	def sendAction(self):
		while 1:
			buf = self.getSendingBuffer(EC_NUM, EC_STATUS_STATUS, EC_STATUS)
			self.sendData(buf)
			time.sleep(5)

	def closeEvent(self, event):
		if self.m.isRunning():
			self.m.end()
		super(Window, self).closeEvent(event)


if __name__ == '__main__':
	import sys
	from PyQt5.QtWidgets import QApplication

	app = QApplication(sys.argv)
	w = Window()
	w.show()
	sys.exit(app.exec_())
