#coding=utf-8
# ycat			2019-11-25	  create 
import sys,os
import PyQt5 
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import qtutility,utility 
import qtawesome as qta
import ui.tableDlg
import mongodb as db 

class alarmWidget(PyQt5.QtWidgets.QWidget): 
	def __init__(self,isActiveAlarm,hasDomain=False,maxLines=100):
		super(alarmWidget, self).__init__()   
		self.setWindowTitle("告警列表")
		self.setMinimumSize(800,400)
		self.table = ui.tableDlg.tableWidget()
		self.table.header.setSectionResizeMode(PyQt5.QtWidgets.QHeaderView.ResizeToContents|PyQt5.QtWidgets.QHeaderView.Interactive)
		
		self.isActiveAlarm = isActiveAlarm
		self.hasDomain = hasDomain
		if self.hasDomain:
			self.table.addColumn("域名")
		#self.table.addColumn("ID")
		self.table.addColumn("告警级别")
		self.table.addColumn("告警对象")
		self.table.addColumn("告警类型")
		self.table.addColumn("告警原因")
		self.table.addColumn("告警描述")
		self.table.addColumn("告警时间") 
		if not isActiveAlarm:
			self.table.addColumn("清除时间")  
		self.maxLines = maxLines 
		  
		layout = PyQt5.QtWidgets.QVBoxLayout(self)  
		layout.addWidget(self.table) 
		layout.setContentsMargins(0,0,0,0)
		self.setLayout(layout) 
		
		if not db.isConnect():
			return
		self._updateAlarmType()
		self._updateAlarm()
		self.timer = PyQt5.QtCore.QTimer(self) #初始化一个定时器
		self.timer.timeout.connect(self._updateAlarm) #计时结束调用operate()方法
		self.timer.start(5000)
		
	def _getCellData(self):
		ret = {}
		for i in range(self.table.count):
			ret[self.table.getData(i,0)] = i
		return ret
		
	def _updateAlarm(self):
		data = self._getCellData()
		data2 = set()
		if self.isActiveAlarm:
			ds = db.find("r_alarm").sort("createTime",db.DESCENDING).list()
		else:
			ds = db.find("r_alarm_history").sort("clearTime",db.DESCENDING).list()
		i1 = 0 
		i2 = 5 
		if not self.isActiveAlarm:
			i2 += 1
		
		for r in ds:
			data2.add(str(r["_id"]))
		
		rr = []
		for d in data:
			if d in data2:
				continue
			rr.append(data[d])
		rr.sort(reverse=True)
		#倒着删除 
		for r in rr:
			self.table.remove(r)
		
		#data = self._getCellData()
		for r in ds:
			id = str(r["_id"])
			#data2.add(id)
			if id in data:
				continue
			reason,level,color = self.getAlarmReason(r["typeId"])
			time = utility.date2str(r["createTime"])
			row = []  
			row += [level,r["moid"],r["typeId"],reason,r["desc"],time]
			if not self.isActiveAlarm:
				row.append(utility.date2str(r["clearTime"]))
			index = self.table.addRow(row)
			i = 1
			if self.hasDomain:
				row.append(r["domain"])
			self.table.setIcon(index,i1,qta.icon("fa.bell",color=color))
			self.table.setData(index,0,id) 
		
		self.table.sort(i2,asc=False)
		
	def getAlarmLevel(self,level): 
		if level == "critical":
			return "严重告警","red"
		elif level == "major":
			return "重要告警","orange"
		elif level == "minor":
			return "轻微告警","yellow"
		elif level == "warning":
			return "警告","blue" 
		return "一般告警","blue"
	
	def getAlarmReason(self,typeId):
		if typeId in self.alarmTypes:
			t = self.alarmTypes[typeId]
			l = t["level"]
			r = t["value"]
		else:
			r = "未知原因"
			l = "major" 
		level = self.getAlarmLevel(l) 
		return r,level[0],level[1]
		
	
	def _updateAlarmType(self):
		ds = db.find("c_alarm_type").list()
		self.alarmTypes = {}
		for r in ds:
			self.alarmTypes[r["_id"]] = r 
			 
def run_app():
	app = PyQt5.QtWidgets.QApplication(sys.argv)
	mainWin = alarmWidget(isActiveAlarm=True) 
	mainWin.show() 
	sys.exit(app.exec_())
	
if __name__ == '__main__':
	run_app()
	