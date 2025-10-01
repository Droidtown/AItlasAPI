#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# 把 AItlasView 加進 path
import requests
import litellm
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

import logging
from typing import Union
from functools import reduce
from pprint import pprint
from datetime import datetime
import articutShell.articutShell as articutShell

import re

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",        # 格式：時間 - 等級 - 訊息
    handlers=[
        logging.FileHandler("./AItlasAPI.log", encoding="utf-8", mode="a"),
        logging.StreamHandler()
    ]
)

purgePat = re.compile("</?[a-zA-Z]+(_[a-zA-Z]+)?>")
G_knowledgePAT: re.Pattern = re.compile(r"<KNOWLEDGE_(?:(?!CNAMember).+?)>(?:(?!中央社).+?)</KNOWLEDGE_(?:(?!CNAMember).+?)>")
G_dictPAT: re.Pattern = re.compile(r"\{[^{}]*\}")
G_sourcePAT: re.Pattern = re.compile(r'(?<="agent_entity": ")[^"]+')
G_taregetPAT: re.Pattern = re.compile(r'(?<="patient_entity": ")[^"]+')
G_labelPAT: re.Pattern = re.compile(r'(?<="action_between_agent_and_patient": ")[^"]+')
G_metaDataPAT: re.Pattern = re.compile(r'(?<="sentenceInArticle": ")[^"]+')
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

newAItlasDirPATH = Path.cwd() / "AItlasResult"
newAItlasDirPATH.mkdir(exist_ok=True, parents=True)
G_accountDICT: dict[str, str] = {}
try:
    with open(Path.cwd()/"account.info", encoding="utf-8") as f:
        G_accountDICT = json.load(f)
    if "url" in G_accountDICT:
        articut = Articut(url=G_accountDICT["url"])
    else:
        articut = Articut(username=G_accountDICT["username"], apikey=G_accountDICT["api_key"])
except Exception as e:
    logging.error(e)
    logging.info("請先新增 account.info 並填入相關資訊")
    exit()

