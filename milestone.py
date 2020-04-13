from __future__ import unicode_literals

import os
import sys
import redis
import psycopg2
import re
import googleplaces 
from googleplaces import GooglePlaces, types, lang 
import requests 
import json 
import decimal
from argparse import ArgumentParser
from linebot.models import FlexSendMessage
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, LocationMessage, VideoMessage, FileMessage, StickerMessage, StickerSendMessage, LocationSendMessage
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


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

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
            handle_TextMessage(event)
        if isinstance(event.message, ImageMessage):
            handle_ImageMessage(event)
        if isinstance(event.message, VideoMessage):
            handle_VideoMessage(event)
        if isinstance(event.message, FileMessage):
            handle_FileMessage(event)
        if isinstance(event.message, StickerMessage):
            handle_StickerMessage(event)
        if isinstance(event.message, LocationMessage):
            handle_LocationMessage(event)

        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

    return 'OK'

# Handler function for news 
def get_news():
    url = os.environ['DATABASE_URL']
    conn = psycopg2.connect(url, sslmode = 'require')
    cursor = conn.cursor()
    
    order =  ''' SELECT * FROM NEWS_TABLE;'''

    cursor.execute(order)
    raw = cursor.fetchmany()
    if raw:
        print('get data successfully')
    
    print(raw)

    conn.commit()
    count = cursor.rowcount

    cursor.close()
    conn.close()

    return raw

# Handler function for counting 
def get_counts():
    url = os.environ['DATABASE_URL']
    conn = psycopg2.connect(url, sslmode = 'require')
    cursor = conn.cursor()
    
    order =  ''' SELECT * FROM COUNTS_TABLE;'''

    cursor.execute(order)
    raw = cursor.fetchall()
    if raw:
        print('get data successfully')
    
    print(raw)

    conn.commit()
    count = cursor.rowcount

    cursor.close()
    conn.close()

    return raw

# Handler function for Text Message
def handle_TextMessage(event):

    if "疫情新闻" in event.message.text:

        try:
            message = get_news()
            print("successfully load news data")
            flex_message = prepare_news_flex(message)

            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text = "疫情新闻",
                    contents = flex_message
                )
            )

            return True

        except:
            return False

    elif "疫情现状" in event.message.text:

        try:
            message = get_counts()
            print("successfully load counts data")
            flex_message = prepare_counts_flex(message)

            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(
                    alt_text = "疫情现状",
                    contents = flex_message
                )
            )

            return True

        except:
            return False

    elif "口罩" in event.message.text:

        try:
            print("detect the 口罩信息")

            line_bot_api.reply_message(
                event.reply_token,
                LocationSendMessage(
                    title = "口罩有售",
                    address = "浸信会医院",
                    latitude = 22.3395,
                    longitude = 114.1802
                )
            )

            return True

        except:
            return False

    else:

        try:
            line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text = "欢迎使用公共疫情机器人，您可以通过输入疫情新闻，疫情现状来查询最新的疫情情况; 输入口罩可以查询目前有售口罩的地址; 发送您所在的位置可以查询到据您最近的医院位置信息"
                    )
            )
            return True

        except:
            return False

# Handler function for Sticker Message
def handle_StickerMessage(event):
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=event.message.package_id,
            sticker_id=event.message.sticker_id)
    )

# Handler function for Image Message
def handle_ImageMessage(event):
    line_bot_api.reply_message(
    event.reply_token,
    TextSendMessage(text="Nice image!")
    )

# Handler function for Video Message
def handle_VideoMessage(event):
    line_bot_api.reply_message(
    event.reply_token,
    TextSendMessage(text="Nice video!")
    )

# Handler function for File Message
def handle_FileMessage(event):
    line_bot_api.reply_message(
    event.reply_token,
    TextSendMessage(text="Nice file!")
    )
    
# Handler function for Location Message
def handle_LocationMessage(event):
    mes = event.message.address
    lat = event.message.latitude
    lon = event.message.longitude

    near_hospital = prepare_hospital(lat, lon)

    print(near_hospital)
    print(near_hospital[0])
    print(type(near_hospital[1]))
    print(near_hospital[1])
    print(near_hospital[2])

    num1 = float(near_hospital[1])
    num2 = float(near_hospital[2])
    print(num1)
    print(type(num1))

    line_bot_api.reply_message(
        event.reply_token,
        LocationSendMessage(
            title = "距离您最近的医院",
            address = near_hospital[0],
            latitude = num1,
            longitude = num2
        )
    )

