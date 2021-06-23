#coding=utf-8 
# ycat			2019-11-03	  create
import os,sys
import math
import PyQt5  
import qtawesome as qta
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__) 
import agvList
import mapMgr
import utility
import local
import enhance
import log
import ui.listDlg
import qtutility
import datetime

class agvTableUI(PyQt5.QtWidgets.QWidget): 
	def __init__(self):
		super(agvTableUI, self).__init__()  
		self.table = self.createTable()
		layout = PyQt5.QtWidgets.QHBoxLayout()
		layout.addWidget(self.table) 
		self.setLayout(layout)
		self.setWindowIcon(qta.icon('fa.diamond',color='blue'))
		self.columns = []
		self.timer = PyQt5.QtCore.QTimer(self) #初始化一个定时器
		self.timer.timeout.connect(self.autoUpdateAgv) #计时结束调用operate()方法
		self.timer.start(3000)
		
		 
	def createTable(self):
		table = PyQt5.QtWidgets.QTableWidget()
		table.setFixedHeight(350)
		columns = ["名称","电量","状态","置信度","任务ID","任务状态", "当前位置", "当前目标","任务目标","描述","操作"]
		table.setColumnCount(len(columns)) 
		table.setEditTriggers(PyQt5.QtWidgets.QAbstractItemView.NoEditTriggers)
		table.setSelectionBehavior(PyQt5.QtWidgets.QAbstractItemView.SelectRows)
		table.setSelectionMode(PyQt5.QtWidgets.QAbstractItemView.SingleSelection)

		table.setHorizontalHeaderLabels(columns)
		table.setVerticalScrollBarPolicy(False)
		table.setHorizontalScrollBarPolicy(False)
		head = table.horizontalHeader()
