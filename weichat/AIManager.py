from weichat import Environment
from weichat.CustomerServiceMsgInterface import ServiceMsg
import json
import requests

def check_contain_chinese(check_str):
     for ch in check_str.decode('utf-8'):
         if u'\u4e00' <= ch <= u'\u9fff':
             return True
     return False

class AIManager:

    @classmethod
    def TransLateText(cls,toUserId,msgText):
        translateUrl=""
        if check_contain_chinese(msgText.encode()):
            translateUrl="http://api.weixin.qq.com/cgi-bin/media/voice/" \
                     "translatecontent?access_token=%s&lfrom=zh_CN&lto=en_US" % Environment.AccessToken.GetToken()
        else:
            translateUrl = "http://api.weixin.qq.com/cgi-bin/media/voice/" \
                           "translatecontent?access_token=%s&lfrom=en_US&lto=zh_CN" % Environment.AccessToken.GetToken()
        req=requests.post(translateUrl,data=msgText.encode())
        jsonData=json.loads(s=req.content.decode())
        ServiceMsg.SendText(toUserId,jsonData["to_content"])

    @classmethod
    def SendAiReply(cls,toUserId,media_id):
        AiUrl = "http://api.weixin.qq.com/cgi-bin/media/voice/" \
                "addvoicetorecofortext?" \
                "access_token=%s&format=&" \
                "voice_id=%s&lang=zh_CN" % (Environment.AccessToken.GetToken(),media_id)
        req = requests.post(AiUrl)
        jsonData = json.loads(s=req.content.decode())
        if jsonData["errmsg"] != "ok":
            ServiceMsg.SendText(toUserId, "我听不清楚你在说什么")
            return
        AiUrl="http://api.weixin.qq.com/cgi-bin/media/voice/" \
              "queryrecoresultfortext?access_token=%s" \
              "&voice_id=%s&lang=zh_CN" % (Environment.AccessToken.GetToken(),media_id)
        req = requests.post(AiUrl)
        jsonData = json.loads(s=req.content.decode())
        ServiceMsg.SendText(toUserId, jsonData["result"])