# Generated by Django 5.2 on 2025-06-05 07:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("main", "0008_event_encouner_time")]

    operations = [
        migrations.RenameField(
            model_name="event", old_name="encouner_time", new_name="encounter_time"
        )
    ]
