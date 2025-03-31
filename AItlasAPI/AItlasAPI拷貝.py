#!/usr/bin/env python3
# -*- coding:utf-8 -*-

#from AItlas_Wiki_Demo import execLoki
from ArticutAPI import Articut
import json
try:
    from AItlas_TW.aitlas_wiki.KG.people import action as actionDICT
except:
    pass

from typing import Union
from functools import reduce
import re

import os
BASEPATH = os.path.dirname(os.path.abspath(__file__))

with open("{}/account.info".format(BASEPATH), encoding="utf-8") as f:
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

class AItlas:
    def is_person(self, entity: str, utteranceLIST: list[str]) -> IsPersonJudgement:
        """
        Check if 'entity' is a person according to the evidences listed in utteranceLIST.
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


    def is_location():
        return None

    def is_superset():
        '''
        inputArgs: "dog", "animal" => False
        '''
        return None

    def is_subset():
        """
        inputArgs: "dog", "animal" => True
        """
        return None

    def converTime():
        """
        """
        return None

    def find_EntyRelation():
        """
        inputArgs: "dog", "animal" => subset
                                   => synonym ("k9", "dog") ("kids", "children")
                                   => superset
                                   => Unknown
        """
        return None

    def what_is_this():
        return None



if __name__ == "__main__":
    longText = """blah blah blah...末綱聰子(???)是一個羽球女子運動員(???)，
    末綱聰子(???)與前田美順(???)的常常組隊參加比賽，
    末綱聰子與前田美順的組合代表日本(???)參加北京(???)舉行的奧運會羽球女子雙打比賽"""

    entity = "前田美順"
    utteranceLIST = ["末綱聰子與前田美順的組合代表日本參加北京舉行的奧運會羽球女子雙打比賽"]
    alias = AItlas()
    isPersonBool = alias.is_person(entity, utteranceLIST) #=>Maybe
    #isLocation = alias.is_location(entity, utteranceLIST)
    print("{} 是 Person 嗎？{}".format(entity, isPersonBool))
