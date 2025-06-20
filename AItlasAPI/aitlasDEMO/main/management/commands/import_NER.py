import json
from django.core.management.base import BaseCommand
from main.models import NER, NERAttribute

class Command(BaseCommand):
    help = "Import NER data from a JSON file"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the JSON file.')

    def handle(self, *args, **options):
        file_path = options['file_path']

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for NER_name, attributes in data.items():
                # 建立 NER 物件
                Ner = NER.objects.create(name=NER_name)

                for key, values in attributes.items():
                    # values 是 list
                    for v in values:
                        if v:  # 跳過空值
                            NERAttribute.objects.create(
                                entityid=Ner,
                                type=key,
                                value=str(v)
                            )
                self.stdout.write(self.style.SUCCESS(f'Imported: {Ner}'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error: {str(e)}'))
