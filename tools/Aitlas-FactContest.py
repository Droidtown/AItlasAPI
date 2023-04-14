#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import os
import re
import tempfile

from pprint import pprint

from ArticutAPI import Articut
with open("../account.info", encoding="utf-8") as f:
    accountDICT = json.load(f)

articut = Articut(username=accountDICT["username"], apikey=accountDICT["apikey"])

quotePat = re.compile("\s['「『《（“][^「『《（]+?['」』》）”]\s")

with open("../data/idLIST.json", encoding="utf-8") as f:
    idLIST = json.load(f)

outputDICT = {}

def querySTR2posSEQ(allQuestionDICT, outputDIR):
    """

    """
    keyLIST = list(allQuestionDICT.keys())
    for key_s in keyLIST:
        tempUDLIST = []
        #<產生動態自訂字典>
        for entry_s in idLIST:
            if entry_s == "":
                break
            elif len(re.findall("[a-zA-Z]+", entry_s)) > 0 and re.findall("[a-zA-Z]+", entry_s)[0] == entry_s:
                pass
            elif entry_s[0] in allQuestionDICT[key_s] and len(entry_s) > 2: #詞長度大於 2 且出現在目標字串內的 id (entry_s[0]) 才被列入動態自訂字典
                tempUDLIST.append(entry_s)
        print(allQuestionDICT[key_s])
        for quote_s in [q.group(0) for q in quotePat.finditer(allQuestionDICT[key_s])]:
            allQuestionDICT[key_s] = allQuestionDICT[key_s].replace(quote_s, quote_s[3:-3])
            tempUDLIST.append(quote_s[3:-3])
        tempDICT = tempfile.NamedTemporaryFile(mode="w+")
        json.dump({"_userDefined":tempUDLIST}, tempDICT)
        tempDICT.flush()
        #</產生動態自訂字典>
        resultDICT = articut.parse(allQuestionDICT[key_s], userDefinedDictFILE=tempDICT.name)
        for sent_s in resultDICT["result_obj"]:
            resultLIST = []
            pos_seq = "-".join([pos_s["pos"].replace("_nounHead", "").replace("_nouny", "").replace("_noun", "").replace("_oov", "") for pos_s in sent_s if pos_s["pos"] != "PUNCTUATION"])
            raw_s = "".join([pos_s["text"] for pos_s in sent_s if pos_s["pos"] != "PUNCTUATION"])
            pos_s = "".join(["<{1}>{0}</{1}>".format(pos_s["text"], pos_s["pos"]) for pos_s in sent_s if pos_s["pos"] != "PUNCTUATION"])
            if raw_s != "":
                resultLIST.append([key_s, raw_s, pos_s])
                if pos_seq in outputDICT.keys():
                    outputDICT[pos_seq].extend(resultLIST)
                else:
                    outputDICT[pos_seq] = resultLIST

    for fileName in outputDICT.keys():
        with open("{}/{}.json".format(outputDIR, fileName), encoding="utf-8", mode="a+") as f:
            json.dump(outputDICT[fileName], f, ensure_ascii=False)


    return outputDICT


if __name__ == "__main__":
    with open("../data/AllQuestion.json", encoding="utf-8") as f:
        questionLIST = json.load(f)
    outputDIR = "../data/preprocessed/stage03_ssp"
    result = querySTR2posSEQ(questionLIST, outputDIR)
    pprint(result)
