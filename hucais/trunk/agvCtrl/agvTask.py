#coding=utf-8
# ycat			2018-8-2	  create
# 任务管理，里面带有线程 
import time 
import setup
import queue
if __name__ == '__main__':
	setup.setCurPath(__file__) 
import enhance
import threading
import queue
import utility
import log
	
#Task回调的返回值  
TASK_CONTINUE = 0		#继续执行下一个任务
TASK_CANCEL = -1		#中止所有的任务
TASK_PAUSE = -2			#停止任务，直到调用resume()为止
TASK_WAIT = -3			#等待任务开始，这里会不停的调用回调，直到收到其它信号为止,仅在beginCallback生效  

class task:
	def __init__(self,agvId):
		self._queue = queue.Queue()
		self.agvId = agvId
		self._running = True
		self._exit = False 
		self._currentTask = None #当前任务 
		self._thread = threading.Thread(target=self._threadFunc)
		self._thread.start()
		
	def fini(self):
		self._exit = True
		self._thread.join()
	
	#beginCallback 任务开始回调,参数: params 
	#finishCallback 任务结束回调,参数: result,more,params
	#返回值为下面值之一：
	#	TASK_CONTINUE = 0
	#	TASK_CANCEL = -1
	#	TASK_PAUSE = -2
	#	TASK_WAIT_SIGNAL = -3 
	def add(self,execFunc,execParams,beginCallback,finishCallback,params): 
		self._queue.put((execFunc,execParams,beginCallback,finishCallback,params))

	def resume(self):
		self._running = True
	
	#是否等到当前任务执行完 
	def clear(self,clearCurrent=True):
		if clearCurrent:
			self._currentTask = None
		while not self._queue.empty():
			self._queue.get(False)
	
	#等待所有任务结束 
	def wait(self):
		while not self._exit:
			if not self._currentTask and self._queue.empty():
				break
			time.sleep(1)
	
	@property
	def isEmpty(self):
		if self._currentTask is not None:
			return False
		return self._queue.empty()
	
	def _getTask(self):
		if self._currentTask:
			return self._currentTask
		else:
			if self._queue.empty():
				return None
			try:
				self._currentTask = self._queue.get(timeout=1)
				return self._currentTask
			except queue.Empty:
				return None
				
	def _threadFunc(self):
		while not self._exit: 
			if not self._running:
				time.sleep(1)
				continue 
				
			obj = self._getTask()
			if obj is None:
				time.sleep(1)
				continue
				
			ret = self._handle(obj) 
			if ret == TASK_WAIT:
				time.sleep(1)
				continue 
			assert ret is not None
			if ret == TASK_CONTINUE:
				continue
			elif ret == TASK_CANCEL: 
				self.clear()
				continue
			elif ret == TASK_PAUSE:
				self._running = False 
				continue
			else:
				assert 0 #unknow ret value  
			
	def _handle(self,obj):
		try:
			execFunc,execParams,beginCallback,finishCallback,params = obj
			if beginCallback:
				ret = beginCallback(params)
				if ret != TASK_CONTINUE:
					return ret
					
			#执行任务 
			execFunc(**execParams)
			self._currentTask = None
			
			if finishCallback is None:
				return TASK_CONTINUE
				
			ret = finishCallback(True,not self._queue.empty(),params)
			assert ret != TASK_WAIT #结束回调不支持TASK_WAIT 
			return ret
		except Exception as e:
			log.exception("handle task failed",e)
			params["exception"] = str(e)
			if finishCallback:
				finishCallback(False,not self._queue.empty(),params) 
			return TASK_CANCEL
		
		
################## unit test ##################   
def test_task():
	def run1(sleepSec):
		time.sleep(sleepSec)
		print("run1",sleepSec)
		
	def callback1(params):  
		count[0] += 1
		return TASK_CONTINUE
	
	def callback2(result,more,params): 
		assert result == params["value"][0]
		assert more == params["value"][1]
		params["count"][0] += 1
		return params["ret"]
	
	def callback3(params):  
		count[0] += 1
		return params["ret"]
	 
	t = task("agv1")
	count = [0,]
	for i in range(3):
		count = [0,]
		t.add(run1,{"sleepSec":0.01},callback1,callback2,{"ret":TASK_CONTINUE,"value":(True,True),"count":count})
		t.add(run1,{"sleepSec":0.01},callback1,callback2,{"ret":TASK_CONTINUE,"value":(True,True),"count":count})
		t.add(run1,{"sleepSec":0.01},callback1,callback2,{"ret":TASK_CONTINUE,"value":(True,False),"count":count})
		assert not t._queue.empty()
		t.wait() 
		assert count[0] == 6
 
	#before cancel 
	count[0] = 0
	t.add(run1,{"sleepSec":0.1},callback1,callback2,{"ret":TASK_CONTINUE,"value":(True,True),"count":count})
	t.add(run1,{"sleepSec":0.1},callback3,callback2,{"ret":TASK_CANCEL,"value":(True,True),"count":count})
	t.add(run1,{"sleepSec":0.1},callback1,callback2,{"ret":TASK_CONTINUE,"value":(True,False),"count":count})
	t.wait()  
	assert count[0] == 3
	
	#finish cancel 
	count[0] = 0
	t.add(run1,{"sleepSec":0.01},callback1,callback2,{"ret":TASK_CONTINUE,"value":(True,True),"count":count})
	t.add(run1,{"sleepSec":0.01},callback1,callback2,{"ret":TASK_CANCEL,"value":(True,True),"count":count})
	t.add(run1,{"sleepSec":0.01},callback1,callback2,{"ret":TASK_CONTINUE,"value":(True,False),"count":count})
	t.wait()
	
	def callback4(params): 
		if params["count"][0] == 4:
			return TASK_CONTINUE
		params["count"][0] += 1
		return TASK_WAIT 
		
	#before wait 
	count[0] = 0
	t.add(run1,{"sleepSec":0.01},callback4,callback2,{"ret":TASK_CONTINUE,"value":(True,True),"count":count})
	t.add(run1,{"sleepSec":0.01},callback1,callback2,{"ret":TASK_CONTINUE,"value":(True,False),"count":count})
	t.wait()
	assert count[0] == 7
	
	def run2():
		raise Exception("Error")
	#exception 
	def callback5(result,more,params):
		assert "exception" in params
		print(params["exception"] , str(Exception("Error")))
		assert params["exception"] == str(Exception("Error"))
		return TASK_CONTINUE
	count[0] = 0
	t.add(run2,{},callback1,callback5,{"ret":TASK_CONTINUE,"value":(True,True),"count":count})
	t.add(run1,{"sleepSec":0.01},callback1,callback2,{"ret":TASK_CONTINUE,"value":(True,False),"count":count})
	t.wait() 
	assert count[0] == 3
	t.fini()
	
if __name__ == '__main__': 
	import utility
	utility.start()
	utility.run_tests(__file__)
	utility.finish()
	
	
	
	
	
	
