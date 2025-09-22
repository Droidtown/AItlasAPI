#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# 把 AItlasView 加進 path
import requests
from pathlib import Path

#sys.path.append(str(Path(__file__).parent / "AItlasView"))
#sys.path.insert(0, "..")

# from .AItlas.main import askLoki
from ArticutAPI import Articut
from copy import deepcopy
import json

# try:
# from AItlas_TW.aitlas_wiki.KG.people import action as actionDICT
# except:
# pass

import sqlite3
import tempfile
from typing import Union
from functools import reduce
from pprint import pprint
from datetime import datetime
import CNA_DTLK.CNA_Articut as CNA_Articut
import re

purgePat = re.compile("</?[a-zA-Z]+(_[a-zA-Z]+)?>")
G_baseTimePAT: re.Pattern = re.compile(r"(?<=）)[0-9]{7}")
G_knowledgePAT: re.Pattern = re.compile(r"<KNOWLEDGE_(?:(?!CNAMember).+?)>(?:(?!中央社).+?)</KNOWLEDGE_(?:(?!CNAMember).+?)>")
G_dictPAT: re.Pattern = re.compile(r"\{[^{}]*\}")
G_sourcePAT: re.Pattern = re.compile(r'(?<="source": ")[^"]+')
G_taregetPAT: re.Pattern = re.compile(r'(?<="target": ")[^"]+')
G_labelPAT: re.Pattern = re.compile(r'(?<="label": ")[^"]+')
G_metaDataPAT: re.Pattern = re.compile(r'(?<="metaData": ")[^"]+')
G_encounterTimePAT: re.Pattern = re.compile(r'(?<="encounter_time": ")[^"]+')

listPackerDICT = {
    "twPat": re.compile(r"[一-龥]"),
    "birthdatePat": re.compile(
        r"(?<=\{\{[Bb]irth[\s_]date[\s_]and[\s_]age\|)\d+\|\d+\|\d+"
    ),
    "parentsPat": re.compile(r"(?<=[\|\[])[一-龥]+?(?=\]\])"),
    "nicknamePat": re.compile(r"(?<=[\|\[])[一-龥]+?(?=\]\])"),
    "birthplacePat": re.compile(r"(?<=[\|\[])[一-龥]+?(?=\]\])"),
    "nationalityPat": re.compile(r"(?<=[\|\[])[一-龥]+?(?=\]\])"),
    "spousePat": re.compile(r"(?<=\|)(\[\[)?[一-龥]+?(\]\])?(?=\|\d)"),
}

# genderPAT = re.compile("<PERSON><AUX><NOUNY>") => if NOUNY in AItlas.get_all(nouny, "biological_gender")

import os

BASEPATH = os.path.dirname(os.path.abspath(__file__))
BaseDIR: Path = Path(__file__).resolve().parent
newAItlasDirPATH = Path.cwd() / "AItlasResult"
newAItlasDirPATH.mkdir(exist_ok=True, parents=True)

try:
    with open("{}/account.info".format(BASEPATH), encoding="utf-8") as f:
        accountDICT = json.load(f)
    articut = Articut(username=accountDICT["username"], apikey=accountDICT["api_key"])
except:
    articut = Articut()


