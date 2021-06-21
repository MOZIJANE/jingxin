#coding=utf-8
#lizhenwei		2017-08-04		create

import os,sys

from PyQt5.QtCore import (Qt,pyqtSignal,pyqtSlot,QModelIndex)
from PyQt5.QtGui import (QBrush,QStandardItemModel,QStandardItem,QMouseEvent)
from PyQt5.QtWidgets import (QApplication,QTableView,QItemDelegate,QAbstractItemView)

class stateDelegate(QItemDelegate):
	'状态item托管'
	sgReverseState = pyqtSignal(QModelIndex)
	
	def __init__(self,colno=2,enClick=False):
		super(stateDelegate,self).__init__()
		
		self.colno = colno
		self.enClick = enClick
		
	def paint(self, painter, option, index):
		if index.column() == self.colno:
			val = index.data()
			d = min(option.rect.width(),option.rect.height())
			painter.save()
			if 0 == val:
				# 0为绿色
				painter.setBrush(QBrush(Qt.green))
			elif 1 == val:
				painter.setBrush(QBrush(Qt.red))
			painter.setPen(Qt.NoPen);
			painter.drawEllipse(option.rect.center(),d>>1,d>>1);
			painter.restore();	
		
		else:
			super(stateDelegate,self).paint(painter,option,index)
		
	def editorEvent(self,event, model, option, index):
		msEvent = QMouseEvent(event)
		if (msEvent.type() == msEvent.MouseButtonRelease) and option.rect.contains(msEvent.x(),msEvent.y()):
			if self.enClick:
				self.sgReverseState.emit(index)
    
		return super(stateDelegate,self).editorEvent(event,model,option,index);
	
	
	
class ioTableView(QTableView):
	
	# 设置bit状态, addr,state
	sgSetBitState = pyqtSignal(int,int)
	
	def __init__(self,mode):
		'mode: 0输入，1输出'
		super(ioTableView,self).__init__()
		self.mode = mode
		self.initUI()

	def initUI(self):
		self.itemModel = QStandardItemModel()
		
		headers = ("地址","名称","状态")
		self.itemModel.setHorizontalHeaderLabels(headers)
		
		self.stateDelegate = stateDelegate(2, self.mode==1)
		
		self.setModel(self.itemModel)
		self.setItemDelegateForColumn(2,self.stateDelegate)
		
		stateSize = 36
		self.verticalHeader().setDefaultSectionSize(stateSize*1.2)
		self.verticalHeader().hide()
		self.setColumnWidth(2,stateSize)
		self.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.setSelectionMode(QAbstractItemView.NoSelection)
		
		self.stateDelegate.sgReverseState.connect(self.onReverseState)
		
		# self.setSortingEnabled(True)
		# self.sortByColumn(0,Qt.AscendingOrder)
		
	def loadIOCfgDict(self,iodict):
		'加载io列表'
		for idname,cfg in iodict.items():
			addrItem = QStandardItem()
			addrItem.setData(cfg["addr"],Qt.EditRole)
			nameItem = QStandardItem(cfg["name"])
			stateItem = QStandardItem()
			stateItem.setData(cfg["state"],Qt.EditRole)
			self.itemModel.appendRow([addrItem,nameItem,stateItem])
		self.sortByColumn(0,Qt.AscendingOrder)
		
	
	@pyqtSlot(QModelIndex)	
	def onReverseState(self,idx):
		'翻转电平'
		preVal = idx.data()
		curVal = preVal^1
		self.itemModel.setData(idx,curVal,Qt.EditRole)
		addr = self.itemModel.index(idx.row(),0).data()
		self.sgSetBitState.emit(addr,curVal)

	@pyqtSlot(int,int)
	def onSetBitState(self,addr,state):
		for i in range(self.itemModel.rowCount()):
			taddr = self.itemModel.item(i,0).data(Qt.EditRole)
			if addr == taddr:
				self.itemModel.item(i,2).setData(state,Qt.EditRole)
				break
	
	
def test():	
	app = QApplication(sys.argv)
	inview = ioTableView(1)
	in0 = {"addr":0,"name":"test0","state":0}
	in1 = {"addr":1,"name":"test1","state":1}
	iodict = {"in0":in0, "in1":in1}
	inview.loadIOCfgDict(iodict)
	inview.show()
	sys.exit(app.exec_())
	
if __name__ == '__main__':
	test()