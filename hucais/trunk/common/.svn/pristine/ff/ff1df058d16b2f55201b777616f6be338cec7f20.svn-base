import sys,os
import matplotlib.pyplot as plt  
import matplotlib.backends.backend_qt5agg 
import PyQt5  
import qtawesome as qta

#下面三句显示中文
from pylab import *
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

#https://matplotlib.org/stable/api/backend_bases_api.html?highlight=navigationtoolbar2#matplotlib.backend_bases.NavigationToolbar2
#http://matplotlib.org/index.html 
class chartWidget(PyQt5.QtWidgets.QWidget): 
	def __init__(self,figName="",addToolbar=True): 
		super(chartWidget, self).__init__()   
		if figName == "":
			self.figName = "fig"+str(id(self))
		else:
			self.figName = figName
		self._fig = plt.figure(self.figName)
		 
		self.canvas = matplotlib.backends.backend_qt5agg.FigureCanvas(self._fig)
		self.canvas.setParent(self) 
		
		self._plotToolbar = matplotlib.backends.backend_qt5agg.NavigationToolbar2QT(self.canvas,self.parent()) 
		 
		class _wrap:
			def __init__(self,func,parent,name):
				self.func = func
				self.parent = parent
				self.name = name
				
			def __call__(self,*param,**params):  
				self.func()
				self.parent._updateToolbar(self.name)  
				
		self.home = self._plotToolbar.home 
		self.back = self._plotToolbar.back
		self.forward = self._plotToolbar.forward 
		self.zoom = self._plotToolbar.zoom
		self.move = self._plotToolbar.pan
		self.save = self._plotToolbar.save_figure 
		
		self.homeAct = PyQt5.QtWidgets.QAction(qta.icon('fa.home',color='black'), "&Home", triggered=_wrap(self.home,self,"home"))
		self.preAct = PyQt5.QtWidgets.QAction(qta.icon('fa.undo',color='black'), "&Pre view", triggered=_wrap(self.back,self,"back"))
		self.forwardAct = PyQt5.QtWidgets.QAction(qta.icon('fa.repeat',color='black'), "&Next view", triggered=_wrap(self.forward,self,"forward"))
		self.zoomAct = PyQt5.QtWidgets.QAction(qta.icon('fa.search',color='black'), "&Zoom", triggered=_wrap(self.zoom,self,"zoom"))
		self.zoomAct.setCheckable(True) 
		self.moveAct = PyQt5.QtWidgets.QAction(qta.icon('fa.arrows',color='black'), "&Move", triggered=_wrap(self.move,self,"move"))
		self.moveAct.setCheckable(True) 
		#self.refreshAct = PyQt5.QtWidgets.QAction(qta.icon('fa.refresh',color='black'), "&Refresh", triggered=_wrap(self.canvas.draw,self)) 
		self.saveAct = PyQt5.QtWidgets.QAction(qta.icon('fa.save',color='black'), "&Save", triggered=_wrap(self.save,self,"save")) 
		
		self.toolbar = PyQt5.QtWidgets.QToolBar("图表控制")
		#self.toolbar.setToolButtonStyle(PyQt5.QtCore.Qt.ToolButtonTextUnderIcon)		 
		self.toolbar.setIconSize(PyQt5.QtCore.QSize(26,26))
		self.toolbar.addAction(self.homeAct)  
		self.toolbar.addAction(self.preAct)  
		self.toolbar.addAction(self.forwardAct)  
		self.toolbar.addAction(self.zoomAct)  
		self.toolbar.addAction(self.moveAct)  
		self.toolbar.addSeparator()
		#self.toolbar.addAction(self.refreshAct)  
		self.toolbar.addAction(self.saveAct)   
		
		layout = PyQt5.QtWidgets.QVBoxLayout(self) 
		if addToolbar:
			layout.addWidget(self.toolbar)
		layout.addWidget(self.canvas)
		#layout.addWidget(self._plotToolbar)
		self.setLayout(layout) 
		 
		 
	def _updateToolbar(self,name):    
		if name == 'move':
			self.moveAct.setChecked(True)
		else:
			self.moveAct.setChecked(False)
		if name == 'zoom':
			self.zoomAct.setChecked(True)
		else:
			self.zoomAct.setChecked(False) 
			 
	#重绘图表 
	def draw(self):
		#self.canvas.draw()
		self.canvas.draw_idle()
		
	@property
	def plot(self):
		#切换使用当前figure  
		self.switch()
		return plt 
	
	@property
	def fig(self):
		return self._fig
		
	@property
	def ax(self):
		return self._fig.gca()	
		
	def switch(self): 
		plt.figure(self.figName) 
		
	#保存当前视图  
	def saveView(self): 
		ax = self.fig.gca()
		return (ax._get_view(),
				# Store both the original and modified positions.
				(ax.get_position(True).frozen(),
				ax.get_position().frozen()))  
	
	#恢复当前视图
	def restoreView(self,view):
		self._plotToolbar.push_current()
		ax = self.fig.gca()
		v, (pos_orig, pos_active) = view
		ax._set_view(v)
		# Restore both the original and modified positions
		ax._set_position(pos_orig, 'original')
		ax._set_position(pos_active, 'active') 
		  
	def saveFigure(self,filename,**params):
		self.fig.savefig(filename,**params)


if __name__ == '__main__':
	import sys
	import PyQt5.QtWidgets
	import chartWidget
	import numpy as np 
	import matplotlib.pyplot as plt  
	app = PyQt5.QtWidgets.QApplication(sys.argv)

	def create_chart(p):
		t = np.arange(0.0, 2.0, 0.01)
		s1 = np.sin(2*np.pi*t)
		s2 = np.sin(4*np.pi*t)

		p.subplot(211)
		p.plot(t, s1)
		p.subplot(212)
		p.plot(t, 2*s2)


	class Dialog(PyQt5.QtWidgets.QDialog): 
		def __init__(self):
			super(Dialog, self).__init__() 
			layout = PyQt5.QtWidgets.QHBoxLayout()
			for i in range(2):
				c = chartWidget.chartWidget()
				c.switch()
				create_chart(c.plot)
				layout.addWidget(c)
				
			self.setLayout(layout)
			self.setWindowTitle("Example matplotlib with QT5")
			
	dialog = Dialog()
	sys.exit(dialog.exec_())		