import json

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from main.models import Event, NewsArticle


class Command(BaseCommand):
    help = "Import news articles from a JSON file"

    def add_arguments(self, parser):
        parser.add_argument("json_file", type=str)

    def handle(self, *args, **options):
        file_path = options["json_file"]

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"讀取檔案錯誤: {e}"))
            return

        count = 0
        for item in data:
            published_at = parse_datetime(item["published_at"])
            if published_at is not None and timezone.is_naive(published_at):
                published_at = make_aware(published_at)

            newsArticle = NewsArticle()
            try:
                newsArticle = NewsArticle.objects.create(
                    title=item["title"],
                    content=item["content"],
                    published_at=published_at,
                    url=item.get("url"),
                    result_segmentation=item["articut_content"]["result_segmentation"],
                    result_obj=item["articut_content"]["result_obj"],
                    result_pos=item["articut_content"]["result_pos"],
                )
                self.stdout.write(self.style.SUCCESS(f"imported: {newsArticle}"))

            except IntegrityError:
                try:
                    newsArticle = NewsArticle.objects.get(
                        title=item["title"],
                        content=item["content"],
                        published_at=published_at,
                    )
                    print("資料重複，改用已存在資料")
                except NewsArticle.DoesNotExist:
                    self.stderr.write(
                        self.style.WARNING(f'資料重複但找不到原始資料: {item["title"]}')
                    )
                    continue  # 無法處理就跳過
            except Exception as e:
                self.stderr.write(
                    self.style.WARNING(f'匯入失敗: {item["title"]} - {e}')
                )
                continue

            count += 1

            for event_d in item.get("event", []):
                encounter_time_at = parse_datetime(event_d["encounter_time"])
                if encounter_time_at is not None and timezone.is_naive(
                    encounter_time_at
                ):
                    encounter_time_at = make_aware(encounter_time_at)

                try:
                    event = Event.objects.create(
                        entityid=newsArticle,
                        url=item["url"],
                        source=event_d["source"],
                        target=event_d["target"],
                        label=event_d["label"],
                        metaData=event_d["metaData"],
                        encounter_time=encounter_time_at,
                    )
                    self.stdout.write(self.style.SUCCESS(f"imported: {event}"))
                except Exception as e:
                    self.stderr.write(self.style.WARNING(f"匯入失敗:{event_d}: {e}"))
