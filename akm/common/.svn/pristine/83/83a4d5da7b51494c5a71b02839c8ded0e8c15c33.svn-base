#coding=utf-8
import sys,os
if "common" not in sys.path:
    sys.path.append("common")
import shell
import edit
import console
import config
import keystone
import utility
import key

CONFIG_MONITOR_IP = None
VERSION = "5.2.2"
BASE_PATH = "./tools/elk/"
KIBANA_PORT = "8088"

def set_hosts():
	h = shell.update_hosts("elk_monitor",CONFIG_MONITOR_IP)

def setup_elasic():
	def elastic_path():
		return "elasticsearch-"+VERSION
	shell.yum_install("java-1.8.0-openjdk-1.8.0.101-3.b13.el7_2")
	utility.run_cmd("groupadd elsearch")
	utility.run_cmd("useradd elsearch -g elsearch -p elasticsearch") 
	t = edit.txt_file("/etc/security/limits.conf")
	t.update("* soft nofile 65536","* soft nofile")
	t.update("* hard nofile 131072","* hard nofile")
	t.update("* soft nproc 2048","* soft nproc")
	t.update("* hard nproc 4096","* hard nproc")
	t.save()
	
	t = edit.txt_file("/etc/sysctl.conf")
	t.update("vm.max_map_count=655360","vm.max_map_count")
	t.save()
	utility.run_cmd("sysctl -p")
	
	shell.yum_install("iptables")
	shell.yum_install("iptables-services")
	shell.start_service("iptables.service")
	
	rr = utility.run_cmd("iptables -I INPUT -p tcp --dport 9200 -j ACCEPT")
	assert rr[1] == ""
	
	rr = utility.run_cmd("iptables -I INPUT -p tcp --dport 5044 -j ACCEPT")
	assert rr[1] == ""
	
	rr = utility.run_cmd("iptables -I INPUT -p tcp --dport "+KIBANA_PORT+" -j ACCEPT")
	assert rr[1] == ""
	
	rr = utility.run_cmd("service iptables save")
	assert rr[0].find("OK") != -1
	
	rr = utility.run_cmd("systemctl restart iptables")
	
	f = BASE_PATH+elastic_path()+".tar.gz"
	f2 = "/"+elastic_path()
	utility.run_cmd("rm -Rf "+f2)
	utility.run_cmd("cp "+ f + " /")
	utility.run_cmd("cd /;tar -zxf " + f2+".tar.gz;cd -")
	utility.run_cmd("rm -f /"+elastic_path()+".tar.gz")
	utility.run_cmd("chmod -R +777 "+f2)
	
	#由于elasticsearch 很耗内存，此处如果检测到宿主机内存小于16G，将elasticsearch中内存配置设置为1G
	check_mem = utility.run_cmd("free -h |awk '/Mem/ {print $2}'")[0]
	t = edit.txt_file(f2+"/config/jvm.options")
	if int(check_mem.split("G")[0]) < 16: #默认free -h取出内存以G为单位
		t.update("-Xms1g","-Xms2g")
		t.update("-Xmx1g","-Xmx2g")
	t.save()
	
	t = edit.txt_file(f2+"/config/elasticsearch.yml")
	t.update("http.port: 9200","http.port:")
	t.update("network.host: "+CONFIG_MONITOR_IP,"network.host:")
	t.update("action.auto_create_index: true","action.auto_create_index:")
	if key.SUPPORT_HA():
		#HA暂定集群名称为combacloud-cluster，节点名称为node-combacloud
		t.update("cluster.name: combacloud-cluster","cluster.name:")
		t.update("node.name: node-combacloud","node.name:")
		t.update("node.master: true","node.master:")
		t.update("node.data: true","node.data:")
		t.update('discovery.zen.ping.unicast.hosts: %s' %str(["%s"%str(i) for i in key.CONTROLLER_IPS()]),"discovery.zen.ping.unicast.hosts:")
		t.update("discovery.zen.ping_timeout: 5s","discovery.zen.ping_timeout:")
		#t.update("discovery.zen.minimum_master_nodes: 1","discovery.zen.minimum_master_nodes:")
		if int(key.CONTROLLER_NUM()) == 2:#为两个节点时，测试此处只能设置为1才正常运行
			t.update("discovery.zen.minimum_master_nodes: 1","discovery.zen.minimum_master_nodes:")
		else:
			t.update("discovery.zen.minimum_master_nodes: %s" %(int(key.CONTROLLER_NUM())/2 +1),"discovery.zen.minimum_master_nodes:")
	t.save()
	
	#ExecStart={0}/bin/elasticsearch > /dev/null报错，删掉 > /dev/null
	sss = """[Unit]
Description=Daemon to start elsearch(elk)
Wants=network-online.target
After=network.target

[Service]
Type=simple
ExecStart={0}/bin/elasticsearch
User=elsearch
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target  
	"""
	#LimitNOPROC=65536
	edit.write_file("/usr/lib/systemd/system/elsearch.service",sss.format(f2))
	shell.start_service("elsearch.service")

	
