# coding: utf-8
# author: pengshuqin
# date: 2019-04-02
# desc: roslaunch

import os
import sys
import setup
if __name__ == '__main__':
	setup.setCurPath(__file__)
import shell
import log


#  - filename + launch args
#  - package + relative-filename + launch args
#packetName,fileName 
def launch(*param,**params):
	import roslaunch
	uuid = roslaunch.rlutil.get_or_generate_uuid(None,True)
	roslaunch.configure_logging(uuid)
	t = roslaunch.rlutil.resolve_launch_arguments(param)[0]
	cli = []
	for key in params.keys():
		cli.append("%s:=%s"%(key, params[key]))
	t = [(t,cli)] if cli != [] else [t]
	parent = roslaunch.parent.ROSLaunchParent(uuid, t)
	parent.start()
	return parent
	

#等于rosrun 
def run(pkgName,nodeName,**params):
	cmd = "rosrun " + pkgName + " " + nodeName
	for k in params:
		cmd += " " + str(k) + "=" + str(params[k])
	ret = shell.run_cmd2(cmd)
	if not ret[1] or ret[0].find("Check failed") != -1:
		log.warning(ret[0])
		return ret[0],False
	else:
		log.info(ret[0])
	return ret[0],True
	
	
def rviz(cfgFilePath,fixFrame=None):
	cmd = "-d " + cfgFilePath 
	if fixFrame:
		cmd += " -f " + fixFrame
	shell.run_cmd2("rviz " + cmd)
	

###################### UNIT TEST ########################
def test_launch():
	la1 = launch("/opt/ros/melodic/share/amcl/examples/amcl_diff.launch")
	la2 = launch("cartographer_ros","demo_backpack_2d.launch",bag_filename="/home/pengshuqin/Downloads/cartographer_paper_deutsches_museum.bag",use_sim_time=False)
	import time
	time.sleep(2)
	la1.shutdown()
	la2.shutdown()
	
if __name__ == "__main__":
	test_launch()
