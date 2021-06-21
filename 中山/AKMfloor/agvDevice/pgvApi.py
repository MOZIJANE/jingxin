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
		raise IOError(result["errormsg"])
	return result
	
def getPgv(agvId):
	param = {"agv": agvId}
	try: 
		return http_get(url + '/api/agv/getpgv', param)
	except:
		raise

if __name__ == '__main__':
	print (getPgv("AGV03"))
	while True:
		time.sleep(2)


