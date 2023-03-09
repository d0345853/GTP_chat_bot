# -*- coding: utf-8 -*-
"""
Created on Wed Jun  2 21:16:35 2021

@author: Ivan
版權屬於「行銷搬進大程式」所有，若有疑問，可聯絡ivanyang0606@gmail.com

Line Bot聊天機器人
第一章 Line Bot申請與串接
Line Bot機器人串接與測試
"""
#載入LineBot所需要的套件
from flask import Flask, request, abort
import openai

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

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

    
    #message = TextSendMessage(text=event.message.text)  #line input
    message = text=event.message.text  #line input


    # if "卡米兔安靜" in message:
    #     text_message = TextSendMessage('好的遵命')              # 轉型
    #     line_bot_api.reply_message(event.reply_token,text_message)  #line output
    # elif "卡米兔說話" in message:
    #     text_message = TextSendMessage('好的遵命')              # 轉型
    #     line_bot_api.reply_message(event.reply_token,text_message)  #line output            
    # else:

    openai.api_key = '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'
    # response = openai.Completion.create(
    #     engine = "text-davinci-003",    # select model
    #     prompt = message,     
    #     max_tokens = 512,               # response tokens
    #     temperature = 1,                # diversity related NLG模型
    #     top_p = 0.75,                   # diversity related
    #     n = 1,                          # num of response
    # )
    #reply_msg = response["choices"][0]["text"].replace('\n','')

    message_log.append({"role": "user", "content": message})
    # Add a message from the chatbot to the conversation history
    message_log.append({"role": "assistant", "content": "You are a helpful assistant."})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # The name of the OpenAI chatbot model to use
        messages=message_log,   # The conversation history up to this point, as a list of dictionaries
        max_tokens=2000,        # The maximum number of tokens (words or subwords) in the generated response
        stop=None,              # The stopping sequence for the generated response, if any (not used here)
        temperature=0.8,        # The "creativity" of the generated response (higher temperature = more creative)
    )
    #reply_msg = response.choices[0].message.content.replace('\n','')
    reply_msg = response.choices[0].message.content
    for choice in response.choices:
        if "text" in choice:
            reply_msg =choice.text
            break

    # If no response with text is found, return the first response's content (which may be empty)
    # return response.choices[0].message.content
    # reply_msg = response[-1]['content'].strip()


    text_message = TextSendMessage(text=message_log)              # 轉型
    line_bot_api.reply_message(event.reply_token,text_message)  #line output


#主程式
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


# import openai

# from flask_ngrok import run_with_ngrok   # colab 使用，本機環境請刪除
# from flask import Flask, request

# # 載入 LINE Message API 相關函式庫
# from linebot import LineBotApi, WebhookHandler
# from linebot.models import TextSendMessage   # 載入 TextSendMessage 模組
# import json

# app = Flask(__name__)

# @app.route("/", methods=['POST'])
# def linebot():
#     body = request.get_data(as_text=True)
#     json_data = json.loads(body)
#     print(json_data)
#     try:
#         line_bot_api = LineBotApi('ZDKxXNN1YeHrqa8+lOlgv9RjOl/2kCVpO5xoDLC3SHfnBBdA9IA3Z/fOQPiHEJhvQ9ImNXMMF/q6Dzl5Rk9UMtpi0a+NJzg+81oARe6dOeaubeXm42HCnNyGJ1j9+oBmOUj+UrZaXLYD3fYc/ybLmgdB04t89/1O/w1cDnyilFU=')
#         handler = WebhookHandler('91ba25530818a52375c97fbd27aac56c')
#         line_bot_api.push_message('Ub08558de58b09af13f8e03da6a5dfca6', TextSendMessage(text='你可以開始了'))

#         signature = request.headers['X-Line-Signature']
#         handler.handle(body, signature)
#         tk = json_data['events'][0]['replyToken']
#         msg = json_data['events'][0]['message']['text']
#         # 取出文字的前五個字元，轉換成小寫
#         ai_msg = msg[:6].lower()
#         reply_msg = ''
#         # 取出文字的前五個字元是 hi ai:
#         if ai_msg == 'hi ai:':
#             openai.api_key = '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'
#             # 將第六個字元之後的訊息發送給 OpenAI
#             response = openai.Completion.create(
#                 engine='text-davinci-003',
#                 prompt=msg[6:],
#                 max_tokens=256,
#                 temperature=0.5,
#                 )
#             # 接收到回覆訊息後，移除換行符號
#             reply_msg = response["choices"][0]["text"].replace('\n','')
#         else:
#             reply_msg = msg
#         text_message = TextSendMessage(text=reply_msg)
#         line_bot_api.reply_message(tk,text_message)
#     except:
#         print('error')
#     return 'OK'

# if __name__ == "__main__":
#     run_with_ngrok(app)   # colab 使用，本機環境請刪除
#     app.run()