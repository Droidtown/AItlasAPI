#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from AItlas_Wiki_Demo import execLoki
from ArticutAPI import Articut
import json
from KG.people import action as actionDICT
from typing import Union
from functools import reduce

with open("account.info", encoding="utf-8") as f:
    accountDICT = json.load(f)
articut = Articut(username=accountDICT["username"], apikey=accountDICT["api_key"])

class MaybePerson:
    reasonLIST : list

    def __init__(self):
        self.reasonLIST = []

    def __repr__(self):
        return "Maybe"

IsPersonJudgement = Union[bool, MaybePerson] #True, False, "Maybe"

peopleLIST = []
for v_D in actionDICT:
    for obj in actionDICT[v_D]:
        if obj == "attribute":
            pass
        else:
            for p_L in actionDICT[v_D][obj]:
                peopleLIST.append(p_L["name"])
peopleLIST = {e for e in peopleLIST}

def wordExtractor(inputLIST, unify=True):
    """
    配合 Articut() 的各種 .getXXXLIST() 只抽出詞彙。
    """
    resultLIST = []
    for i in inputLIST:
        if i == []:
            pass
        else:
            for e in i:
                resultLIST.append(e[-1])
    if unify == True:
        return sorted(list(set(resultLIST)))
    else:
        return sorted(resultLIST)


def is_person(entity: str, utteranceLIST: list[str]) -> IsPersonJudgement:
    """
    Each utterance should contain the entity given.
    """
    # Check the existence of the entity in every utterance.
    checkList = list(map( lambda u: len(re.findall(entity,u))==0
                    , utteranceLIST))
    # Throws ValueError if any of the utterances doesn't satisfy the requirement.
    if reduce(lambda x,y:x or y, checkList):
        errorList = []
        for k,v in enumerate(checkList):
            if v:
                errorList.append(k)
        raise ValueError(f"In indexes:{errorList} of utteranceLIST, the entity doesn't show in the utterance.")

    if entity in peopleLIST:
        return True
    else:
        #get verbs from utteranceLIST

        for u_s in utteranceLIST:
            resultDICT = articut.parse(u_s)
            verbLIST = articut.getVerbStemLIST(resultDICT)
            verbLIST = wordExtractor(verbLIST)

        for v_s in verbLIST:
            checkingUtteranceLIST = []
            intentKey = articut.parse(v_s, level="lv3", pinyin="HANYU")["utterance"][0].replace(" ", "")
            for u_s in utteranceLIST:
                checkingUtteranceLIST.append(u_s[u_s.index(v_s):])
            lokiResult = execLoki(checkingUtteranceLIST)
            if intentKey in lokiResult:
                return MaybePerson()
        return False


if __name__ == "__main__":
    entity = "前田美順"
    utteranceLIST = ["末綱聰子與前田美順的組合代表日本參加北京舉行的奧運會羽球女子雙打比賽"]
    isPersonBool = is_person(entity, utteranceLIST)
    print("{} 是 Person 嗎？{}".format(entity, isPersonBool))
