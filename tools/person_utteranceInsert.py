#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from ArticutAPI import Articut
from requests import post

import os
import re
purgePat = re.compile("</?[a-zA-Z]+(_[a-zA-Z]+)?>")
washPat = re.compile("\(\)|《.+?》")

import json
accountDICT = json.load(open("account.info", encoding="utf-8"))

articut = Articut(username=accountDICT["username"], apikey=accountDICT["api_key"])
lokiURL = "https://api.droidtown.co/Loki/Call/"  #線上版 URL

def _getInfo(accountDICT, projectSTR=""):
    if projectSTR == "":
        response = ""
    else:
        payload = {
            "username" : accountDICT["username"], # 這裡填入您在 https://api.droidtown.co 使用的帳號 email。     Docker 版不需要此參數！
            "loki_key": accountDICT["loki_key"], # 這裡填入您在 https://api.droidtown.co 登入後取得的 loki_key。     Docker 版不需要此參數！
            "project": projectSTR, # 這裡填入您想要查詢的 project name。     線上版不需要此參數！
            "func": "get_info",
            "data": {}
        }
        response = post(lokiURL, json=payload).json()
    return response

def _updateUserDefined(accountDICT, projectSTR="", userdefinedDICT={}):
    payload = {
        "username" : accountDICT["username"], # 這裡填入您在 https://api.droidtown.co 使用的帳號 email。     Docker 版不需要此參數！
        "loki_key" : accountDICT["loki_key"], # 這裡填入您在 https://api.droidtown.co 登入後取得的 loki_key。 Docker 版不需要此參數！
        "project": projectSTR,
        "func": "update_userdefined",
        "data": {
            "user_defined": {
            }
        }
    }
    for k in userdefinedDICT:
        userdefinedDICT[k] = list(set(userdefinedDICT[k]))
    payload["data"]["user_defined"].update(userdefinedDICT)
    response = post(lokiURL, json=payload).json()
    print(response)
    return response

def _createLokiIntent(accountDICT, projectSTR="", intentSTR=""):
    if projectSTR == "" or intentSTR == "":
        response = {"status":"false",
                    "msg":"projectSTR or intentSTR cannot be empty string."}
    else:
        payload = {
            "username" : accountDICT["username"],
            "loki_key" : accountDICT["loki_key"],
            "project": projectSTR,
            "intent": intentSTR,
            "func": "create_intent",
            "data": {
                "type": "basic"
            }
        }
        response = post(lokiURL, json=payload).json()
    return response

def insertLokiUtterance(accountDICT, projectSTR="", intentSTR="", utteranceLIST=[]):

    #Check if the intentSTR exists in desiginated projectSTR.
    intentCheck = _getInfo(accountDICT, projectSTR)
    if intentSTR not in intentCheck["result"]["intent"]:
        _createLokiIntent(accountDICT, projectSTR, intentSTR)
    # #

    #Preparing Payload
    payload = {
        "username" : accountDICT["username"],
        "loki_key" : accountDICT["loki_key"],
        "project": projectSTR,
        "intent": intentSTR,
        "func": "insert_utterance",
        "data": {
            "utterance": utteranceLIST, #新增的句子
            "checked_list": [   #所有詞性全勾選。你可以把不要勾的項目註解掉。
                "ENTITY_noun",  #包含所有名詞
                "UserDefined",
                "ENTITY_num",
                "DegreeP",
                "MODIFIER_color",
                "LOCATION",
                "KNOWLEDGE_addTW",
                "KNOWLEDGE_routeTW",
                "KNOWLEDGE_lawTW",
                "KNOWLEDGE_url",
                "KNOWLEDGE_place",
                "KNOWLEDGE_wikiData",
                "KNOWLEDGE_currency"
            ]
        }
    }
    # #

    response = post(lokiURL, json=payload).json()
    return response


