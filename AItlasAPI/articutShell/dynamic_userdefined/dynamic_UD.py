#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import itertools
import json
import math
import os
import platform
import re
import tempfile
from collections import Counter
from pathlib import Path
from pprint import pprint

from ArticutAPI import Articut

currentDir = Path(os.path.dirname(os.path.abspath(__file__)))
accountFilePath = os.path.join(currentDir.parent, "login.info")

# 確保 abrv 目錄和相關文件存在
abrv_dir = currentDir / "abrv"
if not abrv_dir.exists(): # 純粹確保 abrv 目錄存在 不會報錯正確斷詞
    os.makedirs(abrv_dir, exist_ok=True)
    print(f"Created abrv directory at {abrv_dir}")

# 檢查必要的 json 文件
head_json = abrv_dir / "head.json"
spellCurse_json = abrv_dir / "spellCurse.json"
if not head_json.exists() or not spellCurse_json.exists():  # 純粹確保 abrv 目錄存在 不會報錯正確斷詞
    print(f"Warning: Required files missing in {abrv_dir}")
    print(f"head.json exists: {head_json.exists()}")
    print(f"spellCurse.json exists: {spellCurse_json.exists()}")

try:
    with open(accountFilePath, encoding="utf-8") as f:
        loginDICT = json.load(f)
except:
    loginDICT = {"username": "", "apikey": ""}

if "url" in loginDICT:
    # docker 版登入
    articut = Articut(url=loginDICT["url"])
elif "username" and "apikey" in loginDICT:
    # 線上版登入
    articut = Articut(username=loginDICT["username"], apikey=loginDICT["apikey"])

G_extractTail_pat = re.compile(r"(?<=[/（]..[：、])([^）/]+)(?=[）/、])")
G_extractHeader_pat = re.compile(r"(?<=（中央社記者)([^）]*)")
G_extractText_pat = re.compile(r"</?[^>]+>")
G_headMember_pat = re.compile(
    r"(^.+?)(?:(?=(<LOCATION>)|(<UserDefined>))|(?=<RANGE)|(?=<ENTITY_oov>電))"
)
G_extractZhuyin_pat = re.compile(r"([\u3105-\u3129]+)")

G_abbrFileLIST: list[str] = [
    "KNOWLEDGE_adminAgency",
    "KNOWLEDGE_airlines",
    "KNOWLEDGE_airport",
    "KNOWLEDGE_department",
    "KNOWLEDGE_exhibit",
    "KNOWLEDGE_foundation",
    "KNOWLEDGE_newsAgency",
    "KNOWLEDGE_newsChannel",
    "KNOWLEDGE_newspapers",
    "KNOWLEDGE_organization",
    "KNOWLEDGE_financeKeyword",
    "KNOWLEDGE_party",
    "KNOWLEDGE_sportsAssociations",
    "KNOWLEDGE_stockExchange",
    "KNOWLEDGE_TWPresidentialOffice",
    "KNOWLEDGE_TWProcuratorate",
    "KNOWLEDGE_unitedNationsSystem",
    "KNOWLEDGE_nouns",
    "KNOWLEDGE_TWMRT",
    "KNOWLEDGE_TWJudicial",
    "KNOWLEDGE_TWIndustrialPark",
    "KNOWLEDGE_TWGov",
    "KNOWLEDGE_TWBank",
    "KNOWLEDGE_stockExchange",
    "KNOWLEDGE_financeIndex",
    "KNOWLEDGE_hotels",
    "KNOWLEDGE_regulations"
]


def _getPath(directory: str = "dict_collection") -> Path:
    currentFilePath = Path(__file__).resolve()
    parentDirPath: Path = currentFilePath.parent
    dictPath: Path = parentDirPath / directory

    return dictPath

