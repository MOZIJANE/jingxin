#coding=utf-8
#ZhengShaoGong		2017-08-18		create
import os,sys
from ctypes import *
import time

currentPath = os.path.dirname(__file__)

if __name__ == '__main__':
	if currentPath != "":
		os.chdir(currentPath)
	
g_handStickdll = windll.LoadLibrary("PHB02B.dll")

assert(g_handStickdll)

g_handStickdll.Xinit()
r = g_handStickdll.XOpen(18)
dataint = c_int(0)
t1 = c_ubyte(1)
data = c_ubyte*59
data_in = data(b'r',b'5',b'e',b'd',30,6,7,7,8,9,9,6,56,5,5,5,5,5,5,5);
data_in[4] = b'y'
data_in[5] = b'g'
data_in[6] = c_ubyte(48).value + t1.value
str_t = b"hello"
#datap=data(1,2,3,4,5,6,7....(dataLen)
i=1
j=8
s="heelo"
sendbufferLen = c_char(8)
print (str_t)
while i>0:
	g_handStickdll.XGetInput(byref(dataint),byref(dataLen))
	if dataint.value >0:
		print(dataint.value)		
		g_handStickdll.XSendOutput(data_in,byref(dLen));
		data_in[6] = data_in[6].value + t1.value
		time.sleep(0.5)
	time.sleep(0.1)
	

print(r)
