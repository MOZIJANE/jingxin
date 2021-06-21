#coding=utf-8 
# ycat			 2015/04/10      create
# 用于二进制的封装 
import sys,os
import operator
import struct
import enum 
import enhance
import binascii


class EndianType(enum.Enum):
	BigEndian = 0
	LittleEndian = 1

def crc16(data):
	a = 0xFFFF
	b = 0xA001
	for byte in data:
		a ^= byte#ord(byte)
		for i in range(8):
			last = a % 2
			a >>= 1
			if last == 1:
				a ^= b
	return a&0xFFFF 
	

def checksum(buf,len=2):
	v = 0
	if len == 1:
		v = 0x100
	elif len == 2:
		v = 0x10000	
	elif len == 4:
		v = 0x100000000
	else:
		assert 0 
	return sum(buf)%v

class inBuffer:
	#@common.check(buffer=[])
	def __init__(self,buffer,order=EndianType.BigEndian):
		self._len = len(buffer)
		self._buf = bytearray(buffer)
		self._cursor = 0
		self.order = order

	@property
	def len(self):
		return self._len

	@property
	def buf(self):
		return self._buf		
		
	def getChar(self):
		return self.getStr(1)		
	
	def getByte(self):
		return self.getBuf(1)[0]
		
	def getInt8(self):
		return self.getByte() 
	
	def getInt16(self):
		return self._unpack("h",2)
		
	def getUInt16(self):
		return self._unpack("H",2)
		
	def getInt32(self):
		return self._unpack("i",4)
		
	def getUInt32(self):
		return self._unpack("I",4)

	def getFloat(self):
		return self._unpack("f",4) 
		
	def getDouble(self):
		return self._unpack("d",8)		
		
	def getBool(self):
		return self._unpack("?",1)			
		
	def getInt64(self):
		return self._unpack("q",8)			

	def getUInt64(self):
		return self._unpack("Q",8)			
		
	def getStrWithLen(self,codec="utf-8"):
		c = self.getUInt32()
		return self.getStr(c,codec=codec)
		
	def getStr(self,len,codec="utf-8"): 
		return self.getBuf(len).decode(codec)
		
	def getBuf(self,len):
		if self._cursor + len > self.len:
			raise IndexError(self._cursor + len,self.len)
		bb = self._buf[self._cursor:self._cursor+len]
		self._cursor += len 
		return bb
	
	#返回类似这样的一串 "100500000000201510140046"
	def getHexStr(self,len):
		return binascii.hexlify(self.getBuf(len)).decode("utf8")
	
	def _unpack(self,key,len):
		bb = self.getBuf(len)
		if self.order == EndianType.BigEndian:
			bb = bytearray(reversed(bb))  
		return struct.unpack(key,bb)[0]
		
	def get(self,key,buf):
		if self.order == EndianType.BigEndian:
			buf = bytearray(reversed(buf))  
		return struct.unpack(key,buf)[0]
		
	def __str__(self):
		r = "inbuf[%d] "%self.len
		for s in self._buf:
			r+="%02X "%s
		return r.rstrip()
	
	@property
	def remainLen(self):
		return self.len - self._cursor
		
class outBuffer:
	def __init__(self,order=EndianType.BigEndian):
		self._len = 0	
		self._buf = bytearray()
		self.order = order
	
	@staticmethod
	def fromhex():
		return None
	
	@property
	def len(self):
		return len(self._buf)
		
	@property
	def buf(self):
		return self._buf
	
	def setChar(self,value):
		if isinstance(value,str):
			assert len(value) == 1
			self.setStr(value)
		else:
			self._checkRange(value,-128,127)
			self._buf.append(value)
		
	def setBytes(self,value):  
		for b in value:
			self._buf.append(b) 
		
	def setByte(self,value):
		self._checkRange(value,0,255)
		self._buf.append(value)
	
	def setUInt16(self,value):
		self._checkRange(value,0,65535)
		self._pack("H",value)
	
	def setInt16(self,value):
		self._checkRange(value,-32768,32767)	
		self._pack("h",value)
	
	def setUInt32(self,value):
		self._checkRange(value,0,4294967295)
		self._pack("I",value)
	
	def setInt32(self,value):
		self._checkRange(value,-2147483648,2147483647)
		self._pack("i",value)
		
	def setInt64(self,value):
		self._pack("q",value)

	def setUInt64(self,value):
		self._pack("Q",value)
		
	def setFloat(self,value):
		self._pack("f",value)

	def setDouble(self,value):
		self._pack("d",value)			

	def setBool(self,value):
		assert isinstance(value,bool)
		self._pack("?",value)
		
	def setStr(self,value,codec="utf-8"):
		bb = value.encode(codec)
		for b in bb:
			self._buf.append(b)
			
	def setStrWithLen(self,value,codec="utf-8"):
		bb = value.encode(codec)
		self.setUInt32(len(bb))
		for b in bb:
			self._buf.append(b)
		
	def setBuf(self,buf):
		for b in buf:
			self._buf.append(b)
		
	def _pack(self,t,value):
		bb = struct.pack(t,value)
		if self.order == EndianType.BigEndian:
			bb = reversed(bb)	
		self.setBuf(bb)
		
	def _checkRange(self,value,min,max):
		if value < min:
			raise ValueError(value)
		elif value>max:
			raise ValueError(value)
	
	def __str__(self):
		r = "outbuf[%d] "%self.len
		for s in self._buf:
			r+="%02X "%s
		return r.rstrip()
		