def setup_kibana():
	def kibana_path():
		return "kibana-"+VERSION+"-linux-x86_64"
	
	p = BASE_PATH+kibana_path()+".tar.gz"
	p2 = BASE_PATH+kibana_path()
	p3 = "/root/"+kibana_path()
	shell.run_cmd("tar -xzf "+p)
	utility.run_cmd("rm -Rf /root/"+kibana_path())
	utility.run_cmd("mv "+kibana_path() +" /root/")
	t = edit.txt_file(p3+"/config/kibana.yml")
	t.update("server.port: 8088","server.port")
	##将绑定ip口由原来的"0.0.0.0"改为管理IP
	#t.update('server.host: "%s"' %CONFIG_MONITOR_IP,"server.host")
	t.update('server.host: "0.0.0.0"',"server.host")
	t.update('elasticsearch.url: "http://elk_monitor:9200"',"elasticsearch.url")
	t.save()
	
	shell.run_cmd("tar -zxf "+BASE_PATH+"kibana-time-plugin.tar.gz")
	utility.run_cmd("mv kibana-time-plugin "+p3+"/plugins/")
	t = edit.txt_file(p3+"/plugins/kibana-time-plugin/package.json")
	t.update('"version": "'+VERSION+'"','"version":')
	t.save()

	sss = """[Unit]
Description=Daemon to start Kibana(elk)
Wants=network-online.target
After=network.target

[Service]
Type=simple
ExecStart={0}/bin/kibana

[Install]
WantedBy=multi-user.target 
	"""
	edit.write_file("/usr/lib/systemd/system/kibana.service",sss.format(p3))
	shell.start_service("kibana.service")
	#utility.run_cmd(p3+"/scripts/import_dashboards -dir "++" -es http://elk_monitor:9200")
	
	
