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


def writeDO(id, index, value):
	param = {"index": index, "value": value}
	return _remoteio('/api/remoteio/writeDO', id, param)


def writeDOList(id, values):
	param = {"value": values}
	return _remoteio('/api/remoteio/writeDOList', id, param)


def readDI(id, index):
	param = {"index": index}
	return _remoteio('/api/remoteio/readDI', id, param)


def readDO(id, index):
	param = {"index": index}
	return _remoteio('/api/remoteio/readDO', id, param)


def readDIList(id):
	param = dict()
	return _remoteio('/api/remoteio/readDIList', id, param)


def readDOList(id):
	param = dict()
	return _remoteio('/api/remoteio/readDOList', id, param)

#测试用
def writeDI(id, index, value):
	param = {"index": index, "value": value}
	return _remoteio('/api/remoteio/writeDI', id, param)


def writeDIList(id, values):
	param = {"value": values}
	return _remoteio('/api/remoteio/writeDIList', id, param)


def _remoteio(apiurl, id, param):
	param["id"] = id
	return http_get(url + apiurl, param)


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
