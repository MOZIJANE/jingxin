import sys, os
import setup

if __name__ == '__main__':
	setup.setCurPath(__file__)
import log
import webutility
import time
import json_codec as json
import utility
import remoteio.mockRemoteioControl as mockRemoteioControl
url = 'http://127.0.0.1:' + str(webutility.readPort())
port=502

def http_get(url, param):
	r = webutility.http_get(url, param)
	result = json.load(r)
	if result["errorno"] != 0:
		raise Exception(result["errormsg"])
	return result


def writeDO(id, index, value):
	mockRemoteioControl.setDO(id, port, index, value)


def writeDOList(id, values):
	return _addBackResult(status=mockRemoteioControl.setDOs(id, port, values))

def writeDI(id, index, value):
	mockRemoteioControl.setDI(id, port, index, value)

def writeDIList(id, values):
	return _addBackResult(status=mockRemoteioControl.setDIs(id, port, values))

def readDI(id, index):
	return _addBackResult(status= mockRemoteioControl.readDI(id, port, index))



def readDO(id, index):
	return _addBackResult(status= mockRemoteioControl.readDO(id, port, index))



def readDIList(id):
	return _addBackResult(status=mockRemoteioControl.readDIs(id, port))



def readDOList(id):
	return _addBackResult(status=mockRemoteioControl.readDOs(id, port))



def _addBackResult(errorno=0, errormsg='', **retDic):
	if retDic is None:
		retDic = {}
	retDic["errorno"] = errorno
	if errorno != 0:
		retDic["errormsg"] = errormsg
	else:
		assert not errormsg
		retDic["errormsg"] = ""
	return retDic

# test

def test_remoteio():
	id = 'ZLAN01'
	while True:
		span = 0.5
		writeDOList(id, [1, 1, 1, 1, 1, 1, 1, 1])
		time.sleep(span)
		writeDOList(id, [0, 0, 0, 0, 0, 0, 0, 0])
		time.sleep(span)
		writeDO(id, 2, 1)
		time.sleep(span)
		writeDO(id, 3, 1)
		time.sleep(span)

		print(readDO(id))


if __name__ == '__main__':
	test_remoteio()
