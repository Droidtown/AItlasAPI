#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from ArticutAPI import Articut
from requests import post

import os
import re
purgePat = re.compile("</?[a-zA-Z]+(_[a-zA-Z]+)?>")
washPat = re.compile("\(\)|《.+?》")

import unidecode

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
    projectSTR = "AItlas_wiki_people2" #"AItlas_wiki_people_EN"
    dataDIR = "../data/local_data/"

    for d in os.listdir(dataDIR):
        #filter out directories without EN suffix
        if not d.contains("EN"):
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

                            #reference:
                            #https://www.kalzumeus.com/2010/06/17/falsehoods-programmers-believe-about-names/

                            #pass all EN names with numbers or non alphabet chars
                            #make exceptions for names like Francis St. Paul, Armstrong-Jones, O'Hara

                            if not snt[0].isalpha():
                                special_chars = ["-", "\'", "."]
                                if any(c in snt[0] for c in special_chars)
                                    break
                                else:
                                    pass

                            #pass any strings with accented chars
                            #check if original str is different from decoded str
                            elif unidecode(snt[0]) != snt[0]:
                                pass
                                
                            #make assumption that all caps cannot be real EN name
                            elif snt[0].isupper():
                                pass

                            #pass all sentences ending in ...
                            elif snt[-1] in "...":
                                pass

                            #pass sentence "John is John"
                            elif snt == entrySTR:  #避開「王小明是王小明」
                                pass

                            elif lv2ResultDICT["result_pos"][sent_idx].startswith("<ENTITY_num>")  and lv2ResultDICT["result_pos"][sent_idx].endswith("</ENTITY_num>"):
                                pass

                            #use John Doe and append to sentences with names
                            #use abcde for objects?
                            elif lv2ResultDICT["result_pos"][sent_idx].startswith("<LOCATION>"):
                                utteranceDICT["BeV"].append("{}is{}".format(entrySTR, snt))
                                if nameBOOL:
                                    utteranceDICT["BeV"].append("{}is{}".format("abcde", snt))
                                else:
                                    userdefinedDICT["_entryName"].append(entrySTR)
                                    utteranceDICT["BeV"].append("{}is{}".format("John Doe", snt))
                            else:
                                utteranceDICT["BeV"].append("{}is{}".format(entrySTR, snt))
                                if nameBOOL:
                                    utteranceDICT["BeV"].append("{}is{}".format("abcde", snt))
                                else:
                                    userdefinedDICT["_entryName"].append(entrySTR)
                                    utteranceDICT["BeV"].append("{}is{}".format("John Doe", snt))
                        else:
                            try:
                                EN_ResultDICT = articut.parse(verbLIST[sent_idx][0][-1])
                            except Exception as e:
                                print(f"Error at {d} with {e}")
                            if EN_ResultDICT["status"]:
                                #will need to modify this line, so as to take the first verb of sentence
                                intentSTR = EN_ResultDICT["utterance"][0].replace(" ", "")
                                if intentSTR not in utteranceDICT:
                                    utteranceDICT[intentSTR] = []
                                utteranceDICT[intentSTR].append("{}{}".format(entrySTR, snt))
                                if nameBOOL:
                                    utteranceDICT[intentSTR].append("{}{}".format("abcde", snt))
                                else:
                                    userdefinedDICT["_entryName"].append(entrySTR)
                                    utteranceDICT[intentSTR].append("{}{}".format("John Doe", snt))
                            else:
                                print(f"EN error with {d}")

                updateResult = _updateUserDefined(accountDICT, projectSTR=projectSTR, userdefinedDICT=userdefinedDICT)
                print(utteranceDICT)
                for k in utteranceDICT:
                    insertResult = insertLokiUtterance(accountDICT, projectSTR=projectSTR, intentSTR=k, utteranceLIST=utteranceDICT[k])
                    print(insertResult)