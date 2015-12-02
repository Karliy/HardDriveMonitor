#!/usr/bin/python
#_*_ coding:utf-8 _*_
import os
import smtplib
from email.mime.text import MIMEText
import re
import time

def send_mail(mailfrom,maillist,sub,content):
	msg = MIMEText(content,_subtype='plain',_charset='utf-8')
	msg['Subject'] = sub
	msg['From'] = mailfrom
	msg['to'] = ";".join(maillist)
	try:
		server = smtplib.SMTP()
#		server.set_debuglevel(1)
		server.connect(mail_smtp_server)
		server.login(login_mail_user,login_mail_passwd)
		server.sendmail(mailfrom,maillist, msg.as_string())
		server.close()
		return True
	except Exception, e:
		print str(e)
		return False

def hp_smart_array(cmdpath,ERROR_TAG):
	raid_card_info=os.popen(cmdpath+' ctrl all show').read() 
	raid_card_slot=re.findall('[sS]lot\s(\d)',raid_card_info)
	if len(raid_card_slot)==0:
		print "No raid card found! exit.."
		exit()

	for slotid in range(0,len(raid_card_slot)):
		get_raid_card_status_cmd="%s ctrl slot=%s show status"%(cmdpath,raid_card_slot[slotid])
		get_pd_status_cmd="%s ctrl slot=%s pd all show status"%(cmdpath,raid_card_slot[slotid])
		get_raid_card_status=os.popen(get_raid_card_status_cmd).read()
		check_raid_card_status=re.findall('[Ff][Aa][Ii][Ll]',get_raid_card_status)
		if len(check_raid_card_status)!=0:
			ERROR_TAG=1
		get_pd_status=os.popen(get_pd_status_cmd).read()
		check_pd_status=re.findall('[Ff][Aa][Ii][Ll]',get_pd_status)
		if len(check_pd_status)!=0:
			ERROR_TAG=1
		file=open(LOGFILE,'a')
		file.write("\n===== 第 "+raid_card_slot[slotid]+" 个槽位的RAID卡=====")
		file.write("\nRAID卡状态:")
		file.write(os.popen(get_raid_card_status_cmd).read())
		file.write("硬盘状态:")
		file.write(os.popen(get_pd_status_cmd).read())
		file.write("详细信息:")
		file.write(os.popen("%s ctrl slot=%s show config"%(cmdpath,raid_card_slot[slotid])).read())
		file.write(os.popen("%s ctrl slot=%s show"%(cmdpath,raid_card_slot[slotid])).read())
		file.close()	
	return ERROR_TAG
def lsi_megaraid(cmdpath,ERROR_TAG):
	raid_card_info=os.popen(cmdpath+' -PdGetMissing -aALL').read()
	raid_card_missing=re.findall('No(\d)Missing',raid_card_info)
	if len(raid_card_missing)==0:
		display_allinfo=os.popen(cmdpath+' -AdpAllInfo -aALL').read()
		check_Critical_Disks=re.findall('\s.Critical Disks\s*:\s*(\d*)',display_allinfo)
		check_Failed_Disks=re.findall('\s.Failed Disks\s*:\s*(\d*)',display_allinfo)
		if (check_Critical_Disks[0] != "0") or (check_Failed_Disks[0] !="0"):
			ERROR_TAG=1
			file=open(LOGFILE,'a')
			file.write("存在坏盘或者坏块的硬盘数量如下：")
			file.write("\n坏盘个数为 %s 个"%check_Failed_Disks[0])
			file.write("\n存在坏块的硬盘个数为 %s 个"%check_Critical_Disks[0])
			file.write("\n注意：坏块硬盘的个数统计中可能包含坏块个数！")
			file.write("\n\n详情：")
			file.close()
			pd_list_info=os.popen(cmdpath+' -PDList -aALL').read()
			display_Predictive_Failure_Count=re.findall('Predictive Failure Count.*',pd_list_info)
			for slot in range(0,len(display_Predictive_Failure_Count)):
				check_Predictive_Failure_Count=re.findall('(\d+)',display_Predictive_Failure_Count[slot])
				if check_Predictive_Failure_Count[0] !="0":
					file=open(LOGFILE,'a')
					file.write("\n第%s槽位的硬盘有坏块，坏块个数为:%s"%(slot,check_Predictive_Failure_Count[0]))
					file.close()
			file=open(LOGFILE,'a')
			file.write("\n使用 /bin/MegaCli64 -PDList -aALL命令查看硬盘详细状态。")
		else:
			file=open(LOGFILE,'a')
			file.write("RAID 健康状态正常。")
			file.write("\n\n详细信息如下:\n")
			file.write(os.popen(cmdpath+' -AdpAllInfo -aALL').read())
			file.close()
			
	else:
		ERROR_TAG=1
		file=open(LOGFILE,'a')
		file.write("注意：RAID卡存在未识别的硬盘！")
		file.write("\n您可以使用 /bin/MegaCli64 -PdGetMissing -aALL查看详细信息。")
		file.close()
	return ERROR_TAG
if __name__ == '__main__':
	ERROR_TAG=0
	LOGFILE='/tmp/diskcheck.log'
	file=open(LOGFILE,'w')
	file.write("Script Running Time: "+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'\n\n')
	file.write("IP Address:"+'\n')
	file.write(os.popen("/sbin/ifconfig|grep 'inet addr'").read())
	file.close()
'''eg：
	mail_from='report@126.com'
	mail_to=['abc@126.com','cde@163.com']
	mail_smtp_server="smtp.126.com"
	login_mail_user="report"
	login_mail_passwd="4yRmcn1fMBq"
	login_mail_postfix="126.com"
	lspci_info=os.popen("/sbin/lspci").read()
'''
	mail_from=''
	mail_to=['','']
	mail_smtp_server=""
	login_mail_user=""
	login_mail_passwd=""
	login_mail_postfix=""

#if raid bus controller is MegaRAID
	if len(re.findall('[Mm][Ee][Gg][Aa][Rr][Aa][Ii][Dd]',lspci_info))!=0:
		if os.path.isfile('/bin/MegaCli64'):
			ERROR_TAG=lsi_megaraid('/bin/MegaCli64',ERROR_TAG)
		else:
			print "Please install Megacli cli tools!"
#elif raid bus controller is HP Smart Array
	elif len(re.findall('RAID(\s\w*){2}\:\DHewlett',lspci_info))!=0:
		if os.path.isfile('/usr/sbin/hpssacli'):
			ERROR_TAG=hp_smart_array('/usr/sbin/hpssacli',ERROR_TAG)
		elif os.path.isfile('/usr/sbin/hpacucli'):
			ERROR_TAG=hp_smart_array('/usr/sbin/hpacucli',ERROR_TAG)
		else:
			print "Please install hpssacli or hpacucli tools!"
			exit()
	else:
		print "This Script not support this RAID bus controller!"
		print os.popen("/sbin/lspci|grep -i raid").read()
		exit()

	print os.popen('cat '+LOGFILE).read()
	if ERROR_TAG==1:
		if send_mail(mail_from,mail_to,"服务器磁盘检查告警邮件",os.popen('cat '+LOGFILE).read()):
			print 'Mail Send Success!'
		else:
			print 'Mail Send Error!'
	else:
		print "硬盘状态检查正常 ~ ^.^ ~"
