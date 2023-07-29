#for name the basic intent based on the number of "entity"
from ArticutAPI import Articut
from pprint import pprint
from requests import post
import time


username = "******************" #這裡填入您在 https://api.droidtown.co 使用的帳號 email。若使用空字串，則預設使用每小時 2000 字的公用額度。
apikey   = "******************" #這裡填入您在 https://api.droidtown.co 登入後取得的 api Key。若使用空字串，則預設使用每小時 2000 字的公用額度。

url = "https://api.droidtown.co/Loki/Call/" 

articut = Articut(username, apikey) 

def insert_utt(y,index):
    name= ['danlen_0e','danlen_1e','danlen_2e','danlen_3e','danlen_4e']
    payload = {
                "username" : "******************", # 這裡填入您在 https://api.droidtown.co 使用的帳號 email。     Docker 版不需要此參數！
                "loki_key" : "******************", # 這裡填入您在 https://api.droidtown.co 登入後取得的 loki_key。 Docker 版不需要此參數！
                "project": "JiouProj", #專案名稱
                "intent": name[index], #意圖名稱
                "func": "insert_utterance",
                "data": {
                "utterance":y,   #utterance
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

def inputSTRS():
    utt=utternace(txt, s)
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
            if len(nouns) <=danlen_1e: 
                print(nouns,i,f"一個")
                print(utternace(txt, s)[i])
                insert_utt(utternace(txt, s)[i], danlen_1e)
            elif len(nouns) ==danlen_2e:
                print(nouns,i,f"二個")
                print(utternace(txt, s)[i])
            elif  len(nouns) ==danlen_3e: 
                print(nouns,i,f"三個")
                print(utternace(txt, s)[i])
            elif len(nouns) >=danlen_4e:       
                print(nouns,i,f"四個以上")
                print(utternace(txt, s)[i])
            else:
                pass
        time.sleep(retry_delay)

s=0 #從txt檔的第幾筆資料"
txt="../data/suspending1.txt"
def main():
    utternace(txt, s)
    inputSTRS()    
    
main()