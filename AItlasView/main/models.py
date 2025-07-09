from django.db import models

# Create your models here.
class NewsArticle(models.Model):
    title = models.CharField(blank=True, max_length=255)  # 新聞標題
    content = models.TextField(unique=True)              # 新聞內容
    published_at = models.DateTimeField(blank=True, null=True)     # 發布時間
    url = models.URLField(blank=True, null=True)  # 原始新聞連結
    created_at = models.DateTimeField(auto_now_add=True)  # 新聞被存入系統的時間
    updated_at = models.DateTimeField(auto_now=True) #新聞在系統中被更新的時間
    result_segmentation = models.JSONField(blank=True, null=True)
    result_pos = models.JSONField(blank=True, null=True)
    result_obj = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.content

class Event(models.Model):
    entityid = models.ForeignKey(NewsArticle, on_delete=models.CASCADE, related_name='events') # 關聯到新聞
    source = models.CharField(max_length=20) # 主詞
    target = models.CharField(max_length=20) # 受詞
    label = models.CharField(max_length=30)  # 動詞
    encounter_time = models.DateTimeField(null=True, blank=True) # 事件發生時間
    metaData = models.CharField(max_length=100) # 原始資料
    url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.entityid.title} - {self.source}: {self.target}: {self.label}"

class People(models.Model):
    name = models.CharField(max_length=20)  # 人物名稱

    def __str__(self):
        return self.name

class NER(models.Model):
    name = models.CharField(max_length=20)  # NER 名稱

    def __str__(self):
        return self.name

class Place(models.Model):
    name = models.CharField(max_length=20)  # 地點名稱

    def __str__(self):
        return self.name

class PeopleAttribute(models.Model):
    entityid = models.ForeignKey(People, on_delete=models.CASCADE, related_name='attributes')  # 關聯到 People 模型
    type = models.CharField(max_length=10)  # 屬性類型
    value = models.CharField(max_length=15)  # 屬性值

    def __str__(self):
        return f"{self.entityid.name} - {self.type}: {self.value}"

class NERAttribute(models.Model):
    entityid = models.ForeignKey(NER, on_delete=models.CASCADE, related_name='attributes')  # 關聯到 People 模型
    type = models.CharField(max_length=10)  # 屬性類型
    value = models.CharField(max_length=15)  # 屬性值

    def __str__(self):
        return f"{self.entityid.name} - {self.type}: {self.value}"

class PlaceAttribute(models.Model):
    entityid = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='attributes')  # 關聯到 People 模型
    type = models.CharField(max_length=10)  # 屬性類型
    value = models.CharField(max_length=15)  # 屬性值

    def __str__(self):
        return f"{self.entityid.name} - {self.type}: {self.value}"