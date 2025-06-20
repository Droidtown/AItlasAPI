#!/usr/bin/env python3
# -*- coding:utf-8 -*-

#from .AItlas.main import askLoki
from ArticutAPI import Articut
from copy import deepcopy
import json
#try:
    #from AItlas_TW.aitlas_wiki.KG.people import action as actionDICT
#except:
    #pass

from pathlib import Path
import sqlite3
from typing import Union
from functools import reduce
from pprint import pprint
import re
purgePat = re.compile("</?[a-zA-Z]+(_[a-zA-Z]+)?>")

listPackerDICT = {"twPat": re.compile(r"[一-龥]"),
                  "birthdatePat": re.compile(r"(?<=\{\{[Bb]irth[\s_]date[\s_]and[\s_]age\|)\d+\|\d+\|\d+"),
                  "parentsPat"  : re.compile(r"(?<=[\|\[])[一-龥]+?(?=\]\])"),
                  "nicknamePat" : re.compile(r"(?<=[\|\[])[一-龥]+?(?=\]\])"),
                  "birthplacePat":re.compile(r"(?<=[\|\[])[一-龥]+?(?=\]\])"),
                  "nationalityPat":re.compile(r"(?<=[\|\[])[一-龥]+?(?=\]\])"),
                  "spousePat": re.compile(r"(?<=\|)(\[\[)?[一-龥]+?(\]\])?(?=\|\d)"),
}
#genderPAT = re.compile("<PERSON><AUX><NOUNY>") => if NOUNY in AItlas.get_all(nouny, "biological_gender")
from requests import post
from pprint import pprint

import os
BASEPATH = "/".join(os.path.dirname(os.path.abspath(__file__)).split("/")[:-1])

actualDIR: Path = Path(__file__).resolve()
kgDIR: Path = actualDIR / "aitlasDEMO" / "rawData"

try:
    with open("{}/AItlasAPI/account.info".format(BASEPATH), encoding="utf-8") as f:
        accountDICT = json.load(f)
    articut = Articut(username=accountDICT["username"], apikey=accountDICT["api_key"])
except:
    articut = Articut()

