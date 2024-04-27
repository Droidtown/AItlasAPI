#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import os
import re
import time
from ArticutAPI import Articut


''' 
get data from mainText 從主文得到資料，並且清洗為
1.{"人犯罪名處刑期":"result_pos"}
2.{"罪名判刑期":"result_pos"}
3.{"罪名":"result_pos"}
4.{"刑期":"result_pos"}

起迄到第s個檔案
'''


# articut parse 
def articut(inputSTR):
    articut = Articut(username="anching.cathy@gmail.com", apikey="uIESx@v2Z6o*Rq!Os-c=ew3e4IXQ+Hi")
    resultDICT = articut.parse(inputSTR)

    return resultDICT

# get the json files 
def collect_file_path(folder_path,s):
        file_path=[]
        for filename in os.listdir(folder_path)[:s]:
                file_path.append(os.path.join(folder_path, filename)) # 從資料夾當中，獲取檔案名稱
        return file_path
        
# get the  mainText
def get_MainT_save(file_path): 
    results=[]
    for path in file_path:
        try:
            with open(path, encoding = 'utf8') as file:
                raw_data = json.load(file)       
                utt = raw_data["mainText"]
                if isinstance(utt, str) and len(utt) > 8:
                    utt_result=(utt.replace("\n",""))
                    results.append(utt_result)
                elif isinstance(utt, dict):
                    result_segmentation = utt.get('result_segmentation', 'Key not found')
                    results.append(re.sub("/", "", result_segmentation))
        except Exception as e:
            print(f"Failed: {e}")

    return results

# extract the target utt (e.g., 罪 or 處)
def sentenceFilter(inputSTR, targetSTR):
    removePat = re.compile("[\u4E00-\u9FFF\d]")
    punctuation = "".join(set(removePat.sub("", inputSTR)))
    escaped_punctuation = re.escape(punctuation)
    if not escaped_punctuation:  # 如果沒有出現在punctuation裡面的符號，就忽略
        escaped_punctuation = " "  
    puncPat = re.compile(f"[{escaped_punctuation}]")
    inputLIST = puncPat.split(inputSTR)

    resultLIST = []
    for i in inputLIST:
        if targetSTR in i:                                
            resultLIST.append(i)
    return resultLIST

# get the data before regex
def before_pat(clear_data,i):
    target = []
    for sublist in clear_data:
        if sublist:
            data=sublist[i]
            target.append(data)
    return target

# use the pattern to get the text from utt with POS
def pat_to_text(CrimePat, utt_POS):
    
    Matches = list(CrimePat.finditer(utt_POS))
    if Matches:
        matched_text =  Matches[0].group(0)
        return matched_text
    else:
        return ""

def articut_text(target_data):  #把抓到的target data，articut得到 target result_pos
    result_pos = []
    retry_delay = 0.8
    for i in target_data:
        resultDICT = articut(i)
        if "result_pos" in resultDICT:
            result_pos.append(resultDICT["result_pos"])
        else:
            print("Key 'result_pos' not found in resultDICT:", resultDICT)
         
        time.sleep(retry_delay)
    return sum(result_pos, [])


def target_result(TargetPat, result_posLIST): #把 target result_pos regex 並 得到 {"target_utt":"target_result_pos"}
    Target_dict = {}
    Target_pattern = re.compile(TargetPat)
    for arti_raw in result_posLIST:
        TargetSTR = pat_to_text(Target_pattern, arti_raw)
        Chinese_text = re.sub(r'[^\u4e00-\u9fff\d]', '', TargetSTR)
        
        pos_result = articut(Chinese_text)
        
        if 'result_pos' in pos_result:
            result_pos = pos_result['result_pos'][0]
        else:
            result_pos = "" 

        if Chinese_text:
            Target_dict[Chinese_text] = result_pos
            
    return Target_dict

def arti_and_save(data, TargetPat, Target_path):    
    Target_posLIST = articut_text(data)
    Target_results = target_result(TargetPat, Target_posLIST)
    with open(Target_path,'a',encoding='utf8') as file:
        json.dump(Target_results , file, ensure_ascii=False, indent=4)
    return Target_results


folder_path ="../data/臺灣澎湖地方法院_刑事"
People_path = '../data/PeopleALL.json'
Merged_path = "../data/MergedALL.json"
Crime_path = '../data/CrimeALL.json'
Penalty_path = "../data/PenaltyALL.json"


PeoplePat ='.*'
MergedPat = '((?<=犯</ENTITY_oov)|(?<=[犯結]</ACTION_verb>)|(?<=犯</ENTITY_nouny>)).*'
CrimePat = '((?<=犯</ENTITY_oov)|(?<=[犯結]</ACTION_verb>)|(?<=犯</ENTITY_nouny>)).*(<ENTITY_nouny>[^<]+</ENTITY_nouny>|<ENTITY_oov>罪</ENTITY_oov>|<ENTITY_nounHead>罪</ENTITY_nounHead>)'
PenaltyPat = '(?=<處</ACTION_verb>)?([^>]+>[^<]+</MODIFIER>|[^>]+>[^<]+</ENTITY_nouny>)([^>]+>[^<]+</ENTITY_nounHead>)?([^>]+>[^<]+</TIME_[^>]+>)'

s = 100
if __name__ == '__main__':    
     
    file_path = collect_file_path(folder_path,s) #獲取資料夾裡面到.json檔
    results_FMT = get_MainT_save(file_path) #從剛剛得到的檔案中，extract主文並取得內容
    
    sentenceList=[] #取罪名與刑期
    for texts in results_FMT:
        target_utt = sentenceFilter(inputSTR=texts, targetSTR="罪") + sentenceFilter(inputSTR=texts, targetSTR="處")
        sentenceList.append(target_utt)
        clear_data = [c for c in sentenceList if len(c)== 2 and "罪" in c[0] and "處" in c[1]] #得到target utt list of ['許見安幫助犯洗錢防制法第十四條第一項之洗錢罪', '處有期徒刑參月']
    
    merged_data = [''.join(sublist) for sublist in clear_data] 
    
    #extract 犯(罪名+刑期,人） 
    People_resultsDICT = arti_and_save(merged_data, PeoplePat, People_path)
    
    #extract 罪名+刑期 
    merged_resultsDICT = arti_and_save(merged_data, MergedPat, Merged_path)

    # extract only 罪名
    crime_data= before_pat(clear_data, 0)
    Crime_resultsDICT = arti_and_save(crime_data,CrimePat,Crime_path)

    # extract only 刑期 
    penalty_data = before_pat(clear_data, 1)  
    penalty_resultsDICT = arti_and_save(penalty_data, PenaltyPat, Penalty_path)  
