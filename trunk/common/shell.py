#coding=utf-8 
# ycat			2016-9-29      create
import sys,os,datetime,random 
import subprocess 
import utility
import re
import config
import pexpect
import key
import socket
from io import StringIO
import log

def run_cmd(cmd,showLog=True):
	import console
	if showLog:
		log.debug("# "+cmd)
	child = pexpect.spawn(cmd)
	if not utility.is_win():
		child.logfile_read = console.g_handle 
	child.expect(pexpect.EOF,timeout=None)	 

class _strIO(StringIO):
	def __init__(self,*param):
		StringIO.__init__(self,*param)
	
	def write(self,data):
		if isinstance(data,bytes):
			data = data.decode(encoding="utf-8")
		return StringIO.write(self,data)
	
	
def run_cmd2(cmd,timeout=-1,logFlag=False):
	if logFlag:
		log.debug("# "+cmd)
	child = pexpect.spawn(cmd)
	ret = _strIO()
	child.logfile_read = ret
	i = child.expect([pexpect.EOF,pexpect.TIMEOUT],timeout=timeout)
	ret.seek(0)
	r = ret.read()
	if i == 1:
			return (r,False)
	return (r,True)
	

def sudo(cmd):
	if "PASS" in os.environ:
		os.system("echo $PASS > /tmp/pass;sudo -i -S < /tmp/pass "+cmd)
	else:
		os.system("sudo "+cmd)

def run_cmd_ui(cmd,title=""):
	cmd2 = 'gnome-terminal --tab'
	if title:
		cmd2 += ' -t %s -- '%title 
	cmd2 += cmd
	os.system(cmd2)

	
def backup_file(file):
	if not os.path.exists(file):
		return None
	f = os.path.basename(file)
	f = f+"."+datetime.datetime.strftime(datetime.datetime.now(),'%Y%m%d_%H%M%S')+"."+"bak"
	p = os.path.dirname(file)
	newfile = p+os.path.sep+f
	f1 = open(newfile, "w+b")
	f2 = open(file, "rb")
	f1.write(f2.read())
	f1.close()
	f2.close()
	log.info("backup file " + file + " to " + newfile)
	return newfile

#rpm_name可以为字符串或字符串列表
def yum_install(rpm_name):
	def install_one(rpm): 
		run_cmd("yum -y install "+rpm)
		#´Ë´¦Ä¬ÈÏÎªpython2£¬·ñÔòÔÚÒÑ¾­°²×°Ç°ÌáÏÂ°²×°°üÌáÊ¾ÕÒ²»µ½£¨ºóÐøÈôÓÐ¸ü¶à todo£©
		if rpm == 'python-aodhclient':
			rpm = 'python2-aodhclient'
		elif rpm == 'python-ceilometerclient':
			rpm = 'python2-ceilometerclient'
		elif rpm == 'python-pecan':
			rpm = 'python2-pecan'
		rr = utility.run_cmd("rpm -q "+rpm)
		run_cmd("yum -y update "+rpm)
		if rr[0].find("not installed") != -1:
			log.error("yum install failed, can't find rpm " + rpm + " ," + rr[0])
			raise Exception("yum install failed, can't find rpm " + rpm + " ," + rr[0])
			#return False
		return True
		
	if isinstance(rpm_name,str):
		return install_one(rpm_name)
	else:
		rr = True
		for r in rpm_name:
			rr &= install_one(r)
		return rr
	
#rpm_name可以为字符串或字符串列表
def yum_uninstall(rpm_name):
	def uninstall_one(rpm):
		rr = utility.run_cmd("rpm -q "+rpm)
		if rr[0].find("not installed") == -1:
			run_cmd("yum -y remove "+rpm)
			rr = utility.run_cmd("rpm -q "+rpm)
			if rr[0].find("not installed") == -1:
				log.error("yum uninstall failed, find rpm " + rpm + " ," + rr[0])
				raise Exception("yum uninstall failed, find rpm " + rpm + " ," + rr[0])
				#return False
		return True
		
	if isinstance(rpm_name,str):
		return uninstall_one(rpm_name)
	else:
		rr = True
		for r in rpm_name:
			rr &= uninstall_one(r)
		return rr
	
