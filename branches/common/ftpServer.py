#coding=utf-8
# ycat			2020-04-10	  create
# ftp服务端  
import os,sys
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import datetime
import utility
import log
#https://pyftpdlib.readthedocs.io/en/latest/
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

if utility.is_win():
	g_encode = "gbk"
else:
	g_encode = "utf-8"

class server:
	def __init__(self,port=21):
		def decodeFunc(a, bytes):
			encoding = g_encode
			return bytes.decode(encoding, a.unicode_errors)
		self.ftpServer = None
		a = DummyAuthorizer()
		self.handler = FTPHandler
		self.handler.decode = decodeFunc
		self.handler.authorizer = a
		if not utility.is_win():
			from pyftpdlib.filesystems import UnixFilesystem
			self.handler.abstracted_fs = UnixFilesystem
		self.handler.banner = ""
		
	def setWelcome(self,text):
		self.handler.banner = text

	def addAnonymous(self,path,readonly=True):
		if readonly:
			p = "elr"
		else:
			p = "elradfmwMT"
		self.handler.authorizer.add_anonymous(path,perm=p)
		
	def addUser(self,user,password,path,readonly=True):
		if readonly:
			p = "elr"
		else:
			p = "elradfmwMT"
		#    Read permissions:
		#        "e" = change directory (CWD, CDUP commands)
		#        "l" = list files (LIST, NLST, STAT, MLSD, MLST, SIZE commands)
		#        "r" = retrieve file from the server (RETR command)
		#    Write permissions:
		#        "a" = append data to an existing file (APPE command)
		#        "d" = delete file or directory (DELE, RMD commands)
		#        "f" = rename file or directory (RNFR, RNTO commands)
		#        "m" = create directory (MKD command)
		#        "w" = store a file to the server (STOR, STOU commands)
		#        "M" = change file mode / permission (SITE CHMOD command) New in 0.7.0
		#        "T" = change file modification time (SITE MFMT command) New in 1.5.3
		self.handler.authorizer.add_user(user,password,path,perm=p)

		
	def run(self,port=21):
		self.ftpServer = FTPServer(('0.0.0.0', port), self.handler)          
		self.ftpServer.serve_forever()
		
	def close(self):
		if self.ftpServer:
			self.ftpServer.close_all()


##测试使用 通过
if __name__ == '__main__':
	s = server()
	s.setWelcome("welcome to ycat ftp")
	s.addAnonymous("d:/",readonly=False)
	s.addUser("admin","123456","d:/",readonly=False)
	s.run()
