#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Loki module for Person_Receive

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

DEBUG_Person_Receive = True
try:
    userDefinedDICT = json.load(open(os.path.join(os.path.dirname(__file__), "USER_DEFINED.json"), encoding="utf-8"))
except:
    userDefinedDICT = {"_PersonName":["Albert Camus","Albert Einstein","Alexander Graham Bell","Alexander Hamilton","Alexander III","Alfred Hitchcock","Amelia Mary Earhart","Angelina Jolie","Anne Frank","Annelies Marie Frank","Aphrodite","Ashoka","Augusta Ada King","Augustus","Aung San Suu Kyi","Babe Ruth","Barack Hussein Obama II","Barack Obama","George Herman Ruth","Octavian","Suu Kyi","Obama","Osama bin Laden","William Shakespeare","Shakespeare","Voltaire","Van Gogh","Salvador Dali","Samuel Jackson","Jackson","Ronald Reagan"],"_PersonAward":["Nobel Peace Prize","Nobel Prize","BAFTA Fellowship","Distinguished Flying Cross","Tony Award","Best Featured Actor in a Play"],"_PersonBirth":["Algerian-born","German-born","Nevisian-born","Scottish-born"],"_PersonDisease":["nasopharyngeal cancer"],"_PersonArtStyle":["Cubism","avant-garde","Impressionism","nuclear mysticism"],"_PersonOrganization":["Praetorian Guard","Parthian Empire","Roman Empire","AL","American League","Mother Courage and her Children"]}

# Debug message
def debugInfo(inputSTR, utterance):
    if DEBUG_Person_Receive:
        print("[Person_Receive] {} ===> {}".format(inputSTR, utterance))

def getResult(inputSTR, utterance, args, resultDICT):
    debugInfo(inputSTR, utterance)
    if utterance == "[Dali] receive [his] [formal] [education] [in] [fine] [arts] [in] [Madrid]":
        # write your code here
        pass

    if utterance == "[He] receive a [Tony Award] [for] [Best Featured Actor in a Play] [nomination]":
        # write your code here
        pass

    if utterance == "[He] receive the [1921] [Nobel Prize] [in] [Physics]":
        # write your code here
        pass

    if utterance == "[He] receive the [BAFTA Fellowship] [in 1971]":
        # write your code here
        pass

    if utterance == "[Obama] receive [national] [attention] [in 2004] [with] [his] [March] [Senate] [primary] win":
        # write your code here
        pass

    if utterance == "[She] receive [critical] [acclaim] [for] her [performances] [in] the [drama]":
        # write your code here
        pass

    if utterance == "[She] receive the [United States] [Distinguished Flying Cross] [for] this [accomplishment]":
        # write your code here
        pass

    return resultDICT