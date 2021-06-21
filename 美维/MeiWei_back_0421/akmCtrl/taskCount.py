import qtawesome as qta
import sys
import base64
import os
import time,datetime
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import json
import setup as setup


if __name__ == '__main__':
	setup.setCurPath(__file__)
import mongodb as db


class MainUi(QMainWindow):
	def __init__(self):
		super().__init__()
		self.init_ui()

		if __name__ == '__main__':
			self.first = False
		else:
			self.first = True

		self.countN = 0

		self.timer = QTimer(self) #初始化一个定时器
		self.timer.timeout.connect(self.autoUpdateTask) #计时结束调用operate()方法
		self.timer.start(1000)


	def init_ui(self):
		self.setFixedSize(1280, 700)
		self.main_widget = QWidget()
		self.main_layout = QGridLayout()
		self.main_widget.setLayout(self.main_layout)

		self.left_widget = QWidget()
		self.left_widget.setObjectName('left_widget')
		self.left_layout = QGridLayout()
		self.left_widget.setLayout(self.left_layout)

		self.main_layout.addWidget(self.left_widget, 0,0,1,1)
		self.content = QVBoxLayout()

		titleFont = QFont()
		titleFont.setPointSize(16)
		

		for i in range(15,0,-1):
			text1,taskStatusDict1 = self.getScadaTask(i,1)
			label1 = QLabel(text1)
			label1.setFont(titleFont)
			self.left_layout.addWidget(label1, i,0,1,1)

		self.btn1 = QPushButton()
		self.btn1.setText(text1)
		self.setCentralWidget(self.main_widget)
		self.setWindowIcon(qta.icon('fa.superpowers'))

	def autoUpdateTask(self):
		if self.first:
			self.first = False
			if __name__=='__main__':
				return

		try:
			if self.countN < 5:
				self.countN = self.countN + 1
			else:
				self.countN = 0
				self.init_ui()
		except Exception as e:
			print('Exception in autoUpdateTask')


	def getScadaTask(self,date=1,day=0):
		# t = datetime.datetime.now()
		# t1 = t - datetime.timedelta(days=date)
		# t2 = t1 + datetime.timedelta(days=day)

		# t = datetime.datetime.today()
		# t1 = t - datetime.timedelta(days=date)
		# t2 = t1 + datetime.timedelta(days=day)

		t = datetime.datetime.today() - datetime.timedelta(days=date-1)
		t2 = t + datetime.timedelta(days=day)

		t1 = t.strftime("%Y-%m-%d")
		t2 = t2.strftime("%Y-%m-%d")
		tt1 = datetime.datetime.strptime(t1,'%Y-%m-%d')
		tt2 = datetime.datetime.strptime(t2,'%Y-%m-%d')

		# print('tt1.....',tt1, 'tt2----------',tt2)

		ds = db.find("u_scada_task",{"createTime": {"$gt": tt1, "$lt":tt2}})
		ret = []
		while ds.next():

			i = {
				"name": ds["taskName"],
				"id": str(ds["_id"]),
				"agvId": ds["agvId"],
				"step": ds["step"],
				"status": ds["status"],
				"s": '',
				"createTime": ds["createTime"].strftime('%Y-%m-%d %H:%M:%S') if ds["createTime"] else '',
				"startTime": ds["startTime"].strftime('%Y-%m-%d %H:%M:%S') if ds["startTime"] else '',
				"endTime": ds["endTime"].strftime('%Y-%m-%d %H:%M:%S') if ds["endTime"] else '',
				"failMsg": ds["failMsg"]
			}
			if ds["agvId"] is None or ds["agvId"] == "":
				continue
			ret.append(i)
		# print('scada tasks----->>>',ret, len(ret))
		r = self.calculate(ret,t1,t2)
		return r

	def getFeedTask(self, type=None):
		# t = datetime.datetime.now()
		# t = t - datetime.timedelta(days=DAY2)
		t = datetime.datetime.today() - datetime.timedelta(days=date-1)
		t2 = t + datetime.timedelta(days=day)

		t1 = t.strftime("%Y-%m-%d")
		t2 = t2.strftime("%Y-%m-%d")
		tt1 = datetime.datetime.strptime(t1,'%Y-%m-%d')
		tt2 = datetime.datetime.strptime(t2,'%Y-%m-%d')

		ds = db.find("u_scada_task",{"createTime": {"$gt": tt1, "$lt":tt2}})
		ret = []
		while ds.next():

			i = {
				"name": ds["taskName"],
				"id": str(ds["_id"]),
				# "type": ds["taskType"],
				"agvId": ds["agvId"],
				"step": "",
				"status": self.getFeedStatus(ds["status"]),
				"s": '',
				"createTime": ds["starttime"].strftime('%Y-%m-%d %H:%M:%S') if ds["starttime"] else '',
				"startTime": ds["starttime"].strftime('%Y-%m-%d %H:%M:%S') if ds["starttime"] else '',
				"endTime": ds["endtime"].strftime('%Y-%m-%d %H:%M:%S') if ds["endtime"] else '',
				"failMsg": ds["msg"]

			}
			ret.append(i)
		# print('pda tasks------>', ret)
		r = self.calculate(ret,t1,t2)
		return r

	def getFeedStatus(self,s):
		s = int(s)
		if s == -2:
			return "fail"
		elif s == -1:
			return "error"
		elif s == 1:
			return "working"
		elif s == 0:
			return "finished"
		elif s == 2:
			return "waiting"
		else:
			return ""

	def calculate(self,data,t1,t2):
		# [
		# 	{'name': '从ZZ-AI-DG-09运送货架CA-SCJ-00033到ZZ-AI-DG-08', 'id': '5eb51638cfe1fecc4ac3d3e2', 'agvId': 'AGV04', 'step': 'moveSource', 'status': 'running', 's': '',
		# 	'createTime': '2020-05-08 16:20:08', 'startTime': '2020-05-08 16:46:49', 'endTime': '2020-05-08 16:28:10', 'failMsg': '等待分配小车'},
		# 	{'name': '从ZZ-AI-DG-09运送货架CA-SCJ-00033到ZZ-AI-DG-08', 'id': '5eb517ee9b67083fa9419874', 'agvId': 'AGV04', 'step': 'moveSource', 'status': 'running', 's': '',
		# 	'createTime': '2020-05-08 16:27:26', 'startTime': '2020-05-08 16:27:26', 'endTime': '', 'failMsg': '前往ZZ-AI-DG-09前置点'}
		# ]
		conclude = {}
		rr = ''
		total = len(data)
		for i in range(len(data)):
			task = data[i]
			name = task['name']
			id_ = task['id']
			agvId = task['agvId']
			status = task['status']
			failMsg = task['failMsg']

			if status not in conclude:
				conclude[status] = 1
			else:
				conclude[status] += 1
		suc = 0
		fail = 0
		# print('status----->', conclude, type(conclude))
		for k,v in conclude.items():
			if k == 'success':
				suc =v
			elif k == 'fail':
				fail =v
		try:
			s = (suc/total)*100
		except Exception as e:
			s = 0
		# rr = '%s -> %s   任务总数:%s  成功总数:%s  成功率：%s   失败总数:%s' %(t1.strftime('%Y-%m-%d'),t2.strftime('%Y-%m-%d'),total,suc,'{:.2f}'.format(s),fail)
		# rr = '{} -> {}  任务总数:{}  成功总数:{}  成功率：{}%   失败总数:{}'.format(t1.strftime('%Y-%m-%d'),t2.strftime('%Y-%m-%d'),total,suc,"{:.2f}".format(s),fail)
		rr = '{}   任务总数:{}  成功总数:{}  成功率：{}%   失败总数:{}'.format(t1,total,suc,"{:.2f}".format(s),fail)
		return rr,conclude

if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = MainUi()
	main.show()
	sys.exit(app.exec_())
