from flask import Flask, render_template, request
import requests
import re

app = Flask(__name__)

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

# ひらがなカタカナを抽出
def to_kana(text):
    return re.sub(r"[^ぁ-んァ-ンー]", "", text)

# 促音・拗音を1音として処理
def count_on(text):
    text = to_kana(text)
    text = re.sub(r"[ャュョ]", "ャ", text)
    text = re.sub(r"ッ", "ツ", text)
    return len(text)

def is_575(line):
    parts = re.split("[、。！？\n]", line)
    for p in parts:
        p = p.strip()
        if count_on(p) == 17:
            return p
    return None

def haiku_score(text):
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