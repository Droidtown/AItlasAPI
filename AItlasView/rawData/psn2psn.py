#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from ArticutAPI import Articut
articut = Articut()

import json
import re

def main():
    """"""
    return None


if __name__ == "__main__":
    with open("./京華城案.json", "r", encoding="utf-8") as f:
        inputDICT = json.load(f)["article"]
    #print(inputDICT)

    with open("./AItlas_wiki_person.json", "r", encoding="utf-8") as f:
        knownPersonLIST = [p for p in json.load(f).keys()]
    #print(knownPersonLIST)

    personLIST = []
    for k in knownPersonLIST:
        for news in inputDICT.keys():
            if k in inputDICT[news]:
                personLIST.append(k)
    personLIST = list(set(personLIST))
    print(personLIST)
    print(len(personLIST))

    for news in inputDICT.keys():
        resultDICT = articut.parse(inputDICT[news])
        if resultDICT["status"] == True:
            sentenceLIST = articut.getPersonLIST(resultDICT, includePronounBOOL=False)
            for s in sentenceLIST:
                if s == []:
                    pass
                else:
                    for p in s:
                        personLIST.append(p[-1])
        else:
            print(f"Segmentation Failed with:{news}")
            print(resultDICT)
    personLIST = list(set(personLIST))
    print(personLIST)
    print(len(personLIST))