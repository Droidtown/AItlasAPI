#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from ArticutAPI import Articut
import json
import os
import re
from requests import post

projectName = "AItlas_Wiki_Demo"
targetVerb = "代表"
purgePat = re.compile("</?[a-zA-Z]+(_[a-zA-Z]+)?>")

countLIST = ["KNOWLEDGE_", "ENTITY_noun", "ENTITY_oov", "ENTITY_person", "LOCATION", "UserDefined"]

with open("./account.info", encoding="utf-8") as f:
    accountDICT = json.load(f)

articut = Articut(username=accountDICT["username"], apikey=accountDICT["apikey"])

def verbEntityChoper(inputLIST, targetVerb, purgePat):
    resultDICT = {}
    for i  in inputLIST:
        articutResultDICT = articut.parse(i)
        verbLIST = articut.getVerbStemLIST(articutResultDICT)
        for v in verbLIST[0]:
            if v[-1] == targetVerb:
                entityNum = 0
                for e in countLIST:
                    entityNum = entityNum + int((articutResultDICT["result_pos"][0][v[0]:].count(e))/2)
                    if entityNum == 0:
                        pass
                    elif entityNum in resultDICT:
                        pass
                    else:
                        resultDICT[entityNum] = []
                if entityNum == 0:
                    pass
                else:
                    resultDICT[entityNum].append(re.sub(purgePat, "", articutResultDICT["result_pos"][0][v[0]:]))
    for k in resultDICT.keys():
        resultDICT[k] = list(set(resultDICT[k]))
    return resultDICT

def createIntent(username, loki_key, targetVerb, entityNum):
    global projectName
    intentName = "".join(articut.parse(targetVerb, level="lv3", pinyin="HANYU")["utterance"][0]).replace(" ", "")

    url = "https://api.droidtown.co/Loki/Call/"
    payload = {
        "username" : username,
        "loki_key" : loki_key,
        "project": projectName,
        "intent": intentName + "_{}e".format(entityNum),
        "func": "create_intent",
        "data": {
            "type": "basic" #意圖類別
        }
    }

    response = post(url, json=payload).json()
    return (intentName, response)

def insertUtterance(username, loki_key, targetVerb, utterance2AddDICT):
    global projectName
    intentName = "".join(articut.parse(targetVerb, level="lv3", pinyin="HANYU")["utterance"][0]).replace(" ", "")

    url = "https://api.droidtown.co/Loki/Call/"
    batchSize = 20
    response = None
    for k in utterance2AddDICT.keys():
        createIntent(accountDICT["username"], accountDICT["loki_key"], targetVerb, k)
        for i in range(0, len(utterance2AddDICT[k]), batchSize):
            print(utterance2AddDICT[k][i:i+batchSize])
            payload = {
                "username" : username,
                "loki_key" : loki_key,
                "project": projectName,
                "intent": intentName+"_{}e".format(k),
                "func": "insert_utterance",
                "data": {
                    "utterance": utterance2AddDICT[k][i:i+batchSize],
                    "checked_list": ["LOCATION", "ENTITY_noun"]
                }
            }
            response = post(url, json=payload).json()
    return response


if __name__ == "__main__":

    cadidateLIST = []
    for dir_s in os.listdir("../People_Source")[:100]:
        if dir_s == ".DS_Store":
            os.remove(dir_s)
        elif dir_s.startswith("."):
            os.rmdir(dir_s)
        else:
            for j_file in os.listdir("../People_Source/{}".format(dir_s)):
                if j_file.startswith("."):
                    os.remove("../People_Source/{}/{}".format(dir_s, j_file))
                else:
                    with open("../People_Source/{}/{}".format(dir_s, j_file), encoding="utf-8") as f:
                        wikiDICT = json.load(f)
                    if targetVerb in wikiDICT["abstract"]:
                        print("Found targetVerb {} in file {}".format(targetVerb, j_file))
                        resultDICT = articut.parse(wikiDICT["abstract"])
                        for s in resultDICT["result_pos"]:
                            if len(s) == 1:
                                pass
                            elif "<ACTION_verb>{}</ACTION_verb>".format(targetVerb) in s:
                                cadidateLIST.append(re.sub(purgePat, "", s))


    print("建立意圖..", cadidateLIST)
    utterance2AddDICT = verbEntityChoper(cadidateLIST, targetVerb, purgePat)
    print(utterance2AddDICT)

    utteranceInsertResult = insertUtterance(accountDICT["username"], accountDICT["loki_key"], targetVerb, utterance2AddDICT)
    print("新增語句...", utteranceInsertResult)
