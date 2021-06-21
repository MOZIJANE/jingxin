#coding=utf-8
# ycat			2018-07-10	  create
# 实时曲线图 
import sys,os
import re
import datetime
import utility
import mongodb as db
import scadaUtility
import json_codec
import bottle
import webutility 

g_installModule = set()

def install():
	global g_installModule
	n = utility.app_name()
	if n not in g_installModule:
		g_installModule.add(n)
		scadaUtility.add("/api/"+n+"/realChart",_urlLoad)
		scadaUtility.add("/api/"+n+"/realChart/interval",_urlManage)
	
if __name__ == '__main__':
	utility.run_tests() 
	


	
	
	
	
	
	
	
	
	
	
	
	