#		head.setStretchLastSection(True)
		head.setSectionsClickable(False)
		head.setSectionResizeMode(PyQt5.QtWidgets.QHeaderView.ResizeToContents)
		s = "QHeaderView::section {""color: black;padding-left: 4px;border: 1px solid #6c6c6c;}"
		head.setStyleSheet(s)
		
		v = table.verticalHeader()
		v.setSectionsClickable(False)
		v.setStyleSheet(s) 
		return table
		
	def onClickTable(self,event):
		pass
		
	#QTableWidgetItem 
	def tableItemChanged(self, current, previous): 
		pass
	
	def getBatteryIcon(self,level,isCharged):
		#if isCharged:
		#	return "fa.plug","gold" 
		if level <= 0.1:
			return "fa.battery-0","red"
		if level <= 0.3:
			return "fa.battery-1","orange"
		if level <= 0.5:
			return "fa.battery-2","blue"
		if level <= 0.8:
			return "fa.battery-3","blue"
		return "fa.battery-4","green"
		
	def getTaskStatus2(self,agv):
		a = agv.action
		if a == "none":
			return ""
		t = agv.agvElement.nextTargetPosName
		if not t:
			return ":"+a
		return ":"+a+"("+str(t)+")"
		
	def getTaskStatus(self,v):
		if v == -1:
			return "未知"
		if v == 0:
			return ""
		if v == 1:
			return "等待"
		if v == 2:
			return "运行"
		if v == 3:
			return "暂停"
		if v == 4:
			return "完成"
		if v == 5:
			return "失败"
		if v == 6:
			return "取消"
		return "未知"+str(v)
	
	def getAgvStatus(self,agv): 
		if agv.status  is None:
			return "未连接"
		if agv.mapId is None:
			return "没有地图"
		if agv._initState != 1:
			return "未初始化"
		if not agv.isLinked:
			return "断线"
		if not agv._alarmObj.isActive():
			return "网络异常"
		if agv._hasAlarm:
			return "告警"
		if agv._isBlocked:
			return "阻挡"
		if agv._isEmergency:
			return "急停"
		if not agv._curTarget:
			return "无位置"
		if agv.status: 
			if agv.batteryLevel < local.getfloat("charge","start_charge_level",0.2):
				return "低电量"
			if agv.status["loadmap_status"] != 1:
				return "载入地图失败" 
			if agv.status["reloc_status"] != 1:
				return "重定位失败"
		return ""
	
	def getAgvStatus2(self,agv):
		a = agv.agvElement
		if not a:
			return ""
		agvs = agv.agvElement.blockAgvs[:]
		t = ""
		if a.isDeadlock: 
			t = "[拥塞] "
		if a.isBlocked:
			return t+"block failed("+",".join(agvs)+")"
		if a.checkFailed:
			return t+"check failed("+",".join(agvs)+")"
		return "" 

	def updateAgv(self,agv,rowIndex,insert):
		def set(col,text):
			if isinstance(text,str):
				item = PyQt5.QtWidgets.QTableWidgetItem(text)           
			else:
				item = text
			#item.setBackground(PyQt5.QtGui.QBrush(PyQt5.QtGui.QColor("gainsboro")))
			self.table.setItem(rowIndex,col,item)
			return item
		
		if agv.lockApp is not None:
			icon = "fa.lock"
			c = "blue"
		elif agv._taskInfo is not None or agv.isMoving():
			icon = "fa.car"
			c = "blue"
		elif agv.isAtHome:
			icon = "fa.home"
			c = "green"
		elif agv.isCharge:
			icon = "fa.plug"
			c = "gold" 
		else:
			icon = "fa.ellipsis-h"
			c = "green"
		item = PyQt5.QtWidgets.QTableWidgetItem(qta.icon(icon,color=c),agv.agvId)
	     	
		item.data = agv.agvId                    	 
		i = 0
		set(i,item) 
		if agv.status is None:
			i += 2
			item = PyQt5.QtWidgets.QTableWidgetItem(qta.icon("fa.warning",color="red"),"无法连接")
			set(i,item) 
			return 
		
		b,c = self.getBatteryIcon(agv.batteryLevel,agv.isCharge)
		item = PyQt5.QtWidgets.QTableWidgetItem(qta.icon(b,color=c),"%d%%"%int(agv.batteryLevel*100))    
		i += 1     		
		set(i,item)
		
		i += 1   
		icon = "fa.check-circle"
		n = self.getAgvStatus(agv)
		if n == "":
			n = self.getAgvStatus2(agv)
			if n == "":
				n = "正常"
				c = "green"
			else:
				icon = "fa.warning"
				c = "orange"
		else:
			icon = "fa.warning"
			c = "red"
		if agv.hasShelve:
			n += "[顶升]"
		item = PyQt5.QtWidgets.QTableWidgetItem(qta.icon(icon,color=c),n+"\t")
		set(i,item) 
		
		s = agv.status
		i += 1       	
		c = s["confidence"]
		if c is None:
			c = 0
		set(i,"%d%%"%int(100*c))
		
		i += 1 
		if agv.taskId:
			set(i,agv.taskId)
		elif agv.lockTaskId:
			set(i,"lock:"+agv.lockTaskId)
		else:
			set(i,"")
		
		i += 1 
		set(i,self.getTaskStatus(agv.task_status)+self.getTaskStatus2(agv))
		
		i += 1       	
		set(i,mapMgr.formatLoc(agv.mapId,agv.curTarget)+"\t")        
		 
		i += 1 
		n = "-"
		if agv.agvElement and agv.agvElement.nextTargetPosName:
			n = agv.agvElement.nextTargetPosName
		set(i,n) 
		i += 1 
		n = "-"
		if agv.agvElement and agv.agvElement.targetList:
			n = agv.agvElement.targetList[-1]
		set(i,n)
		#i += 1
		#set(i,"x:%0.2f,y:%0.2f,r:%0.2f\t"%(agv.x,agv.y,math.degrees(agv.angle))) 
		
		i += 1
		msg = ''
		idList = []
		alarmIdDict = getAlarmId()
		if "fatals" in s:
			idList = idList + s["fatals"]
		if "errors" in s:
			idList = idList + s["errors"]
		if "warnings" in s:
			idList = idList + s["warnings"]
		for keys in idList:
			for id in keys:
				if id == "desc" or id == "times":
					continue
				if str(id) == "54018":
					continue
				m = alarmIdDict[str(id)] if str(id) in alarmIdDict else str(id)
				msg = msg + "[%s]"%m
		if not msg:
			if agv.idleSeconds != 0:
				msg = "空闲:"+str(datetime.timedelta(seconds=int(agv.idleSeconds)))
			else:
				msg = "执行:"+str(datetime.timedelta(seconds=int(agv.taskSeconds)))
		set(i,msg) 
		i+=1
		self.updateButtons(rowIndex,i,agv)
		
	def updateButtons(self,row,col,agv):
		w = self.table.cellWidget(row,col)
		if w is None:
			self.addButtons(row,col,agv)
			w = self.table.cellWidget(row,col)
		#w.setFixedSize(400,35)
		i = 0
		l = w.layout()
		b = l.itemAt(i).widget()
		b.setEnabled(agv.isLock() and not agv.isRunning())
		i += 1
		b = l.itemAt(i).widget()
		b.setEnabled(not agv.isLock() and agv.homeLoc != "" and not agv.isHomeTask)
		if agv.isAtHome:
			b.setEnabled(False)
		i += 1
		b = l.itemAt(i).widget()
		b.setEnabled(agv.lockApp == "user" or not agv.isLock()) #
		if agv.isRunning():
			b.setEnabled(False)
		i += 1
		b = l.itemAt(i).widget()
		b.setEnabled(agv.isRunning())
		i += 1
		
		b = l.itemAt(i).widget()
		if agv.pauseState:
			b.setText("恢复")
		else:
			b.setText("暂停")
		i += 1
		
		
	def addButtons(self,row,col,agv): 
		w = PyQt5.QtWidgets.QWidget()
		l = PyQt5.QtWidgets.QHBoxLayout()
		size = (55,30)
		l.setContentsMargins(0,0,0,0)
		b = PyQt5.QtWidgets.QPushButton("解锁")
		b.agvId = agv.agvId
		b.clicked.connect(self.unlockAgv)  
		b.setFixedSize(*size) 
		l.addWidget(b)
		
		b = PyQt5.QtWidgets.QPushButton("返航")
		b.agvId = agv.agvId
		b.clicked.connect(self.gohomeAgv)  
		b.setFixedSize(*size) 
		l.addWidget(b)
		
		b = PyQt5.QtWidgets.QPushButton("移动")
		b.agvId = agv.agvId
		b.clicked.connect(self.moveAgv)  
		b.setFixedSize(*size) 
		l.addWidget(b)
		 
		b = PyQt5.QtWidgets.QPushButton("取消")
		b.agvId = agv.agvId
		b.clicked.connect(self.cancelAgv)  
		b.setFixedSize(*size) 
		l.addWidget(b) 
		
		b = PyQt5.QtWidgets.QPushButton("暂停")
		b.agvId = agv.agvId
		b.clicked.connect(self.pauseAgv)  
		b.setFixedSize(*size) 
		l.addWidget(b) 
		
		w.setLayout(l)
		self.table.setCellWidget(row,col,w)
		self.updateButtons(row,col,agv)
	
	@qtutility.catch
	def pauseAgv(self,v):
		import agvControl
		agvId = self.sender().agvId
		log.info("user press pause",agvId,"button")
		if agvList.getAgv(agvId).pauseState:
			agvList.getAgv(agvId).resume()
		else:
			agvList.getAgv(agvId).pause()
	
	@qtutility.catch
	def cancelAgv(self,v):
		import agvControl
		agvId = self.sender().agvId
		log.info("user press cancel",agvId,"button")
		agvControl.cancel(agvId)
		
	@qtutility.catch
	def unlockAgv(self,v):
		import agvControl
		agvId = self.sender().agvId
		log.info("user press unlock",agvId,"button")
		agvControl.unlock(agvId,"",force=True)
	
	@qtutility.catch
	def gohomeAgv(self,v):
		import agvControl
		agvId = self.sender().agvId
		log.info("user press gohome",agvId,"button")
		agvControl.goHome(agvId,force=True) 
		
	@qtutility.catch
	def moveAgv(self,v): 
		import agvControl
		agvId = self.sender().agvId
		log.info("user press moveAgv",agvId,"button")
		list = ui.listDlg.listDlg(isIconMode=False)
		m = agvList.getAgv(agvId).map
		pp = []
		for p in m.positions:
			pp.append(p.name)
		pp.sort()
		for p in pp:
			list.add(p,p,qta.icon("fa.map-marker",color="green"))  
		list.selected.connect(enhance.bind(self.selectPos,agvId))
		list.exec()
		 
	@utility.catch
	def selectPos(self,agvId,pos):
		import agvControl 
		taskId = "user_"+str(utility.ticks())
		if not agvList.getAgv(agvId).isLock():
			agvControl.lock(agvId,taskId=taskId,appName="user") 
		agvControl.move(agvId,pos,taskId,timeout=30*5,finishCallback=None)
	
	@utility.catch
	def autoUpdateAgv(self):
		try:
			agvs = agvList.getAgvList() 
			for a in agvs: 
				result = self.table.findItems(a,PyQt5.QtCore.Qt.MatchExactly)
				if not result:
					self.table.insertRow(self.table.rowCount())
					index = self.table.rowCount() - 1
					insert = True
				else:
					index = result[0].row()
					insert = False
				agv = agvs[a]
				self.updateAgv(agv,index,insert=insert)
			return 
		except Exception as e:
			log.exception("updateagv",e)
			
g_alarmId = None
def getAlarmId():
	global g_alarmId
	if g_alarmId is None:
		import json
		file = os.path.join(os.path.abspath(os.path.dirname(__file__)), "alarm.json")
		with open(file, 'r',encoding="utf_8") as f:
			g_alarmId = json.load(f)
	return g_alarmId
	
if __name__ == '__main__':
	import time
	utility.start()
	
	while True: 
		#等待所有agv上线 
		aa = agvList.getAgvList()
		for a in aa:
			if aa[a].status is None:
				time.sleep(0.5) 
				break
		else:
			time.sleep(0.5)
			break 

	app = PyQt5.QtWidgets.QApplication(sys.argv)
	
	class dlg(PyQt5.QtWidgets.QDialog): 
		def __init__(self):
			super(dlg, self).__init__() 
			layout = PyQt5.QtWidgets.QHBoxLayout()
			nn = agvTableUI() 
			layout.addWidget(nn)
			 
			self.setLayout(layout)
			self.setWindowTitle("QT测试")	 	
			self.setMinimumSize(400,400)
			 
	d = dlg() 
	d.show() 
	sys.exit(app.exec_())