def dictForger(inputSTR: str, directory: str):
    """
    依 inputSTR 內容查找 dict_collection 中適合的字典檔，
    並組合成一字典檔，該字典檔需經過 dict2File 才可以做為 userDefinedDictFILE 參數送到 parse 中。
    """
    dictPATH = _getPath(directory)
    returnDICT: dict[str, list[str]] = {}
    uDFilenameLIST: list[str] = []

    for filename in os.listdir(dictPATH):
        # <掃出需要用的詞條>
        uDDICT: dict[str, list[str]] = {}
        if filename.startswith("."):
            continue

        jsonPath = Path(dictPATH) / filename
        foundKeys = set()
        foundValues = set()
        with open(jsonPath, encoding="utf-8") as f:
            tmpDICT = json.load(f)
        for k in tmpDICT:
            if k in inputSTR and k not in foundKeys:
                foundKeys.add(k)
                uDDICT.setdefault(k, []).extend(tmpDICT[k])
            else:
                for value in tmpDICT[k]:
                    if value in inputSTR and value not in foundValues:
                        foundValues.add(value)
                        uDDICT.setdefault(k, []).extend(tmpDICT[k])
        try:
            uDDICT.pop("")
        except:
            pass

        tmpLIST: list[str] = []
        for k, vLIST in uDDICT.items():
            tmpLIST.append(k)
            for v in vLIST:
                tmpLIST.append(v)

        if len(tmpLIST) != 0:
            returnDICT[filename.replace(".json", "")] = tmpLIST

    return returnDICT

