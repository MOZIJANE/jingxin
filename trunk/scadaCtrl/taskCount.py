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

		self.timer = QTimer(self) 						#初始化一个定时器
		self.timer.timeout.connect(self.autoUpdateTask) #计时结束调用operate()方法
		self.timer.start(1000)


	def init_ui(self):
		self.setFixedSize(960, 700)
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
		titleFont.setPointSize(12)
		

		for i in range(30,0,-1):
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
			ret.append(i)
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
		conclude = {}
		rr = ''
		total = len(data)
		failList = []
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
			
			if status=='success':
				continue
			if failMsg=="任务成功":
				continue
			failList.append(failMsg)
		suc = 0
		fail = 0
		
		error = 0
		for k,v in conclude.items():
			if k == 'success':
				suc =v
			elif k == 'fail':
				fail =v
			else:
				error = v
		fail = fail + error 

		f1 = 0  # system error
		f2 = 0  # car error
		for x in failList:
			if not x:
				continue
			if 'task canceled' in x:
				f2 += 1
			elif 'http' in x:
				f2 += 1
			elif "block failed" in x:
				f2 += 1
			elif "unexpected" in x:
				f2 += 1
			elif "timeout" in x:
				f2 += 1
			elif "AGV0" in x:
				f2 += 1
			else:
				f1 += 1

		try:
			s = (suc/total)*100
		except Exception as e:
			s = 0

		# rr = '%s -> %s   任务总数:%s  成功总数:%s  成功率：%s   失败总数:%s' %(t1.strftime('%Y-%m-%d'),t2.strftime('%Y-%m-%d'),total,suc,'{:.2f}'.format(s),fail)
		# rr = '{} -> {}  任务总数:{}  成功总数:{}  成功率：{}%   失败总数:{}'.format(t1.strftime('%Y-%m-%d'),t2.strftime('%Y-%m-%d'),total,suc,"{:.2f}".format(s),fail)
		rr = '{}  任务总数:{:<4} 成功总数:{:<4} 成功率：{:<6}%  失败总数:{:<3} 系统故障：{:<3} 小车异常：{:<3}'.format(t1,total,suc,"{:.2f}".format(s),fail,f1,f2)
		return rr,conclude

if __name__ == '__main__':
	app = QApplication(sys.argv)
	main = MainUi()
	main.show()
	sys.exit(app.exec_())
