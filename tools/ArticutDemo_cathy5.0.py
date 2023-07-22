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

folder_path = "../data/People1607" #place "your" path not mine

def main(s):
    start_time = time.time()  # for counting the time
    get_verbs_from_abstracts(folder_path, s)
    end_time = time.time()
    print(f"共花了""{:.1f}秒".format(end_time - start_time))  
    
## define the function to get the assgined verb from 1101536 abtstracts
def get_verbs_from_abstracts(folder_path,s):  
     
    end_index = s + 100    # the number of running files for each
    
    for filename in os.listdir(folder_path)[s:end_index]:
        
        file_path = os.path.join(folder_path, filename)

        with open(file_path, "r", encoding="utf-8") as f:      
            
            data = json.load(f)           
            
            abstract = data.get("abstract")    
   
            retry_delay = 0.3

            toAddLIST = []
            
            resultDICT = articut.parse(abstract, level="lv2")
            
            for i in resultDICT["result_pos"]:
                try:                    
                    if "<ACTION_verb>擔任</ACTION_verb>" in i:
                        i = re.sub(pronounDropPat, "", i)
                        i = re.sub(innerDropPat, "", i)
                        toAddLIST.append(re.sub(purgePat, "", i))
                        #print(toAddLIST) 
                    
                        with open('../data/suspending.txt', 'a', encoding='utf-8') as f:   #the file for saving the utterances with the assigned verb
                                suspending = [item for item in toAddLIST if item]
                                f.writelines(f"{item}\n" for item in suspending)
                    else:
                        #print("failed to get verb")
                        time.sleep(retry_delay)
                        
                                                                        
                except Exception as e:
                    print(f"{e}")
                    time.sleep(retry_delay)
                    pass
                    
if __name__ == '__main__':
    s = 28900   #start from?   your progress 
    while s <= 30000:  #end to ?
        main(s)
        s += 100   

main(s)
os.system("say 'start from scratch and end to happiness'")
