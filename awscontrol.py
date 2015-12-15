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

def AwsMachineTerminate():
    DnsName=""
    IpAdress=""
    InstanceId=""
    DeletedIp=""
    #data=subprocess.check_output('aws ec2 run-instances --image-id ami-0e7d3164 --count 1 --instance-type c3.2xlarge --key-name developer --security-group-ids sg-61111f04 --subnet-id subnet-ffa20088'.split())
    global Supervisor_Count,System_Under_Stres,Last_Supervisor_Add,Wait_Until,More_Than_Need

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
        Log(str(terminateid)+"  id'li makina sistemden cikarildi")    
        WriteConfig()
        ########Yeni supervisor sayilarinin yazilmasi
        #Yeni worker sayilari ve dosyaya yazilmasi
        Supervisor_Count=int(Supervisor_Count)-1
        if Supervisor_Count<6 :
            Metric_Worker=4
            Auto_Worker=(Supervisor_Count*4)-Metric_Worker
        if Supervisor_Count>5 :
            Metric_Worker=6
            Auto_Worker=(Supervisor_Count*4)-Metric_Worker
        print int(Auto_Worker),int(Metric_Worker)
         ####Analytics 
        with open('/etc/8digits/analytics.properties', 'r') as file:
            data = file.readlines()
        for x in range(len(data)):
            SplittedData=data[x].split('=')
            ChangedLine=""
            if SplittedData[0].strip()=="PROD.worker.count":
                ChangedLine="PROD.worker.count="+str(Auto_Worker)+"\n"
                data[x]=ChangedLine
            if SplittedData[0].strip()=="PROD.supervisor.count":
                ChangedLine="PROD.supervisor.count="+str(Supervisor_Count)+"\n"
                data[x]=ChangedLine

        with open('/etc/8digits/analytics.properties', 'w') as file:
            file.writelines( data )
        ######Metric
        with open('/etc/8digits/metrics.properties', 'r') as file:
            data = file.readlines()
        for x in range(len(data)):
            SplittedData=data[x].split('=')
            ChangedLine=""
            if SplittedData[0].strip()=="PROD.worker.count":
                ChangedLine="PROD.worker.count="+str(Metric_Worker)+"\n"
                data[x]=ChangedLine
            if SplittedData[0].strip()=="PROD.supervisor.count":
                ChangedLine="PROD.supervisor.count="+str(Supervisor_Count)+"\n"
                data[x]=ChangedLine
        with open('/etc/8digits/metrics.properties', 'w') as file:
            file.writelines( data )


    else:
        print "Bir sorun var"
    

def AwsMachineCreate():
    global Supervisor_Count,System_Under_Stres,Last_Supervisor_Add,Wait_Until,More_Than_Need
    DnsName=""
    IpAdress=""
    InstanceId=""
    #with open('./sonuc.txt') as data_file:    
    #    data = json.load(data_file)
    data=subprocess.check_output('aws ec2 run-instances --image-id ami-0e7d3164 --count 1 --instance-type c3.2xlarge --key-name developer --security-group-ids sg-61111f04 --subnet-id subnet-ffa20088'.split())
    data = json.loads(data)
    #
    #cl = float(data['Instances']['State']['NetworkInterfaces']['PrivateIpAddresses']['PrivateIpAddress'])
    #print cl
    #pprint(data)
    ################dosyadan kurulum datasini cek

    for instance in data['Instances']:
        DnsName=instance["PrivateDnsName"]
        IpAdress=instance["PrivateIpAddress"]
        InstanceId=instance["InstanceId"]
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
            ChangedLine=ChangedLine+","+IpAdress
	    ChangedLine=ChangedLine+"\'"+"\n"
	    data[x]=ChangedLine
    #print data
    with open('/etc/salt/master.d/groups.conf', 'w') as file:
        file.writelines( data )
    #Yeni worker sayilari ve dosyaya yazilmasi
    Supervisor_Count=int(Supervisor_Count)+1
    if Supervisor_Count<6 :
        Metric_Worker=4
        Auto_Worker=(Supervisor_Count*4)-Metric_Worker
    if Supervisor_Count>5 :
        Metric_Worker=6
        Auto_Worker=(Supervisor_Count*4)-Metric_Worker
    print int(Auto_Worker),int(Metric_Worker)
         ####Analytics 
    with open('/etc/8digits/analytics.properties', 'r') as file:
        data = file.readlines()
    for x in range(len(data)):
        SplittedData=data[x].split('=')
        ChangedLine=""
        if SplittedData[0].strip()=="PROD.worker.count":
            ChangedLine="PROD.worker.count="+str(Auto_Worker)+"\n"
            data[x]=ChangedLine
        if SplittedData[0].strip()=="PROD.supervisor.count":
            ChangedLine="PROD.supervisor.count="+str(Supervisor_Count)+"\n"
            data[x]=ChangedLine

    with open('/etc/8digits/analytics.properties', 'w') as file:
        file.writelines( data )
        ######Metric
    with open('/etc/8digits/metrics.properties', 'r') as file:
        data = file.readlines()
    for x in range(len(data)):
        SplittedData=data[x].split('=')
        ChangedLine=""
        if SplittedData[0].strip()=="PROD.worker.count":
            ChangedLine="PROD.worker.count="+str(Metric_Worker)+"\n"
            data[x]=ChangedLine
        if SplittedData[0].strip()=="PROD.supervisor.count":
            ChangedLine="PROD.supervisor.count="+str(Supervisor_Count)+"\n"
            data[x]=ChangedLine

    with open('/etc/8digits/metrics.properties', 'w') as file:
        file.writelines( data )

 
    #instanceid dosyasinin yazilmasi
    with open("/etc/salt/master.d/instanceid.conf", "a") as myfile:
        newline=IpAdress+":"+InstanceId+"\n"
        myfile.write(newline)

    Log(str(str(IpAdress)+" adresli "+str(InstanceId)+" makinasi sisteme eklendi")) 
    WriteConfig()


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
	Log("Mevcut Yuk Sistem Icin Fazla= "+ str(LoadAverage())+"      gercekleme sayisi "+str(System_Under_Stres))
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
#AwsMachineTerminate()
AwsMachineCreate()
