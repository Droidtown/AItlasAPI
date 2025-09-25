# AItlas

## Usage

### 設定檔
請參考 [LiteLLM](https://docs.litellm.ai/docs/providers) 後，建立`./account.info`，並在檔案內填寫下列設定檔：

```json
{
    "url":"",                                    # 請填入 articut url（線上版 articut 可留空）
    "username":"",                               # 請填入您在卓騰語言科技使用的登入信箱
    "api_key": "",                               # 請填入您登入卓騰語言科技後所顯示的 API 金鑰（ Docker 版可留空）
    "llm": {
        "model": "",                             # 請務必按照 LiteLLM 格式，填入您在 AItlasAPI 中要使用的語言模型及下列設定。
        "api_base": "",
        "env": {                                 # 請務必按照 LiteLLM 格式，填入環境變數。
            "OPENAI_API_KEY": "",
            "AZURE_API_KEY": "",
            "AZURE_API_BASE": "",
            "AZURE_API_VERSION": "",
            "ANTHROPIC_API_KEY": "",
            "GEMINI_API_KEY": ""
        }
    }
}
```

以`gpt-5`為範例：

```json
{
    "url":"http://10.1.1.123:45678",
    "username":"test@gmail.com",                               
    "api_key": "",                               
    "llm": {
        "model": "gpt-5",
        "api_base": "",
        "env": {
            "OPENAI_API_KEY": "myApiKey123",
            "AZURE_API_KEY": "",
            "AZURE_API_BASE": "",
            "AZURE_API_VERSION": "",
            "ANTHROPIC_API_KEY": "",
            "GEMINI_API_KEY": ""
        }
    }
}
```

### 使用 AItlas （可參考 test.py ）
```py
# 文章根據
articleDICT: dict[str, str] = {
    "1140516": "（中央社記者劉世怡台北11日電）北院審理京華城案裁定柯文哲、應曉薇自2日起延長羈押禁見2個月。2人不服提起抗告，高院今天認定原裁定並無違法或不當，駁回抗告，即延長羈押禁見2個月確定。台灣高等法院指出，柯文哲、應曉薇前經原審法院裁定羈押禁見，因期間將屆，經原審台北地院法院訊問後，認定2人犯罪嫌疑重大，且原羈押原因及必要依然存在，因此裁定延長羈押2個月並禁止接見、通信。高院表示，柯文哲、應曉薇抗告主張犯嫌並非重大、無逃亡之虞、無勾串之虞、無羈押必要、原裁定理由不備、身體有恙非保外就醫難以痊癒，請求撤銷原裁定。高院合議庭表示，依卷內事證及向原審法院、看守所函調相關資料，認定2人主張均不足採信，因此認定本件抗告為無理由，予以駁回。本件延長羈押確定。台北地檢署偵辦京華城案、柯文哲政治獻金案，去年底依貪污治罪條例違背職務收受賄賂、圖利、公益侵占與背信等罪起訴前台北市長柯文哲、威京集團主席沈慶京、國民黨台北市議員應曉薇、前台北市長辦公室主任李文宗等11人，具體求處柯文哲總計28年6月徒刑。全案移審後，北院2度裁定在押的柯文哲、沈慶京、應曉薇與李文宗交保，經北檢抗告，高院2度發回更裁，北院1月2日裁定柯文哲、沈慶京、應曉薇、李文宗等4人裁定羈押禁見3個月。北院隨後裁定柯文哲、沈慶京、應曉薇與李文宗等4人，自4月2日、同年6月2日起分別延長羈押2月。北院7月21日裁定柯文哲、應曉薇均自8月2日起延長羈押2月，並禁止接見、通信。李文宗則獲裁定2000萬元交保，限制住居、限制出境出海及配戴電子腳鐶。李男7月23日辦保及配戴電子腳鐶完成，離開法院。此外，沈慶京獲裁定1億8000萬元交保並限制住居、限制出境出海及配戴電子腳環及個案手機。沈慶京7月24日下午繳交保證金，晚間配戴電子腳環及個案手機後，離開法院。（編輯：蕭博文）1140811"
}

#生成檔案檔名
topicSTR: str = "京華城"  

# 初始化 aitlas
aitlas = AItlas(username=G_accountDICT["username"], apikey=G_accountDICT["api_key"], url=G_accountDICT["url"], llm=G_accountDICT["llm"])

# 移除所有換行符號提昇效率
for time_s, article_s in articleDICT.items():
    KG = aitlas.scan(inputSTR=article_s.replace("\n", ""), timeRefSTR=time_s)
    # pprint(KG)

view = aitlas.aitlasViewPacker(directoryNameSTR=topicSTR)
aitlas.view(directoryNameSTR=topicSTR)
```

1. scan
    - input：inputSTR
    - 要做 AItlas 分析的文字
    - output：生成 self.AITLASKG

2. aitlasViewPacker
    - input：生成的檔名
    - output：生成相關資料結構

3. view
    - 將資料寫成 js 和 html 以便視覺化查看
    - input：生成的檔名
    - output：生成相關資料結構


## Overview
AItlas is a knowledge graph designed to go with Loki NLU system.

一言以蔽之，AItlas 是一個基於 Loki NLU 系統所設計的知識圖譜。

知識圖譜指的是一種結構化的資訊儲存方式，特點在於呈現實體 (Entity) 之 間的關係。比如：

1.  上下關係：

- 狗 -> 犬科
- 水 -> 液體

2. 交集關係：

- 水果 <- 蕃茄 -> 蔬菜
- 人類 <- 公司負責人 -> 職位
  …等等

以往知識圖譜往往由領域專家編寫，但隨著領域知識迅速發展，相較之下用人力編寫的知識圖譜進展緩慢。為改善此問題，Wikipedia 和 Wikidata 等由熱心群眾編寫的開放百科全書雖然進展較快，但其本質上仍為人力編寫，遇上具爭議性的問題或是缺乏領域專家的議題、無法公開予大眾的組織內部知識…等等情況時，仍是束手無策。

此外，傳統的語料庫語言學技術藉由標記與統計方法一路發展至近年的資料模型方法，卻往往在資料量不足以致於 P 值不顯著的邊界問題上難以突破。大型語言模型 (LLM, Large Language Models) 如 ChatGPT、Bard... 等，也會遇上加添新的知識資料時，新資料量遠不如舊資料量的不平衡議題，以及訓練新模型的資源需求難以負擔的瓶頸。

主流的改善的方法雖然有微調 (fine-tuning) 和提示工程 (prompt engineering)，但前者會使模型的表現能力從通用趨向專一化，而後者則受限於提示長度和 LLM 的短期記憶限制以及推理表現不佳的問題，無法妥善解決知識圖譜的需求問題。

顯然，在領域專家有限、資料內容不平衡、對知識圖譜的推理能力…等現實問題下，我們需要從底層重新發展「知識圖譜的構建方法」。

透過基於語言學的 NLU/NLP 技術，AItlas 使用和前述方法完全不同的知識圖建構方法。

其運作原理是「自然語言中有許多互呈一致關係 (agreement) 的元素」，例如英文的 "He" 為第三人稱單數，則以其為主語的第一個動詞後會出現 -s 的一致關係詞綴。又如，動詞往往會限定能夠做出這個動作的主詞，具有一定的特性。例如「X 任教於大學」「Y 座落於北台灣」。即便我們不知道 X 是什麼，也不知道 Y 是什麼，但我們仍然得出「X 應該是人類，而 Y 應該是一個建築或是地點…等佔有空間的實體」。

甚至，任何懂中文的人類只要聽到「我到酒吧點了一杯歐洽塔」，即便不知道什麼是「歐洽塔」，也能藉由「到 \_X\_」的詞組結構推測「酒吧」很可能是個地點，藉由「點了一杯 \_Y\_」的動詞組及名詞組結構推測「歐洽塔」很可能是一種飲料。

AItlas 即透過 Articut/Loki 進行語言結構上的自動分類與產生句型模型的能力，構建起一套「可載入任何文本，對其內容進行分析以產生該文本知識圖譜」的資訊系統。

更棒的是，藉由 Loki 全通透的架構特性，設計者可輕易透過 Python 程式語言調整自己所需的運算邏輯以便應用於不同場景。

## 1. Methodology

### 1.1 Wiki Person

#### 1.1.1 zhwiki_abstract_2306/

將 [維基百科](https://www.wikipedia.org/) 中所有中文條目文本的「序言」(Abstract) (待修正) 分別取出以下方 .json 的格式存放在 zhwiki_abstract_2306 目錄中。

```txt
克律塞伊斯
克律塞伊斯（古希臘語：Χρυσηΐς）。[1]古希臘神話人物之一。其事跡見於《伊里亞特》。為特洛伊阿波羅祭司克律塞斯之女，為阿伽門農所俘。後者沉迷於其美貌而拒絕其父贖回，遂遭太陽神降瘟疫於希臘聯軍，使之迫於壓力而派奧德修斯將其送回。一說她與阿伽門農結合，生下一子。其形象於相關藝術作品中得到廣泛反映。
```

```json
{
  "id": "克律塞伊斯",
  "text2": "克律塞伊斯。克律塞伊斯（古希臘語：Χρυσηΐς）。[1]古希臘神話人物之一。其事跡見於《伊里亞特》。為特洛伊阿波羅祭司克律塞斯之女，為阿伽門農所俘。後者沉迷於其美貌而拒絕其父贖回，遂遭太陽神降瘟疫於希臘聯軍，使之迫於壓力而派奧德修斯將其送回。一說她與阿伽門農結合，生下一子。其形象於相關藝術作品中得到廣泛反映。"
}
```

#### 1.1.2 person_classifier.py

從 zhwiki_abstract_2306 下的所有文本中，以正規表示式 (regular expression) 依人名在句中常見的結構 (待修正)，篩選出與「人物」相關的文本存放在 data/people 中。

```python
personPatLIST = ["^{}\s?（[^名又a-zA-Z]+）",
                 "^{}\s?\([^名又a-zA-Z]+\)",
                 "^{}\s?（[^名又a-zA-Z]*）",
                 "^{}，[^a-zA-Z]+人\b",
                 "^{}，[^a-zA-Z]+人(?=[，。])"
                ]
```

#### 1.1.3 utterance_insert.py

讀取 data/people 中的 .json 檔案，抽取文本中出現的所有動詞，依動詞將句子分類後，將含有標的動詞的句子批次送上 [Loki](https://api.droidtown.co/document/#Loki) (Linguisitcs-Oriented Keyword Interface)，根據 Loki 的運作原理，project 為 Wiki People，intent 為標的動詞，utterance 為動詞後的實詞數量，此時 Loki 專案中的 .ref 檔案應為以下 .json 格式。

```json
{
    "pinyin":"",                      # 標的動詞漢語拼音
    "0e":["utterance1","utterance2"], # 動詞後含有零個實詞的句子
    "1e":["utterance1","utterance2"]  # 動詞後含有一個實詞的句子
}
```

#### 1.1.4 pro_drop.py (待修正)

考慮到漢語中 pro-drop 現象頻繁在文本中出現的因素，將 data/people 中所有條目標題人物充當主詞填回序言中每個句子的句首位置。

```json
{
  "id": "克律塞伊斯",
  "text2": "克律塞伊斯。_克律塞伊斯_古希臘神話人物之一。克律塞伊斯事蹟見於《伊里亞特》。_克律塞伊斯_爲特洛伊阿波羅祭司克律塞斯之女，_克律塞伊斯_爲阿伽門農所俘。_克律塞伊斯_後者沉迷於其美貌而拒絕其父贖回，_克律塞伊斯_遂遭太陽神降瘟疫於希臘聯軍，克律塞伊斯使之迫於壓力而派奧德修斯將其送回。_克律塞伊斯_一說她與阿伽門農結合，克律塞伊斯生下一子。克律塞伊斯形象於相關藝術作品中得到廣泛反映"
}
```

## 2. Contents

```python
├── LICENSE
├── README.md
├── AItlasAPI
│   ├── AItlasAPI.py
│   └── AItlasView         
│   └── AItlas_TW          #內含各種 AItlas 所需 source data
│   └── AItlas
├── data
│   ├── preprocessed
│   │   ├── stage01_lines  #原始資料裡拆出來的 lines
│   │   └── stage01_text   #原始資料裡拆出來的 text
│   └── wiki-pages         #原始資料
└── tools
    ├── titleJointer.py    #拆出原始資料的工具
    ├── extract.py (script to extract wikipedia title and summary from topic.txt
    └── topic.txt (txt file containing wikipedia article names)
```