class AItlas:
    def __init__(self, username="", apikey="", url="", llm={}):
        self.username = username
        self.apikey = apikey
        self.url = url
        self.llm = llm
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
            "article": {},
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
        sourceCssDirPATH: Path = Path.cwd() / "AItlasView" / "static" / "css"
        targetCssDirPATH: Path = newAItlasDirPATH / directoryNameSTR / "static" / "css"
        targetCssDirPATH.mkdir(exist_ok=True, parents=True)
        
        for filePATH in sourceCssDirPATH.glob("*.css"):
            # 取內容
            contentSTR: str = filePATH.read_text(encoding="utf-8")

            # 在目標資料夾建立檔案
            newFilePATH: Path = targetCssDirPATH / filePATH.name
            newFilePATH.write_text(contentSTR, encoding="utf-8")

        ### static/js
        sourceJsDirPATH: Path = Path.cwd() / "AItlasView" / "static" / "js"
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
            highlightContentSTR: str = self._highlightArticles(articleSTR=self.viewDICT["article"][0]["content"], peopleDICT=self.viewDICT["person"], placeDICT=self.viewDICT["location"], entityDICT=self.viewDICT["entity"])
            resultLIST: list[dict[str, str]] = [{
                "title": self.viewDICT["article"][0]["title"],
                "content": highlightContentSTR,
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
        sourceHtmlPATH: Path = Path.cwd() / "AItlasView" / "static" / "index.html"
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
        
        logging.info(f"完成 {directoryNameSTR}，可以打開 AItlasResult/{directoryNameSTR}/{directoryNameSTR}.html 查看視覺化資料囉。")
        return None

    def _matchAItlasPerson(self, lang):
        personDICT = {}
        if lang.lower() == "tw":
            personDICT = json.load(
                open(
                    Path.cwd()/"AItlasAPI"/"AItlas_TW/wikipedia/AItlas_wiki_person.json",
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
                    Path.cwd()/"AItlasAPI"/"AItlas_TW/wikipedia/AItlas_wiki_location.json",
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
                    Path.cwd()/"AItlasAPI"/"AItlas_TW/wikipedia/AItlas_wiki_entity.json",
                    "r",
                    encoding="utf-8"
                )
            )
        # elif lang.lower() == "en":
        # locationDICT = json.load(open("AItlas_EN/wikipedia/AItlas_wiki_entity.json", "r", encoding="utf-8"))
        return nerDICT

    def scan(self, inputSTR, timeRefSTR):
        # article
        if timeRefSTR not in self.AITLASKG["article"]:
            self.AITLASKG["article"].update({timeRefSTR: ""})

        self.AITLASKG["article"][timeRefSTR] += inputSTR

        # person
        for personSTR in self.wikipedia_TW["person"].keys():
            if personSTR in inputSTR:
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

    def _callLiteLlm2GenContent(self, sentenceSTR: str="") -> dict:
        """
        給定文章
        讓 LLM 找到『誰對誰做了什麼』的結構

        input:
        sentenceSTR: str
        
        output:
        {
            "status": True/False,
            "msg": "",
            "result": ""
        }
        """
        messageLIST: list[dict[str, str]] = [{
                "content": f"""```json\b{str(sentenceSTR)}```請閱讀這篇文章，，寫成下列 json 格式，不要給我多餘的東西。
                                ```[{{"agent_entity": "","patient_entity": "","action_between_agent_and_patient": "","sentenceInArticle": "","encounter_time": ""/*#這件事情的發生時間，格式用dt.strftime("%Y-%m-%dT%H:%M:%S")的回答*/}},......]```
                                例如： ```[{{"agent_entity": "台北檢查署", "patient_entity": "柯文哲", "action_between_agent_and_patient": "羈押", "sentenceInArticle": "今天(2025-09-25T03:11:00)台北檢查署羈押柯文哲", "encounter_time": "2025-09-25T03:11:00"}}]```
                            """,
                "role": "user"
            }
        ]
        modelSTR: str = self.llm["model"]
        resultDICT: dict = {}

        # ollama openai gemini claude azure
        try:
            for k, v in self.llm["env"].items():
                os.environ[k] = v

            if self.llm["api_base"]:
                resultDICT = litellm.completion(
                    model=modelSTR,
                    messages=messageLIST,
                    api_base=self.llm["api_base"]
                ).model_dump()
            else:
                resultDICT = litellm.completion(
                    model=modelSTR,
                    messages=messageLIST,
                ).model_dump()

            logging.info(resultDICT)
            if "choices" in resultDICT:
                return {"status": True, "result": resultDICT["choices"][0]["message"]["content"]}
            else:
                return {"status": False, "msg": resultDICT}

        except Exception as e:
            logging.error(e)
            return {"status": False, "msg": str(e)}

    def _parseArticutKnowledgeSentence(self, articutResultDICT: dict)-> dict[str, str]:
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
            list[str] pos句子 
        """
        resultPosLIST: list[str] = articutResultDICT["result_pos"]
        timeLIST: list[str] = articutResultDICT["time"]
        sentenceIdxLIST: list[list[int]] = []
        essayLIST: list[list[str]] = []        
        endCodeLIST: list[str] = ["。", "!", "！", "?", "？", ";", "；", "(", ")", "（", "）"]
        idxCompareTableDICT: dict[int, int] = {}  # (result_pos 的 index):(time 的 index)

        # fill sentenceIdxLIST
        timeIndexINT: int = -1
        essayIdxINT: int = -1         # 短文的 idx
        isNewParagraphBOOL: bool = True
        for i, sentence_s in enumerate(resultPosLIST):
            if len(sentence_s)==1:
                if sentence_s in endCodeLIST:
                    isNewParagraphBOOL = True
            else:
                if isNewParagraphBOOL:
                    sentenceIdxLIST.append([])
                    essayIdxINT += 1
                    isNewParagraphBOOL = False

                timeIndexINT += 1
                idxCompareTableDICT.update({i: timeIndexINT})
                sentenceIdxLIST[essayIdxINT].append(i)
        
        # fill essayLIST: 根據 sentenceIdxLIST 找到分別對應的短文 
        for essayIdxINT in range(len(sentenceIdxLIST)):
            essayLIST.append([])
            for i_i in range(len(sentenceIdxLIST[essayIdxINT])):
                posIdxINT: bool = sentenceIdxLIST[essayIdxINT][i_i]
                essayLIST[essayIdxINT].append(resultPosLIST[posIdxINT])
        
        # 比對 sentenceIdxLIST 和 essayLIST
        resultLIST: list[str] = []
        for i_i in range(len(sentenceIdxLIST)):
            posIdxLIST: list[int] = sentenceIdxLIST[i_i]
            paragraphLIST: list[str] = essayLIST[i_i]
            for i in range(len(posIdxLIST)): 
                idx_i: int = idxCompareTableDICT[posIdxLIST[i]]
                if not timeLIST[idx_i]:
                    continue

                # 拿 articut lv3 time 資料
                textSTR: str = timeLIST[idx_i][0]["text"]
                dateTimeSTR: str = timeLIST[idx_i][0]["datetime"].replace(" ", "T")

                # 取代原資料
                paragraphLIST[i] = paragraphLIST[i].replace(textSTR, f"{textSTR}({dateTimeSTR})")
            
            essaySTR: str = "".join(paragraphLIST)
            knowledgeMATCH: re.Match = G_knowledgePAT.findall(essaySTR)
            if len(knowledgeMATCH)>=2:
                resultLIST.append(essaySTR)
        
        return resultLIST

    def _convertRoc(self, rocDateSTR: str, toISO: True) -> str:
        """
        將民國年格式 (例如 '1140613') 轉成 ISO 8601 格式 'YYYY-MM-DDT00:00:00'
        """
        if len(rocDateSTR) != 7 or not rocDateSTR.isdigit():
            return "輸入格式錯誤，應為 7 位數字，例如 '1140613'"

        rocYearSTR = int(rocDateSTR[:3])
        yearSTR = rocYearSTR + 1911  # 民國年轉西元年
        monthSTR = int(rocDateSTR[3:5])
        daySTR = int(rocDateSTR[5:7])

        dt = datetime(yearSTR, monthSTR, daySTR)
        if toISO:
            return dt.strftime("%Y-%m-%dT%H:%M:%S")

        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def _isLegalRocTime(self, timeSTR: str) -> bool:
        """
        檢查輸入值是否為 `%Y-%m-%dT%H:%M:%S` 格式
        """
        try:
            datetime.strptime(timeSTR, "%Y-%m-%dT%H:%M:%S")
            return True
        except ValueError:
            return False

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
                "content": "",
            }],
            "person": {},
            "location": {},
            "entity": {},
            "person2person":[], #關聯圖
            "event": []
        }
        for time_s, article_s in self.AITLASKG["article"].items():
            # 接 Articut
            ## 時間基準
            articutResultDICT: dict = articutShell.parse(inputSTR=article_s, level="lv3", timeRef=self._convertRoc(time_s, toISO=False))

            # article
            viewDICT["article"][0]["content"] += article_s

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
                    for sentence_s, value_l in articutResultDICT["CNA_tag"][f"KNOWLEDGE_{person_s}"].items():
                        viewDICT["person"][sentence_s] = {}
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
                    for sentence_s, value_l in articutResultDICT["CNA_tag"][f"KNOWLEDGE_{location_s}"].items():
                        viewDICT["location"][sentence_s] = {}
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
                    for sentence_s, value_l in articutResultDICT["CNA_tag"][f"KNOWLEDGE_{entity_s}"].items():
                        viewDICT["entity"][sentence_s] = {}
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
            knowledgeSentenceLIST: list[str] = self._parseArticutKnowledgeSentence(articutResultDICT)
            ## 接LLM
            for sentence_s in knowledgeSentenceLIST:
                print(f"[AItlasAPI 774] {sentence_s}")
                result = self._callLiteLlm2GenContent(sentenceSTR=sentence_s)

                if not result["status"]:
                    logging.error(result["msg"])
                    logging.info("LLM生成資料時似乎出了些問題，所以時序圖和關聯圖將會沒有任何事件可顯示。")
                    self.viewDICT = viewDICT
                    return viewDICT

                for m in G_dictPAT.finditer(str(result)):
                    dictSTR: str = m.group()
                    # 找到子結構

                    ## source
                    sourceLIST: list[str] = G_sourcePAT.findall(dictSTR)
                    sourceSTR: str = ""
                    if len(sourceLIST)>0:
                        sourceSTR = purgePat.sub("", sourceLIST[0])

                    if sourceSTR == "":
                        continue

                    ## target
                    targetLIST: list[str] = G_taregetPAT.findall(dictSTR)
                    targetSTR: str = ""
                    if len(targetLIST)>0:
                        targetSTR = purgePat.sub("", targetLIST[0])

                    if targetSTR == "":
                        continue

                    ## label
                    labelLIST: list[str] = G_labelPAT.findall(dictSTR)
                    labelSTR: str = ""
                    if len(labelLIST)>0:
                        labelSTR = purgePat.sub("", labelLIST[0])

                    if labelSTR == "":
                        continue

                    ## metaData
                    metaDataSTR: str = purgePat.sub("", sentence_s)

                    ## encounterTime
                    encounterTimeLIST: list[str] = G_encounterTimePAT.findall(dictSTR)
                    encounterTimeSTR: str = self._convertRoc(time_s, toISO=True)
                    if len(encounterTimeLIST)>0:
                        encounterTimeSTR = purgePat.sub("", encounterTimeLIST[0])
                    
                    # 合成
                    if sourceSTR in sentence_s and targetSTR in sentence_s and self._isLegalRocTime(encounterTimeSTR):
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
            "username": self.username,
            "aitlas_key": G_accountDICT["aitlas_key"],
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
            "username": self.username,  # 這裡填入您在 https://api.droidtown.co 使用的帳號 email。     Docker 版不需要此參數！
            "func": "create_project",
            "data": {
                "name": projectSTR,  # 這裡填入您想要在 Loki 上建立的專案名稱
            },
        }
        response = requests.post(url, json=payload).json()
        lokiKey = response["loki_key"]
        payload = {
            "username": self.username,  # 這裡填入您在 https://api.droidtown.co 使用的帳號 email。     Docker 版不需要此參數！
            "loki_key": lokiKey,  # 這裡填入您在 https://api.droidtown.co 登入後取得的 loki_key。 Docker 版不需要此參數！
            "project": projectSTR,  # 專案名稱 (請先在 Loki 的設定網頁裡建立一個 Project 以便取得它的專案金鑰 (loki_key)
            "intent": "ait_person",  # 意圖名稱
            "func": "create_intent",
            "data": {"type": "basic"},  # 意圖類別
        }
        response = requests.post(url, json=payload).json()
        for i in range(0, len(utteranceLIST), 20):
            payload = {
                "username": self.username,  # 這裡填入您在 https://api.droidtown.co 使用的帳號 email。     Docker 版不需要此參數！
                "loki_key": lokiKey,  # 這裡填入您在 https://api.droidtown.co 登入後取得的 loki_key。 Docker 版不需要此參數！
                "project": projectSTR,  # 專案名稱 (請先在 Loki 的設定網頁裡建立一個 Project 以便取得它的專案金鑰 (loki_key)
                "intent": "ait_person",  # 意圖名稱
                "func": "insert_utterance",
                "data": {"utterance": utteranceLIST[i : i + 20]},
            }
            response = requests.post(url, json=payload).json()


if __name__ == "__main__":
    articleDICT: dict[str, str] = {
        # "1140516": "（中央社記者郭建伸、林巧璉台北16日電）北院審理京華城案引發民眾黨與高雄市政府為容積獎勵隔空交火。民眾黨今天批評高雄市府避重就輕、惡意誤導，呼籲勿配合政客炒作聲量；高雄市副市長林欽榮說，京華城是單一財團小基地，採取所謂自創容積，無法律授權。北院昨天開庭審理京華城案，前民眾黨主席柯文哲的臉書以「綠能，你不能；陳其邁可以，柯文哲不能」為題表示，「高雄亞灣經貿開發計畫不管是營運或企業總部給20%容獎，都不可以。」高雄市府回應，政黨人士混淆視聽，譴責以司法調查弊案類比國家重大經建亞灣2.0。民眾黨今天透過聲明表示，根據「都市計畫法高雄市施行細則」第24條之3規定項目與容積獎勵上限，取得經濟部核發的「營運總部」認定函，法定容積5%，但高雄市府新聞稿中卻未正面回應昨天柯文哲委任律師質疑「為何給予容積獎勵20%，整整比施行細則所規定之上限5%多出3倍？」民眾黨質疑，高雄市政府心虛閃躲、避重就輕，給予容積獎勵的項目是哪些，請高雄市政府具體回應，應依林欽榮所言「容積是公共財」，審議不可黑箱。民眾黨也抨擊，高雄市府新聞稿提及有關京華城部分有諸多錯誤，表格更是惡意誤導，因為京華城從頭到尾都不是「準用都更」，是根據「都市計畫法第24條」由地主自行提出細部計畫申請，台北市政府則依「台北市都市計畫施行自治條例」25條給予容積獎勵，何來「違法準用都更條例」。民眾黨指出，京華城計畫內容具備「公益性、對價性」且提供市府回饋，通過都委會審議才得到容積獎勵，肩負帶動台北市南松山地區與附近老舊街廓有更新活化的任務、並非單一地主受惠。民眾黨抨擊，高雄市政府的表格在土地面積欄位寫「亞灣計畫區為國有土地」是刻意迴避，實際上以「國家重大經建計畫」做包裝，亞灣開發後，原國有土地皆轉賣給私有企業或財團進行開發，而且高雄市政府在上位計畫還沒通過前，就搶先給容積，對照林欽榮對京華城案的攻擊，明顯雙標，根本是「我能你不能」。不過，民眾黨也指出，高雄市政府聲明稿唯一有參考價值的地方，是證實細部計畫可以給容積獎勵，林欽榮在開庭時，不斷鬼打牆稱細部計畫不能給容積獎勵，多給一平方米就是圖利，但亞灣2.0計畫正是林欽榮透過細部計畫給予容積獎勵的實際個案，甚至突破5%上限給到20%。高雄市副市長林欽榮上午在高雄市議會接受媒體聯訪表示，所有容積獎勵須依法授權，亞灣地區容積合法合規，京華城非都更區，僅是單一財團小基地，「這是天差地別」。他說，亞灣地區早在民國91年依都市計畫程序，完全就劃定為公劃公告都市更新地區，對比京華城根本不是都市更新地區，亞灣本來就可有1.5倍容積率使用。林欽榮表示，京華城是單一財團小基地1.6公頃，採取所謂自創容積，無法律授權；監察院2023年有糾正台北市政府、台北市都委會、台北市都發局，「亞灣與京華城是天差地別。亞灣2.0計畫完全是依法授權」。（編輯：謝佳珍）1140516",
        # "1140920": "（中央社記者黃旭昇新北20日電）矯正署台北看守所遞送餐飲過程遭批評，北所今天表示，依收容人的用餐習慣與食品衛生，提供適當不鏽鋼皿具盛裝；至於舍房送入口的位置，主要是受限舊有建築結構安全影響。前台灣民眾黨主席柯文哲的妻子陳佩琪，今天在其臉書（Facebook）粉絲專頁貼文表示，柯文哲近日與她聊北所的生活，讓人無法想像3坪羈押室是怎麼過日子。她貼文轉述，柯文哲說，吃飯是用像臉盆的器皿，把食物全混在一起，從不透明門底下的一個小洞遞進去，那場景就像拿廚餘去餵貓狗一樣。台北看守所對此回應表示，看守所依規定供應全體收容人飲食，並視用餐人數與習慣、食品衛生及種類，使用適當不鏽鋼皿具盛裝。聲明表示，另外，舍房送入口位置是受限舊有建築結構安全影響；北所為兼顧收容安全及健康，將持續維護環境衛生，規劃提升收容品質，以保障收容人權益。（編輯：張銘坤）1140920",
        # "1140915": "（中央社記者林長順台北15日電）京華城案被告柯文哲、應曉薇聲請具保停押獲北院裁准，北檢提抗告，高院撤銷原裁定發回更裁。北院今天重開羈押庭後，再度裁定柯文哲、應曉薇交保，且維持原交保金額。前台北市長柯文哲、中國國民黨籍台北市議員應曉薇涉京華城案等遭羈押禁見，日前聲請具保停押，台灣台北地方法院5日裁定柯文哲7000萬元交保，應曉薇3000萬元交保，都限制住居、限制出境、出海8月。合議庭要求兩人不得與同案被告、證人有任何接觸、騷擾、恐嚇或探詢案情行為，並接受配戴電子腳鐶、攜帶個案手機等科技設備監控。台灣台北地方檢察署以證人尚未詰問完畢，且柯文哲8日具保後即接觸證人陳智菡與陳宥丞等理由，9日向台灣高等法院提起抗告。高院認定檢察官抗告有理由，12日撤銷原裁定，發回原審法院另為適法處理。（編輯：陳清芳）1140915",
        # "1140914": "（中央社記者黃麗芸台北14日電）京華城案被告柯文哲、應曉薇聲請具保停押獲台北地院裁准，北檢抗告成功，北院合議庭明早重開羈押庭。外傳柯文哲支持者「小草」們將到場外聲援，北市警方預計出動40人維安、另安排40警待命。前台北市長柯文哲、國民黨台北市議員應曉薇涉京華城等案遭羈押禁見，日前聲請具保停押，台北地方法院5日裁定柯文哲新台幣7000萬元交保，應曉薇3000萬元交保，並均限制住居、限制出境、出海8月。因台北地檢署提起抗告，高院12日撤銷原裁定發回更裁。台北地院合議庭訂15日上午10時重開羈押庭，要求柯文哲、應曉薇當天上午9時到法警室報到。外傳「小草」們明天上午10時將到北院外幫柯文哲加油、打氣。對此，轄區警方、台北市警察局中正第一分局今天表示，為維護北院周邊交通和安全維護，明天將出動40名警力執行勤務，若有狀況則將再增派預備警力40人。（編輯：黃名璽）1140914",
        # "1140520": "（中央社記者林長順台北20日電）北院審理京華城案，今天傳喚市議員苗博雅作證。苗博雅受訪時說，質詢京華城案初衷就是守護台北市民超過百億的公共財，不應落入特定財團的口袋，至今沒有變過。台北地檢署偵辦京華城案、柯文哲政治獻金案，去年12月26日依貪污治罪條例違背職務收受賄賂罪、圖利、公益侵占、背信等罪嫌，起訴前台北市長柯文哲、威京集團主席沈慶京等11人，並具體求處柯文哲總計28年6月徒刑。台北地方法院今天再開審理庭，以證人身分傳喚社會民主黨台北市議員苗博雅，由檢辯交互詰問，合議庭也提訊在押被告柯文哲、沈慶京、國民黨台北市議員應曉薇、前台北市長辦公室主任李文宗進行訊問，下週前將裁定是否延長羈押。苗博雅出庭前受訪指出，出庭作證是國民義務，既然收到法院傳喚，一定會盡國民的義務，對於檢辯雙方和法官提出的所有問題，就是一個原則，據實以報。苗博雅說，根據媒體報導，柯文哲今年3月間在法院陳述時，主動說苗博雅的質詢是他的保障，但柯文哲的政黨「在我出庭前，運用政治操作來抹黑證人，牴觸他們高唱的司法改革精神」、「我個人可以承受住攻擊，但對其他證人會構成很大的政治壓力」。苗博雅強調，一開始在議會質詢京華城案到現在，就是為了守護台北市民超過百億元的公共財，這是市民共同的財產，不應該落入特定財團的口袋裡面，這是自己的初衷，沒有變過。北院今天上午先針對李文宗是否延押進行訊問，檢察官認為李文宗仍有勾串、滅證之虞，建請法院裁定延長羈押；李文宗則表示自己是無辜的，被冠上莫須有罪名，沒有延押必要。由於李文宗沒有要詰問苗博雅，合議庭訊問後，將李文宗還押台北看守所。合議庭接著勘驗苗博雅於民國110年、111年在市議會質詢柯文哲京華城案影片。柯文哲律師表示，從質詢過程可見，柯文哲對於京華城案確實不清楚，當時在議場的官員說明可證明，京華城案是依都市計畫法第24條規定辦理，沒有適法性的問題。檢方表示，柯文哲律師團聲請勘驗質詢影片，無非是要證明柯文哲不知情，例如柯文哲當時有「抓頭」的動作，但「抓頭」代表的意義一般並沒有明確解釋，無法就此認定為「不知情」。檢方進一步指出，柯文哲曾向媒體解釋自己的「抓頭」動作，意思是「頭殼抱著燒」，接受質詢時說不知情明顯是在卸責。（編輯：蕭博文）1140520",
        # "1140911": "（中央社記者林長順台北11日電）北院5日裁定柯文哲交保，北檢以柯接觸陳智菡等原因提抗告。柯辯護人今天指出，柯當時還沒收到裁定書，且被動與陳智菡同車。檢方表示，裁定5日出爐，清楚寫明不能接觸同案證人。前台北市長柯文哲涉京華城等案，聲請具保停押獲北院裁定新台幣7000萬元交保，限制住居於居所地，並限制出境、出海8月。合議庭並要求柯文哲不得與同案被告、證人有任何接觸、騷擾、恐嚇或探詢案情的行為，並接受左腳配戴電子腳鐶、攜帶個案手機等科技設備監控。台北地檢署認為，本案證人尚未詰問完畢，且柯文哲8日具保後，即與本案證人陳智菡、陳宥丞有所接觸，已違反法院具保命遵守的「不得與證人有任何接觸之行為」的事由，因此提起抗告，目前由台灣高等法院審理中。北院審理京華城案及柯文哲政治獻金案，今天再度開庭，傳喚柯文哲、前競選總部財務長李文宗、木可公司董事長李文娟到庭，並傳喚民眾黨秘書長周榆修、木可公關員工李婉萱作證。柯文哲律師在庭訊時指出。柯文哲8日交保離開法院時，尚未拿到裁定書，不清楚相關細節，且是「被動」與陳智菡等人同台、同車。裁定中提到「不得與同案證人」接觸，是否應僅限尚未出庭作證完成詰問的證人，希望法院釐清「同案證人」定義。公訴檢察官表示，合議庭5日已做出裁定，清楚載明「同案證人」，並未指是「尚未詰問的證人」，陳智菡曾與被告彭振聲聯繫，陳宥丞曾幫忙提供京華城案議會調查小組的資料，「不得與同案證人接觸」應該包含證據清單中的證人才為合理。審判長表示，檢方已對交保裁定提起抗告，若在裁定結果出來前，針對交保裁定內容做補充或變更，將使高院不知道要審的標的是什麼，因此在抗告結果出來前做補充或變更並不適當。（編輯：林恕暉）1140911",
        # "1140909": "（中央社記者林長順台北9日電）前台北市長柯文哲涉京華城等案，聲請具保停押獲北院裁定7000萬元交保，北市議員應曉薇則以3000萬元交保。北檢認為本案證人尚未詰問完畢，仍有羈押必要，今天下午6時許提起抗告。台北地檢署指出，依照台灣高等法院114年8月11日114年度抗字第1881號裁定（被告柯文哲、應曉薇延長羈押抗告遭高院駁回的裁定），認為被告柯文哲涉犯公益侵占罪部分，仍有重要證人尚未調查完畢。北檢盤點10月間尚待交互詰問的重要證人，至少包括黃景茂（10月2日）、張高祥、范有偉（10月16日）、黃珊珊（10月21日）、吳順民（10月30日）等人。檢察官主張不論貪污罪或公益侵占罪，在證人交互詰問完畢前，仍有羈押的必要。北檢表示，柯文哲昨天具保後，即與本案證人陳智菡、陳宥丞有所接觸，已違反法院具保命遵守的「不得與證人有任何接觸之行為」的事由。北檢指出，柯文哲具保後對即將於9月16日到法院作證的共同被告李文宗喊話，但共同被告李文宗就公益侵占的犯罪事實，與被告柯文哲有相互指證的關係。北檢表示，柯文哲於羈押禁見中，持續授權特定人士使用其「本人名義」的社群帳號，將法庭活動片面解讀、惡意扭曲、斷章取義，毫不避諱地隔空串證及製造輿論，抹黑、恐嚇對其不利證述的證人。至於應曉薇部分，北檢認為，尚有證人沈慶京、黃景茂、柯文哲、吳順民待交互詰問。「在證人詰問完畢前，應仍有羈押之必要」是檢察官的一貫主張。柯文哲、應曉薇偵查期間遭北檢聲請羈押禁見獲准，全案移審台北地方法院後，北院於今年1月2日裁定羈押禁見3個月，並先後裁定自4月2日、6月2日、8月2日起各延長羈押禁見2個月，這次羈押期限為10月1日期滿。柯文哲、應曉薇日前聲請具保停止羈押。北院5日裁定柯文哲以自己名義提出新台幣7000萬元保證金，應曉薇以自己名義提出3000萬元保證金後，均准予停止羈押，並均限制住居於居所地，並限制出境、出海8月，均需配戴電子腳鐶。應曉薇5日辦妥手續後離開法院，柯文哲當天律見後表示需再行深思，8日則同意由妻子陳佩琪辦理後續交保程序，於8日下午約2時30分離開法院。（編輯：李錫璋）1140909",
        # "1140907": "（中央社記者陳俊華台北7日電）北院裁定前民眾黨主席柯文哲交保。柯文哲妻子陳佩琪今天說，律師轉述柯文哲第一個心願，是希望立刻回新竹看柯媽媽，「也看看爸爸（的骨灰）放在哪裡，這是他一直懸在心上的心願」。台北地院審理京華城案，前台北市長柯文哲日前聲請具保停止羈押，5日獲北院裁定7000萬元交保，但柯文哲在律見後表示需再行深思。民眾黨指出，等待柯文哲於8日指示律師同意後，立即向北院辦妥交保程序，迎接柯文哲出來。陳佩琪今天晚間到土城看守所外，向支持者加油打氣。她在接受直播時表示，感謝小草、支持者對柯文哲的支持，始終不離不棄；明天她希望去北院幫柯文哲繳齊保釋金後，能夠很順利、平安地跟柯文哲回家。陳佩琪說，律師向她轉述，柯文哲第一個心願，就是希望立刻回新竹看媽媽，所以明天計劃交保後，第一個回新竹看柯媽媽，「也看看爸爸（的骨灰）放在哪裡，這是他一直懸在心上的心願」。陳佩琪指出，3月10日柯文哲父親告別式當天，柯文哲一直爭取能等父親火化、供奉好，但不被答應，沒辦法陪伴父親是柯文哲最大遺憾，所以「明天去新竹探視婆婆，看爸爸在哪裡」，接下來可能就是要認真研究官司如何攻防。陳佩琪表示，律師也跟她說，柯文哲希望可以有正常的書桌、椅子和檯燈，因為在北所裡都沒有桌椅，只能跪著、趴著看東西，且燈光昏暗，這一年來柯文哲快要把眼睛搞壞。陳佩琪說，明天也安排在北院前，簡單的跟大家短暫見面；如果時間足夠的話，柯文哲會全台從北到南，向曾經給他加油、鼓勵的人和團體，「我們都會一一的去跟大家道謝」。（編輯：林克倫）1140907",
        # "1140811": "（中央社記者劉世怡台北11日電）北院審理京華城案裁定柯文哲、應曉薇自2日起延長羈押禁見2個月。2人不服提起抗告，高院今天認定原裁定並無違法或不當，駁回抗告，即延長羈押禁見2個月確定。台灣高等法院指出，柯文哲、應曉薇前經原審法院裁定羈押禁見，因期間將屆，經原審台北地院法院訊問後，認定2人犯罪嫌疑重大，且原羈押原因及必要依然存在，因此裁定延長羈押2個月並禁止接見、通信。高院表示，柯文哲、應曉薇抗告主張犯嫌並非重大、無逃亡之虞、無勾串之虞、無羈押必要、原裁定理由不備、身體有恙非保外就醫難以痊癒，請求撤銷原裁定。高院合議庭表示，依卷內事證及向原審法院、看守所函調相關資料，認定2人主張均不足採信，因此認定本件抗告為無理由，予以駁回。本件延長羈押確定。台北地檢署偵辦京華城案、柯文哲政治獻金案，去年底依貪污治罪條例違背職務收受賄賂、圖利、公益侵占與背信等罪起訴前台北市長柯文哲、威京集團主席沈慶京、國民黨台北市議員應曉薇、前台北市長辦公室主任李文宗等11人，具體求處柯文哲總計28年6月徒刑。全案移審後，北院2度裁定在押的柯文哲、沈慶京、應曉薇與李文宗交保，經北檢抗告，高院2度發回更裁，北院1月2日裁定柯文哲、沈慶京、應曉薇、李文宗等4人裁定羈押禁見3個月。北院隨後裁定柯文哲、沈慶京、應曉薇與李文宗等4人，自4月2日、同年6月2日起分別延長羈押2月。北院7月21日裁定柯文哲、應曉薇均自8月2日起延長羈押2月，並禁止接見、通信。李文宗則獲裁定2000萬元交保，限制住居、限制出境出海及配戴電子腳鐶。李男7月23日辦保及配戴電子腳鐶完成，離開法院。此外，沈慶京獲裁定1億8000萬元交保並限制住居、限制出境出海及配戴電子腳環及個案手機。沈慶京7月24日下午繳交保證金，晚間配戴電子腳環及個案手機後，離開法院。（編輯：蕭博文）1140811",
        # "1140813": "（中央社記者劉世怡台北13日電）台北地院7日開庭審理京華城案，前台北市長柯文哲休庭時情緒激動批評檢察官並丟資料、弄倒水瓶。北檢發函聲請調取當天休庭時間的法庭錄影畫面，北院今天收文，將評議准駁。北院7日召開審理庭，提訊在押的柯文哲，並以證人身分傳喚前台北市副秘書長李得全、前台北市副市長黃珊珊到庭，由檢辯交互詰問。柯文哲在休庭時情緒激動，拿起麥克風對著還在法庭內的公訴檢察官表示，「你們每天這樣亂編故事，不羞恥嗎」、「你們都在想怎麼編故事害人」等語，並對檢察官說出非理性言詞。柯文哲還把紙本資料摔向檢察官，並弄倒水瓶。台北地檢署後來發布新聞稿，對柯文哲在法院審理期日的中間休庭時間，對蒞庭檢察官的非理性言詞及舉動，表達嚴正譴責，並呼籲當事人應遵守法庭秩序，以維護理性、安全的訴訟環境。（編輯：張銘坤）1140813"
    }
    topicSTR: str = "京華城MINI"

    # articleDICT: dict[str, str] = {
    #     "1131229": "（中央社首爾29日綜合外電報導）韓國濟州航空一架載有181人的班機從泰國曼谷起飛降落韓國務安國際機場時，衝出跑道撞護欄起火。根據韓聯社報導，死亡人數上升至179人，全機含機組員僅2人生還。緊急救援人員救出兩名機組人員，並轉移到安全地點，當地衛生官員表示他們意識仍清楚。（譯者：陳政一）1131229",
    #     "1131229": "（中央社首爾29日綜合外電報導）韓國濟州航空今天空難事故機上181人已知177人罹難、2人失蹤、2人獲救，2個黑盒子已找到。英國衛報（The Guardian）報導，韓國國土交通部表示，機上2個黑盒子已由調查人員在殘骸中尋獲，其中在當地時間上午11時30分找到座艙語音紀錄器（CVR），並在下午2時24分找到飛航資料紀錄器（FDR）。根據美國有線電視新聞網（CNN），國土交通部表示，從影片中看來，飛機的起落架似乎沒有放下，但他們將利用飛航資料紀錄器的資料進行進一步調查。務安機場跑道預計將持續關閉至明年1月1日凌晨5時，但這一時間可能會根據情況進行調整。另外，機場已設立臨時停屍間，當局正與罹難者家屬合作，安排將已確認身分的死者轉移到外部設施。韓聯社報導，國土交通部在記者會中表示，關於事故原因，目前有鳥擊、起落架故障等多種說法，但確切的原因有待調查。針對務安機場跑道較短、可能導致事故的說法，國土交通部表示，務安機場跑道長達2800公尺，過去一直有類似機型在該機場安全起降，因此難以將跑道長度視為事故原因。（譯者：王嘉語/核稿：嚴思祺）1131229",
    #     "1131229": "（中央社首爾29日綜合外電報導）韓國濟州航空空難最新死亡數已上升到至少151人。韓聯社報導，當地時間上午9時左右，濟州航空7C2216客機在務安國際機場以機腹著陸，之後脫離跑道撞向機場圍牆，且爆炸起火。失事客機的機型為波音737-800，載有181人，其中乘客175人（韓國籍173人、泰國籍2人），機組員有6人。消防部門推估，除了2人獲救，機上大部分人員已經遇難。韓國國土交通部航空政策室室長朱鍾浣在記者會表示，務安國際機場塔台上午8時57分左右向這架客機發出鳥擊預警，到了8時58分，機長發出求救訊號。朱鍾浣還說，客機約於9時嘗試降落19號跑道，但9時3分左右，客機在沒有放下起落架的情況下以機腹著陸，並撞上機場圍牆。（編輯：陳彥鈞/核稿：嚴思祺）1131229",
    #     "1131230": "（中央社首爾30日綜合外電報導）韓國代理總統崔相穆（Choi Sang-mok）今天下令，一旦濟州航空（Jeju Air）事故的善後工作完成，將對全國航空運作系統進行緊急安全檢查。路透社報導，韓國昨天發生境內最嚴重空難，濟州航空7C2216號班機以機腹著陸並滑出跑道末端，撞上務安（Muan）國際機場圍牆引起爆炸，共179人喪命，2人死裡逃生。崔相穆在首爾舉行的災難管理會議上表示，目前首要任務是確定罹難者身分、支持罹難者家屬，以及治療兩名空難生還者，為此不惜投入所有資源。崔相穆也說：「即使在最終結果出來前，我們也要求官員透明公開事故調查過程，及時通知罹難者家屬。」崔相穆指出：「事故善後工作完成後，將要求國土交通部對整個飛機運作系統進行緊急安全檢查，防止事故再次發生。」濟州航空7C2216號班機是從泰國首都曼谷起飛，機上載有175名乘客與6名機組人員。這架飛機昨天上午9時許試圖迫降在韓國南部的務安國際機場。事故中倖存的2名機組員正因傷接受治療。消防官員表示，調查人員正在調查鳥擊與天候情況是否為事故可能因素。專家表示有許多問題仍待釐清，包括飛機速度為何如此之快，以及當飛機在跑道滑行最終撞上圍牆時，起落架為何沒有放下。（譯者：屈享平/核稿：李佩珊）1131230",
    #     "1140101": "（中央社首爾1日綜合外電報導）韓國濟州航空班機29日在務安機場降落時起落架未放出，機腹觸地高速滑行後撞上跑道尾端施工中的水泥牆爆炸，成為韓國境內最慘重空難，航空安全專家質疑水泥牆是否設置不當。路透社報導，機長發出緊急求救訊號後，仍嘗試降落的原因尚在調查中。然而，2024年初上傳的務安機場操作手冊中提到，這面牆距離跑道尾端過近，並建議在擬議的擴建工程中重新審視設置位置。韓國國土交通部一名官員昨天表示，當局需要先檢查這份文件後才能回應相關問題。航空安全專家批評水泥牆的設置位置，這道牆上安裝輔助飛機降落的導航系統。飛安顧問公司Aero Consulting Experts執行長艾默（Ross Aimer）向路透社表示：「不幸的是，那就是造成所有人死亡的原因，因為他們直接撞上一個水泥結構體。它本來就不該在那裡。」在此同時，警方努力辨識遇難者身分，在機場等候的家屬們，由於無法立刻領回親人的遺體而焦急不已。韓國警察廳表示，仍有5具遺體身分尚待確認，警方正增派人手和運用快速DNA分析儀，以加快身分辨認工作。（譯者：陳昱婷/核稿：徐睿承）1140101",
    #     "1140106": "（中央社首爾6日綜合外電報導）濟州航空失事179人喪命，當中一家9口全數罹難，僅剩家中名為「布丁」的愛犬獨活，昨天動保協會志工帶牠到首爾市府前搭建的聯合靈堂，布丁沒有吠叫，只是默默凝望罹難者牌位。「韓國時報」（The Korea Times）今天報導，韓國濟州航空7C2216號班機上月29日降落韓國務安機場時發生重大事故，造成179死2傷。機上最年長乘客是慶祝本月邁入80大壽、參與家族出遊的裴姓老翁。布丁飼主裴姓老翁與家人同遊泰國，搭機返回韓國時遇到這場空難，一家9口全數罹難。這一家罹難者包含裴翁夫婦、2名女兒、1名女婿、3個孫子（分別是12、18、19歲），以及6歲孫女，家中剩下布丁獨活。布丁現由韓國大型動保團體「維護地球動物權益協會」（CARE）收容。穿著藍色毛孩套裝的布丁大約在今天下午2時由動保志工抱著牠來到公祭現場。在其他動保志工手捧菊花靠近祭壇，以及CARE負責人金榮煥（Kim Young-hwan，音譯）唸悼詞時，布丁靜靜看著聯合公祭的罹難者牌位。CARE打算繼續照料布丁直至替牠找到新飼主為止，並且即日起正式受理布丁的領養申請。（譯者：曹宇帆/核稿：洪啓原）1140106",
    #     "1140122": "（中央社首爾22日綜合外電報導）韓國濟州航空班機去年12月因滑出跑道，撞上跑道末端混凝土牆造成慘重傷亡，韓國國土交通部今天說，將拆除班機失事地點務安國際機場的混凝土牆。路透社報導，雖然調查人員仍在調查濟州航空7C2216班機墜毀的原因，包括據傳遭到鳥擊。但專家表示，跑道末端支撐導航天線的巨大混凝土牆，有可能是使這場災難傷亡更加慘重的原因。在墜機事件後宣布的第一批廣泛改革中，當局說，他們將對7個機場的類似天線建造新地基或做其他調整，將天線安裝在地面以下，或採用易摧毀的結構，以降低風險，這些機場包括務安國際機場和韓國最繁忙機場之一的濟州國際機場。國土交通部在聲明中說：「務安國際機場計劃完全拆除現有的混凝土牆，並將（儀表著陸系統）定位器重新安裝在易摧毀的結構。」去年12月29日的墜機事故造成179人死亡，只有坐在波音737-800客機機尾附近的兩名機組人員倖存。錄影片段顯示，這架客機在沒有放下起落架的情況下高速降落，滑過跑道盡頭撞上混凝土牆並爆炸。機場跑道設計也因不符合安全標準而受到批評，促使當局擴大跑道後端沒有重大障礙物的安全區域。國土交通部說，將確保所有機場都有240公尺長的跑道安全區，以滿足所有相關規定。墜機前，務安機場的跑道安全區大概有200公尺長。（譯者：林沂鋒/核稿：陳政一）1140122",
    #     "1140127": "（中央社首爾27日綜合外電報導）一名官員今天說，韓國當局向國際民航組織、美國、法國和泰國當局，提交濟州航空班機去年12月的空難初步報告，當中提及兩具發動機附著鳥血和羽毛，以及機師因鳥擊而呼叫求救。路透社報導，這份今天發布的報告指出，韓國歷來傷亡最慘重的空難相關調查仍在進行中，並且著重於鳥擊的影響，以及有關發動機和降落引導結構體「定位器」的分析。隸屬聯合國的機構國際民航組織（ICAO）要求事故調查員於30天內提交這起事故的初步報告，並建議在12個月內公布最終版。這份25日分發給罹難者家屬的報告，強調韓國調查員初步調查的許多發現，包括機師在執行降落時曾討論看到一群鳥。根據事故報告，機師通報遭鳥擊的確切時間仍待查證，不過這架失事客機「執行重飛期間，曾因鳥擊而發出3次Mayday緊急求救訊號」，「檢查兩具發動機後，發現均附著羽毛和鳥血」。報告說：「（濟州航空失事班機）撞向路堤後，局部機身爆炸並起火，兩具發動機埋入路堤的土堆裡，前機身散落在距路堤30至200公尺處。」這份報告並未說明，導致兩個飛行紀錄器於機師呼叫求救前，同步停止記錄的原因，僅說明失事班機於距離地面152公尺並以時速298公里的速度飛行之際，黑盒子停止記錄。（譯者：曹宇帆/核稿：陳昱婷）1140127",
    #     "1140206": "（中央社首爾6日綜合外電報導）濟州航空去年底發生179人罹難的韓國歷來最嚴重空難，初步調查報告提及失事班機機師曾因鳥擊而呼救。韓國當局今天表示，將下令境內所有機場安裝熱成像攝影機和鳥類探測雷達。法新社報導，這起空難發生後，當局對全國機場展開特別安全檢查，上述新計畫是其中一環，同時將就特別易吸引鳥類的設施展開全面性調查。國土交通部指出：「所有機場將裝設至少一部熱成像攝影機。」聲明表示，目標明年起開始推動相關計畫，同時也將部署移動式聲波驅鳥器，主要用以因應「中大型鳥類」。國土交通部並表示：「所有機場將安裝鳥類探測雷達，以提升早期發現遠距飛鳥的能力，同時改善飛行器的反應能力。」鳥類探測雷達將偵測飛鳥的體型大小與移動路徑，這些資訊將會傳送給航管人員，進而向機師傳達。國土交通部同時表示，將就遷移易吸引飛鳥的設施「建立法律基礎」，例如廚餘處理廠與果園，讓這些設施遠離機場，並且針對新建設施訂定管制距離。韓國當局於1月25日公布濟州航空空難初步調查報告指出，雖然機師通報遭鳥擊的確切時間仍待查證，不過這架失事客機「執行重飛期間，曾因鳥擊而發出3次Mayday緊急求救訊號」、「檢查兩具發動機後，發現均附著羽毛和鳥血」。（譯者：曹宇帆/核稿：何宏儒）1140206",
    #     "1140721": "（中央社首爾21日綜合外電報導）韓國濟州航空（Jeju Air）去年12月空難奪走179條人命，熟悉空難調查的知情人士今天透露，韓國主導的空難調查中發現「明確證據」，顯示機師在鳥擊事件後關閉了受損較輕的發動機。路透社報導，消息人士表示，包括座艙語音紀錄器、電腦數據，以及在殘骸中發現的發動機實體開關證據顯示，機師在接近預定降落時間前不久發生鳥擊事件後，採取緊急措施，關閉了左側發動機，而非右側發動機。消息人士告訴路透社：「調查團隊有明確證據與備份資料，因此調查結論將不會改變」。由於調查人員尚未發布包含這些證據的正式報告，消息人士要求不要具名。一名政府相關人士表示，針對尋獲的飛機發動機的檢查顯示，鳥擊事件與墜機發生前並未發現任何故障。去年12月29日，濟州航空一架波音737-800客機在務安國際機場墜毀，機上181名乘客與機組員中，除2人外全數罹難，成為韓國國內最嚴重的空難事件。根據聽取過簡報的第3位消息人士表示，調查人員19日向罹難者家屬簡報時指出，鳥擊造成右側發動機受損程度較嚴重，並有間接證據顯示，機師當時關閉的是受損較輕的左側發動機。每日放送電視台（MBN TV）與韓聯社（Yonhap）在內的韓國媒體19日與20日曾披露此消息。韓國調查當局19日取消了原定最新發動機調查進展記者會。罹難者家屬委任律師表示，家屬在預計舉行記者會前已聽取簡報，但對報告似乎將責任歸咎於機師，卻未探討其他肇因，而反對公開。失事的濟州航空客機緊急迫降時衝出務安國際機場跑道，撞上裝有導航設備的水泥牆，造成機身起火並引發部分爆炸。罹難者家屬代表及濟州航空機師工會於週末期間表示，調查重點應該放在水泥牆本身。航空專家認為，水泥牆可能是造成傷亡嚴重的主要原因。濟州航空機師工會指出，韓國航空及鐵道事故調查委員會（ARAIB）在2具發動機內均發現鳥類遺骸的情況下，仍主張左側發動機無問題，是在「誤導民眾」。機師工會指控ARAIB未能提出科學與技術依據證明只靠左側發動機仍可安全降落飛機，企圖將機師當成「代罪羔羊」。（譯者：劉淑琴/核稿：陳政一）1140721",
    # }
    # topicSTR: str = "濟州航空空難"

    # articleDICT: dict[str, str] = {
    #     "1140920": "只是一段測試資料罷了。"
    # }
    # topicSTR: str = "test"

    aitlas = AItlas(username=G_accountDICT["username"], apikey=G_accountDICT["api_key"], url=G_accountDICT["url"], llm=G_accountDICT["llm"])
    for time_s, article_s in articleDICT.items():
        KG = aitlas.scan(inputSTR=article_s.replace("\n", ""), timeRefSTR=time_s)
        # pprint(KG)

    view = aitlas.aitlasViewPacker(directoryNameSTR=topicSTR)
    aitlas.view(directoryNameSTR=topicSTR)
    # isPersonBool = alias.is_person(entity, utteranceLIST) #=>Maybe
    # isLocation = alias.is_location(entity, utteranceLIST)
    # print("{} 是 Person 嗎？{}".format(entity, isPersonBool))
