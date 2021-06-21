#coding=utf-8
# ycat			2017-07-27	  create
# 实现画一条水平或竖线的控件 
import sys,os
import PyQt5.QtWidgets 
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)

class HLine(PyQt5.QtWidgets.QFrame):
	def __init__(self):
		super(HLine, self).__init__()
		self.setFrameShape(PyQt5.QtWidgets.QFrame.HLine)
		self.setFrameShadow(PyQt5.QtWidgets.QFrame.Sunken)	
	
	def setLength(self,value):
		self.setFixedWidth(value)
	
class VLine(PyQt5.QtWidgets.QFrame):
	def __init__(self):
		super(VLine, self).__init__()
		self.setFrameShape(PyQt5.QtWidgets.QFrame.VLine)
		self.setFrameShadow(PyQt5.QtWidgets.QFrame.Sunken)	
	
	def setLength(self,value):
		self.setFixedHeight(value)	
	
if __name__ == '__main__':
	import qtutility
	qtutility.run("line.HLine")

