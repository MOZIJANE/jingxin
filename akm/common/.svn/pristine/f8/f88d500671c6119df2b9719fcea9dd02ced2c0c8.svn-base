#coding=utf-8 
# ycat			2016-9-29      create
import sys,os,re
import utility

class MatchMode:
	Any = 1
	StartPos = 2
	EndPos = 3
	Pattern = 4

def write_file(filename,content):
	f = open(filename,"w")
	f.write(content)
	f.close()
	
class txt_file:
	def __init__(self,file,EditOnly=True):
		self.file = file
		if not os.path.exists(file):
			if EditOnly:
				raise Exception("No such file " + file)
			self.lines = []
		else:
			f = open(file,"r")
			self.lines = [ l.rstrip() for l in f.readlines() ] 
			f.close()
	
	def save(self):
		f = open(self.file,"w+")
		for i,line in enumerate(self.lines):
			if i==len(self.lines)-1:
				f.write(line)
			else:
				f.write(line+"\n")
		f.close()
	
	def insert(self,line,keyword="",mode=MatchMode.Any):
		if keyword == "":
			self.lines.append(line)
		else:
			lineno = self._find(keyword,mode)
			self.lines.insert(lineno,line)
		
	def update(self,line,keyword,mode=MatchMode.Any,updateOne=True):
		c = 0
		while True:
			lineno = self._find(keyword,mode)
			if lineno == -1:
				self.lines.append(line)
				return 1
			self.lines[lineno] = line
			c+=1
			if updateOne:
				return c
	
	def delete(self,keyword,mode=MatchMode.Any,deleteOne=True):
		c = 0
		while True:
			lineno = self._find(keyword,mode)
			if lineno == -1:
				return c
			del self.lines[lineno]
			c+=1
			if deleteOne:
				return c
	
	def _find(self,keyword,mode,startLineno = -1,endLineno = -1):
		assert mode <= MatchMode.Pattern
		assert mode > 0
		assert isinstance(keyword,str)
		assert len(self.lines) <= 0xFFFFFFFF
		for lineno,line in enumerate(self.lines):
			if lineno < startLineno:
				continue
			if endLineno>0 and lineno > endLineno:
				return -1
			if mode == MatchMode.Pattern:
				m = re.match(keyword,line)
				if m:
					return lineno
				else:
					continue
				
			index = line.find(keyword)
			if index == -1:
				continue
			line2 = line.strip()
			index = line2.find(keyword) 
			if mode == MatchMode.Any:
				return lineno
			elif mode == MatchMode.StartPos:
				if index == 0:
					return lineno
			elif mode == MatchMode.EndPos:
				if index == (len(line2) - len(keyword)):
					return lineno
		return -1		

class config_file:
	def __init__(self,file,EditOnly=True):
		self.file = txt_file(file,EditOnly)
	
	def update(self,session,key,value):
		def get_key_str(key,value):
			if len(value):
				return key+"="+value
			return key
		
		index = self._find_key(session,key)
		if index == (-1,-1):
			#can't find session
			self.file.lines.append("["+session+"]")
			self.file.lines.append(get_key_str(key,value))
			return
		if index[1] != -1:
			self.file.lines[index[1]] = get_key_str(key,value)
		if index[1] == -1:
			self.file.lines.insert(index[0]+1,get_key_str(key,value))

	#其实是注释掉配置   
	def delete(self,session,key):
		i = self._find_key(session,key,has_comment=False)
		if i[1] != -1:
			self.file.lines[i[1]] = "#"+self.file.lines[i[1]]
		
	def save(self):
		self.file.save()
	
	def _find_key(self, session, key, has_comment=True):
		r = self._find_session(session)
		if r == (-1,-1):
			return -1,-1
		#先查找#紧接key的值 
		if has_comment:
			rr = "^#"+key+"\s*=.*$"
		else:
			rr = "^"+key+"\s*=.*$"
		index = self.file._find(rr,MatchMode.Pattern,
				startLineno=r[0]+1,endLineno=r[1])
		if index != -1:
			return r[0],index
 
		#先查找#‘空格’key的值，可宽容空格 
		if has_comment:
			rr = "^\s*#?\s*"+key+"\s*=.*$"
		else:
			rr = "^\s*"+key+"\s*=.*$"
		index = self.file._find(rr,MatchMode.Pattern,
				startLineno=r[0]+1,endLineno=r[1])		
		return r[0],index
	
	def _find_session(self,session):
		s = self.file._find("^\s*\["+session+"\]\s*$",MatchMode.Pattern)
		if s == -1:
			return (-1,-1)
		e = self.file._find("^\s*\[.+\]\s*$",MatchMode.Pattern,startLineno=s+1)
		return (s,e)
	
	def sessions(self):
		rr = []
		for l in self.file.lines:
			if re.match("^\s*\[.+\]\s*$",l):
				rr.append(l.strip()[1:-1])
		return rr
	

