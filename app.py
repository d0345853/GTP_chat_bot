# -*- coding: utf-8 -*-
"""
Created on Wed Jun  2 21:16:35 2021

@author: Ivan
版權屬於「行銷搬進大程式」所有，若有疑問，可聯絡ivanyang0606@gmail.com

Line Bot聊天機器人
第一章 Line Bot申請與串接
Line Bot機器人串接與測試
"""
#############################################################
#載入LineBot所需要的套件
from flask import Flask, request, abort
from datetime import datetime, time
import pytz # $ pip install pytz
import requests

import openai
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

#############################################################
msgchk_timer = ["現在時間","目前時間","時刻","幾點","報時","標準時間","時間"]
msgchk_not = ["不知道","我無法","不理解","我不懂","我不能","我无法","我沒","不明白","我不太","不知道","我不是","不清楚","不確定","不提供"]
msgchk_weather = ["天氣","氣象","下雨"]

#############################################################
# 必須放上自己的Channel Access Token
line_bot_api = LineBotApi('ZDKxXNN1YeHrqa8+lOlgv9RjOl/2kCVpO5xoDLC3SHfnBBdA9IA3Z/fOQPiHEJhvQ9ImNXMMF/q6Dzl5Rk9UMtpi0a+NJzg+81oARe6dOeaubeXm42HCnNyGJ1j9+oBmOUj+UrZaXLYD3fYc/ybLmgdB04t89/1O/w1cDnyilFU=')
# 必須放上自己的Channel Secret
handler = WebhookHandler('91ba25530818a52375c97fbd27aac56c')
# 更新訊息
# line_bot_api.push_message('Ub08558de58b09af13f8e03da6a5dfca6', TextSendMessage(text='哈囉哈囉~兔兔來囉!'))


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

#訊息傳遞區塊
##### 基本上程式編輯都在這個function #####
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    #############################################################
    #line input
    #message = TextSendMessage(text=event.message.text)  #line input
    input_message = text=event.message.text  #line input


    # if "卡米兔安靜" in message:
    #     text_message = TextSendMessage('好的遵命')              # 轉型
    #     line_bot_api.reply_message(event.reply_token,text_message)  #line output
    # elif "卡米兔說話" in message:
    #     text_message = TextSendMessage('好的遵命')              # 轉型
    #     line_bot_api.reply_message(event.reply_token,text_message)  #line output            
    # else:

    openai.api_key = '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'

    #############################################################
    # -------------- model 1 --------------     
    # 時間
    if input_message in msgchk_timer:
        time_tz = pytz.timezone('Asia/Taipei') # <- put your local timezone here
        time_now = datetime.now(time_tz) # the current time in your local timezone
        time_current = time_now.strftime("%H:%M:%S")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"現在台灣時間：{time_current}"))

    #############################################################
    # -------------- model 2 -------------- 
    # 天氣    
    elif ("天氣" in input_message) or ("氣象" in input_message) or ("下雨" in input_message) or ("傘" in input_message) :
        # url = '一般天氣預報 - 今明 36 小時天氣預報 JSON 連結'



        weather_log = ""
        weather_url = f"https://opendata.cwb.gov.tw/dist/opendata-swagger.html#/%E9%A0%90%E5%A0%B1/get_v1_rest_datastore_F_C0032_001"
        weather_params = {
            "Authorization": "CWB-86BE978B-666E-4AE1-87B6-C70A998DDD5F",
            "locationName": "台北市",
        }

        #output
        weather_response = requests.get(weather_url, params=weather_params)

        #size=200
        #print(response.status_code) 
 
        if weather_response.status_code == 200:

            data = json.loads(weather_response.text)

            # item
            weather_location = data["records"]["location"][0]["locationName"]
            #weather_elements = data["records"]["location"][0]["weatherElement"]
            weather_state = weather_elements[0]["time"][0]["parameter"]["parameterName"]
            weather_rain_prob = weather_elements[1]["time"][0]["parameter"]["parameterName"]
            #min_tem = weather_elements[2]["time"][0]["parameter"]["parameterName"]
            weather_comfort = weather_elements[3]["time"][0]["parameter"]["parameterName"]
            weather_max_tem = weather_elements[4]["time"][0]["parameter"]["parameterName"]

            # print
            weather_log = weather_location + "未來 8 小時" + weather_state + "，" + weather_comfort + "，最高溫" + weather_max_tem + "度，降雨機率" + weather_rain_prob + "%"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(weather_location))


    else:
        #############################################################
        # -------------- model 3 -------------- 
        # Add a message from the chatbot to the conversation history
        message_log = []
        message_log.append({'role': 'assistant', 'content': 'Your name is 卡米兔, your are a happy rabbit.'})
        message_log.append({'role': 'user', 'content': input_message})
        response_1 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # The name of the OpenAI chatbot model to use
            messages=message_log   # The conversation history up to this point, as a list of dictionaries
        )
        message_log.append({'role': response_1.choices[0].message.role, 'content': response_1.choices[0].message.content})

        #reply_msg = response.choices[0].message.content.replace('\n','')
        # reply_msg = response.choices[0].message.content
        # for choice in response.choices:
        #     if "text" in choice:
        #         reply_msg =choice.text
        #         break
        reply_msg = ""
        reply_msg = format(message_log[-1]['content'].strip())
        # If no response with text is found, return the first response's content (which may be empty)
        # return response.choices[0].message.content
        # reply_msg = response[-1]['content'].strip()
        
        #############################################################
        # -------------- model 4 -------------- 
        # Add a message from the chatbot2 
        if ("不知道" in reply_msg) or ("我無法" in reply_msg) or ("不理解" in reply_msg) or ("我不懂" in reply_msg) or ("我不能" in reply_msg) or  ("我无法" in reply_msg) or ("我沒" in reply_msg) or ("不明白" in reply_msg) or ("我不太" in reply_msg) or ("不知道" in reply_msg) or ("我不是" in reply_msg) or ("不清楚" in reply_msg)or ("不確定" in reply_msg) or ("不提供" in reply_msg):
            response_2 = openai.Completion.create(
                engine = "text-davinci-003",    # select model
                prompt = input_message,     
                max_tokens = 512,               # response tokens
                temperature = 1,                # diversity related NLG模型
                top_p = 0.8,                    # diversity related
                n = 1,                          # num of response
            )
            reply_msg = ""
            reply_msg = response_2["choices"][0]["text"].replace('\n','')

        #############################################################
        # -------------- output -------------- 
        text_message = TextSendMessage(text=reply_msg)              # 轉型
        line_bot_api.reply_message(event.reply_token,text_message)  #line output


#主程式
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