def setup_logstash():	
	def logstash_path():
		return "logstash-"+VERSION
	p = BASE_PATH+logstash_path()+".tar.gz"
	p2 = BASE_PATH+logstash_path()
	p3 = "/root/"+logstash_path()	
	shell.run_cmd("tar -xzf "+p)
	utility.run_cmd("rm -Rf /root/"+logstash_path())
	utility.run_cmd("mv "+logstash_path() +" /root/")
	edit.write_file(p3+"/openstack_pattern","OPENSTACK_SERVICE \S+(\.\S+)*\nOPENSTACK_REQ \[.*\]")
	sss = """input {
    beats {
        port => "5044"   
    }
}   
filter {  
  grok {
    patterns_dir => ["/root/logstash-5.2.2/openstack_pattern"]	
 	match => ["message", "%{DATESTAMP:logtimestamp} %{NUMBER:pid} %{LOGLEVEL:level} %{NOTSPACE:service} (?:%{OPENSTACK_REQ:req}|) %{GREEDYDATA:message}",
              "message","%{DATESTAMP:logtimestamp} %{NUMBER:pid} %{LOGLEVEL:level} %{OPENSTACK_SERVICE:service} %{GREEDYDATA:message}",
              "message","%{DATESTAMP:logtimestamp} %{NUMBER:pid} %{LOGLEVEL:level} %{OPENSTACK_SERVICE:service}" ]
    overwrite => ["message"]
  }
  date {
    match => [ "logtimestamp", "yy-MM-dd HH:mm:ss.SSS" ]
    remove_field => ["logtimestamp"]
  }
}

output {
    elasticsearch {
        hosts => [ "{0}:9200" ]
		index => "openstacklog-%{+YYYY.MM.dd}"
    }
    #stdout { codec => rubydebug }
}"""
	global CONFIG_MONITOR_IP 
	edit.write_file(p3+"/log.conf",sss.replace("{0}",CONFIG_MONITOR_IP))
	sss = """[Unit]
Description=Daemon to start Logstash(elk)
Wants=network-online.target
After=network.target

[Service]
Type=simple
ExecStart={0}/bin/logstash -f {0}/log.conf --config.reload.automatic

[Install]
WantedBy=multi-user.target 
	"""
	edit.write_file("/usr/lib/systemd/system/logstash.service",sss.format(p3))
	shell.start_service("logstash.service")

def setup_metricbeat():		
	def metricbeat_path():
		return "metricbeat-"+VERSION+"-linux-x86_64"	
	p = BASE_PATH+metricbeat_path()+".tar.gz"
	p2 = BASE_PATH+metricbeat_path()
	p3 = "/root/"+metricbeat_path()
	shell.run_cmd("tar -xzf "+p)
	utility.run_cmd("rm -Rf /root/"+metricbeat_path())
	utility.run_cmd("mv "+metricbeat_path() +" /root/")
	
	sss = """metricbeat.modules:
- module: system
  metricsets:
    - cpu
    - load
    #- core
    - diskio
    - filesystem
    - fsstat
    - memory
    - network
    #- process
  enabled: true
  period: 30s
  processes: ['.*']
output.elasticsearch:
  hosts: ["elk_monitor:9200"]"""
	edit.write_file(p3+"/metricbeat.yml",sss) 
	
	sss = """[Unit]
Description=Daemon to start Metricbeat(elk)
Wants=network-online.target
After=network.target

[Service]
Type=simple
ExecStart={0}/metricbeat -e -c {0}/metricbeat.yml  -d "publish"

[Install]
WantedBy=multi-user.target"""
	edit.write_file("/usr/lib/systemd/system/metricbeat.service",sss.format(p3))
	shell.start_service("metricbeat.service")
	
def setup_filebeat():
	def filebeat_path():
		return "filebeat-"+VERSION+"-linux-x86_64"
	p = BASE_PATH+filebeat_path()+".tar.gz"
	p2 = BASE_PATH+filebeat_path()
	p3 = "/root/"+filebeat_path()
	shell.run_cmd("tar -xzf "+p)
	utility.run_cmd("rm -Rf /root/"+filebeat_path())
	utility.run_cmd("mv "+filebeat_path() +" /root/")
	sss = """filebeat.prospectors:
- input_type: log
  paths:
    - /var/log/nova/*.log
    - /var/log/heat/*.log
    - /var/log/keystone/*.log
    - /var/log/manila/*.log
    - /var/log/glance/*.log
    - /var/log/magnum/*.log
    - /var/log/neutron/*.log
    - /var/log/aodh/*.log
    - /var/log/ceilometer/*.log
    - /var/log/cinder/*.log
  exclude_lines: [".* INFO .*",".* DEBUG .*"]
  exclude_files: [".gz$"]
output.logstash:
  hosts: ["elk_monitor:5044"]"""
	edit.write_file(p3+"/filebeat.yml",sss) 
	sss = """[Unit]
Description=Daemon to start Filebeat(elk)
Wants=network-online.target
After=network.target

[Service]
Type=simple
ExecStart={0}/filebeat -e -c {0}/filebeat.yml -d "publish"

[Install]
WantedBy=multi-user.target """
	edit.write_file("/usr/lib/systemd/system/filebeat.service",sss.format(p3))
	shell.start_service("filebeat.service")
	
