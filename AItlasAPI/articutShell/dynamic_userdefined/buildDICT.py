#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
import json
from pathlib import Path


def isUniqe(alreadyDICT: dict[str, str], v: str) -> bool:
    for k in alreadyDICT.keys():
        if k == v:
            return False
    return True


if __name__ == "__main__":
    fileName: str = ""  # 需填入
    currentDir: str = os.getcwd()

    jsonPath = Path(currentDir) / "dict_collection" / fileName

    if not jsonPath.exists():
        jsonPath.touch()
        with open(jsonPath, "w", encoding="utf-8") as f:
            f.write("{}")

    alreadyDICT: dict[str, list[str]] = {}
    with open(jsonPath, "r", encoding="utf-8") as f:
        alreadyDICT = json.load(f)

    while 1:
        key: str = input("輸入key: ")
        value: str = input("輸入value: ")
        valueLIST: list[str] = value.split()

        alreadyDICT[key] = valueLIST
        stop = input("按0以結束: ")
        if stop == "0":
            break

    with open(jsonPath, "w", encoding="utf-8") as f:
        json.dump(alreadyDICT, f, ensure_ascii=False, indent=4)
