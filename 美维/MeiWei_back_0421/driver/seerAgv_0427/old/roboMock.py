import  threading
import time
import  json
import driver.seerAgv_0427.roboKit as roboKit
import driver.seerAgv_0427.roboModel as roboModel
import driver.seerAgv_0427.roboTask as roboTask

server19204=None
server19206=None


g_allstate=roboKit.demoDict['11100']

def startMock():
	global server19204
	global server19206

	if server19204  is None:
		server19204= roboKit.robotServer('192.168.31.196',roboModel.API_PORT_STATE)
	thread2 = threading.Thread(target=startStateServer)
	thread2.start()

	if server19206  is None:
		server19206= roboKit.robotServer('192.168.31.196',roboModel.API_PORT_TASK)
	thread3 = threading.Thread(target=startTaskServer)
	thread3.start()

def startStateServer():
	server19204.start(getSendDataState)

def startTaskServer():
	server19206.start(getSendDataCtrl)

def getSendDataState(index, bodyResult):
	global g_allstate

	return g_allstate

def getSendDataCtrl(index, bodyResult):
	global g_allstate
	global g_flag
	if  index=='13051':
		_thread = threading.Thread(target=countDown, kwargs={'dur': 10}, name="timer_thread")
		_thread.start()

		result = bodyResult.decode("utf-8")

		if len(result) == 0:
			return
		dataresult = json.loads(result)
		g_allstate['target_id']=dataresult['id']
		g_allstate['task_status'] = roboModel.TASK_STATUS_RUNNING
		return ""


def countDown( dur):
	global g_allstate
	if dur < 0:
		return
	g_allstate['task_status'] = roboModel.TASK_STATUS_RUNNING
	time.sleep(dur)
	g_allstate['task_status'] = roboModel.TASK_STATUS_COMPLETED


def endMock():
	global server19204
	global server19205
	if server19204  is not None:
		server19204.end()
	if server19205  is not None:
		server19205.end()



if __name__=='__main__':
	startMock()