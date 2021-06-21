#coding=utf-8
# ycat		2017-08-27	  create
# 命令控制  
import sys,os
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import enhance,log
import enum
from driver.handstick import stickKeyCfg
g_commands = {"clicked":{},"pressDown":{},"pressUp":{}}	
g_commandName = stickKeyCfg.getCommandName()

def connect(type,name,func):
	global g_commandName,g_types
	if name != "all":
		assert name in g_commandName
	assert type in g_commands
	#log.debug("注册按键"+ name + " " + type) 
	if name not in g_commands[type]:
		g_commands[type][name] = enhance.event()
	g_commands[type][name].connect(func)

def emit(type,name):
	global g_commandName,g_types
	if name not in g_commandName:
		return
	if type not in g_commands:
		return
	if name not in g_commands[type]:
		return
	else:
		log.info("触发按键"+name + " " + type)
		g_commands[type][name].emit()
		if "all" in g_commands[type]:
			g_commands[type]["all"].emit()
	
def register(type,name):
	def __call(func):
		connect(type,name,func)
		return func
	return __call			
	
if __name__ == '__main__':
	pass