def dictConfirmer(
    inputSTR: str, inputDICT: dict[str, list[str]]
) -> dict[str, list[str]]:
    """
    input
        dict[str, list[str]] 是一個預計作為動態字典的字典檔
    output
        dict[str, list[str]] 是一個確認作為動態字典的字典檔

    檢查或調整字典檔內容的工具

    例1：
    inputDICT 中，若有屬於 knowledgeGraph.json 的內容，根據 cosine similarity 判斷欲使用哪組。

        如："木蘭"
        1. 作為植物：染井吉野櫻更是阿里山花季主角，今年受氣候影響，目前已經滿開（盛開），另外還有紫藤、木蘭、一葉蘭等花卉接力綻放
        2. 作為颱風：輕颱木蘭預計明天生成、無侵台機會
        3. 作為藝術項目：2010年擊樂劇場「木蘭」初生，2013年達全然改版規模的新版「木蘭」

    例2：移除 abbr 中出現且跟其他項目重複的項目
    """
    # 匯入模型
    dictPATH = _getPath("cosSimilarity_model")
    knowledgeGraphDICT: dict[str, dict[str, list[str]]] = {}
    with open(dictPATH / "knowledgeGraph.json", "r", encoding="utf-8") as d_F:
        knowledgeGraphDICT = json.load(d_F)

    ## 去重
    for k, vLIST in inputDICT.items():
        inputDICT[k] = list(set(inputDICT[k]))

    ## 移除 abbr 中出現且跟其他項目重複的項目
    if "KNOWLEDGE_abbr" in inputDICT:
        itemLIST: list[str] = inputDICT["KNOWLEDGE_abbr"]
        for k_s in inputDICT.keys():
            if k_s != "KNOWLEDGE_abbr":
                newItemLIST: list[str] = []
                for item_S in inputDICT[k_s]:
                    if item_S not in itemLIST:
                        newItemLIST.append(item_S)
                inputDICT[k_s] = newItemLIST

    ## 移除被判成`人名`的 CNA 員工
    if "KNOWLEDGE_CNAMember" in inputDICT:
        CNAMemberLIST: list[str] = inputDICT["KNOWLEDGE_CNAMember"]
        newPersonLIST: list[str] = []
        for personSTR in inputDICT.get("KNOWLEDGE_person", []):
            if personSTR not in CNAMemberLIST:
                newPersonLIST.append(personSTR)

        inputDICT["KNOWLEDGE_person"] = newPersonLIST

    ## 比對 person(來自 articut 判斷) 和 people(來自字典)
    if "KNOWLEDGE_person" in inputDICT and "KNOWLEDGE_people" in inputDICT:
        ## 若 person 中有和 people 一樣的詞彙 -> 移除 person
        for name_s in inputDICT["KNOWLEDGE_people"]:
            if name_s in inputDICT["KNOWLEDGE_person"]:
                inputDICT["KNOWLEDGE_person"].remove(name_s)

    ## 比對 location(來自 articut 判斷) 和 其他
    if "KNOWLEDGE_location" in inputDICT:
        totalTermLIST: list[str] = []
        locationTermLIST: list[str] = inputDICT["KNOWLEDGE_location"]

        for name_s, term_l in inputDICT.items():
            if name_s == "KNOWLEDGE_location":
                continue

            for term_s in term_l:
                totalTermLIST.append(term_s)

        ## 若 totalTermLIST 中有和 location字典 一樣的詞彙 -> 移除 location字典 的詞彙
        for location_s in locationTermLIST:
            if location_s in totalTermLIST:
                inputDICT["KNOWLEDGE_location"].remove(location_s)

    ## 處理`長江`亂 tangle 的問題
    ### 比對`person字典`或`people字典`中是否有`長江`和名字`江yz`
    isYangtzeExist: bool = False
    if "KNOWLEDGE_river" in inputDICT:
        if "長江" in inputDICT["KNOWLEDGE_river"]:
            isYangtzeExist = True

    chiangInPersonSTR: str = ""
    if "KNOWLEDGE_person" in inputDICT:
        for nameSTR in inputDICT["KNOWLEDGE_person"]:
            if nameSTR.startswith("江"):
                chiangInPersonSTR = nameSTR

    chiangInPeopleSTR: str = ""
    if "KNOWLEDGE_people" in inputDICT:
        for nameSTR in inputDICT["KNOWLEDGE_people"]:
            if nameSTR.startswith("江"):
                chiangInPeopleSTR = nameSTR

    ### 比對文章中是否有`長江yz`，有->移除長江，無->啥都不幹
    if len(chiangInPersonSTR) != 0 and isYangtzeExist == True:
        inspectSTR: str = "長" + chiangInPersonSTR
        if inspectSTR in inputSTR:
            try:
                inputDICT["KNOWLEDGE_river"].remove("長江")
            except ValueError:
                pass

    if len(chiangInPeopleSTR) != 0 and isYangtzeExist == True:
        inspectSTR: str = "長" + chiangInPeopleSTR
        if inspectSTR in inputSTR:
            try:
                inputDICT["KNOWLEDGE_river"].remove("長江")
            except ValueError:
                pass

    ## 收集 inputDICT 的重複 value 和 所屬的 key(s)
    copyDICT: dict[str, list[str]] = {}
    for typeName_S, vLIST in inputDICT.items():
        for v in vLIST:
            if v not in copyDICT:
                copyDICT[v] = []

            if v not in copyDICT[v]:
                copyDICT[v].append(typeName_S)

    confirmDICT: dict[str, list[str]] = {}
    for k, vLIST in copyDICT.items():
        if len(vLIST) > 1:
            confirmDICT[k] = vLIST

    ## 檢查 inputDICT 的空字典並移除
    removeLIST: list[str] = []
    for k_s in inputDICT.keys():
        if len(inputDICT[k_s]) == 0:
            removeLIST.append(k_s)

    for remove_s in removeLIST:
        del inputDICT[remove_s]

    ## 逐筆比對 cosine similarity，調整 inputDICT 內容。
    for name_s, vLIST in confirmDICT.items():
        KGKeyLIST: list[str] = list(map(lambda x: x.replace("KNOWLEDGE_", ""), vLIST))
        scoreDICT: dict[str, float] = {}
        articleLIST: list[str] = _extractSubstringLIST(inputSTR, name_s)

        for KGKey in KGKeyLIST:
            if name_s in knowledgeGraphDICT and KGKey in knowledgeGraphDICT[name_s]:
                scoreFLOAT: float = _comparison(
                    knowledgeGraphDICT[name_s][KGKey], articleLIST
                )
                scoreDICT[KGKey] = scoreFLOAT

        if len(scoreDICT) == 0:
            continue

        maxKeySTR = max(scoreDICT, key=scoreDICT.get)
        del scoreDICT[maxKeySTR]

        ## 調整 inputDICT 內容
        for typeSTR in scoreDICT.keys():
            inputDICT["KNOWLEDGE_" + typeSTR].remove(name_s)

            if len(inputDICT["KNOWLEDGE_" + typeSTR]) == 0:
                ## 空了就刪掉
                del inputDICT["KNOWLEDGE_" + typeSTR]

    return inputDICT

