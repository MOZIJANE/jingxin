from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import time
import threading
import setup
import datetime
import functools

if __name__ == '__main__':
	setup.setCurPath(__file__)
import serialapi
import buffer
import utility
import log
import mytimer
import frame.controls.keyValueView as keyValueView
import frame.driver.seerAgv.tcpSocket as tcpSocket

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

g_port = 8080
g_addr = '192.168.128.148'
g_com = 'COM4'
g_isViaTcp = True
g_isRunning = False


class Window(QWidget):
	def __init__(self):
		super(Window, self).__init__()
		self.keyValuePool = dict()
		self.setWindowFlags(Qt.Window)
		self.createMainWindow()
		self.setWindowTitle("梯控调试工具")

	def createMainWindow(self):
		centerLayout = QVBoxLayout()
		tabWidget = QTabWidget()
		self.d = Debug()
		self.s = Setting(self.onCntSerial)
		tabWidget.addTab(self.d, "调试")
		tabWidget.addTab(self.s, "设置")

		tabWidget.setMinimumWidth(450)
		tabWidget.setMinimumHeight(200)

		centerLayout.addWidget(tabWidget)
		centerLayout.addStretch()
		self.setLayout(centerLayout)

	def onCntSerial(self):
		self.d.initSerial()

	def closeEvent(self, event):
		if self.d.m.isRunning():
			self.d.m.end()
		utility.finish()

		super(Window, self).closeEvent(event)


class Setting(QWidget):
	def __init__(self, s):
		super(Setting, self).__init__()
		global g_port
		global g_addr
		global g_com
		global g_isViaTcp

		groupBox = QGroupBox("通信方式")

		self.radio1 = QRadioButton("TCP网关")
		self.radio2 = QRadioButton("485串口")
		self.radio1.clicked.connect(self.r1clicked)
		self.radio2.clicked.connect(self.r1clicked)
		self.radio1.setChecked(g_isViaTcp)
		self.radio2.setChecked(not g_isViaTcp)
		self.cntSerial = s
		vbox = QVBoxLayout()
		vbox.addWidget(self.radio1)
		vbox.addWidget(self.radio2)
		vbox.addStretch(1)
		groupBox.setLayout(vbox)

		self.comEditor = keyValueView.simpleKeyValueEdit('COM地址', g_com, keyValueView.simpleKeyValueEdit.LineEdit,
														 onValueChangedCB=self.onComValueChanged)
		self.ipEditor = keyValueView.simpleKeyValueEdit('IP地址', g_addr, keyValueView.simpleKeyValueEdit.LineEdit,
														onValueChangedCB=self.onIpValueChanged)
		self.portEditor = keyValueView.simpleKeyValueEdit('端口', g_port, keyValueView.simpleKeyValueEdit.SpinBox,
														  onValueChangedCB=self.onPortValueChanged)

		b8 = QPushButton('连接串口')
		b8.clicked.connect(self.cntSerial)

		self.mainLayout = QVBoxLayout()
		self.mainLayout.addWidget(groupBox)
		self.mainLayout.addWidget(self.comEditor)
		self.mainLayout.addWidget(self.ipEditor)
		self.mainLayout.addWidget(self.portEditor)
		self.mainLayout.addWidget(b8)
		self.setLayout(self.mainLayout)

	def r1clicked(self):
		global g_isViaTcp
		g_isViaTcp = self.radio1.isChecked()

	def onComValueChanged(self, obj, value):
		global g_com
		g_com = value

	def onIpValueChanged(self, obj, value):
		global g_addr
		g_addr = value

	def onPortValueChanged(self, obj, value):
		global g_port
		g_port = value


