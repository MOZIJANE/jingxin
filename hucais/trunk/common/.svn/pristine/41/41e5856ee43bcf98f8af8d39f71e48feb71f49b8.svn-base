#coding=utf-8 
# ycat			2016-12-2      create
import os,sys
import console
import utility
import log
import os,sys
import console
import termios	#linux only 

GREEN = "green"
RED = "red"
YELLOW = "yellow"
DEFAULT = "default"

def getchar():
	fd=sys.stdin.fileno()
	if os.isatty(fd):
		old=termios.tcgetattr(fd)
		new=termios.tcgetattr(fd)
		new[3]=new[3]& ~termios.ICANON& ~termios.ECHO
		new[6][termios.VMIN]=1
		new[6][termios.VTIME]=0
	
		try:
			termios.tcsetattr(fd,termios.TCSANOW,new)
			termios.tcsendbreak(fd,0)
			ch=os.read(fd,7)
		finally:
			termios.tcsetattr(fd,termios.TCSAFLUSH,old)
	else:
		ch=os.read(fd,7)	
	return ch

def input_char(msg,default=None,color=DEFAULT):
	console.show(msg,color,add_line=False)
	#sys.stdout.flush()
	t = getchar().decode("utf-8")
	if default is not None:
		if t == "\n":
			t = default
	console.show(t+"\n",color,add_line=False)
	#sys.stdout.flush()
	return str(t)

#发现未完成的安装，do you want to continue ? 
def input_bool(msg,default=None,color=DEFAULT):
	c = input_char(msg,default,color)
	if c == "y" or c =="Y":
		return True
	elif c == "n" or c =="N":
		return False
	else:
		assert 0

def input_int(msg,default=None,color=DEFAULT):
	return int(input_char(msg,default,color))

def input(msg,default=None,color=DEFAULT):
	console.show(msg,color,add_line=False)
	r = raw_input()
	if len(r) == 0:
		if default is not None:
			r = default
	return r

_g_items = {}

# 修饰符，用于给函数添加菜单 
def menu_item(menu_id,menu_name,menu_key,parent_menu_id = 0):
	def __call(func):
		add_menu_item(func,menu_id,menu_name,menu_key,parent_menu_id)
		return func
	return __call


def add_menu_item(func,menu_id,menu_name,menu_key,parent_menu_id = 0): 
	assert len(menu_key) == 1
	assert menu_id != 0
	global _g_items
	
	#assert menu_key not in _g_items
	
	c = utility.empty_class()
	c.func = func
	c.menu_id = menu_id
	c.menu_name = menu_name
	c.menu_key = menu_key.lower()
	c.parent = parent_menu_id
	c.sub_item = []
	
	assert c.menu_id not in _g_items
	_g_items[c.menu_id] = c
	
	
def show_menu(menu_id = 0, loop = False):
	def _find_menus_by_parent_id(menu_id):
		global _g_items
		ret = []
		for m in _g_items:
			item = _g_items[m]
			if item.parent == menu_id:
				ret.append(item)
		ret.sort(key=lambda x:x.menu_id)
		return ret
	
	menus = _find_menus_by_parent_id(menu_id)
	if len(menus) == 0:
		return
	for m in menus:
		show(m.menu_key+": "+m.menu_name)
	show("q"+": "+"Quit")					
	menu_id2 = 0	
	while True:	
		c = input_char("Select menu: ",color="yellow").lower()
		if c == "q":
			console.show("bye")
			sys.exit(0)
		find = False
		for m in menus:
			if m.menu_key == c:
				if m.func:
					m.func()
				console.show("")
				menu_id2 = m.menu_id
				find = True 
				break
		if find:
			break
		
	if menu_id2 != 0:
		show_menu(menu_id2)
	elif loop:
		show_menu(menu_id)
		

g_stdout = None
g_handle = None


def set_stdout(filename="stdout.log"):
	print("set std output to file: ",filename)
	global g_stdout,g_handle
	if not g_stdout:
		g_stdout=sys.stdout
		if not g_handle:
			g_handle=open(filename, "w+")
		sys.stdout = g_handle

def restore_stdout():
	global g_stdout
	if g_stdout is not None:
		sys.stdout = g_stdout
	
class bar:
	def __init__(self, title ,total):
		log.info("start "+title) 
		global g_stdout
		self.out = g_stdout
		if self.out is None:
			self.out = sys.stdout
		self.count = 0
		self.total = total
		self.width = 60
		self.title = title
		self._show()
		self.result = True
		

	def step(self):
		if not self.result:
			return
		self.count += 1
		self._show()
	
	def failed(self,msg):
		self.result = False		
		self.out.write(' ' * 100 + '\r')
		self.out.flush()
		self.out.write("\033[01;33m"+ self.title.ljust(30)+"\033[0m")
		
		self.out.write(" "*self.width+"            \033[22;31m[ FAILED ]\033[0m   ")
		self.out.write(msg)
		self.out.write('\r\n')
		log.info("finish failed "+self.title + ", " + msg)
		self.out.flush()
		
	def _show(self): 
		self.out.write(' ' * 100 + '\r')
		self.out.flush() 
		self.out.write("\033[01;33m"+ self.title.ljust(30)+"\033[0m")
		console = round(self.width * self.count / self.total)
		if console == self.width:
			self.out.write(" "*self.width+"            \033[22;32m[   OK   ]\033[0m")
			self.out.write('\r\n')
			log.info("finish "+self.title)
		else:
			self.out.write('step{0:2}/{1:2}: '.format(self.count, self.total))
			self.out.write('#' * console + '-' * (self.width - console))
			self.out.write('\r')
		self.out.flush() 


def show(msg,color="",add_line=True):
	msg = str(msg)
	global g_stdout
	if color  == "red":
		msg = "\033[31m" + str(msg) + "\033[0m"
	elif color == "yellow":  
		msg = "\033[01;33m" + str(msg) + "\033[0m"
	elif color == "green":
		msg = "\033[32m" + str(msg) + "\033[0m"	
		
	s = g_stdout
	if s is None:
		s = sys.stdout
	s.write(msg)
	if add_line:
		s.write("\n")
	s.flush()


#################### unit test #####################

def test_menu():
	@menu_item(1,"function a","a")
	def funca():
		show("run in funca")

	@menu_item(2,"function b","b")
	def funcb():
		show("run in funcb")

	@menu_item(3,"function c","c")
	def funcb():
		show("run in funcd")
	
	show_menu()


def test():
	import time
	b = bar("dfdftest",total = 5)
	for i in range(5):
		b.step()
		time.sleep(0.2)
	b = bar("teddddddst",total = 5)
	for i in range(5):
		b.step()
		time.sleep(0.2)
	restore_stdout()
	
	b = bar("teddddd333dst",total = 5)
	for i in range(5):
		b.step()
		if i == 3:
			b.failed("fdafsdf fa")
		time.sleep(0.2)	
	restore_stdout()


if __name__ == '__main__':   
	test()
	show("test","red")
	show("test","yellow")
	show("test","green")
	show("test","default")
	test_menu()
	t = input_char("lalala:")
	t2 = input_char("lalala(enter:default Y):",default="Y")
	
#if __name__ == '__main__':	
#	utility.run_tests()	
