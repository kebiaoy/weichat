from weichat import Environment
import json
from jsonschema import validate, ValidationError
import xml.etree.ElementTree as ET
import requests
import os
import sys
import time
import cv2


class SourceMaterial:
    tempSourceMaterial = {}
    foreverSourceMaterial = {}
    xmlPath = ""
    strStatus="status"
    strStatusNew="new"
    strStatusAdded="added"
    strMediaId="mediaID"
    strExpriedTime="expiredTime"
    strTypeVideo="video"
    strTypeThumb="thumb"
    strType="type"
    strName="name"
    strPath="path"
    strThumbId="thumb_id"

    @classmethod
    def InitSourceMaterial(cls, xmlpath):
        cls.xmlPath = xmlpath
        xmlData = ET.parse(xmlpath)
        rootData = xmlData.getroot()
        tempNode = xmlData.find("tempSourceMaterial")
        for tempNodeChild in tempNode:
            mediaType = tempNodeChild.get(cls.strType)
            mediaStatus = tempNodeChild.get(cls.strStatus)
            mediaPath = tempNodeChild.get(cls.strPath)
            mediaName = tempNodeChild.get(cls.strName)
            assert mediaType != ""
            assert mediaStatus != ""
            assert mediaPath != ""
            assert mediaName != ""
            if mediaStatus == cls.strStatusNew:
                media_id, created_at = cls.AddTempSourceMaterial(mediaType, mediaPath, mediaName)
                if media_id != "" and created_at != 0:
                    tempNodeChild.set(cls.strStatus, cls.strStatusAdded)
                    tempNodeChild.set(cls.strMediaId, media_id)
                    tempNodeChild.set(cls.strExpriedTime, str(created_at + 3600 * 24 * 3))

                    if mediaType == cls.strTypeVideo:
                        cap = cv2.VideoCapture(os.path.join(mediaPath, mediaName))
                        success, frame = cap.read()
                        compression_params = []
                        compression_params.append(cv2.IMWRITE_JPEG_QUALITY)
                        compression_params.append(1)
                        tempFileName = os.path.splitext(mediaName)[0] + ".jpg"
                        cv2.imwrite(os.path.join(mediaPath, tempFileName), frame, compression_params)
                        cap.release()
                        thumb_media_id, thumb_created_at = cls.AddTempSourceMaterial(cls.strTypeThumb, mediaPath, tempFileName)
                        os.remove(os.path.join(mediaPath, tempFileName))
                        tempNodeChild.set(cls.strThumbId, thumb_media_id)
                        cls.tempSourceMaterial[mediaName] = {cls.strMediaId: media_id,
                                                             cls.strExpriedTime: created_at + 3600 * 24 * 3,
                                                             cls.strThumbId: thumb_media_id
                                                             }
                    else:
                        cls.tempSourceMaterial[mediaName] = {cls.strMediaId: media_id, cls.strExpriedTime: created_at + 3600 * 24 * 3}

            else:
                mediaMediaId = tempNodeChild.get(cls.strMediaId)
                mediaExpriedTime = tempNodeChild.get(cls.strExpriedTime)
                if mediaType == cls.strTypeVideo:
                    thumb_media_id = tempNodeChild.get(cls.strThumbId)
                    cls.tempSourceMaterial[mediaName] = {cls.strMediaId: mediaMediaId,
                                                         cls.strExpriedTime: mediaExpriedTime,
                                                         cls.strThumbId: thumb_media_id
                                                         }
                else:
                    cls.tempSourceMaterial[mediaName] = {cls.strMediaId: mediaMediaId, cls.strExpriedTime: int(mediaExpriedTime)}
        xmlData.write(file_or_filename=xmlpath,encoding="utf-8")

    @classmethod
    def HandleExpriedItem(cls, MaterialName):
        xmlData = ET.parse(cls.xmlPath)
        rootData = xmlData.getroot()
        print(ET.tostring(rootData, "unicode"))
        tempNode = xmlData.find("tempSourceMaterial")
        retParams={}
        for tempChild in tempNode:
            mediaType = tempChild.get(cls.strType)
            mediaStatus = tempChild.get(cls.strStatus)
            mediaPath = tempChild.get(cls.strPath)
            mediaName = tempChild.get(cls.strName)
            assert mediaType != ""
            assert mediaStatus != ""
            assert mediaPath != ""
            assert mediaName != ""
            if mediaName == MaterialName:
                media_id, created_at = cls.AddTempSourceMaterial(mediaType, mediaPath, mediaName)
                thumb_media_id=""
                if media_id != "" and created_at != 0:
                    tempChild.set(cls.strStatus, cls.strStatusAdded)
                    tempChild.set(cls.strMediaId, media_id)
                    tempChild.set(cls.strExpriedTime, str(created_at + 3600 * 24 * 3))
                    if mediaType == cls.strTypeVideo:
                        cap = cv2.VideoCapture(os.path.join(mediaPath, mediaName))
                        success, frame = cap.read()
                        compression_params = []
                        compression_params.append(cv2.IMWRITE_JPEG_QUALITY)
                        compression_params.append(1)
                        tempFileName = os.path.splitext(mediaName)[0] + ".jpg"
                        cv2.imwrite(os.path.join(mediaPath, tempFileName), frame, compression_params)
                        cap.release()
                        thumb_media_id, thumb_created_at = cls.AddTempSourceMaterial(cls.strTypeThumb, mediaPath, tempFileName)
                        os.remove(os.path.join(mediaPath, tempFileName))
                        tempChild.set(cls.strThumbId, thumb_media_id)
                        cls.tempSourceMaterial[mediaName] = {cls.strMediaId: media_id,
                                                             cls.strThumbId: thumb_media_id
                                                             }
                    else:
                        cls.tempSourceMaterial[mediaName] = {cls.strMediaId: media_id, cls.strExpriedTime: created_at + 3600 * 24 * 3}
                retParams={cls.strMediaId:media_id,cls.strThumbId:thumb_media_id}
                break
        return retParams
    @classmethod
    def GetArticle(cls,articlename):
        xmlData = ET.parse(cls.xmlPath)
        rootData = xmlData.getroot()
        articlesNode = xmlData.findall("articles")
        finNode=None
        retList=[]
        for xmlNode in articlesNode:
            if xmlNode.get("name")==articlename:
                finNode=xmlNode
                break
        if finNode==None:
            return []

        for childNode in finNode:
            retList.append(childNode.attrib)
        return retList
    @classmethod
    def GetSourceMaterial(cls, MaterialName):
        retParams={}
        if cls.tempSourceMaterial.get(MaterialName) != None:
            MaterialItem = cls.tempSourceMaterial.get(MaterialName)
            ExpriedTime = MaterialItem.get(cls.strExpriedTime)
            if time.time() > int(ExpriedTime):
                return cls.HandleExpriedItem()
            retParams={cls.strMediaId:MaterialItem.get(cls.strMediaId),
                       cls.strThumbId:MaterialItem.get(cls.strThumbId)}
        elif cls.foreverSourceMaterial.get(MaterialName) != None:
            pass
        else:
            print("No such Material")
        return retParams

    @classmethod
    def AddTempSourceMaterial(cls, Type, DataPath, name):
        strUrl = "https://api.weixin.qq.com/cgi-bin/media/upload?" \
                 "access_token=%s&type=%s" % (Environment.AccessToken.GetToken(), Type)
        print(strUrl)
        try:
            f=open(os.path.join(DataPath, name), "rb")
            mediaData=f.read()
            f.close()
            files = {'media': (name, mediaData, 'application/octet-stream')}
        except IOError as e:
            print(e.strerror)
            return
        resp = requests.post(url=strUrl, files=files)
        jsonData = json.loads(resp.text)
        mediaDataSchemeSuccess = {
            "$schema": "http://json-schema.org/draft-06/schema#",
            "title": "Product set",
            "type": "object",
            "properties": {
                "type": {"type": "string"},
                "media_id": {"type": "string"},
                "created_at": {"type": "number"}
            },
            "required": ["type", "media_id", "created_at"]
        }
        if Type==cls.strTypeThumb:
            mediaDataSchemeSuccess = {
                "$schema": "http://json-schema.org/draft-06/schema#",
                "title": "Product set",
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "thumb_media_id": {"type": "string"},
                    "created_at": {"type": "number"}
                },
                "required": ["type", "thumb_media_id", "created_at"]
            }
        try:
            validate(jsonData, mediaDataSchemeSuccess)
            if Type==cls.strTypeThumb:
                return jsonData["thumb_media_id"], jsonData["created_at"]
            return jsonData["media_id"], jsonData["created_at"]
        except ValidationError as e:
            print(e.message)
            try:
                mediaDataSchemeFailed = {
                    "$schema": "http://json-schema.org/draft-06/schema#",
                    "title": "Product set",
                    "type": "object",
                    "properties": {
                        "errcode": {"type": "number"},
                        "errmsg": {"type": "string"}
                    },
                    "required": ["errcode", "errmsg"]
                }
                validate(jsonData, mediaDataSchemeFailed)
                print("errcode ", jsonData["errcode"], " errmsg ", jsonData["errmsg"])
                return "", 0
            except ValidationError as e1:
                print(e1.message)
                return "", 0
