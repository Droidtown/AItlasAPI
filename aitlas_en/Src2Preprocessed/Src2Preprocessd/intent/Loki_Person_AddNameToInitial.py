#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Loki module for Person_AddNameToInitial

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

DEBUG_Person_AddNameToInitial = True
try:
    userDefinedDICT = json.load(open(os.path.join(os.path.dirname(__file__), "USER_DEFINED.json"), encoding="utf-8"))
except:
    userDefinedDICT = {}

# Debug message
def debugInfo(inputSTR, utterance):
    if DEBUG_Person_AddNameToInitial:
        print("[Person_AddNameToInitial] {} ===> {}".format(inputSTR, utterance))

def getResult(inputSTR, utterance, args, resultDICT):
    debugInfo(inputSTR, utterance)
    if utterance == "[chiefly] know [for] her work [on] CharlesBabbage's [proposed] mechanical [general-purpose] computer":
        # write your code here
        pass

    if utterance == "be a [mathematician]":
        # write your code here
        pass

    if utterance == "be an [English] [mathematician]":
        # write your code here
        pass

    if utterance == "be an [English] [mathematician] and [writer]":
        # write your code here
        pass

    return resultDICT