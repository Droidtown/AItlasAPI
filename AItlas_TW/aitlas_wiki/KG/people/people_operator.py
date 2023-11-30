#!/usr/bin/env python
# -*- coding:utf-8 -*-

from people import action

def subjectFinder(subj, actionLIST=[]):
    if actionLIST == []:
        for a_str in action:
            objLIST = ["DO({})TO({})AT({})".format(a_str, x.obj, "、".join(x.time)) for x in action[a_str] if x.subj==subj]
            print(objLIST)
    else:
        for a_str in actionLIST:
            objLIST = [x.obj for x in action[a_str] if x.subj==subj]
            objLIST = ["DO({})TO({})AT({})".format(a_str, x.obj, "、".join(x.time)) for x in action[a_str] if x.subj==subj]

if __name__ == "__main__":
    subjectFinder(subj="末綱聰子", actionLIST=[])