#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# 把 AItlasView 加進 path
import sys
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
import re

purgePat = re.compile("</?[a-zA-Z]+(_[a-zA-Z]+)?>")

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
from requests import post
from pprint import pprint

import os

BASEPATH = os.path.dirname(os.path.abspath(__file__))
actualDIR: Path = Path(__file__).resolve().parent
newAItlasDirPATH = actualDIR / "AItlasResult"
newAItlasDirPATH.mkdir(exist_ok=True, parents=True)

try:
    with open("{}/AItlasAPI/account.info".format(BASEPATH), encoding="utf-8") as f:
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
        sourceCssDirPATH: Path = actualDIR.parent / "AItlasView" / "static" / "css"
        targetCssDirPATH: Path = newAItlasDirPATH / directoryNameSTR / "static" / "css"
        targetCssDirPATH.mkdir(exist_ok=True, parents=True)
        
        for filePATH in sourceCssDirPATH.glob("*.css"):
            # 取內容
            contentSTR: str = filePATH.read_text(encoding="utf-8")

            # 在目標資料夾建立檔案
            newFilePATH: Path = targetCssDirPATH / filePATH.name
            newFilePATH.write_text(contentSTR, encoding="utf-8")

        ### static/js
        sourceJsDirPATH: Path = actualDIR.parent / "AItlasView" / "static" / "js"
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
                # "events": self.viewDICT["entity"],
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
        sourceHtmlPATH: Path = actualDIR.parent / "AItlasView" / "static" / "index.html"
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
            #json.dump(viewDICT["person2person"], f, ensure_ascii=False, indent=4)

        ### 寫 event.json
        #with  open(newAItlasKgPATH / "event.json", "w", encoding="utf-8") as f:
            #json.dump(viewDICT["event"], f, ensure_ascii=False, indent=4)
        return None


    def _matchAItlasPerson(self, lang):
        personDICT = {}
        if lang.lower() == "tw":
            personDICT = json.load(
                open(
                    f"{BASEPATH}/AItlas_TW/wikipedia/AItlas_wiki_person.json",
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
                    f"{BASEPATH}/AItlas_TW/wikipedia/AItlas_wiki_location.json",
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
                    f"{BASEPATH}/AItlas_TW/wikipedia/AItlas_wiki_entity.json",
                    "r",
                    encoding="utf-8"
                )
            )
        # elif lang.lower() == "en":
        # locationDICT = json.load(open("AItlas_EN/wikipedia/AItlas_wiki_location.json", "r", encoding="utf-8"))
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

        # Location
        for locationSTR in self.AITLASKG["location"]:
            viewDICT["location"][locationSTR] = {}
            for keySTR, dataSTR in self.AITLASKG["location"][locationSTR].items():
                viewDICT["location"][locationSTR].update({
                    keySTR: [dataSTR]
                })

        # Entity
        for nerSTR in self.AITLASKG["entity"]:
            viewDICT["entity"][nerSTR] = {}
            for keySTR, dataSTR in self.AITLASKG["entity"][nerSTR].items():
                viewDICT["entity"][nerSTR].update({
                    keySTR: [dataSTR],
                })


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
        # 等peter
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
        response = post(aitlasURL, json=payload).json()
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
        response = post(url, json=payload).json()
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
        response = post(url, json=payload).json()
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
            response = post(url, json=payload).json()