def ensure_pyc(filepath):
	if os.path.exists(filepath):
		return
	pyfile = filepath[:-1]
	assert os.path.exists(pyfile)
	import py_compile 
	py_compile.compile(pyfile)
	assert os.path.exists(filepath)
	
def write_systemctrl(path,filename,args):
	ensure_pyc(path+"/" +filename)
	sss = """[Unit]
	Description=Daemon to start {0}(elk)
	Wants=network-online.target
	After=network.target

	[Service]
	Type=simple
	ExecStart=/usr/bin/python2.7 /root/Source/{0}/{1} {2}

	[Install]
	WantedBy=multi-user.target"""
	edit.write_file("/usr/lib/systemd/system/"+path+".service",sss.format(path,filename,args))
	#shell.start_service(path+".service")
	
def setup_pyvirt():
	#utility.run_cmd("tar -zxf tools/virt/pip-1.5.4.tar.gz")
	#utility.run_cmd("cd pip-1.5.4;python setup.py install;cd -")
	#utility.run_cmd("pip install tools/virt/elasticsearch-5.3.0-py2.py3-none-any.whl")
	#utility.run_cmd("rm -Rf pip-1.5.4")
	#shell.yum_install("libguestfs-tools")
	#shell.yum_install("libguestfs-winsupport")
	#
	#if not os.path.exists("/usr/lib/python2.7/site-packages/mysql_connector_python-2.0.4-py2.7.egg-info"):
	#	utility.run_cmd("tar -zxf tools/virt/mysql-connector-python-2.0.4.tar.gz")
	#	utility.run_cmd("cd mysql-connector-python-2.0.4;python setup.py install;cd -")
	#	utility.run_cmd("rm -Rf mysql-connector-python-2.0.4")
	
	if key.TYPE() == "controller":
		write_systemctrl("pyalarm","alarm.pyc","30")
		write_systemctrl("pycheckimg","checkimg.pyc","10")
		write_systemctrl("pylink","link.pyc","30")
		#不管是否是HA，都要pylink拉起来
		shell.start_service("pylink.service")
		#不支持HA情况下，直接拉起service服务
		if not key.SUPPORT_HA():
			shell.start_service("pyalarm.service")
			shell.start_service("pycheckimg.service")
			#shell.start_service("pylink.service")
		#如果支持HA，并判断是controller节点中最后一个controller节点；支持HA，不是最后一个controller节点暂不拉起服务，跳过
		else:
			#如果是HA，后面会统一集群拉起服务，不管服务是否起，此处要先disable（开机不自动启动各自服务）和stop
			utility.run_cmd("systemctl disable pyalarm.service")
			utility.run_cmd("systemctl stop pyalarm.service")
			utility.run_cmd("systemctl disable pycheckimg.service")
			utility.run_cmd("systemctl stop pycheckimg.service")
			if key.IS_LAST_CNO():#判断是controller节点集群中最后一个controller节点
				#controller集群中主节点拉起服务
				#主节点上拉起pyalarm.service服务
				utility.run_cmd("pcs resource create lb-pyalarm systemd:pyalarm")
				utility.run_cmd("pcs constraint order start vip then lb-pyalarm kind=Optional")
				utility.run_cmd("pcs constraint colocation add lb-pyalarm with vip")
				#统一加到组service_group中
				utility.run_cmd("pcs resource group add service_group lb-pyalarm")
				#主节点上拉起pycheckimg.service服务
				utility.run_cmd("pcs resource create lb-pycheckimg systemd:pycheckimg")
				utility.run_cmd("pcs constraint order start vip then lb-pycheckimg kind=Optional")
				utility.run_cmd("pcs constraint colocation add lb-pycheckimg with vip")
				#统一加到组service_group中
				utility.run_cmd("pcs resource group add service_group lb-pycheckimg")
	elif key.TYPE() == "compute":
		write_systemctrl("pyvirt","main.pyc","30")
		write_systemctrl("pylink","link.pyc","30")
		shell.start_service("pyvirt.service")
		shell.start_service("pylink.service")
	elif key.TYPE() == "block":
		write_systemctrl("pycheckvolumn","checkvolumn.pyc","3600")
		write_systemctrl("pylink","link.pyc","30")
		shell.start_service("pycheckvolumn.service")
		shell.start_service("pylink.service")
		
	#各个节点都会拉起pyproc检测service服务进程	
	write_systemctrl("pyproc","proc.pyc","30")
	#判断该pyproc进程运行在控制节点，并是支持HA，
	if key.TYPE() == "controller" and key.SUPPORT_HA():
		#如果是HA，后面会统一集群拉起服务，不管服务是否起，此处要先disable（开机不自动启动各自服务）和stop
		utility.run_cmd("systemctl disable pyproc.service")
		utility.run_cmd("systemctl stop pyproc.service")
		if key.IS_LAST_CNO():#是最后一个controller节点情况下才拉起集群服务
			#主节点上拉起pyproc.service服务
			utility.run_cmd("pcs resource create lb-pyproc systemd:pyproc")
			utility.run_cmd("pcs constraint order start vip then lb-pyproc kind=Optional")
			utility.run_cmd("pcs constraint colocation add lb-pyproc with vip")
			#统一加到组service_group中
			utility.run_cmd("pcs resource group add service_group lb-pyproc")
		else:#不是最后一个controller节点情况暂不拉起服务，返回
			return
	#其他不是controller节点，或不支持HA情况下，可直接拉起服务
	else:
		shell.start_service("pyproc.service")
	
