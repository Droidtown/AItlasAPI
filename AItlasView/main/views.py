import json
import logging
import re
from datetime import datetime
from pathlib import Path
from pprint import pprint
from typing import Any

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt

from .models import Event, NER, NERAttribute, NewsArticle, People, PeopleAttribute, Place, PlaceAttribute

logFORMAT = "%(name)s:%(funcName)s>>%(message)s"
logging.basicConfig(level=logging.INFO, format=logFORMAT)

@csrf_exempt
def clearData(request):
    if request.method == "POST":
        try:
            dataDICT = json.loads(request.body.decode("utf-8"))
            if "article" in dataDICT and dataDICT["article"]:
                status = _clearArticle()
            if "location" in dataDICT and dataDICT["location"]:
                status = _clearLocation()
            if "ner" in dataDICT and dataDICT["ner"]:
                status = _clearNER()
            if "people" in dataDICT and dataDICT["people"]:
                status = _clearPeople()

            return JsonResponse({"stauts": True, "msg": "Task completed."})

        except Exception as e:
            return JsonResponse({"status": False, "message": f"Invalid request data: {str(e)}"})

    return JsonResponse({"status": False, "msg": "Bad Request"})

def getArticleByIDs(request):
    # 解析 ids
    try:
        data = json.loads(request.body.decode("utf-8"))
        ids = data.get("ids", [])  # 這裡會是一個 list，例如 [3, 7, 15, 22]
        if not ids:
            return JsonResponse({"status": False, "message": "No IDs provided."})
    except Exception as e:
        return JsonResponse(
            {"status": False, "message": f"Invalid request data: {str(e)}"}
        )

    # 根據文章 id 獲得資料
    articles = NewsArticle.objects.filter(id__in=ids)

    # 根據各篇文章找出人名、地點、實體
    ## 組合所有文章內容
    allContent = " ".join(article.content for article in articles)

    # ==============================
    # === People 資料前處理 ===
    # ==============================
    ## 找出出現過的人
    mentionedPeople = People.objects.prefetch_related("attributes").filter(
        name__in=[
            person.name for person in People.objects.all() if person.name in allContent
        ]
    )
    ## 建立一個 {name: list of attribute_dict} 的總表，供每篇文章篩選用
    globalPeopleAttributeMap: dict[str, list[dict[str, list[str]]]] = {}

    for person in mentionedPeople:
        attr_dict: dict[str, list[str]] = {}
        for attr in person.attributes.all():
            attr_dict.setdefault(attr.type, []).append(attr.value)
        globalPeopleAttributeMap.setdefault(person.name, []).append(attr_dict)

    # ==============================
    # === Place 資料前處理 ===
    # ==============================
    mentionedPlaces = Place.objects.prefetch_related("attributes").filter(
        name__in=[
            place.name for place in Place.objects.all() if place.name in allContent
        ]
    )

    globalPlaceAttributeMap: dict[str, list[dict[str, list[str]]]] = {}
    for place in mentionedPlaces:
        attr_dict: dict[str, list[str]] = {}
        for attr in place.attributes.all():
            attr_dict.setdefault(attr.type, []).append(attr.value)
        globalPlaceAttributeMap.setdefault(place.name, []).append(attr_dict)

    # ==============================
    # === NER 資料前處理 ===
    # ==============================
    mentionedNers = NER.objects.prefetch_related("attributes").filter(
        name__in=[ner.name for ner in NER.objects.all() if ner.name in allContent]
    )

    globalNERAttributeMap: dict[str, list[dict[str, list[str]]]] = {}
    for ner in mentionedNers:
        attr_dict: dict[str, list[str]] = {}
        for attr in ner.attributes.all():
            attr_dict.setdefault(attr.type, []).append(attr.value)
        globalNERAttributeMap.setdefault(ner.name, []).append(attr_dict)

    resultLIST: list[dict] = []
    allPeopleSet: set = set()
    allNerSet: set = set()
    allPlaceSet: set = set()

    for article in articles:
        events = Event.objects.filter(entityid=article)
        # 針對每篇文章，只留下它實際提到的人、地點、實體
        peopleAttributeDICT: dict[str, list[dict]] = {
            name: attr_list
            for name, attr_list in globalPeopleAttributeMap.items()
            if name in article.content
        }

        placeAttributeDICT = {
            name: attr_list
            for name, attr_list in globalPlaceAttributeMap.items()
            if name in article.content
        }

        nersAttributeDICT = {
            name: attr_list
            for name, attr_list in globalNERAttributeMap.items()
            if name in article.content
        }

        highlightContent = _highlightArticles(
            article, peopleAttributeDICT, placeAttributeDICT, nersAttributeDICT
        )
        resultLIST.append(
            {
                "id": article.id,
                "title": article.title,
                "content": highlightContent,
                "published_at": article.published_at,
                "url": article.url,
                "events": [
                    {
                        "source": e.source,
                        "target": e.target,
                        "label": e.label,
                        "meta_data": e.metaData,
                        "encounter_time": e.encounter_time,
                        "date_only": _parse2Date(str(e.encounter_time)),
                        "url": e.url,
                    }
                    for e in events
                ],
                "peoples": peopleAttributeDICT,
                "places": placeAttributeDICT,
                "ners": nersAttributeDICT,
            }
        )
        allPeopleSet.update(peopleAttributeDICT.keys())
        allPlaceSet.update(placeAttributeDICT.keys())
        allNerSet.update(nersAttributeDICT.keys())

    # 用 JSON 格式回傳文章內容與事件
    return JsonResponse(
        {
            "status": True,
            "articles": resultLIST,
            "global_entities": {
                "peoples": list(allPeopleSet),
                "places": list(allPlaceSet),
                "ners": list(allNerSet),
            },
        }
    )

