#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import os
import re

from pprint import pprint

personPatLIST = ["^{}\s?（[^名又a-zA-Z]*）",
                 "^{}\s?\([^名又a-zA-Z]*\)",
                 "^{}，[^a-zA-Z]+人"
                 ]

dataDIR = "../data/zhwiki_abstract_2306"

def main(entryDIR):
    """
    分辨 fileLIST 中的每一個 json 檔，看它是不是屬於「人類」。如果是的話，就加入列表 [PersonLIST] 中
    """
    personLIST = []
    for json_f in os.listdir(entryDIR):
        try:
            with open("{}/{}".format(entryDIR, json_f), encoding="utf-8") as f:
                topicSTR = json_f.replace(".json", "")
                entrySTR = json.load(f)["abstract"]
            for p in personPatLIST:
                pat = re.compile(p.format(topicSTR))
                if len(list(re.finditer(pat, entrySTR))) > 0:
                    personLIST.append(topicSTR)
                else:
                    pass
        except IsADirectoryError:
            pass
    return personLIST


if __name__ == "__main__":
    personLIST = []
    for init_s in os.listdir(dataDIR):
        if init_s.startswith("._"):
            pass
        else:
            personLIST.extend(main("{}/{}".format(dataDIR, init_s)))
    pprint(personLIST)