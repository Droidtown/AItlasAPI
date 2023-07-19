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
username = "anching.cathy@gmail.com" #這裡填入您在 https://api.droidtown.co 使用的帳號 email。若使用空字串，則預設使用每小時 2000 字的公用額度。
apikey   = "******************" #這裡填入您在 https://api.droidtown.co 登入後取得的 api Key。若使用空字串，則預設使用每小時 2000 字的公用額度。


#folder_path = "../data/People1607" 
articut = Articut(username, apikey)


## define the function to get the assgined verbs from 1101536 abtstracts
def get_verbs_from_abstracts(folder_path,s):  #s 代表要從第幾筆開始跑

    start_time = time.time()  # 紀錄開始時間
    
    end_index = s + 100    #每次設定跑?筆(100)
    
    for filename in os.listdir(folder_path)[s:end_index]:
        
        file_path = os.path.join(folder_path, filename)

        with open(file_path, "r", encoding="utf-8") as f:      
            
            data = json.load(f)           
            
            abstract = data.get("abstract")    
   
            retry_delay = 0.3

            toAddLIST = []
            
            resultDICT = articut.parse(abstract, level="lv2")
            
            for i in resultDICT["result_pos"]:
                if "<ACTION_verb>擔任</ACTION_verb>" in i:
                    i = re.sub(pronounDropPat, "", i)
                    i = re.sub(innerDropPat, "", i)
                    toAddLIST.append(re.sub(purgePat, "", i))
                    print(toAddLIST) 
                    #先把有“擔任“的存起來
                    with open('../data/suspending.txt', 'a', encoding='utf-8') as f:
                            suspending = [item for item in toAddLIST if item]
                            f.writelines(f"{item}\n" for item in suspending)
                            
                    time.sleep(retry_delay)
                    break

                 else: 
                    print("Failed to get verbs")
                    pass
                    
    end_time = time.time()
    print(f"共花了""{:.1f}秒".format(end_time - start_time))   
      
        
                        #url = "https://api.droidtown.co/Loki/Call/"
                      
                        ## create intent
                        #payload = {
                            #"username" : "anching.cathy@gmail.com", # 這裡填入您在 https://api.droidtown.co 使用的帳號 email。     Docker 版不需要此參數！
                            #"loki_key" : "**********************", # 這裡填入您在 https://api.droidtown.co 登入後取得的 loki_key。 Docker 版不需要此參數！
                            #"project": "JiouProj", #專案名稱
                            #"intent": "danlen", #意圖名稱
                            #"func": "create_intent",
                            #"data": {
                                #"type": "basic" #意圖類別
                            #}
                        #}
                        ## insert utterance
                        payload = {
                            "username" : "anching.cathy@gmail.com", # 這裡填入您在 https://api.droidtown.co 使用的帳號 email。     Docker 版不需要此參數！
                            "loki_key" : "***********************", # 這裡填入您在 https://api.droidtown.co 登入後取得的 loki_key。 Docker 版不需要此參數！
                            "project": "JiouProj", #專案名稱
                            "intent": "danlen", #意圖名稱
                            "func": "insert_utterance",
                            "data": {
                                "utterance":toAddLIST,
                                "checked_list": [ #勾選的詞性
                                        "ENTITY_noun"
                                    ]
                                }
                                }
                                
                        #response = post(url, json=payload).json()


#folder_path = "../data/People1607" #欲run的資料夾                     
get_verbs_from_abstracts(folder_path, s) #s是從第幾筆開始
os.system("say 'give me the next index'")

                        