if __name__ == "__main__":
    longText = """台北地方法院審理京華城案，5月13日提訊威京集團主席沈慶京（前）出庭。（中央社檔案照片）（中央社記者林長順台北10日電）台北地方法院審理京華城案今天開庭勘驗相關會議錄音。沈慶京律師當庭聲請具保停押，法官請律師到醫院與沈慶京商討交保金額，且不得低於過去金額。北院預計最快下午裁定。京華城案再度開庭，北院提訊在押的前台北市長、前台北市長辦公室主任李文宗，傳喚前台北市都發局長黃景茂，勘驗北市都發局專家學者諮詢會議、都委會第775次會議、專案小組會議錄音逐字稿。威京集團主席因病治療請假未到庭，由律師代理出庭。律師在開庭時指出，沈慶京羈押至今健康狀態不佳，目前由台北看守所戒護下在台大醫院戒護就醫，且有開刀的必要，因此向北院聲請具保停押。法官指出，經函詢台北醫院，醫院認為沈慶京確實有動手術的必要，台北看守所也回函有法警戒護人力問題，法官准予律師中午前往醫院與沈慶京商談保證金額，但不能少於過去法院裁定的金額。法官也要律師與沈溝通不要以醫院治療為理由拒絕電子監控，表示過去曾有重大人犯因以疾病因素拒絕電子監控但人逃亡，「這讓法院承受很大壓力」。（編輯：方沛清）1140710",
    高雄市副市長林欽榮（右）16日在高雄市議會接受媒體聯訪，回應京華城案相關議題，強調自己對前台北市長柯文哲沒有狹怨報復。左為高雄市長陳其邁。中央社記者林巧璉攝  114年5月16日（中央社記者郭建伸、林巧璉台北16日電）北院審理京華城案引發民眾黨與高雄市政府為容積獎勵隔空交火。民眾黨今天批評高雄市府避重就輕、惡意誤導，呼籲勿配合政客炒作聲量；高雄市副市長林欽榮說，京華城是單一財團小基地，採取所謂自創容積，無法律授權。北院昨天開庭審理京華城案，前民眾黨主席柯文哲的臉書以「綠能，你不能；陳其邁可以，柯文哲不能」為題表示，「高雄亞灣經貿開發計畫不管是營運或企業總部給20%容獎，都不可以。」高雄市府回應，政黨人士混淆視聽，譴責以司法調查弊案類比國家重大經建亞灣2.0。民眾黨今天透過聲明表示，根據「都市計畫法高雄市施行細則」第24條之3規定項目與容積獎勵上限，取得經濟部核發的「營運總部」認定函，法定容積5%，但高雄市府新聞稿中卻未正面回應昨天柯文哲委任律師質疑「為何給予容積獎勵20%，整整比施行細則所規定之上限5%多出3倍？」民眾黨質疑，高雄市政府心虛閃躲、避重就輕，給予容積獎勵的項目是哪些，請高雄市政府具體回應，應依林欽榮所言「容積是公共財」，審議不可黑箱。民眾黨也抨擊，高雄市府新聞稿提及有關京華城部分有諸多錯誤，表格更是惡意誤導，因為京華城從頭到尾都不是「準用都更」，是根據「都市計畫法第24條」由地主自行提出細部計畫申請，台北市政府則依「台北市都市計畫施行自治條例」25條給予容積獎勵，何來「違法準用都更條例」。民眾黨指出，京華城計畫內容具備「公益性、對價性」且提供市府回饋，通過都委會審議才得到容積獎勵，肩負帶動台北市南松山地區與附近老舊街廓有更新活化的任務、並非單一地主受惠。民眾黨抨擊，高雄市政府的表格在土地面積欄位寫「亞灣計畫區為國有土地」是刻意迴避，實際上以「國家重大經建計畫」做包裝，亞灣開發後，原國有土地皆轉賣給私有企業或財團進行開發，而且高雄市政府在上位計畫還沒通過前，就搶先給容積，對照林欽榮對京華城案的攻擊，明顯雙標，根本是「我能你不能」。不過，民眾黨也指出，高雄市政府聲明稿唯一有參考價值的地方，是證實細部計畫可以給容積獎勵，林欽榮在開庭時，不斷鬼打牆稱細部計畫不能給容積獎勵，多給一平方米就是圖利，但亞灣2.0計畫正是林欽榮透過細部計畫給予容積獎勵的實際個案，甚至突破5%上限給到20%。高雄市副市長林欽榮上午在高雄市議會接受媒體聯訪表示，所有容積獎勵須依法授權，亞灣地區容積合法合規，京華城非都更區，僅是單一財團小基地，「這是天差地別」。他說，亞灣地區早在民國91年依都市計畫程序，完全就劃定為公劃公告都市更新地區，對比京華城根本不是都市更新地區，亞灣本來就可有1.5倍容積率使用。林欽榮表示，京華城是單一財團小基地1.6公頃，採取所謂自創容積，無法律授權；監察院2023年有糾正台北市政府、台北市都委會、台北市都發局，「亞灣與京華城是天差地別。亞灣2.0計畫完全是依法授權」。（編輯：謝佳珍）1140516"""


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
