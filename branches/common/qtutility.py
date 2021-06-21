#coding=utf-8 
# ycat			 2015/04/10	  create
import sys,os
import time
import PyQt5
from PyQt5.QtCore import (QCoreApplication,QTimer, QEventLoop)
from PyQt5.QtWidgets import QWidget,QApplication,QDialog,QHBoxLayout,QMessageBox,QLineEdit,QPushButton,QSpinBox,QDoubleSpinBox,QComboBox
import PyQt5.QtGui
import enhance,log


#自动处理异常的修饰符
#用法 @catch 
def catch(func):
	def __call(*p,**pp):
		try:
			return func(*p,**pp)
		except Exception as e:
			log.exception("exception",e)
			#import traceback
			#traceback.print_exc()
			msgBox = QMessageBox(QMessageBox.Critical, "错误", str(e), QMessageBox.NoButton, None)
			msgBox.addButton('确定',QMessageBox.AcceptRole)
			msgBox.exec_()
			return None
	return __call

_exited = False

def resumeSleep():
	global _exited
	_exited = False
	
def stopSleep():
	global _exited
	_exited = True 
	
def sleep(ms):
	global _exited 
	start = time.time()*1000
	while not _exited:
		if time.time()*1000 - start < ms: 
			QCoreApplication.processEvents() 
		else:
			return True
	else:
		log.warning("延时调用退出_exited= %d"%_exited)
		return False
	return True
	
qtSleep = sleep
	
def run(objName,*p,**pp):
	app = QApplication(sys.argv)
	class dlg(QDialog): 
		def __init__(self):
			super(dlg, self).__init__() 
			layout = QHBoxLayout()
			self.ctrl = enhance.create_obj(objName,*p,**pp)
			layout.addWidget(self.ctrl)
			self.setLayout(layout)
			self.setWindowTitle("QT测试")	
			self.setWindowFlags(self.windowFlags()& ~PyQt5.QtCore.Qt.WindowMaximizeButtonHint& PyQt5.QtCore.Qt.WindowMinimizeButtonHint) 
	dialog = dlg()
	sys.exit(dialog.exec_())
	return dialog.ctrl
	
def setFontSize(ctrl,size):
	font = ctrl.font()
	font.setPointSize(size)
	ctrl.setFont(font)
	
def setBackgroupColor(ctrl,color):
	pa = ctrl.palette()
	pa.setColor(PyQt5.QtGui.QPalette.Base,PyQt5.QtGui.QColor(color))
	ctrl.setPalette(pa) 

def clearLayout(layout):
	while layout.count():
		w = layout.itemAt(0).widget()
		if w is None:
			w = layout.itemAt(0).layout()
			clearLayout(w)
			layout.removeItem(w)
		else:
			layout.removeWidget(w)
		w.setParent(None) 	
		
def createBtns(acceptFunc,cancelFunc):
	import qtawesome as qta
	l2 = QHBoxLayout()
	l2.addStretch(1) 
	l2.setSpacing(20)
	b = QPushButton(qta.icon("fa.check",scale_factor=1.5,color="green"),"确定")
	b.setMinimumHeight(40)
	b.clicked.connect(acceptFunc)
	b.setFixedWidth(100)
	l2.addWidget(b)
		
	b2 = QPushButton(qta.icon("fa.remove",scale_factor=1.5,color="red"),"取消")
	b2.setMinimumHeight(40)
	b2.clicked.connect(cancelFunc)
	b2.setFixedWidth(100)
	l2.addWidget(b2)
	return l2,b,b2
	
		
def alert(msg, acceptStr = '确定', rejectStr = None, parent = None):
	msgBox = QMessageBox(QMessageBox.Warning, "警告", msg, QMessageBox.NoButton, parent)
	msgBox.addButton('确定',QMessageBox.AcceptRole)
	if rejectStr:
		msgBox.addButton(rejectStr,QMessageBox.RejectRole)
	ret = msgBox.exec_()				
	return ret == QMessageBox.AcceptRole
	
showWaring = alert
	
def setValue(ctrl,value): 
	import ui.numberBox 
	import ui.checkbox

	if isinstance(ctrl,ui.numberBox.numberBox):
		ctrl.setValue(value) 
	elif isinstance(ctrl,QComboBox):
		for i in range(ctrl.count()):
			if ctrl.itemData(i) == value:
				ctrl.setCurrentIndex(i)
				return
		ctrl.setCurrentIndex(-1)
		return
	elif isinstance(ctrl,ui.checkbox.checkbox):
		if value:
			ctrl.setChecked(True)
		else:
			ctrl.setChecked(False)
	elif isinstance(ctrl,QLineEdit):
		return ctrl.setText(str(value))
	elif isinstance(ctrl,(QDoubleSpinBox,QSpinBox)):
		ctrl.setValue(value)
		return
	#elif isinstance(ctrl,QComboBox):
	#	return ctrl.setText(str(value))
	#print(isinstance(ctrl,QComboBox),"unknown type",ctrl)
	assert 0

