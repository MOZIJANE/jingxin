#coding=utf-8
# ycat			2017-08-27	  create 
import sys,os
import datetime
import utility
import logging
import datetime 
from ctypes import *

cc_map = {
	'default'	  :0,
	'black'		:1,
	'blue'		 :2,
	'green'		:3,
	'cyan'		 :4,
	'red'		  :5,
	'magenta'	  :6,
	'brown'		:7,
	'lightgray'	:8,
	'darkgray'	 :9,
	'lightblue'	:10,
	'lightgreen'   :11,
	'lightcyan'	:12,
	'lightred'	 :13,
	'lightmagenta' :14,
	'yellow'	   :15,
	'white'		:16,
}
		 
CloseHandle = windll.kernel32.CloseHandle
GetStdHandle = windll.kernel32.GetStdHandle
GetConsoleScreenBufferInfo = windll.kernel32.GetConsoleScreenBufferInfo
SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute
 
STD_OUTPUT_HANDLE = -11
 
class COORD(Structure):
   _fields_ = [('X', c_short),
			   ('Y', c_short),
			  ]
 
class SMALL_RECT(Structure):
   _fields_ = [('Left', c_short),
			   ('Top', c_short),
			   ('Right', c_short),
			   ('Bottom', c_short),
			  ]
				
class CONSOLE_SCREEN_BUFFER_INFO(Structure):
   _fields_ = [('dwSize', COORD),
			   ('dwCursorPosition', COORD),
			   ('wAttributes', c_uint),
			   ('srWindow', SMALL_RECT),
			   ('dwMaximumWindowSize', COORD),
			  ]
 
def printColor(fore_color, back_color, text): 
	#prepare
	hconsole = GetStdHandle(STD_OUTPUT_HANDLE)
	cmd_info = CONSOLE_SCREEN_BUFFER_INFO()
	GetConsoleScreenBufferInfo(hconsole, byref(cmd_info))
	old_color = cmd_info.wAttributes
 
	#calculate colors
	fore = cc_map[fore_color]
	if fore: fore = fore - 1
	else: fore = old_color & 0x0F
	back = cc_map[back_color]
	if back: back = (back - 1) << 4
	else: back = old_color & 0xF0
 
	#real output
	SetConsoleTextAttribute(hconsole, fore + back)
	print( text,)
	SetConsoleTextAttribute(hconsole, old_color)
   

class winLoggerHander(logging.Handler): 
	def __init__(self,max_size = 10240): 
		logging.Handler.__init__(self)

	def emit(self,record): 
		b = "black"
		if record.levelno == 50:
			c = "white"
			b = "lightred"
			n = "FATAL"
		elif record.levelno == 20:
			c = "lightcyan"
			n = "INFO "
		elif record.levelno == 30 or record.levelno == 31:
			c = "yellow"
			n = "WARN "
		elif record.levelno == 35:
			c = "lightgreen"
			n = "SUCC "
		elif record.levelno == 40:
			c = "lightred"
			n = "ERROR"
		else:
			c = "white"
			n = "DEBUG"
		msg = "[%s]\t%s: %s"%(n,utility.now_str(True),record.getMessage())
		printColor(c,b,msg)
		 

#############################	unit test	###########################	 
def testColor():
	printColor("white","black","debug")
	printColor("lightgreen","black","info")
	printColor("lightcyan","black","warning")
	printColor("yellow","black","warning")
	printColor("lightred","black","error")
	printColor("white","lightred","critical") 

if __name__ == "__main__": 
	utility.run_tests()
	
		