import sys, urllib, json
import urllib.request
import redis
from collections import Counter


HOST = "redis-15449.c228.us-central1-1.gce.cloud.redislabs.com"
PWD = "eqhpmBGXrr4tb3tkRACWDvffctJ0wBTf"
PORT = "15449" 

redis1 = redis.Redis(host = HOST, password = PWD, port = PORT)

print("redis1")


def FindconfirmedCount(conlist,provinceName):
	output = ""
	for item in conlist:
		if item['provinceName'] == provinceName:
			output = item['confirmedCount']
			break
	return output

URL = "https://api.data.gov.hk/v2/filter?q=%7B%22resource%22%3A%22http%3A%2F%2Fwww.chp.gov.hk%2Ffiles%2Fmisc%2Fbuilding_list_eng.csv%22%2C%22section%22%3A1%2C%22format%22%3A%22json%22%7D"

response = urllib.request.urlopen(URL)
content = response.read()
#con = json.loads(content)
#json.dumps()

redis1.set('Buildings',content)

value = json.loads(redis1.get('Buildings'))
district = list()

for item in value:
	district.append(item['District'])


result = Counter(district)
elements = list(result.elements())
most_common = result.most_common()

#print(result)
#print(elements)
print(most_common)
#print(most_common[0][1])

#allList = ""
#form = "&markers=color:blue%7Clabel:S%7c"
#for item in most_common:
#	allList = allList + form + item[0]
#print(allList)



#https://maps.googleapis.com/maps/api/staticmap?
#center=Brooklyn+Bridge,New+York,NY
##&zoom=13
#&size=600x300
#&maptype=roadmap
#&markers=color:blue%7Clabel:S%7C40.702147,-74.015794
#&markers=color:green%7Clabel:G%7C40.711614,-74.012318
#&markers=color:red%7Clabel:C%7C40.718217,-73.998284
#&key=AIzaSyC4PPIxkv1lR7oQDqPNEVbhWwh_SlRAWPU


#https://maps.googleapis.com/maps/api/staticmap?center=Hong+Kong+Island
#&zoom13&size=600x300&maptype=roadmap
#&markers=color:blue%7Clabel:S%7cKellett View Town Houses, 65 Mount Kellett Road
#&markers=color:red%7Clabel:M%7cIsland Shangri-La
#&markers=color:green%7Clabel:E%7cEmerald Garden, 86 Pok Fu Lam Road	
#&key=AIzaSyC4PPIxkv1lR7oQDqPNEVbhWwh_SlRAWPU