from __future__ import unicode_literals

import os
import sys
import redis
import sys, urllib, json
import urllib.request
import threading

from collections import Counter
from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import (
    MessageEvent, LocationSendMessage,
    TextMessage, TextSendMessage, 
    ImageMessage, ImageSendMessage,
    StickerMessage, StickerSendMessage
)
from linebot.utils import PY3

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

# obtain the port that heroku assigned to this app.
heroku_port = os.getenv('PORT', None)

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

global redis1

@app.route("/callback", methods=['POST'])
def callback():

    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

	# connect to the redis and get the data
    redis1 = ConnectToRedis()

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if isinstance(event.message, TextMessage):
            handle_TextMessage(event,redis1)
        if isinstance(event.message, ImageMessage):
            handle_ImageMessage(event)
        if isinstance(event.message, StickerMessage):
            handle_StickerMessage(event,redis1)

        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

    return 'OK'

# Handler function for Text Message
def handle_TextMessage(event,redis1):
    print(event.message.text)

    #creating the thread for search the data from the redis
    try:
    	t1 = threading.Thread(target=FindWorldConfirmedCase,args=(redis1, event.message.text,event))
    	t2 = threading.Thread(target=FindHkConfiermedCase,args=(redis1, event.message.text,event))
    	t1.start()
    	t2.start()
    except:
    	print("Errorrrrr")

# Handler function for Sticker Message
def handle_StickerMessage(event,redis1):
	#hkmsg = FindHkConfiermedCase(redis1)
	line_bot_api.reply_message(
		event.reply_token,
		LocationSendMessage(
			title='Sai Kung',
			address='Hong Kong',
			latitude=22.3166476,
			longitude=114.2687672
		)
	)


# Handler function for Image Message
def handle_ImageMessage(event):
    line_bot_api.reply_message(
	event.reply_token,
	ImageSendMessage(
		original_content_url="https://cdn2.ettoday.net/images/3185/3185673.jpg",
		preview_image_url="https://img.tt98.com/d/file/tt98/2019120917045534/5dedf5d1bc6b4.jpg"
		)
    )

# Connect to the redis and save the data
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

# Return the number of confirmed case based on the province name 
def FindWorldConfirmedCase(redis1, provinceName, event):
	#global result
	content = json.loads(redis1.get('World'))
	result = "nothing"

	for item in content['newslist']:
		if item['provinceName'] in provinceName :
			result = str(item['confirmedCount'])
			break
		elif item['countryShortCode'] in provinceName:
			result = str(item['confirmedCount'])
			break
		elif item['countryShortCode'].lower() in provinceName:
			result = str(item['confirmedCount'])
			break

	if result == "nothing":
		msg = "Please check whether it is wrong and type again"
		return msg
	else :
		msg = 'The confirmed case in "'+ provinceName +'" is "'+ result +'"'

		line_bot_api.reply_message(
        	event.reply_token,
        	TextSendMessage(msg)
    	)
		return msg



# Return the number of confirmed case in Hong Kong
def FindHkConfiermedCase(redis1, districtName, event):
	result = "nothing"

	content = json.loads(redis1.get('HK'))
	district = list()

	for item in content:
		district.append(item['District'])
	temp = Counter(district)
	most_common = temp.most_common()

	for item in most_common:
		if item[0] in districtName:
			result = str(item[1])
		elif item[0].capitalize() in districtName:
			result = str(item[1])
		elif item[0].title() in districtName:
			result = str(item[1])
	
	if result == "nothing":
		msg = "Please check whether it is wrong and type again"
		return msg
	else :
		msg = 'The confirmed case in "'+ districtName +'" is "'+ result +'"'
		line_bot_api.reply_message(
        	event.reply_token,
        	TextSendMessage(msg)
    	)
		return msg

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(host='0.0.0.0', debug=options.debug, port=heroku_port)
