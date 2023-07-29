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

with open("./account.info", encoding="utf-8") as f:
    accountDICT = json.load(f)

articut = Articut(username=accountDICT["username"], apikey=accountDICT["apikey"])

def verbEntityChoper(inputLIST, targetVerb, purgePat):
    resultLIST = []
    for i  in inputLIST:
        resultDICT = articut.parse(i)
        verbLIST = articut.getVerbStemLIST(resultDICT)
        for v in verbLIST[0]:
            if v[-1] == targetVerb:
                resultLIST.append(re.sub(purgePat, "", resultDICT["result_pos"][0][v[0]:]))
    resultLIST = list(set(resultLIST)-set([targetVerb]))
    return resultLIST

def createIntent(username, loki_key, targetVerb):
    global projectName
    intentName = "".join(articut.parse(targetVerb, level="lv3", pinyin="HANYU")["utterance"][0]).replace(" ", "")

    url = "https://api.droidtown.co/Loki/Call/"
    payload = {
        "username" : username,
        "loki_key" : loki_key,
        "project": projectName,
        "intent": intentName,
        "func": "create_intent",
        "data": {
            "type": "basic" #意圖類別
        }
    }

    response = post(url, json=payload).json()
    return (intentName, response)


def insertUtterance(username, loki_key, targetVerb, utterance2AddLIST):
    global projectName
    intentName = "".join(articut.parse(targetVerb, level="lv3", pinyin="HANYU")["utterance"][0]).replace(" ", "")

    url = "https://api.droidtown.co/Loki/Call/"
    payload = {
        "username" : username,
        "loki_key" : loki_key,
        "project": projectName,
        "intent": intentName,
        "func": "insert_utterance",
        "data": {
            "utterance": utterance2AddLIST,
            "checked_list": []
        }
    }

    response = post(url, json=payload).json()
    return response


if __name__ == "__main__":
    intentCreateResult = createIntent(accountDICT["username"], accountDICT["loki_key"], targetVerb)
    print(intentCreateResult)

    cadidateLIST = []
    for dir_s in os.listdir("../People_Source")[:10]:
        if dir_s.startswith("."):
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
    utterance2AddLIST = verbEntityChoper(cadidateLIST, targetVerb, purgePat)
    print(utterance2AddLIST)

    utteranceInsertResult = insertUtterance(accountDICT["username"], accountDICT["loki_key"], targetVerb, utterance2AddLIST)
    print("新增語句...", utteranceInsertResult)