class AItlas:
    def __init__(self, username="", apikey=""):
        self.articut = Articut(username=username, apikey=apikey)

        self.personNamePAT = re.compile("(?<=<ENTITY_person>)([^<]+)(?=</ENTITY_person>)")
        self.aliasPAT       = []
        self.addressPAT     = []
        self.affiliationPAT = []
        self.awardPAT       = []
        self.birth_datePAT  = []
        self.death_datePAT  = []
        self.biological_genderPAT = []
        self.body_heightPAT = []
        self.body_weightPAT = []
        self.jobtitlePAT = re.compile("<LOCATION>([^<]+</LOCATION>(<RANGE_locality>前</RANGE_locality>)?<(UserDefined|ENTITY_(nounHead|nouny?|oov))>[^<]+)</(UserDefined|ENTITY_(nounHead|nouny?|oov))><ENTITY_person>([^<]+)</ENTITY_person>")
        self.nationalityPAT  = []
        self.parentPAT      = re.compile("(?<=</ENTITY_person>)(<FUNC_inner>[的之]</FUNC_inner>)?<ENTITY_pronoun>[父母爸媽].?</ENTITY_pronoun><ENTITY_person>([^<]+)</ENTITY_person>")
        self.siblingPAT     = re.compile("(?<=</ENTITY_person>)(<FUNC_inner>[的之]</FUNC_inner>)?<ENTITY_pronoun>[哥弟姐姊妹兄].?</ENTITY_pronoun><ENTITY_person>([^<]+)</ENTITY_person>")
        self.childPAT       = []
        self.spousePAT      = re.compile("(?<=</ENTITY_person>)(<FUNC_inner>[的之]</FUNC_inner>)?<ENTITY_pronoun>([丈妻先太].?|老[公婆])</ENTITY_pronoun><ENTITY_person>([^<]+)</ENTITY_person>")
        self.skillsPAT      = []
        self.educationPAT   = []
        self.event_logPAT   = []
        self.descriptionPAT = []
        self.raw_dataPAT    = []
        self.wikipedia_TW: dict[str, dict] = {}
        self.wikipedia_EN: dict[str, dict] = {}
        self.wikipedia_TW["person"] = self._matchAItlas("tw")
        #self.wikipedia_EN["person"] = self._matchAItlas("en")
        self.AITLASKG = {"person":{},
                         "location":{},
                         "entity":{},
                         "interaction":[],
                         "event":[]
                         }


    def view(self):
        #啟動 Django, 跳轉到 Browser
        return None


    def _matchAItlas(self, lang):
        personDICT = {}
        if lang.lower() == "tw":
            personDICT = json.load(open(f"{BASEPATH}/AItlasAPI/AItlas_TW/wikipedia/AItlas_wiki_person.json", "r", encoding="utf-8"))
        #elif lang.lower() == "en":
            #personDICT = json.load(open("AItlas_EN/wikipedia/AItlas_wiki_person.json", "r", encoding="utf-8"))
        return personDICT


    def scan(self, inputSTR):
        for person in self.wikipedia_TW["person"].keys():
            if person in inputSTR:
                #print(f"person:{person}")
                self.AITLASKG["person"][person]=self.wikipedia_TW["person"][person]
        return self.AITLASKG


    def _listPacker(self, datatype, inputSTR):
        if datatype == "生日":
            resultLIST = [i.group().replace("|", "/") for i in listPackerDICT["birthdatePat"].finditer(inputSTR)]
        elif datatype == "父母":
            resultLIST = [i.group() for i in listPackerDICT["birthdatePat"].finditer(inputSTR)]
        elif datatype == "出生地":
            resultLIST = [i.group() for i in listPackerDICT["birthplacePat"].finditer(inputSTR)]
        elif datatype == "國籍":
            resultLIST = [i.group() for i in listPackerDICT["nationalityPat"].finditer(inputSTR)]
        elif datatype == "配偶":
            resultLIST = [i.group() for i in listPackerDICT["spousePat"].finditer(inputSTR)]
        elif datatype == "別名":
            if "、" in inputSTR:
                resultLIST = inputSTR.split("、")
            else:
                resultLIST = [i.group() for i in listPackerDICT["nicknamePat"].finditer(inputSTR)]
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


    def aitlasViewPacker(self):
        translateDICT = {
                         "name"          : "全名",
                         "本名"          : "全名",
                         "姓名"          : "全名",
                         "外文名"        : "外文名",
                         "nickname"      : "別名",
                         "別名"          : "別名",
                         "性別"          : "生理性別",
                         "birth_date"    : "生日",
                         "出生日期"      : "生日",
                         "birth_place"   : "出生地",
                         "place of birth": "出生地",
                         "出生地點"      : "出生地",
                         "death_date"    : "忌日",
                         "逝世日期"      : "忌日",
                         "death_place"   : "死亡地",
                         "逝世地點"      : "死亡地",
                         "death_cause"   : "死因",
                         "affiliation"   : "機構",
                         "office"        : "職銜",
                         "occupation"    : "職銜",
                         "employer"      : "職銜",
                         "job"           : "職銜",
                         "職業"          : "職銜",
                         "title"         : "職銜",
                         "spouse"        : "配偶",
                         "配偶"          : "配偶",
                         "nationality"   : "國籍",
                         "citizenship"   : "國籍",
                         "country"       : "國籍",
                         "國籍"          : "國籍",
                         "party"         : "政黨",
                         "education"     : "教育背景",
                         "educate"       : "教育背景",
                         "母校"          : "教育背景",
                         "教育程度"      : "教育背景",
                         "alma_mater"    : "教育背景",
                         "alma mater"    : "教育背景",
                         "address"       : "地址",
                         "居住地"        : "居住地",
                         "resident"      : "居住地",
                         "language"      : "語言",
                         "dialect"       : "語言",
                         "religion"      : "宗教",
                         "parents"       : "父母",
                         "father"        : "父母",
                         "mother"        : "父母",
                         "children"      : "子女",
                         "website"       : "網站",
                         "awards"        : "獎項",
                         "honours"       : "獎項",
                         "獲獎"          : "獎項",
                         }
        #Person
        viewDICT = {"person":{}}
        for person in self.AITLASKG["person"]:
            viewDICT["person"][person] = {}
            for key in self.AITLASKG["person"][person]:
                if key in translateDICT.keys():
                    #viewDICT["person"][person][translateDICT[key]] = self.AITLASKG["person"][person][key]
                    viewDICT["person"][person][translateDICT[key]] = self._listPacker(translateDICT[key], self.AITLASKG["person"][person][key])
        return viewDICT


    def createKG(self, inputSTR, KG_FilePath=None, KG_FileName="default.ait", userDefinedDICT=None):
        #conn =sqlite3.connect(KG_FileName)
        #cursor = conn.cursor()
        #cursor.execute("DROP TABLE IF EXISTS person;")
        #cursor.execute("DROP TABLE IF EXISTS entity;")
        #conn.commit()
        #cursor.execute('''CREATE TABLE IF NOT EXISTS away
                          #(id INT PRIMARY KEY NOT NULL,
                          #alias JSONB,
                          #address JSONB,
                          #affiliation JSONB,
                          #award JSONB,
                          #birth_date DATETIME,
                          #birth_place JSONB,
                          #;''')

        #cursor.close()
        #conn.close()

        if KG_FilePath == None:
            print("[AItlas]: KG_FilePath is needed!")
            return None
        if KG_FileName.endswith(".ait"):
            pass
        else:
            KG_FileName = KG_FileName+".ait"

        self.posLIST = []
        self.splitLIST = []
        resultDICT = self.articut.parse(inputSTR, userDefinedDictFILE=userDefinedDICT)
        for i in resultDICT["result_pos"]:
            if len(i) > 1:
                self.posLIST.append(i)
            else:
                self.splitLIST.append(i)
        self.splitLIST = list(set(self.splitLIST))
        #print(self.posLIST)
        self.extract_person()
        #self._getPersonKG(inputSTR)
        return None


    def extract_person(self):
        self.personDICT = {}
        for i in self.posLIST:
            for person in self.personNamePAT.findall(i):
                self.personDICT[person] = {"alias" : [],
                                           "address" : [],
                                           "affiliation" : [],
                                           "award" : [],
                                           "birth_date" : None,
                                           "birth_place" : [],
                                           "death_date": None,
                                           "death_place" : [],
                                           "biological_gender" : [],
                                           "body_height" : [],
                                           "body_weight" : [],
                                           "job_title" : [],
                                           "nationality" : [],
                                           "parent" : [],
                                           "sibling" : [],
                                           "child" : [],
                                           "spouse" : [],
                                           "skills" : [],
                                           "education" : [],
                                           "event_log" : [],
                                           "description" : [],
                                           "raw_data" : []
                                           }

        for i in self.posLIST:
            #job_title
            jobtitle = [j.groups() for j in self.jobtitlePAT.finditer(i)]
            if jobtitle != []:
                if purgePat.sub("", jobtitle[0][0]) not in self.personDICT[jobtitle[0][-1]]["job_title"]:
                    self.personDICT[jobtitle[0][-1]]["job_title"].append(purgePat.sub("", jobtitle[0][0]))
                    #nationality
                    nationality = []
                    nationality = self.aitlas_get_all(purgePat.sub("", jobtitle[0][0]), "country")
                    if nationality != []:
                        self.personDICT[jobtitle[0][-1]]["nationality"].extend(nationality)
                #parent
                parent = [j.groups() for j in self.parentPAT.finditer(i)]
                if parent != []:
                    self.personDICT[jobtitle[0][-1]]["parent"].append(purgePat.sub("", parent[0][1]))
                #sibling
                sibling = [j.groups() for j in self.siblingPAT.finditer(i)]
                if sibling != []:
                    self.personDICT[jobtitle[0][-1]]["sibling"].append(purgePat.sub("", sibling[0][1]))
                #spouse
                spouse = [j.groups() for j in self.spousePAT.finditer(i)]
                if spouse != []:
                    self.personDICT[jobtitle[0][-1]]["spouse"].append(purgePat.sub("", spouse[0][2]))


        pprint(self.personDICT)

    #def _getPersonKG(self, inputSTR):

        #refDICT = {}
        #keyLIST = ["alias", "address", "affiliation", "award", "birth_date", "birth_place", "death_date","death_place",
                   #"biological_gender", "body_height", "body_weight", "job_title", "nationality", "parent", "sibling",
                   #"child", "spouse", "skills", "education", "event_log", "description", "raw_data"]
        #for k in keyLIST:
            #refDICT[k] = []

        #self.personDICT = {}
        #for i in self.posLIST:
            #for person in self.personNamePAT.findall(i):
                #self.personDICT[person] = {}
                #for k in keyLIST:
                    #self.personDICT[person][k] = deepcopy(refDICT[k])

        #resultDICT = askLoki(inputSTR, refDICT=refDICT, splitLIST=self.splitLIST)
        #for k_s in resultDICT.keys():
            #for i in  resultDICT[k_s]:
                #for person, value in i.items():
                    #if value not in self.personDICT[person][k_s]:
                        #self.personDICT[person][k_s].append(value)
        ##pprint(self.personDICT)
        #return None


    def person_alias(self):
        return None


    def aitlas_get_all(self, inputSTR, keySTR):
        aitlasURL = "https://api.droidtown.co/aitlas/api/"
        payload = {
            "username": accountDICT["username"],
            "aitlas_key":accountDICT["aitlas_key"],
            "func":["get_all"],
            "input_str": inputSTR,
            "data": {}
        }
        response = post(aitlasURL, json=payload).json()
        return response["results"][keySTR]


    def createLokiProject(self, utteranceLIST):
        url = "https://api.droidtown.co/Loki/Call/"  #線上版 URL
        projectSTR = "aitlas_dev"
        payload = {
            "username" : accountDICT["username"], # 這裡填入您在 https://api.droidtown.co 使用的帳號 email。     Docker 版不需要此參數！
            "func": "create_project",
            "data": {
                "name": projectSTR, # 這裡填入您想要在 Loki 上建立的專案名稱
            }
        }
        response = post(url, json=payload).json()
        lokiKey = response["loki_key"]
        payload = {
            "username" : accountDICT["username"], # 這裡填入您在 https://api.droidtown.co 使用的帳號 email。     Docker 版不需要此參數！
            "loki_key" : lokiKey, # 這裡填入您在 https://api.droidtown.co 登入後取得的 loki_key。 Docker 版不需要此參數！
            "project": projectSTR, #專案名稱 (請先在 Loki 的設定網頁裡建立一個 Project 以便取得它的專案金鑰 (loki_key)
            "intent": "ait_person", #意圖名稱
            "func": "create_intent",
            "data": {
                "type": "basic" #意圖類別
            }
        }
        response = post(url, json=payload).json()
        for i in range(0, len(utteranceLIST), 20):
            payload = {
                "username" : accountDICT["username"], # 這裡填入您在 https://api.droidtown.co 使用的帳號 email。     Docker 版不需要此參數！
                "loki_key" : lokiKey, # 這裡填入您在 https://api.droidtown.co 登入後取得的 loki_key。 Docker 版不需要此參數！
                "project": projectSTR, #專案名稱 (請先在 Loki 的設定網頁裡建立一個 Project 以便取得它的專案金鑰 (loki_key)
                "intent": "ait_person", #意圖名稱
                "func": "insert_utterance",
                "data": {
                    "utterance": utteranceLIST[i:i+20]
                }
            }
            response = post(url, json=payload).json()


    #def is_person(self, entity: str, utteranceLIST: list[str]) -> IsPersonJudgement:
        #"""
        #Check if 'entity' is a person according to the evidences listed in utteranceLIST.
        #Each utterance should contain the entity given.
        #"""
        ## Check the existence of the entity in every utterance.
        #checkList = list(map( lambda u: len(re.findall(entity,u))==0
                        #, utteranceLIST))
        ## Throws ValueError if any of the utterances doesn't satisfy the requirement.
        #if reduce(lambda x,y:x or y, checkList):
            #errorList = []
            #for k,v in enumerate(checkList):
                #if v:
                    #errorList.append(k)
            #raise ValueError(f"In indexes:{errorList} of utteranceLIST, the entity doesn't show in the utterance.")

        #if entity in peopleLIST:
            #return True
        #else:
            ##get verbs from utteranceLIST

            #for u_s in utteranceLIST:
                #resultDICT = articut.parse(u_s)
                #verbLIST = articut.getVerbStemLIST(resultDICT)
                #verbLIST = wordExtractor(verbLIST)

            #for v_s in verbLIST:
                #checkingUtteranceLIST = []
                #intentKey = articut.parse(v_s, level="lv3", pinyin="HANYU")["utterance"][0].replace(" ", "")
                #for u_s in utteranceLIST:
                    #checkingUtteranceLIST.append(u_s[u_s.index(v_s):])
                #lokiResult = execLoki(checkingUtteranceLIST)
                #if intentKey in lokiResult:
                    #return MaybePerson()
            #return False


    #def is_location():
        #return None

    #def is_superset():
        #'''
        #inputArgs: "dog", "animal" => False
        #'''
        #return None

    #def is_subset():
        #"""
        #inputArgs: "dog", "animal" => True
        #"""
        #return None

    #def converTime():
        #"""
        #"""
        #return None

    #def find_EntyRelation():
        #"""
        #inputArgs: "dog", "animal" => subset
                                   #=> synonym ("k9", "dog") ("kids", "children")
                                   #=> superset
                                   #=> Unknown
        #"""
        #return None

    #def what_is_this():
        #return None



