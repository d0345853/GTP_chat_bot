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


##################################
# 必須放上自己的Channel Access Token
line_bot_api = LineBotApi('ZDKxXNN1YeHrqa8+lOlgv9RjOl/2kCVpO5xoDLC3SHfnBBdA9IA3Z/fOQPiHEJhvQ9ImNXMMF/q6Dzl5Rk9UMtpi0a+NJzg+81oARe6dOeaubeXm42HCnNyGJ1j9+oBmOUj+UrZaXLYD3fYc/ybLmgdB04t89/1O/w1cDnyilFU=')
# 必須放上自己的Channel Secret
handler = WebhookHandler('91ba25530818a52375c97fbd27aac56c')
# 更新訊息
# line_bot_api.push_message('Ub08558de58b09af13f8e03da6a5dfca6', TextSendMessage(text='哈囉哈囉~兔兔來囉!'))


# ##################################
# class GroupTicket(models.Model):
#     groupId = models.CharField(max_length=35)
#     expire = models.DateTimeField(null=True)
#     createDate = models.DateTimeField()
#     def createByGroupId(groupId):
#         GroupTicket.objects.filter(groupId=groupId).delete()
#         groupTicket = GroupTicket(
#             groupId = groupId,
#             expire = timezone.now() + timedelta(minutes = 5),
#             createDate = timezone.now()
#         )
#         groupTicket.save()
#     def isExpireByGroupId(groupId):
#         groupTickets = GroupTicket.objects.filter(groupId=groupId)
#         if groupTickets.exists() == False:
#             return False
#         groupTicket = groupTickets[0]
#         return timezone.now() < groupTicket.expire
    
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
    # message = text=event.message.text  #line input
    # if event.source.type == 'group' and message == '卡米兔說話':
    #     GroupTicket.createByGroupId(event.source.group_id)
    #     line_bot_api.reply_message(event.reply_token,'好喔好喔，兔兔來囉')  #line output
    # elif event.source.type == 'group' and message == '卡米兔安靜':
    #     GroupTicket.objects.filter(groupId=event.source.group_id).delete()
    #     line_bot_api.reply_message(event.reply_token,'好喔好喔，安靜模式')  #line output
    # elif (event.source.type == 'group' and GroupTicket.isExpireByGroupId(event.source.group_id) or event.source.type != 'group'):


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


    # Add a message from the chatbot to the conversation history
    message_log = []
    message_log.append({'role': 'assistant', 'content': 'You are a helpful assistant.'})

    message_log.append({'role': 'user', 'content': message})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # The name of the OpenAI chatbot model to use
        messages=message_log   # The conversation history up to this point, as a list of dictionaries
    )
    message_log.append({'role': response.choices[0].message.role, 'content': response.choices[0].message.content})

    #reply_msg = response.choices[0].message.content.replace('\n','')
    # reply_msg = response.choices[0].message.content
    # for choice in response.choices:
    #     if "text" in choice:
    #         reply_msg =choice.text
    #         break
    reply_msg = format(message_log[-1]['content'].strip())
    # If no response with text is found, return the first response's content (which may be empty)
    # return response.choices[0].message.content
    # reply_msg = response[-1]['content'].strip()


    text_message = TextSendMessage(text=reply_msg)              # 轉型
    line_bot_api.reply_message(event.reply_token,text_message)  #line output


#主程式
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

