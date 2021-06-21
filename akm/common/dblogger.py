#coding=utf-8 
# ycat			 2015/02/09      create
import sys,os
import datetime
import utility
import db
import webutility

#logType:1用户日志，0是系统日志 
def write(user_id,desc,logType,autoCommit = True):	
	db.execute("INSERT INTO r_log(LogTypeID,LogDesc,LogDate,UserID,IP)VALUES(%d,%s,'%s','%s','%s')"%
		(logType,db.escape(desc),utility.now_str(),str(user_id),webutility.get_ip()))
	utility.logger().info(str(user_id) + ": " + str(desc))
	if autoCommit:
		db.commit()

def check_log(user_id,desc,logType,index=0):
	#for unit test to check user log
	ds = db.query("select UserID,LogDesc,logTypeID from r_log WHERE logTypeID=%d ORDER BY LogID Desc" % (logType,))
	for i in range(index+1):
		assert ds.next()
		
	assert ds[0]== str(user_id)
	if ds[1] != desc:
		print("wrong log check:")
		print(ds[1])
		print(desc)

	assert ds[1] == desc
	assert ds[2] == logType
	
def clear_test_log():
	db.execute("DELETE FROM  r_log WHERE IP='unittest'")
	db.commit()
	
#############################	unit test	###########################	
def test_write_log():
	utility.set_is_test(True)
	utility.set_now(datetime.datetime(2014,5,27,12,50,43))
	now1 = utility.now()
	
	db.execute("DELETE FROM r_log WHERE LogDesc like 'test_%'")
	db.commit()

	msg = "test_系统创建啦<啦啦>'\"dfdfd"
	msg2 = "test_系统创建啦<啦啦>'\"dfdfddsfdfsfdsf"	
	write(-1,msg,0)

	check_log(-1,msg,0)
	
	
	utility.set_now(datetime.datetime(2014,1,27,12,50,43))
	now2 = utility.now()
	write(1001,msg2,1)
	check_log(1001,msg2,1)
	
	ds = db.query("SELECT LogTypeID,LogDesc,LogDate,UserID,IP FROM r_log WHERE LogDesc like 'test_%%' ORDER BY LogID ASC")
	assert ds.row_count == 2
	assert ds.next()
	assert ds[0] == 0
	assert ds[1] == msg
	assert ds[2] == now1.strftime("%Y-%m-%d %H:%M:%S")
	assert ds[3] == "-1"
	assert ds[4] == "unittest"
	
	assert ds.next()
	assert ds[0] == 1
	assert ds[1] == msg2
	assert ds[2] == now2.strftime("%Y-%m-%d %H:%M:%S")
	assert ds[3] == "1001"
	assert ds[4] == "unittest"
	
	db.execute("DELETE FROM r_log WHERE LogDesc like 'test_%'")
	db.commit()
	clear_test_log()
	utility.set_now(None)
	
if __name__ == '__main__':
	utility.run_tests()
		