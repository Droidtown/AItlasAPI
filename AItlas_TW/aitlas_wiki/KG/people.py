#!/usr/bin/env python3
# -*- coding:utf-8 -*-

schema = {"verb_01":{"attribute":[],
                     "entity_01":[{"name":"person_01", "time":["time_01"]}]
                     },
          "verb_02":{"attribute":[],
                     "entity_02":[{"name":"person_02", "time":["time_02"]}
                                  ]
                     },
          }
# => person_01 DO verb_01 in/on/at/to/from entity_01 (at/in/on time_01)



action = {"代表":{"attribute":[],
                 "日本":[{"name":"末綱聰子", "time":["2008"]},
                        {"name":"武士", "time":[]}
                        ],
                 "德國":[{"name":"朱利安·申克", "time":["2008"]}
                        ]
                },
          "參加":{"attribute":[],
                 "奧林匹克":[{"name":"末綱聰子", "time":["2008"]}
                           ],
                  },
          "出戰":{"attribute":[],
                 "北京奧會":[{"name":"朱利安·申克", "time":["2008"]}
                           ]
                }
          }