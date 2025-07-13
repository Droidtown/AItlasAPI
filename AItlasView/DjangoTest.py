from pathlib import Path
from pprint import pprint

from django.utils import encoding
from requests import post
import json

BASE_PATH = Path(__file__).parent
SERVER_URL = "http://127.0.0.1:8000"

def clearData(article=False, location=False, ner=False, people=False):
    response = post(f"{SERVER_URL}/clearData/", json={
        "article": article,
        "location": location,
        "ner": ner,
        "people": people
    })
    if response.status_code == 200:
        try:
            return response.json()
        except:
            return {"status": False, "msg": f"Parse clearData json failed => {response.text}"}
    else:
        return {"status": False, "msg": f"Request clearData failed => {response.status_code}"}

def importData(article=[], location={}, ner={}, people={}, event=[]):
    response = post(f"{SERVER_URL}/importData/", json={
        "article": article,
        "location": location,
        "ner": ner,
        "people": people,
        "event":  event,
    })
    if response.status_code == 200:
        try:
            return response.json()
        except:
            return {"status": False, "msg": f"Parse importData json failed => {response.text}"}
    else:
        return {"status": False, "msg": f"Request importData failed => {response.status_code}"}

if __name__ == "__main__":
    ## Clear data
    # clearData(article,location, ner, people)
    #status = clearData(True, True, True, True)
    #print("[clearData]")
    #pprint(status)

    ## Import data
    dataPATH = BASE_PATH / "rawData/example"
    dataDICT = {}
    try:
        dataDICT["article"] = json.load(open(dataPATH / "article.json", encoding="utf-8"))
    except:
        dataDICT["article"] = []
    try:
        dataDICT["location"] = json.load(open(dataPATH / "knowledge_plcae.json", encoding="utf-8"))
    except:
        dataDICT["location"] = {}
    try:
        dataDICT["ner"] = json.load(open(dataPATH / "knowledge_NER.json", encoding="utf-8"))
    except:
        dataDICT["ner"] = {}
    try:
        dataDICT["people"] = json.load(open(dataPATH / "knowledge_people.json", encoding="utf-8"))
    except:
        dataDICT["people"] = {}
    try:
        dataDICT["entity"] = json.load(open(BASE_PATH/"rawData/event.json", encoding="utf-8"))
    except:
        dataDICT["entity"] = {}

    #pprint(dataDICT)

    status = importData(dataDICT["article"], dataDICT["location"], dataDICT["ner"], dataDICT["people"])
    print("[importData]")
    pprint(status)