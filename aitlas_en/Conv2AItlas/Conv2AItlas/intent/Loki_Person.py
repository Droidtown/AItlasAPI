#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Loki module for Person

    Input:
        inputSTR      str,
        utterance     str,
        args          str[],
        resultDICT    dict

    Output:
        resultDICT    dict
"""

import json
import os

DEBUG_Person = True
try:
    userDefinedDICT = json.load(open(os.path.join(os.path.dirname(__file__), "USER_DEFINED.json"), encoding="utf-8"))
except:
    userDefinedDICT = {"_PersonName":["Augusta Ada King"]}

# Debug message
def debugInfo(inputSTR, utterance):
    if DEBUG_Person:
        print("[Person] {} ===> {}".format(inputSTR, utterance))

def getResult(inputSTR, utterance, args, resultDICT):
    debugInfo(inputSTR, utterance)
    if utterance == "[Augusta Ada King] be [Countess] [of] [Lovelace]":
        # write your code here
        pass

    return resultDICT