def prepare_news_flex(text):
    text_title = text[0][0]
    text_content = text[0][1]
    text_date = text[0][2]

    contents ={"type": "bubble",
               "header": {
                   "type": "box",
                   "layout": "horizontal",
                   "contents": [
                       {"type": "text", "text": text_title, "size": "xl", "weight": "bold"},
                       {"type": "text", "text": text_date, "size": "lg", "color": "#888888", "align": "end", "gravity": "bottom"}
                   ]
               },
               "hero": {
                   "type": "image",
                   "url": 'https://images-news.now.com/newsimage/NewsImage/2020-03-19-09-37-39yIUYl8IB.jpg',
                   "size": "full",
                   "aspect_ratio": "20:13",
                   "aspect_mode": "cover"
               },
               "body": {
                   "type": "box",
                   "layout": "vertical",
                   "spacing": "md",
                   "contents": [
                       {"type": "text", "text": text_content, "size": "md", "weight": "bold"}
                   ]
               },
               "footer": {
                   "type": "box",
                   "layout": "vertical",
                   "contents": [
                       {"type": "spacer", "size": "md"},
                       {"type": "button", "style": "primary", "color": "#1DB446",
                        "action": {"type": "uri", "label": "详细", "uri": 'https://www.info.gov.hk/gia/general/202004/08/P2020040800714.htm'}}
                   ]
               }
              }


    return contents

def prepare_counts_flex(text):

    print("successfully prepare")
    print(text)

    text_district_island_name = text[0][0]
    text_district_island_count = text[0][1]
    text_district_island_combine = text_district_island_name + text_district_island_count + "人"

    text_district_kowloon_name = text[1][0]
    text_district_kowloon_count = text[1][1]
    text_district_kowloon_combine = text_district_kowloon_name + text_district_kowloon_count + "人"

    text_district_new_name = text[2][0]
    text_district_new_count = text[2][1]
    text_district_new_combine = text_district_new_name + text_district_new_count + "人"

    
    print(text_district_island_combine)

    contents ={"type": "bubble",
               "header": {
                   "type": "box",
                   "layout": "horizontal",
                   "contents": [
                       {"type": "text", "text": "疫情现状", "size": "xl", "weight": "bold"},
                       {"type": "text", "text": "疫情现状", "size": "lg", "color": "#888888", "align": "end", "gravity": "bottom"}
                   ]
               },
               "hero": {
                   "type": "image",
                   "url": 'https://pix10.agoda.net/geo/country/132/3_132_hong_kong_02.jpg?s=1920x',
                   "size": "full",
                   "aspect_ratio": "20:13",
                   "aspect_mode": "cover"
               },
               "body": {
                   "type": "box",
                   "layout": "vertical",
                   "spacing": "md",
                   "contents": [
                       {"type": "text", "text": text_district_island_combine, "size": "md", "weight": "bold"},
                       {"type": "text", "text": text_district_kowloon_combine, "size": "md", "weight": "bold"},
                       {"type": "text", "text": text_district_new_combine, "size": "md", "weight": "bold"}
                   ]
               },
               "footer": {
                   "type": "box",
                   "layout": "vertical",
                   "contents": [
                       {"type": "spacer", "size": "md"},
                       {"type": "button", "style": "primary", "color": "#1DB446",
                        "action": {"type": "uri", "label": "详细", "uri": 'https://sc.isd.gov.hk/TuniS/www.info.gov.hk/gia/general/202004/11/P2020041100512.htm?fontSize=1'}}
                   ]
               }
              }


    return contents

def prepare_hospital(lati, long):
    api_key = 'AIzaSyA4YzcqsEEwT2MINOEMSJLNppLdCzirpgA'
    google_places = GooglePlaces(api_key)

    query_result = google_places.nearby_search(lat_lng = {'lat' : lati, 'lng' : long},
    radius = 5000,
    types = [types.TYPE_HOSPITAL])

    #if query_result.has_attributions: 
        #print (query_result.html_attributions) 
    
    print(query_result.places[0])
    place_name = query_result.places[0].name
    place_lat = query_result.places[0].geo_location['lat']
    place_lon = query_result.places[0].geo_location['lng']

    near = [place_name, place_lat, place_lon]

    # Iterate over the search results 
    #for place in query_result.places: 
        # print(type(place)) 
        # place.get_details() 
        #print (place.name) 
        #print("Latitude", place.geo_location['lat']) 
        #print("Longitude", place.geo_location['lng']) 
    print(near)

    return near
    
if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(host='0.0.0.0', debug=options.debug, port=heroku_port)