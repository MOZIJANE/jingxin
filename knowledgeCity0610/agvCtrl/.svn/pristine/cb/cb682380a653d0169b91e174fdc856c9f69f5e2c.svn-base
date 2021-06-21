import os,sys
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__) 
import math
import counter
#import cwraper
#from ctypes import *  
#	
#class c_result(Structure):
#	_fields_ = []
#	_fields_.append(("count",c_int))	
#	_fields_.append(("weights",POINTER(c_float)))		
#	_fields_.append(("paths",POINTER(POINTER(c_int))))		
# 	
#if sys.platform == "win32":
#	dllName = os.path.dirname(__file__)+r"\route.dll" 
#else:
#	dllName = os.path.abspath(os.path.dirname(__file__))+ "/libroute.so"  
#dll = cwraper.load(dllName)  
#
#cwraper.function(dll,"create_map",c_int,c_void_p)
#cwraper.function(dll,"free_map",c_void_p)
#cwraper.function(dll,"add_line",(c_void_p,c_int,c_int,c_float))
#cwraper.function(dll,"print_result",POINTER(c_result))
#cwraper.function(dll,"free_result",POINTER(c_result))
#cwraper.function(dll,"get_paths",(c_void_p,c_int,c_int,c_int,POINTER(c_result)))
#
#
##查找点与点之间的所有路径 [[w1,[LM1,LM2]],...[w2,[LM1,LM2]]]
#def getAllPaths(map,startPos,endPos,stopCount=sys.maxsize,lines=None,oplines=None,exlines=None):
#	_,startPos = _decodeLoc(startPos)
#	_,endPos = _decodeLoc(endPos)  
#	c = counter.counter()
#	m = _createMap(map,lines=lines,oplines=oplines,exlines=exlines)
#	c.check()
#	
#	result = c_result() 
#	get_paths(m,map.index(startPos),map.index(endPos),stopCount,pointer(result))
#	c.check()
#	free_map(m) 
#	return _getResult(map,result)
#	
#
#def _createMap(map,lines=None,oplines=None,exlines=None): 
#	m = create_map(len(map.positions)) 
#	for pos in map.positions:
#		for line in pos.nextLines:
#			add_line(m,line.startPos.index,line.endPos.index,line.length) 
#	return m
#
#
#def _decodeLoc(loc):
#	index = loc.find(".")
#	if index == -1:
#		return "",loc
#	return loc[0:index],loc[index+1:]
#
#
#def _getResult(map,r):
#	paths = []
#	weights = []
#	for i in range(r.count):
#		weights.append(r.weights[i])
#		pp = [] 
#		k = 0
#		while r.paths[i][k] != -1: 
#			pp.append(map.getPosByIndex(r.paths[i][k]).name)
#			k+=1
#		paths.append(pp) 
#	free_result(r)  
#	return sorted(zip(weights,paths))
#	
#
#def test(mapId,startPos,endPos,count=100):
#	import mapMgr 
#	map = mapMgr.mapInfo.load(mapId)   
#	#map.show()
#	c = counter.counter()
#	ret = getAllPaths(map,startPos,endPos,count)
#	print("cpp",[p[0] for p in ret])
#	#print("cpp",[p[1] for p in ret])
#	c.check()
#	
#	ret = map.getAllPaths(startPos,endPos,count)
#	print("py",[p[0] for p in ret])
#	#print("py",[p[1] for p in ret])
#	c.check() 
#	
##[00] _func() at agvControl.py:820 used 320 ms
##[INFO ] 2020-01-03 16:37:30.041: Begin: AGV07 move from big.AP227 to big.AP240 by paths: [('big', ['AP227', 'LM234', 'LM915', 'LM916', 'LM866', 'LM784', 'LM241', 'LM242', 'LM243', 'LM244', 'AP240'])] task: a2e12964-2b46-40c2-9ddd-e216b883148a timeout 60000 used 320 ms
##mock: AGV02 finish move to big.LM915
##mock: AGV05 finish move to big.LM243
##mock: AGV01 finish move to big.LM784
##[00] rearrange() at agvControl.py:593 used 22899 ms
##[WARN ] 2020-01-03 16:37:52.436: AGV04 can't find new path from LM230 to LM134 old path LM230->LM920,LM920->LM126,LM126->LM110,LM110->LM112,LM112->LM108,LM108->LM780,LM780->LM107,LM107->LM137,LM137->LM136,LM136->LM135,LM135->LM134 ,used: 22899 ms
##[DEBUG] 2020-01-03 16:37:53.262: agvInfo: AGV05 big.LM244 move to big.LM242 ,taskId 5b57292e-1dd7-4848-b58f-c0a91c2ac80fmock: AGV05 start -> LM242
#	
#
#if __name__ == "__main__":
#	#test("test430","LM25","LM28") 
#	test("big","LM300","LM301") 
#	assert 0

