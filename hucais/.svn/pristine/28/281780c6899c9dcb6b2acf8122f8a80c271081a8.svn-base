import sys, os
import time
import setup

if __name__ == '__main__':
	setup.setCurPath(__file__)
import log
import webutility
import mqtt
import json_codec as json

url = 'http://127.0.0.1:' + str(webutility.readPort())


def http_get(url, param, timeout=5):
	r = webutility.http_get(url, param, timeout=timeout)
	result = json.load(r)
	if result["errorno"] != 0:
		raise Exception(result["errormsg"])
	return result


def playAudio(agvId, name, loop):
	return _req('/api/agv/playaudio', agvId, name=name, loop=loop)


def resumeAudio(agvId):
	return _req('/api/agv/resumeaudio', agvId)


def stopAudio(agvId):
	return _req('/api/agv/stopaudio', agvId)


def _req(apiurl, agvId, **param):
	param["agv"] = agvId
	try:
		return http_get(url + apiurl, param)
	except:
		raise


if __name__ == '__main__':
	pass
