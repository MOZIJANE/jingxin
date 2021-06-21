#coding=utf-8
# ycat			2020-04-10	  create
# ftp客户端  
import os,sys
import ftplib
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import datetime
import utility
import log
#https://blog.csdn.net/cl965081198/article/details/82803333
#https://www.cnblogs.com/huzixia/p/10389945.html

def upload(ip,port,user,password,localPath,remotePath=None,showProgressBar=False):
	import enhance
	c = client()
	c.open(ip,port)
	if not user:
		user = "anonymous"
		password = ""
	c.login(user,password)
	if not showProgressBar:
		c.upload(localPath=localPath,remotePath=remotePath)
		return True

	import ui.msgBox
	s = ui.msgBox.progressBar()
	s.title = localPath 		#窗口标题
	s.label = "上传进度"		#进度条标题

	def onclose(*params):
		c.close()
		if os.path.exists(localPath):
			os.remove(localPath)

	if not remotePath:
		remotePath = os.path.basename(localPath)
	f = enhance.bind(c.upload,localPath=localPath,remotePath=remotePath,callback=s.update)
	if s.start(f,cancelFunc=onclose):
		log.info("finish upload:",localPath)
		c.close()
		return True
	else:
		log.warning("user cancel upload:",localPath)
		return False


def download(ip,port,user,password,remotePath,localPath=None,showProgressBar=False):
	import enhance
	c = client()
	c.open(ip,port)
	if not user:
		user = "anonymous"
		password = ""
	c.login(user,password)
	if not showProgressBar:
		c.download(remotePath=remotePath,localPath=localPath)
		return True

	import ui.msgBox
	s = ui.msgBox.progressBar()
	s.title = remotePath 		#窗口标题
	s.label = "下载进度"		#进度条标题

	def onclose(*params): 
		c.close()
		if os.path.exists(localPath):
			os.remove(localPath)

	if not localPath:
		localPath = "./"+os.path.basename(remotePath)
	f = enhance.bind(c.download,remotePath=remotePath,localPath=localPath,callback=s.update)
	if s.start(f,cancelFunc=onclose):
		log.info("finish download:",remotePath)
		c.close()
		return True
	else:
		log.warning("user cancel download:",remotePath)
		return False

