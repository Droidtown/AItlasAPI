from django.contrib import admin
from .models import NewsArticle, People, PeopleAttribute, NER, NERAttribute, Place, PlaceAttribute, Event

# Register your models here.
admin.site.register(NewsArticle)
admin.site.register(People)
admin.site.register(PeopleAttribute)
admin.site.register(NER)
admin.site.register(NERAttribute)
admin.site.register(Place)
admin.site.register(PlaceAttribute)
admin.site.register(Event)