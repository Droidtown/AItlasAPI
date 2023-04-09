#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from glob import glob
import logging
import json
import os
import re
import tempfile

logFORMAT = "%(funcName)s>>%(message)s"
logging.basicConfig(level=logging.DEBUG, format=logFORMAT)

from ArticutAPI import Articut
with open("../account.info", encoding="utf-8") as f:
    accountDICT = json.load(f)



class AItlas:
    def __init__(self, AItlasDIR):
        self.articut = Articut(username=accountDICT["username"], apikey=accountDICT["apikey"])
        self.AItlasDIR = AItlasDIR
        posAliasDICT = {"NOUN":"ENTITY_(nounHead|nouny|noun|oov)",
                        "UD":"UserDefined",
                        "MOD": "MODIFIER",
                        "VERB": "(ACTION_verb|VerbP|ACTION_quantifiedVerb)",
                        "CONJ": "FUNC_conjunction",
                        "0,2":"{0,2}"
                        }
        self.posPurgePat = re.compile("</?\w+?(_\w+)*?>")
        self.actionPatLIST     = [re.compile(r"<{UD}>([^<]+?</{UD}>)<{VERB}>喜歡</{VERB}><{VERB}>([^<]+?</{VERB}>)<{NOUN}>[^<]+?</{NOUN}>((<{VERB}>等</{VERB}><{NOUN}>([^<]+?</{NOUN}>))|(<{CONJ}>[^<]+?</{CONJ}><{NOUN}>([^<]+?</{NOUN}>))){0,2}".format(**posAliasDICT)), #中華鷓鴣喜歡吃蚱蜢等昆蟲及螞蟻
                                  re.compile(r"<{UD}>([^<]+?</{UD}>)(<TIME_justtime>[^<]+?</TIME_justtime>)?(<{MOD}>[亦也]</{MOD}>)?<{VERB}>([^<]+?</{VERB}>)(<{MOD}>[^<]+?</{MOD}>)?<{NOUN}>([^<]+?</{NOUN}>)".format(**posAliasDICT)) #中華鷓鴣同時亦吃野生果實
                                  ]
        #self.entityVerbPatLIST = [re.compile(r"<{UD}>([^<]+?</{UD}>)<{VERB}>喜歡</{VERB}><{VERB}>([^<]+?</{VERB}>)<{NOUN}>[^<]+?</{NOUN}>((<{VERB}>等</{VERB}><{NOUN}>([^<]+?</{NOUN}>))|(<{CONJ}>[^<]+?</{CONJ}><{NOUN}>([^<]+?</{NOUN}>))){0,2}".format(**posAliasDICT)), #中華鷓鴣喜歡吃蚱蜢等昆蟲及螞蟻
                                  #re.compile(r"<{UD}>([^<]+?</{UD}>)(<TIME_justtime>[^<]+?</TIME_justtime>)?(<{MOD}>[亦也]</{MOD}>)?<{VERB}>([^<]+?</{VERB}>)(<{MOD}>[^<]+?</{MOD}>)?<{NOUN}>([^<]+?</{NOUN}>)".format(**posAliasDICT)) #中華鷓鴣同時亦吃野生果實
                                 #]

        self.classifierPatLIST = [
        ]
        self.entityKindPatLIST = [
        ]

        self.entityAttrPatLIST = [re.compile("<{UD}>([^<]+?</{UD}>)<AUX>[^<]+?</AUX><{NOUN}>([^<]+?</{NOUN}><{MOD}>性</{MOD}>)".format(**posAliasDICT)) #鷓鴣是雜食性
                                  ]
        self.locationPatLIST   = [
        ]
        self.personAttrPatLIST = [
        ]

        self.classifierDICT = {}
        self.entityKindDICT = {}
        self.entityAttrDICT = {}
        self.locationDICT = {}
        self.personAttrDICT = {}

        if os.path.exists("../data/preprocessed/AItlas-core/action.json"):
            with open("../data/preprocessed/AItlas-core/action.json", encoding="utf-8", mode="a+") as jFILE:
                self.actionDICT = json.load(jFILE)
        else:
            self.actionDICT = {}

        return None

    def cloudSeeding(self, stage02DIR):
        self.sourceDIR = stage02DIR
        self._actionAItlasMaker()

        return True

    def _actionAItlasMaker(self):
        for f in glob("{}/*.json".format(self.sourceDIR)):
            try:
                with open(f, encoding="utf-8") as jFILE:
                    sourceDICT = json.load(jFILE)
                title = sourceDICT["id"]
                textLIST = ["{}{}".format(title.replace("_", ""), i) for i in sourceDICT["text2"].split(title) if i != title]
            except:
                print("Failed to open file {}!".format(f))

            for t in textLIST:
                tempDICT = tempfile.NamedTemporaryFile(mode="w+")
                json.dump({"_userDefined":[title,]}, tempDICT)
                tempDICT.flush()
                resultDICT = self.articut.parse(t, userDefinedDictFILE=tempDICT.name)
                if resultDICT["status"] == True:
                    #<Remove duplicated subject position noun>
                    for i in range(0, len(resultDICT["result_pos"])):
                        if "><" in resultDICT["result_pos"][i]:
                            iLIST = resultDICT["result_pos"][i].replace("><", ">ʡʢ<").split("ʡʢ")
                            if set(re.sub(self.posPurgePat, "", iLIST[1])).issubset(set(re.sub(self.posPurgePat, "", iLIST[0]))):
                                iLIST.pop(1)
                            resultDICT["result_pos"][i] = "".join(iLIST)
                    #</Remove duplicated subject position noun>
                    for i in resultDICT["result_pos"]:
                        if len(i) > 1:
                            for p in self.actionPatLIST:
                                semanticGroup = p.search(i)
                                #verbGroup = p.search(i)
                                if semanticGroup == None:
                                    pass
                                else:
                                    semanticLIST = [arg for arg in list(semanticGroup.groups()) if arg.endswith(">")]
                                    #<Finding the mainverb>
                                    verbLIST = [v for v in semanticLIST if v.endswith("verb>") or v.endswith("VerbP>")]
                                    if verbLIST == []:
                                        pass
                                    else:
                                        verb = re.sub(self.posPurgePat, "", verbLIST[0])
                                        logging.debug("主要動詞：{}".format(verb))
                                        if verb in self.actionDICT.keys():
                                            pass
                                        else:
                                            self.actionDICT[verb] = {"attr":[]}
                                    #</Finding the mainverb>
                                        #<Finding object>
                                        objLIST = [obj for obj in semanticLIST[semanticLIST.index(verbLIST[0]):] if obj.endswith("nounHead>") or obj.endswith("nouny>") or obj.endswith("noun>") or obj.endswith("oov>")]
                                        if objLIST == []:
                                            pass
                                        else:
                                            objLIST = [re.sub(self.posPurgePat, "", obj) for obj in objLIST if obj[0] != "<"]
                                            logging.debug("主要受詞：{}".format(",".join(objLIST)))
                                            for o in objLIST:
                                                if o in self.actionDICT[verb].keys():
                                                    pass
                                                else:
                                                    self.actionDICT[verb][o] = []
                                        #</Finding object>
                                            #<Finding subject>
                                            subjLIST = [subj for subj in semanticLIST[:semanticLIST.index(verbLIST[0])] if subj.endswith("UserDefined>")]
                                            if subjLIST == []:
                                                pass
                                            else:
                                                subj = re.sub(self.posPurgePat, "", subjLIST[0])
                                                for o in objLIST:
                                                    self.actionDICT[verb][o].append(subj)
                                            #</Finding subject>


                else:
                    return False
        logging.debug(self.actionDICT)
        return True


if __name__ == "__main__":
    stage02DIR = "../data/preprocessed/stage02_text"
    AItlasDIR = "../data/preprocessed/AItlas-core"
    aitlas = AItlas(AItlasDIR=AItlasDIR)
    aitlas.cloudSeeding(stage02DIR)
