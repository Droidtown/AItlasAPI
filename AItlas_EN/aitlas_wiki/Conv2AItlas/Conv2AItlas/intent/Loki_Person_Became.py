#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
    Loki module for Person_Became

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

DEBUG_Person_Became = True
try:
    userDefinedDICT = json.load(open(os.path.join(os.path.dirname(__file__), "USER_DEFINED.json"), encoding="utf-8"))
except:
    userDefinedDICT = {"_PersonName":["Albert Camus","Albert Einstein","Alexander Graham Bell","Alexander Hamilton","Alexander III","Alfred Hitchcock","Amelia Mary Earhart","Angelina Jolie","Anne Frank","Annelies Marie Frank","Aphrodite","Ashoka","Augusta Ada King","Augustus","Aung San Suu Kyi","Babe Ruth","Barack Hussein Obama II","Barack Obama","George Herman Ruth","Octavian","Suu Kyi","Obama","Osama bin Laden","William Shakespeare","Shakespeare","Voltaire","Van Gogh","Salvador Dali","Samuel Jackson","Jackson","Ronald Reagan"],"_PersonAward":["Nobel Peace Prize","Nobel Prize","BAFTA Fellowship","Distinguished Flying Cross","Tony Award","Best Featured Actor in a Play"],"_PersonBirth":["Algerian-born","German-born","Nevisian-born","Scottish-born"],"_PersonDisease":["nasopharyngeal cancer"],"_PersonArtStyle":["Cubism","avant-garde","Impressionism","nuclear mysticism"],"_PersonOrganization":["Praetorian Guard","Parthian Empire","Roman Empire","AL","American League","Mother Courage and her Children"]}

# Debug message
def debugInfo(inputSTR, utterance):
    if DEBUG_Person_Became:
        print("[Person_Became] {} ===> {}".format(inputSTR, utterance))

def getResult(inputSTR, utterance, args, resultDICT):
    debugInfo(inputSTR, utterance)
    if utterance == "[Alexander] become [legendary] [as] a [classical] [hero] [in] the [mould] [of] [Achilles]":
        # write your code here
        pass

    if utterance == "[He] [posthumously] become [one] [of] the [most] [famous] and [influential] figure [in] [Western] [art] [history]":
        # write your code here
        pass

    if utterance == "[He] become [as] [well] know [as] [any] [of] his [actors]":
        # write your code here
        pass

    if utterance == "[He] become [ill] [with] [nasopharyngeal cancer]":
        # write your code here
        pass

    if utterance == "[He] become [increasingly] [attracted] [to] [Cubism] and [avant-garde] [movements]":
        # write your code here
        pass

    if utterance == "[He] become a [civil] [rights] [attorney] and an [academic]":
        # write your code here
        pass

    return resultDICT