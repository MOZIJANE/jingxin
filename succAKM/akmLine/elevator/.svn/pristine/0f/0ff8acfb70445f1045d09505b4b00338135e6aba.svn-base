import sys, os
import setup

if __name__ == '__main__':
	setup.setCurPath(__file__)
import log
import webutility
import time
import json_codec as json
import utility
if utility.is_run_all():
	import main_elevator
	
url = 'http://127.0.0.1:' + str(webutility.readPort())


def http_get(url, param,writelog=True):
	try:
		r = webutility.http_get(url, param,timeout=10,writelog=writelog)
		result = json.load(r)
		if result["errorno"] != 0:
			log.error("elevatorApi failed:",result["errormsg"])
			return {}
		return result
	except Exception as e:
		log.exception("elevatorApi",e)
		return {}


def hold(elevatorId):
	log.info('open door %s'%elevatorId)
	apiurl='/api/elevator/hold'
	param = {"id": elevatorId}
	return http_get(url + apiurl, param)


def unhold(elevatorId):
	log.info('close door %s'%elevatorId)
	apiurl='/api/elevator/unhold'
	param = {"id": elevatorId}
	return http_get(url + apiurl, param)  


def goFloor(elevatorId,floorId):
	assert isinstance(floorId,int)
	log.info('go floor %s by %s '%(floorId, elevatorId))
	apiurl='/api/elevator/go'
	param = {"id": elevatorId, "floor":floorId}
	return http_get(url + apiurl, param) 
	

#{'isOpening': 0, 'isClosing': 0, 'isFinishOpen': 1, 'isRunning': 0, 'isMaintain': 'normal', 'isUpward': 0, 'isDownward': 0, 'inFloor': 2, 'frontDoorRegist': 0, 'backDoorRegist': 0, 'frontDoorRelease': 0, 'backDoorRelease': 0, 'errorno': 0, 'errormsg': ''} 
def status(elevatorId): 
	apiurl='/api/elevator/status'
	param = {"id": elevatorId}
	ret = http_get(url + apiurl, param,writelog=False)  
	if "isOpening" not in ret:
		return None
	return ret

# test

def test_elevator():
	elevatorId='ELEVATOR01'
	while True:
		span = 0.5
		time.sleep(span)
		goFloor(elevatorId,2)
		time.sleep(span)
		goFloor(elevatorId)
		time.sleep(20)
		goFloor(elevatorId,1)
		time.sleep(span)
		goFloor(elevatorId)


if __name__ == '__main__':
	test_elevator()

