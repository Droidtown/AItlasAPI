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
            #"entity": {},
            "interaction": [],
            "event": [],
            "article": "",
        }
        self.viewDICT =  {}

    def view(self, directoryNameSTR: str):
        # post Django
        importData(article=self.viewDICT["article"], location=self.viewDICT["location"], ner=self.viewDICT["entity"], people=self.viewDICT["person"])
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
                "event": [] # 之後如果改 django 那邊的樣式，得跟著改。
            }],
            "person": {},
            "location": {},
            "entity": {},
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

        self.viewDICT = viewDICT

        # 建立 AItlasKG 存檔 PATH
        newAItlasKgPATH: Path = kgDIR / directoryNameSTR / "data"
        newAItlasKgPATH.mkdir(exist_ok=True, parents=True)

        # 寫 person.json
        with open(newAItlasKgPATH / "person.json", "w", encoding="utf-8") as f:
            json.dump(viewDICT["person"], f, ensure_ascii=False, indent=4)

        # 寫 article.json
        with open(newAItlasKgPATH / "article.json", "w", encoding="utf-8") as f:
            json.dump(viewDICT["article"], f, ensure_ascii=False, indent=4)

        # 寫 location.json
        with open(newAItlasKgPATH / "location.json", "w", encoding="utf-8") as f:
            json.dump(viewDICT["location"], f, ensure_ascii=False, indent=4)

        # 寫 ner.json
        with open(newAItlasKgPATH / "entity.json",  "w", encoding="utf-8") as f:
            json.dump(viewDICT["entity"], f, ensure_ascii=False, indent=4)

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
    longText = """（中央社記者郭建伸、王揚宇台北10日電）立法院全院委員會今天審查大法官人事同意權，民眾黨立委麥玉珍詢問，是否贊成京華城案有公開直播的試辦策略。大法官被提名人蕭文生表示，他認為策略可以，但不贊成已經繫屬的案件試辦。

總統府今年3月公布7位大法官被提名人，並將總統提名咨文送到立法院，咨請立法院行使同意權。立法院會6月13日開會時，朝野無異議通過大法官人事同意權案的審查及投票表決相關時程。

立法院全院委員會今天上午審查大法官被提名人蕭文生，蕭文生口頭報告時提到，他未來如有機會與榮幸擔任大法官一職，保障基本人權將是最重要的任務，期盼在普世價值的標準內，建構適合台灣國情的基本人權制度。

立法院日前三讀修法明定法庭直播規定引發法界討論，麥玉珍詢問蕭文生，是否支持在重大案件時法庭公開播送，讓民眾看清法庭審理過程。

蕭文生表示，他贊成法律審公開，因為例如大法官的言詞辯論已公開很久，他認為這沒問題，除非有妨害公共利益等問題；至於事實審部分則是正反意見爭論的核心問題，現行規定是希望一審進行事實審，二審不要重複，但現行一、二審幾乎都在做同樣的事情。他認為，可先解決這個問題，加上立法通過的例外規定，並由法官做最後裁決。

麥玉珍表示，蕭文生認同法庭公開播送，這部分很好，也找回民眾對司法信任，但詢問公開播送的話是否有何處不妥，以及有無替代方案。蕭文生表示，法庭審理公開播送涉及「空中交換」的問題，若能有長一點緩衝時間會更好。麥玉珍詢問，京華城案若有公開直播的試辦策略，是否能提升司法透明、符合憲法原則。

蕭文生表示，他認為策略可以，但不贊成已經繫屬的案件（案件處於審理狀態）試辦，例如試行國民法官制度時，是用已經確定判決的案件。（編輯：蘇龍麒）1140710"
"（中央社記者林長順台北10日電）台北地方法院審理京華城案今天開庭勘驗相關會議錄音。沈慶京律師當庭聲請具保停押，法官請律師到醫院與沈慶京商討交保金額，且不得低於過去金額。北院預計最快下午裁定。

京華城案再度開庭，北院提訊在押的前台北市長柯文哲、前台北市長辦公室主任李文宗，傳喚前台北市都發局長黃景茂，勘驗北市都發局專家學者諮詢會議、都委會第775次會議、專案小組會議錄音逐字稿。

威京集團主席沈慶京因病治療請假未到庭，由律師代理出庭。律師在開庭時指出，沈慶京羈押至今健康狀態不佳，目前由台北看守所戒護下在台大醫院戒護就醫，且有開刀的必要，因此向北院聲請具保停押。法官指出，經函詢台北醫院，醫院認為沈慶京確實有動手術的必要，台北看守所也回函有法警戒護人力問題，法官准予律師中午前往醫院與沈慶京商談保證金額，但不能少於過去法院裁定的金額。

法官也要律師與沈溝通不要以醫院治療為理由拒絕電子監控，表示過去曾有重大人犯因以疾病因素拒絕電子監控但人逃亡，「這讓法院承受很大壓力」。（編輯：方沛清）1140710"
"（中央社記者林長順台北8日電）台北地方法院審理京華城案，今天傳喚時任台北市都委會官員胡方瓊、郭泰祺作證。前台北市副市長彭振聲因家逢巨變目前請假，合議庭訂於7月24日傳喚彭振聲以證人身分出庭。

台北地檢署偵辦京華城案、柯文哲政治獻金案，去年12月26日依貪污治罪條例違背職務收受賄賂罪、圖利、公益侵占、背信等罪嫌，起訴前台北市長柯文哲、威京集團主席沈慶京等11人，並具體求處柯文哲總計28年6月徒刑。

北院今天繼續召開審理庭，提訊在押的柯文哲、國民黨台北市議員應曉薇到庭，沈慶京因住院治療，向法院請假未到。合議庭先後傳喚時任台北市都委會官員胡方瓊、郭泰祺作證，釐清京華城案研議、審議過程。"
"（中央社記者劉世怡台北5日電）台北地檢署偵辦恐嚇檢察官案，向台北地院聲請羈押禁見被告戴瑞甯、林惠珠。北院凌晨認定涉犯恐嚇、煽惑他人犯罪、有串證以及再犯之虞，裁定2人羈押禁見。台北地院裁定指出，被告經訊問後，不爭執檢方所指部分事實，可認被告涉犯恐嚇危害安全罪、煽惑他人犯罪（被告林惠珠）、個人資料保護法非法利用個人資料罪的犯罪嫌疑重大。

裁定提及，被告之間彼此供述不一，有事實足認有串證及勾串共犯或證人之虞，而且有事實足認被告有短期內再犯同種類犯罪之虞。

法院考量被告權益保障及公共利益維護的動態平衡，並審酌憲法上比例原則後，為保全證據，認定本件無法以具保、責付或限制住居代替，而認定2人有羈押必要。

全案緣於，台北地方法院審理京華城案引發社會關注。有特定人士在社群平台張貼承辦京華城案的檢察官姓名、照片，甚至合成潑灑血跡的畫面，並搭配「命債命還」、「記住他們的名字跟臉」等仇恨、威嚇性圖文，引發社會爭議。

台北市警察局刑事警察大隊、調查局資訊安全工作站於3日分別向台北地檢署報請指揮偵辦。北市刑大及調查局資安站溯源追查，發現臉書粉專「迷因台式民主」版主戴瑞甯涉案，當天下午通知39歲、目前擔任資訊工程師的戴男到案，訊後移送北檢。

檢察官漏夜複訊後，認為戴男涉犯刑法第305條恐嚇危害安全及個人資料保護法第41條非法利用個人資料等罪嫌，犯罪嫌疑重大，且有事實足認有湮滅證據、勾串共犯或證人及反覆實施恐嚇行為之虞，向北院聲請羈押禁見。警調另查出，住台中市的林惠珠及周姓男友涉嫌把戴男上網的原圖加工合成後轉傳社群平台，警方3日晚間前往台中將2人拘提到案，移送北檢偵辦。

檢察官認為，林女涉犯罪嫌疑重大，且有事實足認有湮滅證據、勾串共犯或證人之虞，向北院聲請羈押禁見。周男則因罪嫌不足請回。（編輯：黃世雅）1140705"
"（中央社記者林長順台北5日電）台北地檢署偵辦恐嚇檢察官案，認定被告戴瑞甯、林惠珠涉犯恐嚇、違反個資法等罪，且有勾串共犯或證人之虞，向法院聲押禁見。台北地方法院審理後，今天凌晨裁定2人羈押禁見。

台北地方法院審理京華城案引發社會關注。有特定人士在社群平台張貼承辦京華城案的檢察官姓名、照片，甚至合成潑灑血跡的畫面，並搭配「命債命還」、「記住他們的名字跟臉」等仇恨、威嚇性圖文，引發社會爭議。

台北市警察局刑事警察大隊 、調查局資訊安全工作站於3日分別向台北地檢署報請指揮偵辦。北市刑大及調查局資安站溯源追查，發現臉書粉專「迷因台式民主」版主戴瑞甯涉案，當天下午通知39歲、目前擔任資訊工程師的戴男到案，訊後移送北檢。

檢察官漏夜複訊後，認為戴男涉犯刑法第305條恐嚇危害安全及個人資料保護法第41條非法利用個人資料等罪嫌，犯罪嫌疑重大，且有事實足認有湮滅證據、勾串共犯或證人及反覆實施恐嚇行為之虞，向北院聲請羈押禁見。警調另查出，住台中市的林惠珠及周姓男友涉嫌把戴男上網的原圖加工合成後轉傳社群平台，警方3日晚間前往台中將2人拘提到案，移送北檢偵辦。

檢察官認為，林女涉犯刑法第153條第1款煽惑他人犯罪、第305條恐嚇危害安全及個人資料保護法第41條非法利用個人資料等罪嫌，犯罪嫌疑重大，且有事實足認有湮滅證據、勾串共犯或證人之虞，向北院聲請羈押禁見。周男則因罪嫌不足請回。（編輯：徐睿承）1140705"
"（中央社記者林長順台北4日電）北檢偵辦恐嚇檢察官案，今天聲押禁見被告戴瑞甯、林惠珠。北檢指出，檢察官對於任何不法均依法嚴辦，戴、林所為有藉此影響或干預個案審判的重大疑慮，且形成模仿效應，有羈押禁見的必要。

台北地方法院審理京華城案引發社會關注。有特定人士在社群平台張貼承辦京華城案的檢察官姓名、照片，甚至合成潑灑血跡的畫面，並搭配「命債命還」、「記住他們的名字跟臉」等仇恨、威嚇性圖文，引發社會爭議。

台北市警察局刑事警察大隊 、調查局資訊安全工作站於昨天分別向台北地檢署報請指揮偵辦。北市刑大及調查局資安站溯源追查，發現臉書粉專「迷因台式民主」版主戴瑞甯涉案，昨天下午通知39歲、目前擔任資訊工程師的戴男到案，當晚移送北檢。

檢察官漏夜複訊後，認為戴男涉犯刑法第305條恐嚇危害安全及個人資料保護法第41條非法利用個人資料等罪嫌，犯罪嫌疑重大，且有事實足認有湮滅證據、勾串共犯或證人及反覆實施恐嚇行為之虞，向北院聲請羈押禁見。

警調另查出，住台中市的林惠珠及周姓男友涉嫌把戴男上網的原圖加工合成後轉傳社群平台，警方昨晚前往台中將2人拘提到案，今天下午移送北檢偵辦。周男、林女被送到北檢時，以衣服或帽子、口罩蓋住頭臉，面對媒體詢問不發一語。

檢察官認為，林女涉犯刑法第153條第1款煽惑他人犯罪、第305條恐嚇危害安全及個人資料保護法第41條非法利用個人資料等罪嫌，犯罪嫌疑重大，且有事實足認有湮滅證據、勾串共犯或證人之虞，向北院聲請羈押禁見。周男則因罪嫌不足請回。北檢晚間發布新聞稿指出，審酌戴姓、林姓被告所為，使依法執行職務的司法人員產生恐懼及心理壓力，有藉此影響或干預個案審判的重大疑慮；且其等所為在網路世界快速傳播，形成模仿效應，嚴重危害司法秩序及人民對司法的信賴，所以2人均有羈押禁見的必要。

北檢強調，檢察官依法訴追犯罪及法官依法審判，不容非法暴力威脅，對於任何不法，均將依法嚴辦。另同時呼籲民眾勿轉傳類似圖文，以免有觸法之虞。（編輯：張銘坤）1140704"
"（中央社記者林長順台北4日電）北檢偵辦涉恐嚇檢察官案，昨天指揮警調傳喚涉案的戴姓男子到案，今天凌晨聲押禁見。檢警昨天深夜逮捕涉嫌合成照片的周男、林女情侶檔，檢察官複訊後，今天下午將林女聲押禁見、周男請回。

台北地方法院審理京華城案引發社會關注。有特定人士在社群平台張貼承辦京華城案的檢察官姓名、照片，甚至合成潑灑血跡的畫面，並搭配「命債命還」、「記住他們的名字跟臉」等仇恨、威嚇性圖文。台北地檢署指揮台北市刑警大隊及調查局資安站偵辦。

警調發現，臉書（Facebook）粉專「迷因台式民主」發文「把司法官的照片找出來公布是我一個人幹的，跟民眾黨、鬼針草都沒關係。望周知。」警調昨天傳喚「迷因台式民主」版主、39歲戴姓男資訊工程師到案說明。

戴男坦承自行搜索檢察官照片並上網公布，但否認有合成血跡並進行恐嚇情事。警詢後依涉恐嚇危安罪將戴男移送台北地檢署複訊。

檢察官複訊後，認為戴男涉犯恐嚇危害安全及違反個人資料保護法非法蒐集及利用個人資料等罪嫌，犯罪嫌疑重大，有勾串共犯、證人之虞和反覆實施恐嚇行為，向法院聲請羈押禁見。

警調另查出，有網友把戴男上網原圖加工合成後轉傳社群平台，警調鎖定住台中市的41歲周姓男子與林姓女子，2人為情侶，警方昨晚前往台中將2人帶返北市偵訊，並於今天下午依恐嚇危安罪嫌將2人移送北檢偵辦。法界人士指出，網路上散布仇恨、恐嚇的合成照片圖文涉犯刑法第305條恐嚇危害安全及違反個人資料保護法第20條第1項而犯同法第41條非法蒐集及利用個人資料等罪嫌。

法界人士表示，刑法第305條明定，以加害生命、身體、自由、名譽、財產之事恐嚇他人，致生危害於安全者，可處2年以下有期徒刑；若意圖為自己或第三人不法之利益或損害他人之利益，違法揭露個資，也可能構成個人資料保護法第41條之罪，最重可處5年有期徒刑。（編輯：張銘坤）1140704"
"（中央社記者劉建邦台北4日電）臉書「迷因台式民主」版主戴姓男子涉上網公開承辦京華城案的11名檢察官姓名與照片，台北市警方逮人送辦。警方今天另將合成恐嚇照的周姓情侶檔，依恐嚇危安罪嫌移送北檢偵辦。

台北地院審理京華城案期間，前台北市副市長彭振聲妻子墜樓身亡，引發社會關注。有特定人士在社群平台張貼承辦京華城案的檢察官姓名、照片，甚至合成潑灑血跡的畫面，並搭配「命債命還」、「記住他們的名字跟臉」等仇恨、威嚇性圖文。

此外，臉書（Facebook）粉專「迷因台式民主」則發文「把司法官的照片找出來公布是我一個人幹的，跟民眾黨、鬼針草都沒關係。望周知。」台北市警察局刑事警察大隊偵辦此案，並通知版主、39歲戴姓男資訊工程師到案說明。據悉，戴男坦承自行搜索檢察官照片並上網公布，但否認有合成血跡並進行恐嚇情事。警詢後依涉恐嚇危安罪將他移送台北地檢署複訊。檢方今晨聲請羈押禁見。

另警方調查發現，有網友把戴男上網原圖加工合成後轉傳社群平台，警調鎖定住台中市的41歲周姓男子與林姓女子，2人為情侶，警方昨晚前往台中將2人帶返北市偵訊，並於今天下午依恐嚇危安罪嫌將其移送北檢偵辦。（編輯：黃世雅）1140704"
"（中央社記者林長順台北4日電）網路出現針對京華城案檢察官的仇恨性圖文，台北地檢署指揮台北市刑警大隊、調查局偵辦。檢警昨天傳喚臉書粉專「迷因台式民主」版主、戴姓工程師到案，今天凌晨聲請羈押禁見。

另外，有網友將戴男上網原圖加工合成再轉貼社群平台，警調鎖定是住在台中市的周姓男子、林姓女子情侶檔所為，昨天晚間前往台中，將2人帶回台北偵訊，預計今天移送北檢複訊。近日有特定人士在網路社群平台張貼承辦京華城案11名檢察官姓名、照片，甚至合成潑灑血跡的畫面，並搭配「命債命還」、「記住他們的名字跟臉」等仇恨、威嚇性圖文。另有張貼包括北院、高院法官等照片的相關仇恨性圖文被張貼在社群平台。

北檢、法務部、檢察官協會、法官協會、女法官協會、劍青檢改、司法院等機關、團體陸續發表聲明，嚴厲譴責暴力恐嚇行為。臉書粉專「迷因台式民主」發文表示，「把司法官的照片找出來公布是我一個人幹的，跟民眾黨、鬼針草都沒關係。望周知」。北檢指揮北市刑大及調查局資安站偵辦。警調查出，「迷因台式民主」版主是家住新北市汐止區的39歲戴姓資訊工程師，警方通知戴男於昨天下午3時許到至市刑大說明。據悉，戴男坦承是自己搜索相關檢察官照片並上網公布，但否認有合成血跡並進行恐嚇情事。

警方對戴男製作筆錄後，經戴男同意，前往戴男住處搜索，隨後將他帶回偵訊，昨晚依刑法恐嚇危害安全罪、違反個人資料保護法等罪嫌移送北檢。檢察官漏夜複訊後，今天凌晨將戴男聲請羈押禁見。（編輯：管中維）1140704"""


    # longText = """中東夙敵以色列和伊朗空戰進入第8天。以色列總理尼坦雅胡今天矢言「消除」伊朗構成的核子和彈道飛彈威脅。
    # 法新社報導，尼坦雅胡（Benjamin Netanyahu）在南部城巿俾什巴（Beersheba）告訴記者：「我們致力於信守摧毀核威脅的承諾、針對以色列的核滅絕威脅。」伊朗今天的飛彈攻勢擊中當地一間醫院。"""
    aitlas = AItlas()

    topicSTR: str = "京華城案"

    KG = aitlas.scan(longText)
    # pprint(KG)

    view = aitlas.aitlasViewPacker(directoryNameSTR=topicSTR)
    aitlas.view(directoryNameSTR=topicSTR)
    # isPersonBool = alias.is_person(entity, utteranceLIST) #=>Maybe
    # isLocation = alias.is_location(entity, utteranceLIST)
    # print("{} 是 Person 嗎？{}".format(entity, isPersonBool))
