import requests
from weichat import Environment
from weichat.SourceMaterialManager import SourceMaterial
import json
class ServiceMsg:
    StrMsgUrl="https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s"

    @classmethod
    def SendText(cls, toUserId, text):
        """"调用客服接口发送一段文本数据
            toUserId 发送给哪个用户
            text 需要发送的文本
        """
        textData = r'{' \
                   r'"touser":"%s",' \
                   r'"msgtype":"text",' \
                   r'"text":' \
                   r'{' \
                   r'"content":"%s"' \
                   r'}' \
                   r'}' % (toUserId, text)
        textUrl = cls.StrMsgUrl % Environment.AccessToken.GetToken()
        req = requests.post(url=textUrl, data=textData.encode())
        if req.status_code != 200:
            print("send text failed")

    @classmethod
    def SendImage(cls,toUserId,ImageName):
        MediaId = SourceMaterial.GetSourceMaterial(ImageName).get(SourceMaterial.strMediaId)
        textData = r'{' \
                   r'"touser":"%s",' \
                   r'"msgtype":"image",' \
                   r'"image":' \
                   r'{' \
                   r'"media_id":"%s"' \
                   r'}' \
                   r'}' % (toUserId, MediaId)
        textUrl = cls.StrMsgUrl % Environment.AccessToken.GetToken()
        req = requests.post(url=textUrl, data=textData.encode())
        if req.status_code != 200:
            print("send image failed")

    @classmethod
    def SendVoice(cls, toUserId, VoiceName):
        MediaId = SourceMaterial.GetSourceMaterial(VoiceName).get(SourceMaterial.strMediaId)
        textData = r'{' \
                   r'"touser":"%s",' \
                   r'"msgtype":"voice",' \
                   r'"voice":' \
                   r'{' \
                   r'"media_id":"%s"' \
                   r'}' \
                   r'}' % (toUserId, MediaId)
        textUrl = cls.StrMsgUrl % Environment.AccessToken.GetToken()
        req = requests.post(url=textUrl, data=textData.encode())
        if req.status_code != 200:
            print("send voice failed")

    @classmethod
    def SendVideo(cls, toUserId, VideoName,title,description):
        MediaItem = SourceMaterial.GetSourceMaterial(VideoName)
        textData = r'{' \
                   r'"touser":"%s",' \
                   r'"msgtype":"video",' \
                   r'"video":' \
                   r'{' \
                   r'"media_id":"%s",' \
                   r'"thumb_media_id":"%s",' \
                   r'"title":"%s",' \
                   r'"description":"%s"' \
                   r'}' \
                   r'}' % (toUserId,
                           MediaItem.get(SourceMaterial.strMediaId),
                           MediaItem.get(SourceMaterial.strThumbId),
                           title,
                           description)
        textUrl = cls.StrMsgUrl % Environment.AccessToken.GetToken()
        req = requests.post(url=textUrl, data=textData.encode())
        if req.status_code != 200:
            print("send video failed")
    @classmethod
    def SendMisic(cls,toUserId,picName,title,description,musicUrl,hqMusicUrl):
        MediaId = SourceMaterial.GetSourceMaterial(picName).get(SourceMaterial.strMediaId)
        textData=r'{' \
                 r'"touser":"%s",' \
                 r'"msgtype":"music",' \
                 r'"music":' \
                 r'{' \
                 r'"title":"%s",' \
                 r'"description":"%s",' \
                 r'"musicurl":"%s",' \
                 r'"hqmusicurl":"%s",' \
                 r'"thumb_media_id":"%s" ' \
                 r'}' \
                 r'}'%(toUserId,title,description,musicUrl,hqMusicUrl,MediaId)
        textUrl = cls.StrMsgUrl % Environment.AccessToken.GetToken()
        req = requests.post(url=textUrl, data=textData.encode())

    @classmethod
    def SendPicMsg(cls,toUserId,articles):
        textData={
                 "touser":toUserId,
                 "msgtype":"news",
                 "news":{
                 "articles":SourceMaterial.GetArticle(articles)
                 }
                 }
        textUrl = cls.StrMsgUrl % Environment.AccessToken.GetToken()
        req = requests.post(url=textUrl, data=json.dumps(textData,ensure_ascii=False).encode())