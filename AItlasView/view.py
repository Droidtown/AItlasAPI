import os
import sys
from pathlib import Path
from pprint import pprint

def view(directoryNameSTR: str):
    djangoDIR: Path = Path(__file__).parent
    kgPATH: Path = djangoDIR / "rawData" / directoryNameSTR / "data"
    sqlPATH: Path = djangoDIR / "db.sqlite3"


    #設定 django 環境
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
    call_command("importData", str(kgPATH))

    # 啟動伺服器
    call_command("runserver", "127.0.0.1:8000")
    pprint("🚀 啟動 Django Server 成功")

if __name__ == "__main__":
    view("柯父辭世")