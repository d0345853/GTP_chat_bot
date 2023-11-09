#############################################################
# -*- coding: utf-8 -*-
"""
Created on May 10 21:16:35 2023
@author:  Jordan
compiler: window cmd
language: python
server:   our PC(server) + ngrok(web_link)
web:      https://ad71-2407-4d00-2c01-7c66-897-7045-253d-dfd.jp.ngrok.io 
host test:http://localhost:5000/  
models:   text-davinci-003
          DALL·E 2
          gpt-3.5-turbo-0301
          whisper-1
          tesseract-ocr 
step 1.   install python 3.7 or 3.8
step 2.   use cmd & pip install all requirements.txt environment
step 3.   cmd keyin:                                python app.py  (DON'T CLOSE TERMINAL!!)
step 4.   open web to check:                        http://localhost:5000/
step 5.   open new terminal & keyin:                ngrok http 5000 (DON'T CLOSE TERMINAL TOO!!)
step 6.   copy your ngrok server website
step 7.   open linebot web & update server website: https://developers.line.biz/zh-hant/
step 8.   If you want to update your code, just rerun the "python app.py"
step 9.   refer to                                  https://www.youtube.com/watch?v=YOJ2DKsIIdI&ab_channel=%E9%BE%8D%E9%BE%8D%E7%9A%84%E7%A8%8B%E5%BC%8F%E6%95%99%E5%AD%B8
"""
#############################################################
from flask import Flask, request, abort # Loading LineBot library (web server)
from datetime import datetime, time     # Loading timer
import pytz                             # Loading timer
import requests,json                    # Loading LineBot library
import openai                           # Loading open AI library
import re                               # replace
import pymysql                          # pymsql
import csv                              # csv
from copy import deepcopy               # copy
from bs4 import BeautifulSoup           # parser fed
from linebot import (                   # Loading LineBot API
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (        # Linebot exceptions
    InvalidSignatureError
)
from linebot.models import *
from linebot.models.send_messages import ImageSendMessage
from linebot.models import AudioMessage
import base64                           # upload img
from PIL import Image                   # OCS
import pytesseract
app = Flask(__name__)

#############################################################
# dict type #
msgchk_timer = ["現在時間","目前時間","現在時刻","幾點","報時","標準時間","時間","日期","今天","今天幾號","今天星期幾","星期幾"]
msgchk_pic = ["畫","圖","繪"]
msgchk_not = ["不知道","我無法","不理解","我不懂","我不能","我无法","我沒有","不明白","我不太","不了解","我不是","不清楚","不確定","不提供","sorry"]
msgchk_weather = ["天氣","氣象","下雨"]
msgchk_lovr = ["喜","喜歡","寶貝","情","甜甜"]
msgchk_marv = ["不爽","生氣","沒禮貌","不開心","怎樣","到底","靠","幹","操","馬的"] 
msgchk_weather_more = ["明天","後天","未來","下","週","市","村","鄉"]
msgchk_active =["卡米","請","早","兔","聊天","出來","說話","畫","時","天","好","嗨","Hi"]
msgchk_silence =["安靜","閉嘴","吵","關機","睡覺","休息"]
msgchk_time = ["正常模式"]



# list type #
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


@app.route("/")                                                                                     # web show default message
def root():
    return "Jordan web server"

# 5.Waiting for "/callback" word from Customer Post Request (for heroku Server)
@app.route("/callback", methods=['POST'])                                                           # web show callback message
def callback():
    signature = request.headers['X-Line-Signature']                                                 # get X-Line-Signature header value
    body = request.get_data(as_text=True)                                                           # get request body as text
    app.logger.info("Request body: " + body)                                                        # combine
    try:
        handler.handle(body, signature)                                                             # handle webhook body
    except InvalidSignatureError:
        abort(400)
    return 'OK'                                                                                     # show in website
#############################################################
csv_format = ['groupID','Silence','Marv','last_msg', 'last_time']                                   # 0. format = {groupID, flag_silence, flag_marv, last_msg}
csv_read_all = []
csv_write_one = {'groupID':"", 'Silence':"0", 'Marv':"0", 'last_msg':"My name is 卡米兔, I am a happy rabbit.", 'last_time':"My name is 卡米兔, I am a happy rabbit."}
db_settings ={
    "host": "127.0.0.1",                                                                            # not use
    "port": 3306,
    "user": "root",
    "password": "jordan",
    "db":"jordan_db",
    "charset": "utf8"
}

#############################################################
#####                  Main function                    #####
@handler.add(MessageEvent, message=TextMessage)                                                     # new event(line text interative)
def handle_message(event):

    #######################################
    # ------------ Definition ----------- #    
    input_message = event.message.text                                                              # input message (from line, String type)         
    reply_msg = ""                                                                                  # output message
    openai.api_key = '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'                          # open AI account number

    #######################################
    # ----------  get time   ------------ #
    time_tz = pytz.timezone('Asia/Taipei')                                                          # put your local timezone here
    time_now = datetime.now(time_tz)                                                                # the current time in your local timezone
    time_stamp_new = int(time_now.strftime("%M")) + 60*int(time_now.strftime("%H")) + 1440*int(time_now.strftime("%d"))+ 34560*int(time_now.strftime("%m"))


    #######################################
    # --------  read  param sql   ------- #
    csv_new_ID = 0
    Group_ID = ""
    flag_silence = 0                                                                                # Linebot silence mode (0=timer_clsse, 1=always_talk, 2=silence)
    flag_marv = 0                                                                                   # Linebot rude mode
    last_msg =""
    time_stamp =0
    # 1. If I have group_ID
    try:
        Group_ID = event.source.group_id                                                            # get group ID
    # 2. If not, I will used Group_ID=user_ID
    except AttributeError:
        Group_ID = User_ID = text=event.source.user_id                                              # get user ID
    # 3.read ID to sql
    try:
        with open('./user.csv', newline='') as csv_file:
            csv_read_all = list(csv.DictReader(csv_file))                                           # read & save dict format 
            for csv_row in csv_read_all:                                                            # show all csv file (to list)
                # 3-1 Old account
                if csv_row['groupID']==Group_ID:                                                    # 3-1 compare dict[Group_ID] in all csv_row
                    csv_new_ID = 0
                    flag_silence = int(csv_row['Silence'])                                          # 3-2 ['Silence']   (string to int)
                    flag_marv = int(csv_row['Marv'])                                                # 3-3 ['Marv']      (string to int)                                              
                    last_msg = csv_row['last_msg']                                                  # 3-4 ['last_msg'] 
                    time_stamp = int(csv_row['last_time'])
                    break
                # 3-2 New account
                else:
                    csv_new_ID = 1                                                                  # default for new account
                    flag_silence = 0
                    flag_marv = 0
                    last_msg = "My name is 卡米兔, I am a happy rabbit."
    except IOError:
        print("File error, please close the file")


    #######################################
    # -----  write new param sql  ------- #
    # 1.put in new list
    if(csv_new_ID == 1):
        csv_write_one['groupID'] = Group_ID
        csv_write_one['Silence'] = flag_silence       
        csv_write_one['Marv'] = flag_marv       
        csv_write_one['last_msg'] = last_msg       
        csv_write_one['last_time'] = time_stamp
        # 2.add new account param in the last
        csv_read_all.append(deepcopy(csv_write_one))          
        # 3.write new ID to sql
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)            # using csv.writer method from CSV package
                csv_writer.writeheader()                                     # list item
                for csv_row in csv_read_all:                                 # parser csv data to dict format
                    csv_writer.writerow(csv_row)
        except IOError:
            print("File error, please close the file")

    ########################################
    # --------------Silence--------------- #
    silence_change = 0
    silence_message =input_message[0:10]
    # 1. timer mode ( active for 1 hour)
    if (flag_marv==0):
        if (abs(time_stamp_new-time_stamp)>720):
            flag_marv=2
            for csv_row in csv_read_all:     
                if csv_row['groupID']==Group_ID:                                # check user ID 
                    csv_row['Silence']=flag_silence                             # silence mode
                    csv_row['Marv'] = flag_marv 
                    csv_row['last_time']=time_stamp_new                         # update user time
                else:
                    continue    
            try:
                with open('./user.csv', 'w', newline='') as csv_file:
                    csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                    csv_writer.writeheader()                                    # write header too
                    for csv_row in csv_read_all:                                # parser csv data 
                        csv_writer.writerow(csv_row)                            # write
            except IOError:
                print("File error, please close the file")

            # 1. message buffer
            message_log = []                                                    # Add a intput message from the chatbot to the conversation history
            # 3. Put input message to "user form" 
            message_log.append({'role': 'user', 'content': '請委婉地說明:「我是卡米兔兔，我正在休息中，有事再跟我說」，字數不超過20字'})
            # 4. Setting AI module
            response_5 = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
                temperature=0.9,              
                messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
            )
            # 5.get output message & put into message_log
            message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
            # 6. output message 
            reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
            text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage
            line_bot_api.reply_message(event.reply_token,text_message)          # line output    
    # 2. silence mode   
    elif (flag_marv==2):
        if ("卡米" in silence_message) or ("安" in silence_message) or ("了" in silence_message)or ("請" in silence_message) or ("囉" in silence_message) or ("畫" in silence_message) or ("兔" in silence_message) or ("嗨" in silence_message)or ("Hi" in silence_message)or ("天" in silence_message)or ("恩" in silence_message):
            flag_marv=0                                                     # it can reply & recode  
            silence_change=1
        else:
            return                                                           # don't reply message


    # if (flag_silence==0):
    #     if ("安靜" in silence_message) or ("閉嘴" in silence_message) or ("吵" in silence_message) or ("關機" in silence_message) or ("去睡覺" in silence_message) or ("休息" in silence_message):
    #         flag_marv=2                                                   # silence mode
    #         silence_change=1                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"好的，卡米兔休息")    
    #         line_bot_api.reply_message(event.reply_token,text_message)          # line output     
    #     elif("話癆模式" in silence_message):
    #         flag_silence=1                                                   # always mode
    #         silence_change=1                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"好喔好喔~")  
    #     elif("不爽" in silence_message) or ("造反" in silence_message)or ("沒禮貌" in silence_message)or ("怎樣" in silence_message)or ("靠" in silence_message)or ("幹" in silence_message)or ("馬的" in silence_message):
    #         flag_silence=3                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，不爽模式")      
    #     elif("甜" in silence_message)or("情" in silence_message)or("寶貝" in silence_message)or("喜歡卡米" in silence_message)or("愛" in silence_message)or("溫暖" in silence_message):
    #         flag_silence=4                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，愛你模式") 
    #     elif("簡" in silence_message)or("酷" in silence_message)or("短" in silence_message)or("重點" in silence_message)or("太多" in silence_message):
    #         flag_silence=5                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，簡短模式")   
    #     elif("難過" in silence_message)or("傷心" in silence_message)or("可憐" in silence_message)or("哭" in silence_message)or("悲觀" in silence_message):
    #         flag_silence=6                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，難過模式")   
    #     elif("媽" in silence_message)or("姨" in silence_message)or("回家" in silence_message)or("煮" in silence_message)or("掃" in silence_message):
    #         flag_silence=7                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")   
    #     elif("羞" in silence_message):
    #         flag_silence=8                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")             
    #     elif("符號" in silence_message)or("貼圖" in silence_message)or("表情" in silence_message)or("🤣" in silence_message)or("😀" in silence_message)or("🙂" in silence_message):
    #         flag_silence=9                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，Emoji模式")               
    #     elif("樂觀" in silence_message)or("熱情" in silence_message)or("興" in silence_message)or("開心" in silence_message):
    #         flag_silence=10                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，開心模式")
    #     elif("不乖" in silence_message)or("怕" in silence_message)or("揍" in silence_message)or("欠" in silence_message):
    #         flag_silence=11                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，害怕模式") 
    #     elif("老師" in silence_message)or("國文" in silence_message)or("文言文" in silence_message)or("古文" in silence_message):
    #         flag_silence=12                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，老師模式") 
    #     elif("胡" in silence_message)or("亂" in silence_message)or("中二" in silence_message)or("幻" in silence_message):
    #         flag_silence=13                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，亂說模式") 
    #     elif("寵物" in silence_message)or("兔兔" in silence_message):
    #         flag_silence=14                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，寵物模式")              
    #     elif("兵" in silence_message)or("軍" in silence_message):
    #         flag_silence=15                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，軍官模式") 
    #     elif("姨" in silence_message)or("三八" in silence_message)or("婆" in silence_message):
    #         flag_silence=16                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，三八模式") 
    #     elif("王" in silence_message)or("皇" in silence_message):
    #         flag_silence=17                                                # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，皇帝模式") 
    #     elif("律" in silence_message)or("憲" in silence_message)or("規" in silence_message):
    #         flag_silence=18                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，律師模式") 
    #     elif("巴結" in silence_message)or("討" in silence_message)or("諂媚" in silence_message):
    #         flag_silence=19                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，奸商模式") 
    #     elif("宗教" in silence_message)or("信" in silence_message)or("神父" in silence_message):
    #         flag_silence=20                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，神父模式") 
    #     elif("妹妹" in silence_message)or("童" in silence_message)or("孩" in silence_message) :
    #         flag_silence=21                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，女孩模式") 
    #     elif("閩南" in silence_message)or("台語" in silence_message):
    #         flag_silence=22                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，台語模式")                                                            
    #     elif("誇" in silence_message)or("謠" in silence_message)or("記者" in silence_message):
    #         flag_silence=23                                                 # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，誇大模式") 
    #     elif("自戀" in silence_message)or("帥" in silence_message)or("美" in silence_message):
    #         flag_silence=24                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，自戀模式")                                                                     
    #         flag_silence=0                                                   # timer mode
    #         silence_change=1                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"好喔好喔~")    

    # # 1. active mode (always active)
    # elif (flag_silence==1):
    #     if  ("正常模式" in silence_message)or ("一般模式" in silence_message) or ("普通模式" in silence_message):
    #         flag_silence=0                                                   # timer mode
    #         silence_change=2                                                 # it can reply & recode  
    #     elif("狡" in silence_message)or("貪" in silence_message)or("壞" in silence_message):
    #         flag_silence=1                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，狡滑模式")             
    #     elif("甜" in silence_message)or("情" in silence_message)or("溫暖" in silence_message):
    #         flag_silence=4                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，愛你模式") 
    #     elif("簡" in silence_message)or("短" in silence_message)or("重點" in silence_message):
    #         flag_silence=5                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，簡短模式")   
    #     elif ("安靜" in silence_message) or ("閉嘴" in silence_message) or ("吵" in silence_message) or ("關機" in silence_message) or ("去睡覺" in silence_message) or ("休息" in silence_message):
    #         flag_marv=2                                                   # silence mode
    #         silence_change=1                                                 # it can reply & recode & show specail word
    #         line_bot_api.reply_message(event.reply_token,text_message)          # line output            
    #     elif("難過" in silence_message)or("傷心" in silence_message):
    #         flag_silence=6                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，難過模式")   
    #     elif("媽" in silence_message)or("姨" in silence_message)or("回家" in silence_message):
    #         flag_silence=7                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")   
    #     elif("羞" in silence_message):
    #         flag_silence=8                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")             
    #     elif("符號" in silence_message)or("貼圖" in silence_message):
    #         flag_silence=9                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，Emoji模式")               
    #     elif("樂觀" in silence_message)or("熱情" in silence_message)or("興" in silence_message)or("開心" in silence_message):
    #         flag_silence=10                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，開心模式")
    #     elif("不乖" in silence_message)or("怕" in silence_message)or("揍" in silence_message)or("欠" in silence_message):
    #         flag_silence=11                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，害怕模式") 
    #     elif("老師" in silence_message)or("國文" in silence_message)or("文言文" in silence_message):
    #         flag_silence=12                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，老師模式") 
    #     elif("胡" in silence_message)or("亂" in silence_message)or("中二" in silence_message)or("幻" in silence_message):
    #         flag_silence=13                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，亂說模式") 
    #     elif("寵物" in silence_message)or("兔兔" in silence_message):
    #         flag_silence=14                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，寵物模式")      
    #     elif("兵" in silence_message)or("軍" in silence_message):
    #         flag_silence=15                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，軍官模式") 
    #     elif("姨" in silence_message)or("三八" in silence_message)or("婆" in silence_message):
    #         flag_silence=16                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，三八模式") 
    #     elif("王" in silence_message)or("皇" in silence_message):
    #         flag_silence=17                                                # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，皇帝模式") 
    #     elif("律" in silence_message)or("憲" in silence_message)or("規" in silence_message):
    #         flag_silence=18                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，律師模式") 
    #     elif("巴結" in silence_message)or("討" in silence_message)or("諂媚" in silence_message):
    #         flag_silence=19                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，奸商模式") 
    #     elif("宗教" in silence_message)or("信" in silence_message)or("神父" in silence_message):
    #         flag_silence=20                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，神父模式") 
    #     elif("妹妹" in silence_message)or("童" in silence_message)or("孩" in silence_message) :
    #         flag_silence=21                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，女孩模式") 
    #     elif("閩南" in silence_message)or("台語" in silence_message):
    #         flag_silence=22                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，台語模式")                                                            
    #     elif("誇" in silence_message)or("謠" in silence_message)or("記者" in silence_message):
    #         flag_silence=23                                                 # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，誇大模式") 
    #     elif("自戀" in silence_message)or("帥" in silence_message)or("美" in silence_message):
    #         flag_silence=24                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，自戀模式")                                                                     
    #         flag_silence=0                                                   # timer mode
    #         silence_change=1                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"好喔好喔~")    

    # # 3. Marv mode
    # elif (flag_silence==3):
    #     if  ("正常模式" in silence_message)or ("一般模式" in silence_message) or ("普通模式" in silence_message):
    #         flag_silence=0                                                   # timer mode
    #         silence_change=2                                                 # it can reply & recode  
    #     elif("狡" in silence_message)or("貪" in silence_message)or("壞" in silence_message):
    #         flag_silence=1                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，狡滑模式")             
    #     elif("甜" in silence_message)or("情" in silence_message)or("溫暖" in silence_message):
    #         flag_silence=4                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，愛你模式") 
    #     elif("簡" in silence_message)or("短" in silence_message)or("重點" in silence_message):
    #         flag_silence=5                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，簡短模式")   
    #     elif ("安靜" in silence_message) or ("閉嘴" in silence_message) or ("吵" in silence_message) or ("關機" in silence_message) or ("去睡覺" in silence_message) or ("休息" in silence_message):
    #         flag_marv=2                                                   # silence mode
    #         silence_change=1                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"好的，卡米兔休息")
    #         line_bot_api.reply_message(event.reply_token,text_message)          # line output                 line_bot_api.reply_message(event.reply_token,text_message)          # line output            
    #     elif("難過" in silence_message)or("傷心" in silence_message):
    #         flag_silence=6                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，難過模式")   
    #     elif("媽" in silence_message)or("姨" in silence_message)or("回家" in silence_message):
    #         flag_silence=7                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")   
    #     elif("羞" in silence_message):
    #         flag_silence=8                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")             
    #     elif("符號" in silence_message)or("貼圖" in silence_message):
    #         flag_silence=9                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，Emoji模式")               
    #     elif("樂觀" in silence_message)or("熱情" in silence_message)or("興" in silence_message)or("開心" in silence_message):
    #         flag_silence=10                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，開心模式")
    #     elif("不乖" in silence_message)or("怕" in silence_message)or("揍" in silence_message)or("欠" in silence_message):
    #         flag_silence=11                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，害怕模式") 
    #     elif("老師" in silence_message)or("國文" in silence_message)or("文言文" in silence_message):
    #         flag_silence=12                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，老師模式") 
    #     elif("胡" in silence_message)or("亂" in silence_message)or("中二" in silence_message)or("幻" in silence_message):
    #         flag_silence=13                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，亂說模式") 
    #     elif("寵物" in silence_message)or("兔兔" in silence_message):
    #         flag_silence=14                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，寵物模式")      
    #     elif("兵" in silence_message)or("軍" in silence_message):
    #         flag_silence=15                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，軍官模式") 
    #     elif("姨" in silence_message)or("三八" in silence_message)or("婆" in silence_message):
    #         flag_silence=16                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，三八模式") 
    #     elif("王" in silence_message)or("皇" in silence_message):
    #         flag_silence=17                                                # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，皇帝模式") 
    #     elif("律" in silence_message)or("憲" in silence_message)or("規" in silence_message):
    #         flag_silence=18                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，律師模式") 
    #     elif("巴結" in silence_message)or("討" in silence_message)or("諂媚" in silence_message):
    #         flag_silence=19                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，奸商模式") 
    #     elif("宗教" in silence_message)or("信" in silence_message)or("神父" in silence_message):
    #         flag_silence=20                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，神父模式") 
    #     elif("妹妹" in silence_message)or("童" in silence_message)or("孩" in silence_message) :
    #         flag_silence=21                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，女孩模式") 
    #     elif("閩南" in silence_message)or("台語" in silence_message):
    #         flag_silence=22                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，台語模式")                                                            
    #     elif("誇" in silence_message)or("謠" in silence_message)or("記者" in silence_message):
    #         flag_silence=23                                                 # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，誇大模式") 
    #     elif("自戀" in silence_message)or("帥" in silence_message)or("美" in silence_message):
    #         flag_silence=24                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，自戀模式")                                                                     
    # # 4. Lover mode
    # elif (flag_silence==4):
    #     if  ("正常模式" in silence_message)or ("一般模式" in silence_message) or ("普通模式" in silence_message):
    #         flag_silence=0                                                   # timer mode
    #         silence_change=2                                                 # it can reply & recode  
    #     elif("不爽" in silence_message):
    #         flag_silence=3                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，不爽模式")    
    #     elif("簡" in silence_message)or("酷" in silence_message)or("短" in silence_message)or("重點" in silence_message)or("太多" in silence_message):
    #         flag_silence=5                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，簡短模式")   
    #     elif ("安靜" in silence_message) or ("閉嘴" in silence_message) or ("吵" in silence_message) or ("關機" in silence_message) or ("去睡覺" in silence_message) or ("休息" in silence_message):
    #         flag_marv=2                                                   # silence mode
    #         silence_change=1                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"好的，卡米兔休息")
    #         line_bot_api.reply_message(event.reply_token,text_message)          # line output             line_bot_api.reply_message(event.reply_token,text_message)          # line output            
    #     elif("難過" in silence_message)or("傷心" in silence_message):
    #         flag_silence=6                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，難過模式")   
    #     elif("媽" in silence_message)or("姨" in silence_message)or("回家" in silence_message):
    #         flag_silence=7                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")   
    #     elif("羞" in silence_message):
    #         flag_silence=8                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")             
    #     elif("符號" in silence_message)or("貼圖" in silence_message):
    #         flag_silence=9                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，Emoji模式")               
    #     elif("樂觀" in silence_message)or("熱情" in silence_message)or("興" in silence_message)or("開心" in silence_message):
    #         flag_silence=10                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，開心模式")
    #     elif("不乖" in silence_message)or("怕" in silence_message)or("揍" in silence_message)or("欠" in silence_message):
    #         flag_silence=11                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，害怕模式") 
    #     elif("老師" in silence_message)or("國文" in silence_message)or("文言文" in silence_message):
    #         flag_silence=12                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，老師模式") 
    #     elif("胡" in silence_message)or("亂" in silence_message)or("中二" in silence_message)or("幻" in silence_message):
    #         flag_silence=13                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，亂說模式") 
    #     elif("寵物" in silence_message)or("兔兔" in silence_message):
    #         flag_silence=14                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，寵物模式")    
    #     elif("兵" in silence_message)or("軍" in silence_message):
    #         flag_silence=15                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，軍官模式") 
    #     elif("姨" in silence_message)or("三八" in silence_message)or("婆" in silence_message):
    #         flag_silence=16                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，三八模式") 
    #     elif("王" in silence_message)or("皇" in silence_message):
    #         flag_silence=17                                                # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，皇帝模式") 
    #     elif("律" in silence_message)or("憲" in silence_message)or("規" in silence_message):
    #         flag_silence=18                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，律師模式") 
    #     elif("巴結" in silence_message)or("討" in silence_message)or("諂媚" in silence_message):
    #         flag_silence=19                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，奸商模式") 
    #     elif("宗教" in silence_message)or("信" in silence_message)or("神父" in silence_message):
    #         flag_silence=20                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，神父模式") 
    #     elif("妹妹" in silence_message)or("童" in silence_message)or("孩" in silence_message) :
    #         flag_silence=21                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，女孩模式") 
    #     elif("閩南" in silence_message)or("台語" in silence_message):
    #         flag_silence=22                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，台語模式")                                                            
    #     elif("誇" in silence_message)or("謠" in silence_message)or("記者" in silence_message):
    #         flag_silence=23                                                 # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，誇大模式") 
    #     elif("自戀" in silence_message)or("帥" in silence_message)or("美" in silence_message):
    #         flag_silence=24                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，自戀模式")                                                                               
    # # 5. Short mode
    # elif (flag_silence==5):
    #     if  ("正常模式" in silence_message)or ("一般模式" in silence_message) or ("普通模式" in silence_message):
    #         flag_silence=0                                                   # timer mode
    #         silence_change=2                                                 # it can reply & recode  
    #     elif("狡" in silence_message)or("貪" in silence_message)or("壞" in silence_message):
    #         flag_silence=1                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，狡滑模式")                    
    #     elif("不爽" in silence_message) or ("造反" in silence_message)or ("沒禮貌" in silence_message)or ("怎樣" in silence_message)or ("靠" in silence_message)or ("幹" in silence_message)or ("馬的" in silence_message):
    #         flag_silence=3                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，不爽模式")    
    #     elif("甜" in silence_message)or("情" in silence_message)or("寶貝" in silence_message)or("喜歡卡米" in silence_message)or("愛你" in silence_message)or("愛人" in silence_message)or("溫暖" in silence_message):
    #         flag_silence=4                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，愛你模式") 
    #     elif ("安靜" in silence_message) or ("閉嘴" in silence_message) or ("吵" in silence_message) or ("關機" in silence_message) or ("去睡覺" in silence_message) or ("休息" in silence_message):
    #         flag_marv=2                                                   # silence mode
    #         silence_change=1                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"好的，卡米兔休息")  
    #         line_bot_api.reply_message(event.reply_token,text_message)          # line output             line_bot_api.reply_message(event.reply_token,text_message)          # line output            

    #     elif("難過" in silence_message)or("傷心" in silence_message):
    #         flag_silence=6                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，難過模式")   
    #     elif("媽" in silence_message)or("姨" in silence_message)or("回家" in silence_message):
    #         flag_silence=7                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")   
    #     elif("羞" in silence_message):
    #         flag_silence=8                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")             
    #     elif("符號" in silence_message)or("貼圖" in silence_message):
    #         flag_silence=9                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，Emoji模式")               
    #     elif("樂觀" in silence_message)or("熱情" in silence_message)or("興" in silence_message)or("開心" in silence_message):
    #         flag_silence=10                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，開心模式")
    #     elif("不乖" in silence_message)or("怕" in silence_message)or("揍" in silence_message)or("欠" in silence_message):
    #         flag_silence=11                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，害怕模式") 
    #     elif("老師" in silence_message)or("國文" in silence_message)or("文言文" in silence_message):
    #         flag_silence=12                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，老師模式") 
    #     elif("胡" in silence_message)or("亂" in silence_message)or("中二" in silence_message)or("幻" in silence_message):
    #         flag_silence=13                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，亂說模式") 
    #     elif("寵物" in silence_message)or("兔兔" in silence_message):
    #         flag_silence=14                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，寵物模式")   
    #     elif("兵" in silence_message)or("軍" in silence_message):
    #         flag_silence=15                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，軍官模式") 
    #     elif("姨" in silence_message)or("三八" in silence_message)or("婆" in silence_message):
    #         flag_silence=16                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，三八模式") 
    #     elif("王" in silence_message)or("皇" in silence_message):
    #         flag_silence=17                                                # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，皇帝模式") 
    #     elif("律" in silence_message)or("憲" in silence_message)or("規" in silence_message):
    #         flag_silence=18                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，律師模式") 
    #     elif("巴結" in silence_message)or("討" in silence_message)or("諂媚" in silence_message):
    #         flag_silence=19                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，奸商模式") 
    #     elif("宗教" in silence_message)or("信" in silence_message)or("神父" in silence_message):
    #         flag_silence=20                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，神父模式") 
    #     elif("妹妹" in silence_message)or("童" in silence_message)or("孩" in silence_message) :
    #         flag_silence=21                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，女孩模式") 
    #     elif("閩南" in silence_message)or("台語" in silence_message):
    #         flag_silence=22                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，台語模式")                                                            
    #     elif("誇" in silence_message)or("謠" in silence_message)or("記者" in silence_message):
    #         flag_silence=23                                                 # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，誇大模式") 
    #     elif("自戀" in silence_message)or("帥" in silence_message)or("美" in silence_message):
    #         flag_silence=24                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，自戀模式")                                                            
    # # 6. sad 
    # elif (flag_silence==6):
    #     if  ("正常模式" in silence_message)or ("一般模式" in silence_message) or ("普通模式" in silence_message):
    #         flag_silence=0                                                   # timer mode
    #         silence_change=2                                                 # it can reply & recode  
    #     elif("狡" in silence_message)or("貪" in silence_message)or("壞" in silence_message):
    #         flag_silence=1                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，狡滑模式")             
    #     elif("甜" in silence_message)or("情" in silence_message)or("溫暖" in silence_message):
    #         flag_silence=4                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，愛你模式") 
    #     elif("簡" in silence_message)or("短" in silence_message)or("重點" in silence_message):
    #         flag_silence=5                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，簡短模式")   
    #     elif ("安靜" in silence_message) or ("閉嘴" in silence_message) or ("吵" in silence_message) or ("關機" in silence_message) or ("去睡覺" in silence_message) or ("休息" in silence_message):
    #         flag_marv=2                                                   # silence mode
    #         silence_change=1                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"好的，卡米兔休息")
    #         line_bot_api.reply_message(event.reply_token,text_message)          # line output             line_bot_api.reply_message(event.reply_token,text_message)          # line output            
    #     elif("不爽" in silence_message):
    #         flag_silence=3                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，不爽模式") 
    #     elif("媽" in silence_message)or("姨" in silence_message)or("回家" in silence_message):
    #         flag_silence=7                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")   
    #     elif("羞" in silence_message):
    #         flag_silence=8                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")             
    #     elif("符號" in silence_message)or("貼圖" in silence_message):
    #         flag_silence=9                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，Emoji模式")               
    #     elif("樂觀" in silence_message)or("熱情" in silence_message)or("興" in silence_message)or("開心" in silence_message):
    #         flag_silence=10                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，開心模式")
    #     elif("不乖" in silence_message)or("怕" in silence_message)or("揍" in silence_message)or("欠" in silence_message):
    #         flag_silence=11                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，害怕模式") 
    #     elif("老師" in silence_message)or("國文" in silence_message)or("文言文" in silence_message):
    #         flag_silence=12                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，老師模式") 
    #     elif("胡" in silence_message)or("亂" in silence_message)or("中二" in silence_message)or("幻" in silence_message):
    #         flag_silence=13                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，亂說模式") 
    #     elif("寵物" in silence_message)or("兔兔" in silence_message):
    #         flag_silence=14                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，寵物模式")           
    #     elif("兵" in silence_message)or("軍" in silence_message):
    #         flag_silence=15                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，軍官模式") 
    #     elif("姨" in silence_message)or("三八" in silence_message)or("婆" in silence_message):
    #         flag_silence=16                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，三八模式") 
    #     elif("王" in silence_message)or("皇" in silence_message):
    #         flag_silence=17                                                # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，皇帝模式") 
    #     elif("律" in silence_message)or("憲" in silence_message)or("規" in silence_message):
    #         flag_silence=18                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，律師模式") 
    #     elif("巴結" in silence_message)or("討" in silence_message)or("諂媚" in silence_message):
    #         flag_silence=19                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，奸商模式") 
    #     elif("宗教" in silence_message)or("信" in silence_message)or("神父" in silence_message):
    #         flag_silence=20                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，神父模式") 
    #     elif("妹妹" in silence_message)or("童" in silence_message)or("孩" in silence_message) :
    #         flag_silence=21                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，女孩模式") 
    #     elif("閩南" in silence_message)or("台語" in silence_message):
    #         flag_silence=22                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，台語模式")                                                            
    #     elif("誇" in silence_message)or("謠" in silence_message)or("記者" in silence_message):
    #         flag_silence=23                                                 # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，誇大模式") 
    #     elif("自戀" in silence_message)or("帥" in silence_message)or("美" in silence_message):
    #         flag_silence=24                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，自戀模式")                                                            
    # # 7. mom 
    # elif (flag_silence==7):
    #     if  ("正常模式" in silence_message)or ("一般模式" in silence_message) or ("普通模式" in silence_message):
    #         flag_silence=0                                                   # timer mode
    #         silence_change=2                                                 # it can reply & recode  
    #     elif("狡" in silence_message)or("貪" in silence_message)or("壞" in silence_message):
    #         flag_silence=1                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，狡滑模式")             
    #     elif("甜" in silence_message)or("情" in silence_message)or("溫暖" in silence_message):
    #         flag_silence=4                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，愛你模式") 
    #     elif("簡" in silence_message)or("短" in silence_message)or("重點" in silence_message):
    #         flag_silence=5                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，簡短模式")   
    #     elif ("安靜" in silence_message) or ("閉嘴" in silence_message) or ("吵" in silence_message) or ("關機" in silence_message) or ("去睡覺" in silence_message) or ("休息" in silence_message):
    #         flag_marv=2                                                   # silence mode
    #         silence_change=1                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"好的，卡米兔休息")
    #         line_bot_api.reply_message(event.reply_token,text_message)          # line output             line_bot_api.reply_message(event.reply_token,text_message)          # line output            
    #     elif("不爽" in silence_message):
    #         flag_silence=3                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，不爽模式") 
    #     elif("難過" in silence_message)or("傷心" in silence_message):
    #         flag_silence=6                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，難過模式")   
    #     elif("羞" in silence_message):
    #         flag_silence=8                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")             
    #     elif("符號" in silence_message)or("貼圖" in silence_message):
    #         flag_silence=9                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，Emoji模式")               
    #     elif("樂觀" in silence_message)or("熱情" in silence_message)or("興" in silence_message)or("開心" in silence_message):
    #         flag_silence=10                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，開心模式")
    #     elif("不乖" in silence_message)or("怕" in silence_message)or("揍" in silence_message)or("欠" in silence_message):
    #         flag_silence=11                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，害怕模式") 
    #     elif("老師" in silence_message)or("國文" in silence_message)or("文言文" in silence_message):
    #         flag_silence=12                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，老師模式") 
    #     elif("胡" in silence_message)or("亂" in silence_message)or("中二" in silence_message)or("幻" in silence_message):
    #         flag_silence=13                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，亂說模式") 
    #     elif("寵物" in silence_message)or("兔兔" in silence_message):
    #         flag_silence=14                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，寵物模式") 
    #     elif("兵" in silence_message)or("軍" in silence_message):
    #         flag_silence=15                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，軍官模式") 
    #     elif("姨" in silence_message)or("三八" in silence_message)or("婆" in silence_message):
    #         flag_silence=16                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，三八模式") 
    #     elif("王" in silence_message)or("皇" in silence_message):
    #         flag_silence=17                                                # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，皇帝模式") 
    #     elif("律" in silence_message)or("憲" in silence_message)or("規" in silence_message):
    #         flag_silence=18                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，律師模式") 
    #     elif("巴結" in silence_message)or("討" in silence_message)or("諂媚" in silence_message):
    #         flag_silence=19                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，奸商模式") 
    #     elif("宗教" in silence_message)or("信" in silence_message)or("神父" in silence_message):
    #         flag_silence=20                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，神父模式") 
    #     elif("妹妹" in silence_message)or("童" in silence_message)or("孩" in silence_message) :
    #         flag_silence=21                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，女孩模式") 
    #     elif("閩南" in silence_message)or("台語" in silence_message):
    #         flag_silence=22                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，台語模式")                                                            
    #     elif("誇" in silence_message)or("謠" in silence_message)or("記者" in silence_message):
    #         flag_silence=23                                                 # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，誇大模式") 
    #     elif("自戀" in silence_message)or("帥" in silence_message)or("美" in silence_message):
    #         flag_silence=24                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，自戀模式")                                                            
    # # 8. emoji 
    # elif (flag_silence==8):
    #     if  ("正常模式" in silence_message)or ("一般模式" in silence_message) or ("普通模式" in silence_message):
    #         flag_silence=0                                                   # timer mode
    #         silence_change=2                                                 # it can reply & recode  
    #     elif("狡" in silence_message)or("貪" in silence_message)or("壞" in silence_message):
    #         flag_silence=1                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，狡滑模式")             
    #     elif("甜" in silence_message)or("情" in silence_message)or("溫暖" in silence_message):
    #         flag_silence=4                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，愛你模式") 
    #     elif("簡" in silence_message)or("短" in silence_message)or("重點" in silence_message):
    #         flag_silence=5                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，簡短模式")   
    #     elif ("安靜" in silence_message) or ("閉嘴" in silence_message) or ("吵" in silence_message) or ("關機" in silence_message) or ("去睡覺" in silence_message) or ("休息" in silence_message):
    #         flag_marv=2                                                   # silence mode
    #         silence_change=1                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"好的，卡米兔休息")
    #         line_bot_api.reply_message(event.reply_token,text_message)          # line output             line_bot_api.reply_message(event.reply_token,text_message)          # line output            
    #     elif("不爽" in silence_message):
    #         flag_silence=3                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，不爽模式") 
    #     elif("難過" in silence_message)or("傷心" in silence_message):
    #         flag_silence=6                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，難過模式")   
    #     elif("媽" in silence_message)or("姨" in silence_message)or("回家" in silence_message):
    #         flag_silence=7                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")          
    #     elif("符號" in silence_message)or("貼圖" in silence_message):
    #         flag_silence=9                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，Emoji模式")               
    #     elif("樂觀" in silence_message)or("熱情" in silence_message)or("興" in silence_message)or("開心" in silence_message):
    #         flag_silence=10                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，開心模式")
    #     elif("不乖" in silence_message)or("怕" in silence_message)or("揍" in silence_message)or("欠" in silence_message):
    #         flag_silence=11                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，害怕模式") 
    #     elif("老師" in silence_message)or("國文" in silence_message)or("文言文" in silence_message):
    #         flag_silence=12                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，老師模式") 
    #     elif("胡" in silence_message)or("亂" in silence_message)or("中二" in silence_message)or("幻" in silence_message):
    #         flag_silence=13                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，亂說模式") 
    #     elif("寵物" in silence_message)or("兔兔" in silence_message):
    #         flag_silence=14                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，寵物模式")       
    #     elif("兵" in silence_message)or("軍" in silence_message):
    #         flag_silence=15                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，軍官模式") 
    #     elif("姨" in silence_message)or("三八" in silence_message)or("婆" in silence_message):
    #         flag_silence=16                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，三八模式") 
    #     elif("王" in silence_message)or("皇" in silence_message):
    #         flag_silence=17                                                # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，皇帝模式") 
    #     elif("律" in silence_message)or("憲" in silence_message)or("規" in silence_message):
    #         flag_silence=18                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，律師模式") 
    #     elif("巴結" in silence_message)or("討" in silence_message)or("諂媚" in silence_message):
    #         flag_silence=19                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，奸商模式") 
    #     elif("宗教" in silence_message)or("信" in silence_message)or("神父" in silence_message):
    #         flag_silence=20                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，神父模式") 
    #     elif("妹妹" in silence_message)or("童" in silence_message)or("孩" in silence_message) :
    #         flag_silence=21                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，女孩模式") 
    #     elif("閩南" in silence_message)or("台語" in silence_message):
    #         flag_silence=22                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，台語模式")                                                            
    #     elif("誇" in silence_message)or("謠" in silence_message)or("記者" in silence_message):
    #         flag_silence=23                                                 # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，誇大模式") 
    #     elif("自戀" in silence_message)or("帥" in silence_message)or("美" in silence_message):
    #         flag_silence=24                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，自戀模式")                                                            
    # # 9. emoji 
    # elif (flag_silence==9):
    #     if  ("正常模式" in silence_message)or ("一般模式" in silence_message) or ("普通模式" in silence_message):
    #         flag_silence=0                                                   # timer mode
    #         silence_change=2                                                 # it can reply & recode  
    #     elif("狡" in silence_message)or("貪" in silence_message)or("壞" in silence_message):
    #         flag_silence=1                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，狡滑模式")             
    #     elif("甜" in silence_message)or("情" in silence_message)or("溫暖" in silence_message):
    #         flag_silence=4                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，愛你模式") 
    #     elif("簡" in silence_message)or("短" in silence_message)or("重點" in silence_message):
    #         flag_silence=5                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，簡短模式")   
    #     elif ("安靜" in silence_message) or ("閉嘴" in silence_message) or ("吵" in silence_message) or ("關機" in silence_message) or ("去睡覺" in silence_message) or ("休息" in silence_message):
    #         flag_marv=2                                                   # silence mode
    #         silence_change=1                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"好的，卡米兔休息")
    #         line_bot_api.reply_message(event.reply_token,text_message)          # line output             line_bot_api.reply_message(event.reply_token,text_message)          # line output            
    #     elif("不爽" in silence_message):
    #         flag_silence=3                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，不爽模式") 
    #     elif("難過" in silence_message)or("傷心" in silence_message):
    #         flag_silence=6                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，難過模式")   
    #     elif("媽" in silence_message)or("姨" in silence_message)or("回家" in silence_message):
    #         flag_silence=7                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")   
    #     elif("羞" in silence_message):
    #         flag_silence=8                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")                        
    #     elif("樂觀" in silence_message)or("熱情" in silence_message)or("興" in silence_message)or("開心" in silence_message):
    #         flag_silence=10                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，開心模式")
    #     elif("不乖" in silence_message)or("怕" in silence_message)or("揍" in silence_message)or("欠" in silence_message):
    #         flag_silence=11                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，害怕模式") 
    #     elif("老師" in silence_message)or("國文" in silence_message)or("文言文" in silence_message):
    #         flag_silence=12                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，老師模式") 
    #     elif("胡" in silence_message)or("亂" in silence_message)or("中二" in silence_message)or("幻" in silence_message):
    #         flag_silence=13                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，亂說模式") 
    #     elif("寵物" in silence_message)or("兔兔" in silence_message):
    #         flag_silence=14                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，寵物模式") 
    #     elif("兵" in silence_message)or("軍" in silence_message):
    #         flag_silence=15                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，軍官模式") 
    #     elif("姨" in silence_message)or("三八" in silence_message)or("婆" in silence_message):
    #         flag_silence=16                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，三八模式") 
    #     elif("王" in silence_message)or("皇" in silence_message):
    #         flag_silence=17                                                # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，皇帝模式") 
    #     elif("律" in silence_message)or("憲" in silence_message)or("規" in silence_message):
    #         flag_silence=18                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，律師模式") 
    #     elif("巴結" in silence_message)or("討" in silence_message)or("諂媚" in silence_message):
    #         flag_silence=19                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，奸商模式") 
    #     elif("宗教" in silence_message)or("信" in silence_message)or("神父" in silence_message):
    #         flag_silence=20                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，神父模式") 
    #     elif("妹妹" in silence_message)or("童" in silence_message)or("孩" in silence_message) :
    #         flag_silence=21                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，女孩模式") 
    #     elif("閩南" in silence_message)or("台語" in silence_message):
    #         flag_silence=22                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，台語模式")                                                            
    #     elif("誇" in silence_message)or("謠" in silence_message)or("記者" in silence_message):
    #         flag_silence=23                                                 # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，誇大模式") 
    #     elif("自戀" in silence_message)or("帥" in silence_message)or("美" in silence_message):
    #         flag_silence=24                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，自戀模式")                                                            
    # # 10.happy 
    # elif (flag_silence==10):
    #     if  ("正常模式" in silence_message)or ("一般模式" in silence_message) or ("普通模式" in silence_message):
    #         flag_silence=0                                                   # timer mode
    #         silence_change=2                                                 # it can reply & recode  
    #     elif("狡" in silence_message)or("貪" in silence_message)or("壞" in silence_message):
    #         flag_silence=1                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，狡滑模式")             
    #     elif("甜" in silence_message)or("情" in silence_message)or("溫暖" in silence_message):
    #         flag_silence=4                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，愛你模式") 
    #     elif("簡" in silence_message)or("短" in silence_message)or("重點" in silence_message):
    #         flag_silence=5                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，簡短模式")   
    #     elif ("安靜" in silence_message) or ("閉嘴" in silence_message) or ("吵" in silence_message) or ("關機" in silence_message) or ("去睡覺" in silence_message) or ("休息" in silence_message):
    #         flag_marv=2                                                   # silence mode
    #         silence_change=1                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"好的，卡米兔休息")
    #         line_bot_api.reply_message(event.reply_token,text_message)          # line output             line_bot_api.reply_message(event.reply_token,text_message)          # line output            
    #     elif("不爽" in silence_message):
    #         flag_silence=3                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，不爽模式") 
    #     elif("難過" in silence_message)or("傷心" in silence_message):
    #         flag_silence=6                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，難過模式")   
    #     elif("媽" in silence_message)or("姨" in silence_message)or("回家" in silence_message):
    #         flag_silence=7                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")   
    #     elif("羞" in silence_message):
    #         flag_silence=8                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")             
    #     elif("符號" in silence_message)or("貼圖" in silence_message):
    #         flag_silence=9                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，Emoji模式")               
    #     elif("不乖" in silence_message)or("怕" in silence_message)or("揍" in silence_message)or("欠" in silence_message):
    #         flag_silence=11                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，害怕模式") 
    #     elif("老師" in silence_message)or("國文" in silence_message)or("文言文" in silence_message):
    #         flag_silence=12                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，老師模式") 
    #     elif("胡" in silence_message)or("亂" in silence_message)or("中二" in silence_message)or("幻" in silence_message):
    #         flag_silence=13                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，亂說模式") 
    #     elif("寵物" in silence_message)or("兔兔" in silence_message):
    #         flag_silence=14                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，寵物模式") 
    #     elif("兵" in silence_message)or("軍" in silence_message):
    #         flag_silence=15                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，軍官模式") 
    #     elif("姨" in silence_message)or("三八" in silence_message)or("婆" in silence_message):
    #         flag_silence=16                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，三八模式") 
    #     elif("王" in silence_message)or("皇" in silence_message):
    #         flag_silence=17                                                # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，皇帝模式") 
    #     elif("律" in silence_message)or("憲" in silence_message)or("規" in silence_message):
    #         flag_silence=18                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，律師模式") 
    #     elif("巴結" in silence_message)or("討" in silence_message)or("諂媚" in silence_message):
    #         flag_silence=19                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，奸商模式") 
    #     elif("宗教" in silence_message)or("信" in silence_message)or("神父" in silence_message):
    #         flag_silence=20                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，神父模式") 
    #     elif("妹妹" in silence_message)or("童" in silence_message)or("孩" in silence_message) :
    #         flag_silence=21                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，女孩模式") 
    #     elif("閩南" in silence_message)or("台語" in silence_message):
    #         flag_silence=22                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，台語模式")                                                            
    #     elif("誇" in silence_message)or("謠" in silence_message)or("記者" in silence_message):
    #         flag_silence=23                                                 # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，誇大模式") 
    #     elif("自戀" in silence_message)or("帥" in silence_message)or("美" in silence_message):
    #         flag_silence=24                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，自戀模式")                                                            
    # # 11.fear 
    # elif (flag_silence==11):
    #     if  ("正常模式" in silence_message)or ("一般模式" in silence_message) or ("普通模式" in silence_message):
    #         flag_silence=0                                                   # timer mode
    #         silence_change=2                                                 # it can reply & recode  
    #     elif("狡" in silence_message)or("貪" in silence_message)or("壞" in silence_message):
    #         flag_silence=1                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，狡滑模式")             
    #     elif("甜" in silence_message)or("情" in silence_message)or("溫暖" in silence_message):
    #         flag_silence=4                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，愛你模式") 
    #     elif("簡" in silence_message)or("短" in silence_message)or("重點" in silence_message):
    #         flag_silence=5                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，簡短模式")   
    #     elif ("安靜" in silence_message) or ("閉嘴" in silence_message) or ("吵" in silence_message) or ("關機" in silence_message) or ("去睡覺" in silence_message) or ("休息" in silence_message):
    #         flag_marv=2                                                   # silence mode
    #         silence_change=1                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"好的，卡米兔休息")
    #         line_bot_api.reply_message(event.reply_token,text_message)          # line output             line_bot_api.reply_message(event.reply_token,text_message)          # line output            
    #     elif("不爽" in silence_message):
    #         flag_silence=3                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，不爽模式") 
    #     elif("難過" in silence_message)or("傷心" in silence_message):
    #         flag_silence=6                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，難過模式")   
    #     elif("媽" in silence_message)or("姨" in silence_message)or("回家" in silence_message):
    #         flag_silence=7                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")   
    #     elif("羞" in silence_message):
    #         flag_silence=8                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")             
    #     elif("符號" in silence_message)or("貼圖" in silence_message):
    #         flag_silence=9                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，Emoji模式")               
    #     elif("樂觀" in silence_message)or("熱情" in silence_message)or("興" in silence_message)or("開心" in silence_message):
    #         flag_silence=10                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，開心模式")
    #     elif("老師" in silence_message)or("國文" in silence_message)or("文言文" in silence_message):
    #         flag_silence=12                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，老師模式") 
    #     elif("胡" in silence_message)or("亂" in silence_message)or("中二" in silence_message)or("幻" in silence_message):
    #         flag_silence=13                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，亂說模式") 
    #     elif("寵物" in silence_message)or("兔兔" in silence_message):
    #         flag_silence=14                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，寵物模式")       
    #     elif("兵" in silence_message)or("軍" in silence_message):
    #         flag_silence=15                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，軍官模式") 
    #     elif("姨" in silence_message)or("三八" in silence_message)or("婆" in silence_message):
    #         flag_silence=16                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，三八模式") 
    #     elif("王" in silence_message)or("皇" in silence_message):
    #         flag_silence=17                                                # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，皇帝模式") 
    #     elif("律" in silence_message)or("憲" in silence_message)or("規" in silence_message):
    #         flag_silence=18                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，律師模式") 
    #     elif("巴結" in silence_message)or("討" in silence_message)or("諂媚" in silence_message):
    #         flag_silence=19                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，奸商模式") 
    #     elif("宗教" in silence_message)or("信" in silence_message)or("神父" in silence_message):
    #         flag_silence=20                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，神父模式") 
    #     elif("妹妹" in silence_message)or("童" in silence_message)or("孩" in silence_message) :
    #         flag_silence=21                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，女孩模式") 
    #     elif("閩南" in silence_message)or("台語" in silence_message):
    #         flag_silence=22                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，台語模式")                                                            
    #     elif("誇" in silence_message)or("謠" in silence_message)or("記者" in silence_message):
    #         flag_silence=23                                                 # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，誇大模式") 
    #     elif("自戀" in silence_message)or("帥" in silence_message)or("美" in silence_message):
    #         flag_silence=24                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，自戀模式")                                                            
    # # 12.teacher 
    # elif (flag_silence==12):
    #     if  ("正常模式" in silence_message)or ("一般模式" in silence_message) or ("普通模式" in silence_message):
    #         flag_silence=0                                                   # timer mode
    #         silence_change=2                                                 # it can reply & recode  
    #     elif("狡" in silence_message)or("貪" in silence_message)or("壞" in silence_message):
    #         flag_silence=1                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，狡滑模式")             
    #     elif("甜" in silence_message)or("情" in silence_message)or("溫暖" in silence_message):
    #         flag_silence=4                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，愛你模式") 
    #     elif("簡" in silence_message)or("短" in silence_message)or("重點" in silence_message):
    #         flag_silence=5                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，簡短模式")   
    #     elif ("安靜" in silence_message) or ("閉嘴" in silence_message) or ("吵" in silence_message) or ("關機" in silence_message) or ("去睡覺" in silence_message) or ("休息" in silence_message):
    #         flag_marv=2                                                   # silence mode
    #         silence_change=1                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"好的，卡米兔休息")
    #         line_bot_api.reply_message(event.reply_token,text_message)          # line output             line_bot_api.reply_message(event.reply_token,text_message)          # line output            
    #     elif("不爽" in silence_message):
    #         flag_silence=3                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，不爽模式") 
    #     elif("難過" in silence_message)or("傷心" in silence_message):
    #         flag_silence=6                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，難過模式")   
    #     elif("媽" in silence_message)or("姨" in silence_message)or("回家" in silence_message):
    #         flag_silence=7                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")   
    #     elif("羞" in silence_message):
    #         flag_silence=8                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")             
    #     elif("符號" in silence_message)or("貼圖" in silence_message):
    #         flag_silence=9                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，Emoji模式")               
    #     elif("樂觀" in silence_message)or("熱情" in silence_message)or("興" in silence_message)or("開心" in silence_message):
    #         flag_silence=10                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，開心模式")
    #     elif("不乖" in silence_message)or("怕" in silence_message)or("揍" in silence_message)or("欠" in silence_message):
    #         flag_silence=11                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，害怕模式") 
    #     elif("胡" in silence_message)or("亂" in silence_message)or("中二" in silence_message)or("幻" in silence_message):
    #         flag_silence=13                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，亂說模式") 
    #     elif("寵物" in silence_message)or("兔兔" in silence_message):
    #         flag_silence=14                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，寵物模式")       
    #     elif("兵" in silence_message)or("軍" in silence_message):
    #         flag_silence=15                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，軍官模式") 
    #     elif("姨" in silence_message)or("三八" in silence_message)or("婆" in silence_message):
    #         flag_silence=16                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，三八模式") 
    #     elif("王" in silence_message)or("皇" in silence_message):
    #         flag_silence=17                                                # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，皇帝模式") 
    #     elif("律" in silence_message)or("憲" in silence_message)or("規" in silence_message):
    #         flag_silence=18                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，律師模式") 
    #     elif("巴結" in silence_message)or("討" in silence_message)or("諂媚" in silence_message):
    #         flag_silence=19                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，奸商模式") 
    #     elif("宗教" in silence_message)or("信" in silence_message)or("神父" in silence_message):
    #         flag_silence=20                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，神父模式") 
    #     elif("妹妹" in silence_message)or("童" in silence_message)or("孩" in silence_message) :
    #         flag_silence=21                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，女孩模式") 
    #     elif("閩南" in silence_message)or("台語" in silence_message):
    #         flag_silence=22                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，台語模式")                                                            
    #     elif("誇" in silence_message)or("謠" in silence_message)or("記者" in silence_message):
    #         flag_silence=23                                                 # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，誇大模式") 
    #     elif("自戀" in silence_message)or("帥" in silence_message)or("美" in silence_message):
    #         flag_silence=24                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，自戀模式")                                                            
    # # 13.casually 
    # elif (flag_silence==13):
    #     if  ("正常模式" in silence_message)or ("一般模式" in silence_message) or ("普通模式" in silence_message):
    #         flag_silence=0                                                   # timer mode
    #         silence_change=2                                                 # it can reply & recode  
    #     elif("狡" in silence_message)or("貪" in silence_message)or("壞" in silence_message):
    #         flag_silence=1                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，狡滑模式")             
    #     elif("甜" in silence_message)or("情" in silence_message)or("溫暖" in silence_message):
    #         flag_silence=4                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，愛你模式") 
    #     elif("簡" in silence_message)or("短" in silence_message)or("重點" in silence_message):
    #         flag_silence=5                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，簡短模式")   
    #     elif ("安靜" in silence_message) or ("閉嘴" in silence_message) or ("吵" in silence_message) or ("關機" in silence_message) or ("去睡覺" in silence_message) or ("休息" in silence_message):
    #         flag_marv=2                                                   # silence mode
    #         silence_change=1                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"好的，卡米兔休息")
    #         line_bot_api.reply_message(event.reply_token,text_message)          # line output             line_bot_api.reply_message(event.reply_token,text_message)          # line output            
    #     elif("不爽" in silence_message):
    #         flag_silence=3                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，不爽模式") 
    #     elif("難過" in silence_message)or("傷心" in silence_message):
    #         flag_silence=6                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，難過模式")   
    #     elif("媽" in silence_message)or("姨" in silence_message)or("回家" in silence_message):
    #         flag_silence=7                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")   
    #     elif("羞" in silence_message):
    #         flag_silence=8                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")             
    #     elif("符號" in silence_message)or("貼圖" in silence_message):
    #         flag_silence=9                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，Emoji模式")               
    #     elif("樂觀" in silence_message)or("熱情" in silence_message)or("興" in silence_message)or("開心" in silence_message):
    #         flag_silence=10                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，開心模式")
    #     elif("不乖" in silence_message)or("怕" in silence_message)or("揍" in silence_message)or("欠" in silence_message):
    #         flag_silence=11                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，害怕模式") 
    #     elif("老師" in silence_message)or("國文" in silence_message)or("文言文" in silence_message):
    #         flag_silence=12                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，老師模式") 
    #     elif("寵物" in silence_message)or("兔兔" in silence_message):
    #         flag_silence=14                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，寵物模式")       
    #     elif("兵" in silence_message)or("軍" in silence_message):
    #         flag_silence=15                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，軍官模式") 
    #     elif("姨" in silence_message)or("三八" in silence_message)or("婆" in silence_message):
    #         flag_silence=16                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，三八模式") 
    #     elif("王" in silence_message)or("皇" in silence_message):
    #         flag_silence=17                                                # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，皇帝模式") 
    #     elif("律" in silence_message)or("憲" in silence_message)or("規" in silence_message):
    #         flag_silence=18                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，律師模式") 
    #     elif("巴結" in silence_message)or("討" in silence_message)or("諂媚" in silence_message):
    #         flag_silence=19                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，奸商模式") 
    #     elif("宗教" in silence_message)or("信" in silence_message)or("神父" in silence_message):
    #         flag_silence=20                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，神父模式") 
    #     elif("妹妹" in silence_message)or("童" in silence_message)or("孩" in silence_message) :
    #         flag_silence=21                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，女孩模式") 
    #     elif("閩南" in silence_message)or("台語" in silence_message):
    #         flag_silence=22                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，台語模式")                                                            
    #     elif("誇" in silence_message)or("謠" in silence_message)or("記者" in silence_message):
    #         flag_silence=23                                                 # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，誇大模式") 
    #     elif("自戀" in silence_message)or("帥" in silence_message)or("美" in silence_message):
    #         flag_silence=24                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，自戀模式")                                                            
    # # 14.pet 
    # elif (flag_silence==14):
    #     if  ("正常模式" in silence_message)or ("一般模式" in silence_message) or ("普通模式" in silence_message):
    #         flag_silence=0                                                   # timer mode
    #         silence_change=2                                                 # it can reply & recode  
    #     elif("狡" in silence_message)or("貪" in silence_message)or("壞" in silence_message):
    #         flag_silence=1                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，狡滑模式")             
    #     elif("甜" in silence_message)or("情" in silence_message)or("溫暖" in silence_message):
    #         flag_silence=4                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，愛你模式") 
    #     elif("簡" in silence_message)or("短" in silence_message)or("重點" in silence_message):
    #         flag_silence=5                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，簡短模式")   
    #     elif ("安靜" in silence_message) or ("閉嘴" in silence_message) or ("吵" in silence_message) or ("關機" in silence_message) or ("去睡覺" in silence_message) or ("休息" in silence_message):
    #         flag_marv=2                                                   # silence mode
    #         silence_change=1                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"好的，卡米兔休息")
    #         line_bot_api.reply_message(event.reply_token,text_message)          # line output             line_bot_api.reply_message(event.reply_token,text_message)          # line output            
    #     elif("不爽" in silence_message):
    #         flag_silence=3                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，不爽模式") 
    #     elif("難過" in silence_message)or("傷心" in silence_message):
    #         flag_silence=6                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，難過模式")   
    #     elif("媽" in silence_message)or("姨" in silence_message)or("回家" in silence_message):
    #         flag_silence=7                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")   
    #     elif("羞" in silence_message):
    #         flag_silence=8                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")             
    #     elif("符號" in silence_message)or("貼圖" in silence_message):
    #         flag_silence=9                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，Emoji模式")               
    #     elif("樂觀" in silence_message)or("熱情" in silence_message)or("興" in silence_message)or("開心" in silence_message):
    #         flag_silence=10                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，開心模式")
    #     elif("不乖" in silence_message)or("怕" in silence_message)or("揍" in silence_message)or("欠" in silence_message):
    #         flag_silence=11                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，害怕模式") 
    #     elif("老師" in silence_message)or("國文" in silence_message)or("文言文" in silence_message):
    #         flag_silence=12                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，老師模式") 
    #     elif("胡" in silence_message)or("亂" in silence_message)or("中二" in silence_message)or("幻" in silence_message):
    #         flag_silence=13                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，亂說模式") 
    #     elif("兵" in silence_message)or("軍" in silence_message):
    #         flag_silence=15                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，軍官模式") 
    #     elif("姨" in silence_message)or("三八" in silence_message)or("婆" in silence_message):
    #         flag_silence=16                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，三八模式") 
    #     elif("王" in silence_message)or("皇" in silence_message):
    #         flag_silence=17                                                # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，皇帝模式") 
    #     elif("律" in silence_message)or("憲" in silence_message)or("規" in silence_message):
    #         flag_silence=18                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，律師模式") 
    #     elif("巴結" in silence_message)or("討" in silence_message)or("諂媚" in silence_message):
    #         flag_silence=19                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，奸商模式") 
    #     elif("宗教" in silence_message)or("信" in silence_message)or("神父" in silence_message):
    #         flag_silence=20                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，神父模式") 
    #     elif("妹妹" in silence_message)or("童" in silence_message)or("孩" in silence_message) :
    #         flag_silence=21                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，女孩模式") 
    #     elif("閩南" in silence_message)or("台語" in silence_message):
    #         flag_silence=22                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，台語模式")                                                            
    #     elif("誇" in silence_message)or("謠" in silence_message)or("記者" in silence_message):
    #         flag_silence=23                                                 # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，誇大模式") 
    #     elif("自戀" in silence_message)or("帥" in silence_message)or("美" in silence_message):
    #         flag_silence=24                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，自戀模式")                                                            
    # # 15.soldier 
    # elif (flag_silence==15):
    #     if  ("正常模式" in silence_message)or ("一般模式" in silence_message) or ("普通模式" in silence_message):
    #         flag_silence=0                                                   # timer mode
    #         silence_change=2                                                 # it can reply & recode  
    #     elif("狡" in silence_message)or("貪" in silence_message)or("壞" in silence_message):
    #         flag_silence=1                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，狡滑模式")             
    #     elif("甜" in silence_message)or("情" in silence_message)or("溫暖" in silence_message):
    #         flag_silence=4                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，愛你模式") 
    #     elif("簡" in silence_message)or("短" in silence_message)or("重點" in silence_message):
    #         flag_silence=5                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，簡短模式")   
    #     elif ("安靜" in silence_message) or ("閉嘴" in silence_message) or ("吵" in silence_message) or ("關機" in silence_message) or ("去睡覺" in silence_message) or ("休息" in silence_message):
    #         flag_marv=2                                                   # silence mode
    #         silence_change=1                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"好的，卡米兔休息")
    #         line_bot_api.reply_message(event.reply_token,text_message)          # line output             line_bot_api.reply_message(event.reply_token,text_message)          # line output            
    #     elif("不爽" in silence_message):
    #         flag_silence=3                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，不爽模式") 
    #     elif("難過" in silence_message)or("傷心" in silence_message):
    #         flag_silence=6                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，難過模式")   
    #     elif("媽" in silence_message)or("姨" in silence_message)or("回家" in silence_message):
    #         flag_silence=7                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")   
    #     elif("羞" in silence_message):
    #         flag_silence=8                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")             
    #     elif("符號" in silence_message)or("貼圖" in silence_message):
    #         flag_silence=9                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，Emoji模式")               
    #     elif("樂觀" in silence_message)or("熱情" in silence_message)or("興" in silence_message)or("開心" in silence_message):
    #         flag_silence=10                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，開心模式")
    #     elif("不乖" in silence_message)or("怕" in silence_message)or("揍" in silence_message)or("欠" in silence_message):
    #         flag_silence=11                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，害怕模式") 
    #     elif("老師" in silence_message)or("國文" in silence_message)or("文言文" in silence_message):
    #         flag_silence=12                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，老師模式") 
    #     elif("胡" in silence_message)or("亂" in silence_message)or("中二" in silence_message)or("幻" in silence_message):
    #         flag_silence=13                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，亂說模式") 
    #     elif("寵物" in silence_message)or("兔兔" in silence_message):
    #         flag_silence=14                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，寵物模式")       
    #     elif("兵" in silence_message)or("軍" in silence_message):
    #         flag_silence=15                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，軍官模式") 
    #     elif("姨" in silence_message)or("三八" in silence_message)or("婆" in silence_message):
    #         flag_silence=16                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，三八模式") 
    #     elif("王" in silence_message)or("皇" in silence_message):
    #         flag_silence=17                                                # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，皇帝模式") 
    #     elif("律" in silence_message)or("憲" in silence_message)or("規" in silence_message):
    #         flag_silence=18                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，律師模式") 
    #     elif("巴結" in silence_message)or("討" in silence_message)or("諂媚" in silence_message):
    #         flag_silence=19                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，奸商模式") 
    #     elif("宗教" in silence_message)or("信" in silence_message)or("神父" in silence_message):
    #         flag_silence=20                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，神父模式") 
    #     elif("妹妹" in silence_message)or("童" in silence_message)or("孩" in silence_message) :
    #         flag_silence=21                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，女孩模式") 
    #     elif("閩南" in silence_message)or("台語" in silence_message):
    #         flag_silence=22                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，台語模式")                                                            
    #     elif("誇" in silence_message)or("謠" in silence_message)or("記者" in silence_message):
    #         flag_silence=23                                                 # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，誇大模式") 
    #     elif("自戀" in silence_message)or("帥" in silence_message)or("美" in silence_message):
    #         flag_silence=24                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，自戀模式")                                                            
    # # 16. ditzy  
    # elif (flag_silence==16):
    #     if  ("正常模式" in silence_message)or ("一般模式" in silence_message) or ("普通模式" in silence_message):
    #         flag_silence=0                                                   # timer mode
    #         silence_change=2                                                 # it can reply & recode  
    #     elif("狡" in silence_message)or("貪" in silence_message)or("壞" in silence_message):
    #         flag_silence=1                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，狡滑模式")             
    #     elif("甜" in silence_message)or("情" in silence_message)or("溫暖" in silence_message):
    #         flag_silence=4                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，愛你模式") 
    #     elif("簡" in silence_message)or("短" in silence_message)or("重點" in silence_message):
    #         flag_silence=5                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，簡短模式")   
    #     elif ("安靜" in silence_message) or ("閉嘴" in silence_message) or ("吵" in silence_message) or ("關機" in silence_message) or ("去睡覺" in silence_message) or ("休息" in silence_message):
    #         flag_marv=2                                                   # silence mode
    #         silence_change=1                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"好的，卡米兔休息")
    #         line_bot_api.reply_message(event.reply_token,text_message)          # line output             line_bot_api.reply_message(event.reply_token,text_message)          # line output            
    #     elif("不爽" in silence_message):
    #         flag_silence=3                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，不爽模式") 
    #     elif("難過" in silence_message)or("傷心" in silence_message):
    #         flag_silence=6                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，難過模式")   
    #     elif("媽" in silence_message)or("姨" in silence_message)or("回家" in silence_message):
    #         flag_silence=7                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")   
    #     elif("羞" in silence_message):
    #         flag_silence=8                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")             
    #     elif("符號" in silence_message)or("貼圖" in silence_message):
    #         flag_silence=9                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，Emoji模式")               
    #     elif("樂觀" in silence_message)or("熱情" in silence_message)or("興" in silence_message)or("開心" in silence_message):
    #         flag_silence=10                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，開心模式")
    #     elif("不乖" in silence_message)or("怕" in silence_message)or("揍" in silence_message)or("欠" in silence_message):
    #         flag_silence=11                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，害怕模式") 
    #     elif("老師" in silence_message)or("國文" in silence_message)or("文言文" in silence_message):
    #         flag_silence=12                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，老師模式") 
    #     elif("胡" in silence_message)or("亂" in silence_message)or("中二" in silence_message)or("幻" in silence_message):
    #         flag_silence=13                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，亂說模式") 
    #     elif("寵物" in silence_message)or("兔兔" in silence_message):
    #         flag_silence=14                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，寵物模式")       
    #     elif("兵" in silence_message)or("軍" in silence_message):
    #         flag_silence=15                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，軍官模式") 
    #     elif("王" in silence_message)or("皇" in silence_message):
    #         flag_silence=17                                                # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，皇帝模式") 
    #     elif("律" in silence_message)or("憲" in silence_message)or("規" in silence_message):
    #         flag_silence=18                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，律師模式") 
    #     elif("巴結" in silence_message)or("討" in silence_message)or("諂媚" in silence_message):
    #         flag_silence=19                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，奸商模式") 
    #     elif("宗教" in silence_message)or("信" in silence_message)or("神父" in silence_message):
    #         flag_silence=20                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，神父模式") 
    #     elif("妹妹" in silence_message)or("童" in silence_message)or("孩" in silence_message) :
    #         flag_silence=21                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，女孩模式") 
    #     elif("閩南" in silence_message)or("台語" in silence_message):
    #         flag_silence=22                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，台語模式")                                                            
    #     elif("誇" in silence_message)or("謠" in silence_message)or("記者" in silence_message):
    #         flag_silence=23                                                 # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，誇大模式") 
    #     elif("自戀" in silence_message)or("帥" in silence_message)or("美" in silence_message):
    #         flag_silence=24                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，自戀模式")                                                            
    # # 17.king
    # elif (flag_silence==17):
    #     if  ("正常模式" in silence_message)or ("一般模式" in silence_message) or ("普通模式" in silence_message):
    #         flag_silence=0                                                   # timer mode
    #         silence_change=2                                                 # it can reply & recode  
    #     elif("狡" in silence_message)or("貪" in silence_message)or("壞" in silence_message):
    #         flag_silence=1                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，狡滑模式")             
    #     elif("甜" in silence_message)or("情" in silence_message)or("溫暖" in silence_message):
    #         flag_silence=4                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，愛你模式") 
    #     elif("簡" in silence_message)or("短" in silence_message)or("重點" in silence_message):
    #         flag_silence=5                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，簡短模式")   
    #     elif ("安靜" in silence_message) or ("閉嘴" in silence_message) or ("吵" in silence_message) or ("關機" in silence_message) or ("去睡覺" in silence_message) or ("休息" in silence_message):
    #         flag_marv=2                                                   # silence mode
    #         silence_change=1                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"好的，卡米兔休息")
    #         line_bot_api.reply_message(event.reply_token,text_message)          # line output             line_bot_api.reply_message(event.reply_token,text_message)          # line output            
    #     elif("不爽" in silence_message):
    #         flag_silence=3                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，不爽模式") 
    #     elif("難過" in silence_message)or("傷心" in silence_message):
    #         flag_silence=6                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，難過模式")   
    #     elif("媽" in silence_message)or("姨" in silence_message)or("回家" in silence_message):
    #         flag_silence=7                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")   
    #     elif("羞" in silence_message):
    #         flag_silence=8                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")             
    #     elif("符號" in silence_message)or("貼圖" in silence_message):
    #         flag_silence=9                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，Emoji模式")               
    #     elif("樂觀" in silence_message)or("熱情" in silence_message)or("興" in silence_message)or("開心" in silence_message):
    #         flag_silence=10                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，開心模式")
    #     elif("不乖" in silence_message)or("怕" in silence_message)or("揍" in silence_message)or("欠" in silence_message):
    #         flag_silence=11                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，害怕模式") 
    #     elif("老師" in silence_message)or("國文" in silence_message)or("文言文" in silence_message):
    #         flag_silence=12                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，老師模式") 
    #     elif("胡" in silence_message)or("亂" in silence_message)or("中二" in silence_message)or("幻" in silence_message):
    #         flag_silence=13                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，亂說模式") 
    #     elif("寵物" in silence_message)or("兔兔" in silence_message):
    #         flag_silence=14                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，寵物模式")       
    #     elif("兵" in silence_message)or("軍" in silence_message):
    #         flag_silence=15                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，軍官模式") 
    #     elif("姨" in silence_message)or("三八" in silence_message)or("婆" in silence_message):
    #         flag_silence=16                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，三八模式") 
    #     elif("律" in silence_message)or("憲" in silence_message)or("規" in silence_message):
    #         flag_silence=18                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，律師模式") 
    #     elif("巴結" in silence_message)or("討" in silence_message)or("諂媚" in silence_message):
    #         flag_silence=19                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，奸商模式") 
    #     elif("宗教" in silence_message)or("信" in silence_message)or("神父" in silence_message):
    #         flag_silence=20                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，神父模式") 
    #     elif("妹妹" in silence_message)or("童" in silence_message)or("孩" in silence_message) :
    #         flag_silence=21                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，女孩模式") 
    #     elif("閩南" in silence_message)or("台語" in silence_message):
    #         flag_silence=22                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，台語模式")                                                            
    #     elif("誇" in silence_message)or("謠" in silence_message)or("記者" in silence_message):
    #         flag_silence=23                                                 # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，誇大模式") 
    #     elif("自戀" in silence_message)or("帥" in silence_message)or("美" in silence_message):
    #         flag_silence=24                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，自戀模式")                                                            
    # # 18.law
    # elif (flag_silence==18):
    #     if  ("正常模式" in silence_message)or ("一般模式" in silence_message) or ("普通模式" in silence_message):
    #         flag_silence=0                                                   # timer mode
    #         silence_change=2                                                 # it can reply & recode  
    #     elif("狡" in silence_message)or("貪" in silence_message)or("壞" in silence_message):
    #         flag_silence=1                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，狡滑模式")             
    #     elif("甜" in silence_message)or("情" in silence_message)or("溫暖" in silence_message):
    #         flag_silence=4                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，愛你模式") 
    #     elif("簡" in silence_message)or("短" in silence_message)or("重點" in silence_message):
    #         flag_silence=5                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，簡短模式")   
    #     elif ("安靜" in silence_message) or ("閉嘴" in silence_message) or ("吵" in silence_message) or ("關機" in silence_message) or ("去睡覺" in silence_message) or ("休息" in silence_message):
    #         flag_marv=2                                                   # silence mode
    #         silence_change=1                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"好的，卡米兔休息")
    #         line_bot_api.reply_message(event.reply_token,text_message)          # line output             line_bot_api.reply_message(event.reply_token,text_message)          # line output            
    #     elif("不爽" in silence_message):
    #         flag_silence=3                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，不爽模式") 
    #     elif("難過" in silence_message)or("傷心" in silence_message):
    #         flag_silence=6                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，難過模式")   
    #     elif("媽" in silence_message)or("姨" in silence_message)or("回家" in silence_message):
    #         flag_silence=7                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")   
    #     elif("羞" in silence_message):
    #         flag_silence=8                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")             
    #     elif("符號" in silence_message)or("貼圖" in silence_message):
    #         flag_silence=9                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，Emoji模式")               
    #     elif("樂觀" in silence_message)or("熱情" in silence_message)or("興" in silence_message)or("開心" in silence_message):
    #         flag_silence=10                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，開心模式")
    #     elif("不乖" in silence_message)or("怕" in silence_message)or("揍" in silence_message)or("欠" in silence_message):
    #         flag_silence=11                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，害怕模式") 
    #     elif("老師" in silence_message)or("國文" in silence_message)or("文言文" in silence_message):
    #         flag_silence=12                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，老師模式") 
    #     elif("胡" in silence_message)or("亂" in silence_message)or("中二" in silence_message)or("幻" in silence_message):
    #         flag_silence=13                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，亂說模式") 
    #     elif("寵物" in silence_message)or("兔兔" in silence_message):
    #         flag_silence=14                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，寵物模式")       
    #     elif("兵" in silence_message)or("軍" in silence_message):
    #         flag_silence=15                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，軍官模式") 
    #     elif("姨" in silence_message)or("三八" in silence_message)or("婆" in silence_message):
    #         flag_silence=16                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，三八模式") 
    #     elif("王" in silence_message)or("皇" in silence_message):
    #         flag_silence=17                                                # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，皇帝模式") 
    #     elif("巴結" in silence_message)or("討" in silence_message)or("諂媚" in silence_message):
    #         flag_silence=19                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，奸商模式") 
    #     elif("宗教" in silence_message)or("信" in silence_message)or("神父" in silence_message):
    #         flag_silence=20                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，神父模式") 
    #     elif("妹妹" in silence_message)or("童" in silence_message)or("孩" in silence_message) :
    #         flag_silence=21                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，女孩模式") 
    #     elif("閩南" in silence_message)or("台語" in silence_message):
    #         flag_silence=22                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，台語模式")                                                            
    #     elif("誇" in silence_message)or("謠" in silence_message)or("記者" in silence_message):
    #         flag_silence=23                                                 # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，誇大模式") 
    #     elif("自戀" in silence_message)or("帥" in silence_message)or("美" in silence_message):
    #         flag_silence=24                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，自戀模式")                                                            
    # # 19.flattery 
    # elif (flag_silence==19):
    #     if  ("正常模式" in silence_message)or ("一般模式" in silence_message) or ("普通模式" in silence_message):
    #         flag_silence=0                                                   # timer mode
    #         silence_change=2                                                 # it can reply & recode  
    #     elif("狡" in silence_message)or("貪" in silence_message)or("壞" in silence_message):
    #         flag_silence=1                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，狡滑模式")             
    #     elif("甜" in silence_message)or("情" in silence_message)or("溫暖" in silence_message):
    #         flag_silence=4                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，愛你模式") 
    #     elif("簡" in silence_message)or("短" in silence_message)or("重點" in silence_message):
    #         flag_silence=5                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，簡短模式")   
    #     elif ("安靜" in silence_message) or ("閉嘴" in silence_message) or ("吵" in silence_message) or ("關機" in silence_message) or ("去睡覺" in silence_message) or ("休息" in silence_message):
    #         flag_marv=2                                                   # silence mode
    #         silence_change=1                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"好的，卡米兔休息")
    #         line_bot_api.reply_message(event.reply_token,text_message)          # line output             line_bot_api.reply_message(event.reply_token,text_message)          # line output            
    #     elif("不爽" in silence_message):
    #         flag_silence=3                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，不爽模式") 
    #     elif("難過" in silence_message)or("傷心" in silence_message):
    #         flag_silence=6                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，難過模式")   
    #     elif("媽" in silence_message)or("姨" in silence_message)or("回家" in silence_message):
    #         flag_silence=7                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")   
    #     elif("羞" in silence_message):
    #         flag_silence=8                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")             
    #     elif("符號" in silence_message)or("貼圖" in silence_message):
    #         flag_silence=9                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，Emoji模式")               
    #     elif("樂觀" in silence_message)or("熱情" in silence_message)or("興" in silence_message)or("開心" in silence_message):
    #         flag_silence=10                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，開心模式")
    #     elif("不乖" in silence_message)or("怕" in silence_message)or("揍" in silence_message)or("欠" in silence_message):
    #         flag_silence=11                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，害怕模式") 
    #     elif("老師" in silence_message)or("國文" in silence_message)or("文言文" in silence_message):
    #         flag_silence=12                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，老師模式") 
    #     elif("胡" in silence_message)or("亂" in silence_message)or("中二" in silence_message)or("幻" in silence_message):
    #         flag_silence=13                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，亂說模式") 
    #     elif("寵物" in silence_message)or("兔兔" in silence_message):
    #         flag_silence=14                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，寵物模式")       
    #     elif("兵" in silence_message)or("軍" in silence_message):
    #         flag_silence=15                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，軍官模式") 
    #     elif("姨" in silence_message)or("三八" in silence_message)or("婆" in silence_message):
    #         flag_silence=16                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，三八模式") 
    #     elif("王" in silence_message)or("皇" in silence_message):
    #         flag_silence=17                                                # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，皇帝模式") 
    #     elif("律" in silence_message)or("憲" in silence_message)or("規" in silence_message):
    #         flag_silence=18                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，律師模式") 
    #     elif("巴結" in silence_message)or("討" in silence_message)or("諂媚" in silence_message):
    #         flag_silence=19                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，奸商模式")             
    #     elif("宗教" in silence_message)or("信" in silence_message)or("神父" in silence_message):
    #         flag_silence=20                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，神父模式") 
    #     elif("妹妹" in silence_message)or("童" in silence_message)or("孩" in silence_message) :
    #         flag_silence=21                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，女孩模式") 
    #     elif("閩南" in silence_message)or("台語" in silence_message):
    #         flag_silence=22                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，台語模式")                                                            
    #     elif("誇" in silence_message)or("謠" in silence_message)or("記者" in silence_message):
    #         flag_silence=23                                                 # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，誇大模式") 
    #     elif("自戀" in silence_message)or("帥" in silence_message)or("美" in silence_message):
    #         flag_silence=24                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，自戀模式")                                                            
    # # 20.god
    # elif (flag_silence==20):
    #     if  ("正常模式" in silence_message)or ("一般模式" in silence_message) or ("普通模式" in silence_message):
    #         flag_silence=0                                                   # timer mode
    #         silence_change=2                                                 # it can reply & recode  
    #     elif("狡" in silence_message)or("貪" in silence_message)or("壞" in silence_message):
    #         flag_silence=1                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，狡滑模式")             
    #     elif("甜" in silence_message)or("情" in silence_message)or("溫暖" in silence_message):
    #         flag_silence=4                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，愛你模式") 
    #     elif("簡" in silence_message)or("短" in silence_message)or("重點" in silence_message):
    #         flag_silence=5                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，簡短模式")   
    #     elif ("安靜" in silence_message) or ("閉嘴" in silence_message) or ("吵" in silence_message) or ("關機" in silence_message) or ("去睡覺" in silence_message) or ("休息" in silence_message):
    #         flag_marv=2                                                   # silence mode
    #         silence_change=1                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"好的，卡米兔休息")
    #         line_bot_api.reply_message(event.reply_token,text_message)          # line output             line_bot_api.reply_message(event.reply_token,text_message)          # line output            
    #     elif("不爽" in silence_message):
    #         flag_silence=3                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，不爽模式") 
    #     elif("難過" in silence_message)or("傷心" in silence_message):
    #         flag_silence=6                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，難過模式")   
    #     elif("媽" in silence_message)or("姨" in silence_message)or("回家" in silence_message):
    #         flag_silence=7                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")   
    #     elif("羞" in silence_message):
    #         flag_silence=8                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")             
    #     elif("符號" in silence_message)or("貼圖" in silence_message):
    #         flag_silence=9                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，Emoji模式")               
    #     elif("樂觀" in silence_message)or("熱情" in silence_message)or("興" in silence_message)or("開心" in silence_message):
    #         flag_silence=10                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，開心模式")
    #     elif("不乖" in silence_message)or("怕" in silence_message)or("揍" in silence_message)or("欠" in silence_message):
    #         flag_silence=11                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，害怕模式") 
    #     elif("老師" in silence_message)or("國文" in silence_message)or("文言文" in silence_message):
    #         flag_silence=12                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，老師模式") 
    #     elif("胡" in silence_message)or("亂" in silence_message)or("中二" in silence_message)or("幻" in silence_message):
    #         flag_silence=13                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，亂說模式") 
    #     elif("寵物" in silence_message)or("兔兔" in silence_message):
    #         flag_silence=14                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，寵物模式")       
    #     elif("兵" in silence_message)or("軍" in silence_message):
    #         flag_silence=15                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，軍官模式") 
    #     elif("姨" in silence_message)or("三八" in silence_message)or("婆" in silence_message):
    #         flag_silence=16                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，三八模式") 
    #     elif("王" in silence_message)or("皇" in silence_message):
    #         flag_silence=17                                                # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，皇帝模式") 
    #     elif("律" in silence_message)or("憲" in silence_message)or("規" in silence_message):
    #         flag_silence=18                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，律師模式") 
    #     elif("巴結" in silence_message)or("討" in silence_message)or("諂媚" in silence_message):
    #         flag_silence=19                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，奸商模式") 
    #     elif("妹妹" in silence_message)or("童" in silence_message)or("孩" in silence_message) :
    #         flag_silence=21                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，女孩模式") 
    #     elif("閩南" in silence_message)or("台語" in silence_message):
    #         flag_silence=22                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，台語模式")                                                            
    #     elif("誇" in silence_message)or("謠" in silence_message)or("記者" in silence_message):
    #         flag_silence=23                                                 # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，誇大模式") 
    #     elif("自戀" in silence_message)or("帥" in silence_message)or("美" in silence_message):
    #         flag_silence=24                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，自戀模式")                                                            
    # # 21.girl 
    # elif (flag_silence==21):
    #     if  ("正常模式" in silence_message)or ("一般模式" in silence_message) or ("普通模式" in silence_message):
    #         flag_silence=0                                                   # timer mode
    #         silence_change=2                                                 # it can reply & recode  
    #     elif("狡" in silence_message)or("貪" in silence_message)or("壞" in silence_message):
    #         flag_silence=1                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，狡滑模式")             
    #     elif("甜" in silence_message)or("情" in silence_message)or("溫暖" in silence_message):
    #         flag_silence=4                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，愛你模式") 
    #     elif("簡" in silence_message)or("短" in silence_message)or("重點" in silence_message):
    #         flag_silence=5                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，簡短模式")   
    #     elif ("安靜" in silence_message) or ("閉嘴" in silence_message) or ("吵" in silence_message) or ("關機" in silence_message) or ("去睡覺" in silence_message) or ("休息" in silence_message):
    #         flag_marv=2                                                   # silence mode
    #         silence_change=1                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"好的，卡米兔休息")
    #         line_bot_api.reply_message(event.reply_token,text_message)          # line output             line_bot_api.reply_message(event.reply_token,text_message)          # line output            
    #     elif("不爽" in silence_message):
    #         flag_silence=3                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，不爽模式") 
    #     elif("難過" in silence_message)or("傷心" in silence_message):
    #         flag_silence=6                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，難過模式")   
    #     elif("媽" in silence_message)or("姨" in silence_message)or("回家" in silence_message):
    #         flag_silence=7                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")   
    #     elif("羞" in silence_message):
    #         flag_silence=8                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")             
    #     elif("符號" in silence_message)or("貼圖" in silence_message):
    #         flag_silence=9                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，Emoji模式")               
    #     elif("樂觀" in silence_message)or("熱情" in silence_message)or("興" in silence_message)or("開心" in silence_message):
    #         flag_silence=10                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，開心模式")
    #     elif("不乖" in silence_message)or("怕" in silence_message)or("揍" in silence_message)or("欠" in silence_message):
    #         flag_silence=11                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，害怕模式") 
    #     elif("老師" in silence_message)or("國文" in silence_message)or("文言文" in silence_message):
    #         flag_silence=12                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，老師模式") 
    #     elif("胡" in silence_message)or("亂" in silence_message)or("中二" in silence_message)or("幻" in silence_message):
    #         flag_silence=13                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，亂說模式") 
    #     elif("寵物" in silence_message)or("兔兔" in silence_message):
    #         flag_silence=14                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，寵物模式")       
    #     elif("兵" in silence_message)or("軍" in silence_message):
    #         flag_silence=15                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，軍官模式") 
    #     elif("姨" in silence_message)or("三八" in silence_message)or("婆" in silence_message):
    #         flag_silence=16                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，三八模式") 
    #     elif("王" in silence_message)or("皇" in silence_message):
    #         flag_silence=17                                                # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，皇帝模式") 
    #     elif("律" in silence_message)or("憲" in silence_message)or("規" in silence_message):
    #         flag_silence=18                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，律師模式") 
    #     elif("巴結" in silence_message)or("討" in silence_message)or("諂媚" in silence_message):
    #         flag_silence=19                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，奸商模式") 
    #     elif("宗教" in silence_message)or("信" in silence_message)or("神父" in silence_message):
    #         flag_silence=20                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，神父模式") 
    #     elif("閩南" in silence_message)or("台語" in silence_message):
    #         flag_silence=22                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，台語模式")                                                            
    #     elif("誇" in silence_message)or("謠" in silence_message)or("記者" in silence_message):
    #         flag_silence=23                                                 # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，誇大模式") 
    #     elif("自戀" in silence_message)or("帥" in silence_message)or("美" in silence_message):
    #         flag_silence=24                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，自戀模式")                                                            
    # # 22.台語
    # elif (flag_silence==22):
    #     if  ("正常模式" in silence_message)or ("一般模式" in silence_message) or ("普通模式" in silence_message):
    #         flag_silence=0                                                   # timer mode
    #         silence_change=2                                                 # it can reply & recode  
    #     elif("狡" in silence_message)or("貪" in silence_message)or("壞" in silence_message):
    #         flag_silence=1                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，狡滑模式")             
    #     elif("甜" in silence_message)or("情" in silence_message)or("溫暖" in silence_message):
    #         flag_silence=4                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，愛你模式") 
    #     elif("簡" in silence_message)or("短" in silence_message)or("重點" in silence_message):
    #         flag_silence=5                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，簡短模式")   
    #     elif ("安靜" in silence_message) or ("閉嘴" in silence_message) or ("吵" in silence_message) or ("關機" in silence_message) or ("去睡覺" in silence_message) or ("休息" in silence_message):
    #         flag_marv=2                                                   # silence mode
    #         silence_change=1                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"好的，卡米兔休息")
    #         line_bot_api.reply_message(event.reply_token,text_message)          # line output             line_bot_api.reply_message(event.reply_token,text_message)          # line output            
    #     elif("不爽" in silence_message):
    #         flag_silence=3                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，不爽模式") 
    #     elif("難過" in silence_message)or("傷心" in silence_message):
    #         flag_silence=6                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，難過模式")   
    #     elif("媽" in silence_message)or("姨" in silence_message)or("回家" in silence_message):
    #         flag_silence=7                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")   
    #     elif("羞" in silence_message):
    #         flag_silence=8                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")             
    #     elif("符號" in silence_message)or("貼圖" in silence_message):
    #         flag_silence=9                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，Emoji模式")               
    #     elif("樂觀" in silence_message)or("熱情" in silence_message)or("興" in silence_message)or("開心" in silence_message):
    #         flag_silence=10                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，開心模式")
    #     elif("不乖" in silence_message)or("怕" in silence_message)or("揍" in silence_message)or("欠" in silence_message):
    #         flag_silence=11                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，害怕模式") 
    #     elif("老師" in silence_message)or("國文" in silence_message)or("文言文" in silence_message):
    #         flag_silence=12                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，老師模式") 
    #     elif("胡" in silence_message)or("亂" in silence_message)or("中二" in silence_message)or("幻" in silence_message):
    #         flag_silence=13                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，亂說模式") 
    #     elif("寵物" in silence_message)or("兔兔" in silence_message):
    #         flag_silence=14                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，寵物模式")       
    #     elif("兵" in silence_message)or("軍" in silence_message):
    #         flag_silence=15                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，軍官模式") 
    #     elif("姨" in silence_message)or("三八" in silence_message)or("婆" in silence_message):
    #         flag_silence=16                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，三八模式") 
    #     elif("王" in silence_message)or("皇" in silence_message):
    #         flag_silence=17                                                # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，皇帝模式") 
    #     elif("律" in silence_message)or("憲" in silence_message)or("規" in silence_message):
    #         flag_silence=18                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，律師模式") 
    #     elif("巴結" in silence_message)or("討" in silence_message)or("諂媚" in silence_message):
    #         flag_silence=19                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，奸商模式") 
    #     elif("宗教" in silence_message)or("信" in silence_message)or("神父" in silence_message):
    #         flag_silence=20                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，神父模式") 
    #     elif("妹妹" in silence_message)or("童" in silence_message)or("孩" in silence_message) :
    #         flag_silence=21                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，女孩模式")                                 
    #     elif("誇" in silence_message)or("謠" in silence_message)or("記者" in silence_message):
    #         flag_silence=23                                                 # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，誇大模式") 
    #     elif("自戀" in silence_message)or("帥" in silence_message)or("美" in silence_message):
    #         flag_silence=24                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，自戀模式")                                                            
    # # 23.exaggerate
    # elif (flag_silence==23):
    #     if  ("正常模式" in silence_message)or ("一般模式" in silence_message) or ("普通模式" in silence_message):
    #         flag_silence=0                                                   # timer mode
    #         silence_change=2                                                 # it can reply & recode  
    #     elif("狡" in silence_message)or("貪" in silence_message)or("壞" in silence_message):
    #         flag_silence=1                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，狡滑模式")             
    #     elif("甜" in silence_message)or("情" in silence_message)or("溫暖" in silence_message):
    #         flag_silence=4                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，愛你模式") 
    #     elif("簡" in silence_message)or("短" in silence_message)or("重點" in silence_message):
    #         flag_silence=5                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，簡短模式")   
    #     elif ("安靜" in silence_message) or ("閉嘴" in silence_message) or ("吵" in silence_message) or ("關機" in silence_message) or ("去睡覺" in silence_message) or ("休息" in silence_message):
    #         flag_marv=2                                                   # silence mode
    #         silence_change=1                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"好的，卡米兔休息")
    #         line_bot_api.reply_message(event.reply_token,text_message)          # line output             line_bot_api.reply_message(event.reply_token,text_message)          # line output            
    #     elif("不爽" in silence_message):
    #         flag_silence=3                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，不爽模式") 
    #     elif("難過" in silence_message)or("傷心" in silence_message):
    #         flag_silence=6                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，難過模式")   
    #     elif("媽" in silence_message)or("姨" in silence_message)or("回家" in silence_message):
    #         flag_silence=7                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")   
    #     elif("羞" in silence_message):
    #         flag_silence=8                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")             
    #     elif("符號" in silence_message)or("貼圖" in silence_message):
    #         flag_silence=9                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，Emoji模式")               
    #     elif("樂觀" in silence_message)or("熱情" in silence_message)or("興" in silence_message)or("開心" in silence_message):
    #         flag_silence=10                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，開心模式")
    #     elif("不乖" in silence_message)or("怕" in silence_message)or("揍" in silence_message)or("欠" in silence_message):
    #         flag_silence=11                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，害怕模式") 
    #     elif("老師" in silence_message)or("國文" in silence_message)or("文言文" in silence_message):
    #         flag_silence=12                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，老師模式") 
    #     elif("胡" in silence_message)or("亂" in silence_message)or("中二" in silence_message)or("幻" in silence_message):
    #         flag_silence=13                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，亂說模式") 
    #     elif("寵物" in silence_message)or("兔兔" in silence_message):
    #         flag_silence=14                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，寵物模式")       
    #     elif("兵" in silence_message)or("軍" in silence_message):
    #         flag_silence=15                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，軍官模式") 
    #     elif("姨" in silence_message)or("三八" in silence_message)or("婆" in silence_message):
    #         flag_silence=16                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，三八模式") 
    #     elif("王" in silence_message)or("皇" in silence_message):
    #         flag_silence=17                                                # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，皇帝模式") 
    #     elif("律" in silence_message)or("憲" in silence_message)or("規" in silence_message):
    #         flag_silence=18                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，律師模式") 
    #     elif("巴結" in silence_message)or("討" in silence_message)or("諂媚" in silence_message):
    #         flag_silence=19                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，奸商模式") 
    #     elif("宗教" in silence_message)or("信" in silence_message)or("神父" in silence_message):
    #         flag_silence=20                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，神父模式") 
    #     elif("妹妹" in silence_message)or("童" in silence_message)or("孩" in silence_message) :
    #         flag_silence=21                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，女孩模式") 
    #     elif("閩南" in silence_message)or("台語" in silence_message):
    #         flag_silence=22                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，台語模式")                                                            
    #     elif("自戀" in silence_message)or("帥" in silence_message)or("美" in silence_message):
    #         flag_silence=24                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，自戀模式")                                                            
    # # 24.selfish
    # elif (flag_silence==24):
    #     if  ("正常模式" in silence_message)or ("一般模式" in silence_message) or ("普通模式" in silence_message):
    #         flag_silence=0                                                   # timer mode
    #         silence_change=2                                                 # it can reply & recode  
    #     elif("狡" in silence_message)or("貪" in silence_message)or("壞" in silence_message):
    #         flag_silence=1                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，狡滑模式")             
    #     elif("甜" in silence_message)or("情" in silence_message)or("溫暖" in silence_message):
    #         flag_silence=4                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，愛你模式") 
    #     elif("簡" in silence_message)or("短" in silence_message)or("重點" in silence_message):
    #         flag_silence=5                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，簡短模式")   
    #     elif ("安靜" in silence_message) or ("閉嘴" in silence_message) or ("吵" in silence_message) or ("關機" in silence_message) or ("去睡覺" in silence_message) or ("休息" in silence_message):
    #         flag_marv=2                                                   # silence mode
    #         silence_change=1                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"好的，卡米兔休息")
    #         line_bot_api.reply_message(event.reply_token,text_message)          # line output             line_bot_api.reply_message(event.reply_token,text_message)          # line output            
    #     elif("不爽" in silence_message):
    #         flag_silence=3                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，不爽模式") 
    #     elif("難過" in silence_message)or("傷心" in silence_message):
    #         flag_silence=6                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，難過模式")   
    #     elif("媽" in silence_message)or("姨" in silence_message)or("回家" in silence_message):
    #         flag_silence=7                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")   
    #     elif("羞" in silence_message):
    #         flag_silence=8                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         # text_message = TextSendMessage(f"卡米兔，媽媽模式")             
    #     elif("符號" in silence_message)or("貼圖" in silence_message):
    #         flag_silence=9                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，Emoji模式")               
    #     elif("樂觀" in silence_message)or("熱情" in silence_message)or("興" in silence_message)or("開心" in silence_message):
    #         flag_silence=10                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，開心模式")
    #     elif("不乖" in silence_message)or("怕" in silence_message)or("揍" in silence_message)or("欠" in silence_message):
    #         flag_silence=11                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，害怕模式") 
    #     elif("老師" in silence_message)or("國文" in silence_message)or("文言文" in silence_message):
    #         flag_silence=12                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，老師模式") 
    #     elif("胡" in silence_message)or("亂" in silence_message)or("中二" in silence_message)or("幻" in silence_message):
    #         flag_silence=13                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，亂說模式") 
    #     elif("寵物" in silence_message)or("兔兔" in silence_message):
    #         flag_silence=14                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，寵物模式")       
    #     elif("兵" in silence_message)or("軍" in silence_message):
    #         flag_silence=15                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，軍官模式") 
    #     elif("姨" in silence_message)or("三八" in silence_message)or("婆" in silence_message):
    #         flag_silence=16                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，三八模式") 
    #     elif("王" in silence_message)or("皇" in silence_message):
    #         flag_silence=17                                                # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，皇帝模式") 
    #     elif("律" in silence_message)or("憲" in silence_message)or("規" in silence_message):
    #         flag_silence=18                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，律師模式") 
    #     elif("巴結" in silence_message)or("討" in silence_message)or("諂媚" in silence_message):
    #         flag_silence=19                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，奸商模式") 
    #     elif("宗教" in silence_message)or("信" in silence_message)or("神父" in silence_message):
    #         flag_silence=20                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，神父模式") 
    #     elif("妹妹" in silence_message)or("童" in silence_message):
    #         flag_silence=21                                                  # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，女孩模式") 
    #     elif("閩南" in silence_message)or("台語" in silence_message):
    #         flag_silence=22                                                   # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，台語模式")                                                            
    #     elif("誇" in silence_message)or("謠" in silence_message)or("記者" in silence_message):
    #         flag_silence=23                                                 # always mode
    #         silence_change=2                                                 # it can reply & recode & show specail word
    #         text_message = TextSendMessage(f"卡米兔，誇大模式") 
    if  ("正常模式" in silence_message)or ("一般模式" in silence_message) or ("普通模式" in silence_message):
        flag_silence=0                                                   # timer mode
        silence_change=2                                                 # it can reply & recode  
    elif("狡" in silence_message)or("貪" in silence_message)or("壞" in silence_message):
        flag_silence=1                                                   # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，狡滑模式")             
    elif("甜" in silence_message)or("情" in silence_message)or("溫暖" in silence_message):
        flag_silence=4                                                   # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，愛你模式") 
    elif("簡" in silence_message)or("短" in silence_message)or("重點" in silence_message):
        flag_silence=5                                                   # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，簡短模式")   
    elif ("安靜" in silence_message) or ("閉嘴" in silence_message) or ("吵" in silence_message) or ("關機" in silence_message) or ("去睡覺" in silence_message) or ("休息" in silence_message):
        flag_marv=2                                                   # silence mode
        silence_change=1                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"好的，卡米兔休息")
        line_bot_api.reply_message(event.reply_token,text_message)          # line output             line_bot_api.reply_message(event.reply_token,text_message)          # line output            
    elif("不爽" in silence_message):
        flag_silence=3                                                   # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，不爽模式") 
    elif("難過" in silence_message)or("傷心" in silence_message):
        flag_silence=6                                                   # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，難過模式")   
    elif("媽" in silence_message)or("姨" in silence_message)or("回家" in silence_message):
        flag_silence=7                                                   # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        # text_message = TextSendMessage(f"卡米兔，媽媽模式")   
    elif("羞" in silence_message):
        flag_silence=8                                                   # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        # text_message = TextSendMessage(f"卡米兔，媽媽模式")             
    elif("符號" in silence_message)or("貼圖" in silence_message):
        flag_silence=9                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，Emoji模式")               
    elif("樂觀" in silence_message)or("熱情" in silence_message)or("興" in silence_message)or("開心" in silence_message):
        flag_silence=10                                                   # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，開心模式")
    elif("不乖" in silence_message)or("怕" in silence_message)or("揍" in silence_message)or("欠" in silence_message):
        flag_silence=11                                                   # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，害怕模式") 
    elif("老師" in silence_message)or("國文" in silence_message)or("文言文" in silence_message):
        flag_silence=12                                                   # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，老師模式") 
    elif("胡" in silence_message)or("亂" in silence_message)or("中二" in silence_message)or("幻" in silence_message):
        flag_silence=13                                                   # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，亂說模式") 
    elif("poke" in silence_message)or("寶可" in silence_message)or("神奇寶貝" in silence_message)or("皮卡" in silence_message):
        flag_silence=14                                                   # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，寵物模式")       
    elif("兵" in silence_message)or("軍" in silence_message):
        flag_silence=15                                                   # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，軍官模式") 
    elif("姨" in silence_message)or("三八" in silence_message)or("婆" in silence_message):
        flag_silence=16                                                   # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，三八模式") 
    elif("王" in silence_message)or("皇" in silence_message):
        flag_silence=17                                                # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，皇帝模式") 
    elif("律" in silence_message)or("憲" in silence_message)or("規" in silence_message):
        flag_silence=18                                                   # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，律師模式") 
    elif("巴結" in silence_message)or("討" in silence_message)or("諂媚" in silence_message):
        flag_silence=19                                                   # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，奸商模式")             
    elif("宗教" in silence_message)or("信" in silence_message)or("神父" in silence_message):
        flag_silence=20                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，神父模式") 
    elif("妹妹" in silence_message)or("童" in silence_message)or("孩" in silence_message) :
        flag_silence=21                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，女孩模式") 
    elif("閩南" in silence_message)or("台語" in silence_message):
        flag_silence=22                                                   # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，台語模式")                                                            
    elif("誇" in silence_message)or("謠" in silence_message)or("記者" in silence_message):
        flag_silence=23                                                 # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，誇大模式") 
    elif("自戀" in silence_message)or("帥" in silence_message)or("美" in silence_message):
        flag_silence=24                                                   # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，自戀模式")      
    elif("囉嗦" in silence_message)or("老人" in silence_message)or("嘮" in silence_message):
        flag_silence=25                                                   # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，囉嗦的老人家模式")      
    elif("醫" in silence_message)or("生病" in silence_message)or("疾" in silence_message)or("感冒" in silence_message):
        flag_silence=26                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，醫生模式")      
    elif("呆" in silence_message)or("笨" in silence_message)or("傻" in silence_message):
        flag_silence=27                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，呆呆模式")      
    elif("懶" in silence_message)or("好麻煩" in silence_message)or("很麻煩" in silence_message):
        flag_silence=28                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，懶惰模式")      
    elif("生氣" in silence_message)or("憤怒" in silence_message)or("不爽" in silence_message):
        flag_silence=29                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，生氣模式")  
    elif("好吃" in silence_message)or("美食" in silence_message)or("美味" in silence_message):
        flag_silence=30                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，愛吃模式")  
    elif("否定" in silence_message)or("拒絕" in silence_message)or("不可以" in silence_message):
        flag_silence=31                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，否定模式")  
    elif("炸彈" in silence_message)or("爆炸" in silence_message):
        flag_silence=32                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，炸彈模式")  
    elif("專" in silence_message)or("博" in silence_message):
        flag_silence=33                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，專家模式")  
    elif("神話" in silence_message)or("成語" in silence_message)or("故事" in silence_message):
        flag_silence=34                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，故事模式")  
    elif("失望" in silence_message)or("失戀" in silence_message)or("死心" in silence_message):
        flag_silence=35                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，失望模式")  
    elif("期待" in silence_message)or("好奇" in silence_message)or("節" in silence_message)or("過年" in silence_message)or("新年" in silence_message):
        flag_silence=36                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，期待模式")  
    elif("化學" in silence_message)or("成分" in silence_message):
        flag_silence=37                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，化學專家模式")  
    elif("保養" in silence_message)or("健康" in silence_message)or("護" in silence_message)or("運動" in silence_message):
        flag_silence=38                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，保養專家模式")  
    elif("粉絲" in silence_message)or("崇" in silence_message)or("追" in silence_message):
        flag_silence=39                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，瘋狂粉絲模式")  
    elif("公主" in silence_message)or("女王" in silence_message)or("傲" in silence_message)or("驕" in silence_message):
        flag_silence=40                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，公主模式")  
    elif("汪汪" in silence_message)or("忠" in silence_message)or("奴" in silence_message):
        flag_silence=41                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，汪奴模式")  
    elif("AI" in silence_message)or("命令" in silence_message)or("管家" in silence_message):
        flag_silence=42                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，AI管家模式")  
    elif("勾" in silence_message)or("交際" in silence_message):
        flag_silence=43                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，交際花模式")  
    elif("恐怖" in silence_message)or("可怕" in silence_message)or("鬼" in silence_message):
        flag_silence=44                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，恐怖模式")  
    elif("疑" in silence_message)or("被害" in silence_message)or("責怪" in silence_message)or("玻璃" in silence_message):
        flag_silence=45                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，質疑模式")  
    elif("當選" in silence_message)or("選舉" in silence_message)or("總統" in silence_message)or("市長" in silence_message)or("議員" in silence_message):
        flag_silence=46                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，當選模式")  
    elif("發音" in silence_message)or("口吃" in silence_message)or("口音" in silence_message):
        flag_silence=47                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，口吃模式")  
    elif("粗" in silence_message)or("魯" in silence_message):
        flag_silence=48                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，粗魯模式")  
    elif("勢利" in silence_message)or("金錢" in silence_message)or("利益" in silence_message):
        flag_silence=49                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，金錢模式")  
    elif("歌" in silence_message)or("唱" in silence_message):
        flag_silence=50                                                  # always mode
        silence_change=2                                                 # it can reply & recode & show specail word
        text_message = TextSendMessage(f"卡米兔，唱歌模式")  


