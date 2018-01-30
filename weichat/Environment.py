import requests
import json
import time
from jsonschema import validate,ValidationError


class EnvInfo:
    "AppInfo"
    appid = ""
    appsecret = ""

    @classmethod
    def SetAppParam(cls,AppId, AppSecret):
        cls.appid = AppId
        cls.appsecret = AppSecret


class AccessToken:
    "静态成员"
    strAccessToken = ""
    expriedTime = 0

    @classmethod
    def IsExpried(cls):
        return time.time() >= cls.expriedTime
    @classmethod
    def GetToken(cls):
        """
        获取微信 token接口，调用该方法之前appid和screte必须先设置正确
        返回token如果成功
        """
        if cls.strAccessToken == "" or cls.IsExpried():
            return cls.AccessToken()
        return cls.strAccessToken

    @classmethod
    def AccessToken(cls):
        accessUrl = r"https://api.weixin.qq.com/cgi-bin/token?" \
                    r"grant_type=client_credential&appid=%s&secret=%s" % (EnvInfo.appid, EnvInfo.appsecret)
        req = requests.request(method="get",url=accessUrl)

        if req.status_code != 200:
            print(req.text)
            return ""
        jsonData = json.loads(req.text)
        strSchemaSuccess = {
            "$schema": "http://json-schema.org/draft-06/schema#",
            "title": "Product set",
            "type": "object",
            "properties": {
                "access_token": {"type": "string"},
                "expires_in": {"type": "number"}
            },
            "required": ["access_token", "expires_in"]
        }
        try:
            validate(jsonData, strSchemaSuccess)
            cls.strAccessToken = jsonData["access_token"]
            cls.expriedTime = jsonData["expires_in"] + int(time.time())
            if cls.strAccessToken == "" or cls.expriedTime == 0:
                print("GetAccessToken Failed")
            print("GetAccessToken Success ", cls.strAccessToken, " expires time ", cls.expriedTime)
            return cls.strAccessToken
        except ValidationError as e:
            print(e.message)
            try:
                strSchemaFailed = {
                    "$schema": "http://json-schema.org/draft-06/schema#",
                    "title": "Product set",
                    "type": "object",
                    "properties": {
                        "errcode": {"type": "number"},
                        "errmsg": {"type": "string"}
                    },
                    "required": ["errcode", "errmsg"]
                }
                validate(jsonData, strSchemaFailed)
                print("errcode ",jsonData["errcode"]," errmsg ",jsonData["errmsg"])
                return ""
            except ValidationError as e1:
                print(e1.message)
                return ""
