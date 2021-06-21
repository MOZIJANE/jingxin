#coding=utf-8
# ycat			2017-08-030	  create
# opencv的操作 
import cv2
import numpy as np 
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)

#按esc(27)退出 
def wait(millisec=0,key=27):
	ret = cv2.waitKey(millisec)
	if ret == key:
		quit()
		return True
	elif isinstance(key,str):
		if ret&0xFF == ord(key) or ret&0xFF == ord(key.upper()):	
			quit()
			return True
	return False

def quit():
	cv2.destroyAllWindows()
	
	
#homography to pose
def H2Pose(H,cameraMatrix):
	count, rvecs, tvecs, normals = cv2.decomposeHomographyMat(H, cameraMatrix)
	rr = []
	tt = []
	for i,t in enumerate(tvecs):
		#if t[2] < 0:
			#把Z轴平移方向为负的去掉 
		#	continue
		#if i != 0:
		#	continue
		rr.append(rvecs[i])
		tt.append(tvecs[i])
	return rr,tt

#计算两点之间的欧式距离  
def distance(m1,m2):
	return np.sqrt(np.sum(np.square(m1-m2)))
		
def testdistance():
	m1,m2 = np.array([1,1]),np.array([0,0])
	d = distance(m1,m2)
	assert abs(d - 1.41) < 0.1
	mm = np.array([[ 1.62409998],[ 6.84702129],[68.663283  ]])
	d = distance(mm,np.zeros(3))
	print(d)
	
	
if __name__ == "__main__":
	testdistance() 
	

	
	
	
	
	
	
	
	
	
	
	
	
	