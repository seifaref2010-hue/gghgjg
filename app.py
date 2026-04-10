import os
import pandas as pd
from flask import Flask, request, redirect
import plotly.graph_objects as go
from datetime import datetime

# ملف البيانات (هيتعمل تلقائي)
DB_FILE = "data.xlsx"

if not os.path.exists(DB_FILE):
    pd.DataFrame(columns=["ID", "Name", "Score", "Pollution", "Problem", "Risk", "Date"]).to_excel(DB_FILE, index=False)

app = Flask(__name__)

# تحليل البيانات
def analyze(ans):
    score = 100
    logic = {"Brown": -35, "Yellow": -20, "Chlorine": -15, "Rust": -25, "Salty": -30}
    problems = [a for a in ans if a in logic]
    
    for a in ans:
        score += logic.get(a, 0)

    score = max(5, min(100, score))
    risk = "High" if score < 50 else "Medium" if score < 80 else "Safe"

    return score, problems, risk

# الصفحة الرئيسية
@app.route("/")
def home():
    return '''
    <h1>H2O Scan</h1>
    <form action="/process" method="post">
    Name: <input name="name"><br><br>

    Color:
    <input type="radio" name="q1" value="Clear">Clear
    <input type="radio" name="q1" value="Yellow">Yellow
    <input type="radio" name="q1" value="Brown">Brown<br><br>

    Smell:
    <input type="radio" name="q2" value="None">None
    <input type="radio" name="q2" value="Chlorine">Chlorine
    <input type="radio" name="q2" value="Rust">Rust<br><br>

    Taste:
    <input type="radio" name="q3" value="Normal">Normal
    <input type="radio" name="q3" value="Salty">Salty<br><br>

    <button type="submit">Analyze</button>
    </form>
    '''

# معالجة البيانات
@app.route("/process", methods=["POST"])
def process():
    name = request.form.get("name")
    ans = [request.form.get("q1"), request.form.get("q2"), request.form.get("q3")]

    score, problems, risk = analyze(ans)

    df = pd.read_excel(DB_FILE)
    uid = len(df)

    new_row = {
        "ID": uid,
        "Name": name,
        "Score": score,
        "Pollution": 100 - score,
        "Problem": ", ".join(problems),
        "Risk": risk,
        "Date": datetime.now()
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(DB_FILE, index=False)

    return redirect(f"/report/{uid}")

# التقرير
@app.route("/report/<int:uid>")
def report(uid):
    df = pd.read_excel(DB_FILE)
    row = df.iloc[uid]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=row['Score'],
        gauge={'axis': {'range': [0, 100]}}
    ))

    return f"""
    <h1>{row['Name']}</h1>
    {fig.to_html(full_html=False)}
    <h3>Risk: {row['Risk']}</h3>
    <p>Problems: {row['Problem']}</p>
    <a href="/">Back</a>
    """

# الأدمن
@app.route("/admin")
def admin():
    df = pd.read_excel(DB_FILE)
    return df.to_html()

# تشغيل السيرفر
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=