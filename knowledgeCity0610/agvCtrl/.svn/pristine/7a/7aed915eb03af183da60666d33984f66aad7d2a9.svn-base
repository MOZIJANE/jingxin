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
import ui.chartWidget
import mapMgr 
import log
import matplotlib.pyplot as plt  
import counter

class mapUI(ui.chartWidget.chartWidget): 
	def __init__(self,map,showText=False):
		super(mapUI, self).__init__(map.mapId,addToolbar=False)  
		self.map = map   
		self.map.draw(showPoint=False,showText=showText)
		self.timer = PyQt5.QtCore.QTimer(self)  
		self.timer.timeout.connect(self.autoUpdateAgv)
		self.timer.start(2000)
		
		proName = local.get("project","name")
		if utility.is_test():
			proName = "test"
		self.saveDir = os.path.abspath(os.path.dirname(__file__) + "/projects/" + proName + "/snap/" + map.mapId)
		
		#TODO:定时保存图片功能 self.saveFig = plt.figure(figsize=(map.width/4,map.height/4))
		#TODO:定时保存图片功能 self.map.draw(showPoint=False,showText=True,fig=self.saveFig)
		
		self.timer2 = PyQt5.QtCore.QTimer(self)  
		self.timer2.timeout.connect(self.autoSaveFig) 
		self.timer2.start(30000)
		   
	def autoUpdateAgv(self):
		try:
			self.map.drawAgv(None)
			self.draw()
		except Exception as e:
			log.exception("auto update agv",e)
			
	def autoSaveFig(self):
		return 
		#TODO: 定时保存图片功能,会导致有残影 
		try:
			c = counter.counter()
			date = utility.now().strftime("/%Y%m%d/")
			if not os.path.exists(self.saveDir + date):
				os.makedirs(self.saveDir + date)
			file = self.saveDir + date + utility.now().strftime("%Y%m%d_%H%M%S.png")
			self.map.drawAgv(fig=self.saveFig)
			self.saveFig.savefig(file,dpi=100)
			c.check()
		except Exception as e:
			log.exception("auto save agv",e)
		 
	def repaint(self,showPoint,showText):
		try:
			view = self.saveView() 
			self.fig.clear() 
			self.map.draw(showPoint=showPoint,showText=showText)   
			self.restoreView(view)
			self.draw()  
		except Exception as e:
			log.exception("repaint agv",e)
		
		

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
			import mapMgr
			nn = mapUI(mapMgr.getMap("408")) 
			layout.addWidget(nn)
			 
			self.setLayout(layout)
			self.setWindowTitle("QT测试")	 	
			self.setMinimumSize(400,400)
			 
	d = dlg() 
	d.show() 
	sys.exit(app.exec_())
