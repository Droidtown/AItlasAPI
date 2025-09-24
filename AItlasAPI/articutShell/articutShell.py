#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import re
import sys
import time
from pprint import pprint
from pathlib import Path
import json
from typing import Any, Union

from ArticutAPI import Articut

from articutShell.dynamic_userdefined.dynamic_UD import (
    createUDByGuillemets,
    createCNAMemberUD,
    dict2File,
    dictForger,
    findExactDictionary,
    dictConfirmer,
    _getEntry,
    createAbbrUD
)

G_accountDICT: dict = {}
try:
    with open(Path.cwd()/"account.info", encoding="utf-8") as f:
        G_accountDICT = json.load(f)
    if "url" in G_accountDICT:
        articut = Articut(url=G_accountDICT["url"])
    else:
        articut = Articut(username=G_accountDICT["username"], apikey=G_accountDICT["api_key"])
except:
    print("[articutShell] 請先新增 account.info 並填入相關資訊")
    exit()

if "url" in G_accountDICT:
    # docker 版登入
    articut = Articut(url=G_accountDICT["url"])
elif "username" and "apikey" in G_accountDICT:
    # 線上 版登入
    articut = Articut(username=G_accountDICT["username"], apikey=G_accountDICT["apikey"])

G_splitSpecifyPerson_pat = re.compile(r"<ENTITY_person>向[台臺英法德俄泰韓美中共澳越日朝星紐馬菲義華瓜帛烏荷以阿緬波布蒲喀象埃港厄衣甘加肯賴摩莫納奈盧聖塞獅索史坦突辛亞巴孟汶柬賽喬伊約哈黎蒙尼沙斯敘塔土奧比保克芬匈拉印葡羅西哥薩宏牙墨玻蓋秘委斐吉諾吐]方</ENTITY_person>")
G_nameExcept_pat = re.compile(r"向[台臺英法德俄泰韓美中共澳越日朝星紐馬菲義華瓜帛烏荷以阿緬波布蒲喀象埃港厄衣甘加肯賴摩莫納奈盧聖塞獅索史坦突辛亞巴孟汶柬賽喬伊約哈黎蒙尼沙斯敘塔土奧比保克芬匈拉印葡羅西哥薩宏牙墨玻蓋秘委斐吉諾吐]方")
G_extractText_pat = re.compile(r"</?[^>]+>")
G_extracTagAndText_pat = re.compile(r"<([^<]+)>([^<]+)</\1>")
# G_mergeEnglish_pat = re.compile(r"(?<=[a-zA-Z\s])</[a-zA-Z_]+> <[a-zA-Z_]+>(?=[a-zA-Z\s])")
G_mergeByInterpunct_pat = re.compile(
    r"((?<=[a-zA-Z\s])</[a-zA-Z_]+>[ˑ∘·ּ⏺⦁‧∙◦⚫𐄁⸳⸰•●⋅᛫⸱ꞏ･．・·]<[a-zA-Z_]+>(?=[a-zA-Z\s]))"
)
G_getTag_pat = re.compile(r"(<[/a-zA-Z_]+>)")
G_getText_pat = re.compile(r"(?<=\>)([^<]+)(?=\<)")
G_pun_pat = re.compile(r"((?<=>)|(?<=^))[^一-龥a-zA-Z<>]+((?=<)|(?=$))")
G_getQuantifierGroup_pat = re.compile(r"<QUANTIFIER>.</QUANTIFIER><((ENTITY_(?:(oov|noun|nouny|nounHead)))|(FUNC_negation))>(.[會]?)</((ENTITY_(?:(oov|noun|nouny|nounHead)))|(FUNC_negation))>")
G_getAfterQuantifier_pat = re.compile(r"</((?:ENTITY_(?:oov|noun|nouny|nounHead))|(?:FUNC_negation))>")
G_getColorGroup_pat = re.compile(r"<MODIFIER_color>[^<]+</MODIFIER_color>(<[/a-zA-Z_]+>)(..)(<[/a-zA-Z_]+>)")
G_getAfterColor_pat = re.compile(r"<MODIFIER_color>[^<]+</MODIFIER_color><([/a-zA-Z_]+)>..<[/a-zA-Z_]+>")
G_getLocalityGroup_pat = re.compile(r"<(ENTITY_(?:(oov|noun|nouny|nounHead)))>[^<]+</(ENTITY_(?:(oov|noun|nouny|nounHead)))><RANGE_locality>(?!內)[^<]+</RANGE_locality>")
G_getAfterLocality_pat = re.compile(r"</((?:ENTITY_(?:oov|noun|nouny|nounHead))|(?:MODIFIER))><RANGE_locality>[^<]+</RANGE_locality>")
G_getVerbObjectStructure_pat = re.compile(r"(<[^<]+>[抗反返親仇友挺愛毀賣知傾滅排助聯援制]<[^>]+><[^>]+>[台臺英法德俄泰韓美中共澳越日朝星紐馬菲義華瓜帛烏荷以阿緬波布蒲喀象埃港厄衣甘加肯賴摩莫納奈盧聖塞獅索史坦突辛亞巴孟汶柬賽喬伊約哈黎蒙尼沙斯敘塔土奧比保克芬匈拉印葡羅西哥薩宏牙墨玻蓋秘委斐吉諾吐]+<[^>]+>(<[^>]+>[台臺英法德俄泰韓美中共澳越日朝星紐馬菲義華瓜帛烏荷以阿緬波布蒲喀象埃港厄衣甘加肯賴摩莫納奈盧聖塞獅索史坦突辛亞巴孟汶柬賽喬伊約哈黎蒙尼沙斯敘塔土奧比保克芬匈拉印葡羅西哥薩宏牙墨玻蓋秘委斐吉諾吐]<[^>]+>)*)|(<((?!(LOCATION))[^<]+)>[抗反返親仇友挺愛毀賣知傾滅排助聯援制][台臺英法德俄泰韓美中共澳越日朝星紐馬菲義華瓜帛烏荷以阿緬波布蒲喀象埃港厄衣甘加肯賴摩莫納奈盧聖塞獅索史坦突辛亞巴孟汶柬賽喬伊約哈黎蒙尼沙斯敘塔土奧比保克芬匈拉印葡羅西哥薩宏牙墨玻蓋秘委斐吉諾吐]+<((?!(LOCATION))[^<]+)>)(<[^>]+>[台臺英法德俄泰韓美中共澳越日朝星紐馬菲義華瓜帛烏荷以阿緬波布蒲喀象埃港厄衣甘加肯賴摩莫納奈盧聖塞獅索史坦突辛亞巴孟汶柬賽喬伊約哈黎蒙尼沙斯敘塔土奧比保克芬匈拉印葡羅西哥薩宏牙墨玻蓋秘委斐吉諾吐]<[^>]+>)*")
G_getVerbObjectStructurePhrase_pat = re.compile(r"(<[^>]+>[抗反返親仇友挺愛毀賣知傾滅排助聯援制][台臺英法德俄泰韓美中共澳越日朝星紐馬菲義華瓜帛烏荷以阿緬波布蒲喀象埃港厄衣甘加肯賴摩莫納奈盧聖塞獅索史坦突辛亞巴孟汶柬賽喬伊約哈黎蒙尼沙斯敘塔土奧比保克芬匈拉印葡羅西哥薩宏牙墨玻蓋秘委斐吉諾吐]+<[^>]+>(<[^>]+>[台臺英法德俄泰韓美中共澳越日朝星紐馬菲義華瓜帛烏荷以阿緬波布蒲喀象埃港厄衣甘加肯賴摩莫納奈盧聖塞獅索史坦突辛亞巴孟汶柬賽喬伊約哈黎蒙尼沙斯敘塔土奧比保克芬匈拉印葡羅西哥薩宏牙墨玻蓋秘委斐吉諾吐]<[^>]+>)*<[^>]+>(名將|英雄|成功|派系|派|民族|重任|聯盟|氣氛|情緒|勢力|聲浪|現象|情緒|觀點|論述|路線|立場|思想|教育|政權|團體|議案|案|法案|條文|決議|決議文|動議|力量|小組|陣線|議員|學者|協會|主席|計畫|謠言|論|行為|集團|運動|色彩|暴動|國家|路徑)<[^>]+>)|(<[^>]+>[抗反返親仇友挺愛毀賣知傾滅排助聯援制]<[^>]+>(<[^>]+>[台臺英法德俄泰韓美中共澳越日朝星紐馬菲義華瓜帛烏荷以阿緬波布蒲喀象埃港厄衣甘加肯賴摩莫納奈盧聖塞獅索史坦突辛亞巴孟汶柬賽喬伊約哈黎蒙尼沙斯敘塔土奧比保克芬匈拉印葡羅西哥薩宏牙墨玻蓋秘委斐吉諾吐]<[^>]+>)*<[^>]+>[台臺英法德俄泰韓美中共澳越日朝星紐馬菲義華瓜帛烏荷以阿緬波布蒲喀象埃港厄衣甘加肯賴摩莫納奈盧聖塞獅索史坦突辛亞巴孟汶柬賽喬伊約哈黎蒙尼沙斯敘塔土奧比保克芬匈拉印葡羅西哥薩宏牙墨玻蓋秘委斐吉諾吐]+(名將|英雄|成功|派系|派|民族|重任|聯盟|氣氛|情緒|勢力|聲浪|現象|情緒|觀點|論述|路線|立場|思想|教育|政權|團體|議案|案|法案|條文|決議|決議文|動議|力量|小組|陣線|議員|學者|協會|主席|計畫|謠言|論|行為|集團|運動|色彩|暴動|國家|路徑)<[^>]+>)|(<[^>]+>[抗反返親仇友挺愛毀賣知傾滅排助聯援制][台臺英法德俄泰韓美中共澳越日朝星紐馬菲義華瓜帛烏荷以阿緬波布蒲喀象埃港厄衣甘加肯賴摩莫納奈盧聖塞獅索史坦突辛亞巴孟汶柬賽喬伊約哈黎蒙尼沙斯敘塔土奧比保克芬匈拉印葡羅西哥薩宏牙墨玻蓋秘委斐吉諾吐]+(名將|英雄|成功|派系|派|民族|重任|聯盟|氣氛|情緒|勢力|聲浪|現象|情緒|觀點|論述|路線|立場|思想|教育|政權|團體|議案|案|法案|條文|決議|決議文|動議|力量|小組|陣線|議員|學者|協會|主席|計畫|謠言|論|行為|集團|運動|色彩|暴動|國家|路徑)<[^>]+>)")
G_getVerbObjectStructurePhraseCountries_pat = re.compile(r"(<[^>]+>[抗反返親仇友挺愛毀賣知傾滅排助聯援制][台臺英法德俄泰韓美中共澳越日朝星紐馬菲義華瓜帛烏荷以阿緬波布蒲喀象埃港厄衣甘加肯賴摩莫納奈盧聖塞獅索史坦突辛亞巴孟汶柬賽喬伊約哈黎蒙尼沙斯敘塔土奧比保克芬匈拉印葡羅西哥薩宏牙墨玻蓋秘委斐吉諾吐]+<[^>]+><[^>]+>軍<[^>]+>)|(<[^>]+>[抗反返親仇友挺愛毀賣知傾滅排助聯援制][台臺英法德俄泰韓美中共澳越日朝星紐馬菲義華瓜帛烏荷以阿緬波布蒲喀象埃港厄衣甘加肯賴摩莫納奈盧聖塞獅索史坦突辛亞巴孟汶柬賽喬伊約哈黎蒙尼沙斯敘塔土奧比保克芬匈拉印葡羅西哥薩宏牙墨玻蓋秘委斐吉諾吐]*<[^>]+><[^>]+>[台臺英法德俄泰韓美中共澳越日朝星紐馬菲義華瓜帛烏荷以阿緬波布蒲喀象埃港厄衣甘加肯賴摩莫納奈盧聖塞獅索史坦突辛亞巴孟汶柬賽喬伊約哈黎蒙尼沙斯敘塔土奧比保克芬匈拉印葡羅西哥薩宏牙墨玻蓋秘委斐吉諾吐]+軍<[^>]+>)")
G_getCountry_pat = re.compile(r"(<[^>]+>(?!(紐約)|(中共)|(巴黎)|(賽塔)|(馬斯克)|(印象)|(比賽))[台臺英法德俄泰韓美中共澳越日朝星紐馬菲義華瓜帛烏荷以阿緬波布蒲喀象埃港厄衣甘加肯賴摩莫納奈盧聖塞獅索史坦突辛亞巴孟汶柬賽喬伊約哈黎蒙尼沙斯敘塔土奧比保克芬匈拉印葡羅西哥薩宏牙墨玻蓋秘委斐吉諾吐]+<[^>]+>)+")
G_getCountryPhrase_pat = re.compile(r"(<[^>]+>[台臺英法德俄泰韓美中共澳越日朝星紐馬菲義華瓜帛烏荷以阿緬波布蒲喀象埃港厄衣甘加肯賴摩莫納奈盧聖塞獅索史坦突辛亞巴孟汶柬賽喬伊約哈黎蒙尼沙斯敘塔土奧比保克芬匈拉印葡羅西哥薩宏牙墨玻蓋秘委斐吉諾吐]+<[^>]+>)+(<[^>]+>[台臺英法德俄泰韓美中共澳越日朝星紐馬菲義華瓜帛烏荷以阿緬波布蒲喀象埃港厄衣甘加肯賴摩莫納奈盧聖塞獅索史坦突辛亞巴孟汶柬賽喬伊約哈黎蒙尼沙斯敘塔土奧比保克芬匈拉印葡羅西哥薩宏牙墨玻蓋秘委斐吉諾吐]<[^>]+>)*<[^>]+>[台臺英法德俄泰韓美中共澳越日朝星紐馬菲義華瓜帛烏荷以阿緬波布蒲喀象埃港厄衣甘加肯賴摩莫納奈盧聖塞獅索史坦突辛亞巴孟汶柬賽喬伊約哈黎蒙尼沙斯敘塔土奧比保克芬匈拉印葡羅西哥薩宏牙墨玻蓋秘委斐吉諾吐]*(關係|大戰|文化|交流|合作|衝突)<[^>]+>")
G_getCountryAbbr_pat = re.compile(r"((<[^>]+>[台臺英法德俄泰韓美中共澳越日朝星紐馬菲義華瓜帛烏荷以阿緬波布蒲喀象埃港厄衣甘加肯賴摩莫納奈盧聖塞獅索史坦突辛亞巴孟汶柬賽喬伊約哈黎蒙尼沙斯敘塔土奧比保克芬匈拉印葡羅西哥薩宏牙墨玻蓋秘委斐吉諾吐]<[^>]+>)+(<[^>]+>[台臺英法德俄泰韓美中共澳越日朝星紐馬菲義華瓜帛烏荷以阿緬波布蒲喀象埃港厄衣甘加肯賴摩莫納奈盧聖塞獅索史坦突辛亞巴孟汶柬賽喬伊約哈黎蒙尼沙斯敘塔土奧比保克芬匈拉印葡羅西哥薩宏牙墨玻蓋秘委斐吉諾吐]*[媒軍籍方府裔股商資生企國][^<]*<[^>]+>))|(<(?!UserDefined)[^>]+>[台臺英法德俄泰韓美中共澳越日朝星紐馬菲義華瓜帛烏荷以阿緬波布蒲喀象埃港厄衣甘加肯賴摩莫納奈盧聖塞獅索史坦突辛亞巴孟汶柬賽喬伊約哈黎蒙尼沙斯敘塔土奧比保克芬匈拉印葡羅西哥薩宏牙墨玻蓋秘委斐吉諾吐]+[媒軍籍方府裔股商資生企國][^<]*<(?!UserDefined)[^>]+>)")
G_getMediaTerm_pat = re.compile(r"(((<[^>]+>[藍綠白]<[^>]+>)+<[^>]+>[藍綠白]*[委營媒][^<]*<[^>]+>)|((<[^>]+>[藍綠白]<[^>]+>)*<[^>]+>[藍綠白]+[委營媒][^<]*<[^>]+>))(<[^>]+>人物<[^>]+>)*")
G_getJobTitle_pat = re.compile(r"(<[^>]+>前</[^>]+>)*<KNOWLEDGE_(adminAgency|TWAdminDistrict|TWGov|TWJudicial|TWPresidentialOffice|TWProcuratorate|unitedNationsSystem|organization|location)>[^<]+</KNOWLEDGE_(adminAgency|TWAdminDistrict|TWGov|TWJudicial|TWPresidentialOffice|TWProcuratorate|unitedNationsSystem|organization|location)><[^>]+>長<[^>]+>(?!<[^>]+>時間</[^>]+>)")
G_getJobTitlePhrase_pat = re.compile(r"((<[^>]+>前</[^>]+>)*<[^>]+>[^<]*[處科院局組會室署官部館市縣所州]長<[^>]+>)|((<[^>]+>前</[^>]+>)*<KNOWLEDGE_chief>[^<]+</KNOWLEDGE_chief>)")
G_getUnit2Num_pat = re.compile(r"<[^<]+>第[\d一二三四五六七八九十]+</[^<]+><[^<]+>屆</[^<]+>")
G_getChemical2Modifier_pat = re.compile(r"<MODIFIER>[^<]+</MODIFIER><KNOWLEDGE_chemical>[^<]+</KNOWLEDGE_chemical>")

