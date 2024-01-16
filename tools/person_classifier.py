#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import os
import re

purgedPat = re.compile("[\(（].*?[\)）]")

personPat = re.compile("[^a-zA-Z\d或論敵險事繫食示]+([人士員]|出身|學家)$|(?<=[，,。；？！、])[^a-zA-Z\d或論敵險事繫食示，。？！；、]+([人士員]|出身|學家)(?=[、，。])")



dataDIR = "../data/local_data/person"
destination_dir = "../data/People/{}"

def removalListMaker(entryDIR):
    removeLIST = []
    fileLIST = os.listdir("{}/{}".format(dataDIR, entryDIR))
    for f in fileLIST:
        try:
            jContent = json.load(open(f"{dataDIR}/{entryDIR}/{f}"))["abstract"]
            jContent = purgedPat.sub("", jContent)
            if list(personPat.finditer(jContent)) == []:
                removeLIST.append(f)
            else:
                pass
        except:
            removeLIST.append(f)

    return list(set(removeLIST))

if __name__ == "__main__":
    personLIST = []
    data_dirs = os.listdir(dataDIR)
    num_files = len(data_dirs)
    batch_size = 10

    for e_dir in data_dirs:
        removeLIST = removalListMaker(e_dir)
        for r in removeLIST:
            if r.startswith("."):
                try:
                    os.remove(f"{dataDIR}/{e_dir}/{r}")
                except:
                    pass
            else:
                os.remove(f"{dataDIR}/{e_dir}/{r}")
        if os.listdir(f"{dataDIR}/{e_dir}") == []:
            os.removedirs(f"{dataDIR}/{e_dir}")
