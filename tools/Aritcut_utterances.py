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

account_path ="../data/account.info"   #填入你的account path

with open(account_path, encoding="utf-8") as f:  
    accountDICT = json.load(f)
    
username =accountDICT["username"]
apikey=accountDICT["api_key"]

articut = Articut(username, apikey)

url = "https://api.droidtown.co/Loki/Call/" 

folder_path = "../data/People_Source230730"  #填入資料來源

place_path=  "../data/suspending_fuzhe.txt"  #填入暫存處

target_verb = "負責"      #填入動詞

if not os.path.exists(place_path):
    with open(place_path, 'w', encoding='utf-8') as file:
        file.write(target_verb)
    print("success！")
else:
    print("Ready to go!")
                     
def remove_text_before_target(phrase, target):
    try:
        target_index = phrase.index(target)
        return phrase[target_index:]
    except ValueError:
        pass
    return phrase

def main(folder_path,s1):  
    
    end_index = s1 + 100   # 填入each loop
    
    for dir_s in os.listdir(folder_path)[s1:end_index]:  
        if dir_s == ".DS_Store":
            pass
        else:
            for j_file in os.listdir("../data/People_Source230730/{}".format(dir_s)):
                if j_file.startswith("."):
                    os.remove("../data/People_Source230730/{}/{}".format(dir_s, j_file))
                else:
                    with open("../data/People_Source230730/{}/{}".format(dir_s, j_file), encoding="utf-8") as f:
                        data = json.load(f)
                        if target_verb in data["abstract"]:
                            print("Found targetVerb {} in file {}".format(target_verb, j_file))   
                            resultDICT = articut.parse(data["abstract"])

                            for r in resultDICT["result_pos"]:  
                                toAddLIST=[]
                                retry_delay = 0.8
                                try:
                                    if "<ACTION_verb>負責</ACTION_verb>" in r:            #填上target_verb
                                        r = re.sub(pronounDropPat, "", r)
                                        r = re.sub(innerDropPat, "", r)
                                        if len(r)<=1:
                                            pass
                                        else:
                                            toAddLIST.append(re.sub(purgePat, "", r))
                                        
                                        print(toAddLIST) 
                                        
                                        with open(place_path, 'r', encoding='utf-8') as file:
                                                content = file.read()
                                                result = [remove_text_before_target(sentence, target_verb) for sentence in toAddLIST]
                                                for i in result:
                                                    if i not in content:
                                                        with open(place_path, 'a', encoding='utf-8') as file:
                                                            file.write(i + '\n')                                          
                                                
                                        time.sleep(retry_delay) 
                                    else:
                                        pass
                                except ValueError:
                                    pass                                     
                        else:
                            pass
    print(f"到第{s1+100}個資料夾") #填入跟上面一樣的loop
    
def count_lines(place_path):
    with open(place_path, 'r') as file:
        lines = file.readlines()
        return lines

if __name__ == '__main__':    
    s1 =  0 #填入起跑點
    end = 1000 #填入中（間）點或終點:6532  
    print(f"從{s1}開始")
    start_time=time.time()
    while s1 <= end:  
        main(folder_path, s1)
        s1 += 100  # 填入each loop 跟上面一樣
        print("\n", f"接下來從第{s1}資料夾開始",'\n') 
    
    os.system("say 'next round'") 
    
    print("蒐集到",len(count_lines(place_path)),"個句子")    
    