def _extractSubstringLIST(inputSTR: str, subSTR: str) -> list[str]:
    """
    input
        inputSTR 輸入文章
        subSTR   子字串
    output
        list[str]

    根據輸入文章和子字串內容，以子字串為中心分割文章。
    """
    subSTR_pat: str = re.escape(subSTR)
    matches: list[int] = [match.start() for match in re.finditer(subSTR_pat, inputSTR)]

    resultLIST: list[str] = []

    if not matches:
        return []

    for targetIDX in matches:
        startIDX = max(0, targetIDX - 20)
        endIDX = min(len(inputSTR), targetIDX + len(subSTR) + 20)

        resultLIST.append(inputSTR[startIDX:endIDX])

    return resultLIST

def createUDByGuillemets(inputSTR: str) -> dict:
    """
    根據 inputSTR，檢查是否出現書名號，將書名號中的內容建成字典。
    """
    pieceDICT: dict[str, list[str]] = {}

    pat = re.compile(r"(?<=《)[^《]+?(?=》)")
    resultLIST = [x.group() for x in pat.finditer(inputSTR)]

    if len(resultLIST) == 0:
        return {}
    else:
        pieceDICT["KNOWLEDGE_book"] = resultLIST
        return pieceDICT

def createCNAMemberUD(inputSTR: str) -> dict:
    """
    掃描文章，將屬於中央社的同仁另外標出。
    """
    CNAMemberDICT: dict[str, list[str]] = {}
    CNAMemberLIST: list[str] = []

    # 掃描文章尾部
    typeLIST: list[str] = [x.group() for x in G_extractTail_pat.finditer(inputSTR)]
    for typeSTR in typeLIST:
        nameLIST: list[str] = typeSTR.split("、")

        for name in nameLIST:
            CNAMemberLIST.append(name)

    # 掃描文章頭部
    headLIST: list[str] = [x.group() for x in G_extractHeader_pat.finditer(inputSTR)]
    for head in headLIST:
        udDICT = dictForger(inputSTR, "dict_collection")
        udFILE = dict2File(udDICT)
        resultDICT = articut.parse(head, userDefinedDictFILE=udFILE.name)

        for sentence in resultDICT["result_pos"]:
            if len(sentence) == 1:
                continue

            detailLIST: list[str] = [
                x.group() for x in G_headMember_pat.finditer(sentence)
            ]
            if len(detailLIST) == 0:
                name: str = G_extractText_pat.sub("", sentence)
                CNAMemberLIST.append(name)
                continue

            name: str = G_extractText_pat.sub("", detailLIST[0])
            CNAMemberLIST.append(name)

    if len(CNAMemberLIST) == 0:
        return {}
    else:
        CNAMemberDICT["KNOWLEDGE_CNAMember"] = CNAMemberLIST
        return CNAMemberDICT

def createAbbrUD(articleSTR: str, inputDICT: dict[str, list[str]]) -> dict:
    """
    掃描文章，檢查是否有縮略語。

    input:
        文章本身      str
        字典         dict[str, list[str]]
    output:
        縮寫字典      dict[str, list[str]]
    """
    ## Part 1：利用 entity 的拼湊
    allCombinations: set = set()

    ### 獲得所有縮寫的可能
    for k_s, v_l in inputDICT.items():
        if k_s not in G_abbrFileLIST:
            continue

        for v_s in v_l:
            if v_s in articleSTR:
                if len(v_s) < 4:
                    continue
                for extendTerm in _getExtendTermLIST(v_s):
                    allCombinations.add(extendTerm)

    ### 確定有哪些是出現在文章中的
    resultLIST: list[str] = []

    for combinationSTR in list(allCombinations):
        if combinationSTR in articleSTR:
            resultLIST.append(combinationSTR)

    ## Part 2：利用 pos 細分
    ### 獲得所有縮寫的可能
    for k_s, v_l in inputDICT.items():
        if k_s not in G_abbrFileLIST:
            continue

        for v_s in v_l:
            if len(v_s) < 4 or len(v_s)>15 or v_s not in articleSTR:
                continue

            for possibleTermSTR in _getPossibleLIST(v_s):
                if possibleTermSTR in articleSTR:
                    resultLIST.append(possibleTermSTR)

    # 檢查 resultLIST 是否有其他 inputDICT 的值，若有就移除。
    for v_l in inputDICT.values():
        for v_s in v_l:
            if v_s in resultLIST:
                resultLIST.remove(v_s)

    # 檢查 resultLIST 是否有不雅名稱的諧音，若有則移除。
    resultLIST = _tabooDetection(resultLIST)

    return {"KNOWLEDGE_abbr": resultLIST}

