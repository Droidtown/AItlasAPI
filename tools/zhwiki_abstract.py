import os
import re
import shutil

data_folder = "../data/zhwiki_abstract_2306"
output_folder = "../data/zhwiki_abstract_1607"

# 檢查目標資料夾是否存在，如果不存在就創建它
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 正則表達式，匹配包含1個中文字但不包含英文及數字的資料夾名稱
pattern = re.compile(r"^[^\u4e00-\u9fa5]*[\u4e00-\u9fa5][^\w\d]*$")

# 遍歷資料夾下的所有檔案夾
for folder in os.listdir(data_folder):
    folder_path = os.path.join(data_folder, folder)
    if os.path.isdir(folder_path):
        # 檢查檔案夾名稱是否符合條件
        if re.match(pattern, folder):
            # 將符合條件的檔案夾移動到指定資料夾
            destination_path = os.path.join(output_folder, folder)
            shutil.move(folder_path, destination_path)
            print(f"檔案夾 {folder} 已成功移動到 {destination_path} 資料夾。")
            
print(len(os.listdir(output_folder)))