#Dijkstra算法是典型的最短路径算法 
#http://www.cnblogs.com/hanahimi/p/4692638.html 
#grap = {1:{1:0,    2:1,    3:12},
#     2:{2:0,    3:9,    4:3},
#     3:{3:0,    5:5},
#     4:{3:4,    4:0,    5:13,   6:15},
#     5:{5:0,    6:4},
#     6:{6:0}}
def dijkstra(graph, startPos):
	dis = dict((k, [sys.maxsize,[]]) for k in graph)
	dis[startPos][0] = 0
	dis[startPos][1].append(startPos)
	
	minv = startPos
	book = set()
	
	while len(book) < len(graph):
		book.add(minv)					 							# 确定当期顶点的距离
		for w in graph[minv]:										# 以当前点的中心向外扩散
			if dis[minv][0] + graph[minv][w] < dis[w][0]:			# 如果从当前点扩展到某一点的距离小与已知最短距离      
				dis[w][0] = dis[minv][0] + graph[minv][w]			# 对已知距离进行更新
				dis[w][1] = dis[minv][1][:]
				dis[w][1].append(w)

		min = sys.maxsize
		for v in dis:												#从剩下的未确定点中选择最小距离点作为新的扩散点
			if v in book: 
				continue
			if dis[v][0] < min:
				min = dis[v][0]
				minv = v
		if min == sys.maxsize:
			break
			
	for d in dis:
		if dis[d][0] == sys.maxsize:
			dis[d] = (None,[])
	return dis 
	

def distance(p1,p2):
	return math.sqrt(math.pow((p1[0]-p2[0]),2) + math.pow(p1[1]-p2[1],2))
 
 

##################### unit test #####################
def test_dijkstra():
	G = {"1":{"1":0,    "2":1,    "3":12},
		 "2":{"2":0,    "3":9,    "4":3},
		 "3":{"3":0,    "5":5},
		 "4":{"3":4,    "4":0,    "5":13,   "6":15},
		 "5":{"5":0,    "6":4},
		 "6":{"6":0}}
	assert 13, ['4', '3', '5', '6'] == dijkstra(G,"4")["6"]
	dis = dijkstra(G,"1")
	assert 13,['1', '2', '4', '3', '5'] == dis["5"]

	assert  ['1', '2', '4', '3', '5', '6'] == dis["6"][1]
	assert  17  == dis["6"][0]
	assert {"1": 0, "2": 1, "3": 8, "4": 4, "5": 13, "6": 17} == dict((x,dis[x][0]) for x in dijkstra(G,"1")) 
	assert {"1": None, "2": None, "3": 4, "4": 0, "5": 9, "6": 13} == dict((x,dijkstra(G,"4")[x][0]) for x in dijkstra(G,"4"))
	assert {"1": None, "2": None, "3": None, "4": None, "5": None, "6": 0} == dict((x,dijkstra(G,"6")[x][0]) for x in dijkstra(G,"6"))
	 

if __name__ == "__main__":
	import utility
	utility.run_tests()