def _tabooDetection(abbrLIST: list[str])-> list[str]:
    """
    input:
        縮寫字典               list[str]
    output:
        檢查過不含不雅名稱的字典 list[str]
    """
    # 取髒話
    spellCurseLIST: list[list[str]] = []
    jsonFile: Path = currentDir / "abrv" / "spellCurse.json"
    with open(jsonFile, "r", encoding="utf-8") as f:
        spellCurseLIST = json.load(f)

    # 取可能是髒話的縮寫詞
    removeLIST: list[str] = []
    for element_s in abbrLIST:
        resultDICT: dict = articut.parse(inputSTR=element_s, level="lv3")
        spellAbbrLIST: list[str] = [x.group() for x in G_extractZhuyin_pat.finditer(resultDICT['utterance'][0])]

        removeBOOL: bool = False
        for curse_l in spellCurseLIST:
            if isTaboo(curse_l, spellAbbrLIST):
                removeBOOL = True
                break

        if removeBOOL:
            removeLIST.append(element_s)

    # 將可能是髒話的縮寫詞移走
    for removeSTR in removeLIST:
        abbrLIST.remove(removeSTR)

    return abbrLIST

def isTaboo(spellCurseLIST: list[str], spellAbbrLIST: list[str]) -> bool:
    """
    input:
        spellCurseLIST   不雅名稱拼音    ["ㄅㄞ", "ㄔ"]
        spellAbbrLIST    欲檢查縮寫拼音  ["ㄉㄚ", "ㄨㄟ", "ㄨㄤ", "ㄅㄞ", "ㄔ", "ㄅㄞ", "ㄏㄜ", "ㄉㄚ", "ㄙㄞ"]
    output:
        bool             是否參雜不雅名稱
    """
    idx = -1
    for elem in spellCurseLIST:
        try:
            idx = spellAbbrLIST.index(elem, idx + 1)
        except ValueError:
            return False
    return True

