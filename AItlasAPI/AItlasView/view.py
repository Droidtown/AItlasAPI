import os
from pathlib import Path
from pprint import pprint



def view(
    articleFileName: str = "article.json",
    kgPeopleFileName: str = "knowledge_people.json",
    kgNerFileName: str = "knowledge_NER.json",
    kgPlaceFileName: str = "knowledge_place.json"
):
    djangoDIR: Path = Path(__file__).parent
    articlePATH: Path = djangoDIR / "rawData" / articleFileName
    kgPeoplePATH: Path = djangoDIR / "rawData" / kgPeopleFileName
    kgNerPATH: Path = djangoDIR / "rawData" / kgNerFileName
    kgPlacePATH: Path = djangoDIR / "rawData" / kgPlaceFileName
    sqlPATH: Path = djangoDIR / "db.sqlite3"


    # 設定 django 環境
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aitlasDEMO.settings")

    import django

    django.setup()

    from django.core.management import call_command

    # 刪除舊資料
    if sqlPATH.exists():
        sqlPATH.unlink()
        pprint("刪除舊資料庫")

    # 建立新空白資料庫
    call_command("migrate")
    pprint("已建立新資料庫")

    # 匯入資料
    call_command("import_news", str(articlePATH))
    pprint("已匯入所需「文章」資料")

    call_command("import_people", str(kgPeoplePATH))
    pprint("已匯入所需「人物」資料")

    call_command("import_place", str(kgPlacePATH))
    pprint("已匯入所需「地點」資料")

    call_command("import_NER", str(kgNerPATH))
    pprint("已匯入所需「實體」資料")

    # 啟動伺服器
    pprint("🚀 啟動 Django Server")
    call_command("runserver", "127.0.0.1:8000")

if __name__ == "__main__":
    view()