#coding=utf-8 
# ycat			 2015/12/28      create
import sys,os

def from_str(macstr):
	r = macstr.replace("-",":").split(":")
	if len(r) != 6:
		return empty()
	try:
		return mac(*[ int(x,16) for x in r])
	except ValueError:
		return empty()

def empty():
	return mac(0,0,0,0,0,0)

def from_int(intvalue):
	if intvalue > 0xFFFFFFFFFFFF:
		return empty()
		
	n = 0x10000000000
	r = [0,0,0,0,0,0]
	for i in range(6):
		r[i] = int(intvalue/n)
		intvalue %= n
		n /= 0x100
	return mac(*r)

def from_devid(strvalue):
	index = strvalue.find("_")
	if index == -1:
		ss = strvalue
		dd = "0"
	else:
		ss = strvalue[index+1:]
		dd = strvalue[0:index]
	if len(ss) > 12:
		return (dd,empty())
	return (dd,from_int(int(ss,16)))

def from_deviceid(strvalue):
	strn = strvalue.split("_")
	dd = 0
	aa = ""
	if len(strn) == 3:
		dd = strn[0]
		aa = strn[1]
		ss = strn[2]
	elif len(strn) == 2:
		dd = strn[0]
		ss = strn[1]
	elif len(strn) == 1:
		ss = strn[0]
	else:
		ss = strn
	if len(ss) > 12:
		return (0,"",empty())
	return (dd,aa,from_int(int(ss,16)))

#返回当前系统的mac地址 
def system_mac():
	import uuid
	m = uuid.uuid1().hex[-12:]
	s = ""
	for i in range(0,12,2):
		s += m[i] + m[i+1] + "-"
	return from_str(s[:-1])

class mac:
	def __init__(self,*mac):
		assert(len(mac) == 6)
		self._mac = mac
		for x in self._mac:
			assert isinstance(x,int)
	
	def __str__(self):
		return self.to_str()

	def __eq__(self,other):
		for i in range(6):
			if other[i] != self[i]:
				return False
		return True
	
	def __getitem__(self,index):
		return self._mac[index]
	
	def int(self):
		r = 0
		n = 0x10000000000
		for i in range(len(self._mac)):
			r += self[i]*n
			n /= 0x100
		return r
	
	def to_str(self,token=":"):
		return token.join(["%02x"%x for x in self._mac])
	
	#防止mac地址冲突，所以增加domain做为前缀,  
	def devid(self,domainid):
		return str(domainid) + "_" + self.to_str("")
	
	#devid为domainid_accountid_apmac
	def deviceid(self,domainid,accountid):
		return str(domainid) + "_" + str(accountid) + "_" +self.to_str("")
		

#############################	unit test	###########################
def test_sys_mac():
	assert isinstance(system_mac(),mac)
	
def test_mac():
	assert str(mac(0x10,0x16,0x31,0xf2,0x78,0x96)) == "10:16:31:f2:78:96"
	assert str(mac(0x10,0xAB,0xCD,0xf2,0x78,0x96)) == "10:ab:cd:f2:78:96"
	assert str(mac(0x10,0x1,0xEF,0xf2,0x0,0x96)) == "10:01:ef:f2:00:96"
	
	assert mac(0x10,0x1,0xEF,0xf2,0x0,0x96) == from_str("10:01:ef:f2:00:96")
	assert mac(0x10,0x1,0xEF,0xf2,0x0,0x96) == from_str("10:01:EF:F2:00:96")
	assert mac(0x10,0x1,0xEF,0xf2,0x0,0x96) == from_str("10-01-EF-F2-00-96")
	assert empty() == from_str("10:01:EF:F2:00:96:")
	assert empty() == from_str("10:01:EF:F2:00:96:AA")
	assert empty() == from_str("10:01:EF:F2:00:")
	assert empty() == from_str("")
	assert empty() == from_str("::::::")
	assert empty() == from_str("10:01:EF:F2:00:")
	assert empty() == from_str("10:01:EF:F2::96")
	assert empty() == from_str("10:01:ef:f2:00:G1")
	
	assert from_str("10:01:ef:f2:00:96").int() == 0x1001eff20096
	assert mac(0x0,0x1,0xEF,0x0,0xab,0x96).int() == 0x1ef00ab96
	assert from_int(0) == empty()
	assert from_int(1) == mac(0,0,0,0,0,1)
	assert from_int(0x21) == mac(0,0,0,0,0,0x21)
	assert from_int(0x321) == mac(0,0,0,0,3,0x21)
	assert from_int(0x54321) == mac(0,0,0,5,0x43,0x21)
	assert from_int(0x7654321) == mac(0,0,7,0x65,0x43,0x21)
	assert from_int(0x987654321) == mac(0,9,0x87,0x65,0x43,0x21)
	assert from_int(0xba987654321) == mac(0xb,0xa9,0x87,0x65,0x43,0x21)
	assert from_int(0xcba987654321) == mac(0xcb,0xa9,0x87,0x65,0x43,0x21)
	assert from_int(0x1ef00ab96) == mac(0x0,0x1,0xEF,0x0,0xab,0x96)
	
	assert mac(0x10,0x16,0x31,0xf2,0x78,0x96).devid(12) == "12_101631f27896"
	assert ("0",mac(0x10,0x16,0x31,0xf2,0x78,0x96)) == from_devid("101631f27896")
	assert ("12",mac(0x10,0x16,0x31,0xf2,0x78,0x96)) == from_devid("12_101631f27896")
	assert ("12",mac(0x00,0x06,0x31,0xf2,0x78,0x96)) == from_devid("12_631f27896")
	assert ("0",mac(0,0,0,0,0,1)) == from_devid("1")
	assert ("12",empty()) == from_devid("12_1FFFFFFFFFFFF")
	assert ("0",empty()) == from_devid("1FFFFFFFFFFFF")
	assert empty() == from_int(0x1FFFFFFFFFFFF)
	assert empty() == from_int(0x1000000000000)
	
	
def test_mac2int():
	a = from_str('00-27-1d-00-00-01').int()
	assert a == 167990263809
	assert a != 167990263819
	
	a = from_str('00:27:1d:ff:02:ff').int()
	assert a == 168006976255
	assert a != 134
	
	a = from_str('00:27:1d:FF:02:FF').int()
	assert a == 168006976255
	
	a = from_str('').int()
	assert a == 0
	
	a = 167990263809
	mac = from_int(a)
	assert str(mac) == '00:27:1d:00:00:01'
	
	a = 167990263810
	mac = from_int(a)
	assert str(mac) == '00:27:1d:00:00:02'   	
	
if __name__ == '__main__':
	import utility
	utility.run_tests()
	