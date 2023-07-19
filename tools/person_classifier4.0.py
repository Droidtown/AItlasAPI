#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import os
import re
import shutil
from pprint import pprint


personPatLIST = ["^{}\s?（[^名又a-zA-Z]*）",
                 "^{}\s?\([^名又a-zA-Z]*\)",
                 "^{}，[^a-zA-Z]+人\b"
                ]


dataDIR = "../data/zhwiki_abstract_1607"
destination_dir = "../data/People_test"

def main(entryDIR):
    """
    分辨 fileLIST 中的每一個 json 檔，看它是不是屬於「人類」。如果是的話，就加入列表 [PersonLIST] 中
    """
    personLIST = []
    for json_f in os.listdir(entryDIR):
        try:
            with open("{}/{}".format(entryDIR, json_f), encoding="utf-8") as f:
                topicSTR = json_f.replace(".json", "")
                entrySTR = json.load(f)["abstract"]
            for p in personPatLIST:
                pat = re.compile(p.format(topicSTR))
                if len(list(re.finditer(pat, entrySTR))) > 0:
                    personLIST.append(topicSTR)
                else:
                    pass
        except IsADirectoryError:
            pass
    return personLIST


#if __name__ == "__main__":
    #personLIST = []
    #for init_s in os.listdir(dataDIR)[:10]:
        #if init_s.startswith("._"):
            #pass
        #else:
            #personLIST.extend(main("{}/{}".format(dataDIR, init_s)))
    #pprint(personLIST)
if __name__ == "__main__":
    personLIST = []
    data_files = os.listdir(dataDIR)
    num_files = len(data_files[:10])
    batch_size = 10

    for i in range(0, num_files, batch_size):
        batch_files = data_files[i:i+batch_size]

        for init_s in batch_files:
            if init_s.startswith("._"):
                continue
            else:
                personLIST.extend(main("{}/{}".format(dataDIR, init_s)))

        #pprint(personLIST)
        
            ## check if there is a destination_dir
                #if not os.path.exists(destination_dir):
                    #os.makedirs(destination_dir)
                    
        for root, dirs, files in os.walk(dataDIR):
            for file in files:
                if file.endswith(".json"):
                    for member in personLIST:
                        if file.startswith(member):
                            source_path = os.path.join(root, file)
                            destination_path = os.path.join(destination_dir, file)
                            shutil.copy(source_path, destination_path)
                            print(f"檔案 {file} 已成功複製到 {destination_dir} 資料夾。")
    else:
        pass
                                            

print("Finished processing part of the data files.")
    
    
    
    
    
    
