import sys, urllib, json
import urllib.request
import redis
from collections import Counter

def main():
	TempRedis = ConnectToRedis()
	print(FindWorldConfirmedCase(TempRedis,"意大利"))
	print(FindHkConfiermedCase(TempRedis))

def ConnectToRedis():
	HOST = "redis-15449.c228.us-central1-1.gce.cloud.redislabs.com"
	PWD = "eqhpmBGXrr4tb3tkRACWDvffctJ0wBTf"
	PORT = "15449"
	Tian = "http://api.tianapi.com/txapi/ncovabroad/index?key=4a16ea54595dc82b1fa1c4a483ae1866"
	GovHK = "https://api.data.gov.hk/v2/filter?q=%7B%22resource%22%3A%22http%3A%2F%2Fwww.chp.gov.hk%2Ffiles%2Fmisc%2Fbuilding_list_chi.csv%22%2C%22section%22%3A1%2C%22format%22%3A%22json%22%7D"
	redis1 = redis.Redis(host = HOST, password = PWD, port = PORT)

	resOfTian = urllib.request.urlopen(Tian)
	resOfGovhk = urllib.request.urlopen(GovHK)

	conOfTian = resOfTian.read()
	conOfGovhk = resOfGovhk.read()

	redis1.set('World', conOfTian)
	redis1.set('HK', conOfGovhk)

	return redis1

# Return the number of confirmed case based on the province name 
def FindWorldConfirmedCase(redis, provinceName):
	content = json.loads(redis.get('World'))

	for item in content['newslist']:
		if item['provinceName'] == provinceName:
			result = str(item['confirmedCount'])
			break
	result = provinceName + '的确诊人数: "'+ result +'"'
	return result

# Return the number of confirmed case in Hong Kong
def FindHkConfiermedCase(redis):
	content = json.loads(redis.get('HK'))
	district = list()

	for item in content:
		district.append(item['地區'])
	temp = Counter(district)
	most_common = temp.most_common()

	result = ""
	for item in most_common:
		result = result + item[0] + ":" + str(item[1]) + "\n"

	return result

main()