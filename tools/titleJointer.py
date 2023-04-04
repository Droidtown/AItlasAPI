#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import os
import re

from ArticutAPI import Articut
with open("../account.info", encoding="utf-8") as f:
    accountDICT = json.load(f)
articut = Articut(username=accountDICT["username"], apikey=accountDICT["apikey"])


purgePat = re.compile("(\\t\\n\d)|(\d?\\t)|(\\n)|（[^）]*?）|(\([^）]*?\))")
posPurgePat = re.compile("</?\w+?(_\w+?)+?>")

def txt2dict(rawdataDIR):
    """
    Convert rawdata text into stage01 dict format and pack it into a list to be saved as json format.
    """
    resultLIST = []
    for i in os.listdir(rawdataDIR):
        with open("{}/{}".format(rawdataDIR, i)) as f:
            dLIST = f.readlines()
        for d in dLIST[:4]:
            resultLIST.append(json.loads(d))
            resultLIST[-1]["text"] = re.sub(purgePat, "", resultLIST[-1]["text"].replace(" ", ""))
            resultLIST[-1]["lines"] = "" #re.sub(purgePat, "", resultLIST[-1]["lines"].replace(" ", ""))
            #if resultLIST[-1]["lines"] == resultLIST[-1]["text"]:
                #resultLIST[-1]["lines"] = ""
        with open("../data/preprocessed/stage01_text/{}".format(i.replace("jsonl", "json")), encoding="utf-8", mode="w") as newF:
            json.dump(resultLIST, newF, ensure_ascii=False)

    return resultLIST

def stage02maker(stage01DIR):
    """

    """
    resultLIST = []
    for i in os.listdir(stage01DIR):
        with open("{}/{}".format(stage01DIR, i)) as f:
            stage01LIST = json.load(f)
        for e in stage01LIST:
            title = re.sub("_(.+?)", "", e["id"])
            rDICT = articut.parse(e["text"])
            jointedTEXT = titleJointer(title, rDICT["result_pos"])
            resultLIST.append({"id":title, "text2":jointedTEXT})
    return resultLIST

def titleJointer(titleSTR, result_pos):
    resultLIST = []
    for c in range(0, len(result_pos)):
        if result_pos[c+1] in "|=、．" or result_pos[c-1] in "|=、．":
            pass
        elif [result_pos[c]] == [g.grou(0) for  g in re.finditer("<TIME_[^>]+>[^<]+</TIME[^>]+>")]:
            resultLIST.append(result_pos[c])
        elif result_pos[c].startswith("<UserDefined>"):
            resultLIST.append(result_pos[c])
        elif result_pos[c].startswith("<FUNC_inter>但") or result_pos[c].startswith("<FUNC_inter>即") or result_pos[c].startswith("<FUNC_inter>此外"):
            resultLIST.append(result_pos[c])
        elif result_pos[c].endswith("</RANGE_period>") or result_pos[c].endswith("</RANGE_locality>"):
            resultLIST.append(result_pos[c])
        elif result_pos[c].startswith("<AUX>") or result_pos[c].startswith("<ACTION") or result_pos[c].startswith("<ASPECT>") or result_pos[c].startswith("<MODAL>") or result_pos[c].startswith("<TIME") or result_pos[c].startswith("<FUNC_inner>") or result_pos[c].startswith("<QUANTIFIER>"):
            resultLIST.append("<UserDefined>{}</UserDefined>{}".format(titleSTR, result_pos[c]))
        elif result_pos[c].startswith("<ENTITY_pronoun>"):
            resultLIST.append("<UserDefined>{}</UserDefined>{}".format(titleSTR, re.sub("<ENTITY_pronoun>[^<]+</ENTITY_pronoun>", "", result_pos[c], count=1)))
        elif result_pos[c].startswith("<FUNC_determiner>"):
            resultLIST.append("<UserDefined>{}</UserDefined>{}".format(titleSTR, re.sub("<FUNC_determiner>[^<]+</FUNC_determiner>", "", result_pos[c], count=1)))
        elif result_pos[c].startswith("<ENTITY_DetPhrase>"):
            resultLIST.append("<UserDefined>{}</UserDefined>{}".format(titleSTR, re.sub("<ENTITY_DetPhrase>[^<]+</ENTITY_DetPhrase>", "", result_pos[c], count=1)))
        elif result_pos[c].startswith("<FUNC_inter>"):
            resultLIST.append("<UserDefined>{}</UserDefined>{}".format(titleSTR, re.sub("<FUNC_inter>[^<]+</FUNC_inter>", "", result_pos[c], count=1)))
        elif result_pos[c].startswith("<ENTITY_nouny>此") or result_pos[c].startswith("<ENTITY_nouny>物"):
            resultLIST.append("<UserDefined>{}</UserDefined>{}".format(titleSTR, re.sub("<ENTITY_nouny>[^<]+</ENTITY_nouny>", "", result_pos[c], count=1)))
        elif [result_pos[c]] == [g.grou(0) for  g in re.finditer("<ENTITY_[^c>]+>[^<]+</ENTITY[^c>]+>")]:
            resultLIST.append("<UserDefined>{}</UserDefined><AUX>是</AUX>{}".format(titleSTR, result_pos[c]))
        else:
            resultLIST.append("<UserDefined>_{}_</UserDefined>{}".format(titleSTR, result_pos[c]))
    return resultLIST




if __name__ == "__main__":
    #rawdataDIR = "../data/wiki-pages"
    #resultLIST = txt2dict(rawdataDIR)



