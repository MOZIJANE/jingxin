#coding=utf-8 
# ycat			 2015/04/10      create
#重命令基本函数，这样utility可以使用 
import sys,os
import operator
import time

def is_python3():
	return sys.version[0] == '3'
	
def is_run_all():
	return "runAll" in os.environ
	
def os_cmp(o1,o2):
	if is_python3():
		if operator.eq(o1,o2):
			return 0
		else:
			return -1
	else:	
		return cmp(o1,o2)
	
g_app_name = ""

def app_name():
	if is_run_all():
		return "runall"
	global g_app_name
	if g_app_name == "":
		def _get_app_name():
			#从上一级目录取进程信息
			p = os.path.split(os.path.dirname(os.getcwd()+"/"))
			return p[-1]
		g_app_name = _get_app_name()
	return g_app_name

def set_app_name(name):
	global g_app_name
	g_app_name = name
	
def ticks():
	return int(time.time()*1000) 	