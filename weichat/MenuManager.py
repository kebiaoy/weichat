import json
from weichat import Environment
import requests

class MenuManager:
    @classmethod
    def CreateMenu(cls,MenuData):
        f=open(MenuData,"rb")
        jsonData=json.loads(s=f.read(),encoding="utf-8")
        f.close()
        MenuUrl="https://api.weixin.qq.com/cgi-bin/menu/create?access_token=%s" % Environment.AccessToken.GetToken()
        req=requests.post(MenuUrl,data=json.dumps(obj=jsonData,ensure_ascii=False).encode())
        print(req.text)