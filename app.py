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

from linebot import (                   # Loading LineBot API
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
app = Flask(__name__)

#############################################################
msgchk_timer = ["現在時間","目前時間","時刻","幾點","報時","標準時間","時間","日期","今天","今天幾號","今天星期幾","星期幾"]
msgchk_not = ["不知道","我無法","不理解","我不懂","我不能","我无法","我沒有","不明白","我不太","不了解","我不是","不清楚","不確定","不提供"]
msgchk_weather = ["天氣","氣象","下雨"]
weather_list = {"宜蘭縣":"F-D0047-001","桃園市":"F-D0047-005","新竹縣":"F-D0047-009","苗栗縣":"F-D0047-013",
    "彰化縣":"F-D0047-017","南投縣":"F-D0047-021","雲林縣":"F-D0047-025","嘉義縣":"F-D0047-029",
    "屏東縣":"F-D0047-033","臺東縣":"F-D0047-037","花蓮縣":"F-D0047-041","澎湖縣":"F-D0047-045",
    "基隆市":"F-D0047-049","新竹市":"F-D0047-053","嘉義市":"F-D0047-057","臺北市":"F-D0047-061",
    "高雄市":"F-D0047-065","新北市":"F-D0047-069","臺中市":"F-D0047-073","臺南市":"F-D0047-077",
    "連江縣":"F-D0047-081","金門縣":"F-D0047-085"}
weather_name = {0:"宜蘭",1:"桃園",2:"新竹",3:"苗栗",
    4:"彰化",5:"南投",6:"雲林",7:"嘉義",
    8:"屏東",9:"台東",10:"花蓮",11:"澎湖",
    12:"基隆",13:"新竹",14:"嘉義",15:"台北",
    16:"高雄",17:"新北",18:"台中",19:"台南",
    20:"連江",21:"金門"}

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
    signature = request.headers['X-Line-Signature']                         # get X-Line-Signature header value
    body = request.get_data(as_text=True)                                   # get request body as text
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)                                     # handle webhook body
    except InvalidSignatureError:
        abort(400)
    return 'OK'


#############################################################
#####                  Main function                    #####
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    #######################################
    # ------------ Definition ----------- #    
    input_message = event.message.text                                      # input message (from line, String type)         
    reply_msg = ""                                                          # output message
    openai.api_key = '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'  # open AI account number


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
        time_tz = pytz.timezone('Asia/Taipei')                              # <- put your local timezone here
        time_now = datetime.now(time_tz)                                    # the current time in your local timezone
        time_current = time_now.strftime("%m/%d  %H:%M:%S")                 # output format
        reply_msg = f"現在台灣時間：\n{time_current}"
        # 2. Line Output 
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))

    #######################################
    # --------------Weather-------------- #
    elif ("天氣" in input_message) or ("氣象" in input_message) or ("下雨" in input_message) or ("傘" in input_message) or ("風" in input_message) :

        # 1.weather parameter
        weather_code = 'CWB-86BE978B-666E-4AE1-87B6-C70A998DDD5F'           # weather API code
        weather_list = 'F-D0047-061'                                        # Web list code (for 8 hour predict)
        weather_output = {}                                                 # for each location
        weather_index = 0                                                   # weather location index (for weather_name)
        # 2.weather url link(JSON Format)
        weather_url = f'https://opendata.cwb.gov.tw/fileapi/v1/opendataapi/F-C0032-001?Authorization={weather_code}&downloadType=WEB&format=JSON'

        # if ("明天" in input_message):
        #     weather_url = f'https://opendata.cwb.gov.tw/api/v1/rest/datastore/{weather_list}?Authorization={weather_code}&elementName=WeatherDescription'

        weather_data = requests.get(weather_url)   # 取得主要縣市預報資料
        weather_data_json = weather_data.json()  # json 格式化訊息內容
        weather_location = weather_data_json['cwbopendata']['dataset']['location']    # 取得縣市的預報內容
        #weather_location = weather_data_json['records']['locations'][0]['location']  # 取得縣市的預報內容
        for i in weather_location:
            weather_locationname = i['locationName']    # 縣市名稱
            weather_state = i['weatherElement'][0]['time'][0]['parameter']['parameterName']    # 天氣現象
            #weather_min_tem = i['weatherElement'][1]['time'][0]['parameter']['parameterName']  # 最低溫
            weather_max_tem = i['weatherElement'][2]['time'][0]['parameter']['parameterName']  # 最高溫
            weather_comfort = i['weatherElement'][3]['time'][0]['parameter']['parameterName']    # 舒適度
            weather_rain_prob = i['weatherElement'][4]['time'][0]['parameter']['parameterName']   # 降雨機率

            weather_output[weather_locationname]=f"{weather_locationname}未來 8 小時{weather_state}，{weather_comfort}，最高溫{weather_max_tem}度，降雨機率{weather_rain_prob}%"

            # if ("明天" in input_message):
            #     line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"{weather_locationname}未來 36 小時{weather_state}，{weather_comfort}，最高溫{weather_max_tem}度，降雨機率{weather_rain_prob}%"))
            # else:
            #     line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"{weather_locationname}未來 8 小時{weather_state}，{weather_comfort}，最高溫{weather_max_tem}度，降雨機率{weather_rain_prob}%"))

        # 今天資料
        for i in weather_locationname:
            if weather_name[weather_index] in input_message:        # 如果使用者的地址包含縣市名稱
                reply_msg = weather_output[i]  # 將 msg 換成對應的預報資訊
                break
            else:
                reply_msg = weather_output["臺北市"]
                # 將進一步的預報網址換成對應的預報網址
            weather_index+=1
        
        # 未來資料
        if ("明天" in input_message) or ("後天" in input_message) or ("下星期" in input_message) or ("未來" in input_message):
            weather_index=0     # reset_index
            for i in weather_output:
                if weather_name[weather_index] in input_message:        # 如果使用者的地址包含縣市名稱
                    # 將進一步的預報網址換成對應的預報網址
                    weather_url = f'https://opendata.cwb.gov.tw/api/v1/rest/datastore/{weather_list[i]}?Authorization={weather_code}&elementName=WeatherDescription'
                    weather_data = requests.get(weather_url)  # 取得主要縣市裡各個區域鄉鎮的氣象預報
                    weather_data_json = weather_data.json() # json 格式化訊息內容
                    weather_location = weather_data_json['records']['locations'][0]['location']    # 取得預報內容
                    break
                weather_index+=1
            for i in weather_name:
                weather_locationname = i['locationName']   # 取得縣市名稱
                weather_data = i['weatherElement'][0]['time'][1]['elementValue'][0]['value']  # 綜合描述
                if weather_locationname in input_message:    # 如果使用者的地址包含鄉鎮區域名稱
                    reply_msg = f'未來一周天氣{weather_data}' # 將 msg 換成對應的預報資訊
                    break
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg) )  # line output

    #######################################
    # --------------- Web --------------- #
    elif ("www" in input_message) or ("http" in input_message):
        reply_msg = ""                          # no anwser

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