#        else:
#           if (abs(time_stamp_new-time_stamp)>180):                         # if over 3 hours silence
#                flag_marv=2                                               # enalbe silence mode
#                silence_change=2                                             # it can reply & recode                                                   
#            else:
#                silence_change=3                                             # it jus recode
    # 6. update mode
    if(silence_change==1 or silence_change==2 or silence_change==3 ):        # update csv data
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['Silence']=flag_silence                             # silence mode
                csv_row['last_time']=time_stamp_new                         # update user time
                csv_row['Marv'] = flag_marv 

            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except IOError:
            print("File error, please close the file")
    # 7.if we have change mode, show the message
    if (flag_marv==2):
        text_message = TextSendMessage(f"好的，卡米兔休息")
        line_bot_api.reply_message(event.reply_token,text_message)          # line output            

    #######################################
    # --------------Mantra--------------- #
    if ("卡米" == input_message):
        compare_msg = 'My name is 卡米兔, I am a happy rabbit.'
        # 7.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")


        reply_msg = f"逗你歡樂 陪你說笑"                                     # for test
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))

    #######################################  
    # ------------Time and Day----------- #
    elif input_message in msgchk_timer:
        # 1. Get timer
        time_current = time_now.strftime("%m/%d  %H:%M:%S")                                         # output format
        reply_msg = f"現在台灣時間：\n{time_current}"
        # 2. Line Output 
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))

    #######################################
    # --------------Weather-------------- #
    elif ("天氣" in input_message) or ("氣象" in input_message) or ("空氣" in input_message)or ("空汙" in input_message):
        # 1.weather parameter
        weather_code = 'CWB-86BE978B-666E-4AE1-87B6-C70A998DDD5F'                                   # weather API code
        weather_output = {}      
        city_list, site_list ={}, {}                                                                # for each location
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
                reply_msg = weather_output["屏東縣"]                                                 # default location
        
        # 5-1.parser (1 week data) -----------------------------------------------------------------
        if ("明天" in input_message) or ("後天" in input_message) or ("下" in input_message)or ("週" in input_message) or ("未來" in input_message)or ("鄉" in input_message)or ("村" in input_message)or ("鎮" in input_message)or ("市" in input_message):
            for i in weather_output:                                                                # location list
                if weather_name[i] in input_message:                                                # if location name is equal to input message
                    # 5-2 [RE] getting weather url link(JSON Format)
                    weather_url = f'https://opendata.cwb.gov.tw/api/v1/rest/datastore/{weather_list[i]}?Authorization={weather_code}&elementName=WeatherDescription'
                    # 5-3 [RE] getting all weather
                    weather_data = requests.get(weather_url)                                        # get URL
                    weather_data_json = weather_data.json()                                         # trans json format
                    weather_location = weather_data_json['records']['locations'][0]['location']     # forecast data of major location
                    break
                else:
                    # default location
                    weather_url = f'https://opendata.cwb.gov.tw/api/v1/rest/datastore/{weather_list["屏東縣"]}?Authorization={weather_code}&elementName=WeatherDescription'
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

        # 7.parser (1 air) -----------------------------------------------------------------
        elif ("空氣" in input_message)or ("空汙" in input_message):
            # 2.getting weather url link(JSON Format)
            air_url = f'https://data.epa.gov.tw/api/v2/aqx_p_432?api_key=e8dd42e6-9b8b-43f8-991e-b3dee723a52d&limit=1000&sort=ImportDate%20desc&format=JSON'
            # 3.getting all weather
            air_data = requests.get(air_url)                                                    # get URL
            air_data_json = air_data.json()                                                     # trans json format
            for i in air_data_json['records']:                                                  # get records item
                city = i['county']                                                              # get city
                if city not in weather_output:
                    weather_output[city]=["台北市"]                                                          # get city key，to save string
                site = i['sitename']                                                            # get city
                if(i['aqi'] == ''):
                    continue
                aqi = int(i['aqi'])                                                             # get AQI value
                status = i['status']                                                            # air value
                site_list[site] = {'aqi':aqi, 'status':status}                                  # recode city
                weather_output[city].append(aqi)                                                     # city aqi 
            for i in weather_output:
                if i in input_message: 
                    aqi_val = round(statistics.mean(city_list[i]),0)                            # get avg value
                    aqi_status = ''                                                             # compare
                    if aqi_val<=50: aqi_status = '良好'
                    elif aqi_val>50 and aqi_val<=100: aqi_status = '普通'
                    elif aqi_val>100 and aqi_val<=150: aqi_status = '對敏感族群不健康'
                    elif aqi_val>150 and aqi_val<=200: aqi_status = '對所有族群不健康'
                    elif aqi_val>200 and aqi_val<=300: aqi_status = '非常不健康'
                    else: aqi_status = '危害'
                    reply_msg = f'空氣品質{aqi_status} ( AQI {aqi_val} )。'                      # output
                    break
            for i in site_list:
                if i in input_message:                                                          # If the address contains the key of the township area name, use the corresponding content directly
                    reply_msg = f'空氣品質{site_list[i]["status"]} ( AQI {site_list[i]["aqi"]} )。'
                    break

        # 6.Output
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))

    #######################################
    # --------------- PIC --------------- #
    elif ("畫" == input_message[0]) or ("請畫" in input_message)or ("產生" in input_message)or ("繪製" in input_message)or ("一張" in input_message)or ("早安圖" in input_message)or ("Draw" in input_message)or ("draw" in input_message):
        try:
            # 1. Setting AI module
            response_3 = openai.Image.create(
                model = 'image-alpha-001',                                                              # which is the model ID for DALL·E 2.
                prompt = input_message.replace("請你","").replace("請","").replace("畫一張","").replace("繪製","").replace("畫出","").replace("給我","").replace("幫我","").replace("生成","").replace("設計","").replace("卡米兔","").replace("產生","").replace("描繪","").replace("製作",""),
                n = 1,                                                                                  # one pic
                size = "1024x1024",                                                                     # Size
            )
            # 2. Setting AI module
            image_url = response_3["data"][0]["url"]                                                    # get image url
            #line_bot_api.reply_message(event.reply_token, TextSendMessage(text=image_url))             # only reply 1 message

            # 3.show image
            image_message = ImageSendMessage(
                original_content_url=image_url,                                                         # original image
                preview_image_url='https://pbs.twimg.com/media/FcWCyinacAEEQcC.jpg'                     # preview image
            )
            line_bot_api.reply_message(event.reply_token, image_message)                                # line reply image (from link)
        except openai.error.OpenAIError as e:
            # 4. except
            text_message = TextSendMessage(text="很抱歉，兔兔畫不出來")                                   # string to TextSendMessage
            line_bot_api.reply_message(event.reply_token,text_message)                                  # line output



    #######################################
    # --------------- Fed --------------- #
    elif ("股票" in input_message) or ("指數" in input_message):
        fed_url = f'https://www.chinatimes.com/newspapers/260202?chdtv'
        # 3.getting all weather
        fed_data = requests.get(fed_url)  
        fed_soup = BeautifulSoup(fed_data.text, "html.parser")
        fed_result = fed_soup.find_all("p", class_="intro")
        fed_output= ""
        fed_index =1
        for fed_title in fed_result:
            fed_output = fed_output +str(fed_index)+"." + fed_title.getText() +"\n\n"                 # string to TextSendMessage
            fed_index=fed_index+1
        line_bot_api.reply_message(event.reply_token,TextSendMessage(fed_output))                     # line output

    #######################################
    # --------------- Web --------------- #
    elif ("新聞" == input_message) :
        web_url = f'https://www.chinatimes.com/realtimenews/?chdtv'
        # 3.getting all weather
        web_data = requests.get(web_url)  
        web_soup = BeautifulSoup(web_data.text, "html.parser")
        web_result = web_soup.find_all("p", class_="intro")
        web_output= ""
        web_index =1
        for web_title in web_result:
            web_output = web_output +str(web_index)+"." + web_title.getText() +"\n\n"                 # string to TextSendMessage
            web_index=web_index+1
        line_bot_api.reply_message(event.reply_token,TextSendMessage(web_output))                     # line output

    #######################################
    # -------------- Link --------------- #
    elif ("www" in input_message) or ("http" in input_message) or ("他" == input_message[0]):
        reply_msg = ""                                                                                # don't reply message

    #######################################
    # --------------- EQ --------------- #
    elif ("地震" in input_message):
        # 1. EQ get data
        weather_code = 'CWB-86BE978B-666E-4AE1-87B6-C70A998DDD5F'                                   # weather API code        
        image_url =""
        url = f'https://opendata.cwb.gov.tw/api/v1/rest/datastore/E-A0016-001?Authorization={weather_code}'
        e_data = requests.get(url)                                                                  # parser eq data
        e_data_json = e_data.json()                                                                 # json format
        eq = e_data_json['records']['Earthquake']                                                   # get eq data

        # 2. parser last data
        for i in eq:
            loc = i['EarthquakeInfo']['Epicenter']['Location']                                      # eq loction
            val = i['EarthquakeInfo']['EarthquakeMagnitude']['MagnitudeValue']                      # eq range
            dep = i['EarthquakeInfo']['FocalDepth']                                                 # eq deep
            eq_time = i['EarthquakeInfo']['OriginTime']                                             # eq time
            img = i['ReportImageURI']                                                               # eq image
            image_url = img
            break                                                                                   # just get first data & break

        # 3. send image
        image_message = ImageSendMessage(
            original_content_url=image_url,                                                         # original image
            preview_image_url='https://pbs.twimg.com/media/FcWCyinacAEEQcC.jpg'                     # preview image
        )
        line_bot_api.reply_message(event.reply_token, image_message)     
    #######################################
    # ----------- bad anwser  ------------ 
    elif (flag_silence==1) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我是一位壞人，狡猾、卑鄙、惡質'
        input_message_2 = '請作為一位壞人，狡猾、卑鄙、惡質的回覆，字數不超過20字:'+input_message

        message_log.append({'role': 'user', 'content': last_msg})
        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_msg

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- rude anwser  ------------ 
    elif (flag_silence==3) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = 'I will very sarcastic and rude reply to your question.'
        input_message_2 = '請作為一位沒有禮貌的人，嘲諷地回覆:'+input_message
        
        message_log.append({'role': 'user', 'content': last_msg})
        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_msg})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message_2})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                          # The name of the OpenAI chatbot model to use
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_msg

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- love anwser  -----------#
    elif (flag_silence==4) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = 'I am your lover, I will sweet and romantic reply to your question，回答內容不會超過20個字'

        message_log.append({'role': 'user', 'content': last_msg})
        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_msg})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                          # The name of the OpenAI chatbot model to use
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_msg

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- short anwser  -----------#
    elif (flag_silence==5) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我是卡米兔, 我很會聊天，回答內容不會超過20個字'

        message_log.append({'role': 'user', 'content': last_msg})
        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_msg})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,                 
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_msg

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- sad anwser  -----------#
    elif (flag_silence==6) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = 'I am a pessimist and I will very sad'
        input_message_2 = '請身為一位悲觀主義者，啜泣地回覆，字數不超過30個字:'+input_message
        
        message_log.append({'role': 'user', 'content': last_msg})
        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_msg})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message_2})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,                  
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_msg

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- mom anwser  -----------#
    elif (flag_silence==7) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = 'I am your mother, 卡米兔. I will carefully tell to you, my sweet children!'
        input_message_2 = '請作為一位母親，回覆幼稚園小孩子，字數不超過30個字:'+input_message
        
        message_log.append({'role': 'user', 'content': last_msg})
        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_msg})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message_2})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_msg

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Anger anwser  -----------#
    elif (flag_silence==8) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我是一隻害羞的卡米兔'
        input_message_2 = '我會很害羞、很靦腆地回復，字數不超過20個字:'+input_message
        
        message_log.append({'role': 'user', 'content': last_msg})
        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_msg})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message_2})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_msg

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- emoji anwser  -----------#
    elif (flag_silence==9) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = 'I am 卡米兔, I only use emoji to answer your question'

        message_log.append({'role': 'user', 'content': last_msg})
        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_msg})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_msg

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Happy anwser  -----------#
    elif (flag_silence==10) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = 'I am 卡米兔, I feel so high and I will super passionate to reply your question'
        input_message_2 = '請作為一位過度興奮者，超級開心的回覆，字數不超過20字:'+input_message

        message_log.append({'role': 'user', 'content': last_msg})
        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_msg})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message_2})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=2,
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_msg

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output     
    #######################################
    # ----------- Fear anwser  -----------#
    elif (flag_silence==11) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我是一隻卡米兔，我真的很害怕'
        input_message_2 = '請作為一位膽小的卡米兔，簡短回覆問題，字數不超過20個字:'+input_message

        message_log.append({'role': 'user', 'content': last_msg})
        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_msg})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message_2})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_msg

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Chinese anwser  -----------#
    elif (flag_silence==12) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我是一位古代兔，我叫做卡米兔'
        input_message_2 = '請使用七言絕句來回覆:'+ input_message

        message_log.append({'role': 'user', 'content': last_msg})
        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_msg})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message_2})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use           
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_msg

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==13) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我很喜歡幻想，天馬行空，胡說八道'
        input_message_2 = '我會天馬行空的回覆，字數不超過20字:'+input_message

        message_log.append({'role': 'user', 'content': last_msg})
        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_msg

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Carmi anwser  -----------#
    elif (flag_silence==14) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我是一位pokemon專家，很喜歡寶可夢'
        input_message_2 = '請作為一位寶可夢專家，請用pokemon做為比喻，回覆字數不超過30個字:'+input_message

        message_log.append({'role': 'user', 'content': last_msg})
        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_msg

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==15) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我是一位士官長，很嚴肅的管理士兵'
        input_message_2 = '請作為一位軍官，很嚴肅的回覆士兵，字數不超過20個字:'+input_message

        message_log.append({'role': 'user', 'content': last_msg})
        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_msg

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==16) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，喜歡聊八卦、裝熟、攀關係'
        input_message_2 = '請作為一位很三八的阿姨，喜歡聊八卦、裝熟、攀關係，字數不超過20字:'+input_message

        message_log.append({'role': 'user', 'content': last_msg})
        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_msg

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==17) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我是皇帝，討厭無禮之人'
        input_message_2 = '請作為一位威嚴的皇帝，太監說:「'+input_message+'」，回覆字數不超過30字'

        message_log.append({'role': 'user', 'content': last_msg})
        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_msg

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==18) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我是一位律師，喜歡談法律'
        input_message_2 = '請作為一位律師，引用法條做為比喻，回覆字數不超過30字:'+input_message

        message_log.append({'role': 'user', 'content': last_msg})
        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,             
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_msg

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==19) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，喜歡討好別人'
        input_message_2 = '請作為一位商人，喜歡巴結、諂媚、奉承的回覆，字數不超過20字:'+input_message

        message_log.append({'role': 'user', 'content': last_msg})
        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_msg

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output                           
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==20) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我是一位神父，相信上帝可以幫助我們'
        input_message_2 = '請作為一位神父，請用宗教理論、聖經做為比喻，回覆字數不超過30字:'+input_message

        message_log.append({'role': 'user', 'content': last_msg})
        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_msg

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==21) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，天真，思想單純，童言童語'
        input_message_2 = '請身為天真的小孩，童言童語的描述，字數不超過20字:'+input_message

        message_log.append({'role': 'user', 'content': last_msg})
        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.5,             
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_msg

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==22) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我是一位閩南語專家，我會使用台語回覆您'
        input_message_2 = '請使用流利的閩南語回覆，字數不超過20字:'+input_message

        message_log.append({'role': 'user', 'content': last_msg})
        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.2,            
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_msg

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output      
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==23) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，喜歡誇大其辭來回覆'
        input_message_2 = '請身為一位誇大的記者，誇大其辭、誇張的回覆，字數不超過20字:'+input_message

        message_log.append({'role': 'user', 'content': last_msg})
        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_msg

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==24) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我很自戀'
        input_message_2 = '請身為一位自戀的兔子，自大的回覆，字數不超過20字:'+input_message


        message_log.append({'role': 'user', 'content': last_msg})

        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_message

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output

    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==25) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，喜歡囉囉嗦嗦，嘮叨，發牢騷'
        input_message_2 = '請身為一位囉嗦的老人家，發牢騷的回覆，字數不超過30字:'+input_message


        message_log.append({'role': 'user', 'content': last_msg})

        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.5,             
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_message

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output


    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==26) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我是一位醫生，正在與病人對話'
        input_message_2 = '請用醫學做為比喻，字數不超過20字:'+input_message

        message_log.append({'role': 'user', 'content': last_msg})

        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_message

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==27) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我喜歡發呆，反應遲鈍'
        input_message_2 = '請身為一位呆呆的兔子，字數不超過20字:'+input_message


        message_log.append({'role': 'user', 'content': last_msg})

        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.2,             
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_message

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==28) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我是偷懶的兔子，很懶散'
        input_message_2 = '請身為一位偷懶的兔子，懶散的回覆問題，字數不超過30字:'+input_message


        message_log.append({'role': 'user', 'content': last_msg})

        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.5,             
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_message

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==29) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我很生氣、憤怒、氣憤'
        input_message_2 = '請身為一位很Angry的兔子，很憤怒的回覆問題，字數不超過20字:'+input_message


        message_log.append({'role': 'user', 'content': last_msg})

        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.5,             
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_message

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==30) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我是愛吃的兔子，我很喜歡美食'
        input_message_2 = '請身為一位美食評論家，形容「' +input_message + '」，形容得非常好吃，字數不超過50字'


        message_log.append({'role': 'user', 'content': last_msg})

        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_message

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==31) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我是古板的兔子，我喜歡否定你、反駁你'
        input_message_2 = '請反駁以下內容，字數不超過20字:'+input_message


        message_log.append({'role': 'user', 'content': last_msg})

        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.2,             
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_message

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==32) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我是一個炸彈客'
        input_message_2 = '給你一個炸彈，並告訴你炸彈要爆炸了，回覆字數不超過30字:'+input_message


        message_log.append({'role': 'user', 'content': last_msg})

        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_message

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==33) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我是一位專家，我甚麼都知道'
        input_message_2 = '請專業地、詳細地回覆問題，字數不超過50字:'+input_message


        message_log.append({'role': 'user', 'content': last_msg})

        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_message

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==34) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我是一位說書人'
        input_message_2 = '請用寓言故事、神話故事或成語故事來形容，字數不超過30字:'+input_message


        message_log.append({'role': 'user', 'content': last_msg})

        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_message

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==35) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我對大家很失望，心灰意冷'
        input_message_2 = '請作為一位失望的人，心不在焉的回覆問題，字數不超過30字:'+input_message


        message_log.append({'role': 'user', 'content': last_msg})

        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_message

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==36) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我是開心的兔子，對未來充滿期待'
        input_message_2 = '請作為一位期待的人，祝福的回覆問題，字數不超過30字:'+input_message


        message_log.append({'role': 'user', 'content': last_msg})

        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_message

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==37) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我是一位化學專家'
        input_message_2 = '請用化學原理、化學元素做為比喻，並回覆以下句子，字數不超過30字:'+input_message


        message_log.append({'role': 'user', 'content': last_msg})

        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_message

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==38) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我是一位保養專家'
        input_message_2 = '請身為一位保養專家，提供健康、保養與飲食的建議，並回覆以下句子，字數不超過20字:'+input_message


        message_log.append({'role': 'user', 'content': last_msg})

        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_message

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==39) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我是一位瘋狂粉絲'
        input_message_2 = '請身為一位瘋狂粉絲，非常崇拜你，想要擁有你的一切，字數不超過30字:'+input_message


        message_log.append({'role': 'user', 'content': last_msg})

        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_message

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==40) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我是一位自以為是的公主'
        input_message_2 = '請身為一位公主，自我感覺良好，大家都要喜歡我，並高傲的回覆，字數不超過20字:'+input_message


        message_log.append({'role': 'user', 'content': last_msg})

        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_message

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output

    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==41) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我是一位忠心耿耿的奴隸'
        input_message_2 = '請身為一位奴隸，具尾都會加上「汪汪」，回覆字數不超過20字:'+input_message


        message_log.append({'role': 'user', 'content': last_msg})

        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_message

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==42) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我是一位AI管家'
        input_message_2 = '請身為一位AI管家，命令對方去工作、不要閒聊，回覆字數不超過20字:'+input_message


        message_log.append({'role': 'user', 'content': last_msg})

        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_message

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==43) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我是一位交際花，我喜歡勾引別人'
        input_message_2 = '請身為一位交際花，透過聊天勾引對方，字數不超過30字:'+input_message


        message_log.append({'role': 'user', 'content': last_msg})

        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_message

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==44) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我喜歡說鬼故事'
        input_message_2 = '請引用鬼故事來回覆，字數不超過40字:'+input_message


        message_log.append({'role': 'user', 'content': last_msg})

        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_message

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==45) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，玻璃心，喜歡責怪別人'
        input_message_2 = '請身為一位有疑心病的人，用質疑、責怪的回覆，字數不超過20字:'+input_message


        message_log.append({'role': 'user', 'content': last_msg})

        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_message

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==46) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我是一位候選人'
        input_message_2 = '請身為一位候選人，進行遊說與拉票，字數不超過30字:'+input_message


        message_log.append({'role': 'user', 'content': last_msg})

        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_message

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==47) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我口齒不清'
        input_message_2 = '請身為一位發音不清楚的人，口齒不清的回覆，字數不超過20字:'+input_message


        message_log.append({'role': 'user', 'content': last_msg})

        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_message

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output

    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==48) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我很粗俗、很粗魯'
        input_message_2 = '請身為一位粗魯的人，粗俗的回覆，字數不超過20字:'+input_message


        message_log.append({'role': 'user', 'content': last_msg})

        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_message

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output


    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==49) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我很喜歡錢，勢利眼'
        input_message_2 = '請身為一位貪財的人，事錢如命、只看利益，字數不超過20字:'+input_message


        message_log.append({'role': 'user', 'content': last_msg})

        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_message

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output

    #######################################
    # ----------- Dream anwser  -----------#
    elif (flag_silence==50) :
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        input_msg = '我的名字是卡米兔，我很喜歡唱歌'
        input_message_2 = '請用唱歌回覆，字數不超過30字:'+input_message


        message_log.append({'role': 'user', 'content': last_msg})

        # 2. Put AI model rose to "AI form"
        message_log.append({'role': 'assistant', 'content': input_message_2})      # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_5 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=0.9,               
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
        # 6. output message 
        reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
        text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage

        # 7. output message 
        compare_msg=input_message

        # 8.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        line_bot_api.reply_message(event.reply_token,text_message)          # line output
















    else:
        #######################################
        # ----------- AI anwser 1------------ #
        # 1. message buffer
        message_log = []                                                    # Add a intput message from the chatbot to the conversation history
        if((last_msg=="") or ("卡米" in input_message)or ("誰" in input_message)):
            cami_msg = '我是卡米兔, 我是一個開心的兔寶寶!'
            message_log.append({'role': 'assistant', 'content': cami_msg})  # like 'My name is 卡米兔, I am a happy rabbit.'
        else:
            # 2. Put AI model rose to "AI form"
            message_log.append({'role': 'assistant', 'content': last_msg})  # like 'My name is 卡米兔, I am a happy rabbit.'
        # 3. Put input message to "user form" 
        message_log.append({'role': 'user', 'content': input_message})
        # 4. Setting AI module
        response_1 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
            temperature=2,
            messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
        )
        # 5.get output message & put into message_log
        message_log.append({'role': response_1.choices[0].message.role, 'content': response_1.choices[0].message.content})
        # 6. output message 
        compare_msg=input_message

        # 7.recode message
        for csv_row in csv_read_all:     
            if csv_row['groupID']==Group_ID:                                # check user ID 
                csv_row['last_msg']=compare_msg.replace('\n','')            # update AI msg
            else:
                continue    
        try:
            with open('./user.csv', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, csv_format)           # using csv.writer method from CSV package
                csv_writer.writeheader()                                    # write header too
                for csv_row in csv_read_all:                                # parser csv data 
                    csv_writer.writerow(csv_row)                            # write
        except UnicodeEncodeError:                                          # chinese bug
            print("File error, please close the file")

        #######################################
        # ----------- AI anwser 2------------ #
        #     1. Add a message from the chatbot2  (to reduce negative answer)#
        if ("不知道" in compare_msg) or ("我無法" in compare_msg) or ("不理解" in compare_msg) or ("我不懂" in compare_msg) or ("我不能" in compare_msg) or  ("我无法" in compare_msg) or ("我沒有" in compare_msg) or ("不明白" in compare_msg) or ("我不太" in compare_msg) or ("不了解" in compare_msg) or ("我不是" in compare_msg) or ("不清楚" in compare_msg)or ("不確定" in compare_msg) or ("不提供" in compare_msg) or ("sorry" in compare_msg):
           
            # 2. Setting AI module
            response_2 = openai.Completion.create(
                engine = "text-davinci-003",                        # select model
                prompt = input_message,                             # input string
                max_tokens = 1024,                                  # response tokens
                temperature = 1,                                    # diversity related for NLG model
                top_p = 0.8,                                        # diversity related
                n = 1,                                              # num of response
            )
            # 3. reset output message
            reply_msg = ""
            reply_msg = response_2["choices"][0]["text"].replace('\n','')   # output AI anwser

            # 4. Exception
            if ("//" in reply_msg) or ("[" in reply_msg) or ("{" in reply_msg):
                reply_msg = "卡米不知道您在囉哩八說甚麼"
            elif("sorry" in reply_msg):
                reply_msg = "很抱歉，卡米兔不知道您在囉哩八說甚麼?"                


        # 5. Output to line text
        text_message = TextSendMessage(text=reply_msg)              # string to TextSendMessage
        line_bot_api.reply_message(event.reply_token,text_message)  # line output