def _getPossibleLIST(udSTR: str) -> list[str]:
    """
    input:
        一個字典中的詞
    output:
        這個詞中可作為 abbr 的字元(按照順序)
    """
    rangeLocalityLIST: list[str] = ["上", "下", "左", "右", "內", "外", "旁", "底"]
    headLIST: list[str] = []
    jsonFile: Path = currentDir / "abrv" / "head.json"
    with open(jsonFile, "r", encoding="utf-8") as f:
        headLIST = json.load(f)

    # 送入 articut 拆解
    posLIST: list[str] = [
        "LOCATION",
        "KNOWLEDGE_chemical",
        "ENTITY_num",
        "ENTITY_classifier",
        "ENTITY_measurement",
        "ENTITY_pronoun",
        "ENTITY_noun",
        "ENTITY_nouny",
        "ENTITY_nounHead",
        "ENTITY_oov",
        "ENTITY_person",
        "ACTION_verb",
        "VerbP",
        "MODIFIER",
        "MODIFIER_color",
        "ModifierP",
        "QUANTIFIER",
    ]
    # 拿出 articut 斷詞結果
    resultDICT: dict = articut.parse(udSTR)
    charLIST: list[str] = []
    lastElementLIST: list[str] = []

    if "result_obj" not in resultDICT:
        return []

    # 檢查各部件
    for i in range(len(resultDICT["result_obj"][0])):
        wordDICT = resultDICT["result_obj"][0][i]
        if wordDICT["pos"] in posLIST:
            textSTR: str = wordDICT["text"]
            for j in range(len(textSTR)):
                if j == 0:
                    ## 取元素的第一個字，但不能是：rangeLocalityLIST
                    if textSTR[j] not in rangeLocalityLIST:
                        if i == len(resultDICT["result_obj"][0])-1 and i!=0:
                            lastElementLIST.append(textSTR[j])
                        else:
                            charLIST.append(textSTR[j])
                else:
                    ## 再取所有元素中有在中心語表的，但不能是：rangeLocalityLIST
                    if (textSTR[j] in headLIST) and (
                        textSTR[j] not in rangeLocalityLIST
                    ):
                        if i == len(resultDICT["result_obj"][0])-1 and i!=0:
                            lastElementLIST.append(textSTR[j])
                        else:
                            charLIST.append(textSTR[j])

    returnLIST: list[str] = combine2Abbr(charLIST=charLIST, lastElementLIST=lastElementLIST, itemNumber=len(resultDICT["result_obj"][0])-1)
    return returnLIST

def combine2Abbr(charLIST: list[str], lastElementLIST: list[str], itemNumber: int) -> list[str]:
    """
    input:
        可作為 abbr 的字元(按照順序)
    output:
        這些字元可能組成的 abbr
    """
    combinationsLIST: list[tuple] = []
    maxLengthINT: int = 6
    if len(charLIST) < 5:
        maxLengthINT = maxLengthINT

    for r in range(3, maxLengthINT):
        combinationsLIST.extend(itertools.combinations(charLIST, r))

    combineLIST: list[str] = []
    for combinationTUPLE in combinationsLIST:
        abbrSTR: str = ""
        for elementSTR in combinationTUPLE:
            abbrSTR += elementSTR

        combineLIST.append(abbrSTR)
        for lastElementSTR in lastElementLIST:
            if len(abbrSTR) >= itemNumber:
                combineLIST.append(abbrSTR+lastElementSTR)

        if len(lastElementLIST)>=2:
            combineLIST.append(abbrSTR+lastElementLIST[0]+lastElementLIST[-1])

    returnLIST: list[str] = []
    posLIST: list[str] = ["ENTITY_nouny", "ENTITY_oov"]
    for udAbbrSTR in combineLIST:
        udAbbrResultDICT: dict = articut.parse(inputSTR=udAbbrSTR)
        if len(udAbbrResultDICT["result_obj"][0])==1:
            if udAbbrResultDICT["result_obj"][0][0]["pos"] in posLIST:
                returnLIST.append(udAbbrSTR)
            
        else:
            returnLIST.append(udAbbrSTR)

    return returnLIST

def _getExtendTermLIST(udSTR: str) -> list[str]:
    """
    input:
        字典中的詞       str
    output:
        這個詞可能的變化 list[str]
    """
    posLIST: list[str] = [
        "LOCATION",
        "KNOWLEDGE_chemical",
        "ENTITY_num",
        "ENTITY_classifier",
        "ENTITY_measurement",
        "ENTITY_pronoun",
        "ENTITY_noun",
        "ENTITY_nouny",
        "ENTITY_nounHead",
        "ENTITY_oov",
        "ACTION_verb",
        "VerbP",
        "MODIFIER",
        "MODIFIER_color",
        "ModifierP",
        "QUANTIFIER",
        "TIME_holiday",
        "TIME_justtime",
        "TIME_day",
        "TIME_week",
        "TIME_month",
        "TIME_season",
        "TIME_year",
        "TIME_decade"
    ]
    combinationsLIST: list[tuple] = []
    resultDICT: dict = articut.parse(udSTR)
    wordLIST: list[dict[str, str]] = []
    if "result_obj" in resultDICT:
        # 拿出 articut 斷詞結果
        if len(resultDICT["result_obj"][0]) < 3:
            return [udSTR]

        for wordDICT in resultDICT["result_obj"][0]:
            if wordDICT["pos"] in posLIST:
                wordLIST.append(wordDICT["text"])

    abbrMaxLenINT: int = 6
    if len(wordLIST) < 6:
        abbrMaxLenINT = len(wordLIST)

    for r in range(3, abbrMaxLenINT):
        combinationsLIST.extend(itertools.combinations(wordLIST[:-1], r))

    returnLIST: list[str] = []
    for combinationTUPLE in combinationsLIST:
        abbrSTR: str = ""
        for elementSTR in combinationTUPLE:
            abbrSTR += elementSTR
        abbrSTR += wordLIST[-1]
        returnLIST.append(abbrSTR)

    return returnLIST

