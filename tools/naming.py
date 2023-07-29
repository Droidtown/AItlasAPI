from ArticutAPI import Articut
from pprint import pprint
from requests import post
import time


username = "*******************" #這裡填入您在 https://api.droidtown.co 使用的帳號 email。若使用空字串，則預設使用每小時 2000 字的公用額度。
apikey   = "*******************" #這裡填入您在 https://api.droidtown.co 登入後取得的 api Key。若使用空字串，則預設使用每小時 2000 字的公用額度。

url = "https://api.droidtown.co/Loki/Call/" 

articut = Articut(username, apikey) 

def insert_utt(y,index):
    name= ['danlen_0e','danlen_1e','danlen_2e','danlen_3e','danlen_4e']
    payload = {
                "username" : "*******************", # 這裡填入您在 https://api.droidtown.co 使用的帳號 email。     Docker 版不需要此參數！
                "loki_key" : "*******************", # 這裡填入您在 https://api.droidtown.co 登入後取得的 loki_key。 Docker 版不需要此參數！
                "project": "JiouProj", #專案名稱
                "intent": name[index], #意圖名稱
                "func": "insert_utterance",
                "data": {
                "utterance":[y],   #utterance
                "checked_list": [ #勾選的詞性
                        "ENTITY_noun"
                        ]
                        }
                        }                       
    response = post(url, json=payload).json()
    pprint(response['msg'])  

def utternace(txt,s,s1):  #sfor start, s1 for the end
    with open(txt, 'r', encoding="utf-8") as f:
        utterance= f.readlines()
        utterance = [line.strip() for line in utterance if line.strip()][s:s1]
    return utterance

def inputSTRS():
    utt=utternace(txt, s, s1)
    retry_delay = 0.5
    for i, u in enumerate(utt):
        resultDICT = articut.parse(u, level="lv2")
        nounStemLIST = articut.getNounStemLIST(resultDICT)
        #pprint(nounStemLIST)
        for nouns in nounStemLIST:
            danlen_1e = 1
            danlen_2e = 2
            danlen_3e = 3
            danlen_4e = 4 
            if len(nouns) <= 1: 
                print(nouns,s+i+1,f"零/一個")
                print(utternace(txt, s,s1)[i])
                insert_utt(utternace(txt, s, s1)[i], danlen_1e)
                i+=1                      
            if len(nouns) ==2: 
                print(nouns,f"第{s+i+1}筆",f"二個")
                print(utternace(txt, s,s1)[i])
                insert_utt(utternace(txt, s, s1)[i], danlen_2e)
                i+=1
            if len(nouns) ==3: 
                print(nouns,f"第{s+i+1}筆",f"三個")
                print(utternace(txt, s,s1)[i])
                insert_utt(utternace(txt, s, s1)[i], danlen_3e)
                i+=1
            if len(nouns) >=4: 
                print(nouns,f"第{s+i+1}筆",f"四個以上")
                print(utternace(txt, s,s1)[i])
                insert_utt(utternace(txt, s, s1)[i], danlen_4e)
                i+=1
            else:
                pass
            time.sleep(retry_delay)


txt="../data/suspending.txt"
def main(s, s1):
    utternace(txt, s,s1)
    inputSTRS()
    s+=40
    s1+=40      
    
s = 0  # 從 第幾筆資料 
s1 = s + 40 
if __name__ == "__main__":
    while s1<=600: #欲處理到哪一筆
        main(s, s1)
        s+=40
        s1 = s + 40  
    os.system("say 'next run'") 