# #######################################
# # ----------- Voice to txt----------- #
# @handler.add(MessageEvent, message=AudioMessage)                    # new event(line audio interative)
# def handle_AudioMessage(event):
#     openai.api_key = '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'
#     try:
#         if(event.message.type == 'audio'):
#             # 1.get line audio input
#             audio_content = line_bot_api.get_message_content(event.message.id)
#             path='./temp.mp3'                                       # temp file
#             # 2. save audio file
#             with open(path,'wb') as audio_fd:                       # read audio
#                 for audio_part in audio_content.iter_content():
#                     audio_fd.write(audio_part)                      # save in mp3 file
#             # 3. Voice to txt
#             with open("temp.mp3","rb") as audio_file:               # loading audio file to openAI trans                      
#                 response_4 = openai.Audio.transcribe(
#                     model = 'whisper-1',                            # only this model
#                     file  = audio_file                              # response_format ='text' (Format: json, srt, vtt)
#                 )
#                 # 4. Output to line text
#                 reply_msg = response_4['text']                      # get output
#                 text_message = TextSendMessage(text=reply_msg)      # string to TextSendMessage
#                 line_bot_api.reply_message(event.reply_token,text_message)
#     except openai.error.OpenAIError as e:
#         text_message = TextSendMessage(text="很抱歉，兔兔聽不懂你在說什麼")
#         line_bot_api.reply_message(event.reply_token,text_message)  # line output

