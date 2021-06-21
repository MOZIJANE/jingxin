#!/bin/sh
# auth: ives

HASJOB=0
if [ $# == 1 ] ; then
	if [ "$1" == "job" ] ; then
		HASJOB=1
	else
		echo "invalid param: $1"
		exit 1
	fi
fi


ROOT=$(cd $(dirname $0); pwd)
PY_VER=$(python3 --version | awk '{print $2}' | tr '.' ' ' | awk '{print $1 $2}')

COMPILE_FILE="assembleWeb mqtt setup"
DSTNAME=mesWeb
OTHER_FILE="mes.bat default.ini ie32 ie64"

if [ $HASJOB == 1 ] ; then
	DSTNAME=mesAssemble1
	COMPILE_FILE="mesAssemble1 mqtt setup mesApi"
	OTHER_FILE="assemble1.bat default.ini ie32 ie64"
fi

function compile(){
	for f in $COMPILE_FILE ; do
		python3 -m py_compile $f.py
		if [ $? != 0 ] ; then
			echo -e "\033[31mcompile ${f} failed!\033[0m"
			exit 1
		else
			echo -e "\033[32mcompile ${f} succeed.\033[0m"
		fi
	done
}

function pack(){
	cd $ROOT
	rm -rf $DSTNAME
	mkdir -p $DSTNAME

	for f in $COMPILE_FILE ; do
		mv __pycache__/$f.cpython-${PY_VER}.pyc $DSTNAME/$f.pyc
	done

	for f in $OTHER_FILE ; do
		cp -r $f $DSTNAME/
	done

	rm -rf $DSTNAME.tar.gz
	tar -zcf $DSTNAME.tar.gz $DSTNAME/*
	if [ $? != 0 ] ; then
		echo -e "\033[31mpack ${DSTNAME} failed!\033[0m"
		exit 1
	else
		echo -e "\033[32mpack ${DSTNAME} succeed.\033[0m"
	fi
	rm -rf $DSTNAME
}


compile
pack