def ping(ip_str,showLog=False):
	r = utility.run_cmd("ping -w 2 " + ip_str,showLog=showLog)
	if len(r[1]):
		return False
	return r[0].find("ttl") != -1 or r[0].find("TTL") != -1

def ping2(ip_str,s_ip,showLog=False):
	r = utility.run_cmd("ping -w 2 " + ip_str + " -S " + s_ip,showLog=showLog)
	if len(r[1]):
		return False
	return r[0].find("ttl") != -1 or r[0].find("TTL") != -1

def hostname():
	return socket.gethostname()	
	
def run_mysql_cmd(sql,user = "root",pwd = None):
	import console
	if pwd is None and user == "root":
		pwd = config.get("environment","mysql_root_password")
	error = "ERROR\s\d+"
	cursor = "MariaDB.*>"
	def run_one(child,cmd):
		if cmd[-1] != ";":
			child.sendline(cmd + ";")
		else:
			child.sendline(cmd)
		log.debug("run sql: " + cmd);
		i = child.expect([error,cursor,pexpect.TIMEOUT],timeout=10)
		if i == 1:
			return (True,child.before)
		if i == 0:
			log.error("Sql Error: " + cmd)
		elif i == 2:
			log.error("Run Sql " + cmd + " timeout")
		assert 0	
		return (False,child.before)

	if 'controller' not in hostname():
		child = pexpect.spawn("mysql -u " + user + " -p " + " -h " + " controller ")
	else:
		child = pexpect.spawn("mysql -u " + user + " -p")
	#直接连接controller节点数据库即可
	#child = pexpect.spawn("mysql -u " + user + " -p " + " -h " + " controller ")
	
	child.logfile_read = console.g_handle # sys.stdout 
	i = child.expect(["Enter password:",pexpect.TIMEOUT],timeout=10)
	if i != 0:
		log.error("Wait pwd timeout," + child.before)
		assert 0
		return (False,child.before)
	child.sendline(pwd)
	child.logfile_send = console.g_handle # sys.stdout 
	i = child.expect([error,cursor,pexpect.TIMEOUT],timeout=10)
	if i == 0:
		log.error("Wrong db password," + child.before)
		assert 0
		return (False,child.before)
	if i == 2:
		log.error("Wait cursor timeout," + child.before)
		assert 0
		return (False,child.before)

	if isinstance(sql,str):
		r = run_one(child,sql)
	else:
		r0 = True
		r1 = ""
		for s in sql:
			rr = run_one(child,s)
			if not rr[0]:
				return rr
			r0 &= rr[0]
			r1 += "\n"+rr[1]
		r = (r0,r1)
	child.sendline("quit;")
	return r

	
def start_service(service_name):
	def run_one(service):
		utility.run_cmd("systemctl enable " + service)
		utility.run_cmd("systemctl restart " + service)
		if check_service(service):
			log.info("start service " + service + " succeed")
			return True
		else:
			log.error("start service " + service + " fail")
			log.error(utility.run_cmd("systemctl status "+service)[0]);
			raise Exception(utility.run_cmd("systemctl status "+service)[0])
			return False
		
	if isinstance(service_name,str):
		r = run_one(service_name)
	else:
		r = True
		for s in service_name:
			r &= run_one(s)
	return r

def stop_service(service_name):
	def run_one(service):
		utility.run_cmd("systemctl stop " + service)
		if not check_service(service):
			log.info("stop service " + service + " succeed")
			return True
		else:
			log.error("stop service " + service + " fail")
			log.error(utility.run_cmd("systemctl status "+service)[0]);
			raise Exception(utility.run_cmd("systemctl status "+service)[0])
			return False
		
	if isinstance(service_name,str):
		r = run_one(service_name)
	else:
		r = True
		for s in service_name:
			r &= run_one(s)
	return r


def check_service(service_name):
	r = utility.run_cmd("systemctl  | grep "+service_name,showLog=False)
	rr = re.search("loaded\s+active\s+",r[0])
	return rr is not None