# _mergeSpecialVerbAndNoun 特殊詞合成
## 會見
G_hui4Chien4_pat = re.compile(r"<MODAL>會</MODAL><ACTION_verb>見</ACTION_verb>")
## 前景/後景
G_chien2hou4ching3_pat = re.compile(r"<RANGE_locality>[前後]</RANGE_locality><[^<]+>景</[^<]+>")


def versions() -> dict[str, str]:
    """
    回傳目前的 CNA_Articut_VERSION 和 CNA_Articut_RELEASEDATE
    """
    versions: dict[str, str] = {
        "CNA_Articut_VERSION": "0.14.1",
        "CNA_Articut_RELEASEDATE": "2025/07/28",
    }
    return versions


def parse(
    inputSTR: str,
    level: str = "lv2",
    chemicalBOOL: bool = True,
    dictDirectorySTR: str = "dict_collection",
    emojiBOOL: bool = True,
    openDataPlaceAccessBOOL: bool = False,
    wikiDataBOOL: bool = False,
    indexWithPOS: bool = False,
    timeRef: Union[Any, None] = None,
    pinyin: str = "BOPOMOFO",
    autoBreakBOOL: bool = True,
    requestID: str = "",
) -> dict:
    """
    執行斷詞
    """
    startTime: float = time.perf_counter()
    # 第一次 parse : 目的是拿出要建立成字典的知識！
    firstDICT = articut.parse(
        inputSTR=inputSTR,
        level=level,
        chemicalBOOL=chemicalBOOL,
        emojiBOOL=emojiBOOL,
        openDataPlaceAccessBOOL=openDataPlaceAccessBOOL,
        wikiDataBOOL=wikiDataBOOL,
        indexWithPOS=indexWithPOS,
        timeRef=timeRef,
        pinyin=pinyin,
        autoBreakBOOL=autoBreakBOOL,
        requestID=requestID,
    )
    # 動態建立字典
    useDICT: dict[str, list[str]] = {}

    ## articut 原生知識
    getLIST: list[list[tuple]] = []

    ### 拿 person
    getLIST = getPersonLIST(firstDICT, indexWithPOS=False)
    personLIST: list[str] = []
    if getLIST!=None:
        for get_L in getLIST:
            if len(get_L) != 0 and not _nameExcept(get_L[0][2]):
                personLIST.append(get_L[0][2])
        useDICT.update({"KNOWLEDGE_person": personLIST})

    ### 拿 AddTW
    getLIST = getAddTWLIST(firstDICT, indexWithPOS=False)
    addressTWLIST: list[str] = []
    if getLIST!=None:
        for get_L in getLIST:
            if len(get_L) != 0:
                addressTWLIST.append(get_L[0][2])
        useDICT.update({"KNOWLEDGE_TWAddress": addressTWLIST})

    ### 拿 currency
    getLIST = NER_getMoneyLIST(firstDICT, indexWithPOS=False)
    currencyLIST: list[str] = []
    if getLIST!=None:
        for get_L in getLIST:
            if len(get_L) != 0:
                currencyLIST.append(get_L[0][2])
        useDICT.update({"KNOWLEDGE_currency": currencyLIST})

    ### 拿 LOCATION
    getLIST = getLocationStemLIST(firstDICT, indexWithPOS=False)
    locationLIST: list[str] = []
    if getLIST!=None:
        for get_L in getLIST:
            if len(get_L) != 0:
                locationLIST.append(get_L[0][2])
        useDICT.update({"KNOWLEDGE_location": locationLIST})

    ### 拿 url
    getLIST = NER_getWWWLIST(firstDICT, indexWithPOS=False)
    urlLIST: list[str] = []
    if getLIST!=None:
        for get_L in getLIST:
            if len(get_L) != 0:
                urlLIST.append(get_L[0][2])
        useDICT.update({"KNOWLEDGE_url": urlLIST})

    ## CNA 字典知識
    pieceDICT: dict[str, list[str]] = createUDByGuillemets(inputSTR)
    CNAMemberDICT: dict[str, list[str]] = createCNAMemberUD(inputSTR)
    udDICT: dict[str, list[str]] = dictForger(inputSTR, dictDirectorySTR)

    useDICT.update(pieceDICT)
    useDICT.update(CNAMemberDICT)
    useDICT.update(udDICT)

    # 確認字典內容
    useDICT = dictConfirmer(inputSTR, useDICT)

    # 新增縮寫功能
    abbrDICT: dict[str, list[str]] = createAbbrUD(inputSTR, useDICT)
    if len(abbrDICT["KNOWLEDGE_abbr"])!=0:
        useDICT.update(abbrDICT)

    # 將字典建成暫存檔
    udFILE = dict2File(useDICT)

    resultDICT = articut.parse(
        inputSTR=inputSTR,
        level=level,
        userDefinedDictFILE=udFILE.name,
        chemicalBOOL=chemicalBOOL,
        emojiBOOL=emojiBOOL,
        openDataPlaceAccessBOOL=openDataPlaceAccessBOOL,
        wikiDataBOOL=wikiDataBOOL,
        indexWithPOS=indexWithPOS,
        timeRef=timeRef,
        pinyin=pinyin,
        autoBreakBOOL=autoBreakBOOL,
        requestID=requestID,
    )

    resultDICT = _splitSpecifyPerson(resultDICT)
    # resultDICT = _mergeEnglish(resultDICT)
    resultDICT = _mergeFragment(resultDICT)
    resultDICT = _tagReplacement(resultDICT, useDICT)
    resultDICT = _mergeJobTitle(resultDICT)
    resultDICT = _createCNATag(resultDICT, directorySTR=dictDirectorySTR)
    resultDICT = _normalizePOS(resultDICT)

    endTime: float = time.perf_counter()
    resultDICT["exec_time"] = endTime-startTime
    return resultDICT


def getAddTWLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    取出斷詞結果中含有 (KNOWLEDGE_addTW) 標籤的字串。 該字串為一台灣地址。
    """
    return articut.getAddTWLIST(resultDICT, indexWithPOS)


def getChemicalLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    取出斷詞結果中的化學類詞 (KNOWLEDGE_chemical)。 每個句子內的化學類詞為一個 list。
    """
    return articut.getChemicalLIST(resultDICT, indexWithPOS)


def getColorLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    取出斷詞結果中含有 (MODIFIER_color) 標籤的字串。 該字串為一顏色表述字串。
    """
    return articut.getColorLIST(resultDICT, indexWithPOS)


def getContentWordLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    取出斷詞結果中的實詞 (content word)。 每個句子內的實詞為一個 list。
    """
    return articut.getContentWordLIST(resultDICT, indexWithPOS)


def getCurrencyLIST(resultDICT: dict, indexWithPOS: bool = True, greedyBOOL: bool = False) -> list[list]:
    """
    取出斷詞結果中的貨幣金額 (KNOWLEDGE_currency) 標籤的字串。 每個句子內的「貨幣金額」，將列為一個 list。 若 greedy = True，則以下格式會加到回傳 list
    貨幣名稱 + 數字 (包含「'」與「,」符號) 新台幣 100 美金9.99 歐元 1,999'99
    """
    return articut.getCurrencyLIST(resultDICT, indexWithPOS, greedyBOOL)


def getLocationStemLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    取出斷詞結果中的地理位置 (location)。此處指的是地理位置標記的行政區地名詞彙，例如「台北」、「桃園」、「墨西哥」。 每個句子內的地理位置列為一個 list。
    """
    return articut.getLocationStemLIST(resultDICT, indexWithPOS)


def getNounStemLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    取出斷詞結果中的名詞 (noun)。此處指的是 ENTITY_noun、ENTITY_nouny、ENTITY_nounHead 或 ENTITY_oov 標記的名詞詞彙。 每個句子內的名詞為一個 list。
    """
    return articut.getNounStemLIST(resultDICT, indexWithPOS)


def getOpenDataPlaceLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    取出斷詞結果中的景點 (KNOWLEDGE_place) 標籤的字串。此處指的是景點 (KNOWLEDGE_place)標記的非行政地點名稱詞彙，例如「鹿港老街」、「宜蘭運動公園」。 每個句子內的景點為一個 list。
    """
    return articut.getOpenDataPlaceLIST(resultDICT, indexWithPOS)


def getPersonLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    取出斷詞結果中的人名 (Person) 若 includePronounBOOL 為 True，則連代名詞 (Pronoun) 一併回傳；若為 False，則只回傳人名。 回傳結果為一個 list。
    """
    return articut.getPersonLIST(resultDICT, indexWithPOS)


def getQuestionLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    取出斷詞結果中含有 (CLAUSE_Q) 標籤的句子。 此處指的是
    <CLAUSE_AnotAQ>: A-not-A 問句
    <CLAUSE_YesNoQ>: 是非問句
    <CLAUSE_WhoQ">: 「誰」問句
    <CLAUSE_WhatQ>: 「物」問句
    <CLAUSE_WhereQ>: 「何地」問句
    <CLAUSE_WhenQ>: 「何時」問句
    <CLAUSE_HowQ>: 「程度/過程」問句
    <CLAUSE_WhyQ>: 「原因」問句
    每個句子內若有 <CLAUSE_Q> 標籤，整個句子將會存進 list。
    """
    return articut.getQuestionLIST(resultDICT, indexWithPOS)


def getTimeLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    取出斷詞結果中的時間 (time)。 每個句子內的「時間」詞列為一個 list。
    """
    return articut.getTimeLIST(resultDICT, indexWithPOS)


def getVerbStemLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    取出斷詞結果中的動詞 (verb)。此處指的是 ACTION_verb 標記的動詞詞彙。 每個句子內的動詞為一個 list。
    """
    return articut.getVerbStemLIST(resultDICT, indexWithPOS)


def getWikiDataLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    取出斷詞結果中的 WikiData 標記文字。此處指的是 KNOWLEDGE_wikiData 標記的條目名稱。 每個句子內的條目名稱為一個 list。
    """
    return articut.getWikiDataLIST(resultDICT, indexWithPOS)


def NER_getAgeLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    依 MSRA (微軟亞洲研究院, Microsoft Research Lab Asia) NER 標準取出文本中的「歲數」字串
    """
    return articut.NER.getAge(resultDICT, indexWithPOS)


def NER_getAngleLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    依 MSRA (微軟亞洲研究院, Microsoft Research Lab Asia) NER 標準取出文本中的描述「角度」的字串
    """
    return articut.NER.getAngle(resultDICT, indexWithPOS)


def NER_getAreaLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    依 MSRA (微軟亞洲研究院, Microsoft Research Lab Asia) NER 標準取出文本中的描述「週邊地區」的字串
    """
    return articut.NER.getArea(resultDICT, indexWithPOS)


def NER_getCapacityLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    依 MSRA (微軟亞洲研究院, Microsoft Research Lab Asia) NER 標準取出文本中的描述「容量」的字串
    """
    return articut.NER.getCapacity(resultDICT, indexWithPOS)


def NER_getDateLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    依 MSRA (微軟亞洲研究院, Microsoft Research Lab Asia) NER 標準取出文本中的描述「日期」的字串
    """
    return articut.NER.getDate(resultDICT, indexWithPOS)


def NER_getDecimalLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    依 MSRA (微軟亞洲研究院, Microsoft Research Lab Asia) NER 標準取出文本中的描述「小數」的字串
    """
    return articut.NER.getDecimal(resultDICT, indexWithPOS)


def NER_getDurationLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    依 MSRA (微軟亞洲研究院, Microsoft Research Lab Asia) NER 標準取出文本中的描述「時間區間」的字串
    """
    return articut.NER.getDuration(resultDICT, indexWithPOS)


def NER_getEmojiLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    取出文本中的「emoji」的符號
    """
    return articut.NER.getEmoji(resultDICT, indexWithPOS)


def NER_getFoodLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    取出文本中的食物
    """
    return articut.NER.getFood(resultDICT, indexWithPOS)


def NER_getFractionLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    依 MSRA (微軟亞洲研究院, Microsoft Research Lab Asia) NER 標準取出文本中的描述「分數」的字串
    """
    return articut.NER.getFraction(resultDICT, indexWithPOS)


def NER_getFrequencyLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    依 MSRA (微軟亞洲研究院, Microsoft Research Lab Asia) NER 標準取出文本中的描述「頻率」的字串
    """
    return articut.NER.getFrequency(resultDICT, indexWithPOS)


def NER_getIntegerLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    依 MSRA (微軟亞洲研究院, Microsoft Research Lab Asia) NER 標準取出文本中的描述「整數」的字串
    """
    return articut.NER.getInteger(resultDICT, indexWithPOS)


def NER_getLengthLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    依 MSRA (微軟亞洲研究院, Microsoft Research Lab Asia) NER 標準取出文本中的描述「長度」的字串
    """
    return articut.NER.getLength(resultDICT, indexWithPOS)


def NER_getLocationLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    依 MSRA (微軟亞洲研究院, Microsoft Research Lab Asia) NER 標準取出文本中的描述「重量」的字串。
    此功能和 ArticutAPI 中的 getLoctionStemLIST() 等效。
    """
    return articut.NER.getLocation(resultDICT, indexWithPOS)


def NER_getMeasureLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    依 MSRA (微軟亞洲研究院, Microsoft Research Lab Asia) NER 標準取出文本中為「測量值」的字串
    """
    return articut.NER.getMeasure(resultDICT, indexWithPOS)


def NER_getMoneyLIST(resultDICT: dict, greedyBOOL: bool = False, indexWithPOS: bool = True) -> list[list]:
    """
    依 MSRA (微軟亞洲研究院, Microsoft Research Lab Asia) NER 標準取出文本中的描述「金額」的字串
    此功能和 ArticutAPI 中的 getCurrencyLIST() 等效。
    """
    return articut.NER.getMoney(resultDICT, greedyBOOL, indexWithPOS)


def NER_getOrdinalLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    依 MSRA (微軟亞洲研究院, Microsoft Research Lab Asia) NER 標準取出文本中的描述「序數」的字串
    """
    return articut.NER.getOrdinal(resultDICT, indexWithPOS)


def NER_getPercentLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    依 MSRA (微軟亞洲研究院, Microsoft Research Lab Asia) NER 標準取出文本中的描述「百分比/千分比/萬分比」的字串
    """
    return articut.NER.getPercent(resultDICT, indexWithPOS)


def NER_getPersonLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    依 MSRA (微軟亞洲研究院, Microsoft Research Lab Asia) NER 標準取出文本中的描述「人名」的字串
    此功能和 ArticutAPI 中的 getPersonLIST() 等效。
    取出斷詞結果中的人名 (Person)
    若 includePronounBOOL 為 True，則連代名詞 (Pronoun) 一併回傳；若為 False，則只回傳人名。
    """
    return articut.NER.getPerson(resultDICT, indexWithPOS)


def NER_getRateLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    依 MSRA (微軟亞洲研究院, Microsoft Research Lab Asia) NER 標準取出文本中的描述「比例」的字串
    """
    return articut.NER.getRate(resultDICT, indexWithPOS)


def NER_getSpeedLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    依 MSRA (微軟亞洲研究院, Microsoft Research Lab Asia) NER 標準取出文本中的描述「速度」的字串
    """
    return articut.NER.getSpeed(resultDICT, indexWithPOS)


def NER_getTemperatureLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    依 MSRA (微軟亞洲研究院, Microsoft Research Lab Asia) NER 標準取出文本中的描述「溫度」的字串
    """
    return articut.NER.getSpeed(resultDICT, indexWithPOS)


def NER_getTimeLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    依 NER 標準取出文本中的描述「時間」的字串
    """
    return articut.NER.getSpeed(resultDICT, indexWithPOS)


