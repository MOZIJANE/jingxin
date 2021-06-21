# coding: utf-8
# author: ives
# date: 2018-03-01
# desc: IO控制模块通用接口

import sys
import os
import json

if __name__ == '__main__':
	currentPath = os.path.dirname(__file__)
	if currentPath != "":
		os.chdir(currentPath)

import log


#返回配置信息
def getConfs(path):
	fileList = []
	if os.path.exists(path):
		dirs = os.listdir(path)
		for d in dirs:
			file = path + '/' + d
			if os.path.isfile(file):
				fileList.append(file)
	confs = []
	for f in fileList:
		try:
			fd = open(f, 'r')
			data = json.load(fd)
			fd.close()
			confs.append(data)
			log.info('[ioutility: getConfs] load file \'%s\'. ' %f)
		except Exception as e:
			log.exception("[ioutility: getConfs] catct except: ", e)
	return confs


# 字符串转整数
def str2Int(hex):
	if not isinstance(hex, str):
		log.warning('[ioutility: Hex2Int] param is not string.')
		return 0
	val = hex.replace(' ', '')
	if val[:2] == '0x':
		return int(val, 16)
	elif val.isdigit():
		return int(val)
	else:
		log.warning('[ioutility: Hex2Int] param is not int string.')
		return 0


#========================================== unit test ==========================================
def test_getConfs():
	def deldir(path):
		if not os.path.exists(dir):
			return
		files = os.listdir(path)
		for f in files:
			os.remove(path + '/' + f)
		os.rmdir(path)

	dir = os.path.realpath(sys.path[0]) + '/test'
	deldir(dir)
	if not os.path.exists(dir):
		os.mkdir(dir)
	for idx in range(10):
		data = {'order': idx, 'num': {"int" : idx, "hex" : "0x01"}, "str": ["hehe", "2018"]}
		f = dir + '/cfg_' + str(idx) + '.json'
		json.dump(data, open(f, "w"))
	confs = getConfs(dir)
	assert len(confs) == 10
	deldir(dir)


def test_str2Int():
	assert str2Int(1) == 0
	assert str2Int("") == 0
	assert str2Int("0xab") == 0xab
	assert str2Int(" 0xab ") == 0xab
	assert str2Int(" 221 ") == 221
		
if __name__ == '__main__':
	#test_getConfs()
	test_str2Int()