def run_cmd_seq(cmd,respond_list,timeout=3):
	import console
	log.info("run seq cmd:"+cmd)
	child = pexpect.spawn(cmd)
	child.logfile_read = console.g_handle # sys.stdout 
	child.logfile_send = console.g_handle # sys.stdout 
	for r in respond_list:
		if isinstance(r,list):
			try:
				for n in r:
					log.info("excepting :" + ",".join([n[0] for n in r]))
					
				index = child.expect([re.escape(n[0]) for n in r],timeout=timeout)
				if r[index][1] is not None:
					child.sendline(r[index][1])
					log.info("send :"+r[index][1])
			except pexpect.exceptions.TIMEOUT as e:
				log.error("run seq cmd: " + cmd + " error")
				ee = Exception("prexcept failed`"+child.before+"`, expect: `"
					       + ",".join([n[0] for n in r])+"`");
				log.exception("run seq cmd "+cmd+" failed",ee)
				raise
		else:
			try:
				log.info("excepting :"+r[0])
				child.expect(re.escape(r[0]),timeout=timeout)
				if r[1] is not None:
					child.sendline(r[1])
					log.info("send :"+r[1])
			except pexpect.exceptions.TIMEOUT as e:
				log.error("run seq cmd: " + cmd + " error")
				ee = Exception("prexcept failed`"+child.before+"`, expect: `" + r[0]+"`");
				log.exception("run seq cmd "+cmd+" failed",ee)
				raise
	child.interact() # Give control of the child to the user.
	log.info("run seq cmd: " + cmd + " succeed")
	
def get_bridge():
	global key
	key = ''
	ret = {} 
	r = utility.run_cmd("brctl show",showLog=False)
	if r[0].find('interface') == -1:
		return ret
	for line in r[0].splitlines():
		tmp = line.split('\t')
		if tmp[0] == 'bridge name' and tmp[1] == 'bridge id':
			continue	
		list_value = []
		for i in range(len(tmp)):
			if len(tmp[i]) > 0 and (tmp[i][0].isalpha() or tmp[i][0].isdigit()):
				list_value.append(tmp[i])	
		if len(list_value) == 4:
			key = list_value[0]
			list_dev = []
			ret[key] = []
			ret[key].append(list_value[3])
		else:
			ret[key].append(list_value[0])
			
	return ret
	
def get_networks():
	ret = []
	#	r = utility.run_cmd("ifconfig -a | grep mtu | grep -E '(enp|eth|eno|ens|em)'| grep -v 'ovs-system'",showLog=False)
	r = utility.run_cmd("ip addr | grep  mtu | awk '{print $2}'",showLog=False)
	for rr in r[0].splitlines():
		if len(rr):
			if rr == "lo:":
				continue
			i = rr.find(":")
			if i != -1:
				ret.append(rr[0:i])
	return ret

#根据网卡名取出ip地址和掩码  
def get_network_ip(network_name):
	def get_ip(s):
		i = s.find("/")
		if i == -1:
			return None
		if s.count(".") != 3:
			return None
		ip = s[0:i]
		mask = int(s[i+1:])
		return (ip,mask)
	
	r = utility.run_cmd("""ip addr show %s | grep "inet " | awk '{print $2}'"""%network_name,showLog=False)
	ss = r[0].splitlines()
	ret = []
	if len(ss) != 0: 
		for s in ss:
			ip = get_ip(s)
			if ip is not None:
				ret.append(ip)
	else:
		ret.append(('none',0))
	return ret

#取出网卡的描述，会带上ip地址
def get_network_desc(network_name):
	ips = get_network_ip(network_name)
	if len(ips) == 0:
		return network_name + ": (none)"
	else:
		return network_name +": (" + ",".join([x[0] for x in ips]) + ")"

#两个字符串是否同个子网
def is_same_net(ip1,ip2,mask=24):
    if not utility.is_ip_address(ip1) or not utility.is_ip_address(ip2):
        return False
    if str(mask).isdigit():
        if int(mask) < 0 or int(mask) > 32:
            return False
    else:
        return False
    ip1_list=ip1.split('.')
    ip2_list=ip2.split('.')
    if len(ip1_list) == 4 and len(ip2_list) == 4:
        quotient = int(mask / 8)
        remainder = int(mask % 8)
        for i in range(quotient):
            if ip1_list[i].isdigit() and ip2_list[i].isdigit():
                if bin(int(ip1_list[i]))[2:] != bin(int(ip2_list[i]))[2:]:
                    return False
            else:
                return False
        if remainder:
            if ip1_list[quotient].isdigit() and ip2_list[quotient].isdigit():
                ip1_r = (bin(int(ip1_list[quotient]))[2:]).zfill(8)
                ip2_r = (bin(int(ip2_list[quotient]))[2:]).zfill(8)
                if ip1_r[:remainder] != ip2_r[:remainder]:
                    return False
            else:
                return False
        return True
    return False