def NER_getWeightLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    依 MSRA (微軟亞洲研究院, Microsoft Research Lab Asia) NER 標準取出文本中的描述「重量」的字串
    """
    return articut.NER.getWeight(resultDICT, indexWithPOS)


def NER_getWWWLIST(resultDICT: dict, indexWithPOS: bool = True) -> list[list]:
    """
    依 MSRA (微軟亞洲研究院, Microsoft Research Lab Asia) NER 標準取出文本中的描述「URL 連結」的字串
    """
    return articut.NER.getWWW(resultDICT, indexWithPOS)


def lawsToolkit_getCrimeLIST(resultDICT: dict) -> list[list]:
    """
    取得罪名。
    """
    return articut.LawsToolkit.getCrime(resultDICT)


def lawsToolkit_getPenaltyLIST(resultDICT: dict) -> list[list]:
    """
    取得刑責。
    """
    return articut.LawsToolkit.getPenalty(resultDICT)


def lawsToolkit_getLawArticleLIST(resultDICT: dict) -> list[list]:
    """
    取得法條編號。
    """
    return articut.LawsToolkit.getLawArticle(resultDICT)


def localRE_getAddressCountyLIST(
    resultDICT: dict, indexWithPOS: bool = True
) -> list[list]:
    """
    取出 Articut 斷詞結果中標記取出是哪個「縣」。
    """
    return articut.localRE.getAddressCounty(resultDICT, indexWithPOS)


def localRE_getAddressCityLIST(
    resultDICT: dict, indexWithPOS: bool = True
) -> list[list]:
    """
    取出 Articut 斷詞結果中標記取出是哪個「市」。
    """
    return articut.localRE.getAddressCity(resultDICT, indexWithPOS)


def localRE_getAddressDistrictLIST(
    resultDICT: dict, indexWithPOS: bool = True
) -> list[list]:
    """
    取出 Articut 斷詞結果中標記取出是哪個「區」。
    """
    return articut.localRE.getAddressDistrict(resultDICT, indexWithPOS)


def localRE_getAddressTownshipLIST(
    resultDICT: dict, indexWithPOS: bool = True
) -> list[list]:
    """
    取出 Articut 斷詞結果中標記取出是哪個「鄉」或「里」。
    """
    return articut.localRE.getAddressTownship(resultDICT, indexWithPOS)


def localRE_getAddressTownLIST(
    resultDICT: dict, indexWithPOS: bool = True
) -> list[list]:
    """
    取出 Articut 斷詞結果中標記取出是哪個「鎮」。
    """
    return articut.localRE.getAddressTown(resultDICT, indexWithPOS)


def localRE_getAddressVillageLIST(
    resultDICT: dict, indexWithPOS: bool = True
) -> list[list]:
    """
    取出 Articut 斷詞結果中標記取出是哪個「村」。
    """
    return articut.localRE.getAddressVillage(resultDICT, indexWithPOS)


def localRE_getAddressNeighborhoodLIST(
    resultDICT: dict, indexWithPOS: bool = True
) -> list[list]:
    """
    取出 Articut 斷詞結果中標記取出是哪個「鄰」。
    """
    return articut.localRE.getAddressNeighborhood(resultDICT, indexWithPOS)


def localRE_getAddressRoadLIST(
    resultDICT: dict, indexWithPOS: bool = True
) -> list[list]:
    """
    取出 Articut 斷詞結果中標記取出是哪條「路」。
    """
    return articut.localRE.getAddressRoad(resultDICT, indexWithPOS)


def localRE_getAddressSectionLIST(
    resultDICT: dict, indexWithPOS: bool = True
) -> list[list]:
    """
    取出 Articut 斷詞結果中標記取出是哪一「段」。
    """
    return articut.localRE.getAddressSection(resultDICT, indexWithPOS)


def localRE_getAddressAlleyLIST(
    resultDICT: dict, indexWithPOS: bool = True
) -> list[list]:
    """
    取出 Articut 斷詞結果中標記取出是哪一「巷」或「弄」。
    """
    return articut.localRE.getAddressAlley(resultDICT, indexWithPOS)


def localRE_getAddressNumberLIST(
    resultDICT: dict, indexWithPOS: bool = True
) -> list[list]:
    """
    取出 Articut 斷詞結果中標記取出是幾「號」。
    """
    return articut.localRE.getAddressNumber(resultDICT, indexWithPOS)


def localRE_getAddressFloorLIST(
    resultDICT: dict, indexWithPOS: bool = True
) -> list[list]:
    """
    取出 Articut 斷詞結果中標記取出是幾「樓」。
    """
    return articut.localRE.getAddressFloor(resultDICT, indexWithPOS)


def localRE_getAddressRoomLIST(
    resultDICT: dict, indexWithPOS: bool = True
) -> list[list]:
    """
    取出 Articut 斷詞結果中標記取出「室」的編號。
    """
    return articut.localRE.getAddressRoom(resultDICT, indexWithPOS)


def _tagReplacement(resultDICT: dict, myDICT: dict[str, list[str]]) -> dict:
    """
    將 userdefined的詞語 tag 換成 <KNOWLEDGE_xxx> 的格式。
    """
    # 更改 result_obj
    ## 一般字典
    for sentencesLIST in resultDICT["result_obj"]:
        for wordDICT in sentencesLIST:
            if wordDICT["pos"] == "UserDefined":
                wordDICT["pos"] = findExactDictionary(wordDICT["text"], myDICT)

    # 更改 result_pos
    resultDICT["result_pos"] = _getResultPosByResultObj(resultDICT["result_obj"])

    return resultDICT


def _getResultObjByResultPos(resultPos: list[str]) -> list[list[dict[str, str]]]:
    """
    經由 resultPos 得到對應的 resultObj
    """
    newResultObj: list[list[dict]] = []
    for sentence_S in resultPos:
        sentenceLIST: list[dict] = []
        itemLIST: list[tuple[str, str]] = [
            x.groups() for x in G_extracTagAndText_pat.finditer(sentence_S)
        ]

        if len(itemLIST) == 0:
            itemDICT: dict[str, str] = {}
            itemDICT["pos"] = "PUNCTUATION"
            itemDICT["text"] = sentence_S
            sentenceLIST.append(itemDICT)
            newResultObj.append(sentenceLIST)
            continue

        for item_T in itemLIST:
            itemDICT: dict[str, str] = {}
            itemDICT["pos"] = item_T[0]
            itemDICT["text"] = item_T[1]
            sentenceLIST.append(itemDICT)

        newResultObj.append(sentenceLIST)

    return newResultObj


def _getResultSegmentationByResultPos(resultPos: list[str]) -> list[str]:
    """
    經由 resultPos 得到對應的 resultSegmentation
    """
    newResultSegmentation: list[str] = []
    for sentence_S in resultPos:
        nameLIST: list[str] = re.findall(r"<[a-zA-Z]", sentence_S)
        if len(nameLIST) == 0:
            newResultSegmentation.append(sentence_S)
            continue

        newSentenceSTR: str = re.sub(G_extractText_pat, "/", sentence_S)
        newSentenceSTR = newSentenceSTR.replace("//", "/")
        newSentenceSTR = newSentenceSTR.strip("/")
        newResultSegmentation.append(newSentenceSTR)

    return newResultSegmentation


def _getResultPosByResultObj(resultObj: list[list[dict[str, str]]]) -> list[str]:
    """
    經由 resultObj 得到對應的 resultPos
    """
    newResultPosLIST: list[str] = []
    for sentences_L in resultObj:
        sentenceSTR: str = ""
        for word_D in sentences_L:
            if word_D["pos"] == "PUNCTUATION":
                sentenceSTR += word_D["text"]
            else:
                sentenceSTR += "<"
                sentenceSTR += word_D["pos"]
                sentenceSTR += ">"
                sentenceSTR += word_D["text"]
                sentenceSTR += "<"
                endTag: str = word_D["pos"][:0] + "/" + word_D["pos"][0:]
                sentenceSTR += endTag
                sentenceSTR += ">"

        newResultPosLIST.append(sentenceSTR)

    return newResultPosLIST


def _createCNATag(resultDICT: dict, directorySTR: str) -> dict:
    """
    新增一個 Key 為 CNATAG，將所有該文本中使用到的 <KNOWLEDGE_xxx> 紀錄於此。
    <KNOWLEDGE_xxx> 會經過檢查，一律輸出該筆內容的 key。
    """
    CNATag: dict[str, dict[str, list[str]]] = {}
    KNOWLEDGE_pat = r"(KNOWLEDGE_.*|.*_dict)"

    for sentenceLIST in resultDICT["result_obj"]:
        for wordDICT in sentenceLIST:
            posSTR = wordDICT["pos"]
            textSTR = wordDICT["text"]

            match: Union[(re.Match[str]), (None)] = re.search(KNOWLEDGE_pat, posSTR)

            if match:
                entryDICT: dict[str, list[str]] = _getEntry(posSTR, textSTR, directorySTR)

                if posSTR not in CNATag:
                    CNATag[posSTR] = {}

                CNATag[posSTR].update(entryDICT)

    resultDICT["CNA_tag"] = CNATag
    return resultDICT

def _normalizePOS(resultDICT: dict) -> dict:
    """
    正規化 LOCATION
    """
    for sentencesLIST in resultDICT["result_obj"]:
        for wordDICT in sentencesLIST:
            if wordDICT["pos"] == "LOCATION":
                wordDICT["pos"] = "KNOWLEDGE_location"

    # 更改 result_pos
    resultDICT["result_pos"] = _getResultPosByResultObj(resultDICT["result_obj"])

    return resultDICT

def _nameExcept(nameSTR: str) -> bool:
    """
    是否該排除此人名作為 person。
    如：向美方 -> true
    """
    nameLIST: list[str] = [x.groups() for x in G_nameExcept_pat.finditer(nameSTR)]
    if len(nameLIST) != 0:
        return True
    return False

def _splitSpecifyPerson(resultDICT: dict) -> dict:
    """
    檢查標記為 Person 的 entity，若符合特定格式，拆開。
    如：<ENTITY_person>向美方</ENTITY_person> -> <FUNC_inner>向</FUNC_inner><ENTITY_noun>美方</<ENTITY_noun>>
    """
    newResultPosLIST: list[str] = _addSymbolToPunc(resultDICT["result_pos"])
    joinSTR: str = "".join(newResultPosLIST)

    ### 找到結構
    personLIST = [x.group() for x in G_splitSpecifyPerson_pat.finditer(joinSTR)]

    if len(personLIST)==0:
        return resultDICT

    ### 合成新結構
    newPersonLIST = []
    for structure in personLIST:
        struLIST: list[str] = [x.group() for x in G_getText_pat.finditer(structure)]
        newPersonLIST.append("<FUNC_inner>向</FUNC_inner><ENTITY_noun>" + str(struLIST[0][1:]) + "</ENTITY_noun>")

    ### 代替原結構
    for i in range(len(personLIST)):
        joinSTR = re.sub(personLIST[i], newPersonLIST[i], joinSTR)

    # 根據新的 result_pos 修改 result_segmentation & result_obj
    resultPosLIST: list[str] = _splitResultPosSTR(joinSTR)
    resultDICT["result_pos"] = resultPosLIST
    resultDICT["result_obj"] = _getResultObjByResultPos(resultPosLIST)
    resultDICT["result_segmentation"] = _getResultSegmentationByResultPos(resultPosLIST)

    return resultDICT


def _mergeEnglish(resultDICT: dict) -> dict:
    print(resultDICT["result_pos"])
    joinSTR: str = "".join(resultDICT["result_pos"])
    print(joinSTR)
    # mergeEngSTR: str = G_mergeEnglish_pat.sub(" ", joinSTR)
    # newResultPOSLIST: list[str] = re.split(r"(?<=>).(?=<)", mergeEngSTR)
    # print(newResultPOSLIST)

    # resultDICT["result_pos"] = newResultPOSLIST
    # resultDICT["result_obj"] = _getResultObjByResultPos(newResultPOSLIST)
    # resultDICT["result_segmentation"] = _getResultSegmentationByResultPos(
    #     newResultPOSLIST
    # )

    return resultDICT

def _mergeFragment(resultDICT: dict) -> dict:
    """
    合併 MODIFIER_color、quantifier(全、半、都)、RANGE_locality
    """
    resultDICT = _mergeByInterpunct(resultDICT)
    resultDICT = _mergeQuantifier(resultDICT)
    resultDICT = _mergeColor(resultDICT)
    resultDICT = _mergeSpecialVerbAndNoun(resultDICT)
    resultDICT = _mergeVerbObjectStructure(resultDICT)
    resultDICT = _mergeCountry(resultDICT)
    resultDICT = _mergeCountryAbbr(resultDICT)
    resultDICT = _mergeMediaTerm(resultDICT)
    resultDICT = _mergeUnit2Num(resultDICT)
    resultDICT = _mergeChemical2Modifier(resultDICT)
    resultDICT = _mergeLocality(resultDICT)

    return resultDICT

def _mergeByInterpunct(resultDICT: dict) -> dict:
    """
    將 articut 斷詞結果後處理。若遇到分隔號，則將前後元素合併。
    """
    newResultPosLIST: list[str] = _addSymbolToPunc(resultDICT["result_pos"])
    joinSTR: str = "".join(newResultPosLIST)

    ## 找分隔號結構。
    patternLIST: list[tuple[str, str]] = [
        x.groups() for x in G_mergeByInterpunct_pat.finditer(joinSTR)
    ]
    replacePatternLIST: list[str] = []
    if len(patternLIST) == 0:
        return resultDICT

    ## 對分隔號結構做精簡，取出之後要用的分隔號。
    for pattern_T in patternLIST:
        interpunct_S: str = G_getTag_pat.sub("", pattern_T[0])
        replacePatternLIST.append(interpunct_S)

    ## 對每個分隔號結構做取代，取代成分隔號。
    for i in range(len(patternLIST)):
        joinSTR = re.sub(patternLIST[i][0], replacePatternLIST[i], joinSTR)

    resultPosLIST: list[str] = _splitResultPosSTR(joinSTR)

    # 萃取出新的 result_obj、result_pos_result_segmentation
    resultDICT["result_pos"] = resultPosLIST
    resultDICT["result_obj"] = _getResultObjByResultPos(resultPosLIST)
    resultDICT["result_segmentation"] = _getResultSegmentationByResultPos(resultPosLIST)

    return resultDICT

def _mergeQuantifier(resultDICT: dict) -> dict:
    """
    合併 QUANTIFIER 中全、半、都與其後方合適的詞(1個音節)
    """
    # 處理標籤

    ## join result_pos
    newResultPosLIST: list[str] = _addSymbolToPunc(resultDICT["result_pos"])
    joinSTR: str = "".join(newResultPosLIST)

    ## 找結構。
    patternLIST: list[str] = [x.group() for x in G_getQuantifierGroup_pat.finditer(joinSTR)]
    if len(patternLIST)==0:
        return resultDICT

    ## 精簡結構，取出之後要用的素材。
    nameLIST: list[str] = []
    tagLIST: list[list[tuple[str, str]]] = []
    for pattern_S in patternLIST:
        tmpLIST: list[tuple[str, str]] = [x.groups() for x in G_getText_pat.finditer(pattern_S)]
        nameSTR: str = ""
        for name_T in tmpLIST:
            nameSTR= nameSTR + name_T[0]

        nameLIST.append(nameSTR)
        tagLIST.append([x.groups() for x in G_getAfterQuantifier_pat.finditer(pattern_S)])

    ## 合成新結構
    replaceLIST: list[str] = []
    for i in range(len(tagLIST)):
        replaceLIST.append("<" + tagLIST[i][0][0] + ">" + nameLIST[i] + "</" + tagLIST[i][0][0] + ">")

    ## 以新結構取代原結構
    for i in range(len(patternLIST)):
        joinSTR = re.sub(patternLIST[i], replaceLIST[i], joinSTR)

    resultPosLIST: list[str] = _splitResultPosSTR(joinSTR)

    # 更新 result_pos、 result_obj 和 result_segmentation
    resultDICT["result_pos"] = resultPosLIST
    resultDICT["result_obj"] = _getResultObjByResultPos(resultPosLIST)
    resultDICT["result_segmentation"] = _getResultSegmentationByResultPos(resultPosLIST)

    return resultDICT

def _mergeColor(resultDICT: dict) -> dict:
    """
    合併 MODIFIER_color 與其後方合適的詞(2個音節)
    """
    # 處理 color
    ## join result_pos
    newPosLIST: list[str] = _addSymbolToPunc(resultDICT["result_pos"])
    joinSTR: str = "".join(newPosLIST)

    ## 找結構。
    patternLIST: list[str] = [x.group() for x in G_getColorGroup_pat.finditer(joinSTR)]
    if len(patternLIST)==0:
        return resultDICT

    ## 精簡結構，取出之後要用的素材。
    nameLIST: list[str] = []
    tagLIST: list[list[tuple[str, str]]] = []
    for pattern_S in patternLIST:
        tmpLIST: list[tuple[str, str]] = [x.groups() for x in G_getText_pat.finditer(pattern_S)]
        nameSTR: str = ""
        for name_T in tmpLIST:
            nameSTR= nameSTR + name_T[0]

        nameLIST.append(nameSTR)
        tagLIST.append([x.groups() for x in G_getAfterColor_pat.finditer(pattern_S)])

    ## 合成新結構
    replaceLIST: list[str] = []
    for i in range(len(tagLIST)):
        replaceLIST.append("<" + tagLIST[i][0][0] + ">" + nameLIST[i] + "</" + tagLIST[i][0][0] + ">")

    ## 以新結構取代原結構
    for i in range(len(patternLIST)):
        joinSTR = re.sub(patternLIST[i], replaceLIST[i], joinSTR)

    resultPosLIST: list[str] = _splitResultPosSTR(joinSTR)

    # 更新 result_pos、 result_obj 和 result_segmentation
    resultDICT["result_pos"] = resultPosLIST
    resultDICT["result_obj"] = _getResultObjByResultPos(resultPosLIST)
    resultDICT["result_segmentation"] = _getResultSegmentationByResultPos(resultPosLIST)

    return resultDICT

def _mergeSpecialVerbAndNoun(resultDICT: dict) -> dict:
    """
    合成不適合在 Articut 底層處理的詞
    e.g.：會見(中古漢語)
    """
    # 遍歷檢查 result_pos
    newPosLIST: list[str] = _addSymbolToPunc(resultDICT["result_pos"])
    joinSTR: str = "".join(newPosLIST)

    ## 處理動詞
    ### 找到結構
    hui4Chien4LIST: list[str] = [x.group() for x in G_hui4Chien4_pat.finditer(joinSTR)]

    if len(hui4Chien4LIST)!=0:
        ### 合成新結構
        newHui4Chien4LIST = []
        for structure in hui4Chien4LIST:
            struLIST: list[str] = [x.group() for x in G_getText_pat.finditer(structure)]
            struSTR: str = "".join(struLIST)
            newHui4Chien4LIST.append("<ACT_verb>" + struSTR + "</ACT_verb>")

        ### 代替原結構
        for i in range(len(hui4Chien4LIST)):
            joinSTR = re.sub(hui4Chien4LIST[i], newHui4Chien4LIST[i], joinSTR)

    ## 處理名詞
    ### 找到結構
    chien2hou4ching3LIST: list[str] = [x.group() for x in G_chien2hou4ching3_pat.finditer(joinSTR)]

    if len(chien2hou4ching3LIST)!=0:
        ### 合成新結構
        newChien2hou4ching3LIST = []
        for structure in chien2hou4ching3LIST:
            struLIST: list[str] = [x.group() for x in G_getText_pat.finditer(structure)]
            struSTR: str = "".join(struLIST)
            newChien2hou4ching3LIST.append("<ENTY_noun>" + struSTR + "</ENTY_noun>")

        ### 代替原結構
        for i in range(len(chien2hou4ching3LIST)):
            joinSTR = re.sub(chien2hou4ching3LIST[i], newChien2hou4ching3LIST[i], joinSTR)

    # 根據新的 result_pos 修改 result_segmentation & result_obj
    resultPosLIST: list[str] = _splitResultPosSTR(joinSTR)
    resultDICT["result_pos"] = resultPosLIST
    resultDICT["result_obj"] = _getResultObjByResultPos(resultPosLIST)
    resultDICT["result_segmentation"] = _getResultSegmentationByResultPos(resultPosLIST)

    return resultDICT

def _mergeLocality(resultDICT: dict) -> dict:
    """
    合併合適的詞與其後方的 RANGE_locality 
    """
    # 處理 RANGE_locality

    ## join result_pos
    newPosLIST: list[str] = _addSymbolToPunc(resultDICT["result_pos"])
    joinSTR: str = "".join(newPosLIST)

    ## 找結構。
    patternLIST: list[str] = [x.group() for x in G_getLocalityGroup_pat.finditer(joinSTR)]
    if len(patternLIST)==0:
        return resultDICT

    ## 精簡結構，取出之後要用的素材。
    nameLIST: list[str] = []
    tagLIST: list[list[tuple[str, str]]] = []
    for pattern_S in patternLIST:
        tmpLIST: list[tuple[str, str]] = [x.groups() for x in G_getText_pat.finditer(pattern_S)]
        nameSTR: str = ""
        for name_T in tmpLIST:
            nameSTR= nameSTR + name_T[0]

        nameLIST.append(nameSTR)
        tagLIST.append([x.groups() for x in G_getAfterLocality_pat.finditer(pattern_S)])

    ## 合成新結構
    replaceLIST: list[str] = []
    for i in range(len(tagLIST)):
        replaceLIST.append("<" + tagLIST[i][0][0] + ">" + nameLIST[i] + "</" + tagLIST[i][0][0] + ">")

    ## 以新結構取代原結構
    for i in range(len(patternLIST)):
        joinSTR = re.sub(patternLIST[i], replaceLIST[i], joinSTR)

    resultPosLIST: list[str] = _splitResultPosSTR(joinSTR)

    # 更新 result_pos、 result_obj 和 result_segmentation
    resultDICT["result_pos"] = resultPosLIST
    resultDICT["result_obj"] = _getResultObjByResultPos(resultPosLIST)
    resultDICT["result_segmentation"] = _getResultSegmentationByResultPos(resultPosLIST)

    return resultDICT

def _mergeVerbObjectStructure(resultDICT: dict) -> dict:
    """
    VerbObjectStructure：動賓結構，標記 POS 為 ACT_intlRelation 或 進一步合成 ENTY_intlRelation
    如：[抗反返親仇友挺愛毀賣知傾滅排助聯援制][台臺英法德俄泰韓美中共澳越日朝星紐馬菲義華瓜帛烏荷以阿緬波布蒲喀象埃港厄衣甘加肯賴摩莫納奈盧聖塞獅索史坦突辛亞巴孟汶柬賽喬伊約哈黎蒙尼沙斯敘塔土奧比保克芬匈拉印葡羅西哥薩宏牙墨玻蓋秘委斐吉諾吐]
    """
    # 遍歷檢查 result_pos
    newPosLIST: list[str] = _addSymbolToPunc(resultDICT["result_pos"])
    joinSTR: str = "".join(newPosLIST)

    ## 被斷成兩半的結構，合起來。如：抗/中 -> 抗中。並和所有屬於上述動賓結構的範例一同修改 POS 為 ACT_intlRelation。
    ### 找到結構
    verbPLIST: list[str] = [x.group() for x in G_getVerbObjectStructure_pat.finditer(joinSTR)]

    if len(verbPLIST)!=0:
        ### 合成新結構
        newVerbPLIST: list[str] = []
        for structure in verbPLIST:
            struLIST: list[str] = [x.group() for x in G_getText_pat.finditer(structure)]
            struSTR: str = "".join(struLIST)
            newVerbPLIST.append("<ACT_intlRelation>" + struSTR + "</ACT_intlRelation>")

        ### 代替原結構
        for i in range(len(verbPLIST)):
            joinSTR = re.sub(verbPLIST[i], newVerbPLIST[i], joinSTR)

    ## 額外處理特殊名詞(單國)，合起來。如：抗x/元素、抗/x元素 合起來，POS 設成 ENTITY_intlRelation
    ### 找到結構
    verbPLIST = [x.group() for x in G_getVerbObjectStructurePhrase_pat.finditer(joinSTR)]

    ### 合成新結構
    newVerbPLIST = []
    for structure in verbPLIST:
        struLIST: list[str] = [x.group() for x in G_getText_pat.finditer(structure)]
        struSTR: str = "".join(struLIST)
        newVerbPLIST.append("<ENTY_intlRelation>" + struSTR + "</ENTY_intlRelation>")

    ### 代替原結構
    for i in range(len(verbPLIST)):
        joinSTR = re.sub(verbPLIST[i], newVerbPLIST[i], joinSTR)

    ## 額外處理特殊名詞(多國)，合起來，POS 延續後方詞彙。如：抗X/Y軍 -> 抗XY軍
    ### 找到結構
    verbPLIST = [x.group() for x in G_getVerbObjectStructurePhraseCountries_pat.finditer(joinSTR)]

    ### 合成新結構
    newVerbPLIST = []
    for structure in verbPLIST:
        struLIST: list[str] = [x.group() for x in G_getText_pat.finditer(structure)]
        struSTR: str = "".join(struLIST)
        newVerbPLIST.append("<ENTY_intlRelation>" + struSTR + "</ENTY_intlRelation>")

    ### 代替原結構
    for i in range(len(verbPLIST)):
        joinSTR = re.sub(verbPLIST[i], newVerbPLIST[i], joinSTR)

    # 根據新的 result_pos 修改 result_segmentation & result_obj
    resultPosLIST: list[str] = _splitResultPosSTR(joinSTR)
    resultDICT["result_pos"] = resultPosLIST
    resultDICT["result_obj"] = _getResultObjByResultPos(resultPosLIST)
    resultDICT["result_segmentation"] = _getResultSegmentationByResultPos(resultPosLIST)

    return resultDICT

def _mergeCountry(resultDICT: dict) -> dict:
    """
    將多個國家拼在一起，標記 POS 為 ENTY_countries
    如：日/美澳/印 -> 日美澳印；日美澳/印 -> 日美澳印
    """
    # 遍歷檢查 result_pos
    newPosLIST: list[str] = _addSymbolToPunc(resultDICT["result_pos"])
    joinSTR: str = "".join(newPosLIST)

    ## 把國家合起來，如：美/日中 -> 美日中，POS 設成 ENTY_countries
    ### 找到結構
    countryLIST: list[str] = [x.group() for x in G_getCountry_pat.finditer(joinSTR)]

    if len(countryLIST)==0:
        return resultDICT

    ### 合成新結構
    newCountryLIST: list[str] = []
    for structure in countryLIST:
        struLIST: list[str] = [x.group() for x in G_getText_pat.finditer(structure)]
        struSTR: str = "".join(struLIST)
        newCountryLIST.append("<ENTY_countries>" + struSTR + "</ENTY_countries>")

    ### 代替原結構
    for i in range(len(countryLIST)):
        joinSTR = re.sub(countryLIST[i], newCountryLIST[i], joinSTR)

    ## 額外處理特殊名詞，如：中日/大戰 -> 中日大戰，POS 設成 ENTY_intlRelation
    ### 找到結構
    countryLIST = [x.group() for x in G_getCountryPhrase_pat.finditer(joinSTR)]

    ### 合成新結構
    newCountryLIST = []
    for structure in countryLIST:
        struLIST: list[str] = [x.group() for x in G_getText_pat.finditer(structure)]
        struSTR: str = "".join(struLIST)
        newCountryLIST.append("<ENTY_intlRelation>" + struSTR + "</ENTY_intlRelation>")

     ### 代替原結構
    for i in range(len(countryLIST)):
        joinSTR = re.sub(countryLIST[i], newCountryLIST[i], joinSTR)

    # 根據新的 result_pos 修改 result_segmentation & result_obj
    resultPosLIST: list[str] = _splitResultPosSTR(joinSTR)
    resultDICT["result_pos"] = resultPosLIST
    resultDICT["result_obj"] = _getResultObjByResultPos(resultPosLIST)
    resultDICT["result_segmentation"] = _getResultSegmentationByResultPos(resultPosLIST)

    return resultDICT

def _mergeCountryAbbr(resultDICT: dict) -> dict:
    """
    將國家和名詞拼在一起，標記 POS 為 ENTY_countryAbbr
    如：[英法德俄泰韓美中...秘委斐吉諾吐][媒軍籍方府裔股商資生企國]
    """
    # 遍歷檢查 result_pos
    newPosLIST: list[str] = _addSymbolToPunc(resultDICT["result_pos"])
    joinSTR: str = "".join(newPosLIST)

    ## 把國家合起來，如：美/日中 -> 美日中，POS 設成 ENTY_countryAbbr
    ### 找到結構
    countryAbbrLIST: list[str] = [x.group() for x in G_getCountryAbbr_pat.finditer(joinSTR)]

    if len(countryAbbrLIST)==0:
        return resultDICT

    ### 合成新結構
    newCountryAbbrLIST = []
    for structure in countryAbbrLIST:
        struLIST: list[str] = [x.group() for x in G_getText_pat.finditer(structure)]
        struSTR: str = "".join(struLIST)
        newCountryAbbrLIST.append("<ENTY_countryAbbr>" + struSTR + "</ENTY_countryAbbr>")

    ### 代替原結構
    for i in range(len(countryAbbrLIST)):
        joinSTR = re.sub(countryAbbrLIST[i], newCountryAbbrLIST[i], joinSTR)

    # 根據新的 result_pos 修改 result_segmentation & result_obj
    resultPosLIST: list[str] = _splitResultPosSTR(joinSTR)
    resultDICT["result_pos"] = resultPosLIST
    resultDICT["result_obj"] = _getResultObjByResultPos(resultPosLIST)
    resultDICT["result_segmentation"] = _getResultSegmentationByResultPos(resultPosLIST)

    return resultDICT

def _mergeMediaTerm(resultDICT: dict) -> dict:
    """
    合成新聞用語中關於政治的部分，標記 POS 為 ENTY_political
    如：[藍綠白][營委]
    """
    # 遍歷檢查 result_pos
    newPosLIST: list[str] = _addSymbolToPunc(resultDICT["result_pos"])
    joinSTR: str = "".join(newPosLIST)

    ## 把新聞用語合起來，如：藍/營 -> 藍營，POS 設成 ENTY_political
    ### 找到結構
    mediaTermLIST: list[str] = [x.group() for x in G_getMediaTerm_pat.finditer(joinSTR)]

    if len(mediaTermLIST)==0:
        return resultDICT

    ### 合成新結構
    newMediaTermLIST = []
    for structure in mediaTermLIST:
        struLIST: list[str] = [x.group() for x in G_getText_pat.finditer(structure)]
        struSTR: str = "".join(struLIST)
        newMediaTermLIST.append("<ENTY_political>" + struSTR + "</ENTY_political>")

    ### 代替原結構
    for i in range(len(mediaTermLIST)):
        joinSTR = re.sub(mediaTermLIST[i], newMediaTermLIST[i], joinSTR)

    # 根據新的 result_pos 修改 result_segmentation & result_obj
    resultPosLIST: list[str] = _splitResultPosSTR(joinSTR)
    resultDICT["result_pos"] = resultPosLIST
    resultDICT["result_obj"] = _getResultObjByResultPos(resultPosLIST)
    resultDICT["result_segmentation"] = _getResultSegmentationByResultPos(resultPosLIST)

    return resultDICT

def _mergeUnit2Num(resultDICT: dict) -> dict:
    """
    將被切開的單位和前方數字合成
    e.g. 第22/屆 -> 第22屆
    """
    # 遍歷檢查 result_pos
    newPosLIST: list[str] = _addSymbolToPunc(resultDICT["result_pos"])
    joinSTR: str = "".join(newPosLIST)

    ## 把單位和數字合起來，如：第22/屆 -> 第22屆，POS 設成 ENTITY_DetPhrase
    ### 找到結構
    unit2NumLIST: list[str] = [x.group() for x in G_getUnit2Num_pat.finditer(joinSTR)]

    if len(unit2NumLIST)==0:
        return resultDICT

    ### 合成新結構
    newUnit2NumLIST = []
    for structure in unit2NumLIST:
        struLIST: list[str] = [x.group() for x in G_getText_pat.finditer(structure)]
        struSTR: str = "".join(struLIST)
        newUnit2NumLIST.append("<ENTITY_DetPhrase>" + struSTR + "</ENTITY_DetPhrase>")

    ### 代替原結構
    for i in range(len(unit2NumLIST)):
        joinSTR = re.sub(unit2NumLIST[i], newUnit2NumLIST[i], joinSTR)

    # 根據新的 result_pos 修改 result_segmentation & result_obj
    resultPosLIST: list[str] = _splitResultPosSTR(joinSTR)
    resultDICT["result_pos"] = resultPosLIST
    resultDICT["result_obj"] = _getResultObjByResultPos(resultPosLIST)
    resultDICT["result_segmentation"] = _getResultSegmentationByResultPos(resultPosLIST)

    return resultDICT

def _mergeChemical2Modifier(resultDICT: dict) -> dict:
    """
    將化學元素和其前方的形容詞/副詞合併。
    e.g. 高/鈣 -> 高鈣
    """
    # 遍歷檢查 result_pos
    newPosLIST: list[str] = _addSymbolToPunc(resultDICT["result_pos"])
    joinSTR: str = "".join(newPosLIST)

    ## 把化學元素和其前方的形容詞/副詞合起來，如：高/鈣 -> 高鈣，POS 設成 ENTY_chemicalPattern
    ### 找到結構
    chemical2ModifierLIST: list[str] = [x.group() for x in G_getChemical2Modifier_pat.finditer(joinSTR)]

    if len(chemical2ModifierLIST)==0:
        return resultDICT

    ### 合成新結構
    newChemical2ModifierLIST = []
    for structure in chemical2ModifierLIST:
        struLIST: list[str] = [x.group() for x in G_getText_pat.finditer(structure)]
        struSTR: str = "".join(struLIST)
        newChemical2ModifierLIST.append("<ENTY_chemicalPattern>" + struSTR + "</ENTY_chemicalPattern>")

    ### 代替原結構
    for i in range(len(chemical2ModifierLIST)):
        joinSTR = re.sub(chemical2ModifierLIST[i], newChemical2ModifierLIST[i], joinSTR)

    # 根據新的 result_pos 修改 result_segmentation & result_obj
    resultPosLIST: list[str] = _splitResultPosSTR(joinSTR)
    resultDICT["result_pos"] = resultPosLIST
    resultDICT["result_obj"] = _getResultObjByResultPos(resultPosLIST)
    resultDICT["result_segmentation"] = _getResultSegmentationByResultPos(resultPosLIST)

    return resultDICT

def _mergeJobTitle(resultDICT: dict) -> dict:
    """
    合成工作單位和職稱，標記 POS 為 KNOWLEDGE_jobTitle
    如：教育局/長 -> 教育局長
    """
    # 遍歷檢查 result_pos
    newPosLIST: list[str] = _addSymbolToPunc(resultDICT["result_pos"])
    joinSTR: str = "".join(newPosLIST)

    ## 把工作單位和職稱合起來，如：教育局/長 -> 教育局長，POS 設為 KNOWLEDGE_jobTitle
    ### 找到結構
    jobTitleLIST: list[str] = [x.group() for x in G_getJobTitle_pat.finditer(joinSTR)]

    if len(jobTitleLIST)!=0:
        ### 合成新結構
        newJobTitleLIST: list[str] = []
        for structure in jobTitleLIST:
            struLIST: list[str] = [x.group() for x in G_getText_pat.finditer(structure)]
            struSTR: str = "".join(struLIST)
            newJobTitleLIST.append("<KNOWLEDGE_jobTitle>" + struSTR + "</KNOWLEDGE_jobTitle>")

        ### 代替原結構
        for i in range(len(jobTitleLIST)):
            joinSTR = re.sub(jobTitleLIST[i], newJobTitleLIST[i], joinSTR)

    ## 若原本斷詞結果就是 xx局長 ，將其 POS 一律改為 KNOWLEDGE_jobTitle
    ### 找到結構
    jobTitleLIST = [x.group() for x in G_getJobTitlePhrase_pat.finditer(joinSTR)]

    if len(jobTitleLIST) != 0:
        ### 合成新結構
        newJobTitleLIST: list[str] = []
        for structure in jobTitleLIST:
            struLIST: list[str] = [x.group() for x in G_getText_pat.finditer(structure)]
            struSTR: str = "".join(struLIST)
            newJobTitleLIST.append("<KNOWLEDGE_jobTitle>" + struSTR + "</KNOWLEDGE_jobTitle>")

        ### 代替原結構
        for i in range(len(jobTitleLIST)):
            joinSTR = re.sub(jobTitleLIST[i], newJobTitleLIST[i], joinSTR)

    # 根據新的 result_pos 修改 result_segmentation & result_obj
    resultPosLIST: list[str] = _splitResultPosSTR(joinSTR)
    resultDICT["result_pos"] = resultPosLIST
    resultDICT["result_obj"] = _getResultObjByResultPos(resultPosLIST)
    resultDICT["result_segmentation"] = _getResultSegmentationByResultPos(resultPosLIST)

    return resultDICT

def _splitResultPosSTR(joinSTR: str) -> list[str]:
    joinSTR = joinSTR.replace("↭↭", "↭")
    return joinSTR.split("↭")

def _addSymbolToPunc(resultPosLIST: list[str]) -> list[str]:
    """
    將標點符號的前後都新增一個 ↭ ，以便後續切開。
    """
    newResultPosLIST: list[str] = []

    for i in range(len(resultPosLIST)):
        newSentenceSTR: str = ""
        if len(resultPosLIST[i]) == 1:
            if i==0:
                newSentenceSTR = resultPosLIST[i] + "↭"
            elif i==len(resultPosLIST)-1:
                newSentenceSTR = "↭" + resultPosLIST[i]
            else:
                newSentenceSTR = "↭"+ resultPosLIST[i] + "↭"

        else:
            newSentenceSTR = resultPosLIST[i]

        newResultPosLIST.append(newSentenceSTR)

    return newResultPosLIST