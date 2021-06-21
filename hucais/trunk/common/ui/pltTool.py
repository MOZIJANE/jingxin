#coding=utf-8 
# ycat			 2020/04/10	  create
# 设置工具栏
#https://matplotlib.org/gallery/user_interfaces/toolmanager_sgskip.html#sphx-glr-gallery-user-interfaces-toolmanager-sgskip-py
#https://matplotlib.org/api/backend_tools_api.html#matplotlib.backend_tools.ToolToggleBase

#https://matplotlib.org/stable/gallery/user_interfaces/toolmanager_sgskip.html
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
	

def tools():
	if not hasattr(plt.gcf().canvas,"manager"):
		return {}
	if plt.gcf().canvas.manager is None:
		return {}
	return plt.gcf().canvas.manager.toolmanager.tools
	
#按下默认按钮 
def onclick(key,trigger):
	tt = tools()
	if key not in tt:
		return None
	h = tt[key]
	old = h.trigger
	h.trigger = trigger
	return old
	
def activeTools():
	ret = []
	if not hasattr(plt.gcf().canvas,"manager"):
		return ret
	if plt.gcf().canvas.manager is None:
		return ret
	for group, active in plt.gcf().canvas.manager.toolmanager.active_toggle.items():
		if not active:
			continue
		if isinstance(active,str):
			ret.append(active)
		else:
			for a in active:
				ret.append(a)
	return ret
	
########## unit test ##########
def test():
	print(tools()) 
	def click(*param):
		print(activeTools())
	def click2(v,*param):
		print(v,"hello")	
		
	createButton("test",click)
	createCheckButton("test22",click2)
	remove("help")
	plt.plot(0,0,"r+")
	
	onclick("home",click)
	plt.show()
	
	
	
if __name__ == '__main__':  
	test()
	
	



