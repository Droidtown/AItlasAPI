##找動詞的句子
from ArticutAPI import Articut
import re
import os
import json
import time



account_path ="../data/account.info"   #填入你的account path

target_folder = "../data/utterances"

os.makedirs(target_folder, exist_ok=True)

with open(account_path, encoding="utf-8") as f:  
    accountDICT = json.load(f)
    
username =accountDICT["username"]
apikey=accountDICT["api_key"]
articut = Articut(username, apikey)

purgePat = re.compile("</?\w+(_+\w?)?>")

def verbExtractor(VERB):
    verbLIST = []
    if VERB is None:
        pass
    else:
        for i in VERB:
            if i == []:
                pass
            else:
                for e in i:
                    verbLIST.append(e[-1])

    return verbLIST

def Noun_utt(entities, result_pos):
    result=[]
    for i, e in enumerate(entities):      
        # print("第{}個句子，名詞是{}]".format(i,e))
        utt = ''.join(re.findall(r'\d*[一-龥]*', result_pos[i]))  #wash the details 
        # print("有{}個的名詞句子:{}".format(len(e),utt)) 
        result.append(utt) 
    result=[u for u in result if u!='']
    return result      #名詞的句子

def create_Vjson(VerbLIST):
    if VerbLIST:
        for verbs in VerbLIST:
            resultDICT = articut.parse(verbs, level="lv3", pinyin="HANYU")
            if "utterance" in resultDICT.keys( ):
                pinyinName = "".join(resultDICT["utterance"][0]).replace(" ", "")      
                data = {"pinyin": pinyinName}
                filename =f"{verbs}.json"
                target_path = os.path.join(target_folder, filename)
                if not os.path.exists(target_path):
                    with open(target_path, "w") as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                    print(f"Created {filename}")
                else:
                    print(f"already existed {filename}")
            else:
                pass
    else:
        print(f"get no verbs")
        
           
def main(folder_path,s):
    end_index = s1 + 1   # 填入each loop
    for dir_s in os.listdir(folder_path)[s:end_index]:  
        if dir_s == ".DS_Store":
            pass
        else:
            for j_file in os.listdir("../data/People_Source230730/{}".format(dir_s)):
                if j_file.startswith("."):
                    os.remove("../data/People_Source230730/{}/{}".format(dir_s, j_file))
                else:
                    with open("../data/People_Source230730/{}/{}".format(dir_s, j_file), encoding="utf-8") as f:
                        data = json.load(f)
                        verb_data = data["abstract"] #要parse的句子
                        resultDICT = articut.parse(verb_data, level="lv1") 
                        verb = articut.getVerbStemLIST(resultDICT)  #get verbs with index      
                        VerbLIST=set(verbExtractor(verb)) #get only verbs 
                        create_Vjson(VerbLIST) #create  V.json files
                        entities=articut.getNounStemLIST(resultDICT) #get entities with index
                        result_pos=resultDICT['result_pos']
                        result = Noun_utt(entities,result_pos) # utterance with the intersection of verbs and entities
                        relay_time= 2.0
                        if VerbLIST:
                            for V in VerbLIST: 
                                for rt in result:          
                                    if V in rt:
                                        print("Found targetVerb {} in file {}".format(V, j_file))  
                                        results = articut.parse(rt, level="lv1") 
                                        entities_result= articut.getNounStemLIST(results)
                                        result_pos1=results['result_pos']
                                        time.sleep(relay_time)
                                        new_data={}
                                        for i, e in enumerate(entities_result): 
                                            # print("第{}個句子，名詞是{}，動詞是{}]".format(i+1,e,V))
                                            utt = ''.join(re.findall(r'\d*[一-龥]*', result_pos1[i]))  #wash the details 
                                            n = len(e)
                                            # print("有{}個的名詞句子:{}".format(n,utt)) 
                                            new_data[f"{n}e"] = [utt]
                                            filename = f"{V}.json"
                                            target_path = os.path.join(target_folder, filename)
                                            with open(target_path, "r") as f:
                                                existing_data = json.load(f)
                                                for key, value in new_data.items():
                                                    existing_data.setdefault(key, []) #處理 the utterance with the same{n}
                                                    for item in value:
                                                        if item not in existing_data[key]:
                                                            existing_data[key].append(item)
                                                            with open(target_path, 'w', encoding='utf-8') as file:
                                                                json.dump(existing_data, file, ensure_ascii=False, indent=4)
                                                            print("{}sucessfully saved in :{}".format(new_data,filename))
                                                        else:
                                                            print("{}already existed in:{}".format(new_data,filename))                                                     
                                    else: 
                                        pass
                            time.sleep(relay_time)
                        else:
                            pass
        
        

folder_path = "../data/People_Source230730"          
 
if __name__ == '__main__': 
    s1 =  1000 #填入起點資料夾
    end = 2000 #填入中（間）點資料夾:6532
    print(f"從{s1}開始")
    start_time=time.time()
    while s1 <= end:  
        main(folder_path, s1)
        s1 += 1  # 填入each loop 跟上面一樣
        print("\n", f"接下來從第{end+1}資料夾開始",'\n') 
    
    os.system("say 'next round'")     
    
