#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Loki module for dai4byao3_5e

    Input:
        inputSTR      str,
        utterance     str,
        args          str[],
        resultDICT    dict,
        refDICT       dict

    Output:
        resultDICT    dict
"""

from random import sample
import json
import os

DEBUG_dai4byao3_5e = True
CHATBOT_MODE = False

userDefinedDICT = {}
try:
    userDefinedDICT = json.load(open(os.path.join(os.path.dirname(__file__), "USER_DEFINED.json"), encoding="utf-8"))
except Exception as e:
    print("[ERROR] userDefinedDICT => {}".format(str(e)))

responseDICT = {}
if CHATBOT_MODE:
    try:
        responseDICT = json.load(open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "reply/reply_dai4byao3_5e.json"), encoding="utf-8"))
    except Exception as e:
        print("[ERROR] responseDICT => {}".format(str(e)))

# 將符合句型的參數列表印出。這是 debug 或是開發用的。
def debugInfo(inputSTR, utterance):
    if DEBUG_dai4byao3_5e:
        print("[dai4byao3_5e] {} ===> {}".format(inputSTR, utterance))

def getResponse(utterance, args):
    resultSTR = ""
    if utterance in responseDICT:
        if len(responseDICT[utterance]):
            resultSTR = sample(responseDICT[utterance], 1)[0].format(*args)

    return resultSTR

def getResult(inputSTR, utterance, args, resultDICT, refDICT):
    debugInfo(inputSTR, utterance)
    if utterance == "代表匈牙利國家隊參加[2016年夏季]奧林匹克運動[會]水球比賽":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
        else:
            # write your code here
            pass

    if utterance == "代表奧地利參加[1964年]和[1968年冬季]奧林匹克運動[會]高山滑雪比賽":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
        else:
            # write your code here
            pass

    if utterance == "代表奧地利參加[2014年]和[2018年冬季]奧林匹克運動[會]北歐[兩項]比賽":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
        else:
            # write your code here
            pass

    if utterance == "代表捷克斯洛伐克國家隊參加[1992年冬季]奧林匹克運動[會]冰球比賽":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
        else:
            # write your code here
            pass

    if utterance == "代表母[性]與豐饒的女神之間[相互]關聯":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
        else:
            # write your code here
            pass

    if utterance == "代表法國參加[1980年]和[1984年冬季]奧林匹克運動[會]高山滑雪比賽":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
        else:
            # write your code here
            pass

    if utterance == "代表瑞典國家隊參加[1936年冬季]奧林匹克運動[會]冰球比賽":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
        else:
            # write your code here
            pass

    if utterance == "代表紐西蘭國家隊參加[1998年][大]英國協運動[會]板球比賽":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
        else:
            # write your code here
            pass

    if utterance == "代表義大利國奧隊參加[1924年夏季]奧林匹克運動[會]足球比賽":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
        else:
            # write your code here
            pass

    if utterance == "代表義大利國家隊參加[1948年夏季]奧林匹克運動[會]水球比賽":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
        else:
            # write your code here
            pass

    if utterance == "代表芬蘭國家隊參加[1980年冬季]奧林匹克運動[會]冰球比賽":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
        else:
            # write your code here
            pass

    if utterance == "代表葡萄牙參加[2004年夏季]奧林匹克運動[會]自行車比賽":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
        else:
            # write your code here
            pass

    if utterance == "代表西班牙參加[1992年]和[1996年夏季]奧林匹克運動[會]曲棍球比賽":
        if CHATBOT_MODE:
            resultDICT["response"] = getResponse(utterance, args)
        else:
            # write your code here
            pass

    return resultDICT