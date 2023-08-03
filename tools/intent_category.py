from ArticutAPI import Articut
from pprint import pprint
from requests import post
import os
import time
import json

url = "https://api.droidtown.co/Loki/Call/" 

account_path ="../data/account.info"   #填入你的account path

with open(account_path, encoding="utf-8") as f:  
    accountDICT = json.load(f)
    
username =accountDICT["username"]
apikey=accountDICT["api_key"]

articut = Articut(username, apikey)

projectName = "Fu4zhe2"  #填入專案名稱（順便copy loki_key)

loki_key = "5UBX2l9O9hkhlgL#kxqQROjh^-l_#99" # 填入loki_key

txt="../data/suspending_fuzhe.txt"   #填入文本path

targetVerb ='負責' #填入target verb

intentName = "".join(articut.parse(targetVerb, level="lv3", pinyin="HANYU")["utterance"][0]).replace(" ", "")
 
name = [f"{intentName}_{num}e" for num in range(0, 5)]

def createIntent(i):
    global projectName
    global loki_key
    global name  
    url = "https://api.droidtown.co/Loki/Call/"
    payload = {
        "username" : username,
        "loki_key" : loki_key, #填入loki_key
        "project": projectName,
        "intent": name[i],
        "func": "create_intent",
        "data": {
            "type": "basic" 
        }
    }

    response = post(url, json=payload).json()
    print(response)

def insert_utt(y,index):
    global projectName
    global name
    global loki_key
    payload = {
                "username" : username,
                "loki_key" : loki_key, #填入loki_key
                "project": projectName, 
                "intent": name[index], 
                "func": "insert_utterance",
                "data": {
                "utterance":[y],   
                "checked_list": ["LOCATION", "ENTITY_noun"]
                        }
                        }                       
    response = post(url, json=payload).json()
    pprint(response['msg'])  

def utternace(txt,s,s1):  
    with open(txt, 'r', encoding="utf-8") as f:
        utterance= f.readlines()
        utterance = [line.strip() for line in utterance if line.strip()][s:s1]
    return utterance

def inputSTRS():
    utt=utternace(txt, s, s1)
    retry_delay = 0.2
    for i, u in enumerate(utt):
        resultDICT = articut.parse(u, level="lv2")
        nounStemLIST = articut.getNounStemLIST(resultDICT)
        for nouns in nounStemLIST:
            if len(nouns) == 1: 
                print(nouns,f"第{s+i+1}筆",f"一個")
                print(utternace(txt, s,s1)[i])
                insert_utt(utternace(txt, s, s1)[i], 1)    
                i+=1                      
            if len(nouns) ==2: 
                print(nouns,f"第{s+i+1}筆",f"二個")
                print(utternace(txt, s,s1)[i])
                insert_utt(utternace(txt, s, s1)[i], 2)
                i+=1
            if len(nouns) ==3: 
                print(nouns,f"第{s+i+1}筆",f"三個")
                print(utternace(txt, s,s1)[i])
                insert_utt(utternace(txt, s, s1)[i], 3)
                i+=1
            if len(nouns) >=4: 
                print(nouns,f"第{s+i+1}筆",f"四個以上")
                print(utternace(txt, s,s1)[i])
                insert_utt(utternace(txt, s, s1)[i],4)
                i+=1
            else:
                pass
            time.sleep(retry_delay)

s = 1800       # 填入開始索引 
s1 = s + 10  # each loop
if __name__ == "__main__":
    #i=1   #分類為1個entity開始命名
    #while i<5:                     #5 是代表create 有四個entities的
        #createIntent(i)
        #i+=1        
    #os.system("say 'finish creation'") 
    while s1<=2341:          #為結束索引 也可以自行改 
        print(f"從{s}")
        utternace(txt, s,s1)
        inputSTRS()        
        s+= 10   # each loop
        s1 = s + 10 # each loop
        print("\n", f"接下來從{s}開始") 
    os.system("say 'next run'") 