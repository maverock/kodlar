#!/usr/bin/env python

import argparse
import subprocess
import json
from pprint import pprint
DnsName=""
IpAdress=""
InstanceId=""
DeletedIp=""
#data=subprocess.check_output('aws ec2 run-instances --image-id ami-0e7d3164 --count 1 --instance-type c3.2xlarge --key-name developer --security-group-ids sg-61111f04 --subnet-id subnet-ffa20088'.split())


with open('/etc/salt/master.d/groups.conf', 'r') as file:
    data = file.readlines()

for x in range(len(data)):
    SplittedData=data[x].split(',')
    ChangedLine=""
    if SplittedData[0].strip()[:5]=="storm" or SplittedData[0].strip()[:5]=="super":
	for t in range(len(SplittedData)-2):
	    ChangedLine=ChangedLine+SplittedData[t]+','
	ChangedLine=ChangedLine+SplittedData[len(SplittedData)-2].replace("\'","").replace("\n","")
	DeletedIp=SplittedData[len(SplittedData)-1].replace("\'","").replace("\n","")
	ChangedLine=ChangedLine+"\'"+"\n"
	data[x]=ChangedLine

with open("/etc/salt/master.d/instanceid.conf", "r") as file:
    instancedata= file.readlines()
#d=
if DeletedIp==instancedata[len(instancedata)-1].split(':')[0]: 
    terminateid=instancedata[len(instancedata)-1].split(':')[1]
    instancedata[len(instancedata)-1]=""
    with open('/etc/salt/master.d/groups.conf', 'w') as file:
    	file.writelines( data )
    with open('/etc/salt/master.d/instanceid.conf', 'w') as file:
	file.writelines(instancedata)

    terminatecommand="aws ec2 terminate-instances --region us-east-1 --instance-id "+terminateid
    print terminatecommand
    forlog=subprocess.check_output(terminatecommand.split())
    with open("/deneme.log", "a") as myfile:
        myfile.write(forlog)

else:
    print "Bir sorun var"