#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import os
import re

purgePat = re.compile("(\\t\\n\d)|(\d?\\t)|(\\n)|（[^）]*?）|(\([^）]*?\))")

def txt2dict(rawdataDIR):
    """

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


if __name__ == "__main__":
    rawdataDIR = "../data/wiki-pages"
    resultLIST = txt2dict(rawdataDIR)


