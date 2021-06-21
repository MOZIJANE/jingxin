#!/usr/bin/env python
#coding=utf-8
# ycat			2019-11-12	  create
import os,sys 
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import utility
import PyQt5   
import local
import qtawesome as qta
import log
import ui.logWidget
import ui.chartWidget
import mapMgr
import agvUI,mapUI,taskWidget
import openDlg
import alarm.alarmWidget
import config


class MainWindow(PyQt5.QtWidgets.QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__() 
		self.createActions()
		#self.createMenus()
		self.createToolBars()
		self.createStatusBar()
		self.createDockWindows()
		self.setMinimumSize(1024,768)
		self.setWindowIcon(qta.icon('fa.object-group',color='gold'))

		self.mapTab = PyQt5.QtWidgets.QTabWidget()
		self.mapTab.setTabsClosable(True)
		#setTabButton(index,position,*widget) 
		self.mapTab.setIconSize(PyQt5.QtCore.QSize(18,18)) 
		self.mapTab.tabCloseRequested.connect(self.closeMap)
		
		#self.textEdit = voteDlg.voteDlg()
		self.setCentralWidget(self.mapTab) 
		self.setWindowTitle("京信调度系统V2.0")
		
		self.timer = PyQt5.QtCore.QTimer(self) #初始化一个定时器
		self.timer.timeout.connect(self.autoUpdateMap) #计时结束调用operate()方法
		self.timer.start(3000)
		
		
	def closeEvent(self,event):
		import qtutility
		if not qtutility.alert(msg="是否退出AGV调度系统？", acceptStr = '确定', rejectStr = '取消'):
			event.ignore()
			return
		utility.finish()
		 
	def createMenus(self):
		self.fileMenu = self.menuBar().addMenu("&File") 
		self.fileMenu.addAction(self.openAct) 
		self.fileMenu.addSeparator()
	
	def createActions(self):
		self.openAct = PyQt5.QtWidgets.QAction(qta.icon('fa.folder-open-o',color='sienna'), "&Home", triggered=self.open)
  
		self.homeAct = PyQt5.QtWidgets.QAction(qta.icon('fa.home',color='green'), "复位", triggered=self.home)
		self.backAct = PyQt5.QtWidgets.QAction(qta.icon('fa.undo',color='aquamarine'), "前一视图", triggered=self.back)
		self.forwardAct = PyQt5.QtWidgets.QAction(qta.icon('fa.repeat',color='aquamarine'), "后一视图", triggered=self.forward)
		self.zoomAct = PyQt5.QtWidgets.QAction(qta.icon('fa.search',color='darkorchid'), "缩放", triggered=self.zoom)
		self.zoomAct.setCheckable(True) 
		self.moveAct = PyQt5.QtWidgets.QAction(qta.icon('fa.arrows',color='orange'), "移动", triggered=self.move)
		self.moveAct.setCheckable(True) 
		self.saveAct = PyQt5.QtWidgets.QAction(qta.icon('fa.save',color='darkcyan'), "截图", triggered=self.save)
		
		self.showPointAct = PyQt5.QtWidgets.QAction(qta.icon('fa.th',color='gray'), "环境", triggered=self.showPoint)
		self.showPointAct.setCheckable(True) 
		self.showTextAct = PyQt5.QtWidgets.QAction(qta.icon('fa.font',color='blue'), "描述", triggered=self.showText)
		self.showTextAct.setCheckable(True) 
		self.showTextAct.setChecked(False)
	
	def createDockWindows(self): 
		dock1 = PyQt5.QtWidgets.QDockWidget("列表", self)
		self.agvTable = agvUI.agvTableUI()  
		dock1.setWidget(self.agvTable) 
		self.addDockWidget(PyQt5.QtCore.Qt.BottomDockWidgetArea, dock1)  
		
#		dock2 = PyQt5.QtWidgets.QDockWidget("任务", self)
#		dock2.setWidget(taskWidget.taskWidget())
#		self.addDockWidget(PyQt5.QtCore.Qt.BottomDockWidgetArea, dock2) 
#		self.tabifyDockWidget(dock1,dock2)
		
#		dock3 = PyQt5.QtWidgets.QDockWidget("告警", self)
#		dock3.setWidget(alarm.alarmWidget.alarmWidget(isActiveAlarm=True))
#		self.addDockWidget(PyQt5.QtCore.Qt.BottomDockWidgetArea, dock3) 
#		self.tabifyDockWidget(dock2,dock3)
#		
#		if local.get("project","name") == "fastprint" and config.getbool("mongo","enable",True) and not utility.is_test():
#			import scadaCtrl.taskUI as taskUI
#			dock4 = PyQt5.QtWidgets.QDockWidget("SCADA列表", self)
#			self.taskTable = taskUI.agvTaskUI()  
#			dock4.setWidget(self.taskTable) 
#			self.addDockWidget(PyQt5.QtCore.Qt.BottomDockWidgetArea, dock4) 
#			self.tabifyDockWidget(dock3,dock4)
		
		#dock4 = PyQt5.QtWidgets.QDockWidget("输出", self)
		#self.logger = ui.logWidget.logWidget() 
		#self.logger.setupLog()
		#dock4.setWidget(self.logger) 
		#self.addDockWidget(PyQt5.QtCore.Qt.BottomDockWidgetArea, dock4) 
		#
		#self.tabifyDockWidget(dock3,dock4)
		dock1.raise_()
		
	
	def createToolBars(self):
		self.fileToolBar = self.addToolBar("File") 
		self.fileToolBar.addAction(self.openAct) 
		self.fileToolBar.setIconSize(PyQt5.QtCore.QSize(26,26)) 

		self.mapToolbar = self.addToolBar("Edit")
		self.mapToolbar.addAction(self.homeAct) 
		self.mapToolbar.addAction(self.backAct) 
		self.mapToolbar.addAction(self.forwardAct) 
		self.mapToolbar.addAction(self.zoomAct) 
		self.mapToolbar.addAction(self.moveAct) 
		self.mapToolbar.addSeparator()
		self.mapToolbar.addAction(self.saveAct)   
		self.mapToolbar.setIconSize(PyQt5.QtCore.QSize(26,26)) 
		
		self.viewToolBar = self.addToolBar("View") 
		self.viewToolBar.addAction(self.showPointAct) 
		self.viewToolBar.addAction(self.showTextAct) 
		self.viewToolBar.setIconSize(PyQt5.QtCore.QSize(26,26)) 
		#self.mapToolbar.setToolButtonStyle(PyQt5.QtCore.Qt.ToolButtonTextUnderIcon)		 

	def createStatusBar(self):
		self.statusBar().showMessage("Ready")
	
	################ other ################
	def autoUpdateMap(self):
		import mapMgr
		import agvList 
		import elevatorMgr   
		agvList.getAgvList()  
		if not agvList.g_mapIdList:
			return
		mm2 = []
		mm = utility.clone(agvList.g_mapIdList)  
		for m in mm:
			if not mapMgr.isActived(m):
				continue
			mm2.append(m) 
			for e in elevatorMgr.getMaps(m):
				mm2.append(e)
   
		mm = self.getOpenMaps() 
		for m in mm2: 
			if m not in mm:
				self.openMap(m)
		
	def getOpenMaps(self):
		mm = []
		for i in range(self.mapTab.count()):
			mm.append(self.mapTab.tabText(i))
		return mm
		
	def closeMap(self,index):
		self.mapTab.removeTab(index)
		
	################ action ################
	def openMap(self,mapId,closeable=False):
		mm = self.getOpenMaps()
		if mapId in mm:
			return mm.index(mapId)
		import mapMgr
		a = mapUI.mapUI(mapMgr.getMap(mapId),showText=self.showTextAct.isChecked()) 
		i = self.mapTab.addTab(a,qta.icon('fa.map-o',color='blue') ,mapId) 
		if not closeable:
			self.mapTab.tabBar().setTabButton(i,PyQt5.QtWidgets.QTabBar.RightSide,None)
		return i
	
	def open(self):
		dlg = openDlg.openDlg()
		dlg.exec()
		if dlg.mapId:
			i = self.openMap(dlg.mapId,closeable=True)
			self.mapTab.setCurrentIndex(i)
		
	def home(self):
		self.mapTab.currentWidget().home()
	
	def back(self):
		self.mapTab.currentWidget().back()
		
	def forward(self):
		self.mapTab.currentWidget().forward()
		
	def zoom(self):	 
		self.moveAct.setChecked(False) 
		for i in range(self.mapTab.count()):
			self.mapTab.widget(i).zoom()
		#self.mapTab.currentWidget().zoom()
		
	def move(self):
		self.zoomAct.setChecked(False) 
		for i in range(self.mapTab.count()):
			self.mapTab.widget(i).move()
		#self.mapTab.currentWidget().move()
		
	def save(self):
		self.mapTab.currentWidget().save()
	
	def showPoint(self):
		for i in range(self.mapTab.count()):
			self.mapTab.widget(i).repaint(self.showPointAct.isChecked(),self.showTextAct.isChecked())
		
	def showText(self):
		self.showPoint()
		
g_app = None


def createApp():
	global g_app
	if g_app:
		return
	g_app = PyQt5.QtWidgets.QApplication(sys.argv)
	return g_app


def show(mapId=None): 
	app = createApp()
	mainWin = MainWindow()
	if mapId:
		mainWin.openMap(mapId)
	mainWin.show()
	if not utility.is_test():
		mainWin.showMaximized()
	sys.exit(app.exec_())


if __name__ == '__main__': 
	show()
