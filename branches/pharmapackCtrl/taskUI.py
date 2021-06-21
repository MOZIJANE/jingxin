#coding=utf-8
# ycat			2019-11-25	  create 
import os
import sys
import PyQt5 
import time
import datetime
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
	
import log
import local
import qtutility,utility 
import ui.tableDlg
import mongodb as db 
import json_codec as json
import mongodb as db

class agvTaskUI(PyQt5.QtWidgets.QWidget): 
	def __init__(self,ip=None,port=None):
		super(agvTaskUI, self).__init__()   
		self.setWindowTitle("AGV任务列表")
		self.setMinimumSize(800,400)
		self.table = ui.tableDlg.tableWidget()
		
		self.table.header.setSectionResizeMode(PyQt5.QtWidgets.QHeaderView.ResizeToContents|PyQt5.QtWidgets.QHeaderView.Interactive)
		self.table.addColumn("名称")
		self.table.addColumn("任务ID")
		# self.table.addColumn("任务类型")
		self.table.addColumn("AGV")
		self.table.addColumn("任务当前步骤")
		self.table.addColumn("任务状态")
		self.table.addColumn("状态机") 
		self.table.addColumn("创建时间")
		self.table.addColumn("开始时间")
		self.table.addColumn("结束时间")
		self.table.addColumn("消息")
		
		
		if ip is None or port is None:
			ip = local.get("taskUI","ip","127.0.0.1")
			port = local.get("taskUI","port",5550)
		self.url = 'http://%s:%s'%(ip,port)
		
		self.countN = 5
		if __name__ == '__main__':
			self.first = False
		else:
			self.first = True
			
		layout = PyQt5.QtWidgets.QVBoxLayout(self)  
		layout.addWidget(self.table) 
		# layout.setContentsMargins(0,0,0,0)
		self.setLayout(layout) 
		
		self.timer = PyQt5.QtCore.QTimer(self) #初始化一个定时器
		self.timer.timeout.connect(self.autoUpdateTask) #计时结束调用operate()方法
		self.timer.start(5000)
		
	def updateTaskBydb(self):
		order = self.getColOrder()
		tasks = getScadaTask() + getFeedTask()
		c = self.table.count
		for i in range(c):
			self.table.remove(c-1-i)
		
		tasks = sortTask(tasks)
		count = len(tasks)
		for i in range(count):
			if order:
				v = list(tasks[i].values())
			else:
				v = list(tasks[count-i-1].values())
		
			index = self.table.addRow(v)
			self.table.setItemColor(index,4,bgColor=getColor(v[4]))
		# self.table.sort(6,order)
	
	def getColOrder(self):
		if self.table.count <= 1:
			return False
		else:
			for i in range(self.table.count-1):
				row1 = self.table.getItemText(i,6)
				row2 = self.table.getItemText(i+1,6)
				if row1 != row2:
					return row1 < row2
			return False
		
	def autoUpdateTask(self):
		if self.first:
			#服务器未启动，第一次不更新
			self.first = False
			if __name__ != '__main__':
				return
		try:
			if self.countN < 5:
				self.countN = self.countN + 1
			else:
				self.countN = 0
				self.countN = 0
				self.updateTaskBydb()
				
			tasks = self.getCurrentStatus()
			for task in tasks: 
				result = self.table.model.findItems(task["id"],PyQt5.QtCore.Qt.MatchExactly,1)
				if result:
					index = result[0].row()
					self.table.setItem(index,5,task["status"])
		except Exception as e:
			log.exception("update task error:",e)
		return 
		
	def getCurrentStatus(self):
		import webutility
		url = self.url+ "/api/scada/getTaskStatus" 
		r = webutility.http_get(url, None, timeout=30,writelog=False)
		result = json.load(r)
		if result["errorno"] != 0: 
			raise Exception(result["errormsg"])
		return result["status"]
	
def getScadaTask():
	t = datetime.datetime.now()
	t = t - datetime.timedelta(days=1)
	ds = db.find("u_scada_task",{"createTime": {"$gt": t}})
	ret = []
	while ds.next():
		i = {
			"name": ds["taskName"],
			"id": str(ds["_id"]),
			# "type": ds["type"],
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
	
	return ret
	
def getFeedTask():
	t = datetime.datetime.now()
	t = t - datetime.timedelta(days=1)
	ds = db.find("u_agv_task",{"starttime": {"$gt": t}})
	ret = []
	while ds.next():
		i = {
			"name": ds["taskName"],
			"id": str(ds["_id"]),
			# "type": ds["taskType"],
			"agvId": ds["agvId"],
			"step": "",
			"status": getFeedStatus(ds["status"]),
			"s": '',
			"createTime": ds["starttime"].strftime('%Y-%m-%d %H:%M:%S') if ds["starttime"] else '',
			"startTime": ds["starttime"].strftime('%Y-%m-%d %H:%M:%S') if ds["starttime"] else '',
			"endTime": ds["endtime"].strftime('%Y-%m-%d %H:%M:%S') if ds["endtime"] else '',
			"failMsg": ds["msg"]
			
		}
		ret.append(i)
	return ret

def getFeedStatus(s):
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
	
def getColor(status):
	if status is None:
		return "white"
	elif status == "fail":
		return "red"
	elif status == "error":
		return "yellow"
	elif status == "working" or status == "running":
		return "grey"
	elif status == "finished" or status == "success":
		return "green"
	elif status == "waiting":
		return "white"
	else:
		return "white"

def sortTask(task):
	if(len(task)>1): 
		mid=task[len(task)//2]
		left,right=[],[]
		task.remove(mid)
		midv = list(mid.values())[6]
		for i in range(len(task)):
			v = list(task[i].values())[6]
			if v > midv:
				right.append(task[i])
			else:
				left.append(task[i]) 
		return sortTask(left)+[mid]+sortTask(right) 
	else:
		return task
	
def run_app():
	app = PyQt5.QtWidgets.QApplication(sys.argv)
	mainWin = agvTaskUI() 
	mainWin.show() 
	sys.exit(app.exec_())
	
if __name__ == '__main__':
	run_app()
	