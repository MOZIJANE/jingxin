#coding=utf-8
# ycat			2017-08-16	  create
# 可以简单选择文本的对话框 
import sys,os
import qtawesome as qta
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import ui.inputBox
import PyQt5
import qtutility

DEFAULT_FONT_SIZE = 12	

def getText(title,defaultValue=""):
	dlg = inputDlg(title)
	dlg.addText("",defaultValue=defaultValue)
	if dlg.show():
		return dlg.getValues()[0]
	else:
		return None
		
def getInt(title,defaultValue=0,min = None, max = None):
	dlg = inputDlg(title)
	dlg.addInt("",defaultValue=defaultValue,min=min,max=max)
	if dlg.show():
		return int(dlg.getValues()[0])
	else:
		return None

def getFloat(title,defaultValue=0.0):
	dlg = inputDlg(title)
	dlg.addFloat("",defaultValue=defaultValue)
	if dlg.show():
		return float(dlg.getValues()[0])
	else:
		return None
	
#def getBool(title,trueValue,falseValue,defaultValue=False):
#	pass
#	

class inputDlg(PyQt5.QtWidgets.QDialog):	
	def __init__(self,title):
		super(inputDlg, self).__init__()
		self.setWindowTitle(title)
		self.setWindowIcon(qta.icon("fa.pencil-square-o"))
		self.setFixedSize(300,450)
		
		self.setWindowFlags(PyQt5.QtCore.Qt.WindowCloseButtonHint) 		
		l = PyQt5.QtWidgets.QFormLayout()
		l.setFormAlignment(PyQt5.QtCore.Qt.AlignHCenter | PyQt5.QtCore.Qt.AlignTop)
		l.setSpacing(10)  
					
		l2 = PyQt5.QtWidgets.QHBoxLayout()
		l2.setSpacing(20)
		b = PyQt5.QtWidgets.QPushButton(qta.icon("fa.check",scale_factor=1.5,color="green"),"确定")
		b.setMinimumHeight(40)
		b.setFixedWidth(80)
		b.clicked.connect(self.accept)
		l2.addWidget(b)
		
		b = PyQt5.QtWidgets.QPushButton(qta.icon("fa.remove",scale_factor=1.5,color="red"),"取消")
		b.setMinimumHeight(40)
		b.setFixedWidth(80)
		b.clicked.connect(self.reject)
		l2.addWidget(b)
		
		l3 = PyQt5.QtWidgets.QVBoxLayout()
		l3.addLayout(l)
		l3.addLayout(l2)
		self.setLayout(l3) 
		self.formLayout = l
		self.inputs = []
		
	def addText(self,label,ctrl=PyQt5.QtWidgets.QLineEdit,maxSize=30,defaultValue=""):
		input = ctrl()
		qtutility.setValue(input,defaultValue)
		qtutility.setFontSize(input,DEFAULT_FONT_SIZE)
		if label:
			t = self.getLabel(label)
			self.formLayout.addRow(t,input)
		else:
			self.formLayout.addWidget(input)
		self.inputs.append(input)
		self.setFixedSize(300,60*(len(self.inputs)+1))
		return input
		
	def addInt(self,label,ctrl=PyQt5.QtWidgets.QSpinBox,min = None, max = None,defaultValue=0):
		input = ctrl() 
		qtutility.setFontSize(input,DEFAULT_FONT_SIZE)
		if min is not None:
			input.setMinimum(min)
		else:
			input.setMinimum(0)
		if max is not None:
			input.setMaximum(max) 
		else:
			input.setMaximum(999)
		qtutility.setValue(input,defaultValue)
		
		if label:
			t = self.getLabel(label)
			self.formLayout.addRow(t,input)
		else:
			self.formLayout.addWidget(input)
		self.inputs.append(input)
		self.setFixedSize(300,60*(len(self.inputs)+1))
		return input
		
	def addFloat(self,label,ctrl=PyQt5.QtWidgets.QDoubleSpinBox,min=None,max=None,defaultValue=0):
		return addInt(label=label,ctrl=ctrl,min=min,max=max,defaultValue=defaultValue)
			
	def getLabel(self,text):
		c = PyQt5.QtWidgets.QLabel(text)
		font = c.font()
		font.setPointSize(DEFAULT_FONT_SIZE)
		c.setFont(font)
		return c
		
	def getValues(self):
		vv = []
		for v in self.inputs:
			vv.append(qtutility.getValue(v))
		return vv
		
	def show(self):
		return self.exec_() == PyQt5.QtWidgets.QDialog.Accepted
	
if __name__ == '__main__':
	app = PyQt5.QtWidgets.QApplication(sys.argv)
	print(getText("ddddd","gggggg"))
	print(getInt("ddddd",100))
	print(getFloat("ddddd",100))
	#d = inputDlg("ddddddddddddd","vvvvv")
	#d.exec_()

