#coding=utf-8
# ycat			2019-11-25	  create 
import sys,os
import PyQt5 
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import qtutility,utility
import log
import qtawesome as qta
import ui.tableDlg 
import taskList

class taskWidget(PyQt5.QtWidgets.QWidget): 
	def __init__(self,maxLines=100):
		super(taskWidget, self).__init__()   
		self.table = ui.tableDlg.tableWidget()
		self.table.addColumn("ID") 
		self.table.addColumn("任务状态") 
		self.table.addColumn("AGV")
		self.table.addColumn("起始位置")
		self.table.addColumn("目标位置")
		self.table.addColumn("开始时间") 
		self.table.addColumn("结束时间")  
		self.table.addColumn("时长")  
		self.table.addColumn("步骤")
		self.table.addColumn("路径")
		self.table.addColumn("未完成路径")
		self.maxLines = maxLines 
		  
		layout = PyQt5.QtWidgets.QVBoxLayout(self)  
		layout.addWidget(self.table) 
		layout.setContentsMargins(0,0,0,0)
		self.setLayout(layout)  
		self._updateTask() 
		self.timer = PyQt5.QtCore.QTimer(self) #初始化一个定时器
		self.timer.timeout.connect(self._updateTask) #计时结束调用operate()方法
		self.timer.start(5000)
		
	def _getCellData(self):
		ret = {}
		for i in range(self.table.count):
			data = self.table.getItemText(i,0)
			if data in ret:
				log.error("logical error",data,ret)
			assert data not in ret
			ret[data] = i
		return ret
		
	def _FindData(self,id):
		for i in range(self.table.count):
			if self.table.getItemText(i,0) == id:
				return i
		return -1
		
	def _updateTask(self):
		now = utility.now() 
		def addRow(task,index=-1):
			row = []
			row.append(task["id"]) 
			if task["status"] == "begin":
				row.append("运行")
				color = "#50b7c1"
			elif task["status"] == "wait":
				row.append("等待")
				color = "gray"
			elif task["success"]:
				row.append("完成")
				color = "green"
			else:
				row.append(task["exception"])
				color = "red"
			row.append(task["agv"])
			row.append(task["start"])
			row.append(task["target"])
			row.append(utility.date2str(task["createTime"]))
			if "finishTime" in task:
				row.append(utility.date2str(task["finishTime"]))
				row.append(utility.date2str(task["finishTime"]-task["createTime"]))
			else:
				row.append("-")
				row.append(utility.date2str(now-task["createTime"]))
			row.append(task["step"])
			row.append(task["paths"])
			row.append(task["unfinishPaths"]) 
			if index == -1: 
				index = self.table.addRow(row)
			else:  
				self.table.update(index,row)
			self.table.setItemColor(index,1,color="white",bgColor=color)
			return index
			
		data = self._getCellData()
		#tasks = taskList.getAllList().values()[0:self.maxLines]
		tasks = sorted(taskList.getAllList().values(),key=lambda x:x["createTime"],reverse=True)[0:self.maxLines]
		ids = set([ t["id"] for t in tasks])
		
		rr = []
		for d in data:
			if d not in ids:
				rr.append(data[d]) 
		rr.sort(reverse=True)

		for r in rr:
			self.table.remove(r) 
		 
		for t in tasks: 	 
			index = self._FindData(t["id"]) 
			addRow(t,index=index)
		self.table.sort(5,asc=False)
 
################## unit test ##################

if __name__ == '__main__':
	app = PyQt5.QtWidgets.QApplication(sys.argv)
	class dlg(PyQt5.QtWidgets.QDialog): 
		def __init__(self):
			super(dlg, self).__init__() 
			layout = PyQt5.QtWidgets.QHBoxLayout()
			nn = taskWidget()  
			layout.addWidget(nn) 
			self.setLayout(layout)
			self.setWindowTitle("QT测试")	 	
			self.setMinimumSize(800,400)
			self.ctrl = nn
			 
	d = dlg()  
	d.show() 
	sys.exit(app.exec_())

	
	
	
	
	
	
	
	
	
	