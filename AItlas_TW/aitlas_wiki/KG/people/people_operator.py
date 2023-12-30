#!/usr/bin/env python
# -*- coding:utf-8 -*-

from people import action

def subjectFinder(subj, actionLIST=[]):
    objLIST=[]
    if actionLIST == []:
        for a_str in action:
            objLIST.extend(["DO({})TO({})AT({})".format(a_str, x.obj, "、".join(x.time)) for x in action[a_str] if x.subj==subj])
    else:
        for a_str in actionLIST:
            objLIST = [x.obj for x in action[a_str] if x.subj==subj]
            objLIST = ["DO({})TO({})AT({})".format(a_str, x.obj, "、".join(x.time)) for x in action[a_str] if x.subj==subj]
    return objLIST

def subjectDeducer(subj, actionLIST=[]):
    who = subjectFinder(subj)
    if who == []:
        if actionLIST == []:
            return "Cannot deduction"
        else:
            for a_str in actionLIST:
                if a_str in action:
                    return "Maybe"
                #objLIST = [x.obj for x in action[a_str] if x.subj==subj]
                #objLIST = ["DO({})TO({})AT({})".format(a_str, x.obj, "、".join(x.time)) for x in action[a_str] if x.subj==subj]
    else:
        return who

if __name__ == "__main__":
    #who = subjectFinder(subj="末綱聰子", actionLIST=["代表"])
    #print(who)

    isPerson = subjectDeducer(subj="小明", actionLIST=["代表"])
    print(isPerson)