#coding=utf-8
# ycat			2017-07-27	  create
# 空文件模板 
import sys,os
import setup
import qtawesome as qta
import threading

if __name__ == '__main__':
	setup.setCurPath(__file__)
from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog,QProgressBar,
        QInputDialog, QGridLayout, QWidget, QHBoxLayout,
        QLabel, QPushButton, QSpinBox, QTextEdit,QLineEdit,QMessageBox,QFormLayout,
        QVBoxLayout)
from PyQt5.QtGui import (QStandardItemModel,QStandardItem,QIcon)
from PyQt5.QtCore import QCoreApplication,Qt,QTimer
import ui.inputBox
import qtutility
#import user
import ui.meta
import log


class RetThread(threading.Thread):
	def __init__(self, func, args=(), name=''):
		threading.Thread.__init__(self,target=func,args=args)
		self.name = name
		self.func = func
		self.args = args
		self.result = None

	def run(self):
		try:
			if self.func:
				self.result = self.func(*self.args)
		except Exception as e:
			log.exception("invoke {0} exception, info:".format(str(self.func)),e)
		finally:
			pass

	def get_result(self):
		try:
			return self.result
		except Exception:
			return None

class loginDlg(QDialog):
	def __init__(self,users=[],fontSize=15):
		super(loginDlg, self).__init__(None)
		self.setWindowTitle("用户登陆") 
		l1 = QFormLayout()
		l1.setSpacing(10)
		b = QWidget()
		b.setFixedSize(20,20)
		l1.addRow(b)  
				
		b = QComboBox()
		for u in users:
			b.addItem(u,u)
		qtutility.setFontSize(b,fontSize)
		self.userBox = b
		t = QLabel("用户名")
		qtutility.setFontSize(t,fontSize)
		l1.addRow(t,b)
		
		self.pwdBox = ui.meta.pwdCtrl()#ui.inputBox.inputBox()
		self.pwdBox.setEchoMode(QLineEdit.Password) 
		qtutility.setFontSize(self.pwdBox,fontSize)
		t = QLabel("密码  ")
		qtutility.setFontSize(t,fontSize)
		l1.addRow(t,self.pwdBox)
		
		l2 = QHBoxLayout()
		l2.setSpacing(20)
		b = QPushButton(qta.icon("fa.check",scale_factor=1.5,color="green"),"确定")
		b.setMinimumHeight(40) 
		l2.addWidget(b)
		
		b = QPushButton(qta.icon("fa.remove",scale_factor=1.5,color="red"),"取消")
		b.setMinimumHeight(40)
		b.clicked.connect(self.reject)
		l2.addWidget(b)
		
		l = QVBoxLayout()
		l.addLayout(l1)
		l.addLayout(l2)
		
		self.setLayout(l)
		self.setMinimumSize(300,200)
		self.setWindowIcon(qta.icon("fa.user"))
		self.setWindowFlags(Qt.WindowCloseButtonHint)
	 
	 
class messageBox(QDialog):
	def __init__(self,title,message,iconName,iconColor,buttons=["确定","取消"],fontSize=15):
		super(messageBox, self).__init__(None)
		self.setMinimumSize(200,120)
		self.setWindowIcon(qta.icon("fa.info-circle"))
		self.setWindowFlags(Qt.WindowCloseButtonHint)
		
		self.setWindowTitle(title) 
		
		l1 = QHBoxLayout()
		l1.addStretch()
		l1.setSpacing(20)
		
		icon = QLabel()
		icon.setPixmap(QIcon(qta.icon(iconName,scale_factor=1,color=iconColor)).pixmap(36,36))
		l1.addWidget(icon)
		text = QLabel(message)
		text.setWordWrap(True)
		qtutility.setFontSize(text,fontSize)
		l1.addWidget(text)
		l1.addStretch()
		
		assert len(buttons) <= 2
		l2 = QHBoxLayout()
		l2.setSpacing(20)
		b = QPushButton(qta.icon("fa.check",scale_factor=1.5,color="green"),buttons[0])
		b.setFixedSize(80,32) 
		b.clicked.connect(self.accept)
		l2.addWidget(b)
		
		if len(buttons) > 1:
			b = QPushButton(qta.icon("fa.remove",scale_factor=1.5,color="red"),buttons[1])
			b.setMinimumHeight(40)
			b.clicked.connect(self.reject)
			b.setFixedSize(80,32) 
			l2.addWidget(b)
		
		l = QVBoxLayout()
		l.addLayout(l1)
		l.addLayout(l2)
		self.setLayout(l)
		
	def show(self):
		return self.exec()
		
