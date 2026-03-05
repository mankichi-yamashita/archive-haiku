from flask import Flask, render_template, request
import requests
import re
import MeCab

app = Flask(__name__)

# MeCab 初期化（unidic-lite使用）
tagger = MeCab.Tagger("-Ochasen")

# Wikipedia API
WIKI_API = "https://ja.wikipedia.org/w/api.php"

def get_wikipedia_text(keyword):
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "explaintext": True,
        "titles": keyword
    }
    res = requests.get(WIKI_API, params=params)
    data = res.json()
    pages = data["query"]["pages"]
    page = next(iter(pages.values()))
    return page.get("extract", "")

def count_on(text):
    node = tagger.parseToNode(text)
    count = 0
    while node:
        features = node.feature.split(",")
        if len(features) > 7:
            reading = features[7]
            if reading != "*":
                # 促音・拗音を1音としてカウント
                reading = re.sub(r"[ャュョャュョッ]", "ャ", reading)
                count += len(reading)
        node = node.next
    return count

def is_575(line):
    parts = re.split("[、。！？\n]", line)
    for p in parts:
        if len(p.strip()) > 0:
            if count_on(p.strip()) == 17:
                return p.strip()
    return None

def haiku_score(text):
    # 単純な俳句らしさスコア
    kigo_words = ["春", "夏", "秋", "冬", "雪", "月", "花", "風"]
    score = 0
    for k in kigo_words:
        if k in text:
            score += 20
    score += min(len(text), 17)
    return min(score, 100)

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    keyword = ""
    if request.method == "POST":
        keyword = request.form["keyword"]
        text = get_wikipedia_text(keyword)
        lines = text.split("\n")
        for line in lines:
            h = is_575(line)
            if h:
                results.append({
                    "text": h,
                    "score": haiku_score(h)
                })
    return render_template("index.html", results=results, keyword=keyword)

if __name__ == "__main__":
    app.run()