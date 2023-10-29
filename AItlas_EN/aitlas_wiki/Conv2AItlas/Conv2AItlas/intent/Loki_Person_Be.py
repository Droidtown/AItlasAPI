#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Loki module for Person_Be

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

DEBUG_Person_Be = True
try:
    userDefinedDICT = json.load(open(os.path.join(os.path.dirname(__file__), "USER_DEFINED.json"), encoding="utf-8"))
except:
    userDefinedDICT = {"_PersonName":["Albert Camus","Albert Einstein","Alexander Graham Bell","Alexander Hamilton","Alexander III","Alfred Hitchcock","Amelia Mary Earhart","Angelina Jolie","Anne Frank","Annelies Marie Frank","Aphrodite","Ashoka","Augusta Ada King","Augustus","Aung San Suu Kyi","Babe Ruth","Barack Hussein Obama II","Barack Obama","George Herman Ruth","Octavian","Suu Kyi","Obama","Osama bin Laden","William Shakespeare","Shakespeare","Voltaire","Van Gogh","Salvador Dali","Samuel Jackson","Jackson","Ronald Reagan"],"_PersonAward":["Nobel Peace Prize","Nobel Prize","BAFTA Fellowship","Distinguished Flying Cross","Tony Award","Best Featured Actor in a Play"],"_PersonBirth":["Algerian-born","German-born","Nevisian-born","Scottish-born"],"_PersonDisease":["nasopharyngeal cancer"],"_PersonArtStyle":["Cubism","avant-garde","Impressionism","nuclear mysticism"],"_PersonOrganization":["Praetorian Guard","Parthian Empire","Roman Empire","AL","American League","Mother Courage and her Children"]}

# Debug message
def debugInfo(inputSTR, utterance):
    if DEBUG_Person_Be:
        print("[Person_Be] {} ===> {}".format(inputSTR, utterance))

def getResult(inputSTR, utterance, args, resultDICT):
    debugInfo(inputSTR, utterance)
    if utterance == "[Albert Camus] be an [Algerian-born] [French] [philosopher] , [author] , [dramatist] , and [journalist]":
        # write your code here
        pass

    if utterance == "[Albert Einstein] be a [German-born] [theoretical] [physicist]":
        # write your code here
        pass

    if utterance == "[Alexander Hamilton] be a [Nevisian-born] [American] [military] [officer]":
        # write your code here
        pass

    if utterance == "[Alexander III] [of] [Macedon] be a [king of] the [ancient] [Greek] [kingdom] [of] [Macedon]":
        # write your code here
        pass

    if utterance == "[Alfred Hitchcock] be an [English] [filmmaker]":
        # write your code here
        pass

    if utterance == "[Amelia Mary Earhart] be an [American] [aviation] [pioneer] and [writer]":
        # write your code here
        pass

    if utterance == "[Aphrodite] be an [ancient] [Greek] [goddess]":
        # write your code here
        pass

    if utterance == "[Ashoka] be the third [emperor] [of] the [Maurya] [Empire]":
        # write your code here
        pass

    if utterance == "[Augusta Ada King] be [Countess] [of] [Lovelace]":
        # write your code here
        pass

    if utterance == "[Augustus] be the first [Roman] [emperor]":
        # write your code here
        pass

    if utterance == "[Aung San Suu Kyi] be a [Burmese] [politician] , [diplomat] , [author] , and a 1991 [Nobel Peace Prize] [laureate]":
        # write your code here
        pass

    if utterance == "[Batman] be a [superhero]":
        # write your code here
        pass

    if utterance == "[Voltaire] be [one] [of] the first [authors] [to] become [renowned] and [commercially] [successful] [internationally]":
        # write your code here
        pass

    if utterance == "[Voltaire] be an [advocate of] [freedom] [of] [speech]":
        # write your code here
        pass

    return resultDICT