################## unit test ##################
def test_config_file():
	s = """[nova]
nova=gggggggg
    [spice]   
#
# From nova
#
# Maximum value: 65535
#html5proxy_port=6082
# Location of spice HTML5 console proxy, in the form
#html5proxy_base_url=http://127.0.0.1:6082/spice_auto.html
server_listen=127.0.0.1
# Number of seconds to wait for an SR to settle if the VDI does not exist when
nova=xxx"""
	p = os.path.dirname(__file__) + os.path.sep + "test2.txt"
	f = open(p,"w+t")
	f.write(s)
	f.close()
	t = config_file(p)
	rrr = t.sessions()
	assert len(rrr) == 2
	assert rrr[0] == "nova"
	assert rrr[1] == "spice"
	
	assert (-1,-1) == t._find_session("noexist")
	assert (0,2) == t._find_session("nova")
	assert (2,-1) == t._find_session("spice")
	assert (0,1) == t._find_key("nova","nova")
	assert (-1,-1) == t._find_key("nova2","nova")
	assert (0,-1) == t._find_key("nova","html5proxy_base_url")
	assert (2,12) == t._find_key("spice","nova")
	assert (2,9) == t._find_key("spice","html5proxy_base_url")
	assert (2,7) == t._find_key("spice","html5proxy_port")
	assert (2,-1) == t._find_key("spice","html5proxy_port",False)
	assert (2,10) == t._find_key("spice","server_listen")
	os.remove(p)
	s = """[nova]
	v1=3434343
	v2=bbbbbbbbbb
	[default]
	    v1=aaaaaaaaa
	v2=fsdfsdfs"""
	f = open(p,"w+t")
	f.write(s)
	f.close()
	t = config_file(p)
	t.delete("nova","v1")
	t.delete("nova","v22")
	t.update("nova","v2","56sdfasdfsd")
	t.update("nova","v3","vvv333")
	t.update("default","v1","vvv222")
	t.update("default","v4","v4444")
	t.update("default","v5","v4444")
	t.delete("default","v5")
	t.update("newnew","v5","v4444")
	t.save()
	s = """[nova]
v3=vvv333
#	v1=3434343
v2=56sdfasdfsd
[default]
#v5=v4444
v4=v4444
v1=vvv222
v2=fsdfsdfs
[newnew]
v5=v4444"""
	ss = s.splitlines()
	assert utility.equal(ss,t.file.lines)
	os.remove(p)
	
