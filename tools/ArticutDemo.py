#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from ArticutAPI import Articut
from pprint import pprint
from requests import post
import re

purgePat = re.compile("</?\w+(_+\w?)?>")
pronounDropPat = re.compile("^<ENTITY_pronoun>[^<]+</ENTITY_pronoun>|^<ENTITY_person>[^<]+</ENTITY_person>")
innerDropPat = re.compile("^<FUNC_inner>[^<]+</FUNC_inner>")
username = "peter.w@droidtown.co" #這裡填入您在 https://api.droidtown.co 使用的帳號 email。若使用空字串，則預設使用每小時 2000 字的公用額度。
apikey   = "EnVFPaXLkq-OwWkW2Rw-@yrrcfqWS-&" #這裡填入您在 https://api.droidtown.co 登入後取得的 api Key。若使用空字串，則預設使用每小時 2000 字的公用額度。

articut = Articut(username, apikey)
topicNameLIST = []
#for i in wikifileLIST:
    #with open(i) as f:
        #topicNameLIST.append(i.replace(".json" ""))
        #inputSTR = json.load(f)["abstract"]
inputSTR = """蔣渭水（臺灣話：Tsiúnn Ūi-súi，1888年2月8日（有其他說法[註 1]）—1931年8月5日），字雪谷，是出身臺灣宜蘭的醫師、社會運動者及民族運動者。他是臺灣文化協會及臺灣民眾黨共同創辦人及重要領導人物之一。他是臺灣日治時期反對殖民統治運動代表性的人物之一。[1]

他著有代表作短文《臨床講義》等；他在該文中以醫學診療表單形式，講述了當時臺灣社會如何遭受嚴重的「文化營養不良」。

他的弟弟是知名政治人物蔣渭川。 """
inputSTR = inputSTR.replace(" ", "").replace("\n", "")
resultDICT = articut.parse(inputSTR, level="lv2")
toAddLIST = []
for i in resultDICT["result_pos"]:
    if "<ACTION_verb>領導</ACTION_verb>" in i:
        i = re.sub(pronounDropPat, "", i)
        i = re.sub(innerDropPat, "", i)
        toAddLIST.append(re.sub(purgePat, "", i))


url = "https://api.droidtown.co/Loki/Call/"

# create intent
payload = {
    #"username" : "peter.w@droidtown.co", # 這裡填入您在 https://api.droidtown.co 使用的帳號 email。     Docker 版不需要此參數！
    #"loki_key" : "_EWl=uo65G3k+=qcV#CmNLW7eORhS2G", # 這裡填入您在 https://api.droidtown.co 登入後取得的 loki_key。 Docker 版不需要此參數！
    "project": "myProj", #專案名稱
    "intent": "Lead_01", #意圖名稱
    "func": "create_intent",
    "data": {
        "type": "basic" #意圖類別
    }
}

response = post(url, json=payload).json()

# update userdefined
payload = {
    #"username" : "", # 這裡填入您在 https://api.droidtown.co 使用的帳號 email。     Docker 版不需要此參數！
    #"loki_key" : "", # 這裡填入您在 https://api.droidtown.co 登入後取得的 loki_key。 Docker 版不需要此參數！
    "project": "Weather", #專案名稱
    "intent": "AskWeather", #意圖名稱
    "func": "update_userdefined",
    "data": {
        "user_defined": { #自定義辭典
            "_topicName": topicNameLIST
        }
    }
}

response = post(url, json=payload).json()

# insert utterance
payload = {
    #"username" : "peter.w@droidtown.co", # 這裡填入您在 https://api.droidtown.co 使用的帳號 email。     Docker 版不需要此參數！
    #"loki_key" : "_EWl=uo65G3k+=qcV#CmNLW7eORhS2G", # 這裡填入您在 https://api.droidtown.co 登入後取得的 loki_key。 Docker 版不需要此參數！
    "project": "myProj", #專案名稱
    "intent": "Lead_01", #意圖名稱
    "func": "insert_utterance",
    "data": {
        "utterance": toAddLIST,
        "checked_list": [ #勾選的詞性
            "ENTITY_noun"
        ]
    }
}

response = post(url, json=payload).json()
pprint(response)