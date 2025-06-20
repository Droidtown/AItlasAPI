#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Loki 3.0 Template For Python3

    [URL] https://nlu.droidtown.co/Loki/BulkAPI/

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
                    "msg": "No Match Intent!"
                }
            ]
        }
"""

from requests import post
from requests import codes
import math
try:
    from intent import Loki_Person_Be
    from intent import Loki_Person
except:
    from .intent import Loki_Person_Be
    from .intent import Loki_Person


LOKI_URL = "https://nlu.droidtown.co/Loki/BulkAPI/"
USERNAME = ""
LOKI_KEY = ""
# Filter descrption
# INTENT_FILTER = []        => All intents (Default)
# INTENT_FILTER = [intentN] => Only use intent of INTENT_FILTER
INTENT_FILTER = []
INPUT_LIMIT = 20

class LokiResult():
    status = False
    message = ""
    version = ""
    lokiResultLIST = []

    def __init__(self, inputLIST, filterLIST):
        self.status = False
        self.message = ""
        self.version = ""
        self.lokiResultLIST = []
        # Default: INTENT_FILTER
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

def runLoki(inputLIST, filterLIST=[]):
    # set intent as key to empty list
    resultDICT = {
        #"key": []
    }
    lokiRst = LokiResult(inputLIST, filterLIST)
    if lokiRst.getStatus():
        for index, key in enumerate(inputLIST):
            for resultIndex in range(0, lokiRst.getLokiLen(index)):
                # Person_Be
                if lokiRst.getIntent(index, resultIndex) == "Person_Be":
                    resultDICT = Loki_Person_Be.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), resultDICT)

                # Person
                if lokiRst.getIntent(index, resultIndex) == "Person":
                    resultDICT = Loki_Person.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), resultDICT)

    else:
        resultDICT = {"msg": lokiRst.getMessage()}
    return resultDICT

def execLoki(content, filterLIST=[], splitLIST=[]):
    """
    input
        content       STR / STR[]    要執行 loki 分析的內容 (string or string list)
        filterLIST    STR[]          specific intents (empty: all intent)
        splitLIST     STR[]          split by symbols (empty: don't split)
                                     * using splitLIST if the content includes multiple utterances with an intent

    output
        resultDICT    DICT           merge results of runLoki(), remeber to set default to resultDICT

    e.g.
        splitLIST = ["!", ",", ".", "
", "　", ";"]
        resultDICT = execLoki("How is the weather today? How is the weather tomorrow?")                      # output => ["weather today"]
        resultDICT = execLoki("How is the weather today? How is the weather tomorrow?", splitLIST=splitLIST) # output => ["weather today", "weather tomorrow"]
        resultDICT = execLoki(["How is the weather today?", "How is the weather tomorrow?"])                 # output => ["weather today", "weather tomorrow"]
    """
    contentLIST = []
    if type(content) == str:
        contentLIST = [content]
    if type(content) == list:
        contentLIST = content

    resultDICT = {}
    if contentLIST:
        if splitLIST:
            # split by splitLIST
            splitPAT = re.compile("[{}]".format("".join(splitLIST)))
            inputLIST = []
            for c in contentLIST:
                tmpLIST = splitPAT.split(c)
                inputLIST.extend(tmpLIST)
            # remove empty
            while "" in inputLIST:
                inputLIST.remove("")
        else:
            # don't split
            inputLIST = contentLIST

        # batch with limitation of INPUT_LIMIT
        for i in range(0, math.ceil(len(inputLIST) / INPUT_LIMIT)):
            lokiResultDICT = runLoki(inputLIST[i*INPUT_LIMIT:(i+1)*INPUT_LIMIT], filterLIST)
            if "msg" in lokiResultDICT:
                return lokiResultDICT

            # save lokiResultDICT to resultDICT
            for k in lokiResultDICT:
                if k not in resultDICT:
                    resultDICT[k] = []
                resultDICT[k].extend(lokiResultDICT[k])

    return resultDICT

def testLoki(inputLIST, filterLIST):
    INPUT_LIMIT = 20
    for i in range(0, math.ceil(len(inputLIST) / INPUT_LIMIT)):
        resultDICT = runLoki(inputLIST[i*INPUT_LIMIT:(i+1)*INPUT_LIMIT], filterLIST)

    if "msg" in resultDICT:
        print(resultDICT["msg"])

def testIntent():
    # Person_Be
    print("[TEST] Person_Be")
    inputLIST = ["""Batman is a superhero""","""Augustus was the first Roman emperor""","""Aphrodite is an ancient Greek goddess""","""Augusta Ada King be Countess of Lovelace""","""Alfred Hitchcock was an English filmmaker""","""Ashoka was the third emperor of the Maurya Empire""","""Albert Einstein was a German-born theoretical physicist""","""Amelia Mary Earhart was an American aviation pioneer and writer""","""Alexander Hamilton was a Nevisian-born American military officer""","""Alexander III of Macedon was a king of the ancient Greek kingdom of Macedon""","""Albert Camus was an Algerian-born French philosopher, author, dramatist, and journalist""","""Aung San Suu Kyi is a Burmese politician, diplomat, author, and a 1991 Nobel Peace Prize laureate"""]
    testLoki(inputLIST, ['Person_Be'])
    print("")

    # Person
    print("[TEST] Person")
    inputLIST = ["""Augusta Ada King be Countess of Lovelace"""]
    testLoki(inputLIST, ['Person'])
    print("")


if __name__ == "__main__":
    # Test all intents
    testIntent()

    # Test other
    filterLIST = []
    splitLIST = ["!", ",", ".", "
", "　", ";"]
    resultDICT = execLoki("How is the weather today? How is the weather tomorrow?")                      # output => ["weather today"]
    resultDICT = execLoki("How is the weather today? How is the weather tomorrow?", splitLIST=splitLIST) # output => ["weather today", "weather tomorrow"]
    resultDICT = execLoki(["How is the weather today?", "How is the weather tomorrow?"])                 # output => ["weather today", "weather tomorrow"]