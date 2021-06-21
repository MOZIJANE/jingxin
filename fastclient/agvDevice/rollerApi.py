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
		raise IOError(result["errormsg"])
	return result
	
#返回值
#paramObj["result"] = True
#paramObj["resultDesc"] = "success" 

def rollerSetUnit(agvId, unitId):
	return _roller('/api/agv/rollerSetUnit', agvId, unitId=unitId)


def rollerBackLoad(agvId, unitId):
	return _roller('/api/agv/rollerBackLoad', agvId, unitId=unitId)

def rollerBackUnload(agvId, unitId):
	return _roller('/api/agv/rollerBackUnload', agvId, unitId=unitId)

def rollerFrontLoad(agvId, unitId):
	return _roller('/api/agv/rollerFrontLoad', agvId, unitId=unitId)
	
def rollerFrontUnload(agvId, unitId):
	return _roller('/api/agv/rollerFrontUnload', agvId, unitId=unitId)
	

def rollerLoadStatus(agvId, unitId):
	return _roller('/api/agv/rollerLoadStatus', agvId, unitId=unitId)
	
def rollerUnloadStatus(agvId, unitId):
	return _roller('/api/agv/rollerUnloadStatus', agvId, unitId=unitId)


def rollerClampOpen(agvId, dir):
	return _roller('/api/agv/rollerClampOpen', agvId, dir=dir)


def rollerClampClose(agvId, dir):
	return _roller('/api/agv/rollerClampClose', agvId, dir=dir)


def finishButtonStatus(agvId):
	return _roller('/api/agv/finishButtonStatus', agvId)


def rollerClampStatus(agvId,dir):
	return _roller('/api/agv/rollerClampStatus', agvId, dir=dir)


def unitStatus(agvId, unitId):
	return _roller('/api/agv/unitStatus', agvId, unitId=unitId)
	
def rollerStop(agvId):
	return _roller('/api/agv/rollerStop', agvId)
	
def rollerReset(agvId):
	return _roller('/api/agv/rollerReset', agvId)
	
def rollerDeviceInfo(agvId):
	return _roller('/api/agv/rollerDeviceInfo', agvId)
	
def _roller(apiurl,agvId,timeoutSec=5,**param):
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

