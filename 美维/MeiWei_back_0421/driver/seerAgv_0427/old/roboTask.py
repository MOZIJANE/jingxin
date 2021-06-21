import datetime
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import mongodb as db
import enhance
import lock
import threading
import driver.seerAgv_0427.roboModel as roboModel

putEvent = enhance.event()
editEvent = enhance.event()
clearEvent = enhance.event()

g_lock = threading.RLock()


@lock.lock(g_lock)
def putTask(id, code, data, type,groupsn):
	ds = roboModel.taskItem(sn=id, code=code, data=data, type=type,groupsn=groupsn).getdict()
	sn = ds['sn']
	code = ds['code']
	type = ds['type']
	ret = db.update_one("u_robo_task", filter={'sn': id}, fields=ds, update_or_insert=True)
	ds = db.find("u_robo_task")
	result = ds.list()
	maxlen= max(10,len(result))

	for index in range(0,maxlen-10):
		current= result[index]
		currentstatus=current['status']
		if currentstatus != 1 and currentstatus != -1:
			currentsn=current['sn']
			clearTask(currentsn)
	
	putEvent.emit(sn)
	if ret.upserted_id is None:
		raise Exception('添加任务失败,sn:{sn},code:{code}'.format(sn=id, code=code))


@lock.lock(g_lock)
def editTask(id, code, status, errorno=0, errormsg='',startTime=None, finishTime=None):
	ds = db.find_one("u_robo_task", {"sn": id, "code": code})
	ds['status'] = status
	ds['errorno'] = errorno
	ds['errormsg'] = errormsg
	if startTime is not None:
		ds['startTime']=startTime
	if errorno == -2 or errorno == 0:
		if finishTime is not None:
			ds['finishTime'] = finishTime
	ret = db.update_one("u_robo_task", filter={'sn': id}, fields=ds)
	editEvent.emit(id)
	if ret is not None and ret.modified_count != 1:
		raise Exception('修改任务失败,sn:{sn},code:{code}'.format(sn=id, code=code))


@lock.lock(g_lock)
def clearTask(id):
	ds = db.find_one("u_robo_task", {"sn": id})
	delresult = db.delete_one("u_robo_task", {"_id": ds["_id"]})
	if delresult is not None and delresult.deleted_count == 1:
		db.insert("u_robo_task_histroy", ds)
		clearEvent.emit(ds['sn'])
	else:
		raise Exception('清除任务失败,sn:{sn}'.format(sn=id))



def setorUpdateTasks(ds,sn):
	ds['createTime'] = datetime.datetime.now()
	ds['lastRunningTime'] = None
	ds['runCount']=0
	ds['sn']=sn
	ret = db.update_one("u_robo_tasks", filter={'sn': sn}, fields=ds, update_or_insert=True)
	if ret.upserted_id is None and ret.modified_count==0:
		raise Exception('添加任务链失败,sn:{sn}'.format(sn=sn))
	
	
def getTasks():
	ds = db.find("u_robo_tasks")
	result = ds.list()
	return result

def getTasksBySn(sn):
	result = db.find_one("u_robo_tasks", filter={'sn': sn})
	return result

def getTask():
	ds = db.find("u_robo_task")
	result = ds.list()
	return result

def delTasks(id):
	delresult = db.delete_one("u_robo_tasks", {"sn": id})
	if delresult is None or delresult.deleted_count == 0:
		raise Exception('删除任务链失败,sn:{sn}'.format(sn=id))

def getTaskHistory():
	ds = db.find("u_robo_task_histroy", {})
	result = ds.list()
	return result


def getOverrunTask(code):
	ds = db.find_one("u_robo_task", {"status": 1, "code": code})
	return ds


if __name__ == '__main__':
	pass
