#coding=utf-8
# ycat			2017-07-27	  create
# 日志接口
import sys,os
import logging
import traceback
import logging.config
import time

g_log = None
g_app_name = ""

def app_name():
	global g_app_name
	if g_app_name == "":
		def _get_app_name():
			#从上一级目录取进程信息
			p = os.path.split(os.path.dirname(os.getcwd()+"/"))
			return p[-1]
		g_app_name = _get_app_name()
	return g_app_name

class _console_format(logging.Formatter):
	format_str = "[%(levelname)s]%(asctime)s: %(message)s"
	def __init__(self):
		super(_console_format,self).__init__(_console_format.format_str)
	
	def format(self,record):
		r = super(_console_format,self).format(record)
		if sys.platform == "win32":
			return r
		if record.levelno == 50:
			c = "\033[31;47m"	
		elif record.levelno == 20:
			c = "\033[36m"
		elif record.levelno == 30:
			c = "\033[33m"
		elif record.levelno == 40:
			c = "\033[31m"
		else:
			c = "\033[37m"
		return c + r + "\033[0m"

def copy_old_log(path,oldpath,name):
	myId = os.getpgid(0)
	for file in os.listdir(path):
		i = file.find(name+"_p")
		if i == -1:
			continue 
		i2 = file.find(".log")
		if i2 == -1:
			continue
		pid = file[len(name+"_p"):i2]
		if not str.isdigit(pid):
			continue
		try:
			if os.getpgid(int(pid)) == myId:
				continue
		except:
			pass 
		cmd = "mv -f %s/%s %s/ 2> /dev/null"%(path,file,oldpath)
		os.system(cmd)
		
def _init_logger():
	import ConfigParser
	global g_log
	if g_log:
		return g_log
	name = app_name()
	g_log = logging.getLogger(name)
	fileName = './default.ini'
	if not os.path.exists(fileName):
		print('can not find default.ini file!')
		exit(1)
	config = ConfigParser.ConfigParser()
	config.read(fileName)
	set_level(int(config.get("logger","level")))
		
	if (not sys.platform == "win32"):
		p = config.get("logger","logger_path")
		try:
			if is_python3():
				os.makedirs(p,exist_ok=True)
			else:
				os.makedirs(p)
		except OSError as e:
			if str(e).find("File exists") == -1:
				print("log.py:",e)
		
		#把日志移到old文件夹中 
		oldpath = os.path.join(p,"oldLog")
		
		try:
			if is_python3():
				os.makedirs(oldpath,exist_ok=True)
			else:
				os.makedirs(oldpath)
		except OSError as e:
			if str(e).find("File exists") == -1:
				print("log.py",e)
		
		copy_old_log(p,oldpath,name)
		
		#删除old文件夹的旧日志
		cmd = "find %s/*.log -mtime +30 -type f -exec rm -Rf {} \\; 2> /dev/null"%oldpath
		#print(cmd)
		os.system(cmd)
			
		name = name + "_p" + str(os.getpid()) + ".log"
	
		timelog = logging.handlers.TimedRotatingFileHandler(os.path.join(p,name),when='MIDNIGHT',interval=1,backupCount=30)
		timelog.suffix = "%Y%m%d.log" 
		timelog.formatter = logging.Formatter(_console_format.format_str)
		g_log.addHandler(timelog)
		write_console = bool(config.get("logger","enable_console"))
	else:
		write_console = True
		
	if write_console:
		if sys.platform == "win32":
			if not os.path.exists("./log"):
				os.mkdir("./log")
			timelog = logging.handlers.TimedRotatingFileHandler("./log/%s.log" %(app_name()),when='MIDNIGHT',interval=1,backupCount=30)
			timelog.suffix = "%Y%m%d.log" 
			timelog.formatter = logging.Formatter(_console_format.format_str)
			g_log.addHandler(timelog)
		
			#import winConsole
			#h = winConsole.winLoggerHander()	 
		else:
			h = logging.StreamHandler(sys.stdout)
			h.formatter = _console_format()
		#g_log.addHandler(h)
	
	def _write_exception_log(title,exception_obj):
		s = title + " cause a error: " + str(exception_obj) + "\n"
		try:
			s += traceback.format_exc()
		except Exception as e:
			pass
		g_log.critical(s)	
	g_log.exception = _write_exception_log
	return g_log
 
def logger():
	if g_log:
		return g_log
	return _init_logger()

def disable_log():
	#TODO: ycat 未完成 
	global g_log 
	g_log = logging.getLogger("empty")
	
def enable_log():
	#TODO: ycat 未完成 
	set_level(-1)

##CRITICAL=50,ERROR=40,WARNING=30,INFO=20,DEBUG=10,NOTSET=-1 	
def set_level(levelno):
	global g_log
	g_log.level = levelno	
	
def _makeMsg(*param):	 
	msg = ""
	for p in param:
		msg += str(p) + " " 
	return msg.rstrip()
	
def debug(*param):	
	logger().debug(_makeMsg(*param))

def info(*param):	
	logger().info(_makeMsg(*param))
	
def warning(*param):	
	logger().warning(_makeMsg(*param))

def error(*param):	
	logger().error(_makeMsg(*param))	

def critical(*param):	
	logger().critical(_makeMsg(*param))		
	
def critical(*param):	
	logger().critical(_makeMsg(*param))	
	
def showTrace(func=debug):
	func(getTrace())
	
def exception(*param,**params):
	return logger().exception(*param,**params)
	
def getTrace():
	import inspect
	r = "Show Trace :\n"
	s = inspect.stack()[1:]
	for i,ss in enumerate(s): 
		r += '[%02d] File "%s", line %d, in %s \n'%(i+1,ss[1],ss[2],ss[3])
	return r

def is_python3():
	return sys.version[0] == '3'

##################### Unit Test #############################	
def test_logger(): 
	showTrace()
	debug("this is a test log ",1,"sss3") 
	for i in range(10):
		debug("this is a test log ",1+i,"sss3")
		info("this is a test log ",1+i,"sss2")
		warning("this is a test log ",1+i,"sss4")
		error("this is a test log ",1+i,"sss1")
	try:
		
		assert 0
	except Exception as e:
		exception("this is a test log",e)
		
	
def test_disable_log():
	#set_is_test(False)
	enable_log()
	error("test is a test")
	disable_log()
	error("test is a test2, you dont see!!!!")
	enable_log()
	error("test is a test3, you should see")
	#set_is_test(True) 	
	
if __name__ == '__main__':
	test_logger()
	test_disable_log()
