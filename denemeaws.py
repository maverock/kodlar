#!/usr/bin/env python

import argparse
import subprocess
import json
from pprint import pprint
DnsName=[]
IpAdress=[]

#data = open('/home/birim/sonuc.txt')
#data = json.loads(data.text)
with open('./sonuc.txt') as data_file:    
    data = json.load(data_file)

#cl = float(data['Instances']['State']['NetworkInterfaces']['PrivateIpAddresses']['PrivateIpAddress'])
#print cl
#pprint(data)
################dosyadan kurulum datasini cek

for instance in data['Instances']:
    DnsName.append(instance["PrivateDnsName"])
    IpAdress.append(instance["PrivateIpAddress"])

############ etc altini oku

with open('/etc/salt/master.d/groups.conf', 'r') as file:
    data = file.readlines()

for x in range(len(data)):
    SplittedData=data[x].split(',')
    ChangedLine=""
    if SplittedData[0].strip()[:5]=="storm" or SplittedData[0].strip()[:5]=="super":
	for t in range(len(SplittedData)-1):
	    ChangedLine=ChangedLine+SplittedData[t]+','
	ChangedLine=ChangedLine+SplittedData[len(SplittedData)-1].replace("\'","").replace("\n","")
	for item in IpAdress:
	    ChangedLine=ChangedLine+","+item
	ChangedLine=ChangedLine+"\'"+"\n"
	data[x]=ChangedLine
#print data
with open('/etc/salt/master.d/groups.conf', 'w') as file:
    file.writelines( data )
