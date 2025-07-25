#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from pathlib import Path
from AItlasAPI import AItlas
import json

if __name__ == "__main__":
    applePaperDIR: Path = Path.cwd() / "applePaper"

    for topicDIR in applePaperDIR.iterdir():
        tmp: str = "headline"
        for jsonPATH in topicDIR.glob(f"{tmp}*.json"):
            nameSTR: str = jsonPATH.name.replace(".json", "")
            contentSTR: str = json.load(open(jsonPATH, "r", encoding="utf-8"))

            aitlas = AItlas()
            KG = aitlas.scan(contentSTR)
            view = aitlas.aitlasViewPacker(directoryNameSTR=nameSTR)
            aitlas.view(directoryNameSTR=nameSTR)