class AItlas:
    def __init__(self, username="", apikey="", url=""):
        self.articut = Articut(username=username, apikey=apikey, url=url)

        self.personNamePAT = re.compile(
            "(?<=<ENTITY_person>)([^<]+)(?=</ENTITY_person>)"
        )
        self.aliasPAT = []
        self.addressPAT = []
        self.affiliationPAT = []
        self.awardPAT = []
        self.birth_datePAT = []
        self.death_datePAT = []
        self.biological_genderPAT = []
        self.body_heightPAT = []
        self.body_weightPAT = []
        self.jobtitlePAT = re.compile(
            "<LOCATION>([^<]+</LOCATION>(<RANGE_locality>前</RANGE_locality>)?<(UserDefined|ENTITY_(nounHead|nouny?|oov))>[^<]+)</(UserDefined|ENTITY_(nounHead|nouny?|oov))><ENTITY_person>([^<]+)</ENTITY_person>"
        )
        self.nationalityPAT = []
        self.parentPAT = re.compile(
            "(?<=</ENTITY_person>)(<FUNC_inner>[的之]</FUNC_inner>)?<ENTITY_pronoun>[父母爸媽].?</ENTITY_pronoun><ENTITY_person>([^<]+)</ENTITY_person>"
        )
        self.siblingPAT = re.compile(
            "(?<=</ENTITY_person>)(<FUNC_inner>[的之]</FUNC_inner>)?<ENTITY_pronoun>[哥弟姐姊妹兄].?</ENTITY_pronoun><ENTITY_person>([^<]+)</ENTITY_person>"
        )
        self.childPAT = []
        self.spousePAT = re.compile(
            "(?<=</ENTITY_person>)(<FUNC_inner>[的之]</FUNC_inner>)?<ENTITY_pronoun>([丈妻先太].?|老[公婆])</ENTITY_pronoun><ENTITY_person>([^<]+)</ENTITY_person>"
        )
        self.skillsPAT = []
        self.educationPAT = []
        self.event_logPAT = []
        self.descriptionPAT = []
        self.raw_dataPAT = []
        self.wikipedia_TW: dict[str, dict] = {}
        self.wikipedia_EN: dict[str, dict] = {}
        self.wikipedia_TW["person"] = self._matchAItlasPerson("tw")
        # self.wikipedia_EN["person"] = self._matchAItlasPerson("en")
        self.wikipedia_TW["location"] = self._matchAItlasLocation("tw")
        # self.wikipedia_EN["location"] = self._matchAItlasLocation("en")
        self.wikipedia_TW["entity"] =  self._matchAItlasNer("tw")
        # self.wikipedia_EN["ner"] = self._matchAItlasNer("en")

        self.AITLASKG = {
            "person": {},
            "location": {},
            "entity": {},
            "interaction": [],
            "event": [],
            "article": "",
        }
        self.viewDICT =  {}

    def _getAvailableFolder(self, parentDirPATH: Path, folderNameSTR: str) -> Path:
        """
        判斷 folder_name 是否已存在於 parent_folder 中
        若已存在，回傳 folder_name_1、folder_name_2 等不重複資料夾名稱
        """
        parentDirPATH = Path(parentDirPATH)
        targetFolder = parentDirPATH / folderNameSTR

        if not targetFolder.exists():
            return folderNameSTR

        counter = 1
        while True:
            newName = f"{folderNameSTR}_{counter}"
            newFolder = parentDirPATH / newName
            if not newFolder.exists():
                return newName
            counter += 1

    def _highlightArticles(self, articleSTR, peopleDICT=None, placeDICT=None, entityDICT=None):
        """
        將文章中的人名、地名、NER hightlight 顯示
        """
        # 依照人名長度排序(長->短)
        peopleNames = sorted(peopleDICT.keys(), key=len, reverse=True)
        placeNames = sorted(placeDICT.keys(), key=len, reverse=True)
        nerNames = sorted(entityDICT.keys(), key=len, reverse=True)

        # 建立 regex pattern
        highlightedContent = articleSTR
        if peopleNames:
            peoplePattern = re.compile(r"(" + "|".join(map(re.escape, peopleNames)) + r")")
            highlightedContent = peoplePattern.sub(
                r'<span class="highlight_yellow">\1</span>', highlightedContent
            )
        if placeNames:
            placePattern = re.compile(r"(" + "|".join(map(re.escape, placeNames)) + r")")
            highlightedContent = placePattern.sub(
                r'<span class="highlight_pink">\1</span>', highlightedContent
            )
        if nerNames:
            nerPattern = re.compile(r"(" + "|".join(map(re.escape, nerNames)) + r")")
            highlightedContent = nerPattern.sub(
                r'<span class="highlight_blue">\1</span>', highlightedContent
            )

        return highlightedContent

    def view(self, directoryNameSTR: str):
        directoryNameSTR = self._getAvailableFolder(newAItlasDirPATH, directoryNameSTR)

        # 存 AItlasKG
        ## 存 static/css 跟 static/js 跟 static/{directoryNameSTR}.html
        ### static/css
        sourceCssDirPATH: Path = BaseDIR.parent / "AItlasView" / "static" / "css"
        targetCssDirPATH: Path = newAItlasDirPATH / directoryNameSTR / "static" / "css"
        targetCssDirPATH.mkdir(exist_ok=True, parents=True)
        
        for filePATH in sourceCssDirPATH.glob("*.css"):
            # 取內容
            contentSTR: str = filePATH.read_text(encoding="utf-8")

            # 在目標資料夾建立檔案
            newFilePATH: Path = targetCssDirPATH / filePATH.name
            newFilePATH.write_text(contentSTR, encoding="utf-8")

        ### static/js
        sourceJsDirPATH: Path = BaseDIR.parent / "AItlasView" / "static" / "js"
        targetJsDirPATH: Path = newAItlasDirPATH / directoryNameSTR / "static" / "js"
        targetJsDirPATH.mkdir(exist_ok=True, parents=True)

        for filePATH in sourceJsDirPATH.glob("*.js"):
            # 取內容
            contentSTR: str = filePATH.read_text(encoding="utf-8")

            # 在目標資料夾建立檔案
            newFilePATH: Path = targetJsDirPATH / filePATH.name
            newFilePATH.write_text(contentSTR, encoding="utf-8")

        ### static/js/data.js
        with open( newAItlasDirPATH / directoryNameSTR / "static" / "js" / "data.js", "w", encoding="utf-8" )as f:
            highlightContent: str = self._highlightArticles(articleSTR=self.AITLASKG["article"], peopleDICT=self.viewDICT["person"], placeDICT=self.viewDICT["location"], entityDICT=self.viewDICT["entity"])
            resultLIST: list[dict[str, str]] = [{
                "title": self.viewDICT["article"][0]["title"],
                "content": highlightContent,
                "events": self.viewDICT["event"],
                "peoples": self.viewDICT["person"],
                "places": self.viewDICT["location"],
                "entities": self.viewDICT["entity"]
            }]
            dataDICT: dict = {
                "articles": resultLIST,
                "global_entities": {
                    "peoples": list(self.viewDICT["person"].keys()),
                    "places": list(self.viewDICT["location"].keys()),
                    "entities": list(self.viewDICT["entity"].keys()),
                }
            }
            
            dataJsSTR: str = f"var dataDICT = {json.dumps(dataDICT, ensure_ascii=False, indent=4)}\n"
            
            f.write(dataJsSTR)

        ### static/index.html
        sourceHtmlPATH: Path = BaseDIR.parent / "AItlasView" / "static" / "index.html"
        contentSTR: str = sourceHtmlPATH.read_text(encoding="utf-8")
        targetHtmlPATH: Path = newAItlasDirPATH / directoryNameSTR / f"{directoryNameSTR}.html"
        targetHtmlPATH.write_text(contentSTR)

        ## 存 AItlasResult/
        newAItlasKgPATH: Path = newAItlasDirPATH / directoryNameSTR / "data"
        newAItlasKgPATH.mkdir(exist_ok=True, parents=True)
    
        ### 寫 person.json
        with open(newAItlasKgPATH / "person.json", "w", encoding="utf-8") as f:
            json.dump(self.viewDICT["person"], f, ensure_ascii=False, indent=4)

        ### 寫 article.json
        with open(newAItlasKgPATH / "article.json", "w", encoding="utf-8") as f:
            json.dump(self.viewDICT["article"], f, ensure_ascii=False, indent=4)

        ### 寫 location.json
        with open(newAItlasKgPATH / "location.json", "w", encoding="utf-8") as f:
            json.dump(self.viewDICT["location"], f, ensure_ascii=False, indent=4)

        ### 寫 ner.json
        with open(newAItlasKgPATH / "entity.json",  "w", encoding="utf-8") as f:
            json.dump(self.viewDICT["entity"], f, ensure_ascii=False, indent=4)

        ### 寫 人物圖 person2person.json
        #with open(newAItlasKgPATH / "person2person.json",  "w", encoding="utf-8") as f:
            #json.dump(self.viewDICT["person2person"], f, ensure_ascii=False, indent=4)

        ### 寫 event.json
        with  open(newAItlasKgPATH / "event.json", "w", encoding="utf-8") as f:
            json.dump(self.viewDICT["event"], f, ensure_ascii=False, indent=4)
        
        return None

    def _matchAItlasPerson(self, lang):
        personDICT = {}
        if lang.lower() == "tw":
            BaseDIR: Path = Path(__file__).resolve().parent
            personDICT = json.load(
                open(
                    BaseDIR/"AItlas_TW/wikipedia/AItlas_wiki_person.json",
                    "r",
                    encoding="utf-8",
                )
            )
        # elif lang.lower() == "en":
        # personDICT = json.load(open("AItlas_EN/wikipedia/AItlas_wiki_person.json", "r", encoding="utf-8"))
        return personDICT

    def _matchAItlasLocation(self, lang):
        locationDICT = {}
        if lang.lower() == "tw":
            locationDICT = json.load(
                open(
                    BaseDIR/"AItlas_TW/wikipedia/AItlas_wiki_location.json",
                    "r",
                    encoding="utf-8"
                )
            )
        # elif lang.lower() == "en":
        # locationDICT = json.load(open("AItlas_EN/wikipedia/AItlas_wiki_location.json", "r", encoding="utf-8"))
        return locationDICT

    def _matchAItlasNer(self, lang):
        nerDICT = {}
        if lang.lower() == "tw":
            nerDICT = json.load(
                open(
                    BaseDIR/"AItlas_TW/wikipedia/AItlas_wiki_entity.json",
                    "r",
                    encoding="utf-8"
                )
            )
        # elif lang.lower() == "en":
        # locationDICT = json.load(open("AItlas_EN/wikipedia/AItlas_wiki_entity.json", "r", encoding="utf-8"))
        return nerDICT

    def scan(self, inputSTR):
        # article
        self.AITLASKG["article"] = inputSTR

        # person
        for personSTR in self.wikipedia_TW["person"].keys():
            if personSTR in inputSTR:
                # print(f"person:{personSTR}")
                self.AITLASKG["person"][personSTR] = self.wikipedia_TW["person"][personSTR]

        # location
        for originLocationSTR, dataDICT in self.wikipedia_TW["location"].items():
            locationSTR: str = dataDICT["locationName"]
            if locationSTR in inputSTR:
                self.AITLASKG["location"][locationSTR] = self.wikipedia_TW["location"][originLocationSTR]

        # entity
        for originNerSTR, dataDICT in self.wikipedia_TW["entity"].items():
            nerSTR: str = dataDICT["nerName"]
            if nerSTR in inputSTR:
                self.AITLASKG["entity"][nerSTR] = self.wikipedia_TW["entity"][originNerSTR]


        return self.AITLASKG

    def _listPacker(self, datatype, inputSTR):
        if datatype == "生日":
            resultLIST = [
                i.group().replace("|", "/")
                for i in listPackerDICT["birthdatePat"].finditer(inputSTR)
            ]
        elif datatype == "父母":
            resultLIST = [
                i.group() for i in listPackerDICT["birthdatePat"].finditer(inputSTR)
            ]
        elif datatype == "出生地":
            resultLIST = [
                i.group() for i in listPackerDICT["birthplacePat"].finditer(inputSTR)
            ]
        elif datatype == "國籍":
            resultLIST = [
                i.group() for i in listPackerDICT["nationalityPat"].finditer(inputSTR)
            ]
        elif datatype == "配偶":
            resultLIST = [
                i.group() for i in listPackerDICT["spousePat"].finditer(inputSTR)
            ]
        elif datatype == "別名":
            if "、" in inputSTR:
                resultLIST = inputSTR.split("、")
            else:
                resultLIST = [
                    i.group() for i in listPackerDICT["nicknamePat"].finditer(inputSTR)
                ]
        else:
            resultLIST = [inputSTR]

        for i in range(0, len(resultLIST)):
            if re.match(r"\d+/\d+/\d+", resultLIST[i]):
                pass
            elif listPackerDICT["twPat"].findall(resultLIST[i]) == []:
                resultLIST[i] = None
            else:
                resultLIST[i] = resultLIST[i].replace("[[", "").replace("]]", "")
        while None in resultLIST:
            resultLIST.remove(None)
        return resultLIST

    def _callLLM2GenContent(self, modelnameSTR: str="Gemma3-27B", sentenceSTR: str="") -> dict:
        """
        給定文章和指定的 LLM
        [Gemma2-9B, Gemma3-12B, Gemma3-27B, Llama3-8B, Llama3-70B, Llama3-Taiwan-8B, Llama3.3-70B, Phi3-3B, Phi4-14B, Nemotron-4B]
        讓 LLM 找到『誰對誰做了什麼』的結構

        回傳 eventDICT 
        若為空 dict 則為
        """
        url = "https://api.droidtown.co/Loki/Call/" # 中文版

        payload = {
            "username": accountDICT["username"],
            "func": "call_llm",
            "data": {
                "model": modelnameSTR, # [Gemma2-9B, Gemma3-12B, Gemma3-27B, Llama3-8B, Llama3-70B, Llama3-Taiwan-8B, Llama3.3-70B, Phi3-3B, Phi4-14B, Nemotron-4B]
                "system": "你是一位關注新事物的記者", # optional
                "assistant": "", # optional
                "user": f"""```json\b{str(sentenceSTR)}```請閱讀這篇文章，以有<KNOWLEDGE_*>([^<]+)</KNOWLEDGE_*>的元素為優先，找到誰對誰做了什麼的結構，沒有的話就留空，寫成下列 json 格式，不要給我多餘的東西
                        ```[{{"source": ""/*主詞*/,"target": ""/*#受詞*/,"label": ""/*#主詞對受詞做的事情*/,"metaData": ""/*#文章中的這句句子*/,"encounter_time": ""/*#這件事情的發生時間*/}},......]```\b""" # required
            }
        }
        response = requests.post(url, json=payload)
        # 先檢查 status code
        if response.status_code != 200:
            return {}

        try:
            resultDICT = response.json()
            chSTR = resultDICT["result"][0]["message"]["content"]
            return chSTR
        except requests.exceptions.JSONDecodeError:
            return {}

    def _parseArticutKnowledgeSentence(self, articutResultDICT: dict, baseTimeSTR: str)-> dict[str, str]:
        """
        找到含有兩個以上 <KNOWLEDGE_*>[^<]+</KNOWLEDGE_*> 的句子回傳
        {
            "<KNOWLEDGE_party>民進黨</KNOWLEDGE_party><ACTION_verb>任命</ACTION_verb>": "民進黨任命",
            "": "",
            ...
        }
        
        input:
            dict  articutResultDICT
        output:
            dict[str, str]  pos句:時間  
        """
        resultPosLIST: list[str] = articutResultDICT["result_pos"]
        # timeLIST: list[str] = articutResultDICT["time"]
        resultDICT: dict[str, str] = {}

        # 填
        for idx, sentence_s in enumerate(resultPosLIST):
            matches: re.Match = G_knowledgePAT.findall(sentence_s)
            if len(matches) >=2 :
                resultDICT[sentence_s] = baseTimeSTR
                # if len(timeLIST[idx])>0:
                #     resultDICT[sentence_s] = timeLIST[idx][0]["datetime"].replace(" ", "T")

        return resultDICT

    def _convertRoc2Iso(self, rocDateSTR: str) -> str:
        """
        將民國年格式 (例如 '1140613') 轉成 ISO 8601 格式 'YYYY-MM-DDT00:00:00'
        """
        if len(rocDateSTR) != 7 or not rocDateSTR.isdigit():
            raise ValueError("輸入格式錯誤，應為 7 位數字，例如 '1140613'")

        rocYearSTR = int(rocDateSTR[:3])
        yearSTR = rocYearSTR + 1911  # 民國年轉西元年
        monthSTR = int(rocDateSTR[3:5])
        daySTR = int(rocDateSTR[5:7])

        dt = datetime(yearSTR, monthSTR, daySTR)
        return dt.strftime("%Y-%m-%dT%H:%M:%S")

    def aitlasViewPacker(self, directoryNameSTR: str):
        translatePersonDICT = {
            "name": "全名",
            "本名": "全名",
            "姓名": "全名",
            "外文名": "外文名",
            "nickname": "別名",
            "別名": "別名",
            "性別": "生理性別",
            "birth_date": "生日",
            "出生日期": "生日",
            "birth_place": "出生地",
            "place of birth": "出生地",
            "出生地點": "出生地",
            "death_date": "忌日",
            "逝世日期": "忌日",
            "death_place": "死亡地",
            "逝世地點": "死亡地",
            "death_cause": "死因",
            "affiliation": "機構",
            "office": "職銜",
            "occupation": "職銜",
            "employer": "職銜",
            "job": "職銜",
            "職業": "職銜",
            "title": "職銜",
            "spouse": "配偶",
            "配偶": "配偶",
            "nationality": "國籍",
            "citizenship": "國籍",
            "country": "國籍",
            "國籍": "國籍",
            "party": "政黨",
            "education": "教育背景",
            "educate": "教育背景",
            "母校": "教育背景",
            "教育程度": "教育背景",
            "alma_mater": "教育背景",
            "alma mater": "教育背景",
            "address": "地址",
            "居住地": "居住地",
            "resident": "居住地",
            "language": "語言",
            "dialect": "語言",
            "religion": "宗教",
            "parents": "父母",
            "father": "父母",
            "mother": "父母",
            "children": "子女",
            "website": "網站",
            "awards": "獎項",
            "honours": "獎項",
            "獲獎": "獎項",
        }

        viewDICT = {
            "article": [{
                "title": directoryNameSTR,
                "content": self.AITLASKG["article"],
            }],
            "person": {},
            "location": {},
            "entity": {},
            "person2person":[], #關聯圖
            "event": []
        }
        # 接 Articut
        ## 時間基準
        baseTimeSTR: str = ""
        baseTimeLIST: list[str] = G_baseTimePAT.findall(viewDICT["article"][0]["content"])
        if len(baseTimeLIST)>0:
            baseTimeSTR = self._convertRoc2Iso(baseTimeLIST[-1])

        articutResultDICT: dict = CNA_Articut.parse(inputSTR=viewDICT["article"][0]["content"], level="lv3")

        # Person
        for person in self.AITLASKG["person"]:
            viewDICT["person"][person] = {}
            for key in self.AITLASKG["person"][person]:
                if key in translatePersonDICT.keys():
                    # viewDICT["person"][person][translateDICT[key]] = self.AITLASKG["person"][person][key]
                    valueSET: set = set()
                    for itemSTR in self.AITLASKG["person"][person][key]:
                        for x in self._listPacker(translatePersonDICT[key], itemSTR):
                            valueSET.add(x)

                    viewDICT["person"][person][translatePersonDICT[key]] = list(valueSET)
        
        ## 比對 Articut
        personLIST: list[str] = [
            "person",
            "people"
        ]
        for person_s in personLIST:
            ### person
            if f"KNOWLEDGE_{person_s}" in articutResultDICT["CNA_tag"]:
                for key_s, value_l in articutResultDICT["CNA_tag"][f"KNOWLEDGE_{person_s}"].items():
                    viewDICT["person"][key_s] = {}
                    for value_s in value_l:
                        viewDICT["person"][value_s] = {}

        # Location
        for locationSTR in self.AITLASKG["location"]:
            viewDICT["location"][locationSTR] = {}
            for keySTR, dataSTR in self.AITLASKG["location"][locationSTR].items():
                viewDICT["location"][locationSTR].update({
                    keySTR: [dataSTR]
                })

        ## 比對 articut
        locationLIST: list[str] = [
            "city",
            "country",
            "internationalLocation",
            "JapanCity",
            "lake",
            "MalaysiaCity",
            "river",
            "ThailandCity",
            "TWAdminDistrict",
            "TWBridge",
            "TWDam",
            "TWMountains",
            "TWRiver",
            "TWTunnel",
            "VietnamCity"
        ]
        for location_s in locationLIST:
            ### location
            if f"KNOWLEDGE_{location_s}" in articutResultDICT["CNA_tag"]:
                for key_s, value_l in articutResultDICT["CNA_tag"][f"KNOWLEDGE_{location_s}"].items():
                    viewDICT["location"][key_s] = {}
                    for value_s in value_l:
                        viewDICT["location"][value_s] = {}

        # Entity
        for nerSTR in self.AITLASKG["entity"]:
            viewDICT["entity"][nerSTR] = {}
            for keySTR, dataSTR in self.AITLASKG["entity"][nerSTR].items():
                viewDICT["entity"][nerSTR].update({
                    keySTR: [dataSTR],
                })

        ## 比對 Articut
        entityLIST: list[str] = [
            "adminAgency",
            "airlines",
            "airport",
            "award",
            "band",
            "Baseball",
            "chief",
            "CNGov",
            "company",
            "correctionalInstitution",
            "department",
            "emergingStockCompany",
            "fishingPort",
            "foundation",
            "hospital",
            "hotels",
            "JPGov",
            "medicalSpecialty",
            "NBA_Teams",
            "newsAgency",
            "newsChannel",
            "newspapers",
            "NFL_Teams",
            "nightmarket",
            "organization",
            "party",
            "pharmacyTW",
            "pttCompanyAlias",
            "scenery",
            "school",
            "sportsAssociations",
            "stockExchange",
            "transportation",
            "TWBank",
            "TWBasketball",
            "TWGov",
            "TWHikingTrail",
            "TWIndustrialPark",
            "TWInternetMedia",
            "TWJudicial",
            "TWMRT",
            "TWPresidentialOffice",
            "TWProcuratorate",
            "TWScenery",
            "TWSchool",
            "TWSpecLocations",
            "TWTelevision",
            "TWTVChannel",
            "TWUniversity",
            "TWVolleyball",
            "typhoon",
            "unitedNationsSystem",
            "weapon",
            "webplatform",
            "WNBA_Teams"
        ]

        for entity_s in entityLIST:
            if f"KNOWLEDGE_{entity_s}" in articutResultDICT["CNA_tag"]:
                for key_s, value_l in articutResultDICT["CNA_tag"][f"KNOWLEDGE_{entity_s}"].items():
                    viewDICT["entity"][key_s] = {}
                    for value_s in value_l:
                        viewDICT["entity"][value_s] = {}

        #人物關聯圖
        #tempDICT = tempfile.NamedTemporaryFile(mode="w+")
        #udLIST = [e for e in viewDICT["entity"].keys()]
        #json.dump({"_Entity":udLIST}, tempDICT, ensure_ascii=False)
        #tempDICT.flush()
        #resultDICT = articut.parse(self.AITLASKG["article"], userDefinedDictFILE=tempDICT.name)
        #print(resultDICT["result_pos"])
        #p2pPatLIST = [re.compile(r"<ENTITY_person>[^<]+</ENTITY_person>.+<ACTION_verb>[^<]+</ACTION_verb>.+<ENTITY_person>[^<]+</ENTITY_person>"),

        #              ]

        # event
        knowledgeSentenceDICT: dict[str, str] = self._parseArticutKnowledgeSentence(articutResultDICT, baseTimeSTR=baseTimeSTR)
        
        ## 接LLM
        for key_s in knowledgeSentenceDICT.keys():
            result = self._callLLM2GenContent(sentenceSTR=key_s)
            for m in G_dictPAT.finditer(result):
                dictSTR: str = m.group()
                # 找到子結構
                sourceLIST: list[str] = G_sourcePAT.findall(dictSTR)
                sourceSTR: str = ""
                if len(sourceLIST)>0:
                    sourceSTR = purgePat.sub("", sourceLIST[0])

                targetLIST: list[str] = G_taregetPAT.findall(dictSTR)
                targetSTR: str = ""
                if len(targetLIST)>0:
                    targetSTR = purgePat.sub("", targetLIST[0])

                labelLIST: list[str] = G_labelPAT.findall(dictSTR)
                labelSTR: str = ""
                if len(labelLIST)>0:
                    labelSTR = purgePat.sub("", labelLIST[0])

                metaDataLIST: list[str] = G_metaDataPAT.findall(dictSTR)
                metaDataSTR: str = ""
                if len(metaDataLIST)>0:
                    metaDataSTR = purgePat.sub("", metaDataLIST[0])

                encounterTimeSTR = knowledgeSentenceDICT[key_s]
                
                # 合成
                if sourceSTR in key_s and targetSTR in key_s and labelSTR in key_s:
                    lableArticutResult: dict = articut.parse(labelSTR)
                    if "ACTION" in lableArticutResult["result_obj"][0][0]["pos"]:
                        dictDICT: dict[str, str] = {
                            "source": sourceSTR,
                            "target": targetSTR,
                            "label": labelSTR,
                            "metaData": metaDataSTR,
                            "encounter_time": encounterTimeSTR
                        }

                        viewDICT["event"].append(dictDICT)
        
        self.viewDICT = viewDICT

        return viewDICT

    # <Please Ignroe createKG for now. 2025.06.20>
    def createKG(
        self,
        inputSTR,
        KG_FilePath=None,
        KG_FileName="default.ait",
        userDefinedDICT=None,
    ):
        if KG_FilePath == None:
            print("[AItlas]: KG_FilePath is needed!")
            return None
        if KG_FileName.endswith(".ait"):
            pass
        else:
            KG_FileName = KG_FileName + ".ait"

        self.posLIST = []
        self.splitLIST = []
        resultDICT = self.articut.parse(inputSTR, userDefinedDictFILE=userDefinedDICT)
        for i in resultDICT["result_pos"]:
            if len(i) > 1:
                self.posLIST.append(i)
            else:
                self.splitLIST.append(i)
        self.splitLIST = list(set(self.splitLIST))
        # print(self.posLIST)
        self.extract_person()
        # self._getPersonKG(inputSTR)
        return None

    def extract_person(self):
        self.personDICT = {}
        for i in self.posLIST:
            for person in self.personNamePAT.findall(i):
                self.personDICT[person] = {
                    "alias": [],
                    "address": [],
                    "affiliation": [],
                    "award": [],
                    "birth_date": None,
                    "birth_place": [],
                    "death_date": None,
                    "death_place": [],
                    "biological_gender": [],
                    "body_height": [],
                    "body_weight": [],
                    "job_title": [],
                    "nationality": [],
                    "parent": [],
                    "sibling": [],
                    "child": [],
                    "spouse": [],
                    "skills": [],
                    "education": [],
                    "event_log": [],
                    "description": [],
                    "raw_data": [],
                }

        for i in self.posLIST:
            # job_title
            jobtitle = [j.groups() for j in self.jobtitlePAT.finditer(i)]
            if jobtitle != []:
                if (
                    purgePat.sub("", jobtitle[0][0])
                    not in self.personDICT[jobtitle[0][-1]]["job_title"]
                ):
                    self.personDICT[jobtitle[0][-1]]["job_title"].append(
                        purgePat.sub("", jobtitle[0][0])
                    )
                    # nationality
                    nationality = []
                    nationality = self.aitlas_get_all(
                        purgePat.sub("", jobtitle[0][0]), "country"
                    )
                    if nationality != []:
                        self.personDICT[jobtitle[0][-1]]["nationality"].extend(
                            nationality
                        )
                # parent
                parent = [j.groups() for j in self.parentPAT.finditer(i)]
                if parent != []:
                    self.personDICT[jobtitle[0][-1]]["parent"].append(
                        purgePat.sub("", parent[0][1])
                    )
                # sibling
                sibling = [j.groups() for j in self.siblingPAT.finditer(i)]
                if sibling != []:
                    self.personDICT[jobtitle[0][-1]]["sibling"].append(
                        purgePat.sub("", sibling[0][1])
                    )
                # spouse
                spouse = [j.groups() for j in self.spousePAT.finditer(i)]
                if spouse != []:
                    self.personDICT[jobtitle[0][-1]]["spouse"].append(
                        purgePat.sub("", spouse[0][2])
                    )

    def person_alias(self):
        return None

    def aitlas_get_all(self, inputSTR, keySTR):
        aitlasURL = "https://api.droidtown.co/aitlas/api/"
        payload = {
            "username": accountDICT["username"],
            "aitlas_key": accountDICT["aitlas_key"],
            "func": ["get_all"],
            "input_str": inputSTR,
            "data": {},
        }
        response = requests.post(aitlasURL, json=payload).json()
        return response["results"][keySTR]

    def createLokiProject(self, utteranceLIST):
        url = "https://api.droidtown.co/Loki/Call/"  # 線上版 URL
        projectSTR = "aitlas_dev"
        payload = {
            "username": accountDICT[
                "username"
            ],  # 這裡填入您在 https://api.droidtown.co 使用的帳號 email。     Docker 版不需要此參數！
            "func": "create_project",
            "data": {
                "name": projectSTR,  # 這裡填入您想要在 Loki 上建立的專案名稱
            },
        }
        response = requests.post(url, json=payload).json()
        lokiKey = response["loki_key"]
        payload = {
            "username": accountDICT[
                "username"
            ],  # 這裡填入您在 https://api.droidtown.co 使用的帳號 email。     Docker 版不需要此參數！
            "loki_key": lokiKey,  # 這裡填入您在 https://api.droidtown.co 登入後取得的 loki_key。 Docker 版不需要此參數！
            "project": projectSTR,  # 專案名稱 (請先在 Loki 的設定網頁裡建立一個 Project 以便取得它的專案金鑰 (loki_key)
            "intent": "ait_person",  # 意圖名稱
            "func": "create_intent",
            "data": {"type": "basic"},  # 意圖類別
        }
        response = requests.post(url, json=payload).json()
        for i in range(0, len(utteranceLIST), 20):
            payload = {
                "username": accountDICT[
                    "username"
                ],  # 這裡填入您在 https://api.droidtown.co 使用的帳號 email。     Docker 版不需要此參數！
                "loki_key": lokiKey,  # 這裡填入您在 https://api.droidtown.co 登入後取得的 loki_key。 Docker 版不需要此參數！
                "project": projectSTR,  # 專案名稱 (請先在 Loki 的設定網頁裡建立一個 Project 以便取得它的專案金鑰 (loki_key)
                "intent": "ait_person",  # 意圖名稱
                "func": "insert_utterance",
                "data": {"utterance": utteranceLIST[i : i + 20]},
            }
            response = requests.post(url, json=payload).json()


if __name__ == "__main__":
    longText = """"""


    # longText = """中東夙敵以色列和伊朗空戰進入第8天。以色列總理尼坦雅胡今天矢言「消除」伊朗構成的核子和彈道飛彈威脅。
    # 法新社報導，尼坦雅胡（Benjamin Netanyahu）在南部城巿俾什巴（Beersheba）告訴記者：「我們致力於信守摧毀核威脅的承諾、針對以色列的核滅絕威脅。」伊朗今天的飛彈攻勢擊中當地一間醫院。"""
    aitlas = AItlas()

    topicSTR: str = "京華城MINI"

    KG = aitlas.scan(longText)
    # pprint(KG)

    view = aitlas.aitlasViewPacker(directoryNameSTR=topicSTR)
    aitlas.view(directoryNameSTR=topicSTR)
    # isPersonBool = alias.is_person(entity, utteranceLIST) #=>Maybe
    # isLocation = alias.is_location(entity, utteranceLIST)
    # print("{} 是 Person 嗎？{}".format(entity, isPersonBool))
