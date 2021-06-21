#coding=utf-8 
# ycat			2016-12-15      create
import sys,os,datetime 
import subprocess 
import utility  
import pexpect
import pexpect.pxssh
import console

def login(hostname,user,password,timeout=120):
	s = pexpect.pxssh.pxssh()
	s.logfile_read = console.g_handle
	s.logfile_send = console.g_handle 
	s.login (hostname, user, password,login_timeout=timeout)
	s.prompt()
	utility.logger().info(s.name + ": login "+hostname + " succeed")
	return s

def logout(ssh):
	ssh.logout()

#调用login的返回结果  
def run_cmd(ssh,cmd,timeout=120):
	ssh.sendline(cmd)  
	ssh.prompt(timeout=timeout)
	utility.logger().info(ssh.name + ": #"+cmd)
	#utility.logger().info(ssh.before)
	return ssh.before

#scp将本地文件拷贝到远端	
def scp(ip, user, passwd, localfile, remotefile):  
	passwd_key = '.*assword.*'
	#带上StrictHostKeyChecking=no 表示不管是否是第一次建立连接，一定会是直接输入password
	if os.path.isdir(localfile):   
		cmdline = 'scp -o StrictHostKeyChecking=no -r %s %s@%s:%s' % (localfile, user, ip, remotefile)   
	else:   
		cmdline = 'scp -o StrictHostKeyChecking=no %s %s@%s:%s' % (localfile, user, ip, remotefile)   
	try:  
		child = pexpect.spawn(cmdline)
		child.expect(passwd_key)  
		child.sendline(passwd)  
		child.expect(pexpect.EOF)  
		#child.interact()  
		#child.read()  
		#child.expect('$')
		utility.logger().info("scp file " + localfile + " to " + ip +"@"+remotefile)
		utility.logger().info(child.before)
	except:  
		utility.logger().error("Error: scp file " + localfile + " to " + ip +"@"+remotefile)
		utility.logger().info(child.before)
		#raise #屏蔽避免在已经建立了root免认证下拷贝出错情况

#scp_from将远端文件拷贝到本地		
def scp_from(ip, user, passwd, remotefile, localfile):  
	passwd_key = '.*assword.*'
	#带上StrictHostKeyChecking=no 表示不管是否是第一次建立连接，一定会是直接输入password;目录下所有文件拷贝到localfile
	cmdline = 'scp -o StrictHostKeyChecking=no %s@%s:%s/* %s' % (user, ip, remotefile, localfile)   
	try:  
		child = pexpect.spawn(cmdline)
		child.expect(passwd_key)  
		child.sendline(passwd)  
		child.expect(pexpect.EOF)  
		#child.interact()  
		#child.read()  
		#child.expect('$')
		utility.logger().info("scp file " + localfile + " from " + ip +"@"+remotefile)
		utility.logger().info(child.before)
	except:  
		utility.logger().error("Error: scp file " + localfile + " from " + ip +"@"+remotefile)
		utility.logger().info(child.before)
		#raise #屏蔽避免在已经建立了root免认证下拷贝出错情况

def read_file(ssh,filename):
	return run_cmd(ssh,"cat "+filename)

def write_file(ssh,content,filename):
	run_cmd(ssh,'echo "'+content+'" > '+filename)
	
def reboot(ssh):
	utility.logger().error(ssh.name + ": start reboot ")
	run_cmd(ssh,"reboot")
	

