#coding=utf-8 
# ycat			2018-10-11      create
# 对动态库进行封装 
import ctypes  
import functools

g_dlls = {}


def include(module):
	pass

def load(dllPath):
	global g_dlls
	if dllPath in g_dlls:
		return g_dlls[dllPath]
	dll = ctypes.CDLL(dllPath)
	g_dlls[dllPath] = dll
	return dll

def _setFuncInfo(dll,funcName,args=(),ret=None):
	f = getattr(dll,funcName)
	f.restype = ret
	if isinstance(args,tuple):
		f.argtypes = args
	else:
		f.argtypes = (args,)
 
# @注册函数的修饰符
def defind(dll,args=(),ret=None):
	def __call(func):
		_setFuncInfo(dll,func.__name__,args,ret)
		return func
	return __call	
	
	
def _bind(func,*param,**params):
	return functools.partial(func,*param,**params)

def _runFunc(dll,funcName,*param,**params):
	return getattr(dll,funcName)(*param,**params)
	
def function(dll,funcName,args=(),ret=None):
	_setFuncInfo(dll,funcName,args,ret)
	import inspect
	s = inspect.stack()[1][0]
	s.f_globals[funcName] = _bind(_runFunc,dll,funcName)


def pointer(obj):
	if hasattr(obj,"contents"):
		return obj
	else:
		return ctypes.pointer(obj)
	
def get(obj):
	if hasattr(obj,"contents"):
		return obj.contents
	else:
		return obj
	
#创建二维数组，返回结构体为 POINTER(POINTER(type))
# POINTER(POINTER(type)) = array2d(c_double,20,2)
def array2d(type,rows,cols):
	array = (ctypes.POINTER(type)*rows)()
	for i in range(rows):
		array[i] = (type*cols)()
	return array
	
	
#ctypes创建的内存不能自动对齐，可以使用如下方法对齐内存
#https://chl0000.iteye.com/blog/1915305 
def alloc_aligned(size, alignment):  
	buf_size = size + (alignment - 1)  
	#先使用bytearray函数分配一块内存  
	raw_memory = bytearray(buf_size)  
	#然后从raw_memory创建一个ctypes对象  
	ctypes_raw_type = (ctypes.c_char * buf_size)  
	ctypes_raw_memory = ctypes_raw_type.from_buffer(raw_memory)  
	#通过ctypes对象的addressof获得内存指针的值  
	raw_address = ctypes.addressof(ctypes_raw_memory)  
	offset = raw_address % alignment  
	#通过内存地址可以得出，对齐内存的偏移量  
	offset_to_aligned = (alignment - offset) % alignment  
	ctypes_aligned_type = (ctypes.c_char * (buf_size - offset_to_aligned))  
	#通过内存的偏移量，创建对齐内存的ctype对象  
	ctypes_aligned_memory = ctypes_aligned_type.from_buffer(raw_memory, offset_to_aligned)  
	return ctypes_aligned_memory  
		
	
# defind usage example: 
#@defind(dll,(pf_vector,pf_matrix),POINTER(pf_pdf_gaussian))
#def pf_pdf_gaussian_alloc(x, cx):
#	return dll.pf_pdf_gaussian_alloc(x,cx)

#ctypes支持的原生数据类型如下:                                    
# 注意回调函数不支持结构体做返回值 
# 指针的contents内容id也会变化,不能做key值 
# 
#| ctypes类型     | C 类型                                   | Python 类型                
#| ---------------- | -------------------------------------- | ---------------------------
#| c_char           | char                                   | 1-character string         
#| c_wchar          | wchar_t                                | 1-character unicode string 
#| c_byte           | char                                   | int/long                   
#| c_ubyte          | unsigned char                        	 | int/long                   
#| c_bool           | bool                                   | bool                       
#| c_short          | short                                  | int/long                   
#| c_ushort         | unsigned short                       	 | int/long                   
#| c_int            | int                                    | int/long                   
#| c_uint           | unsigned int                           | int/long                   
#| c_long           | long                                   | int/long                   
#| c_ulong          | unsigned long                        	 | int/long                   
#| c_longlong     	| __int64 or longlong                 	 | int/long                   
#| c_ulonglong   	| unsigned __int64 or unsigned long long | int/long                   
#| c_float          | float                                  | float                      
#| c_double        	| double                                 | float                      
#| c_longdouble 	| long double float                      | float                      
#| c_char_p        	| char *                                 | string or None             
#| c_wchar_p     	| wchar_t *                              | unicode or None            
#| c_void_p        	| void *                                 | int/long or None           
#---------------------------------------------------------------------------------------------  


