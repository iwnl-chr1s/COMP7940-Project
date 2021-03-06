import sys, urllib, json
import urllib.request
import redis
import threading
from collections import Counter

global msg 

def main():
	TempRedis = ConnectToRedis()
	#print(FindWorldConfirmedCase(TempRedis,"意大利"))
	#print(FindHkConfiermedCase(TempRedis))
	#print(message("意大利"))
	#FindLocation(TempRedis,"Sai Kung")
	msg = "1"
	print(msg)
	print(testing(TempRedis))

def ConnectToRedis():
	HOST = "redis-15449.c228.us-central1-1.gce.cloud.redislabs.com"
	PWD = "eqhpmBGXrr4tb3tkRACWDvffctJ0wBTf"
	PORT = "15449"
	Tian = "http://api.tianapi.com/txapi/ncovabroad/index?key=4a16ea54595dc82b1fa1c4a483ae1866"
	GovHK = "https://api.data.gov.hk/v2/filter?q=%7B%22resource%22%3A%22http%3A%2F%2Fwww.chp.gov.hk%2Ffiles%2Fmisc%2Fbuilding_list_eng.csv%22%2C%22section%22%3A1%2C%22format%22%3A%22json%22%7D"
	redis1 = redis.Redis(host = HOST, password = PWD, port = PORT)

	resOfTian = urllib.request.urlopen(Tian)
	resOfGovhk = urllib.request.urlopen(GovHK)

	conOfTian = resOfTian.read()
	conOfGovhk = resOfGovhk.read()

	redis1.set('World', conOfTian)
	redis1.set('HK', conOfGovhk)

	return redis1

def FindLocation(redis, testDis):
	content = json.loads(redis.get('HK'))
	Geoencoding = "https://maps.googleapis.com/maps/api/geocode/json?key=AIzaSyBag1UucvzhXNXzacTDrbkT1XaMTMV-GTo&address="

	address = ""
	for item in content:
		if item['District'] == testDis:
			address = item['Building name']+ "," + item['District']

	Geoencoding = Geoencoding + address.replace(" ", "+")
	print(Geoencoding)

	LocationRes = urllib.request.urlopen(Geoencoding)
	LocationCon = json.loads(LocationRes.read())
	print(LocationCon['results'][0]['geometry']['location']['lat'])


# Return the number of confirmed case based on the province name 
def FindWorldConfirmedCase(redis, provinceName):
	content = json.loads(redis.get('World'))

	for item in content['newslist']:
		if item['provinceName'] == provinceName:
			result = str(item['confirmedCount'])
			break
	result = provinceName + '的确诊人数: "'+ result +'"'

	msg = result
	print(msg)
	return result

# Return the number of confirmed case in Hong Kong
def FindHkConfiermedCase(redis):
	content = json.loads(redis.get('HK'))
	district = list()

	for item in content:
		district.append(item['District'])
	temp = Counter(district)
	most_common = temp.most_common()

	result = ""
	for item in most_common:
		result = result + item[0] + ":" + str(item[1]) + "\n"

	return result

def message(provinceName):
	response = urllib.request.urlopen("http://api.tianapi.com/txapi/ncovabroad/index?key=4a16ea54595dc82b1fa1c4a483ae1866")
	content = response.read()
	con = json.loads(content)
	conlist = con['newslist']
	for item in conlist:
		if item['provinceName'] == provinceName:
			result = item['confirmedCount']
	output = str(result)
	return output

def testing(TempRedis):
	try:
		t1 = threading.Thread(target=FindWorldConfirmedCase,args=(TempRedis,"意大利",))
		t2 = threading.Thread(target=FindWorldConfirmedCase,args=(TempRedis,"法国",))
		t1.start()
		t2.start()
	except:
		print("Error")

	return msg

main()