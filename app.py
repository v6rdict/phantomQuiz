"""
Which Constellation Are You? — a small Flask personality quiz.

Run locally:
    pip install -r requirements.txt
    python app.py
Then open http://127.0.0.1:5000 in a browser, or generate a QR code
with generate_qr.py once you've deployed it publicly.
"""
from flask import Flask, request, session, redirect, url_for, render_template_string
import random

app = Flask(__name__)
app.secret_key = "replace-this-with-a-real-secret-key"  # needed for session cookies

# ---------------------------------------------------------------------------
# Quiz content — edit this section to make it your own quiz.
# Each option maps to a constellation "code". Whichever code the person picks
# most often determines their result.
# ---------------------------------------------------------------------------
QUESTIONS = [
    {
        "prompt": "A plan falls apart the morning it's supposed to happen. You:",
        "options": [
            ("Charge ahead with a new plan on the spot", "orion"),
            ("Get everyone together to figure it out as a group", "ursa"),
            ("Quietly rework the timeline until it fits", "draco"),
            ("Turn it into a story worth telling later", "cass"),
        ],
    },
    {
        "prompt": "Your ideal weekend involves:",
        "options": [
            ("Something physical — a hike, a match, a project with your hands", "orion"),
            ("A small gathering with people you trust", "ursa"),
            ("Deep focus on something intricate, alone", "draco"),
            ("Being seen somewhere fun, dressed for it", "cass"),
        ],
    },
    {
        "prompt": "People come to you for:",
        "options": [
            ("A push to actually go do the thing", "orion"),
            ("Comfort and steady support", "ursa"),
            ("A well-thought-out plan", "draco"),
            ("Energy and a good time", "cass"),
        ],
    },
    {
        "prompt": "Your biggest strength is probably:",
        "options": [
            ("Courage", "orion"),
            ("Loyalty", "ursa"),
            ("Patience", "draco"),
            ("Confidence", "cass"),
        ],
    },
    {
        "prompt": "A rival outshines you at something. Your first instinct:",
        "options": [
            ("Compete harder, immediately", "orion"),
            ("Check in on how everyone's feeling about it", "ursa"),
            ("Study exactly how they did it", "draco"),
            ("Shrug it off and make your own moment", "cass"),
        ],
    },
]

RESULTS = {
    "orion": {
        "name": "Orion",
        "title": "The Hunter",
        "blurb": (
            "You move first and think while moving. Orion is the constellation "
            "everyone can find in the sky because it doesn't hide — and neither "
            "do you. You're at your best when there's something to chase."
        ),
    },
    "ursa": {
        "name": "Ursa Major",
        "title": "The Guardian",
        "blurb": (
            "The Great Bear stays visible all year, a fixed point people navigate "
            "by. You're the steady one — dependable, protective, the friend who "
            "shows up without being asked."
        ),
    },
    "draco": {
        "name": "Draco",
        "title": "The Strategist",
        "blurb": (
            "Draco coils quietly around the pole star, patient and precise. You "
            "think several moves ahead and rarely act until you're sure — which "
            "is exactly why it usually works."
        ),
    },
    "cass": {
        "name": "Cassiopeia",
        "title": "The Radiant",
        "blurb": (
            "Cassiopeia is bright, unmistakable, a little vain — in the best way. "
            "You bring energy into every room you enter and you're not sorry "
            "about it."
        ),
    },
}

