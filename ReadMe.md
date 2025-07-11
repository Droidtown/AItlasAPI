# AItlas

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
│   └── AItlasView         #內含 django 專案，呈現 AItlas 的可能性
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

## 3. Usage

a. 先到`AItlasAPI/AItlasAPI/AItlasView`執行`python3 manage.py runserver`後直到出現

> Django version 3+都可以

```md
Django version 5.2.4, using settings 'aitlasDEMO.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

b. 打開`AItlasAPI.py`，在程式進入點能夠看到使用範例如下方，可以直接執行。
c. 在`http://127.0.0.1:8000/`觀察結果

```python
if __name__ == "__main__":
    longText = """中東夙敵以色列和伊朗空戰進入第8天。以色列總理尼坦雅胡今天矢言「消除」伊朗構成的核子和彈道飛彈威脅。法新社報導，尼坦雅胡（Benjamin Netanyahu）在南部城巿俾什巴（Beersheba）告訴記者：「我們致力於信守摧毀核威脅的承諾、針對以色列的核滅絕威脅。」伊朗今天的飛彈攻勢擊中當地一間醫院。"""
    aitlas = AItlas()
    topicSTR: str = "中東"
    KG = aitlas.scan(longText)

    view = aitlas.aitlasViewPacker(directoryNameSTR=topicSTR)
    aitlas.view(directoryNameSTR=topicSTR)
```

### scan
- input：inputSTR
  - 要做 AItlas 分析的文字
- output：生成 self.AITLASKG

### aitlasViewPacker
- input：self
- output：生成 django 專案呈現所需的檔案

### view
- 對 django 寫入須呈現的資料

