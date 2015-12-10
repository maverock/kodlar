#!/usr/bin/env python

import argparse
import subprocess
import json
from pprint import pprint
import requests
import datetime
Supervisor_Count=0
System_Under_Stres=0
Last_Supervisor_Add=0
Wait_Until=0
More_Than_Need=0

def LoadAverage():
    Deger=""
    Toplam=0
    api_url= Url_Builder()
    r = requests.get(api_url)
    data = json.loads(r.text)
    LineCount=len(data)
    for x in data :
	for t in xrange(len(x['datapoints'])-1,-1,-1):
	    if x['datapoints'][t][0] is not None :
		Deger=x['datapoints'][t][0]
		Toplam=Toplam+Deger
		break
	#print x['target'],Deger
    return Toplam/LineCount

def Url_Builder():
    Ips=[]
    Init="https://graphite.8digits.com/render?width=400&from=-4minutes&until=now&height=250&hideLegend=true&tz=Europe%2FIstanbul"
    InitEnd="&title=Supervisor%20Load&_uniq=0.34630449186079204&format=json"
    IpBegin="&target=servers.ip-"
    IpEnd=".loadavg.01"
    Url=""
    with open('/etc/salt/master.d/instanceid.conf', 'r') as file:
	data = file.readlines()
    Url=Url+Init
    for x in range(len(data)):
	Url=Url+IpBegin+data[x].split(':')[0].replace(".","-")+IpEnd
    Url=Url+InitEnd
    return Url


def Log( s ):
    with open("/var/log/birim/controller.log", "a") as myfile:
	newline=str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))+"  "+str(s)+"\n"
	myfile.write(newline)

def ReadConfig():
    with open('/home/admin/birim_kodlar/runtime.conf', 'r') as file:
	configdata = file.readlines()
    global Supervisor_Count,System_Under_Stres,Last_Supervisor_Add,Wait_Until,More_Than_Need
    Supervisor_Count=configdata[0].split("=")[1].strip()
    System_Under_Stres=configdata[1].split("=")[1].strip()
    Last_Supervisor_Add=configdata[2].split("=")[1].strip()
    Wait_Until=configdata[3].split("=")[1].strip()
    More_Than_Need=configdata[4].split("=")[1].strip()

def WriteConfig():
    global Supervisor_Count,System_Under_Stres,Last_Supervisor_Add,Wait_Until,More_Than_Need
    with open('/home/admin/birim_kodlar/runtime.conf', 'w') as file:
        file.write("Supervisor_Count="+str(Supervisor_Count)+"\n" )
	file.write("System_Under_Stres="+str(System_Under_Stres)+"\n")
	file.write("Last_Supervisor_Add="+str(Last_Supervisor_Add)+"\n")
	file.write("Wait_Until="+str(Wait_Until)+"\n")
	file.write("More_Than_Need="+str(More_Than_Need)+"\n")
	file.close()

def Control():
    global Supervisor_Count,System_Under_Stres,Last_Supervisor_Add,Wait_Until,More_Than_Need
    if Wait_Until>datetime.datetime.now().strftime("%Y-%m-%d %H:%M"):
	Log("Bekleme suresi etkin")
	return
#########Sistem stres altinda
    if LoadAverage() > 10 :
	System_Under_Stres=int(System_Under_Stres)+1
	Log("Mevcut Yuk Sistem Icin Fazla= "+ str(LoadAverage()))
	WriteConfig()
#########Supervisor sayisi fazla
    if LoadAverage() < 5 :
	More_Than_Need=int(More_Than_Need)+1
	Log("Supervisor sayisi suan icin fazla ortalama yuk = "+str(LoadAverage())+"	gerceklesme sayisi "+str(More_Than_Need))
	WriteConfig()
#########Sistem sorunsuz calisiyor
    if LoadAverage() > 5 and LoadAverage() < 10 :
	System_Under_Stres=0
	More_Than_Need=0
	Log("Suan sistem sorunsuz calismakta= "+ str(LoadAverage())+"	tum sayaclar sifirlandi")
	WriteConfig()


#Gonder="Mevcut yuk="+str(LoadAverage())
#Log(Gonder)
ReadConfig()
#print Supervisor_Count,Wait_Until
#print Url_Builder()
Control()