BASE_CSS = """
:root {
    --bg: #0b1224;
    --bg-soft: #121a33;
    --line: #253158;
    --gold: #e8b95c;
    --text: #eef1fb;
    --text-dim: #9aa3c7;
}
* { box-sizing: border-box; }
body {
    margin: 0;
    min-height: 100vh;
    background: radial-gradient(ellipse at top, #16204a 0%, var(--bg) 60%);
    color: var(--text);
    font-family: 'Georgia', 'Iowan Old Style', serif;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
}
.card {
    width: 100%;
    max-width: 560px;
    background: var(--bg-soft);
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 40px 36px;
    position: relative;
    overflow: hidden;
}
.card::before {
    content: "";
    position: absolute;
    inset: 0;
    background-image:
        radial-gradient(1px 1px at 20px 30px, #ffffff55 0%, transparent 60%),
        radial-gradient(1px 1px at 120px 80px, #ffffff33 0%, transparent 60%),
        radial-gradient(1.5px 1.5px at 200px 20px, #ffffff44 0%, transparent 60%),
        radial-gradient(1px 1px at 300px 120px, #ffffff33 0%, transparent 60%),
        radial-gradient(1px 1px at 40px 160px, #ffffff44 0%, transparent 60%),
        radial-gradient(1.5px 1.5px at 420px 60px, #ffffff33 0%, transparent 60%);
    pointer-events: none;
}
.eyebrow {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    font-size: 12px;
    color: var(--gold);
    margin: 0 0 10px 0;
}
h1 {
    font-size: 28px;
    line-height: 1.3;
    margin: 0 0 6px 0;
}
p.sub {
    color: var(--text-dim);
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 14px;
    margin: 0 0 28px 0;
}
.progress {
    display: flex;
    gap: 8px;
    margin-bottom: 28px;
}
.dot {
    height: 6px;
    flex: 1;
    border-radius: 3px;
    background: var(--line);
}
.dot.filled { background: var(--gold); }
form { display: flex; flex-direction: column; gap: 12px; }
button.option {
    text-align: left;
    background: #0e1630;
    border: 1px solid var(--line);
    color: var(--text);
    padding: 16px 18px;
    border-radius: 12px;
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 15px;
    cursor: pointer;
    transition: border-color 0.15s ease, background 0.15s ease;
}
button.option:hover { border-color: var(--gold); background: #131c3c; }
a.start-btn, button.start-btn {
    display: inline-block;
    margin-top: 8px;
    background: var(--gold);
    color: #1a1204;
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-weight: 700;
    text-decoration: none;
    padding: 14px 22px;
    border-radius: 10px;
    text-align: center;
    border: none;
    cursor: pointer;
    font-size: 15px;
}
.result-name {
    font-size: 34px;
    color: var(--gold);
    margin: 4px 0 2px 0;
}
.result-title {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    color: var(--text-dim);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    font-size: 13px;
    margin-bottom: 20px;
}
.blurb { line-height: 1.6; font-size: 16px; }
"""

INTRO_HTML = """
<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Which Constellation Are You?</title><style>{{ css }}</style></head>
<body><div class="card">
  <p class="eyebrow">A 5-question quiz</p>
  <h1>Which Constellation Are You?</h1>
  <p class="sub">Answer honestly. It takes about a minute.</p>
  <a class="start-btn" href="{{ url_for('question', qnum=0) }}">Start</a>
</div></body></html>
"""

QUESTION_HTML = """
<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Question {{ qnum + 1 }}</title><style>{{ css }}</style></head>
<body><div class="card">
  <p class="eyebrow">Question {{ qnum + 1 }} of {{ total }}</p>
  <div class="progress">
    {% for i in range(total) %}
      <div class="dot {{ 'filled' if i <= qnum else '' }}"></div>
    {% endfor %}
  </div>
  <h1>{{ question.prompt }}</h1>
  <form method="POST" style="margin-top:20px;">
    {% for label, code in question.options %}
      <button class="option" type="submit" name="choice" value="{{ code }}">{{ label }}</button>
    {% endfor %}
  </form>
</div></body></html>
"""

RESULT_HTML = """
<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Your result: {{ result.name }}</title><style>{{ css }}</style></head>
<body><div class="card">
  <p class="eyebrow">Your constellation is</p>
  <div class="result-name">{{ result.name }}</div>
  <div class="result-title">{{ result.title }}</div>
  <p class="blurb">{{ result.blurb }}</p>
  <a class="start-btn" href="{{ url_for('intro') }}">Take it again</a>
</div></body></html>
"""


@app.route("/")
def intro():
    session.clear()
    return render_template_string(INTRO_HTML, css=BASE_CSS)


@app.route("/q/<int:qnum>", methods=["GET", "POST"])
def question(qnum):
    answers = session.get("answers", [])

    if request.method == "POST":
        choice = request.form.get("choice")
        if choice:
            answers.append(choice)
            session["answers"] = answers
        return redirect(url_for("question", qnum=qnum + 1))

    if qnum >= len(QUESTIONS):
        return redirect(url_for("result"))

    return render_template_string(
        QUESTION_HTML,
        css=BASE_CSS,
        qnum=qnum,
        total=len(QUESTIONS),
        question=QUESTIONS[qnum],
    )


@app.route("/result")
def result():
    answers = session.get("answers", [])
    if len(answers) < len(QUESTIONS):
        return redirect(url_for("intro"))

    counts = {}
    for code in answers:
        counts[code] = counts.get(code, 0) + 1
    top_score = max(counts.values())
    winners = [code for code, n in counts.items() if n == top_score]
    winner = random.choice(winners)  # tie-break randomly

    return render_template_string(RESULT_HTML, css=BASE_CSS, result=RESULTS[winner])


if __name__ == "__main__":
    # host="0.0.0.0" makes it reachable from other devices on your network,
    # which is useful for testing the QR code on your phone before deploying.
    app.run(host="0.0.0.0", port=5000, debug=True)
