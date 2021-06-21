#coding=utf-8
#ZhengShaoGong		2017-08-18		create
#lizhenwei			2017-08-28		modify
import os,sys
import ctypes
import time
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import utility

if utility.is_win32():
	dllpath = os.path.dirname(__file__) + "/"+"PHB02B_32.dll"
elif utility.is_win64():
	dllpath = os.path.dirname(__file__) + "/"+"PHBX_64.dll"
	
g_handStickdll = ctypes.windll.LoadLibrary(dllpath)	
assert(g_handStickdll)
g_erowlen = [11,16,16,16] # 每行占用的字符数
g_buflen = ctypes.c_int(sum(g_erowlen))
g_buf = (ctypes.c_char * g_buflen.value)()
g_buf[:]=(' '*g_buflen.value).encode('utf-8')

def openStick():
	global g_handStickdll
	g_handStickdll.Xinit()
	return 0 == g_handStickdll.XOpen(18)

def closeStick():
	global g_handStickdll
	return 0 == g_handStickdll.XClose()

def showMsgRow0(msg):
	'第0行显示最多11个字符'
	return showMsgRow(msg,0)
	
def showMsgRow1(msg):
	'第1行显示最多16个字符'
	return showMsgRow(msg,1)
	
def showMsgRow2(msg):
	'第2行显示最多16个字符'
	return showMsgRow(msg,2)

def showMsgRow3(msg):
	'第3行显示最多16个字符'
	return showMsgRow(msg,3)

def clearMsgRow0():
	return clearMsgRow(0)

def clearMsgRow1():
	return clearMsgRow(1)

def clearMsgRow2():
	return clearMsgRow(2)

def clearMsgRow3():
	return clearMsgRow(3)
	
def clearMsg():
	global g_buf,g_erowlen
	g_buf[:] = (' '* (sum(g_erowlen))).encode('utf-8')
	return sendOutput()
	
def clearMsgRow(rowId):
	global g_buf,g_erowlen
	assert rowId < len(g_erowlen)
	msg = ' '*g_erowlen[rowId]
	return showMsgRow(msg, rowId)
	
def showMsgRow(msg, rowId):
	setBufMsg(msg, rowId)
	return sendOutput()

def setBufMsg(msg, rowId):
	global g_buf,g_erowlen
	tl = len(msg)
	if 0 == rowId:
		st = 0
		ed = g_erowlen[0]
	elif 1 == rowId:
		st = g_erowlen[0]
		ed = st + g_erowlen[1]
	elif 2 == rowId:
		st = sum(g_erowlen[:2])
		ed = st + g_erowlen[2]
	elif 3 == rowId:
		st = sum(g_erowlen[:3])
		ed = st + g_erowlen[3]
	l = ed - st
	assert tl <= l
	if msg:
		g_buf[st:st+tl] = msg.encode('utf-8')
	if tl < l:
		sp = l - tl
		g_buf[st+tl:ed] = (' '*sp).encode('utf-8')

def getInput():
	# 经测试最大支持2个按键同时按下
	global g_handStickdll
	d = ctypes.c_int(0)
	count = ctypes.c_char(0)
	r = g_handStickdll.XGetInput(ctypes.byref(d), ctypes.byref(count))
	if 0!=r:
		return None
	d = d.value
	keyList = []
	while True:
		ebyte = d&0xff
		if not ebyte:
			break
		keyList.append(ebyte)
		d = d>>8
	return keyList
	
def sendOutput():
	global g_handStickdll,g_buf,g_buflen
	r = g_handStickdll.XSendOutput(g_buf, ctypes.byref(g_buflen))
	return 0==r
	
def test_stick():
	assert openStick()
	assert clearMsg()
	assert showMsgRow0("Enable")
	assert showMsgRow1("SPEED 1")
	assert showMsgRow2("X:123.4 Y:321.5")
	assert showMsgRow3("Z:80.4  R:-123.4")
	while True:
		keyList = getInput()
		if len(keyList) == 0:
			# print('no Key')
			pass
		else:
			print('press ', keyList)
		time.sleep(0.02)	
	assert closeStick()
	
def test_msg():
	import random
	assert openStick()
	assert clearMsg()
	assert showMsgRow0("Enable")
	assert showMsgRow1("SPEED ++")
	while True:
		x,y = random.uniform(0,500),random.uniform(0,500)
		z = random.uniform(0,100)
		r = random.uniform(-175,175)
		assert showMsgRow("X:%5.1f Y:%6.1f"%(x,y),2)
		assert showMsgRow("Z:%5.1f R:%6.1f"%(z,r),3)
		time.sleep(1)
	
if __name__ == '__main__':
	# test_stick()
	test_msg()