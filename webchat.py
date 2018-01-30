# -*- coding: utf-8 -*-
# filename: main.py
from http.server import HTTPServer, BaseHTTPRequestHandler
from http.client import parse_headers
from urllib.request import Request, urlopen
from urllib.parse import urlparse, parse_qs
import hashlib
import xml.etree.ElementTree as ET
import json
from weichat.CustomerServiceMsgInterface import ServiceMsg
from weichat import Environment
from weichat.SourceMaterialManager import SourceMaterial
from weichat.MenuManager import MenuManager
from weichat.AIManager import AIManager
import cv2


class MyHandler(BaseHTTPRequestHandler):
    # 这一步主要是为了验证token使用的，微信公众号界面
    def do_GET(self):
        parse_data = urlparse(self.path)
        qs_data = parse_qs(parse_data.query)
        timestamp = qs_data["timestamp"][0]
        nonce = qs_data["nonce"][0]
        list = ["biaobiao123", timestamp, nonce]
        list.sort()
        sha1 = hashlib.sha1()
        sha1.update(list[0].encode('utf-8'))
        sha1.update(list[1].encode('utf-8'))
        sha1.update(list[2].encode('utf-8'))
        hashcode = sha1.hexdigest()
        if hashcode == qs_data["signature"][0]:
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(qs_data["echostr"][0].encode('utf-8'))

    # success必须先发送，因为微信文档说的是接收到消息后处理时间不能超过5秒，超过5秒会失败
    def send_success(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.send_header("Content-Length", "7")
        self.end_headers()
        self.wfile.write("success".encode('utf-8'))

    def do_POST(self):
        self.send_success()
        headerData = self.headers.keys()
        data = self.rfile.read()
        print(data)
        xmlData = ET.fromstring(data)
        msgToUserName = xmlData.find("ToUserName")
        msgFromUserName = xmlData.find("FromUserName")
        msgType = xmlData.find("MsgType")
        msgContent = xmlData.find("Content")
        if msgType.text == "text":
            AIManager.TransLateText(msgFromUserName.text,msgContent.text)
        elif msgType.text=="voice":
            msgMediaId = xmlData.find("MediaId")
            AIManager.SendAiReply(msgFromUserName.text,msgMediaId.text)
        elif msgType.text == "event":
            msgEvent = xmlData.find("Event")
            if msgEvent.text == "CLICK":
                EventKey= xmlData.find("EventKey")
                if EventKey.text=="firstSeeWorld":
                    ServiceMsg.SendVideo(msgFromUserName.text, "firstSeeWorld.mp4","睁眼看世界","沐沐第一次睁眼看世界")
                elif EventKey.text=="firstWantEeatMilk":
                    ServiceMsg.SendVideo(msgFromUserName.text, "firstWantEeatMilk.mp4", "我是好吃鬼", "沐沐第一次哭着要吃奶奶了")
                elif EventKey.text == "firstLose":
                    ServiceMsg.SendVideo(msgFromUserName.text, "firstLose.mp4", "投降啦", "我家沐沐睡觉就是投降")
                elif EventKey.text == "mumuSwim":
                    ServiceMsg.SendVideo(msgFromUserName.text, "mumuSwim.mp4", "洗澡澡啦", "我爱洗澡皮肤好好")
                elif EventKey.text == "shuohua":
                    ServiceMsg.SendImage(msgFromUserName.text,"shuohua.jpg")
                elif EventKey.text == "weixiao":
                    ServiceMsg.SendImage(msgFromUserName.text, "weixiao.jpg")
                elif EventKey.text == "xiangShouAnMo":
                    ServiceMsg.SendImage(msgFromUserName.text, "xiangShouAnMo.jpg")
                elif EventKey.text == "mumuZuiGuaiGuai":
                    ServiceMsg.SendImage(msgFromUserName.text, "mumuZuiGuaiGuai.jpg")
                elif EventKey.text == "Try":
                    ServiceMsg.SendVoice(msgFromUserName.text, "Try.mp3")
                elif EventKey.text == "pythonTest":
                    ServiceMsg.SendPicMsg(msgFromUserName.text, "pythonTest")
                elif EventKey.text == "text":
                    ServiceMsg.SendText(msgFromUserName.text, "即使天空海阔没有爱，还有你这一个人")
                elif EventKey.text == "Music":
                    ServiceMsg.SendMisic(msgFromUserName.text, "aihou.jpg","送一首爱后余生给你","这是一首很霸气的歌哦"
                                         ,"https://y.qq.com/n/yqq/song/004b12Dm4L0snA.html","https://y.qq.com/n/yqq/song/004b12Dm4L0snA.html")

if __name__ == '__main__':

    # appid 和 appsecret 需要在微信公众号页面获取
    Environment.EnvInfo.SetAppParam("wxfb561e3bff378164", "ff4762e4a89900ec0ea4492c3c1fabef")
    MenuManager.CreateMenu("./res/菜单.json")
    # 初始化素材环境
    SourceMaterial.InitSourceMaterial("./res/Sourcematerial.xml")
    app = HTTPServer(("192.168.31.162", 80), MyHandler)
    app.serve_forever()