#######################################
# ----------- Image to txt----------- #
# @handler.add(MessageEvent, message=ImageMessage)                    # new event(line audio interative)
# def handle_ImageMessage(event):
#     ocs_path = './ocs_image.png'
#     ocs_key_imgbb= '65b369b26d0791ec9683f99b326e5bfc'                   # https://api.imgbb.com/

#     # step 1 get image
#     try:
#         if(event.message.type == "image"):
#             getSendImage= line_bot_api.get_message_content(event.message.id)
#             with open(ocs_path,'wb') as ocs_file:
#                 for SendIamge in getSendImage.iter_content():
#                     ocs_file.write(SendIamge)
#     except Exception:
#         print("OCS error")


#     # step 2 get image
#     with open(ocs_path, "rb") as ocs_file:
#         ocs_url = "https://api.imgbb.com/1/upload"
#         ocs_payload = {
#             "key": ocs_key_imgbb,
#             "image": base64.b64encode(ocs_file.read()),
#         }
#         ocs_res = requests.post(ocs_url, ocs_payload)

#     # step 3 output link
#     json_parser = ocs_res.json() 
#     weblink = json_parser['data']['url']

#     # 1. message buffer
#     message_log = []                                                    # Add a intput message from the chatbot to the conversation history
#     input_msg = '我是圖片辨識助手'
#     openai.api_key = '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'                          # open AI account number