def homepage(request):
    articles = NewsArticle.objects.all()

    context = {
        "articles": articles,
    }
    return render(request, "index.html", context=context)

@csrf_exempt
def importData(request):
    if request.method == "POST":
        try:
            dataDICT = json.loads(request.body.decode("utf-8"))
            if "article" in dataDICT and dataDICT["article"]:
                status = _importArticle(dataDICT["article"])
            if "location" in dataDICT and dataDICT["location"]:
                status = _importLocation(dataDICT["location"])
            if "ner" in dataDICT and dataDICT["ner"]:
                status = _importNER(dataDICT["ner"])
            if "people" in dataDICT and dataDICT["people"]:
                status = _importPeople(dataDICT["people"])

            return JsonResponse({"stauts": True, "msg": "Task completed."})

        except Exception as e:
            return JsonResponse({"status": False, "message": f"Invalid request data: {str(e)}"})

    return JsonResponse({"status": False, "msg": "Bad Request"})

##############################################################################
def _clearArticle():
    try:
        NewsArticle.objects.all().delete()
        logging.info("[INFO] Delete NewsArticle successful.")
    except Exception as e:
        logging.error(f"[ERROR] Delete NewsArticle failed. => {str(e)}")

    return True

def _clearLocation():
    try:
        PlaceAttribute.objects.all().delete()
        logging.info("[INFO] Delete PlaceAttribute successful.")
    except Exception as e:
        logging.error(f"[ERROR] Delete PlaceAttribute failed. => {str(e)}")

    try:
        Place.objects.all().delete()
        logging.info("[INFO] Delete Place successful.")
    except Exception as e:
        logging.error(f"[ERROR] Delete Place failed. => {str(e)}")

    return True

def _clearNER():
    try:
        NERAttribute.objects.all().delete()
        logging.info("[INFO] Delete NERAttribute successful.")
    except Exception as e:
        logging.error(f"[ERROR] Delete NERAttribute failed. => {str(e)}")

    try:
        NER.objects.all().delete()
        logging.info("[INFO] Delete NER successful.")
    except Exception as e:
        logging.error(f"[ERROR] Delete NER failed. => {str(e)}")

    return True

def _clearPeople():
    try:
        PeopleAttribute.objects.all().delete()
        logging.info("[INFO] Delete PeopleAttribute successful.")
    except Exception as e:
        logging.error(f"[ERROR] Delete PeopleAttribute failed. => {str(e)}")

    try:
        People.objects.all().delete()
        logging.info("[INFO] Delete People successful.")
    except Exception as e:
        logging.error(f"[ERROR] Delete People failed. => {str(e)}")

    return True

