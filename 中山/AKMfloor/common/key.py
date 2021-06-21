#coding=utf-8 
# ycat			2016-9-29      create
import sys,os
import config
import shell

cfg = None

#设置枚举类型，选择获取不同类型
def enum(**enums):
	return type('Enum', (), enums)
RETYPE = enum(NAME=0, IP=1, NAMEIP=2)
IPTYPE = enum(MANAGER=0, PROVIDER=1, VXLAN=2, VLAN=3, FLAT=4)

def get_cfg():
	global cfg 
	return cfg

def select_config_file():
	import setup_config
	import console
	console.restore_stdout()
	setup_config.select_config_file()

def set_config(filename):
	global cfg
	cfg = config.config(filename)

def get_type_name(typeno):
	if typeno == 1:
		return "controller"
	elif typeno == 3:
		return "compute"
	elif typeno == 4:
		return "block"
	elif typeno == 5:
		return "object"
	else:
		assert 0
		
def TYPE(): 
	i = get_cfg().getint("setup","type")
	return get_type_name(i)

#安装机子的顺序，例如第几台compute机子 
def SETUP_NO(): 
	return get_cfg().getint("setup","setup_no")

#判断是不是最后一个控制节点安装
def IS_LAST_CNO():
	if SETUP_NO() == CONTROLLER_NUM():
		return True
	else:
		return False


def PROVIDER_INTERFACE_NAME(): 
	return get_cfg().get("setup","interface_provider_name")

def PROVIDER_IP(): 
	return get_cfg().get("setup","interface_provider_ip")

def PROVIDER_MASK(): 
	return get_cfg().get("setup","interface_provider_mask")

def PROVIDER_CIDR():
	#return PROVIDER_IP()+"/"+str(PROVIDER_MASK())
	return  SEGMENT_IP(IPTYPE.PROVIDER, str(PROVIDER_MASK()))+"/"+str(PROVIDER_MASK())

def FLAT_INTERFACE_NAME(): 
	return get_cfg().get("setup","interface_flat_name")

def FLAT_IP(): 
	return get_cfg().get("setup","interface_flat_ip")

def FLAT_MASK(): 
	return get_cfg().get("setup","interface_flat_mask")

def FLAT_CIDR():
	#return FLAT_IP()+"/"+str(FLAT_MASK())
	return  SEGMENT_IP(IPTYPE.FLAT, str(FLAT_MASK()))+"/"+str(FLAT_MASK())

def ISFLAT():
	return get_cfg().getbool("setup","isflat",False)

def MANAGER_INTERFACE_NAME(): 
	return get_cfg().get("setup","interface_manager_name")

def MANAGER_IP(): 
	return get_cfg().get("setup","interface_manager_ip")

def SEGMENT_IP(iptype=IPTYPE.MANAGER, ipmask='24'):
	#根据网络类型从配置文件获取ip
	if iptype == IPTYPE.MANAGER:
		IP = MANAGER_IP()
	elif iptype == IPTYPE.PROVIDER:
		IP = PROVIDER_IP()
	elif iptype == IPTYPE.VXLAN:
		IP = VXLAN_IP()
	elif iptype == IPTYPE.VLAN:
		IP = VLAN_IP()
	elif iptype == IPTYPE.FLAT:
		IP = FLAT_IP()
	#根据mask设置网段	
	IP_LIST = IP.split(".")
	if ipmask == '24':
		IP_LIST[-1] = "0"
	elif ipmask == '16':
		IP_LIST[-1] = "0"
		IP_LIST[-2] = "0"
	elif ipmask == '8':
		IP_LIST[-1] = "0"
		IP_LIST[-2] = "0"
		IP_LIST[-3] = "0"
	return ".".join(IP_LIST)

def MANAGER_MASK(): 
	return get_cfg().get("setup","interface_manager_mask")

def MANAGER_CIDR():
	#return  MANAGER_IP()+"/"+str(MANAGER_MASK())
	return  SEGMENT_IP(IPTYPE.MANAGER, str(MANAGER_MASK()))+"/"+str(MANAGER_MASK())

def VLAN_INTERFACE_NAME(): 
	return get_cfg().get("setup","interface_vlan_name")

def VLAN_IP(): 
	return get_cfg().get("setup","interface_vlan_ip")

def VLAN_MASK(): 
	return get_cfg().get("setup","interface_vlan_mask")

def VLAN_CIDR():
	#return  VLAN_IP()+"/"+str(VLAN_MASK())
	return  SEGMENT_IP(IPTYPE.VLAN, str(VLAN_MASK()))+"/"+str(VLAN_MASK())

def ISVLAN():
	return get_cfg().getbool("setup","isvlan",False)

def VXLAN_INTERFACE_NAME(): 
	return get_cfg().get("setup","interface_vxlan_name")

