#############################################################
# -*- coding: utf-8 -*-
"""
Created on May 10 21:16:35 2023
@author: Jordan
"""
#############################################################
from flask import Flask, request, abort # Loading LineBot library
from datetime import datetime, time     # Loading timer
import pytz                             # Loading timer
import requests                         # Loading LineBot library
import openai                           # Loading open AI library
import re                               # replace
from linebot import (                   # Loading LineBot API
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
app = Flask(__name__)

#############################################################
msgchk_timer = ["現在時間","目前時間","現在時刻","幾點","報時","標準時間","時間","日期","今天","今天幾號","今天星期幾","星期幾"]
msgchk_pic = ["畫","圖","繪"]
msgchk_not = ["不知道","我無法","不理解","我不懂","我不能","我无法","我沒有","不明白","我不太","不了解","我不是","不清楚","不確定","不提供"]
msgchk_weather = ["天氣","氣象","下雨"]
msgchk_weather_more = ["明天","後天","未來","下","週","市","村","鄉"]
weather_list = {"宜蘭縣":"F-D0047-003","桃園市":"F-D0047-007","新竹縣":"F-D0047-011","苗栗縣":"F-D0047-015",
    "彰化縣":"F-D0047-019","南投縣":"F-D0047-023","雲林縣":"F-D0047-027","嘉義縣":"F-D0047-031",
    "屏東縣":"F-D0047-035","臺東縣":"F-D0047-039","花蓮縣":"F-D0047-043","澎湖縣":"F-D0047-047",
    "基隆市":"F-D0047-051","新竹市":"F-D0047-055","嘉義市":"F-D0047-059","臺北市":"F-D0047-063",
    "高雄市":"F-D0047-067","新北市":"F-D0047-071","臺中市":"F-D0047-075","臺南市":"F-D0047-079",
    "連江縣":"F-D0047-083","金門縣":"F-D0047-087"}
weather_name = {"宜蘭縣":"宜蘭","桃園市":"桃園","新竹縣":"新竹","苗栗縣":"苗栗",
    "彰化縣":"彰化","南投縣":"南投","雲林縣":"雲林","嘉義縣":"嘉義",
    "屏東縣":"屏東","臺東縣":"台東","花蓮縣":"花蓮","澎湖縣":"澎湖",
    "基隆市":"基隆","新竹市":"新竹","嘉義市":"嘉義","臺北市":"台北",
    "高雄市":"高雄","新北市":"新北","臺中市":"台中","臺南市":"台南",
    "連江縣":"連江","金門縣":"金門"}

#############################################################
# 1. Put your Channel Access Token (line bot ID)
line_bot_api = LineBotApi('ZDKxXNN1YeHrqa8+lOlgv9RjOl/2kCVpO5xoDLC3SHfnBBdA9IA3Z/fOQPiHEJhvQ9ImNXMMF/q6Dzl5Rk9UMtpi0a+NJzg+81oARe6dOeaubeXm42HCnNyGJ1j9+oBmOUj+UrZaXLYD3fYc/ybLmgdB04t89/1O/w1cDnyilFU=')

# 2. Put your Channel Secret (help linebot to heroku server)
handler = WebhookHandler('91ba25530818a52375c97fbd27aac56c')

# 3. Show Update message (If you update success, linebot will show it)
# line_bot_api.push_message('Ub08558de58b09af13f8e03da6a5dfca6', TextSendMessage(text='哈囉哈囉~兔兔來囉!'))

# 4.Waiting for "/callback" word from Customer Post Request (for heroku Server)
@app.route("/callback", methods=['POST'])   
def callback():
    signature = request.headers['X-Line-Signature']                                                 # get X-Line-Signature header value
    body = request.get_data(as_text=True)                                                           # get request body as text
    app.logger.info("Request body: " + body)                                                        # combine
    try:
        handler.handle(body, signature)                                                             # handle webhook body
    except InvalidSignatureError:
        abort(400)
    return 'OK'
#############################################################
db_setting ={
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "jordan",
    "db":"jordan_db",
    "charset": "utf8"
}
#############################################################
#####                  Main function                    #####
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    #######################################
    # ------------ Definition ----------- #    
    input_message = event.message.text                                                              # input message (from line, String type)         
    reply_msg = ""                                                                                  # output message
    openai.api_key = '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'                          # open AI account number


    # "安" "卡米" "請" "早" "兔"
    # if "卡米兔安靜" in message:
    #     text_message = TextSendMessage('好的遵命')              # 轉型
    #     line_bot_api.reply_message(event.reply_token,text_message)  #line output
    # elif "卡米兔說話" in message:
    #     text_message = TextSendMessage('好的遵命')              # 轉型
    #     line_bot_api.reply_message(event.reply_token,text_message)  #line output            
    # else:

    
    #######################################
    # --------------Mantra--------------- #
    if ("卡米" == input_message):
        reply_msg = f"逗你歡樂 陪你說笑"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))

    #######################################  
    # ------------Time and Day----------- #
    elif input_message in msgchk_timer:
        # 1. Get timer
        time_tz = pytz.timezone('Asia/Taipei')                                                      # put your local timezone here
        time_now = datetime.now(time_tz)                                                            # the current time in your local timezone
        time_current = time_now.strftime("%m/%d  %H:%M:%S")                                         # output format
        reply_msg = f"現在台灣時間：\n{time_current}"
        # 2. Line Output 
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))

    #######################################
    # --------------Weather-------------- #
    elif ("天氣" in input_message) or ("氣象" in input_message) or ("下雨" in input_message):
        # 1.weather parameter
        weather_code = 'CWB-86BE978B-666E-4AE1-87B6-C70A998DDD5F'                                   # weather API code
        weather_output = {}                                                                         # for each location
        # 2.getting weather url link(JSON Format)
        weather_url = f'https://opendata.cwb.gov.tw/fileapi/v1/opendataapi/F-C0032-001?Authorization={weather_code}&downloadType=WEB&format=JSON'
        # 3.getting all weather
        weather_data = requests.get(weather_url)                                                    # get URL
        weather_data_json = weather_data.json()                                                     # trans json format
        weather_location = weather_data_json['cwbopendata']['dataset']['location']                  # forecast data of major location

        # 4-1.parser (8 hour data) -----------------------------------------------------------------
        for i in weather_location:
            weather_locationname = i['locationName']                                                # location (for index)
            weather_state = i['weatherElement'][0]['time'][0]['parameter']['parameterName']         # weater status
            weather_min_tem = i['weatherElement'][1]['time'][0]['parameter']['parameterName']       # min temperature
            weather_max_tem = i['weatherElement'][2]['time'][0]['parameter']['parameterName']       # max temperature
            weather_comfort = i['weatherElement'][3]['time'][0]['parameter']['parameterName']       # Comfort word
            weather_rain_prob = i['weatherElement'][4]['time'][0]['parameter']['parameterName']     # chance of rain
            #output 
            weather_output[weather_locationname]=f"{weather_locationname}未來 8 小時{weather_state}，{weather_comfort}，溫度{weather_min_tem}~{weather_max_tem}度，降雨機率{weather_rain_prob}%"

        # 4-2. check input message
        for i in weather_output:                                                                    # location list
            if weather_name[i] in input_message:                                                    # if location name is equal to input message
                reply_msg = weather_output[i]                                                       # output                              
                break
            else:
                reply_msg = weather_output["臺北市"]                                                # default location
        
        # 5-1.parser (1 week data) -----------------------------------------------------------------
        if ("明天" in input_message) or ("後天" in input_message) or ("下" in input_message)or ("週" in input_message) or ("未來" in input_message)or ("鄉" in input_message)or ("村" in input_message)or ("鎮" in input_message)or ("市" in input_message):
            for i in weather_output:                                                               # location list
                if weather_name[i] in input_message:                                               # if location name is equal to input message
                    # 5-2 [RE] getting weather url link(JSON Format)
                    weather_url = f'https://opendata.cwb.gov.tw/api/v1/rest/datastore/{weather_list[i]}?Authorization={weather_code}&elementName=WeatherDescription'
                    # 5-3 [RE] getting all weather
                    weather_data = requests.get(weather_url)                                        # get URL
                    weather_data_json = weather_data.json()                                         # trans json format
                    weather_location = weather_data_json['records']['locations'][0]['location']     # forecast data of major location
                    break
                else:
                    # default location
                    weather_url = f'https://opendata.cwb.gov.tw/api/v1/rest/datastore/{weather_list["臺北市"]}?Authorization={weather_code}&elementName=WeatherDescription'
                    weather_data = requests.get(weather_url)
                    weather_data_json = weather_data.json()
                    weather_location = weather_data_json['records']['locations'][0]['location']
            # 5-4 [RE] check input message
            for i in weather_location:
                weather_locationname = i['locationName']                                            # location (for index)
                weather_data = i['weatherElement'][0]['time'][1]['elementValue'][0]['value']        # Comprehensive data
                if weather_locationname in input_message:                                           # small location name is equal to input message
                    reply_msg = f'{weather_locationname}未來一周{weather_data}'                      # output
                    break
                else:
                    reply_msg = f'{weather_locationname}未來一周{weather_data}'                      # last value

        # 6.Output
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))

    #######################################
    # --------------- PIC --------------- #
    elif ("畫一" in input_message) or ("請畫" in input_message)or ("畫出" in input_message)or ("產生" in input_message)or ("繪製" in input_message)or ("一張" in input_message):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="兔兔努力畫圖中"))
  
        # 2. Setting AI module
        response_3 = openai.Image.create(
            prompt = input_message.replace("請","").replace("的圖片","").replace("照片","").replace("繪製","").replace("畫出","").replace("一張","").replace("給我","").replace("幫我","").replace("生成","").replace("畫","").replace("設計","").replace("產生","").replace("的圖","").replace("描繪","").replace("製作",""), 
                                                                                                    #remove unnecessary image
            n = 1,                                                                                  # one pic
            size = "1024X1024"                                                                      # Size
        )
        
        image_url = response_3["data"][0]["url"]                                                    # get image url
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=image_url))

        line_bot_api.reply_message(event.reply_token,                                               # line reply image (from link)
                                   ImageSendMessage(orignial_content_url=image_url,                 # original image
                                                    preview_image_url=image_url))                   # zip preview image
    #######################################
    # --------------- Web --------------- #
    elif ("www" in input_message) or ("http" in input_message):
        reply_msg = ""                                                                              # don't reply message

    else:
        #######################################
        # ----------- AI anwser 1------------ #
        # 1. message buffer
        message_log = []                                            # Add a intput message from the chatbot to the conversation history
        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': 'Your name is 卡米兔, your are a happy rabbit.'})   
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_1 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",                                  # The name of the OpenAI chatbot model to use
            messages=message_log                                    # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_1.choices[0].message.role, 'content': response_1.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())      # If no response with text is found, return the first response's content (which may be empty)

        #######################################
        # ----------- AI anwser 2------------ #
        #     1. Add a message from the chatbot2  (to reduce negative answer)#
        if ("不知道" in reply_msg) or ("我無法" in reply_msg) or ("不理解" in reply_msg) or ("我不懂" in reply_msg) or ("我不能" in reply_msg) or  ("我无法" in reply_msg) or ("我沒有" in reply_msg) or ("不明白" in reply_msg) or ("我不太" in reply_msg) or ("不了解" in reply_msg) or ("我不是" in reply_msg) or ("不清楚" in reply_msg)or ("不確定" in reply_msg) or ("不提供" in reply_msg):
           
            # 2. Setting AI module
            response_2 = openai.Completion.create(
                engine = "text-davinci-003",                        # select model
                prompt = input_message,                             # input string
                max_tokens = 512,                                   # response tokens
                temperature = 1,                                    # diversity related for NLG model
                top_p = 0.8,                                        # diversity related
                n = 1,                                              # num of response
            )
            # 3. reset output message
            reply_msg = ""
            # 4. Exception
            if ("//" in reply_msg) or ("[" in reply_msg) or ("{" in reply_msg):
                reply_msg = "卡米卡米 ~"
            elif("sorry" in reply_msg):
                reply_msg = "很抱歉，卡米兔不知道您在囉哩八說甚麼?"                
            else:
                reply_msg = response_2["choices"][0]["text"].replace('\n','')   # output AI anwser

        #######################################
        # -------------- output ------------- #  
        text_message = TextSendMessage(text=reply_msg)              # string to TextSendMessage
        line_bot_api.reply_message(event.reply_token,text_message)  # line output



#############################################################
#####               Process input point                 #####
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))                        # run OS server
    app.run(host='0.0.0.0', port=port)                              # setting server port

