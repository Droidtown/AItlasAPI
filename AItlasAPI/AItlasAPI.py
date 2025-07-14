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
#try:
from AItlasView.DjangoTest import importData as importData
#except:
    #from AItlasView.view import view as aitlasView

import sqlite3
import tempfile
from typing import Union
from functools import reduce
from pprint import pprint
import re

import AItlasView.view

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
kgDIR: Path = actualDIR / "AItlasView" / "rawData"


try:
    with open("{}/AItlasAPI/account.info".format(BASEPATH), encoding="utf-8") as f:
        accountDICT = json.load(f)
    articut = Articut(username=accountDICT["username"], apikey=accountDICT["api_key"])
except:
    articut = Articut()


class AItlas:
    def __init__(self, username="", apikey=""):
        self.articut = Articut(username=username, apikey=apikey)

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

    def view(self, directoryNameSTR: str):
        # post Django
        importData(article=self.viewDICT["article"], location=self.viewDICT["location"], ner=self.viewDICT["entity"], people=self.viewDICT["person"], event=self.viewDICT["event"])
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
                "articut_content": {},
                "published_at": "",
                "url": "",
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

        # Ner
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

        # 存 AItlasKG
        newAItlasKgPATH: Path = kgDIR / directoryNameSTR / "data"
        newAItlasKgPATH.mkdir(exist_ok=True, parents=True)

        ## 寫 person.json
        with open(newAItlasKgPATH / "person.json", "w", encoding="utf-8") as f:
            json.dump(viewDICT["person"], f, ensure_ascii=False, indent=4)

        ## 寫 article.json
        with open(newAItlasKgPATH / "article.json", "w", encoding="utf-8") as f:
            json.dump(viewDICT["article"], f, ensure_ascii=False, indent=4)

        ## 寫 location.json
        with open(newAItlasKgPATH / "location.json", "w", encoding="utf-8") as f:
            json.dump(viewDICT["location"], f, ensure_ascii=False, indent=4)

        ## 寫 ner.json
        with open(newAItlasKgPATH / "entity.json",  "w", encoding="utf-8") as f:
            json.dump(viewDICT["entity"], f, ensure_ascii=False, indent=4)

        ##寫 人物圖 person2person.json
        #with open(newAItlasKgPATH / "person2person.json",  "w", encoding="utf-8") as f:
            #json.dump(viewDICT["person2person"], f, ensure_ascii=False, indent=4)

        ## 寫 event.json
        #with  open(newAItlasKgPATH / "event.json", "w", encoding="utf-8") as f:
            #json.dump(viewDICT["entity"], f, ensure_ascii=False, indent=4)

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
    （中央社記者黃麗芸台北3日電）臉書粉專「迷因台式民主」版主戴男涉將京華城案11名承辦檢察官姓名和照片上網公開，北市警方今天深夜將他依涉恐嚇危安罪移送北檢複訊，另自台中帶回合成恐嚇照的情侶檔偵辦。台北地院審理京華城案，前北市副市長彭振聲妻子墜樓身亡引發社會關注。有特定人士在網路社群平台張貼承辦京華城案檢察官姓名、照片，甚至合成潑灑血跡的畫面，並搭配「命債命還」、「記住他們的名字跟臉」等仇恨、威嚇性圖文。臉書粉專「迷因台式民主」今天上午發文表示，「把司法官的照片找出來公布是我一個人幹的，跟民眾黨、鬼針草都沒關係。望周知」。台北市警察局刑事警察大隊偵辦此案，並通知「迷因台式民主」版主、39歲戴姓男資訊工程師於下午3時許到案說明。據悉，戴男坦承是自己搜索相關檢察官照片並上網公布，但否認有合成血跡並進行恐嚇情事。全案詢後，警方於深夜11時許將戴男依涉恐嚇危安罪移送台北地檢署複訊。針對有網友將戴男貼上網原圖加工合成再轉貼一事，警方也已鎖定涉案者身分，晚間自台中將涉案的41歲周男、林女情侶檔帶回偵辦中。（編輯：陳彥鈞）1140703網路出現針對京華城案檢察官的仇恨性圖文，台北地檢署指揮台北市刑警大隊、調查局偵辦。警方3日下午傳喚臉書粉專「迷因台式民主」版主、戴姓男工程師到案，並搜索戴男住處，深夜移送北檢複訊。中央社記者林長順攝 114年7月3日",
    （中央社記者葉素萍台北2日電）北市前副市長彭振聲妻子在高雄住處墜樓身亡，藍白指控司法迫害、押人取供。民進黨發言人吳崢今天說，若有政治人物或政黨刻意操作，趁機消費這起悲傷事件，惡意渲染，這是非常冷血、惡質的手法。北院審理京華城案，昨天傳喚北市前副市長彭振聲，他開庭前聽聞妻子過世痛哭失聲。民眾黨表示將全力協助彭振聲處理後續事宜，並支持捍衛清白；國民黨質疑司法押人取供。民進黨上午舉行「桃園送禮救罷免 打壓罷團出奧步」記者會。吳崢表示，全台灣人看到昨天這起悲劇，都相當不忍，也感受得到彭振聲心中的哀傷跟悲痛，民進黨要向彭振聲與家人致上哀悼之意，也希望這樣的事件不要被有心人士拿來利用。吳崢說，如果有政治人物或政黨刻意操作，趁機消費這起悲傷事件，進行惡意渲染，這是非常冷血、也是非常惡質的一種手法。（編輯：萬淑彰）1140702珍惜生命，自殺不能解決問題，生命一定可以找到出路。若須諮商或相關協助，可撥衛福部專線「1925」、生命線專線「1995」或張老師服務專線「1980」。",
    京華城案，台北地院28日表示，被告柯文哲等人涉犯本刑5年以上重罪，有逃亡及串供之虞，裁定6月2日起延押禁見2個月。高虹安（右1）28日因誣告案赴台灣高等法院，被問到柯文哲遭延押，她並無回應。中央社記者劉世怡攝 114年5月28日（中央社記者劉世怡台北28日電）遭停職的新竹市長高虹安被旅美教授陳時奮自訴誣告罪，一審判刑10月，經上訴，高等法院今天開庭。高虹安進入法院前，被問柯文哲在京華城案遭延押2個月的看法，她並無回應。全案緣於，不滿陳時奮於民國110年在臉書（Facebook）發文指出「被指導教授除名的高虹安」等言論，提告加重誹謗罪；陳時奮獲不起訴處分後，自訴高虹安誣告罪嫌。一審台北地方法院判決指出，高虹安明知博士論文有抄襲期刊論文情事，陳時奮發文指控內容與事實並無相悖，竟對陳時奮提告，具誣告的直接故意，依誣告罪判處10月徒刑；案經上訴，二審由台灣高等法院審理，審理期間，高虹安做無罪答辯，主張沒有捏造證據，並沒有誣告，陳時奮則請求重判。二審今天再度開庭，高虹安進入法院前，面對媒體提問，民眾黨前主席在京華城案遭延押2個月的看法，她並無回應，快步走進法院。（編輯：張銘坤）1140528",
    （中央社記者林長順台北20日電）台北地方法院審理京華城案，今天以證人身分傳喚台北市議員苗博雅，由檢辯交互詰問。由於前台北市長柯文哲等在押被告的羈押期限將至，合議庭將先後召開訊問庭，決定是否延長羈押。社會民主黨北市議員苗博雅在臉書（Facebook）上貼文指出，收到台北地方法院證人傳喚，今天上午就被告貪污等案件出庭作證。身為法律人，非常清楚依法作證是國民義務，既然收到法院傳喚通知，就會依法出席。對於檢辯雙方及法官提出的問題，一定據實以告。苗博雅表示，在民主國家，接受法院傳喚出庭，是很正常的事。法院是發現真實、追求公義的場所，身為證人的義務就是依據事實陳述。台北地檢署偵辦京華城案、柯文哲政治獻金案，去年12月26日依貪污治罪條例違背職務收受賄賂罪、圖利、公益侵占、背信等罪嫌，起訴柯文哲、威京集團主席等11人，並具體求處柯文哲總計28年6月徒刑。其餘被起訴的被告，包括前台北市長辦公室主任李文宗、前台北市副市長彭振聲、前台北市都發局長黃景茂、前台北市都委會執秘邵琇珮、國民黨台北市議員、應曉薇助理吳順民及張志澄、木可公司董事長李文娟、會計師端木正。檢方起訴時引用苗博雅於109年11月11日的市政總質詢，質疑柯文哲「京華城案不是都更、也不是危老，何以給予京華城公司比照都更、危老法令來申請獎勵」。檢察官在此案準備程序時，聲請傳喚苗博雅作證。另外，柯文哲、沈慶京、應曉薇、李文宗的羈押期限將至，北院今天也將先後訊問4名被告，決定是否延長羈押。（編輯：戴光育）1140520台北地方法院審理京華城案，20日以證人身分傳喚社會民主黨台北市議員苗博雅（前）出庭作證。中央社記者裴禛攝  114年5月20日",
    圖為去年12月京華城工地施工情況。（中央社檔案照片）（中央社記者林長順台北24日電）北檢偵辦京華城案，認為柯文哲等人涉違法圖利京華城案容積獎勵20%，聲請扣押京華城土地，台北地方法院3度裁准，高院3度發回。北院今天召開訊問庭，聽取檢方及鼎越開發公司主張。北院整理扣押案兩大爭點，包括容積獎勵是否為已實現的不法利益；再者，檢方計算的不法利益金額，相較於扣押土地本身，是否符合比例原則。檢方指出，京華城土地不法容積價值約新台幣121億元，小於土地價值142億元，並未未過度扣押，檢方聲請符合比例原則，扣押具有最後手段性，若不扣押，恐會轉移處分給他人，侵害國家追徵不法利得的權利。鼎越開發公司律師指出，京華城土地信託後向銀行團聯貸，地籍若被扣押，將構成聯貸案的違約要件，銀行團可以暫停撥款，已有銀行要求提前還款，若持續扣押，可能使京華廣場面臨成為爛尾樓的風險。律師表示，鼎越開發今年4月9日已向台北市都發局遞件申請變更設計，將容積率從840%降為728%，暫緩申請20%容積獎勵，北市府對外表示預估要3個月時間審查申請案，若通過變更，檢方所主張的犯罪利得就未實現，扣押問題也將不復存在。台北地檢署偵辦京華城案，認定前台北市長、前副市長彭振聲等人涉違法圖利行為，讓第三人的鼎越開發公司獲有建築容積獎勵率20%的不法利益，屬於犯罪所得應予沒收，經估算不法利益達新台幣111億7023萬6000元。為保全日後追繳，北檢向北院聲請扣押鼎越公司所有的台北市松山區西松段三小段156地號土地（京華城案土地）。北院一審、更一審均裁准，但遭台灣高等法院撤銷發回；北院更二審裁准扣押，鼎越公司不服提起抗告，高院今年2月間撤銷更二審裁定並發回更裁。（編輯：張銘坤）1140424",
    台北地方法院繼續審理京華城及政治獻金案召開準備程序庭，17日上午提訊在押的前台北市長柯文哲（中），這是柯文哲4月初在台北醫院手術後首次出庭。中央社記者鄭清元攝 114年4月17日（中央社記者劉世怡台北17日電）台北地院審理京華城案，今天提訊被告柯文哲，聚焦檢方聲請勘驗偵訊光碟駁斥「以不雅片威脅柯文哲認罪」。柯文哲說，完整偵訊光碟應全部公開，讓外界知道檢察官怎麼對付他。台北地檢署偵辦京華城案、政治獻金案，去年12月26日偵查終結，依貪污治罪條例違背職務收受賄賂罪、圖利、公益侵占、背信等罪起訴前台北市長柯文哲等11人，並具體求處柯文哲總計28年6月徒刑。台北地方法院3月20日開庭時，柯文哲指出，檢察官林俊言訊問時威脅、霸凌他，曾對他表示行動硬碟有不雅影片，若不坦承犯行就會交給法院公開，「我還差點被騙，想說是不是我被關太久，還好我們家陳佩琪家教甚嚴，不可能有不雅影片」。對此，台北地檢署駁斥不實指控，並向台北地院遞狀，聲請勘驗柯文哲的偵訊光碟及扣案行動硬碟，在法庭內公開行動硬碟的檔案內容，並就檢察官的訊問過程，還原事實真相。台北地院今天上午再度開準備程序庭，提訊柯文哲到庭，柯文哲說，偵訊光碟錄影都完整，應全部公開，當天檢察官林俊言在跟他打心理戰，他也知道，最後審判柯文哲的是台灣社會大眾，「讓社會大眾知道檢察官是怎麼對付我」。不過，辯護人鄭深元說，無論有無不雅照，均與本案無關，因此沒有勘驗必要。法官許芳瑜提及，今天開庭重點為確認檢辯雙方聲請詰問證人及調查證據，以及同案被告李文宗及李文娟請求調閱柯文哲手機及行動硬碟檔案，請檢辯及柯文哲表示意見。辯護人蕭奕弘及鄭深元主張，同案被告前台北市副市長彭振聲、前台北市都委會執秘邵琇珮及證人楊智盛，疑遭檢方不正訊問，有筆錄記載欠缺同一性，均沒有證據能力，尤其檢察官訊問彭振聲時提及「你現在甘願做余文」，明顯要彭振聲去咬柯文哲，涉不正訊問的情形情，也發生訊問邵琇珮時。蕭奕弘聲請勘驗涉不正訊問偵訊光碟，於法庭進行簡報時，二度當庭撥放彭振聲及邵琇珮被訊問影片，立即遭打斷，蕭奕弘主張身為矚目案件被告的律師，有義務讓社會大眾知道訊問狀況。許芳瑜表示，現在不是勘驗時間，還未准許勘驗及範圍，不應在今天聲請勘驗階段，就下結論指摘不正訊問及當庭播放；檢察官姜長志則說，今天不是律師個人舞台秀，檢辯雙方應努力說服法官。公訴檢察官表示，偵辦檢察官沒有不正訊問，其中彭振聲部分，檢方有必要告知依照貪污治罪條例第8條規定，被告自白有給予減刑或是免刑的可能，彭振聲沒覺得遭不正訊問，但柯文哲卻幫彭振聲說遭不正訊問，而且柯文哲現在主張彭振聲被不正訊問，等於是剝奪彭振聲減刑的機會。檢察官表示，當初訊問彭振聲，檢方提及不要再有下一個余文說法部分，是考量113年8月底查扣柯文哲的行動硬碟，裡頭工作簿記載「小沈 1500」，認為柯文哲涉收新台幣1500萬元賄賂，彭振聲應該不知情，不應替罪背鍋。許芳瑜諭知，合議庭審理案件依法審理，不會受到外界影響，一般相關案件，怎麼處理就怎麼處理，如果宣判的結果，檢方、被告不服，可以提起上訴救濟，現在為準備程序階段，請檢辯針對證據有無證明力表示意見。另一方面，許芳瑜提示扣案手機（編號A1-44）的照片並告知型號；柯文哲說，他不記得這支手機，可能關太久了，對手機沒印象，李文宗、李文娟要調手機的數位鑑識檔案，他同意，但是調閱行動硬碟（編號A1-37）部分，要他先看過之後，再表示意見。柯文哲強調，希望檢察官把所有扣案的資料都移到法院，並且都要給他一份存檔，避免被斷章取義；辯護人鄭深元補充，請法官注意，本案已起訴，所有電子檔檢方都應移交，檢方不應留存，避免會有不詳管道流出可能。此外，柯文哲準備3張講稿向法官表示，這是社會矚目案件，他在搞不清楚狀況下就被羈押至今8個月等語；法官回應，先處理檢辯進行證據能力爭點討論，結束後，會讓柯文哲在法庭內講。（編輯：李錫璋）1140417",
    前民眾黨主席柯文哲因腎結石致腎積水，2日戒護外醫至衛福部立台北醫院。（民眾提供）中央社記者王鴻國傳真 114年4月2日（中央社記者趙敏雅新北2日電）民眾黨前主席柯文哲今天進行輸尿管鏡手術取出結石。日前民眾黨主席黃國昌遞交申請為柯文哲爭取自費延醫。據了解，台北看守所今天晚間7時許，已將審核結果函覆柯文哲律師團。羈押中的涉京華城案、政治獻金案等遭起訴，近期數次戒護就醫。台灣民眾黨主席3月29日傍晚到台北看守所遞申請書，表明為柯文哲爭取自費延醫。北所昨天表示，依規定審核，會將柯文哲最新健康情形，併由專業醫事人員審酌後再回覆。據指出，北所晚間7時許已將審核結果函覆給柯文哲律師團。對此，北所副所長陳啟森回應中央社記者詢問時表示，相關細節不便說明。柯文哲今天上午7時在台北看守所人員戒護下，到台北醫院進行輸尿管鏡手術，順利取出結石並轉入戒護病房。院方表示，柯文哲希望今天出院，但尊重醫療建議，將住院觀察1天，以確保術後恢復順利。柯文哲妻子陳佩琪受訪時說，她昨天下午2時許接獲北所電話通知，只知道柯文哲要開泌尿道的刀，「其他事情我一概都不知道」。北所晚間發布新聞稿指出，北所昨天獲悉柯文哲後續所需接受的醫療行為後，即依規定報請被告繫屬法院獲准，並通知家屬，惟個案醫療細節與事前的住院規劃等均涉及醫療專業，所方恪遵醫院安排，配合醫囑並維護當事人隱私，歉難事先說明。北所表示，今天上午依醫囑戒護柯文哲接受治療，並辦理住院手續後，再行聯繫家屬，目前已由醫院密集提供柯文哲所需照護。（編輯：蕭博文）1140402",
    台北地方法院審理京華城案，1日再開準備程序庭，傳喚前台北市副市長彭振聲出庭。中央社記者趙世勳攝  114年4月1日（中央社記者林長順台北1日電）台北地方法院審理京華城案，今天再開準備程序庭，傳喚應曉薇助理吳順民、前台北市副市長彭振聲。2人涉犯收賄、圖利等罪，在偵查期間均被檢方聲押禁見獲准，先後以新台幣500萬元交保。台北地檢署偵辦京華城案、柯文哲政治獻金案，去年12月26日依貪污治罪條例違背職務收受賄賂罪、圖利、公益侵占、背信等罪嫌，起訴前台北市長柯文哲、沈慶京等11人，並具體求處柯文哲總計28年6月徒刑。除柯、沈外，其餘被起訴的被告還包括前台北市長辦公室主任李文宗、彭振聲、前台北市都發局長黃景茂、前台北市都委會執秘邵琇珮、國民黨台北市議員應曉薇、吳順民、京華城監察人張志澄、木可公司董事長李文娟、會計師端木正。吳順民被控收受沈慶京賄賂363萬5484元，與應曉薇共同要求北市府將京華城公司陳情案送入都委會研議，濫用議員權力干涉公務員行使職權，並持續護航鼎越公司取得最高20%容積獎勵的建造執照。北檢依貪污治罪條例違背職務之行為收受賄賂罪起訴吳順民。彭振聲則涉嫌與柯文哲、沈慶京共犯圖利京華城公司，被檢方依貪污治罪條例主管監督事務圖利罪起訴。檢察官審酌彭振聲犯後坦承犯行，偵查中自白犯罪，向法院求刑3年。彭振聲於1月23日首度開庭時表示，偵查中該講的都講了，該認罪的也都認了，「我沒有要翻供」，對於檢察官起訴沒有意見。（編輯：張銘坤）1140401",
    前台北市長柯文哲（右2）1月22日在多名法警戒護下，到醫院探望當時仍在住院中的父親。（中央社檔案照片）（中央社記者趙敏雅新北1日電）民眾黨前主席柯文哲曾於3月25、29日戒護就醫，北所表示，今天上午針對柯文哲醫療需求安排，按醫囑戒護到醫院回診檢查，已於午間返所；醫療情形屬個人隱私，無法說明。涉京華城案、政治獻金案遭台北地檢署依貪污罪等起訴，目前羈押台北看守所。北所下午發布文字指出，針對柯文哲醫療需求安排，上午按醫囑戒護到醫院回診檢查，使其受妥適健康照護，並在午間返回北所。針對柯文哲健康狀況，北所表示，個案醫療情形，均屬個人隱私，無法說明。有關民眾黨主席遞送的自費延醫申請，台北看守所副所長陳啟森下午回應中央社記者時說，依規定審核，會將柯文哲最新健康情形，併由專業醫事人員審酌後再回覆。柯妻陳佩琪日前在記者會上說，柯文哲血尿，可能會腎臟損傷，有緊急就醫需求。北所3月29日發布文字說明，指柯文哲已於17日、20日、21日接受專業醫師看診，依醫囑於25日上午戒護外醫檢查及治療，經醫院評估未達住院標準後返所照護。北所昨天發布新聞稿指出，所方3月29日晚間接獲柯文哲反映身體不適後，依照相關生理數值緊密監測，雖未發現異常，但仍以最嚴謹標準，審慎評估後續就醫需求，戒送醫院進行多項檢查。對於柯文哲3月29日晚間11時57分返所，北所說明，經醫師診察柯文哲身體狀況穩定，未達到留院觀察標準，並向柯文哲確認無任何不適後，才返回北所照護。另外，北所表示，針對柯文哲需求安排後續就診與檢查規劃，確保能獲充足醫療資源，維護其收容期間健康。（編輯：黃名璽）1140401",
    （中央社記者陳俊華台北1日電）媒體報導，民眾黨前主席柯文哲今天第三度戒護就醫，預計明天進行手術。民眾黨說，透過北所新聞稿無從得知柯文哲實際身體狀況與就醫原因，懇請相關主責機關，儘速核准讓柯文哲自費延醫。涉京華城案、政治獻金案遭台北地檢署依貪污罪等起訴，目前羈押台北看守所。TVBS新聞網報導，柯文哲今天上午去部北醫院做超音波，發現之前診斷的尿道結石並沒有完全排出，會堵塞輸尿管導致水腎，因此安排明天進行手術。台灣民眾黨透過媒體群組表示，針對柯文哲上午再次戒護就醫，透過台北看守所提供的新聞稿內容，民眾黨無從得知柯文哲實際身體狀況，也無法了解這次戒護就醫的原因為何，甚至無法確認柯文哲是否得到完整、妥善的治療。民眾黨指出，3月29日已正式提出自費延醫的請求，希望由專業醫師給予柯文哲更全面的醫療照顧，儘管台北看守所提及「已針對其需求安排後續就診與檢查規劃」，民眾黨仍希望給予柯文哲妥善、完整的醫療照顧。因此，懇請相關主責機關，儘速核准讓柯文哲自費延醫。（編輯：翟思嘉）1140401",
    （中央社記者劉建邦台北4日電）臉書「迷因台式民主」版主戴姓男子涉上網公開承辦京華城案的11名檢察官姓名與照片，台北市警方逮人送辦。警方今天另將合成恐嚇照的周姓情侶檔，依恐嚇危安罪嫌移送北檢偵辦。台北地院審理京華城案期間，前台北市副市長彭振聲妻子墜樓身亡，引發社會關注。有特定人士在社群平台張貼承辦京華城案的檢察官姓名、照片，甚至合成潑灑血跡的畫面，並搭配「命債命還」、「記住他們的名字跟臉」等仇恨、威嚇性圖文。此外，臉書（Facebook）粉專「迷因台式民主」則發文「把司法官的照片找出來公布是我一個人幹的，跟民眾黨、鬼針草都沒關係。望周知。」台北市警察局刑事警察大隊偵辦此案，並通知版主、39歲戴姓男資訊工程師到案說明。網路出現針對京華城案檢察官的仇恨性圖文，台北地檢署指揮台北市刑警大隊、調查局偵辦。警方3日下午傳喚臉書粉專「迷因台式民主」版主、戴姓男工程師到案，並搜索戴男住處，深夜移送北檢複訊。中央社記者林長順攝 114年7月3日據悉，戴男坦承自行搜索檢察官照片並上網公布，但否認有合成血跡並進行恐嚇情事。警詢後依涉恐嚇危安罪將他移送台北地檢署複訊。檢方今晨聲請羈押禁見。另警方調查發現，有網友把戴男上網原圖加工合成後轉傳社群平台，警調鎖定住台中市的41歲周姓男子與林姓女子，2人為情侶，警方昨晚前往台中將2人帶返北市偵訊，並於今天下午依恐嚇危安罪嫌將其移送北檢偵辦。（編輯：黃世雅）1140704珍惜生命，自殺不能解決問題，生命一定可以找到出路。若須諮商或相關協助，可撥衛福部專線「1925」、生命線專線「1995」或張老師服務專線「1980」。",
    新台幣兌美元匯率3日強升1.91角，收在28.828元，睽違3年多再現低於29元的收盤價位。圖為新台幣與美元鈔票。（中央社檔案照片）新台幣強升1.91角穩坐最強亞幣 暌違3年收盤再現28元美國與越南達成貿易協議，淡化經濟前景的不確定性，金融市場正面表態，美股領漲，台灣股市與幣值跟著上揚，新台幣兌美元匯率收在28.828元，強升1.91角，睽違3年多，再現低於29元的收盤價。外匯交易員指出，近日新台幣啟動強勁升勢，但央行每天持續在盤中各點位提供流動性，只是國際因素推動新台幣往升值強勁，同時出口表現亮麗，基本面也為升勢增添柴火。（看完整報導）24藍委罷免案7月26日投票 中選會公布罷免理由、答辯書中選會3日公告24名國民黨立委與遭停職的新竹市長高虹安罷免案的罷免理由書與答辯書。罷免理由主要包括由傅崐萁領導的國民黨立院黨團成員強行通過各種修法、亂刪政府預算致國會大亂，或甚至立場傾向意圖侵犯台灣的中共政權，面臨罷免的立委和高虹安則一一提出答辯。中央社整理完整罷免理由及答辯書，以及後續可能發展，帶你一次看懂。（看完整報導）德媒：比亞迪產能嚴重過剩 中國電動車泡沫即將破裂德國商報近日以「中國電動車泡沫即將破裂」為題、「比亞迪正處於泡沫中」為副標題的評論指出，中國有全球最大的電動汽車市場，但恐怕也是最脆弱的。西方汽車製造商早已明確認為，中國電動車生產體系已經過熱，而前面就是大爆炸。評論提到，中國電動車市場龍頭比亞迪的這一徵兆最為明顯，儘管比亞迪是全球最大的電動車製造商，但其成長戰略日益動搖，在市場動能減弱下仍全力生產，結果造成了巨大的產能過剩。（看完整報導）數發部打詐納管Threads 9月15日生效數發部宣布，考量台灣使用者占比及網路平台被利用在刊登詐騙廣告的風險，確定將Threads納入管理，由於相關系統調整需要時間，法遵要求於9月15日起生效，Threads成為數發部詐防條例下，第7個納管的網路廣告平台。Threads母公司Meta表示，正在檢視「詐欺犯罪危害防制條例」（詐防條例）中納管Threads的相關細節。（看完整報導）涉恐嚇京華城案檢察官 粉專版主到案、查獲合成照犯嫌台北地院審理京華城案之際，台北市前副市長彭振聲妻子墜樓身亡，事後網路上出現刊載承辦京華城案檢察官姓名及照片，被合成潑灑血跡，並寫下「命債命還」等字眼，就連承辦法官的姓名和照片也被公開。北市警方3日通知「迷因台式民主」版主、戴姓男工程師到案說明，晚間移送北檢，另自台中帶回合成恐嚇照的情侶檔偵辦。（看完整報導）Shein先調高價格再打折騙消費者 法國重罰13.6億法國反托拉斯機構展開近一年反競爭調查後，3日以包括誤導性折扣等「欺騙性商業行為」為由，宣布對中國跨境電商平台Shein罰款創紀錄的4000萬歐元（約新台幣13億6280萬元）。該機構指出，根據法國法規，參考價為零售商提供折扣前30天內的最低價，Shein未考慮先前的價格，有時先提高價格再推出折扣，違反這項規定。（看完整報導）法國人為何抗拒冷氣？僅4分之1家戶安裝 關鍵在文化習慣與法規6月30日熱浪席捲歐洲，今年熱浪來得異常早，歐洲各城市高度警戒。西班牙野火和其他地方2日再奪6條性命。聯合國氣候機構指出，都巿熱島效應在酷熱天氣期間可能導致更多人死亡。這波熱浪讓法國抗拒冷氣的文化再受關注。據統計，僅25%法國人有冷氣，安裝固定式冷氣的家戶更僅4%，遠低於鄰國。民眾各出奇招，躲避酷暑。受訪者表示，不裝冷氣的主因並非電費，而是習慣、建築法規和生態考量。（看完整報導）鹿兒島外海地震頻傳 日本專家：與7月5日傳言毫無關聯本南部鹿兒島外海吐噶喇群島最近地震頻傳，2日在十島村的惡石島測得近來最大震度6弱，日本氣象廳召開緊急記者會提醒注意緊急避難，搖晃劇烈地區可能有房屋倒塌風險。隨著時間逼近漫畫「預言」日本發生大災難的日期，社群媒體流傳這可能是南海海槽大地震，或是其他地方發生地震的前兆。對此，專家表示，兩者在科學上毫無關聯，7月5日發生地震也是毫無科學根據的謠言。（看完整報導）iPASS MONEY、LINE Pay年底分家 還能轉帳LINE好友嗎？QA一次看「一卡通公司iPASS MONEY」2日宣布將於今年底終止與LINE Pay合作，原先在LINE Pay錢包中的iPASS MONEY功能轉移到「一卡通 iPASS MONEY」APP 後，還能轉帳給LINE好友嗎？帳戶餘額如何處理？中央社整理相關資訊，帶讀者一次了解。（看完整報導）道奇柯蕭達3000K里程碑 MLB史上第20人、左投第4人美國職棒大聯盟MLB洛杉磯道奇明星投手柯蕭2日先發迎戰芝加哥白襪，在6局上三振白襪打者凱普拉之後，成為大聯盟歷史上第20位達成生涯第3000次三振的投手，同時他也成為第4位達到此里程碑的左投。柯蕭大聯盟生涯的441場比賽中（438場先發），他的戰績是216勝94敗，自責分率為2.52。這位10度入選全明星賽的球員在2011年、2013年和2014年獲得國聯賽揚獎，並在2014年被選為國聯最有價值球員。（看完整報導）以下平台上午8時同時發布早安世界，給你最精華的新聞摘要！電子報、Facebook、Instagram限時動態、YouTube",
    台北地方法院審理京華城案，27日提訊在押的前台北市長柯文哲（中）出庭。中央社記者翁睿坤攝  114年5月27日（中央社記者郭建伸台北27日電）台北地方法院今天裁定繼續延押民眾黨前黨主席柯文哲。民眾黨晚間透過聲明表達憤怒且無法接受，強調裁定延押理由書根本找不到繼續羈押的具體事證，通篇是空洞的形容詞；對比綠色權貴一再輕易逃亡，人民對司法信任再度重創。台北地方法院審理京華城案，今年1月、3月間兩度裁定柯文哲、沈慶京、應曉薇、李文宗羈押禁見。北院今天裁定，柯文哲等4名被告自6月2日起延長羈押2個月，並停止接見、通信。民眾黨晚間透過聲明表示，北院裁定的延押理由書中，根本找不到有必要繼續羈押柯文哲的具體事證，不僅通篇裁定充斥空洞籠統的形容詞，更是套用「萬用例稿」複製貼上，一句晦暗不明就裁定繼續延押，嚴重違反刑事訴訟法的羈押規定，令人完全無法接受。民眾黨說，合議庭竟無視前幾次開庭中，許多檢察官偵訊時透過不正訊問所引導出的筆錄記載，皆在證人交互詰問時一一呈現不堪一擊，檢方甚至以證人片面臆測之詞作為起訴依據，僅憑臆測證詞來認定柯文哲涉嫌重大。民眾黨說，多名證人皆證言，柯文哲從未針對京華城容積獎勵下指導棋，一切根據都委會審議結果，依法辦理施行公告；既是依法辦理，如此欲加之罪，怎能以剝奪人身自由之最劇烈手段延押，侵害柯文哲人權。民眾黨表示，柯文哲多次在法庭上強調「不可能逃亡，否則台灣民眾黨就毀了。」加上柯文哲年邁母親重病，更證明柯文哲不可能棄之不顧。民眾黨抨擊，儘管如此，北院仍舊裁定延押，一句「趨吉避凶是基本人性」即認定柯文哲有逃亡之虞，對比綠色權貴一再輕易逃亡，如此的雙標，讓人民對司法信任再度重創。（編輯：謝佳珍）1140527",
    台北地方法院審理京華城案，27日提訊在押的前台北市長柯文哲（中）出庭。中央社記者翁睿坤攝 114年5月27日（中央社記者林長順台北27日電）台北地方法院審理京華城案，今年1月、3月間兩度裁定柯文哲、沈慶京、應曉薇、李文宗羈押禁見。北院今天裁定，柯文哲等4名被告自6月2日起延長羈押2個月，並停止接見、通信。台北地檢署偵辦京華城案、政治獻金案，去年12月26日偵查終結，依貪污治罪條例違背職務收受賄賂罪、圖利、公益侵占與背信罪等起訴前台北市長柯文哲、威京集團主席、國民黨台北市議員、前台北市長辦公室主任李文宗等11人，並具體求處柯文哲總計28年6月徒刑。全案移審後，北院2度裁定在押被告柯文哲、沈慶京、應曉薇與李文宗交保，經北檢抗告，台灣高等法院2度發回更裁，北院1月2日認定柯文哲等4人涉犯重罪犯罪嫌疑重大，且有逃亡、滅證、勾串之虞，裁定羈押禁見3個月。北院於3月28日裁定柯文哲等4人自4月2日起延長羈押2月，並停止接見、通信。由於羈押期限將至，北院上週開庭訊問4名被告，今天裁定柯文哲等4人自自6月2日起延長羈押2個月，並停止接見、通信。（編輯：林恕暉）1140527",
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