def install_controller():
	bar = console.bar("elk.componet",total=6)
	set_hosts()
	setup_elasic()
	bar.step()
	setup_kibana()
	bar.step()
	setup_logstash()	
	bar.step()
	setup_metricbeat()
	bar.step()
	setup_filebeat()
	bar.step()
	setup_pyvirt()
	if "pyvirt" not in sys.path:
		sys.path.append("pyvirt")
	#由于配置elk集群情况。3个节点情况下，安装第一个节点在此处直接更新数据会出错，此处判断最后一个节点再更新数据，elk集群内部数据再同步
	import update_elk_data
	update_elk_data.update_data()
	if not key.SUPPORT_HA():#如果不是HA安装，正常导入数据
		update_elk_data.update_data()
	elif key.SUPPORT_HA() and key.IS_LAST_CNO():#如果是HA安装，并是最后一个节点，则导入数据（elk加入到haproxy，controller前提下），其他情况不导入
		update_elk_data.update_data()
	bar.step()
	
def install_compute():
	bar = console.bar("elk.componet",total=3)
	set_hosts()
	setup_metricbeat()
	bar.step()
	setup_filebeat()
	bar.step()
	setup_pyvirt()
	bar.step()
	
def verify():
	r = utility.run_cmd("curl elk_monitor:9200")
	assert r[0].find("You Know, for Search") != -1

def service():
	if key.TYPE() == "controller":
		return ["elsearch.service","logstash.service","kibana.service","metricbeat.service","filebeat.service","pyalarm.service","pylink.service","pycheckimg.service"]
	else:
		return ["metricbeat.service","filebeat.service","pyvirt.service","pylink.service"]

def setup():
	global CONFIG_MONITOR_IP
	CONFIG_MONITOR_IP = key.CONTROLLER_IP()
	if key.TYPE() == "controller":
	    install_controller()
	elif key.TYPE() == "compute":
		install_compute()
	elif key.TYPE() == "block":
		setup_pyvirt()
	verify()
	
if __name__ == '__main__':
	ensure_pyc("pyvirt/main.pyc")
	ensure_pyc("pyalarm/alarm.pyc")
	
	key.select_config_file()
	setup()


