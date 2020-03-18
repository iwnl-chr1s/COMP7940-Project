import sys, urllib, json
import urllib.request

def FindconfirmedCount(conlist,provinceName):
	output = ""
	for item in conlist:
		if item['provinceName'] == provinceName:
			output = item['confirmedCount']
			break
	return output

response = urllib.request.urlopen("http://api.tianapi.com/txapi/ncovabroad/index?key=4a16ea54595dc82b1fa1c4a483ae1866")
content = response.read()
#if(content):
#    print(str(content,encoding='utf-8'))
	 #print(content.decode("UTF-8"))
con = json.loads(content)
conlist = con['newslist']
#print(conlist[0]['provinceName'] == "意大利")

test = "意大利"
result = FindconfirmedCount(conlist,test)
print(type(result))


