#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Loki module for Person_Create

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

DEBUG_Person_Create = True
try:
    userDefinedDICT = json.load(open(os.path.join(os.path.dirname(__file__), "USER_DEFINED.json"), encoding="utf-8"))
except:
    userDefinedDICT = {"_PersonName":["Albert Camus","Albert Einstein","Alexander Graham Bell","Alexander Hamilton","Alexander III","Alfred Hitchcock","Amelia Mary Earhart","Angelina Jolie","Anne Frank","Annelies Marie Frank","Aphrodite","Ashoka","Augusta Ada King","Augustus","Aung San Suu Kyi","Babe Ruth","Barack Hussein Obama II","Barack Obama","George Herman Ruth","Octavian","Suu Kyi","Obama","Osama bin Laden","William Shakespeare","Shakespeare","Voltaire","Van Gogh","Salvador Dali","Samuel Jackson","Jackson","Ronald Reagan"],"_PersonAward":["Nobel Peace Prize","Nobel Prize","BAFTA Fellowship","Distinguished Flying Cross","Tony Award","Best Featured Actor in a Play"],"_PersonBirth":["Algerian-born","German-born","Nevisian-born","Scottish-born"],"_PersonDisease":["nasopharyngeal cancer"],"_PersonArtStyle":["Cubism","avant-garde","Impressionism","nuclear mysticism"],"_PersonOrganization":["Praetorian Guard","Parthian Empire","Roman Empire","AL","American League","Mother Courage and her Children"]}

# Debug message
def debugInfo(inputSTR, utterance):
    if DEBUG_Person_Create:
        print("[Person_Create] {} ===> {}".format(inputSTR, utterance))

def getResult(inputSTR, utterance, args, resultDICT):
    debugInfo(inputSTR, utterance)
    if utterance == "[He] create [about] [2100] [artworks] , [including] [around] [860] [oil] [paintings]":
        # write your code here
        pass

    if utterance == "[He] create a [new] [approach] [to] [still] [lifes] and [local] [landscapes]":
        # write your code here
        pass

    return resultDICT