#!/bin/bash

current_path=`pwd`
mypwdpath=$(cd "$(dirname "$0")"; pwd)
cd $mypwdpath

install_hp(){
    yum install -y --nogpgcheck "$mypwdpath/hpacucli-9.30-15.0.x86_64.rpm"
    if [ $? = 0  ];then
        echo "HP Smart Array cmd tools install ok!" 
    else
        echo "HP Smart Array cmd tools install failed ! please check!!!"
    fi
}
install_hp_dl380_gen8(){
    rpm -ivh "$mypwdpath/hpssacli-2.0-23.0.x86_64.rpm"
    if [ $? = 0  ];then
        echo "HP Smart Storage Administrator CLI install ok!" 
    else
        echo "HP Smart Storage Administrator CLI install failed ! please check!!!"
    fi



}
install_mpt(){
    \cp -f "$mypwdpath/lsiutil.x86_64" /bin
    if [ $? = 0  ];then
        echo "LSI MPT cmd tools install ok!" 
    else
        echo "LSI MPT cmd tools install failed ! please check!!!"
    fi 
}

install_Mega(){
    rpm -ivh $mypwdpath/Lib_Utils-1.00-09.noarch.rpm 
    rpm -ivh $mypwdpath/MegaCli-8.04.07-1.noarch.rpm
    if [ $? = 0  ];then
        echo "MegaRAID cmd tools install ok!" 
    else
        echo "MegaRAID cmd tools install failed ! please check!!!"
    fi 
    \cp -f "/opt/MegaRAID/MegaCli/MegaCli64" /bin
}

check_raid_type(){
    lspci |grep "MPT"|grep "LSI" > /dev/null
    if [ $? = 0  ];then
        install_mpt
    fi

    lspci |grep -iE "MegaRAID|MegaSAS" > /dev/null
    if [ $? = 0  ];then
        install_Mega
    fi

    lspci |grep -Ei "ProLiant|Hewlett-Packard|Hewlett_packard" > /dev/null
    if [ $? = 0  ];then
        dmidecode|grep "Product Name"|grep -i "DL380p"|grep -i "gen8" >/dev/null
        if [ $? = 0  ];then
            install_hp_dl380_gen8
        else
            install_hp
        fi
    fi

}




check_raid_type
