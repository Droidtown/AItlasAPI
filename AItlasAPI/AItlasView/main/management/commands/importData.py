import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from main.models import Event, NewsArticle, People, PeopleAttribute

actualDIR: Path = Path(__file__).resolve().parent


class Command(BaseCommand):
    help = "Import data from a directory!"
    def __init__(self):
        super().__init__()
        self.filePATH = None

    def add_arguments(self, parser):
        parser.add_argument(
            "directory", type=str, help="Something useful in the directory."
        )

    def importArticle(self):
        ## 讀文章資料
        try:
            articlePATH: Path = Path(self.filePATH) / "article.json"
            with open(articlePATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"讀取檔案錯誤: {e}"))
            return

        for item in data:
            content = item["content"].strip()  # 去除前後空白

            try:
                newsArticle, created = NewsArticle.objects.get_or_create(
                    content=content,
                    defaults={
                        "title": item.get("title", ""),
                    },
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"imported: {newsArticle}"))
                else:
                    self.stdout.write(self.style.WARNING(f"資料已存在: {newsArticle}"))

            except Exception as e:
                self.stderr.write(
                    self.style.WARNING(f'匯入失敗: {item.get("title", "")} - {e}')
                )
                continue

    def importPeople(self):
        try:
            PeoplePATH: Path = Path(self.filePATH) / "person.json"
            with open(PeoplePATH, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for person_name, attributes in data.items():
                # 建立 People 物件
                person = People.objects.create(name=person_name)

                for key, values in attributes.items():
                    # values 是 list
                    for v in values:
                        if v:  # 跳過空值
                            # engKey = FIELD_NAME_MAP.get(key, key)
                            PeopleAttribute.objects.create(
                                entityid=person,
                                type=key,
                                value=str(v)
                            )
                self.stdout.write(self.style.SUCCESS(f'Imported: {person}'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {str(e)}'))

    def importLocation(self):
        try:
            locationPATH: Path = Path(self.filePATH) / "location.json"
            with open(locationPATH, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for location_name, attributes in data.items():
                # 建立 Location 物件
                location = People.objects.create(name=location_name)
                print(location)

                for key, values in attributes.items():
                    # values 是 list
                    for v in values:
                        if v:  # 跳過空值
                            # engKey = FIELD_NAME_MAP.get(key, key)
                            PeopleAttribute.objects.create(
                                entityid=location,
                                type=key,
                                value=str(v)
                            )
                self.stdout.write(self.style.SUCCESS(f'Imported: {location}'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {str(e)}'))

    def handle(self, *args, **options):
        self.filePATH = options["directory"]
        self.importArticle()
        self.importPeople()