class client:
	def __init__(self,debug=False,passive=False):
		self.ftp = ftplib.FTP()
		self.ftp.set_pasv(passive)
		self.ftp.encoding = "utf-8"
		self.setDebug(debug)
		self.fp=None

	def setDebug(self,debug):
		#0: no debugging output (default)
		#1: print commands and responses but not body text etc.
		#2: also print raw lines read and sent before stripping CR/LF
		if debug:
			self.ftp.set_debuglevel(2)
		else:
			self.ftp.set_debuglevel(0)


	def open(self,ip,port=21):
		try:
			return self.ftp.connect(ip,port)
		except Exception as e:
			log.error("ftp open failed",ip,":",port)
			raise

	def login(self,user="anonymous",password=""):
		e = None
		try:
			return self.ftp.login(user,password)
		except ftplib.error_perm as e1:
			e = e1
		raise Exception("ftp.login `%s` failed: "%user+str(e))

	def welcome(self):
		return self.ftp.getwelcome()

	@staticmethod
	def _decodeLine(line):
		r = {}
		#"-rwxr-xr-x    1 1000     1000          108 Dec 19 11:04 ycat.sh"
		#-rw-r--r--    1 1001     1000     39779641 Jan 10  2018 GoogleChrome_XP_49.0.2623.112_PortableSoft.7z
		#drwxr-xr-x    4 0        0            4096 Jan 10  2018 GoogleChromePortable
		#['-rw-r--r--', '1', '1001', '1000', '39779641', 'Jan', '10', '2018', 'GoogleChrome']
		ss = line.split()
		if line[0] == "d":
			r["isDir"] = True
			r["size"] = 0
		else:
			r["isDir"] = False
			r["size"] = int(ss[4])
		r["name"] = ss[-1]
		#第7部分，有时候为年,有时候为小时分钟，区别是在于文件的修改时间与 服务器的当前时间  比较，  如果在1年之内，则显示 （时：分），超过1年， 显示年
		if ss[7].find(":") == -1:
			r["datetime"] = datetime.datetime.strptime(ss[5]+"-"+ss[6]+"-"+ss[7],"%b-%d-%Y")
		else:
			n = datetime.datetime.now()
			t1 = datetime.datetime.strptime(ss[5]+"-"+ss[6]+"-"+str(n.year-1)+" "+ss[7],"%b-%d-%Y %H:%M")
			t2 = datetime.datetime.strptime(ss[5]+"-"+ss[6]+"-"+str(n.year)+" "+ss[7],"%b-%d-%Y %H:%M")
			if t2 > n:
				r["datetime"] = t1 + datetime.timedelta(hours=8)
			else:
				r["datetime"] = t2 + datetime.timedelta(hours=8)

		r["owner"] = ss[2]
		r["attribute"] = ss[0]
		return r

	#返回[{"name":"","isDir":True|False,"size":0,"datetime":datetime}...]列表
	#path=""表示当前目录
	def getFiles(self,path=""):
		def _readDir(codec):
			ret = []
			def read(line):
				ret.append(client._decodeLine(line))
			self.ftp.encoding = codec
			if path:
				self.ftp.dir(path,read)
			else:
				self.ftp.dir(read)
			return ret
		try:
			return _readDir("utf-8")
		except UnicodeDecodeError as e:
			pass
		ret = _readDir("gbk")
		self.ftp.encoding = "utf-8"
		return ret

	def exists(self,path):
		try:
			return len(self.ftp.nlst(path)) >= 0
		except ftplib.error_perm as e:
			return False

	#返回所有文件名,type=0(目录和文件),type=1(目录),type=2(文件)
	def dir(self,path="",type=0):
		ff = self.getFiles(path)
		if type == 0:
			return [f["name"] for f in ff]
		if type == 1:
			return [f["name"] for f in ff if f["isDir"]]
		if type == 2:
			return [f["name"] for f in ff if not f["isDir"]]

	#TODO:查看文件树
	def tree(self,showFunc=print):
		pass

	def mkdir(self,path):
		e = None
		try:
			return self.ftp.mkd(path)
		except ftplib.error_perm as e1:
			e = e1
		raise Exception("ftp.mkdir `%s` failed: "%path+str(e))

	def remove(self,path,force=False):
		pp =self.getFiles(path)
		if not pp:
			return
		if len(pp)==1 and not pp[0]["isDir"]:
			return self.ftp.delete(path)
		if force:
			#pp = self.getFiles(path)
			for p in pp:
				p1 = path+"/"+p["name"]
				if not p["isDir"]:
					self.ftp.delete(p1)
				else:
					self.remove(p1,force=True)
		self.ftp.rmd(path)

	def rename(self,oldName,newName):
		return self.ftp.rename(oldName,newName)

	def setCurDir(self,path):
		self.ftp.cwd(path)

	def getCurDir(self):
		return self.ftp.pwd()

	def fileSize(self,file):
		try:
			p = self.getFiles(file)
			if len(p) == 1 and not p[0]["isDir"]:
				return p[0]["size"]
			return 0	#is dir
		except ftplib.error_perm:
			return None

	#callback(count,total)
	def download(self,remotePath,localPath=None,callback=None):
		if not localPath:
			localPath = "./"+os.path.basename(remotePath)
		total = self.fileSize(remotePath)
		if total is None:
			raise IOError("remote file not existed: "+remotePath)

		self.fp = open(localPath, 'wb')
		cb = None
		if callback:
			d = {}
			d["count"] = 0
			def  download_file_cb(b):
				if self.fp is not None:
					self.fp.write(b)
					d["count"] = d["count"] + len(b)
					callback(d["count"],total)
			cb = download_file_cb
		else:
			cb = self.fp.write
		e = None
		try:
			self.ftp.retrbinary('RETR ' + remotePath,callback = cb)
			if callback:
				callback(total,total)
		except ftplib.error_perm as e1:
			e = e1
		finally:
			if self.fp:
				self.fp.close()
				self.fp=None
		if e:
			raise Exception("ftp.download `%s` failed: "%remotePath+str(e))


	#callback(count,total)
	def upload(self,localPath,remotePath=None,callback=None):
		if not os.path.exists(localPath):
			raise IOError("file not existed: "+localPath)
		cb = None
		total = os.path.getsize(localPath)
		if callback:
			d = {}
			d["count"] = 0
			def  upload_file_cb(b):
				d["count"] = d["count"] + len(b)
				callback(d["count"],total)
			cb = upload_file_cb
		self.fp = open(localPath, 'rb')
		if not remotePath:
			remotePath = os.path.basename(localPath)
		self.ftp.storbinary('STOR ' + remotePath, self.fp, callback = cb)
		if callback:
			callback(total,total)
		if self.fp:
			self.fp.close()
			self.fp = None

	def close(self):
		if self.fp:
			self.fp.close()
			self.fp = None
		#self.ftp.quit()
		self.ftp.close()


