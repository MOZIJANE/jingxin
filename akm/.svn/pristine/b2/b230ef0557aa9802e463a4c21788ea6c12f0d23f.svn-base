# coding: utf-8
# author: pengshuqin
# date: 2019-10-17
# desc: 模拟器

import os
import sys
import threading
import time
import setup

if __name__ == '__main__':
	setup.setCurPath(__file__)

import log
import utility

g_remoteioList = {}
g_remoteDiList = {}


def _getTestRemoteio(id):
	global g_remoteioList
	if id not in g_remoteioList:
		g_remoteioList[id] = [0]*8
	return g_remoteioList[id]
 
def _getTestRemoteDi(id):
	global g_remoteDiList
	if id not in g_remoteDiList:
		g_remoteDiList[id] = [0]*8
	return g_remoteDiList[id]

def setDO(ip,port,addr, value):
	_getTestRemoteio(ip)[addr] = value
	return _getTestRemoteio(ip)

def setDOs(ip,port, value):
	values = list(map(lambda x:int(x),value.split(',')))
	assert len(_getTestRemoteio(ip)) == len(values)
	for i in range(0,len(values)):
		_getTestRemoteio(ip)[i] = values[i]
	return _getTestRemoteio(ip)

def setDI(ip,port,addr, value):
	_getTestRemoteDi(ip)[addr] = value
	return _getTestRemoteDi(ip)

def setDIs(ip,port, value):
	values = list(map(lambda x:int(x),value.split(',')))
	assert len(_getTestRemoteDi(ip)) == len(values)
	for i in range(0,len(values)):
		_getTestRemoteDi(ip)[i] = values[i]
	return _getTestRemoteDi(ip)
	
def readDI(ip,port,addr):
	return _getTestRemoteDi(ip)[addr]

def readDIs(ip,port):
	return _getTestRemoteDi(ip)

def readDO(ip,port,addr):
	return _getTestRemoteio(ip)[addr]


def readDOs(ip,port):
	return _getTestRemoteio(ip)




