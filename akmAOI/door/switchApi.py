import sys, os
import setup

if __name__ == '__main__':
	setup.setCurPath(__file__)
import log
import webutility
import time
import json_codec as json
import utility
url = 'http://127.0.0.1:' + str(webutility.readPort())


def http_get(url, param):
	r = webutility.http_get(url, param)
	result = json.load(r)
	if result["errorno"] != 0:
		raise Exception(result["errormsg"])
	return result



def switchOpen(switchId):
	if utility.is_test():
		time.sleep(3) 
		return True
	return _switch('/api/switch/on', switchId)


def switchClose(switchId):
	if utility.is_test():
		time.sleep(3)
		return True
	return _switch('/api/switch/off', switchId)


def switchIsLock(switchId):
	if utility.is_test():
		time.sleep(3)
		return True
	return _switch('/api/switch/islock', switchId)


def _switch(apiurl, id):
	param = {"id": id}
	try:
		return http_get(url + apiurl, param)
	except:
		raise

# test

def test_switch():
	switchId='DOOR01'
	while True:
		span = 0.5
		time.sleep(span)
		switchOpen(switchId)
		time.sleep(span)
		switchClose(switchId)
		time.sleep(span)
		switchOpen(switchId)
		time.sleep(span)
		switchClose(switchId)


if __name__ == '__main__':
	test_switch()

