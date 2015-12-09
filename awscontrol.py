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

def LoadAverage():
    Deger=""
    Toplam=0
    #api_url = "https://graphite.8digits.com/render?width=400&from=-4minutes&until=now&height=250&hideLegend=true&tz=Europe%2FIstanbul&target=servers.ip-10-0-0-37.loadavg.01&target=servers.ip-10-0-0-29.loadavg.01&target=servers.ip-10-0-0-73.loadavg.01&target=servers.ip-10-0-0-36.loadavg.01&target=servers.ip-10-0-0-38.loadavg.01&target=servers.ip-10-0-0-34.loadavg.01&target=servers.ip-10-0-0-35.loadavg.01&title=Supervisor%20Load&_uniq=0.34630449186079204&format=json"
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
    
    #print "Ortalama=",Toplam/LineCount
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
	data = file.readlines()
    global Supervisor_Count,System_Under_Stres,Last_Supervisor_Add,Wait_Until
    Supervisor_Count=data[0].split("=")[1]
    System_Under_Stres=data[1].split("=")[1]
    Last_Supervisor_Add=data[2].split("=")[1]
    Wait_Until=data[3].split("=")[1]

def Control():
    if Wait_until <> 0 and




Gonder="Mevcut yuk="+str(LoadAverage())
Log(Gonder)
ReadConfig()
print Supervisor_Count,Wait_Until
#print Url_Builder()