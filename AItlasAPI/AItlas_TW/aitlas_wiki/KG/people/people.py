#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# => person_01 DO verb_01 in/on/at/to/from entity_01 (at/in/on time_01)
from people_type import People, VerbTypes, IntransitiveVerb, TransitiveVerb, DitransitiveVerb

action:dict[str, list[VerbTypes]]

action = {"代表":[TransitiveVerb("日本", "末綱聰子", ["2008"]),
                 TransitiveVerb("德國", "朱利安．申克", ["2008"]),
                 TransitiveVerb("日本", "武士", []),
                ],
          "參加":[TransitiveVerb("奧林匹克", "末綱聰子", ["2008"])],
          "出戰":[TransitiveVerb("北京奧會", "朱利安．申克", ["2008"])]
          #"":[TransitiveVerb()]
          #None:{"attribute":[],
                #"comfert.AV":{"enty":["one.AV", "true.AV"]}
                #}
          }

