from flask import Flask, render_template, request
import requests
import urllib.parse
import MeCab

app = Flask(__name__)

# MeCab 初期化
tagger = MeCab.Tagger()

# Wikipediaから文章取得
def get_wikipedia_text(keyword):

    keyword_encoded = urllib.parse.quote(keyword)
    url = f"https://ja.wikipedia.org/api/rest_v1/page/summary/{keyword_encoded}"

    try:
        res = requests.get(url, timeout=10)

        if res.status_code != 200:
            return ""

        data = res.json()

        if "extract" in data:
            return data["extract"]

        return ""

    except Exception as e:
        print("Wikipedia API error:", e)
        return ""


# 俳句っぽく整形
def make_haiku(text):

    words = []

    node = tagger.parseToNode(text)

    while node:
        surface = node.surface
        if surface:
            words.append(surface)
        node = node.next

    if len(words) < 5:
        return []

    results = []

    for i in range(min(5, len(words) - 4)):
        haiku = "".join(words[i:i+5])
        results.append(haiku)

    return results


@app.route("/", methods=["GET", "POST"])
def index():

    results = []
    keyword = ""
    error = ""

    if request.method == "POST":

        keyword = request.form.get("keyword")

        text = get_wikipedia_text(keyword)

        if not text:
            error = "Wikipediaの記事が取得できませんでした"
        else:
            results = make_haiku(text)

    return render_template(
        "index.html",
        results=results,
        keyword=keyword,
        error=error
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
```
