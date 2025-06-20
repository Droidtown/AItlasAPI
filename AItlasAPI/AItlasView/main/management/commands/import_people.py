import json
from django.core.management.base import BaseCommand
from main.models import People, PeopleAttribute


class Command(BaseCommand):
    help = "Import people data from a JSON file"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the JSON file.')

    def handle(self, *args, **options):
        file_path = options['file_path']

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
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

    def parse_date(self, raw_date):
        from datetime import datetime
        if not raw_date:
            return None
        try:
            return datetime.strptime(raw_date, "%Y年%m月%d日").date()
        except ValueError:
            return None