if __name__ == "__main__":
    projectSTR = "AItlas_wiki_people2"
    dataDIR = "../data/local_data/People_2306_washed2401"

    for d in os.listdir(dataDIR):
        if d in "一二三四五六七八九十":
            pass
        else:
            fileDIR = f"{dataDIR}/{d}"
            for j in os.listdir(fileDIR): #j 就是檔名
                entrySTR = j.replace(".json", "")
                utteranceDICT = {"BeV":[]}
                userdefinedDICT = {"_entryName":[]}
                #取得條目內容
                try:
                    jContent = json.load(open(f"{fileDIR}/{j}", "r", encoding="utf-8"))
                except Exception as e:
                    with open("error.log", "a", encoding="utf-8") as log:
                        log.write(f"{fileDIR}/{j} found error {e}\n")
                    continue

                jContent["abstract"] = washPat.sub("", jContent["abstract"]).replace("\n", "")
                try:
                    lv2ResultDICT = articut.parse(jContent["abstract"])
                    #多驗一步，看這個條目是不是「人名」，若是，稍後要再加一份「非人名 (梅仁)」在句首位置；若否，則加一份「人名 (梅友仁)」在句首位置。
                    nameBOOL = articut.parse(entrySTR)["result_pos"][0].startswith(f"<ENTITY_person>{entrySTR}")
                except Exception as e:
                    print(f"lv2 Error at {d} with {e}")

                #逐句檢查該句是否有動詞：若有，加入 utteranceDICT；若無，加個「是 (AUX)」給它。
                verbLIST = articut.getVerbStemLIST(lv2ResultDICT)
                for sent_idx in range(0, len(verbLIST)):
                    if len(lv2ResultDICT["result_pos"][sent_idx]) > 1:
                        snt = purgePat.sub("", lv2ResultDICT["result_pos"][sent_idx])
                        if not verbLIST[sent_idx]:
                            if snt[0] in "號字筆卒原祖又一": #避開古人特有的「字某某、號某某、筆名某某」的資訊；這個之後手動建一下就好了。
                                pass
                            elif snt[-1] in "等":
                                pass
                            elif snt == entrySTR:  #避開「王小明是王小明」
                                pass
                            elif lv2ResultDICT["result_pos"][sent_idx].startswith("<ENTITY_num>")  and lv2ResultDICT["result_pos"][sent_idx].endswith("</ENTITY_num>"):
                                pass
                            elif lv2ResultDICT["result_pos"][sent_idx].startswith("<LOCATION>"):
                                utteranceDICT["BeV"].append("{}是{}".format(entrySTR, snt))
                                if nameBOOL:
                                    utteranceDICT["BeV"].append("{}是{}".format("梅仁", snt))
                                else:
                                    userdefinedDICT["_entryName"].append(entrySTR)
                                    utteranceDICT["BeV"].append("{}是{}".format("梅友仁", snt))
                            else:
                                utteranceDICT["BeV"].append("{}是{}".format(entrySTR, snt))
                                if nameBOOL:
                                    utteranceDICT["BeV"].append("{}是{}".format("梅仁", snt))
                                else:
                                    userdefinedDICT["_entryName"].append(entrySTR)
                                    utteranceDICT["BeV"].append("{}是{}".format("梅友仁", snt))
                        else:
                            try:
                                lv3ResultDICT = articut.parse(verbLIST[sent_idx][0][-1], level="lv3", pinyin="HANYU")
                            except Exception as e:
                                print(f"lv3 Error at {d} with {e}")
                            if lv3ResultDICT["status"]:
                                intentSTR = lv3ResultDICT["utterance"][0].replace(" ", "")
                                if intentSTR not in utteranceDICT:
                                    utteranceDICT[intentSTR] = []
                                utteranceDICT[intentSTR].append("{}{}".format(entrySTR, snt))
                                if nameBOOL:
                                    utteranceDICT[intentSTR].append("{}{}".format("梅仁", snt))
                                else:
                                    userdefinedDICT["_entryName"].append(entrySTR)
                                    utteranceDICT[intentSTR].append("{}{}".format("梅友仁", snt))
                            else:
                                print(f"lv3 Pinyin Error with {d}")
                updateResult = _updateUserDefined(accountDICT, projectSTR=projectSTR, userdefinedDICT=userdefinedDICT)
                print(utteranceDICT)
                for k in utteranceDICT:
                    insertResult = insertLokiUtterance(accountDICT, projectSTR=projectSTR, intentSTR=k, utteranceLIST=utteranceDICT[k])
                    print(insertResult)