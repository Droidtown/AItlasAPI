from ArticutAPI import Articut
from pprint import pprint
from requests import post
import os
import re
import json
import time



purgePat = re.compile("</?\w+(_+\w?)?>")
pronounDropPat = re.compile("^<ENTITY_pronoun>[^<]+</ENTITY_pronoun>|^<ENTITY_person>[^<]+</ENTITY_person>")
innerDropPat = re.compile("^<FUNC_inner>[^<]+</FUNC_inner>")
username = "********************" #這裡填入您在 https://api.droidtown.co 使用的帳號 email。若使用空字串，則預設使用每小時 2000 字的公用額度。
apikey   = "******************" #這裡填入您在 https://api.droidtown.co 登入後取得的 api Key。若使用空字串，則預設使用每小時 2000 字的公用額度。
                
articut = Articut(username, apikey)

folder_path = "../data/People1607"   
    
## get the assgined verb from 1101536 abtstracts
def main(folder_path,s1):  
         
    start_time = time.time()  # 紀錄開始時間
    end_index = s1 + 100    # the number is running files for each
    
    for filename in os.listdir(folder_path)[s1:end_index]:
        
        file_path = os.path.join(folder_path, filename)

        with open(file_path, "r", encoding="utf-8") as f:      
            
            data = json.load(f)           
            
            abstract = data.get("abstract")
            
            pattern = r"（[^名又a-zA-Z]*）|\([^名又a-zA-Z]*\)|，[^a-zA-Z]+人|，{{0,1}}[^a-zA-Z。]+人\b"
            
            ABSTRACT= [p.replace("（）","")  for p in abstract.split("。") if any(re.findall(pattern, p))]
                     
            result = " ".join(ABSTRACT)
                            
            if len(result)>=10:
                            
                resultDICT = articut.parse(result, level="lv2")
                
                for i in resultDICT["result_pos"]:
                
                    toAddLIST=[]               
                    retry_delay=0.8
                    try:                    
                        if "<ACTION_verb>擔任</ACTION_verb>" in i:
                            i = re.sub(pronounDropPat, "", i)
                            i = re.sub(innerDropPat, "", i)
                            toAddLIST.append(re.sub(purgePat, "", i))
                            time.sleep(retry_delay) 
                                            
                            with open('../data/suspending.txt', 'a', encoding='utf-8') as f:   #the file for saving the utterances with the assigned verb
                                suspending = set(item for item in toAddLIST if item)
                                f.writelines(f"{item}\n" for item in suspending)
                        else:
                            pass
                        
                    except Exception as e:
                        print(f"{e}")
                        pass           
            else:
                pass
                
    end_time = time.time()
    print(f"{s1}到{end_index}共花了""{:.1f}秒".format(end_time - start_time))  

    url = "https://api.droidtown.co/Loki/Call/" 
    
    txt="../data/suspending.txt"
    

def insert_utt(txt,s):
    
    payload = {
                "username" : "anching.cathy@gmail.com", # 這裡填入您在 https://api.droidtown.co 使用的帳號 email。     Docker 版不需要此參數！
                "loki_key" : "m7f*3bB6^7GfjovYjBjaf$bn4wcjgyU", # 這裡填入您在 https://api.droidtown.co 登入後取得的 loki_key。 Docker 版不需要此參數！
                "project": "JiouProj", #專案名稱
                "intent": "danlen98", #意圖名稱
                "func": "insert_utterance",
                "data": {
                "utterance":utternace(txt, s),   #utterance(txt,s)
                "checked_list": [ #勾選的詞性
                        "ENTITY_noun"
                        ]
                        }
                        }                       
    response = post(url, json=payload).json()
    pprint(response['msg'])


def utternace(txt, s):
    batch = s+10
    with open(txt, 'r', encoding="utf-8") as f:
        utterance= f.readlines()
        utterance = [line.strip() for line in utterance if line.strip()][s:batch]
    return utterance


url = "https://api.droidtown.co/Loki/Call/" 

txt="../data/suspending.txt"
   

if __name__ == '__main__': 
    s1 = 70100  #start from?= end +100
    while s1 <= 71000:  #end to ?
        main(folder_path, s1)
        s1 += 100  
    os.system("say 'finish running'") 
    
    s=189  #index of txt #########
    with open(txt, 'r', encoding="utf-8") as f:
            utterance= f.readlines()
            utterance = [line.strip() for line in utterance if line.strip()]  
            length= len(utterance)
            print(f"總共有{length}筆，從{s}筆開始") 
            print(utterance)   
            
    retry_delay = 1.0     
    while s <= length:
        insert_utt(txt,s)
        s+=10
        time.sleep(retry_delay)
    os.system("say 'input the next start'")    
