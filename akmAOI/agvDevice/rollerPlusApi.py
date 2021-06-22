import sys,os 
import time
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import log
import webutility
import mqtt
import json_codec as json

url = 'http://127.0.0.1:'+str(webutility.readPort())

def http_get(url,param,timeout=30):
	r = webutility.http_get(url, param,timeout=timeout)
	result = json.load(r)
	if result["errorno"] != 0: 
		raise Exception(result["errormsg"])
	return result
	
#返回值
#paramObj["result"] = True
#paramObj["resultDesc"] = "success" 

def rollerSetInit(agvId):
	return _roller('/api/agv/rollerSetInit', agvId)

def rollerRobotLoad(agvId, unitId):
	return _roller('/api/agv/rollerRobotLoad', agvId, unitId = unitId)

def rollerRobotUnLoad(agvId, unitId):
	return _roller('/api/agv/rollerRobotUnLoad', agvId, unitId = unitId)

def rollerRobotBarUp(agvId, unitId):
	return _roller('/api/agv/rollerRobotBarUp', agvId, unitId = unitId)

def rollerRobotBarDown(agvId, unitId):
	return _roller('/api/agv/rollerRobotBarDown', agvId, unitId = unitId)

def checkBarUpStatus(agvId, unitId):
	return _roller('/api/agv/checkBarUpStatus', agvId, unitId = unitId)

def checkBarDownStatus(agvId, unitId):
	return _roller('/api/agv/checkBarDownStatus', agvId, unitId = unitId)


def rollerRobotStop(agvId):
	return _roller('/api/agv/rollerRobotStop', agvId)

def checkUnitStatus(agvId, unitId):
	return _roller('/api/agv/checkUnitStatus', agvId, unitId = unitId)

def checkUnitloadStatus(agvId, unitId):
	return _roller('/api/agv/checkUnitloadStatus', agvId, unitId = unitId)

def checkUnitUnloadStatus(agvId, unitId):
	return _roller('/api/agv/checkUnitUnloadStatus', agvId, unitId = unitId)



def rollerEmergency(agvId):
	return _roller('/api/agv/rollerEmergency', agvId)

	
def rollerRes(agvId):
	return _roller('/api/agv/rollerRes', agvId)
	

	
def _roller(apiurl,agvId,timeoutSec=30,**param):
	param["agv"] = agvId
	param["timeoutSec"] = timeoutSec
	try: 
		return http_get(url + apiurl, param,timeout=timeoutSec+2)
	except Exception as e:
		log.debug(e)
		raise

if __name__ == '__main__':
	while True:
		time.sleep(2)