def testBuffer():	
	def _testBuffer(order):
		o = outBuffer(order)
		o.setChar('a')
		o.setChar(0x62)
		o.setByte(0xCE)
		o.setByte(0xFF)
		o.setUInt16(65535)
		o.setInt16(-32768)
		o.setUInt32(165535)
		o.setInt32(-132768)
		o.setDouble(165535.12)
		o.setFloat(-132768.12)
		o.setStr("hello world")
		o.setStr("你好，世界")
		o.setBool(False)
		o.setBool(True)
		try:
			o.setUInt16(65535+100)
			assert 0
		except ValueError:
			pass
		#print(o)
		
		i = inBuffer(o.buf,order)
		#print(i)
		assert 'a' == i.getChar()
		assert 'b' == i.getChar()
		assert 0xCE == i.getByte()
		assert 0xFF == i.getByte()
		assert 65535 == i.getUInt16()
		assert -32768 == i.getInt16()
		assert 165535 == i.getUInt32()
		assert -132768 == i.getInt32()
		assert 165535.12 == i.getDouble()
		assert abs(-132768.12 - i.getFloat()) < 0.01
		assert "hello world" == i.getStr(len("hello world"))
		
		assert "你好，世界" == i.getStr(i.remainLen-2)
		assert not i.getBool()
		assert i.getBool()
		
		try:
			i.getBool()
			assert 0
		except IndexError:
			pass
		
		o = outBuffer(order)
		o.setUInt16(0xABCD)
		if order == EndianType.BigEndian: 
			assert "outbuf[2] AB CD" == str(o)
		else:
			assert "outbuf[2] CD AB" == str(o)
			
	_testBuffer(EndianType.BigEndian)
	_testBuffer(EndianType.LittleEndian)
	i = inBuffer([0x11,0x22,0x33,0x44],EndianType.BigEndian)
	assert i.getUInt16() == 0x1122
	i = inBuffer([0x11,0x22,0x33,0x44],EndianType.BigEndian)
	assert i.getUInt32() == 0x11223344
	i = inBuffer([0x11,0x22,0x33,0x44],EndianType.LittleEndian)
	assert i.getUInt16() == 0x2211
	i = inBuffer([0x11,0x22,0x33,0x44],EndianType.LittleEndian)
	assert i.getUInt32() == 0x44332211
	
	b = outBuffer()
	b.setBytes(b"\x01\x03\x04")
	assert b.buf == b"\x01\x03\x04"
	
def testCheckSum():
	b = [0x11,0x22,0x33,0x44,0x55,0x66,0x11,0x22,0x33,0x44,0x55,0x66,0x11,0x22,0x33,0x44,0x55,0x66,0x11,0x22,0x33,0x44,0x55,0x66,0x11,0x22,0x33,0x44,0x55]
	assert 1683 == checksum(b,4)
	assert 147 == checksum(b,1)
	b = [0x27,0x00,0x00,0x00,0x05,0x61,0x64,0x6D,0x69,0x6E,0x00,0x00,0x00,0x20,0x63,0x61,0x32,0x39,0x32,0x34,0x64,0x38,0x36,0x36,0x39,0x31,0x61,0x38,0x39,0x30,0x62,0x64,0x39,0x36,0x61,0x64,0x35,0x65,0x31,0x31,0x36,0x32,0x30,0x63,0x34,0x61]
	assert 0x9205 == crc16(b) 
	
	
if __name__ == '__main__':
	import utility
	utility.run_tests() 
		