def _highlightArticles(article, peopleDICT=None, placeDICT=None, nerDICT=None):
    """
    將文章中的人名、地名、NER hightlight 顯示
    """
    # 依照人名長度排序(長->短)
    peopleNames = sorted(peopleDICT.keys(), key=len, reverse=True)
    placeNames = sorted(placeDICT.keys(), key=len, reverse=True)
    nerNames = sorted(nerDICT.keys(), key=len, reverse=True)

    # 建立 regex pattern
    highlightedContent = article.content
    if peopleNames:
        peoplePattern = re.compile(r"(" + "|".join(map(re.escape, peopleNames)) + r")")
        highlightedContent = peoplePattern.sub(
            r'<span class="highlight_yellow">\1</span>', highlightedContent
        )
    if placeNames:
        placePattern = re.compile(r"(" + "|".join(map(re.escape, placeNames)) + r")")
        highlightedContent = placePattern.sub(
            r'<span class="highlight_pink">\1</span>', highlightedContent
        )
    if nerNames:
        nerPattern = re.compile(r"(" + "|".join(map(re.escape, nerNames)) + r")")
        highlightedContent = nerPattern.sub(
            r'<span class="highlight_blue">\1</span>', highlightedContent
        )

    return highlightedContent

def _importArticle(dataLIST):
    for d_d in dataLIST:
        content = d_d["content"].strip()  # 去除前後空白
        try:
            article, created = NewsArticle.objects.get_or_create(
                content=content,
                defaults={
                    "title": d_d.get("title", ""),
                },
            )
            if created:
                logging.info(f"[INFO] Create NewsArticle successful. => {article}")

        except Exception as e:
            logging.error(f"[ERROR] Create NewsArticle failed. => {item.get('title', '')}, {str(e)}")
            continue

    return True

def _importLocation(dataDICT):
    for place_s, place_d in dataDICT.items():
        # 建立 Place 物件
        place, created = Place.objects.get_or_create(name=place_s)
        if created:
            logging.info(f"[INFO] Create Place successful. => {place}")

        for k_s, v_l in place_d.items():
            for v_s in v_l:
                if v_s:
                    try:
                        placeAttribute, created = PlaceAttribute.objects.get_or_create(
                            entityid=place,
                            type=k_s,
                            value=str(v_s)
                        )
                        if created:
                            logging.info(f"[INFO] Create PlaceAttribute successful. => {place}, {k_s}, {v_s}")

                    except Exception as e:
                        logging.error(f"[ERROR] Create PlaceAttribute failed. => {place}, {k_s}, {v_s}, {str(e)}")
                        continue

    return True

def _importNER(dataDICT):
    for ner_s, ner_d in dataDICT.items():
        # 建立 NER 物件
        ner, created = NER.objects.get_or_create(name=ner_s)
        if created:
            logging.info(f"[INFO] Create NER successful. => {ner}")

        for k_s, v_l in ner_d.items():
            for v_s in v_l:
                if v_s:
                    try:
                        nerAttribute, created = NERAttribute.objects.get_or_create(
                            entityid=ner,
                            type=k_s,
                            value=str(v_s)
                        )
                        if created:
                            logging.info(f"[INFO] Create NERAttribute successful. => {ner}, {k_s}, {v_s}")

                    except Exception as e:
                        logging.error(f"[ERROR] Create NERAttribute failed. => {ner}, {k_s}, {v_s}, {str(e)}")
                        continue

    return True

def _importPeople(dataDICT):
    for person_s, person_d in dataDICT.items():
        # 建立 People 物件
        person, created = People.objects.get_or_create(name=person_s)
        if created:
            logging.info(f"[INFO] Create People successful. => {person}")

        for k_s, v_l in person_d.items():
            for v_s in v_l:
                if v_s:
                    try:
                        peopleAttribute, created = PeopleAttribute.objects.get_or_create(
                            entityid=person,
                            type=k_s,
                            value=str(v_s)
                        )
                        if created:
                            logging.info(f"[INFO] Create PeopleAttribute successful. => {person}, {k_s}, {v_s}")

                    except Exception as e:
                        logging.error(f"[ERROR] Create PeopleAttribute failed. => {person}, {k_s}, {v_s}, {str(e)}")
                        continue

    return True

def _parse2Date(isoSTR: str):
    dt = datetime.fromisoformat(isoSTR)
    return dt.strftime("%Y-%m-%d")