def read_hosts():
	import edit
	h = {}
	t = edit.txt_file("/etc/hosts")
	for line in t.lines:
		if line.find("localhost") != -1:
			continue
		l =  line.strip()
		if len(l) == 0:
			continue
		if l[0] == "#":
			continue
		hh = l.split()
		if len(hh) < 2:
			continue
		h[hh[1]] = hh[0]
	return h
	
def update_hosts(host,ip):
	import edit
	h = read_hosts()
	if host not in h:
		t = edit.txt_file("/etc/hosts")
		t.insert(ip+" "+host+"\n")
		t.save()

def stop_selinux():
	import edit
	t = edit.txt_file("/etc/selinux/config")
	t.update("SELINUX=disabled","SELINUX=",edit.MatchMode.StartPos)
	t.save()
	utility.run_cmd("setenforce 0")
	r = utility.run_cmd("/usr/sbin/sestatus -v")
	assert r[0].find("disabled") != -1
	
	utility.run_cmd("systemctl disable firewalld")
	utility.run_cmd("systemctl stop firewalld")

#判断是否为虚拟机
def is_virtual_host():
	r = utility.run_cmd("virt-what")
	return r[0] == "kvm"


def is_cluster_ok(controller_num):
	if not ping("controller"+str(controller_num)):
		return False
	cmd = "pcs cluster auth controller" + str(controller_num) + " -u hacluster -p " + config.get("environment","cluster_password")
	r = utility.run_cmd(cmd)
	return r[0].find("uthorized") != -1

#判断是不是集群最后一个controller
def is_last_controller():
	count = 0
	for i in range(key.CONTROLLER_NUM()):
		if is_cluster_ok(i+1):
			count += 1
	log.info("find cluster count="+str(count))
	if count == key.CONTROLLER_NUM():
		return True
	else:
		return False


################## unit test ##################
def test_backup_file():
	p = os.path.dirname(__file__)
	assert not backup_file("notexist.txt")			       
	f = open(p+"/test.txt","w+")
	value = "this is a test" + str(random.random())
	f.write(value)
	f.close()
	assert os.path.exists(p+"/test.txt")
	
	bb = backup_file(p+"/test.txt")
	assert bb
	newfile  = p+os.path.sep+"test.txt."+datetime.datetime.strftime(datetime.datetime.now(),'%Y%m%d_%H%M%S')+"."+"bak"
	assert bb==newfile
	assert os.path.exists(newfile)
	f = open(newfile,"rt")
	assert f.read() == value
	f.close()
	os.remove(newfile)
	os.remove(p+"/test.txt")
	assert not os.path.exists(p+"/test.txt")
	assert not os.path.exists(newfile)
	
def test_ping():
	assert ping("127.0.0.1")
	assert not ping("27.0.0.1")
	
def test_yum():
	assert yum_install("chrony")
	assert not yum_install("chrony222")
	assert yum_install(["chrony","chrony"])
	
def test_run_mysql_cmd():
	assert run_mysql_cmd("show databases;","root","123456")
	assert not run_mysql_cmd("use test3434","root","123456") #wrong sql 
	assert not run_mysql_cmd("use test","root","wrong")  #wrong pwd 
	
def test_start_service():
	assert start_service("mariadb.service")
	assert not start_service("mariadb.servic222e")
	
if __name__ == '__main__':
	print(get_networks())
	r = get_networks()
	print("=========")
	print(get_network_desc("lo"))
	print(get_network_desc(r[0]))
	#print(read_hosts()) 
	#import utility
	#utility.run_tests()
	#run_cmd("ping 127.0.0.1")
	print(get_bridge())
	
