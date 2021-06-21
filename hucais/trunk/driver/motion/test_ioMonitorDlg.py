#coding=utf-8
# lizhenwei		2017-08-04		create
import os,sys
from PyQt5.QtCore import (Qt,pyqtSignal,pyqtSlot,QModelIndex)
from PyQt5.QtGui import (QBrush,QStandardItemModel,QStandardItem,QMouseEvent)
from PyQt5.QtWidgets import (QApplication,QWidget, QDialog, QTableView,QItemDelegate,
		QAbstractItemView,QGroupBox,QPushButton,QGridLayout, QHBoxLayout, QVBoxLayout)

import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)			

from driver.motion import motionConfig
from driver.motion import smcApi
from driver.motion import ioCtrl 
from driver.motion import ioInputScanThd
from driver.motion import ioView
	
class ioMonitorDlg(QDialog):
	'IO监控界面'
	def __init__(self,parent=None):
		super(ioMonitorDlg,self).__init__()
		self.createUI()
		self.ioInScanThd = ioInputScanThd.ioInputScanThd()
		self.ioInScanThd.sgBitChanged.connect(self.onSetInBitState)
		self.ioOutView.sgSetBitState.connect(self.onSetOutBitState)
		self.initUI()
		self.ioInScanThd.start()
		
	def createUI(self):
		self.ioInView = ioView.ioTableView(0)
		self.ioOutView = ioView.ioTableView(1)
		
		ioInGpbox = QGroupBox("IO输入")
		inlay = QHBoxLayout()
		inlay.addWidget(self.ioInView)
		ioInGpbox.setLayout(inlay)
		
		ioOutGpbox = QGroupBox("IO输出")
		outlay = QHBoxLayout()
		outlay.addWidget(self.ioOutView)
		ioOutGpbox.setLayout(outlay)
		
		lay = QHBoxLayout()
		lay.addWidget(ioInGpbox)
		lay.addWidget(ioOutGpbox)
		self.setLayout(lay)
		
		self.setMinimumHeight(800)
		self.setWindowTitle("IO监控")
	
	def initUI(self):
		incfglist = motionConfig.g_motionCfg.ioInCfgList
		outcfglist = motionConfig.g_motionCfg.ioOutCfgList
		self.ioInView.loadIOCfgDict(incfglist)
		self.ioOutView.loadIOCfgDict(outcfglist)
		
		# 读取port状态，设置界面
		state = ioCtrl.ioInCtrl.readAll()
		print(state)
		for idname,cfg in incfglist.items():
			addr = cfg["addr"]
			bitState = ((state & (1 << addr)) >> addr)
			self.ioInView.onSetBitState(addr,  bitState)
		
		state = ioCtrl.ioOutCtrl.readAll()
		print(state)
		for idname, cfg in outcfglist.items():
			addr = cfg["addr"]
			bitState = ((state & (1 << addr)) >> addr)
			self.ioOutView.onSetBitState(addr, bitState)
			
	def onSetInBitState(self,cfg):
		self.ioInView.onSetBitState(cfg["addr"],cfg["state"])
		
	def onSetOutBitState(self,addr,state):
		ioCtrl.ioOutCtrl.writeBitState(addr,state)
		
if __name__ == "__main__":
	app = QApplication(sys.argv)
	ioDlg = ioMonitorDlg()
	ioDlg.show()
	sys.exit(app.exec_())