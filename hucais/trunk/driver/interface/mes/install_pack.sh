#!/bin/sh
# auth: ives

ROOT=$(cd $(dirname $0); pwd)
PY_VER=$(python3 --version | awk '{print $2}' | tr '.' ' ' | awk '{print $1 $2}')

COMPILE_FILE="main_pack mqtt uiMesPack main_assemble uiMesAssemble mongodb"
DSTNAME=mesPack
OTHER_FILE="scadaPack.bat scadaAssemble3.bat default.ini"

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
		cp $f $DSTNAME/
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