def _vLIST(inputLIST: list[str]) -> list[str]:
    vLIST = []

    for i in inputLIST:
        resultDICT = articut.parse(i)
        vsLIST = articut.getVerbStemLIST(resultDICT)
        for s in vsLIST:
            vLIST.extend([v[-1] for v in s if s != []])
    return vLIST

def _counterCosineSimilarity(counter01, counter02, w=1) -> float:
    """
    計算 counter01 和 counter02 兩者的餘弦相似度
    """
    terms = set(counter01).union(counter02)
    dotprod = sum(counter01.get(k, 0) * counter02.get(k, 0) for k in terms)
    magA = math.sqrt(sum(counter01.get(k, 0) ** 2 for k in terms))
    magB = math.sqrt(sum(counter02.get(k, 0) ** 2 for k in terms))

    try:
        return (dotprod / (magA * magB)) * w
    except ZeroDivisionError:
        return 0

def _comparison(vLIST1: list[str], vLIST2: list[str]) -> float:
    if len(vLIST1) == 0 or len(vLIST2) == 0:
        return 0.0

    c1 = Counter(_vLIST(vLIST1))
    c2 = Counter(_vLIST(vLIST2))
    cfResult = _counterCosineSimilarity(c1, c2)
    return cfResult

def dict2File(uDDICT: dict[str, list[str]]):
    """
    將 dict 寫成暫存檔，方可作為 parse 的 userDefinedDictFILE 參數。
    """
    # <將字典寫入暫存檔>
    if platform.system() == "Windows":
        dictFILE = tempfile.NamedTemporaryFile(mode="w+", delete=False)
    else:
        dictFILE = tempfile.NamedTemporaryFile(mode="w+")
    json.dump(uDDICT, dictFILE)
    dictFILE.flush()
    # </將字典寫入暫存檔>
    return dictFILE

def findExactDictionary(text: str, myDICT: dict[str, list[str]]) -> str:
    """
    根據 udFilenameLIST 檢查 text 是否屬於該字典。
    若是：回傳該字典名稱；若否：回傳 UserDefined。
    例外：udFilenameLIST 中若為 KNOWLEDGE_book，直接回傳 KNOWLEDGE_book。
    """
    for k, vLIST in myDICT.items():
        for v in vLIST:
            if text == v:
                return k

    return "UserDefined"

def _getEntry(posSTR: str, textSTR: str, directorySTR: str) -> dict[str, list[str]]:
    """
    根據 Pos 和 Text 查詢指定檔案
    回傳指定檔案的 key 和 value
    """
    dictPATH = _getPath(directorySTR)
    filename: str = posSTR + ".json"
    jsonPath = Path(dictPATH) / filename
    try:
        with open(jsonPath, encoding="utf-8") as f:
            tmpDICT = json.load(f)
    except FileNotFoundError:
        return {textSTR: []}

    for k_s, v_l in tmpDICT.items():
        if textSTR == k_s or textSTR in v_l:
            return {k_s: v_l}

    return {}


if __name__ == "__main__":
    #print(createAbbrUD("參加國際數理學科奧林匹亞競賽及國際科學展覽成績優良學生升學優待辦法", {"tmp":"參加國際數理學科奧林匹亞競賽及國際科學展覽成績優良學生升學優待辦法"}))
    print(_getPossibleLIST("高雄國際航空站"))