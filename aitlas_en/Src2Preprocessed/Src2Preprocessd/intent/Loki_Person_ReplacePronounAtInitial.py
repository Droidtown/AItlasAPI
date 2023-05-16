#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Loki module for Person_ReplacePronounAtInitial

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

DEBUG_Person_ReplacePronounAtInitial = True
try:
    userDefinedDICT = json.load(open(os.path.join(os.path.dirname(__file__), "USER_DEFINED.json"), encoding="utf-8"))
except:
    userDefinedDICT = {}

# Debug message
def debugInfo(inputSTR, utterance):
    if DEBUG_Person_ReplacePronounAtInitial:
        print("[Person_ReplacePronounAtInitial] {} ===> {}".format(inputSTR, utterance))

def getResult(inputSTR, utterance, args, resultDICT):
    debugInfo(inputSTR, utterance)
    if utterance == "[She] be the first [to] recognise that [the] [machine] have [applications] [beyond] [pure] [calculation]":
        # write your code here
        pass

    return resultDICT