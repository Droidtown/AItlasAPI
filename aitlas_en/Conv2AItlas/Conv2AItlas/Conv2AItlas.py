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
    from intent import Loki_Person_Direct
    from intent import Loki_Person_Develop
    from intent import Loki_Person_Became
    from intent import Loki_Person_Credit
    from intent import Loki_Person_Set
    from intent import Loki_Person
    from intent import Loki_Person_Reform
    from intent import Loki_Person_Establish
    from intent import Loki_Person_Lead
    from intent import Loki_Person_Publish
    from intent import Loki_Person_Produce
    from intent import Loki_Person_Wrote
    from intent import Loki_Person_Make
    from intent import Loki_Person_Receive
    from intent import Loki_Person_Secure
    from intent import Loki_Person_Order
    from intent import Loki_Person_Create
except:
    from .intent import Loki_Person_Be
    from .intent import Loki_Person_Direct
    from .intent import Loki_Person_Develop
    from .intent import Loki_Person_Became
    from .intent import Loki_Person_Credit
    from .intent import Loki_Person_Set
    from .intent import Loki_Person
    from .intent import Loki_Person_Reform
    from .intent import Loki_Person_Establish
    from .intent import Loki_Person_Lead
    from .intent import Loki_Person_Publish
    from .intent import Loki_Person_Produce
    from .intent import Loki_Person_Wrote
    from .intent import Loki_Person_Make
    from .intent import Loki_Person_Receive
    from .intent import Loki_Person_Secure
    from .intent import Loki_Person_Order
    from .intent import Loki_Person_Create


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

                # Person_Direct
                if lokiRst.getIntent(index, resultIndex) == "Person_Direct":
                    resultDICT = Loki_Person_Direct.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), resultDICT)

                # Person_Develop
                if lokiRst.getIntent(index, resultIndex) == "Person_Develop":
                    resultDICT = Loki_Person_Develop.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), resultDICT)

                # Person_Became
                if lokiRst.getIntent(index, resultIndex) == "Person_Became":
                    resultDICT = Loki_Person_Became.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), resultDICT)

                # Person_Credit
                if lokiRst.getIntent(index, resultIndex) == "Person_Credit":
                    resultDICT = Loki_Person_Credit.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), resultDICT)

                # Person_Set
                if lokiRst.getIntent(index, resultIndex) == "Person_Set":
                    resultDICT = Loki_Person_Set.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), resultDICT)

                # Person
                if lokiRst.getIntent(index, resultIndex) == "Person":
                    resultDICT = Loki_Person.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), resultDICT)

                # Person_Reform
                if lokiRst.getIntent(index, resultIndex) == "Person_Reform":
                    resultDICT = Loki_Person_Reform.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), resultDICT)

                # Person_Establish
                if lokiRst.getIntent(index, resultIndex) == "Person_Establish":
                    resultDICT = Loki_Person_Establish.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), resultDICT)

                # Person_Lead
                if lokiRst.getIntent(index, resultIndex) == "Person_Lead":
                    resultDICT = Loki_Person_Lead.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), resultDICT)

                # Person_Publish
                if lokiRst.getIntent(index, resultIndex) == "Person_Publish":
                    resultDICT = Loki_Person_Publish.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), resultDICT)

                # Person_Produce
                if lokiRst.getIntent(index, resultIndex) == "Person_Produce":
                    resultDICT = Loki_Person_Produce.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), resultDICT)

                # Person_Wrote
                if lokiRst.getIntent(index, resultIndex) == "Person_Wrote":
                    resultDICT = Loki_Person_Wrote.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), resultDICT)

                # Person_Make
                if lokiRst.getIntent(index, resultIndex) == "Person_Make":
                    resultDICT = Loki_Person_Make.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), resultDICT)

                # Person_Receive
                if lokiRst.getIntent(index, resultIndex) == "Person_Receive":
                    resultDICT = Loki_Person_Receive.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), resultDICT)

                # Person_Secure
                if lokiRst.getIntent(index, resultIndex) == "Person_Secure":
                    resultDICT = Loki_Person_Secure.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), resultDICT)

                # Person_Order
                if lokiRst.getIntent(index, resultIndex) == "Person_Order":
                    resultDICT = Loki_Person_Order.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), resultDICT)

                # Person_Create
                if lokiRst.getIntent(index, resultIndex) == "Person_Create":
                    resultDICT = Loki_Person_Create.getResult(key, lokiRst.getUtterance(index, resultIndex), lokiRst.getArgs(index, resultIndex), resultDICT)

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
    inputLIST = ["""Batman is a superhero""","""Augustus was the first Roman emperor""","""Aphrodite is an ancient Greek goddess""","""Augusta Ada King be Countess of Lovelace""","""Alfred Hitchcock was an English filmmaker""","""Voltaire was an advocate of freedom of speech""","""Ashoka was the third emperor of the Maurya Empire""","""Albert Einstein was a German-born theoretical physicist""","""Amelia Mary Earhart was an American aviation pioneer and writer""","""Alexander Hamilton was a Nevisian-born American military officer""","""Alexander III of Macedon was a king of the ancient Greek kingdom of Macedon""","""Albert Camus was an Algerian-born French philosopher, author, dramatist, and journalist""","""Aung San Suu Kyi is a Burmese politician, diplomat, author, and a 1991 Nobel Peace Prize laureate""","""Voltaire was one of the first authors to become renowned and commercially successful internationally"""]
    testLoki(inputLIST, ['Person_Be'])
    print("")

    # Person_Direct
    print("[TEST] Person_Direct")
    inputLIST = ["""He directed over 50 feature films"""]
    testLoki(inputLIST, ['Person_Direct'])
    print("")

    # Person_Develop
    print("[TEST] Person_Develop")
    inputLIST = ["""He developed his "nuclear mysticism" style""","""He developed networks of roads with an official courier system"""]
    testLoki(inputLIST, ['Person_Develop'])
    print("")

    # Person_Became
    print("[TEST] Person_Became")
    inputLIST = ["""He became ill with nasopharyngeal cancer""","""He became as well known as any of his actors""","""He became a civil rights attorney and an academic""","""He became increasingly attracted to Cubism and avant-garde movements""","""Alexander became legendary as a classical hero in the mould of Achilles""","""He posthumously became one of the most famous and influential figures in Western art history"""]
    testLoki(inputLIST, ['Person_Became'])
    print("")

    # Person_Credit
    print("[TEST] Person_Credit")
    inputLIST = ["""He is credited with patenting the first practical telephone""","""He is credited with laying the foundation for American government and finance""","""He is credited with playing an important role in the spread of Buddhism across ancient Asia"""]
    testLoki(inputLIST, ['Person_Credit'])
    print("")

    # Person_Set
    print("[TEST] Person_Set")
    inputLIST = ["""She set many other records"""]
    testLoki(inputLIST, ['Person_Set'])
    print("")

    # Person
    print("[TEST] Person")
    inputLIST = ["""Augusta Ada King be Countess of Lovelace"""]
    testLoki(inputLIST, ['Person'])
    print("")

    # Person_Reform
    print("[TEST] Person_Reform")
    inputLIST = ["""He reformed the Roman system of taxation"""]
    testLoki(inputLIST, ['Person_Reform'])
    print("")

    # Person_Establish
    print("[TEST] Person_Establish")
    inputLIST = ["""He established a standing army""","""He established the Praetorian Guard as well as official police and fire-fighting services for Rome"""]
    testLoki(inputLIST, ['Person_Establish'])
    print("")

    # Person_Lead
    print("[TEST] Person_Lead")
    inputLIST = ["""Babe Ruth led the AL in home runs during a season 12 times"""]
    testLoki(inputLIST, ['Person_Lead'])
    print("")

    # Person_Publish
    print("[TEST] Person_Publish")
    inputLIST = ["""Obama has published three best-selling books"""]
    testLoki(inputLIST, ['Person_Publish'])
    print("")

    # Person_Produce
    print("[TEST] Person_Produce")
    inputLIST = ["""Shakespeare produced most of his known works between 1589 and 1613"""]
    testLoki(inputLIST, ['Person_Produce'])
    print("")

    # Person_Wrote
    print("[TEST] Person_Wrote")
    inputLIST = ["""He wrote more than 20000 letters and 2000 books and pamphlets""","""He also wrote fiction, poetry, autobiography, essays, and criticism"""]
    testLoki(inputLIST, ['Person_Wrote'])
    print("")

    # Person_Make
    print("[TEST] Person_Make")
    inputLIST = ["""Babe Ruth made many public appearances""","""He made peace with the Parthian Empire through diplomacy""","""Jackson made his professional theatre debut in Mother Courage and her Children in 1980"""]
    testLoki(inputLIST, ['Person_Make'])
    print("")

    # Person_Receive
    print("[TEST] Person_Receive")
    inputLIST = ["""He received the BAFTA Fellowship in 1971""","""He received the 1921 Nobel Prize in Physics""","""Dali received his formal education in fine arts in Madrid""","""She received critical acclaim for her performances in the drama ""","""He received a Tony Award for Best Featured Actor in a Play nomination""","""Obama received national attention in 2004 with his March Senate primary win""","""She received the United States Distinguished Flying Cross for this accomplishment"""]
    testLoki(inputLIST, ['Person_Receive'])
    print("")

    # Person_Secure
    print("[TEST] Person_Secure")
    inputLIST = ["""He secured the empire with a buffer region of client states"""]
    testLoki(inputLIST, ['Person_Secure'])
    print("")

    # Person_Order
    print("[TEST] Person_Order")
    inputLIST = ["""He ordered the invasion of Grenada in 1983""","""He ordered the counterterrorism raid which killed Osama bin Laden"""]
    testLoki(inputLIST, ['Person_Order'])
    print("")

    # Person_Create
    print("[TEST] Person_Create")
    inputLIST = ["""He created a new approach to still lifes and local landscapes""","""He created about 2100 artworks, including around 860 oil paintings"""]
    testLoki(inputLIST, ['Person_Create'])
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