if __name__ == "__main__":
    longText = """blah blah blah...末綱聰子是一個羽球女子運動員，
    末綱聰子(???)與前田美順(???)的常常組隊參加比賽，
    末綱聰子與前田美順的組合代表日本(???)參加北京(???)舉行的奧運會羽球女子雙打比賽"""

    #entity = "前田美順"
    #utteranceLIST = ["末綱聰子與前田美順的組合代表日本參加北京舉行的奧運會羽球女子雙打比賽"]
    aitlas = AItlas()
    #aitlas.createKG(inputSTR=longText, KG_FilePath= kgDIR/ "aitlas.kg")

    longText = """民眾黨前主席柯文哲的父親柯承發今天辭世。民眾黨代理黨主席黃國昌說，請柯家人放心，民眾黨會做他們最堅強的後盾；所有後事，都要尊重柯家人的意願跟想法，希望能尊重他們的隱私。
國民黨主席朱立倫也透過聲明表示，對於柯文哲的父親柯承發過世，深表哀悼，希望柯文哲以及其家人節哀珍重。"""

    longText = """中東夙敵以色列和伊朗空戰進入第8天。以色列總理尼坦雅胡今天矢言「消除」伊朗構成的核子和彈道飛彈威脅。
法新社報導，尼坦雅胡（Benjamin Netanyahu）在南部城巿俾什巴（Beersheba）告訴記者：「我們致力於信守摧毀核威脅的承諾、針對以色列的核滅絕威脅。」伊朗今天的飛彈攻勢擊中當地一間醫院。"""
    KG = aitlas.scan(longText)
    pprint(KG)
    view = aitlas.aitlasViewPacker(topicSTR="以色列伊朗戰爭2025", filePath= kgDIR/ "aitlas.kg")
    pprint(view)
    aitlas.view()
    #isPersonBool = alias.is_person(entity, utteranceLIST) #=>Maybe
    #isLocation = alias.is_location(entity, utteranceLIST)
    #print("{} 是 Person 嗎？{}".format(entity, isPersonBool))