def VXLAN_IP(): 
	return get_cfg().get("setup","interface_vxlan_ip")

def VXLAN_MASK(): 
	return get_cfg().get("setup","interface_vxlan_mask")

def VXLAN_CIDR():
	#return  VXLAN_IP()+"/"+str(VXLAN_MASK())
	return  SEGMENT_IP(IPTYPE.VXLAN, str(VXLAN_MASK()))+"/"+str(VXLAN_MASK())

def ISVXLAN():
	return get_cfg().getbool("setup","isvxlan",False)

def MECH_NO():
	return get_cfg().getint("setup","mech_no")

def IS_ACTION():
	return SETUP_NO() == 1

def SUPPORT_HA(): 
	return get_cfg().getbool("setup","enable_controller_ha",False) 

def CONTROLLER_NUM(): 
	return get_cfg().getint("setup","max_controller_num",1) 	

def DISK_DEV():
	return get_cfg().get("setup","disk_dev")

def SHARE_DEV():
	return get_cfg().get("setup","share_dev")

def BLOCK_TYPE():
	return get_cfg().get("setup","block_type")

def NFS_VOLUME_ADDRESS():
	return get_cfg().get("setup","nfs_volume_address")

def NFS_VOLUME_PATH():
	return get_cfg().get("setup","nfs_volume_path")

def NFS_IMAGE_ADDRESS():
	return get_cfg().get("setup","nfs_image_address")

def NFS_IMAGE_PATH():
	return get_cfg().get("setup","nfs_image_path")

def NFS_INSTANCE_ADDRESS():
	return get_cfg().get("setup","nfs_instance_address")

def NFS_INSTANCE_PATH():
	return get_cfg().get("setup","nfs_instance_path")

def GLANCE_TO_NFS():
	return get_cfg().get("setup","is_glance_mount_to_nfs")

def IS_GLANCE_TO_CEPH():
	return get_cfg().getbool("setup","ceph_image",False)

def IS_INSTANCE_TO_CEPH():
	return get_cfg().getbool("setup","ceph_instance",False)

def IS_BLOCK_TO_CEPH():
	return get_cfg().getbool("setup","ceph_block",False)

def VNC_ADDRESS():
	return get_cfg().get("setup","vnc_address")

def ENVIRONMENT():
	return get_cfg().get("setup","environment")

def CEPH_ADDRESS_INSTANCE():
	return get_cfg().get("setup","ceph_address_instance")

def CEPH_PASSWORD_INSTANCE():
	return get_cfg().get("setup","ceph_password_instance")

def CEPH_ADDRESS_IMAGE():
	return get_cfg().get("setup","ceph_address_image")

def CEPH_PASSWORD_IMAGE():
	return get_cfg().get("setup","ceph_password_image")

def CEPH_ADDRESS_VOLUME():
	return get_cfg().get("setup","ceph_address_volume")

def CEPH_PASSWORD_VOLUME():
	return get_cfg().get("setup","ceph_password_volume")

#虚IP的controller的IP
g_hosts = None
def CONTROLLER_IP():
	ip = get_cfg().get("setup","virtual_controller_ip") 
	if len(ip) != 0:
		return ip
	if TYPE() == "controller":
		return MANAGER_IP()
	#旧版本没有配置这个  
	assert 0

def HOSTS():
	global g_hosts
	if g_hosts is None:
		g_hosts = shell.read_hosts()
	return g_hosts

def CONTROLLER_IPS(retype=None): 
	global g_hosts
	r = []
	t = {}
	if g_hosts is None:
		g_hosts = shell.read_hosts()
	for h in g_hosts:
		if h == "controller":
			continue
		if h.find("controller") != -1:
			t[h] = g_hosts[h]
			#r.append(g_hosts[h])
	c = len(t)
	if retype == RETYPE.NAMEIP: #获取得到字典形式controller和ip信息
		return t
	elif retype == RETYPE.NAME: #按顺序获取得到list形式的name
		for i in range(c):
			r.append("controller" + (i+1))
		return r
	else:#不传参数或传入参数为RETYPE.IP，则默认返回排好顺序的IP（原来直接由dict转成list是无序的）
		for i in range(c):
			r.append(t["controller" + str(i+1)])
		return r
			

#判断自己是controller几
def WHO_AM_I():
	assert TYPE() == "controller"
	if CONTROLLER_IP() == MANAGER_IP():
		return 0
	h = HOSTS()
	if "controller1" in h:
		if h["controller1"] == MANAGER_IP():
			return 1

	if "controller2" in h:
		if h["controller2"] == MANAGER_IP():
			return 2

	if "controller3" in h:
		if h["controller3"] == MANAGER_IP():
			return 3

	return -1


def set_step(step): 
	get_cfg().set("setup","setup_step",step)
		
def step(): 
	return get_cfg().get("setup","setup_step")
