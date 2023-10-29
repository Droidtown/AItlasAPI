#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Loki 4.0 Template For Python3

    [URL] https://api.droidtown.co/Loki/BulkAPI/

    Request:
        {
            "username": "your_username",
            "input_list": ["your_input_1", "your_input_2"],
            "loki_key": "your_loki_key",
            "filter_list": ["intent_filter_list"] # optional
        }

    Response:
        {
            "status": True,
            "msg": "Success!",
            "version": "v223",
            "word_count_balance": 2000,
            "result_list": [
                {
                    "status": True,
                    "msg": "Success!",
                    "results": [
                        {
                            "intent": "intentName",
                            "pattern": "matchPattern",
                            "utterance": "matchUtterance",
                            "argument": ["arg1", "arg2", ... "argN"]
                        },
                        ...
                    ]
                },
                {
                    "status": False,
                    "msg": "No matching Intent."
                }
            ]
        }
"""

from requests import post
from requests import codes
import json
import math
import os
import re
try:
    from intent import Loki_dai4byao3_4e
    from intent import Loki_dai4byao3_3e
    from intent import Loki_dai4byao3_5e
    from intent import Loki_dai4byao3_2e
    from intent import Loki_dai4byao3_6e
    from intent import Loki_dai4byao3_7e
    from intent import Loki_dai4byao3_1e
except:
    from .intent import Loki_dai4byao3_4e
    from .intent import Loki_dai4byao3_3e
    from .intent import Loki_dai4byao3_5e
    from .intent import Loki_dai4byao3_2e
    from .intent import Loki_dai4byao3_6e
    from .intent import Loki_dai4byao3_7e
    from .intent import Loki_dai4byao3_1e


LOKI_URL = "https://api.droidtown.co/Loki/BulkAPI/"
try:
    accountInfo = json.load(open(os.path.join(os.path.dirname(__file__), "account.info"), encoding="utf-8"))
    USERNAME = accountInfo["username"]
    LOKI_KEY = accountInfo["loki_key"]
except Exception as e:
    print("[ERROR] AccountInfo => {}".format(str(e)))
    USERNAME = ""
    LOKI_KEY = ""

# 意圖過濾器說明
# INTENT_FILTER = []        => 比對全部的意圖 (預設)
# INTENT_FILTER = [intentN] => 僅比對 INTENT_FILTER 內的意圖
INTENT_FILTER = []
INPUT_LIMIT = 20

class LokiResult():
    status = False
    message = ""
    version = ""
    balance = -1
    lokiResultLIST = []

    def __init__(self, inputLIST, filterLIST):
        self.status = False
        self.message = ""
        self.version = ""
        self.balance = -1
        self.lokiResultLIST = []
        # filterLIST 空的就採用預設的 INTENT_FILTER
        if filterLIST == []:
            filterLIST = INTENT_FILTER

        try:
            result = post(LOKI_URL, json={
                "username": USERNAME,
                "input_list": inputLIST,
                "loki_key": LOKI_KEY,
                "filter_list": filterLIST
            })

            if result.status_code == codes.ok:
                result = result.json()
                self.status = result["status"]
                self.message = result["msg"]
                if result["status"]:
                    self.version = result["version"]
                    if "word_count_balance" in result:
                        self.balance = result["word_count_balance"]
                    self.lokiResultLIST = result["result_list"]
            else:
                self.message = "{} Connection failed.".format(result.status_code)
        except Exception as e:
            self.message = str(e)

    def getStatus(self):
        return self.status

    def getMessage(self):
        return self.message

    def getVersion(self):
        return self.version

    def getBalance(self):
        return self.balance

    def getLokiStatus(self, index):
        rst = False
        if index < len(self.lokiResultLIST):
            rst = self.lokiResultLIST[index]["status"]
        return rst

    def getLokiMessage(self, index):
        rst = ""
        if index < len(self.lokiResultLIST):
            rst = self.lokiResultLIST[index]["msg"]
        return rst

    def getLokiLen(self, index):
        rst = 0
        if index < len(self.lokiResultLIST):
            if self.lokiResultLIST[index]["status"]:
                rst = len(self.lokiResultLIST[index]["results"])
        return rst

    def getLokiResult(self, index, resultIndex):
        lokiResultDICT = None
        if resultIndex < self.getLokiLen(index):
            lokiResultDICT = self.lokiResultLIST[index]["results"][resultIndex]
        return lokiResultDICT

    def getIntent(self, index, resultIndex):
        rst = ""
        lokiResultDICT = self.getLokiResult(index, resultIndex)
        if lokiResultDICT:
            rst = lokiResultDICT["intent"]
        return rst

    def getPattern(self, index, resultIndex):
        rst = ""
        lokiResultDICT = self.getLokiResult(index, resultIndex)
        if lokiResultDICT:
            rst = lokiResultDICT["pattern"]
        return rst

    def getUtterance(self, index, resultIndex):
        rst = ""
        lokiResultDICT = self.getLokiResult(index, resultIndex)
        if lokiResultDICT:
            rst = lokiResultDICT["utterance"]
        return rst

    def getArgs(self, index, resultIndex):
        rst = []
        lokiResultDICT = self.getLokiResult(index, resultIndex)
        if lokiResultDICT:
            rst = lokiResultDICT["argument"]
        return rst

def runLoki(inputLIST, filterLIST=[], refDICT={}):
    resultDICT = refDICT
    lokiRst = LokiResult(inputLIST, filterLIST)
    if lokiRst.getStatus():
        for index, key in enumerate(inputLIST):
            lokiResultDICT = {}
            for resultIndex in range(0, lokiRst.getLokiLen(index)):
                # dai4byao3_4e
                if lokiRst.getIntent(index, resultIndex) == "dai4byao3_4e":
                    lokiResultDICT = Loki_dai4byao3_4e.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), lokiResultDICT, refDICT)

                # dai4byao3_3e
                if lokiRst.getIntent(index, resultIndex) == "dai4byao3_3e":
                    lokiResultDICT = Loki_dai4byao3_3e.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), lokiResultDICT, refDICT)

                # dai4byao3_5e
                if lokiRst.getIntent(index, resultIndex) == "dai4byao3_5e":
                    lokiResultDICT = Loki_dai4byao3_5e.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), lokiResultDICT, refDICT)

                # dai4byao3_2e
                if lokiRst.getIntent(index, resultIndex) == "dai4byao3_2e":
                    lokiResultDICT = Loki_dai4byao3_2e.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), lokiResultDICT, refDICT)

                # dai4byao3_6e
                if lokiRst.getIntent(index, resultIndex) == "dai4byao3_6e":
                    lokiResultDICT = Loki_dai4byao3_6e.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), lokiResultDICT, refDICT)

                # dai4byao3_7e
                if lokiRst.getIntent(index, resultIndex) == "dai4byao3_7e":
                    lokiResultDICT = Loki_dai4byao3_7e.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), lokiResultDICT, refDICT)

                # dai4byao3_1e
                if lokiRst.getIntent(index, resultIndex) == "dai4byao3_1e":
                    lokiResultDICT = Loki_dai4byao3_1e.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), lokiResultDICT, refDICT)

            # save lokiResultDICT to resultDICT
            for k in lokiResultDICT:
                if k not in resultDICT:
                    resultDICT[k] = []
                if type(resultDICT[k]) != list:
                    resultDICT[k] = [resultDICT[k]] if resultDICT[k] else []
                if type(lokiResultDICT[k]) == list:
                    resultDICT[k].extend(lokiResultDICT[k])
                else:
                    resultDICT[k].append(lokiResultDICT[k])
    else:
        resultDICT["msg"] = lokiRst.getMessage()
    return resultDICT

def execLoki(content, filterLIST=[], splitLIST=[], refDICT={}):
    """
    input
        content       STR / STR[]    要執行 loki 分析的內容 (可以是字串或字串列表)
        filterLIST    STR[]          指定要比對的意圖 (空列表代表不指定)
        splitLIST     STR[]          指定要斷句的符號 (空列表代表不指定)
                                     * 如果一句 content 內包含同一意圖的多個 utterance，請使用 splitLIST 切割 content
        refDICT       DICT           參考內容

    output
        resultDICT    DICT           合併 runLoki() 的結果

    e.g.
        splitLIST = ["！", "，", "。", "？", "!", ",", "\n", "；", "\u3000", ";"]
        resultDICT = execLoki("今天天氣如何？後天氣象如何？")                      # output => ["今天天氣"]
        resultDICT = execLoki("今天天氣如何？後天氣象如何？", splitLIST=splitLIST) # output => ["今天天氣", "後天氣象"]
        resultDICT = execLoki(["今天天氣如何？", "後天氣象如何？"])                # output => ["今天天氣", "後天氣象"]
    """
    resultDICT = refDICT
    if resultDICT is None:
        resultDICT = {}

    contentLIST = []
    if type(content) == str:
        contentLIST = [content]
    if type(content) == list:
        contentLIST = content

    if contentLIST:
        if splitLIST:
            # 依 splitLIST 做分句切割
            splitPAT = re.compile("[{}]".format("".join(splitLIST)))
            inputLIST = []
            for c in contentLIST:
                tmpLIST = splitPAT.split(c)
                inputLIST.extend(tmpLIST)
            # 去除空字串
            while "" in inputLIST:
                inputLIST.remove("")
        else:
            # 不做分句切割處理
            inputLIST = contentLIST

        # 依 INPUT_LIMIT 限制批次處理
        for i in range(0, math.ceil(len(inputLIST) / INPUT_LIMIT)):
            resultDICT = runLoki(inputLIST[i*INPUT_LIMIT:(i+1)*INPUT_LIMIT], filterLIST=filterLIST, refDICT=refDICT)
            if "msg" in resultDICT:
                break

    return resultDICT

def testLoki(inputLIST, filterLIST):
    INPUT_LIMIT = 20
    for i in range(0, math.ceil(len(inputLIST) / INPUT_LIMIT)):
        resultDICT = runLoki(inputLIST[i*INPUT_LIMIT:(i+1)*INPUT_LIMIT], filterLIST)

    if "msg" in resultDICT:
        print(resultDICT["msg"])

def testIntent():
    # dai4byao3_4e
    print("[TEST] dai4byao3_4e")
    inputLIST = ['代表日本參加1990年亞洲運動會自行車比賽','代表義大利參加國際雪車聯合會世界錦標賽','代表克羅埃西亞國家隊參加1998年國際足總世界盃','代表德國參加1912年夏季奧林匹克運動會賽艇比賽','代表德國參加1952年夏季奧林匹克運動會馬術比賽','代表西德參加1988年夏季奧林匹克運動會擊劍比賽','代表古巴參加2000年和2004年夏季奧林匹克運動會拳擊比賽','代表東德參加1976年和1980年夏季奧林匹克運動會游泳比賽','代表澳大利亞參加2006年和2010年大英國協運動會跳水比賽','代表瑞典參加1980年和1984年夏季奧林匹克運動會游泳比賽','代表芬蘭參加2010年和2022年冬季奧林匹克運動會冰球比賽']
    testLoki(inputLIST, ['dai4byao3_4e'])
    print("")

    # dai4byao3_3e
    print("[TEST] dai4byao3_3e")
    inputLIST = ['代表大會吉林地區代表','代表芬蘭參加世界摔跤錦標賽','代表大會第一次會議在北京召開','代表中華人民共和國參加射擊國際間團隊比賽','代表大會常務委員會第二十九次會議於1997年12月29日通過']
    testLoki(inputLIST, ['dai4byao3_3e'])
    print("")

    # dai4byao3_5e
    print("[TEST] dai4byao3_5e")
    inputLIST = ['代表母性與豐饒的女神之間相互關聯','代表紐西蘭國家隊參加1998年大英國協運動會板球比賽','代表葡萄牙參加2004年夏季奧林匹克運動會自行車比賽','代表瑞典國家隊參加1936年冬季奧林匹克運動會冰球比賽','代表芬蘭國家隊參加1980年冬季奧林匹克運動會冰球比賽','代表匈牙利國家隊參加2016年夏季奧林匹克運動會水球比賽','代表義大利國奧隊參加1924年夏季奧林匹克運動會足球比賽','代表義大利國家隊參加1948年夏季奧林匹克運動會水球比賽','代表法國參加1980年和1984年冬季奧林匹克運動會高山滑雪比賽','代表西班牙參加1992年和1996年夏季奧林匹克運動會曲棍球比賽','代表奧地利參加1964年和1968年冬季奧林匹克運動會高山滑雪比賽','代表奧地利參加2014年和2018年冬季奧林匹克運動會北歐兩項比賽','代表捷克斯洛伐克國家隊參加1992年冬季奧林匹克運動會冰球比賽']
    testLoki(inputLIST, ['dai4byao3_5e'])
    print("")

    # dai4byao3_2e
    print("[TEST] dai4byao3_2e")
    inputLIST = ['代表大會常務委員會通過']
    testLoki(inputLIST, ['dai4byao3_2e'])
    print("")

    # dai4byao3_6e
    print("[TEST] dai4byao3_6e")
    inputLIST = ['代表中華人民共和國參加桌球國際間團體比賽的體育之隊']
    testLoki(inputLIST, ['dai4byao3_6e'])
    print("")

    # dai4byao3_7e
    print("[TEST] dai4byao3_7e")
    inputLIST = ['代表羅馬尼亞國家隊參加1994年國際足總世界盃和1996年歐洲足球錦標賽']
    testLoki(inputLIST, ['dai4byao3_7e'])
    print("")

    # dai4byao3_1e
    print("[TEST] dai4byao3_1e")
    inputLIST = ['代表東德','代表機構','代表母性','代表阿根廷','代表大會授權','代表之作Historism','代表德國參加1992年','代表瑞典參加1980年','代表芬蘭參加1976年','代表義大利參加2004年']
    testLoki(inputLIST, ['dai4byao3_1e'])
    print("")


if __name__ == "__main__":
    # 測試所有意圖
    testIntent()

    # 測試其它句子
    filterLIST = []
    splitLIST = ["！", "，", "。", "？", "!", ",", "\n", "；", "\u3000", ";"]
    # 設定參考資料
    refDICT = {
        #"key": []
    }
    #resultDICT = execLoki("今天天氣如何？後天氣象如何？", filterLIST=filterLIST, refDICT=refDICT)                      # output => {"key": ["今天天氣"]}
    #resultDICT = execLoki("今天天氣如何？後天氣象如何？", filterLIST=filterLIST, splitLIST=splitLIST, refDICT=refDICT) # output => {"key": ["今天天氣", "後天氣象"]}
    #resultDICT = execLoki(["今天天氣如何？", "後天氣象如何？"], filterLIST=filterLIST, refDICT=refDICT)                # output => {"key": ["今天天氣", "後天氣象"]}