#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Loki module for Person_AddNameToInitial_adv

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

DEBUG_Person_AddNameToInitial_adv = True
try:
    userDefinedDICT = json.load(open(os.path.join(os.path.dirname(__file__), "USER_DEFINED.json"), encoding="utf-8"))
except:
    userDefinedDICT = {}

# Debug message
def debugInfo(inputSTR, utterance):
    if DEBUG_Person_AddNameToInitial_adv:
        print("[Person_AddNameToInitial_adv] {} ===> {}".format(inputSTR, utterance))

def getResult(inputSTR, utterance, args, resultDICT):
    debugInfo(inputSTR, utterance)
    if utterance == "Countess of Lovelace":
        # write your code here
        pass

    return resultDICT