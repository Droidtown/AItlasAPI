from pprint import pprint
from requests import post
import time
import os

url = "https://api.droidtown.co/Loki/Call/" 

txt="../data/suspending.txt"

def main(txt,s):
    # start_time = time.time()  # 紀錄開始時間 
    payload = {
                    "username" : "*********************", # 這裡填入您在 https://api.droidtown.co 使用的帳號 email。     Docker 版不需要此參數！
                    "loki_key" : "*********************", # 這裡填入您在 https://api.droidtown.co 登入後取得的 loki_key。 Docker 版不需要此參數！
                    "project": "JiouProj", #專案名稱
                    "intent": "danlen98", #意圖名稱
                    "func": "insert_utterance",
                    "data": {
                    "utterance":utternace(txt, s),
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

if __name__ == '__main__':
    with open(txt, 'r', encoding="utf-8") as f:
        utterance= f.readlines()
        utterance = [line.strip() for line in utterance if line.strip()]  
        length= len(utterance) 
         
        s = 70                                #type the next start s
        print(f"總共有{length}筆，從{s}筆開始") 
        retry_delay = 1.0     
        
        while s <= length:
            main(txt,s)
            s+=10
            time.sleep(retry_delay)
            
main(txt, s)

os.system("say 'type the next start s'")