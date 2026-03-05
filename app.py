from flask import Flask, render_template, request
import requests
import urllib.parse
from janome.tokenizer import Tokenizer
import random

app = Flask(__name__)

tokenizer = Tokenizer()

########################################
# カタカナ → ひらがな
########################################

def kata_to_hira(text):

    result = ""

    for c in text:
        code = ord(c)

        if 0x30A1 <= code <= 0x30F6:
            result += chr(code - 0x60)
        else:
            result += c

    return result


########################################
# モーラ数カウント
########################################

def mora_count(reading):

    if reading == "*":
        return 0

    reading = kata_to_hira(reading)

    return len(reading)


########################################
# Wikipedia取得
########################################

def get_wikipedia_text(keyword):

    keyword_encoded = urllib.parse.quote(keyword)

    url = f"https://ja.wikipedia.org/api/rest_v1/page/summary/{keyword_encoded}"

    try:

        res = requests.get(url, timeout=10)

        if res.status_code != 200:
            return ""

        data = res.json()

        if "extract" in data:

            # メモリ節約
            return data["extract"][:1200]

        return ""

    except Exception as e:

        print("Wikipedia error:", e)
        return ""


########################################
# 俳句生成
########################################

def generate_haiku(text):

    tokens = tokenizer.tokenize(text)

    readings = []
    surfaces = []

    for t in tokens:

        r = t.reading

        if r == "*":
            r = t.surface

        readings.append(r)
        surfaces.append(t.surface)

    results = []

    for start in range(len(readings)):

        mora = 0
        phrase = []
        parts = []
        target = [5,7,5]
        index = 0

        for i in range(start,len(readings)):

            m = mora_count(readings[i])

            if m == 0:
                break

            mora += m
            phrase.append(surfaces[i])

            if mora == target[index]:

                parts.append("".join(phrase))

                phrase = []
                mora = 0
                index += 1

                if index == 3:

                    haiku = "\n".join(parts)

                    results.append(haiku)

                    break

            elif mora > target[index]:
                break

    # 重複削除
    results = list(set(results))

    # ランダム順
    random.shuffle(results)

    return results[:10]


########################################
# スコア生成
########################################

def score_haiku():

    return random.randint(70,98)


########################################
# ルート
########################################

@app.route("/", methods=["GET","POST"])

def index():

    keyword = ""
    results = []
    scores = []
    error = ""

    if request.method == "POST":

        keyword = request.form.get("keyword")

        text = get_wikipedia_text(keyword)

        if not text:

            error = "Wikipedia記事が取得できません"

        else:

            results = generate_haiku(text)

            scores = [score_haiku() for _ in results]

            if not results:
                error = "俳句が見つかりませんでした"

    return render_template(

        "index.html",
        keyword=keyword,
        results=zip(results,scores),
        error=error

    )


########################################
# 実行
########################################

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=10000)