def getValue(ctrl): 
	import ui.numberBox 
	import ui.checkbox
	
	if isinstance(ctrl,ui.numberBox.numberBox):
		return ctrl.value()
	elif isinstance(ctrl,PyQt5.QtWidgets.QComboBox):
		if ctrl.currentIndex():
			return ctrl.itemData(ctrl.currentIndex())
		else:
			if ctrl.count():
				return ctrl.itemData(0)
			else:
				return None
	elif isinstance(ctrl,ui.checkbox.checkbox):
		return ctrl.isChecked()
	elif isinstance(ctrl,QLineEdit):
		return ctrl.text()
	elif isinstance(ctrl,(QDoubleSpinBox,QSpinBox)):
		return ctrl.value()
	print("unknow type ",type(ctrl))
	assert 0
	 
def setChangedEvent(ctrl,valueChanged):
	import ui.checkbox,ui.numberBox
	if isinstance(ctrl,PyQt5.QtWidgets.QComboBox):
		ctrl.currentIndexChanged.connect(valueChanged) 
	elif isinstance(ctrl,ui.checkbox.checkbox):
		ctrl.clicked.connect(valueChanged) 
	elif isinstance(ctrl,QLineEdit):
		ctrl.textChanged.connect(valueChanged) 
	elif isinstance(ctrl,(PyQt5.QtWidgets.QSpinBox,PyQt5.QtWidgets.QDoubleSpinBox)):
		ctrl.valueChanged.connect(valueChanged) 
		#ctrl.textChanged.connect(valueChanged) 
	elif isinstance(ctrl,ui.numberBox.numberBox):
		ctrl.textChanged.connect(valueChanged) 
		
		
##把QT的路径转成matplotlib的路径 
#def qt2path(qtPathObj):
#	assert isinstance(qtPathObj,PyQt5.QtGui.QPainterPath)
#	import matplotlib.path as mpath  
#	import matplotlib.patches as mpatches
#	polygonList = qtPathObj.toSubpathPolygons(PyQt5.QtGui.QTransform())
#	paths = []
#	for poly in polygonList:
#		for i,p in  enumerate(poly):
#			if i == 0:
#				paths.append((mpath.Path.MOVETO, (p.x(),-p.y())))
#			else:
#				paths.append((mpath.Path.LINETO, (p.x(),-p.y())))
#	if len(paths):
#		codes, verts = zip(*paths) 
#		return mpath.Path(verts, codes)
#	else:
#		return None
#		
#def addPath(qtPathObj,**param):
#	import matplotlib.pyplot as plt
#	import matplotlib.patches as mpatches
#	p = qt2path(qtPathObj)
#	if p is None:
#		return
#	return plt.gca().add_patch(mpatches.PathPatch(p, **param))
		
def showPath(qtPath,lineColor=(0,0,0),fillColor=(0,255,0)):
	app = QApplication(sys.argv)
	class dlg(QDialog): 
		def __init__(self):
			super(dlg, self).__init__() 
			self.qtPath = qtPath
			layout = QHBoxLayout()
			self.resize(400, 300)
			#layout.addWidget(enhance.create_obj(objName,*p,**pp))
			self.setLayout(layout)
			self.setWindowTitle("QT测试")	
			self.setWindowFlags(self.windowFlags()& ~PyQt5.QtCore.Qt.WindowMaximizeButtonHint& PyQt5.QtCore.Qt.WindowMinimizeButtonHint) 
			
		def paintEvent(self, event):
			paint = PyQt5.QtGui.QPainter(self)  
			#paint.begin(self)
			paint.setViewport(-40,-40,400,400)
			self.drawPath(paint) 
			#paint.end()
			
		def drawPath(self,paint):
			paint.setPen(PyQt5.QtGui.QPen(PyQt5.QtGui.QColor(*lineColor), 1))
			paint.setBrush(PyQt5.QtGui.QColor(*fillColor))
			paint.drawPath(self.qtPath)
			
	dialog = dlg()
	sys.exit(dialog.exec_()) 

#去掉右上角的?号
def cancelQuestionMark(dlg):
	dlg.setWindowFlags(PyQt5.QtCore.Qt.WindowCloseButtonHint)  	

	
if __name__ == '__main__': 
	testtt()
	assert 0
	chassis = PyQt5.QtGui.QPainterPath()
	chassis.addRect(0,0,100,120)
	showPath(chassis)
	
#	import utility
#	s = utility.ticks()
#	for i in range(10000):
#		time.sleep(0)
#		QCoreApplication.processEvents()
#	#sleep(1500)
#	print(s - utility.ticks())
	
	