def test_txt():
	p = os.path.dirname(__file__)
	f = open(p+"/test1.txt","w+t")
	for i in range(100):
		value = "this is a test" + str(i) + "\n"
		f.write(value)
	f.close()
	assert os.path.exists(p+"/test1.txt")
	t = txt_file(p+"/test1.txt")
	assert 100 == len(t.lines)
	for i in range(100): 
		assert t.lines[i] == "this is a test" + str(i)  
		assert i == t._find("test"+str(i),MatchMode.Any)
		assert i == t._find("test"+str(i),MatchMode.EndPos)
		assert -1 == t._find("test"+str(i),MatchMode.StartPos)
		assert -1 == t._find("test",MatchMode.EndPos)
		assert i == t._find("this is a test"+str(i),MatchMode.EndPos)
		assert i == t._find("^.*"+str(i)+"$",MatchMode.Pattern)
	assert -1 == t._find("noexist",MatchMode.Any)	
	assert 1 == t.delete("test50",MatchMode.Any,True)
	assert -1 == t._find("test50",MatchMode.Any)
	for i in range(50):
		assert t.lines[i] == "this is a test" + str(i) 
	for i in range(50,99):
		assert t.lines[i] == "this is a test" + str(i+1)
		
	assert 0 == t.delete("test50",MatchMode.Any,True)	
	assert 99 == len(t.lines)

	t.delete("this",MatchMode.StartPos,False)
	assert 0 == len(t.lines)
	
	for i in range(10):
		t.insert("value" + str(i))
	t.insert("value-1","value0")
	t.save()
	
	f = open(p+"/test1.txt","r+t")
	ii = -1
	for l in f.readlines():
		if ii == 9:
			assert l == "value"+str(ii)
		else:
			assert l == "value"+str(ii)+"\n"
		ii+=1
	f.close()
	
	for i in range(-1,10):
		t.update("update"+str(i),"value"+str(i))
	t.save()
	
	f = open(p+"/test1.txt","r+t")
	ii = -1
	
	#print(f.read())
	#f.seek(0)
	for l in f.readlines(): 
		if ii == 9:
			assert l == "update"+str(ii)
		else:
			assert l == "update"+str(ii)+"\n"
		ii+=1
	f.close()
	
	t.delete("update",deleteOne=False)
	assert 0 == len(t.lines)
	t.insert("  \t  value   \t")
	assert 0 == t._find("value",MatchMode.StartPos)
	assert 0 == t._find("value",MatchMode.EndPos)
	
	os.remove(p+"/test1.txt")

def test_nova():
	sss = """[DEFAULT]

#
# From nova.conf
# * A list of JSON values which describe the aliases. For example:
#
#     pci_alias = {
#       "name": "QuickAssist",
#       "product_id": "0443",
#       "vendor_id": "8086",
#       "device_type": "type-PCI"
#     }
#
#   defines an alias for the Intel QuickAssist card. (multi valued). Valid key
#   values are :
#
#   * "name": Name of the PCI alias.
#   * "product_id": Product ID of the device in hexadecimal.
#   * "vendor_id": Vendor ID of the device in hexadecimal.
#   * "device_type": Type of PCI device. Valid values are: "type-PCI",
#     "type-PF" and "type-VF".
#  (multi valued)
#pci_alias ="""
	p = os.path.dirname(__file__) + os.path.sep + "test3.txt"
	f = open(p,"w+t")
	f.write(sss)
	f.close()
	t = config_file(p)
	t.update("DEFAULT","pci_alias","abc1234546564")
	t.save()
	sss2 = """[DEFAULT]

#
# From nova.conf
# * A list of JSON values which describe the aliases. For example:
#
#     pci_alias = {
#       "name": "QuickAssist",
#       "product_id": "0443",
#       "vendor_id": "8086",
#       "device_type": "type-PCI"
#     }
#
#   defines an alias for the Intel QuickAssist card. (multi valued). Valid key
#   values are :
#
#   * "name": Name of the PCI alias.
#   * "product_id": Product ID of the device in hexadecimal.
#   * "vendor_id": Vendor ID of the device in hexadecimal.
#   * "device_type": Type of PCI device. Valid values are: "type-PCI",
#     "type-PF" and "type-VF".
#  (multi valued)
pci_alias=abc1234546564"""
	f = open(p,"r")
	sss3=f.read()
	f.close()
	assert sss3 == sss2
	os.remove(p)
	
	
if __name__ == '__main__':
	import utility
	utility.run_tests()
	
	