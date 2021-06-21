import sys,os 
import time
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
		raise IOError(str(result["errormsg"]))
	return result
	
#返回值
#paramObj["result"] = True
#paramObj["resultDesc"] = "success" 
	
def rotationReset(agvId,timeoutSec=30):
	return _rotation('/api/agv/rotationreset', agvId,timeoutSec)
	
def rotationClear(agvId,timeoutSec=30):
	return _rotation('/api/agv/rotationclear', agvId,timeoutSec)
 	
def rotationLeft(agvId,target=90,timeoutSec=30):
	return _rotation('/api/agv/rotationleft', agvId,timeoutSec,target=int(target)) 

def rotationRight(agvId,target=90,timeoutSec=30):
	return _rotation('/api/agv/rotationright', agvId,timeoutSec,target=int(target)) 

def rotationStop(agvId,timeoutSec=90):
	return _rotation('/api/agv/rotationstop', agvId,timeoutSec)
	
def rotationDistanceStatus(agvId,timeoutSec=10):
	return _rotation('/api/agv/rotationdistancestatus', agvId,timeoutSec)
	
def _rotation(apiurl,agvId,timeoutSec,**param):
	param["agv"] = agvId
	param["timeoutSec"] = timeoutSec
	try: 
		return http_get(url + apiurl, param,timeout=timeoutSec)
	except:
		raise

if __name__ == '__main__':
	# rotationLeft("AGV02")
	# rotationRight("AGV02")
	rotationReset("AGV05")
	while True:
		time.sleep(2)


