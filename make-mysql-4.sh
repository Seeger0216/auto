#!/bin/bash
set ff=unix
user_check(){
	if [ $(id -u) != 0 ];then
	echo "-------------ERROT:Please use root to execute the script---------------"
	sudo su -
	fi
	}
user_check

apt update
apt install cmake bison libncurses5-dev build-essential -y
if [ $? != 0 ];then
	echo "----------------------------Install error!!!----------------------------"
	exit
fi

cd ~
wget https://dev.mysql.com/get/Downloads/MySQL-5.7/mysql-boost-5.7.18.tar.gz
MYSQL=mysql-boost-5.7.18.tar.gz
if [ ! -f $MYSQL ];then
	echo "----------------------------Please confirm that the MYSQLfile exists!!!----------------------------"
	exit
else
	tar -xzv -f mysql-boost-5.7.18.tar.gz 
	cd mysql-5.7.18/
	cmake -DCMAKE_INSTALL_PREFIX=/usr/local/mysql -DMYSQL_DATADIR=/usr/local/mysql/data -DWITH_BOOST=./boost/boost_1_59_0 -DSYSCONFDIR=/etc -DWITH_INNOBASE_STORAGE_ENGINE=1 -DWITH_PARTITION_STORAGE_ENGINE=1 -DWITH_FEDERATED_STORAGE_ENGINE=1 -DWITH_BLACKHOLE_STORAGE_ENGINE=1 -DWITH_MYISAM_STORAGE_ENGINE=1 -DWITH_MEMORY_STORAGE_ENGINE=1 -DENABLED_LOCAL_INFILE=1 -DWITH_READLINE=1 -DMYSQL_TCP_PORT=3306 -DEXTRA_CHARSETS=all -DDEFAULT_CHARSET=utf8 -DDEFAULT_COLLATION=utf8_general_ci
	make -j 4
	if [ $? != 0 ];then
		echo "----------------------------Install error!!!----------------------------"
		exit
	fi
fi
