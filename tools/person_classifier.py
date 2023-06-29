#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import os
import re

personPatLIST = ["{}\s?（[^名又]*）",
                 "{}\s?([^名又]*)",
                 "{}，[^，]+人"
                 ]

dataDIR = "../data/zhwiki_abstract_2306"

def main(entryDIR):
    """
    分辨 fileLIST 中的每一個 json 檔，看它是不是屬於「人類」。如果是的話，就加入列表 [PersonLIST] 中
    """
    for json_f in os.listdir(entryDIR):
        with open("{}/{}".format(entryDIR, json_f), encoding="utf-8") as f:
            topicSTR = json_f.replace(".json", "")
            entrySTR = json.load(f)["abstract"]

    return None


if __name__ == "__main__":
    for init_s in os.listdir(dataDIR):
        if init_s.startswith("._"):
            pass
        else:
            main("{}/{}".format(dataDIR, init_s))