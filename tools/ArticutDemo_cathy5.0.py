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


#folder_path = "../data/People1607" #資料夾是中文字的檔名（即不包括表情符號.英文字.數字）
articut = Articut(username, apikey)


## define the function to get the assgined verbs from 1101536 abtstracts
def get_verbs_from_abstracts(folder_path,s):  #s 代表要從第幾筆開始跑

    start_time = time.time()  # 紀錄開始時間
    
    end_index = s + 100    #每次跑1百筆

    for filename in os.listdir(folder_path)[s:end_index]:
        file_path = os.path.join(folder_path, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            abstract = data.get("abstract")

            resultDICT = articut.parse(abstract, level="lv2")

            toAddLIST = []

            for i in resultDICT["result_pos"]:

                    if "<ACTION_verb>擔任</ACTION_verb>" in i:
                        i = re.sub(pronounDropPat, "", i)
                        i = re.sub(innerDropPat, "", i)
                        toAddLIST.append(re.sub(purgePat, "", i))
                        print(toAddLIST)
                        
                        existing_data = set()
                        
                        # read already there
                        with open('../data/iu.txt', 'r', encoding='utf-8') as f:
                            existing_data = set(line.strip() for line in f)
                        
                        # 写入新的数据，避免重复
                        with open('../data/iu.txt', 'a', encoding='utf-8') as f:
                            new_data = [item for item in toAddLIST if item not in existing_data]
                            f.writelines(f"{item}\n" for item in new_data)                       
                            
                            print(f"recorded")

        
                        url = "https://api.droidtown.co/Loki/Call/"
                      
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
                       
                        
                        max_retries = 2
                        retry_delay = 30
                        
                        for _ in range(max_retries):
                            resultDICT = post(url, json=payload).json()
                            #response = post(url, json=payload).json()
                            pprint(resultDICT)
                            if resultDICT ["status"] == True:
                                #pprint(resultDICT)
                                break
                            else:
                                time.sleep(retry_delay)
                        
                        # 仍然没有成功请求，则印出來
                        else:
                            print("Failed to get a successful response after multiple retries")                        
                                               
                        

                    else:
                        pass


folder_path = "../data/People1607" #資料夾是中文字的檔名（即不包括表情符號.英文字.數字）                       
#get_verbs_from_abstracts(folder_path, 22100) 

def run_get_verbs(start, end):
    start_time = time.time()  # 紀錄開始時間
    for j in range(start, end, 100):        
        try:
            get_verbs_from_abstracts(folder_path, j)
        except Exception as e:
            print(f"Error occurred: {e}")
            pass     
    end_time = time.time()
    #execution_time = end_time - start_time
    print(f"跑了{end-start}共花了""{:.1f}秒".format(end_time - start_time)) 

### 調整
run_get_verbs(23000, 24000)

os.system("say 'give me the next index'")

                        

