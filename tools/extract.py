#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import wikipedia
import json
import os

def getWikiSection(topic):
    content = {
        "title": wikipedia.page(topic, auto_suggest = False).title,
        "text": wikipedia.summary(topic, auto_suggest = False)
    }

    file_name = "json_en/" + topic + ".json"
    file_exists = os.path.isfile(file_name)

    if not file_exists:
        print(topic)
        with open(file_name, "w") as outfile:
            json.dump(content, outfile)

def main():
    file = open("topic.txt", "r")
    for line in file:
        getWikiSection(line.strip())
    file.close()

if __name__ == "__main__":
    main()
