#coding=utf-8 
# ycat			 2020/04/10	  create
# 设置工具栏
#https://matplotlib.org/gallery/user_interfaces/toolmanager_sgskip.html#sphx-glr-gallery-user-interfaces-toolmanager-sgskip-py
#https://matplotlib.org/api/backend_tools_api.html#matplotlib.backend_tools.ToolToggleBase
import sys,os
import matplotlib.pyplot as plt
plt.rcParams['toolbar'] = 'toolmanager'
from matplotlib.backend_tools import ToolBase, ToolToggleBase
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)

#onclick定义: def click(*param)
#可以配置几个属性
#	c.image = 'zoom_to_rect'
#	c.cursor = 2
#	c.default_keymap = ['f', 'ctrl+f']
#	c.description = "" 
#
#cursor定义：
#	HAND = 0
#	MOVE = 3
#	POINTER = 1
#	SELECT_REGION = 2
#	WAIT = 4
def createButton(name,onclick):
	c = ToolBase
	c.trigger = onclick
	plt.gcf().canvas.manager.toolmanager.add_tool(name,c)
	#第一个group="navigation"
	plt.gcf().canvas.manager.toolbar.add_tool(name,group="new")
	return c

#onclick定义: def click(enable,*param)
def createCheckButton(name,onclick,defaultCheck=False):
	def enable(*param,**params):
		onclick(True,*param,**params)
	def disable(*param,**params):
		onclick(False,*param,**params)
	c = ToolToggleBase
	c.enable = enable
	c.disable = disable
	c.default_toggled = defaultCheck
	plt.gcf().canvas.manager.toolmanager.add_tool(name,c)
	plt.gcf().canvas.manager.toolbar.add_tool(name,group="new")
	return c
 
def remove(name):
	plt.gcf().canvas.manager.toolmanager.remove_tool(name)
	
	
########## unit test ##########
def test():
	def click(*param):
		print("hello")
	def click2(v,*param):
		print(v,"hello")	
		
	createButton("test",click)
	createCheckButton("test22",click2)
	remove("help")
	plt.plot(0,0,"r+")
	plt.show()
	
	
	
if __name__ == '__main__':  
	test()
	
	