############# unit test #############
def test_decodeLine():
	s = "-rw-r--r--    1 1001     1000     39779641 Jan 10  2018 GoogleChrome_XP_49.0.2623.112_PortableSoft.7z"
	f = client._decodeLine(s)
	assert f == {'isDir': False, 'size': 39779641, 'name': 'GoogleChrome_XP_49.0.2623.112_PortableSoft.7z', 'datetime': datetime.datetime(2018, 1, 10, 0, 0), 'owner': '1001', 'attribute': '-rw-r--r--'}
	s = "drwxr-xr-x    4 0        0            4096 Jan 10  2018 GoogleChromePortable"
	f = client._decodeLine(s)
	assert f == {'isDir': True, 'size': 0, 'name': 'GoogleChromePortable', 'datetime': datetime.datetime(2018, 1, 10, 0, 0), 'owner': '0', 'attribute': 'drwxr-xr-x'}
	s = "-rwxr-xr-x    1 1000     1000          108 Dec 19 11:04 ycat.sh"
	f = client._decodeLine(s)
	assert f == {'isDir': False, 'size': 108, 'name': 'ycat.sh', 'datetime': datetime.datetime(2019, 12, 19, 11, 4), 'owner': '1000', 'attribute': '-rwxr-xr-x'}

def test1():
	ip = "10.30.80.4"
	f = client(debug=False)
	f.open(ip)
	f.login("znzz","123456")
	print(f.welcome())
	f.setCurDir("/")
	assert "/" == f.getCurDir()

	a = f.dir(type=1)
	print(a)
	a = f.dir(path="/home/znzz/ycat/",type=0)
	print(a)
	print(f.fileSize("/home/znzz/t.py"))
	f.download("/home/znzz/t.py")
	#f.mkdir("ycat")
	#assert "ycat" in f.dir()


def test2():
	import ftpServer,threading
	s = ftpServer.server()
	s.setWelcome("ycat hello world")
	s.addUser("admin","123456","./test",readonly=False)

	t = threading.Thread(target=s.run)
	t.start()

	f = client(debug=False)
	f.open("127.0.0.1")
	f.login("admin","123456")
	assert "ycat hello world" in f.welcome()
	assert "test_config1.cfg" in f.dir("/")
	#f.setDebug(True)
	try:
		f.remove("/test1",force=True)
	except Exception as e:
		print(e)
	assert not f.exists("/test1")
	print(f.dir("/"))
	f.mkdir("/test1")

	def cb(b,t):
		print("%0.1f%%"%(b/t*100.))

	f.upload("./ftp.py","/test1/",cb)
	f.download("/test1/ftp.py","./test/tttt.py",cb)
	print(f.fileSize("./test1/ftp.py"))
	f.rename("/test1/ftp.py","/test1/ftp22.py")
	f.remove("/test1/ftp22.py")
	f.mkdir("/test1/ycat2")
	f.remove("/test1",force=True)
	s.close()
	t.join()

def ttt():
	import ftp
	ip = "192.168.252.186"
	f = ftp.client(debug=True)
	f.open(ip,2121)
	f.login("sound","123456")
	print(f.dir())
	f.upload("./__init__.py")
	f.close()

def testqt():
	from PyQt5.QtWidgets import QApplication
	app = QApplication(sys.argv)
	upload(ip="127.0.0.1",port=21,user="",password="",localPath=r"aaa.mp4",remotePath="",showProgressBar=True)
	download(ip="127.0.0.1",port=21,user="",password="",remotePath="aaa.mp4",localPath=r"",showProgressBar=True)
	sys.exit(app.exec_())

if __name__ == '__main__':
	ttt()
	assert 0


	test_decodeLine()
	test2()
	print("======== finish")
	import time
	time.sleep(10)