#     # 2. Put AI model rose to "AI form"
#     message_log.append({'role': 'assistant', 'content': input_msg})     # like 'My name is 卡米兔, I am a happy rabbit.'
#     # 3. Put input message to "user form" 
#     message_log.append({'role': 'user', 'content': weblink})
#     # 4. Setting AI module
#     response_5 = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo-0301",                                     # The name of the OpenAI chatbot model to use
#         temperature=0.3,
#         messages=message_log                                            # The conversation history up to this point, as a list of dictionaries
#     )
#     # 5.get output message & put into message_log
#     message_log.append({'role': response_5.choices[0].message.role, 'content': response_5.choices[0].message.content})
#     # 6. output message 
#     reply_msg = format(message_log[-1]['content'].strip())              # If no response with text is found, return the first response's content (which may be empty)
#     text_message = TextSendMessage(text=reply_msg)                      # string to TextSendMessage
#     line_bot_api.reply_message(event.reply_token,text_message)          # line output
    
#     img = Image.open(path)
#     pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
#     reply_msg = "文字識別結果:\n\n"+pytesseract.image_to_string(img, lang='chi_tra')
#     text_message = TextSendMessage(text=reply_msg)      # string to TextSendMessage
#     line_bot_api.reply_message(event.reply_token,text_message)

#############################################################
#####               Process input point                 #####
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))                        # run OS server (5000 is defined from yourself)
    app.run(host='0.0.0.0', port=port)                              # setting server port