class Debug(QWidget):
	def __init__(self):
		super(Debug, self).__init__()
		self.floor = 3
		# self.initSerial()
		self.m = serialapi.master(g_com)
		b = QPushButton('开始不断发送')
		b.setCheckable(True)
		b.clicked.connect(self.b1clicked)
		b2 = QPushButton('测试')
		b2.clicked.connect(self.b2clicked)

		b3 = QPushButton('查询状态')
		b3.clicked.connect(self.b3clicked)

		b4 = QPushButton('去楼层')
		b4.clicked.connect(self.b4clicked)

		groupBox = QGroupBox("呼梯参数")

		self.radio1 = QRadioButton("前门")
		self.radio2 = QRadioButton("后门")

		self.radio1.setChecked(True)

		vbox = QHBoxLayout()
		vbox.addWidget(self.radio1)
		vbox.addWidget(self.radio2)

		self.floorEditor = QSpinBox()
		self.floorEditor.setMaximum(7)
		self.floorEditor.setMinimum(0)
		self.floorEditor.setValue(self.floor)
		vbox.addWidget(QLabel("物理层:"))
		vbox.addWidget(self.floorEditor)
		groupBox.setLayout(vbox)

		b6 = QPushButton('保持')
		b6.clicked.connect(self.b6clicked)

		b7 = QPushButton('关闭')
		b7.clicked.connect(self.b7clicked)

		groupBox2 = QGroupBox("开门参数")

		self.radio3 = QCheckBox("前门")
		self.radio4 = QCheckBox("后门")

		self.radio3.setChecked(True)

		vbox = QHBoxLayout()
		vbox.addWidget(self.radio3)
		vbox.addWidget(self.radio4)

		groupBox2.setLayout(vbox)

		self.mainLayout = QVBoxLayout()
		self.mainLayout.addWidget(b)
		self.mainLayout.addWidget(b2)
		self.mainLayout.addWidget(b3)
		self.mainLayout.addWidget(groupBox)

		self.mainLayout.addWidget(b4)

		self.mainLayout.addWidget(groupBox2)

		self.mainLayout.addWidget(b6)
		self.mainLayout.addWidget(b7)
		self.mainWidget = QWidget()

		self.mainWidget.setLayout(self.mainLayout)

		self.dataLayout = QVBoxLayout()
		self.statisticsView1 = keyValueView.simpleKeyValueLabel('开门', '')
		self.statisticsView2 = keyValueView.simpleKeyValueLabel('关门', '')
		self.statisticsView3 = keyValueView.simpleKeyValueLabel('是否运行中', '')
		self.statisticsView4 = keyValueView.simpleKeyValueLabel('是否维护中', '')
		self.statisticsView5 = keyValueView.simpleKeyValueLabel('上行', '')
		self.statisticsView6 = keyValueView.simpleKeyValueLabel('下行', '')
		self.statisticsView7 = keyValueView.simpleKeyValueLabel('物理楼层', '')
		self.statisticsView8 = keyValueView.simpleKeyValueLabel('开门到位', '')

		self.dataLayout.addWidget(self.statisticsView1)
		self.dataLayout.addWidget(self.statisticsView2)
		self.dataLayout.addWidget(self.statisticsView3)
		self.dataLayout.addWidget(self.statisticsView4)
		self.dataLayout.addWidget(self.statisticsView5)
		self.dataLayout.addWidget(self.statisticsView6)
		self.dataLayout.addWidget(self.statisticsView7)
		self.dataLayout.addWidget(self.statisticsView8)

		self.dataWidget = QWidget()
		self.dataWidget.setFixedWidth(150)
		groupBox3 = QGroupBox("状态")
		groupBox3.setLayout(self.dataLayout)

		self.dataLayout2 = QVBoxLayout()
		self.statisticsView11 = keyValueView.simpleKeyValueLabel('关门到位', '')

		self.dataLayout2.addWidget(self.statisticsView11)

		groupBox4 = QGroupBox("状态捕获")
		groupBox4.setLayout(self.dataLayout2)

		self.dataLayout3 = QGridLayout()
		def gofloor(currentFloor):
			if self.radio1.isChecked():
				frontDoor = ord(str(currentFloor).encode('utf-8'))
			else:
				frontDoor = 0x00

			if self.radio2.isChecked():
				rearDoor = ord(str(currentFloor).encode('utf-8'))
			else:
				rearDoor = 0x00

			floorData = bytes([frontDoor, rearDoor])
			buf = self.getSendingBuffer(EC_NUM, floorData, EC_GOFLOOR)
			self.sendData(buf)

		b1=QPushButton('1')
		b1.setShortcut(Qt.Key_F1)
		b1.clicked.connect(functools.partial(gofloor,1))
		b2=QPushButton('2')
		b1.setShortcut(Qt.Key_F2)

		b2.clicked.connect(functools.partial(gofloor,2))
		b3=QPushButton('3')
		b1.setShortcut(Qt.Key_3)

		b3.clicked.connect(functools.partial(gofloor,3))
		b4=QPushButton('4')
		b1.setShortcut(Qt.Key_4)

		b4.clicked.connect(functools.partial(gofloor,4))
		b5=QPushButton('5')
		b1.setShortcut(Qt.Key_5)

		b5.clicked.connect(functools.partial(gofloor,5))


		self.dataLayout3.addWidget(b1, *(0, 0))
		self.dataLayout3.addWidget(b2, *(0, 1))
		self.dataLayout3.addWidget(b3, *(0, 2))
		self.dataLayout3.addWidget(b4, *(1, 0))
		self.dataLayout3.addWidget(b5, *(1, 1))


		groupBox5 = QGroupBox("快速按楼")
		groupBox5.setLayout(self.dataLayout3)

		ll = QVBoxLayout()
		ll.addWidget(groupBox3)
		ll.addWidget(groupBox4)
		ll.addWidget(groupBox5)
		self.dataWidget.setLayout(ll)

		vboxlayout = QHBoxLayout()
		vboxlayout.addWidget(self.mainWidget)
		vboxlayout.addWidget(self.dataWidget)
		self.setLayout(vboxlayout)

		self.clearthread = threading.Timer(1.0, self.sendAction)
		self.clearthread.run()

	def initSerial(self):
		global g_com
		self.m = serialapi.master(g_com)
		self.m.run()

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
		checksum = 0x00
		for datitem in dat.buf:
			checksum += datitem
		checksum = 0xff & checksum
		return checksum

	def getSendingBuffer(self, addr, data, type):
		buf = buffer.outBuffer()
		buf.setBytes(b"\x02")
		buf.setByte(addr)
		buf.setBytes(b"\x4D")
		buf.setBytes(type)
		buf.setBytes(data)

		cksm = self.checksum_calc(buf)

		buf.setByte(cksm)

		buf.setBytes(b"\x03")
		log.info("_request type " + str(type) + " " + str(addr) + " " + str(data) + " rawData " + str(buf))
		return buf.buf

	def b1clicked(self):
		global g_isRunning

		g_isRunning = not g_isRunning

	def b2clicked(self):
		buf = self.getSendingBuffer(EC_NUM, EC_STATUS_STATUS, EC_STATUS)
		self.sendData(buf)

	def sendData(self, buf):
		# v1 = utility.now()
		# v2 = datetime.datetime(year=2019, month=8, day=10)
		# if v1 > v2:
		# 	return

		def onRecived(result):
			self.resultHandler(result)

		if g_isViaTcp:
			try:
				result = self.sendViaTcp(buf)
				self.resultHandler(result)
			except Exception as ex:
				ret = QMessageBox.warning(self, "错误", str(ex),
										  QMessageBox.Ok)
		else:
			self.m.onRecived = onRecived
			self.m.send(buf)

	def resultHandler(self, result):
		# result.getBuf(10)
		log.info("从TCP返回" if g_isViaTcp else "从串口485返回")
		ret = bytes(result.getBuf(result._len))
		try:
			if ret[0] == 0x02 and ret[-1] == 0x03:
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
					log.info("状态位:" + tempstr + ",运行位:" + baseStatus)
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

					isSubCloosed = -1
					isOpening = int(tempstr[-4])
					isClosing = int(tempstr[-5])
					isFinishOpen = int(tempstr[-7])
					isOutOfService = int(tempstr[-6])

					floor = ret[4]
					log.info('开门中', isOpening)
					log.info('关门中', isClosing)

					log.info('主门是否关闭', isFinishOpen)
					# log.info('副门是否关闭',isSubCloosed)
					log.info('是否运行中', isRunning)
					log.info('是否在维护（不可用）', '消防维护' if isOutOfService == 1 else '正常可用')
					log.info('上行', isUpward)
					log.info('下行', isDownward)
					log.info('物理楼层', floor)

					self.statisticsView1.updateValue(isOpening)
					self.statisticsView2.updateValue(isClosing)
					self.statisticsView3.updateValue(isRunning)
					self.statisticsView4.updateValue('消防维护' if isOutOfService == 1 else '正常可用')
					self.statisticsView5.updateValue(isUpward)
					self.statisticsView6.updateValue(isDownward)
					self.statisticsView7.updateValue(floor)
					self.statisticsView8.updateValue(isFinishOpen)

					if isFinishOpen == 0 and isClosing == 0 and isOpening == 0:
						doorStatus = 1
					else:
						doorStatus = 0
					self.statisticsView11.updateValue(doorStatus)


				elif ret[3] == 0x35:
					if ret[4] == 0x01:
						fdoor = True
					else:
						fdoor = False
					if ret[5] == 0x01:
						rdoor = True
					else:
						rdoor = False
					log.info("前门登记{0}，后门登记{1}".format(('成功' if fdoor else '失败'), ('成功' if rdoor else '失败')))

				elif ret[3] == 0x36:
					if ret[4] == 0xff:
						fhold = True
					else:
						fhold = False
					if ret[5] == 0xff:
						rhold = True
					else:
						rhold = False
					log.info("前门开门{0}，后门开门{1}".format(('保持' if fhold else '释放'), ('保持' if rhold else '释放')))
		except Exception as e:
			log.warning(e)

	def b3clicked(self):
		buf = self.getSendingBuffer(EC_NUM, EC_STATUS_STATUS, EC_STATUS)
		self.sendData(buf)

	def b4clicked(self):
		currentFloor = self.floorEditor.value()

		if self.radio1.isChecked():
			frontDoor = ord(str(currentFloor).encode('utf-8'))
		else:
			frontDoor = 0x00

		if self.radio2.isChecked():
			rearDoor = ord(str(currentFloor).encode('utf-8'))
		else:
			rearDoor = 0x00

		floorData = bytes([frontDoor, rearDoor])
		buf = self.getSendingBuffer(EC_NUM, floorData, EC_GOFLOOR)
		self.sendData(buf)

	def b6clicked(self):
		if not self.radio3.isChecked() and not self.radio4.isChecked():
			buf = self.getSendingBuffer(EC_NUM, EC_DOORCTRL_NONE, EC_DOOROPENCTRL)
		elif not self.radio3.isChecked() and self.radio4.isChecked():
			buf = self.getSendingBuffer(EC_NUM, EC_DOORCTRL_SUB, EC_DOOROPENCTRL)
		elif self.radio3.isChecked() and not self.radio4.isChecked():
			buf = self.getSendingBuffer(EC_NUM, EC_DOORCTRL_MAIN, EC_DOOROPENCTRL)
		elif self.radio3.isChecked() and self.radio4.isChecked():
			buf = self.getSendingBuffer(EC_NUM, EC_DOORCTRL_BOTH, EC_DOOROPENCTRL)
		self.sendData(buf)

	def b7clicked(self):
		if not self.radio3.isChecked() and not self.radio4.isChecked():
			buf = self.getSendingBuffer(EC_NUM, EC_DOORCTRL_NONE, EC_DOORCLOSECTRL)
		elif not self.radio3.isChecked() and self.radio4.isChecked():
			buf = self.getSendingBuffer(EC_NUM, EC_DOORCTRL_SUB, EC_DOORCLOSECTRL)
		elif self.radio3.isChecked() and not self.radio4.isChecked():
			buf = self.getSendingBuffer(EC_NUM, EC_DOORCTRL_MAIN, EC_DOORCLOSECTRL)
		elif self.radio3.isChecked() and self.radio4.isChecked():
			buf = self.getSendingBuffer(EC_NUM, EC_DOORCTRL_BOTH, EC_DOORCLOSECTRL)
		self.sendData(buf)

	def sendAction(self):
		global g_isRunning
		if g_isRunning:
			buf = self.getSendingBuffer(EC_NUM, EC_STATUS_STATUS, EC_STATUS)
			self.sendData(buf)
		else:
			pass


def test_getSendingBuffer():
	import sys
	from PyQt5.QtWidgets import QApplication
	app = QApplication(sys.argv)
	w = Debug()
	buf = w.getSendingBuffer(EC_NUM, EC_STATUS_STATUS, EC_STATUS)
	assert buf

	sys.exit(app.exec_())


if __name__ == '__main__':
	import sys
	from PyQt5.QtWidgets import QApplication

	utility.start()
	app = QApplication(sys.argv)
	w = Window()


	@mytimer.interval(1000)
	def sendData():
		w.d.sendAction()


	w.show()
	sys.exit(app.exec_())
# test_getSendingBuffer()
