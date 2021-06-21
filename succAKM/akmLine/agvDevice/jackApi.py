import sys,os 
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import log,utility
if utility.is_run_all():
	import main_agvDevice
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
def jackDistanceStatus(agvId,timeoutSec=90):
	"""resultData = {
					"hasAlarm": 1,
					"nutrualStatus": 1,
					"jackStatus": 4096,
					"rotationStatus": (4096,1)
				}"""
	return _jack('/api/agv/jackDistanceStatus', agvId,timeoutSec)


def jackDeviceInfo(agvId,timeoutSec=90):
	"""resultData = {
					"hasAlarm": 1,
					"nutrualStatus": 1,
					"jackStatus": 4096,
					"rotationStatus": (4096,1)
				}"""
	return _jack('/api/agv/jackdeviceinfo', agvId,timeoutSec)
 
def jackUp(agvId,timeoutSec=90,loc=None):
	return _jack('/api/agv/jackup', agvId,timeoutSec,loc)

def jackDown(agvId,timeoutSec=90,loc=None):
	return _jack('/api/agv/jackdown', agvId,timeoutSec,loc) 


def jackUpCattle(agvId,timeoutSec=90):
	return _jack('/api/agv/jackUpCattle', agvId,timeoutSec)

def jackDownCattle(agvId,timeoutSec=90):
	return _jack('/api/agv/jackDownCattle', agvId,timeoutSec)

def jackClearCattle(agvId,timeoutSec=90):
	return _jack('/api/agv/jackClearCattle', agvId,timeoutSec)


def jackUpStatus(agvId,timeoutSec=90):
	return _jack('/api/agv/jackupstatus', agvId,timeoutSec)

def jackDownStatus(agvId,timeoutSec=90):
	return _jack('/api/agv/jackdownstatus', agvId,timeoutSec)


def jackStop(agvId):
	return _jack('/api/agv/jackstop', agvId)
	
def _jack(apiurl,agvId,timeoutSec,loc=None):
	param = {"agv": agvId, "timeoutSec": timeoutSec,"loc":loc}
	try: 
		return http_get(url + apiurl, param,timeout=timeoutSec+2)
	except:
		raise

if __name__ == '__main__':
	jackUp("AGV01")
	while True:
		import time
		time.sleep(2)


