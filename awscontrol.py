#!/usr/bin/env python

import argparse
import subprocess
import json
from pprint import pprint
import requests

def loadaverage():
    Deger=""
    Toplam=0
    api_url = "https://graphite.8digits.com/render?width=400&from=-4minutes&until=now&height=250&hideLegend=true&tz=Europe%2FIstanbul&target=servers.ip-10-0-0-37.loadavg.01&target=servers.ip-10-0-0-29.loadavg.01&target=servers.ip-10-0-0-73.loadavg.01&target=servers.ip-10-0-0-36.loadavg.01&target=servers.ip-10-0-0-38.loadavg.01&target=servers.ip-10-0-0-34.loadavg.01&target=servers.ip-10-0-0-35.loadavg.01&title=Supervisor%20Load&_uniq=0.34630449186079204&format=json"
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

print loadaverage()