class progressBox(QDialog):
	def __init__(self,status):
		super(progressBox, self).__init__(None)
		self.setFixedSize(300,60)
		self.setWindowIcon(qta.icon("fa.clock-o"))
		self.setWindowTitle(status.title) 

		p = QProgressBar()
		p.setFormat("%p%") 
		p.setRange(0,100)
		
		p.setAlignment(Qt.AlignCenter)
		l = QHBoxLayout()
		if status.label:
			l.addWidget(QLabel(status.label))
		l.addWidget(p,Qt.AlignCenter)
		self.setLayout(l)
		self.progressBar = p
		self.status = status
		self._timer = QTimer(self)
		self._timer.setInterval(100)
		self._timer.timeout.connect(self.update)
		self._timer.start()
		
	def update(self):
		if self.status.total == 0:
			self.accept()
			return
		#self.progressBar.setRange(0,self.status.total)
		self.progressBar.setValue(self.status.current/self.status.total*100.)
		if self.status.current >= self.status.total:
			self.accept()
			return
		if not self.status._thread.isAlive():
			self.close()
			return
			
	def closeEvent(self,event):
		return super(progressBox, self).closeEvent(event)
		
		
class progressBar:
	def __init__(self):
		self.total = 100	#总进度
		self.current = 0	#当前进度
		self.title = ""		#窗口标题
		self.label = ""		#进度条标题
		self._thread = None	
		self.cancelFunc = None
		
	#func(status)正常运行函数，cancel(status)取消函数，如果定义了取消函数才有关闭按钮
	def start(self,func,cancelFunc=None):
		self.cancelFunc = cancelFunc
		t = RetThread(func=func)
		self._thread = t
		t.start()
		ret = self.show()
		t.join()
		return ret

	def show(self):
		b = progressBox(self)
		if self.cancelFunc:
			b.setWindowFlags(Qt.WindowCloseButtonHint|Qt.MSWindowsFixedSizeDialogHint)
		else:
			b.setWindowFlags(Qt.WindowTitleHint|Qt.MSWindowsFixedSizeDialogHint)
		if b.exec() == b.Accepted:
			return True
		if self.cancelFunc:
			self.cancelFunc(self)
		return False
		
	def update(self,count,total):
		self.total = total
		self.current = count
		
def alert(message):
	b = messageBox("警告",message=message,iconName="fa.warning",iconColor="orange",buttons=["确定"])
	#w = QCoreApplication.instance().windowIcon ()
	#b.setWindowIcon(w)
	#print(w)
	b.exec()
	
warning = alert

def info(message):
	b = messageBox("信息",message=message,iconName="fa.info-circle",iconColor="blue",buttons=["确定"])
	b.exec()

def error(message):
	b = messageBox("错误",message=message,iconName="fa.warning",iconColor="red",buttons=["确定"])
	return b.exec() == 1
	
def confirm(message):
	b = messageBox("确认",message=message,iconName="fa.question-circle",iconColor="blue",buttons=["确定","取消"])
	return b.exec() == 1
	
 
################ unit test ################
def testprogress():
	p = progressBar()
	p.title = "ycat test"
	p.label = "下载进度"
	p.total = 100
	def run():
		import time
		for i in range(10):
			p.current += 1
			time.sleep(1)
		
	p.start(run)
	
def testlogin():
	dialog = loginDlg()
	sys.exit(dialog.exec_())
	
def testalert():
	#dialog = messageBox("测试","测试消息"*3,"fa.gear","green")
	alert("message")
	warning("message\n"*30)
	print(confirm("确定是否需要取消"))
	info("hello")
	error("hello")
	
if __name__ == '__main__':
	app = QApplication(sys.argv) 
	testprogress()
	testalert()
	sys.exit(app.exec_())
	
