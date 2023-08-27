#!/usr/bin/env python3
# -*- coding:utf-8 -*-


from KG.people import action as actionDICT
peopleLIST = []
for v_D in actionDICT:
    for obj in actionDICT[v_D]:
        if obj == "attribute":
            pass
        else:
            for p_L in actionDICT[v_D][obj]:
                peopleLIST.append(p_L[0])
peopleLIST = {e for e in peopleLIST}

def is_person(personSTR, utteranceLIST=[]):
    """
    return
    0: no
    0.5: maybe
    1: yes
    """
    if person in peopleLIST:
        return 1
    #else:
        #get verbs from utteranceLIST
        #if a verb is listed in actionDICT, and the obj/entity matches:
        #    return 0.5
        #else:
        #    return 0


if __name__ == "__main__":
    person = "末綱聰子"
    is_person(person)
