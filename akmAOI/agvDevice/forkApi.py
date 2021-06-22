import sys,os 
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import log,utility
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
	

def forkLoad(agvId,timeoutSec=90,loc=None):
	return _fork('/api/agv/forkLoad', agvId,timeoutSec,loc)

def forkUnload(agvId,timeoutSec=90,loc=None):
	return _fork('/api/agv/forkUnload', agvId,timeoutSec,loc)

def forkUpStatus(agvId,timeoutSec=90):
	return _fork('/api/agv/forkUpStatus', agvId,timeoutSec)

def forkDownStatus(agvId,timeoutSec=90):
	return _fork('/api/agv/forkDownStatus', agvId,timeoutSec)

def forkReset(agvId,timeoutSec=90):
	return _fork('/api/agv/forkreset', agvId,timeoutSec)


def _fork(apiurl,agvId,timeoutSec,loc=None):
	param = {"agv": agvId}
	try: 
		return http_get(url + apiurl, param,timeout=timeoutSec+2)
	except:
		raise

if __name__ == '__main__':
	while True:
		import time
		time.sleep(2)


