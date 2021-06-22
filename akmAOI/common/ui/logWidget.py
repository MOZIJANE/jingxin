import sys,os
import PyQt5
from PyQt5.QtWidgets import QTextEdit
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import (QFont, QIcon,QColor, QTextCharFormat,
        QTextCursor, QTextTableFormat,QPalette)
from PyQt5.QtCore import pyqtSignal,pyqtSlot
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import qtutility,utility,log
import logging
import qtawesome as qta
import shutil 

class logWidget(PyQt5.QtWidgets.QWidget):
	_signal = pyqtSignal(str,str,str) 
	
	def __init__(self,maxLines=5000):
		super(logWidget, self).__init__()   
		self.textCtrl = QTextEdit()
		
		qtutility.setBackgroupColor(self.textCtrl,"black")
		self.textCtrl.setTextBackgroundColor(QColor("black"))
		self.textCtrl.setTextColor(QColor("white"))  
		qtutility.setFontSize(self.textCtrl,12)
		self.textCtrl.setLineWrapMode(0)	#Text is not wrapped at all
		self.textCtrl.setReadOnly(True)
		
		self._signal.connect(self._insertLog)
		self.autoScroll = True
		self.maxLines = maxLines 
		
		self.saveAsAct = PyQt5.QtWidgets.QAction(qta.icon('fa.save',color='black'), "&Save", triggered=self.saveAs) 
		
		self.toolbar = PyQt5.QtWidgets.QToolBar("日志控制")
		self.toolbar.addAction(self.saveAsAct)   
		#self.toolbar.setIconSize(PyQt5.QtCore.QSize(18,18))
		
		layout = PyQt5.QtWidgets.QVBoxLayout(self) 
		layout.addWidget(self.toolbar)
		layout.addWidget(self.textCtrl) 
		layout.setContentsMargins(0,0,0,0)
		self.setLayout(layout) 
		 
		
	def saveAs(self):    
		options = PyQt5.QtWidgets.QFileDialog.Options()
		#options |= PyQt5.QtWidgets.QFileDialog.DontUseNativeDialog
		fileName, _ = PyQt5.QtWidgets.QFileDialog.getSaveFileName(self,
				"保存日志",
				log.g_cur_log_file,
				"Log Files (*.log)", options=options) 
		if fileName: 
			shutil.copyfile(log.g_cur_log_file,fileName)
		 
		
	def debug(self,msg):
		self._writeLog(msg,"white","black")
		
	def info(self,msg): 
		self._writeLog(msg,"cyan")
		
	def warning(self,msg):
		self._writeLog(msg,"yellow")
	
	def error(self,msg):
		self._writeLog(msg,"red")	
		
	def critical(self,msg):	
		self._writeLog(msg,"white","red")	
		
	def success(self,msg): 
		self._writeLog(msg,"limegreen")	
		
	def _writeLog(self,msg,color,bgcolor="black"): 
		self._signal.emit(msg,color,bgcolor)
		
	def _insertLog(self,msg,color,bgcolor="black"): 
		t = "<span style='color:{1};background-color:{2}'>{0}</span>".format(msg,color,bgcolor) 
		self.textCtrl.append(t)
		self._autoScroll()
		
	def _autoScroll(self):
		if self.textCtrl.document().lineCount() > self.maxLines:
			num = self.textCtrl.document().lineCount() - self.maxLines + int(self.maxLines/10) 
			self._removeLines(num)
		if self.autoScroll:
			self.textCtrl.moveCursor(QTextCursor.End) 
			self.textCtrl.moveCursor(QTextCursor.StartOfLine) 
			
		
	def _removeLines(self,lines):
		cur = self.textCtrl.textCursor()
		cur.setPosition(0)
		for i in range(lines):
			cur.movePosition(QTextCursor.Down,QTextCursor.KeepAnchor)
		cur.movePosition(QTextCursor.StartOfLine,QTextCursor.KeepAnchor) 
		cur.removeSelectedText() 
		self.textCtrl.moveCursor(QTextCursor.StartOfBlock) 
		 
	#设置到log
	def setupLog(self):
		h = qtLogHander(self)
		f = logging.Formatter("[%(levelname)s]%(asctime)s: %(message)s")
		h.setFormatter(f)
		log.logger().addHandler(h)
		
		

class qtLogHander(logging.Handler): 
	def __init__(self,ctrl):
		self.ctrl = ctrl
		logging.Handler.__init__(self) 

	def emit(self,record):  
		msg = self.format(record)  
		func = self.ctrl.debug
		#CRITICAL=50,ERROR=40,SUCCESS=35,WARNING=30,INFO=20,DEBUG=10,NOTSET=-1 	
		if record.levelno == 50:
			func = self.ctrl.critical 
		elif record.levelno == 40:
			func = self.ctrl.error 
		elif record.levelno == 35:
			func = self.ctrl.success 
		elif record.levelno == 30:
			func = self.ctrl.warning 
		elif record.levelno == 20:
			func = self.ctrl.info
		func(msg)

################## unit test ##################

if __name__ == '__main__':
	def threadFunc(c):
		import time
		time.sleep(1)
		import time
		i = 0
		while True:
			time.sleep(1)
			log.info("ycat test",i)
			i += 1

	import PyQt5,threading
	app = PyQt5.QtWidgets.QApplication(sys.argv)
	
	class dlg(PyQt5.QtWidgets.QDialog): 
		def __init__(self):
			super(dlg, self).__init__() 
			layout = PyQt5.QtWidgets.QHBoxLayout()
			nn = logWidget(10) 
			nn.setupLog()
			layout.addWidget(nn) 
			self.setLayout(layout)
			self.setWindowTitle("QT测试")	 	
			self.setMinimumSize(800,400)
			self.ctrl = nn
			 
	d = dlg() 
	t1 = threading.Thread(target=threadFunc,args=[d.ctrl,])
	t2 = threading.Thread(target=threadFunc,args=[d.ctrl,])
	t1.start()
	t2.start()
	d.show() 
	sys.exit(app.exec_())

	
	
	
	
	
	
	
	
	
	