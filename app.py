from flask import Flask, render_template, request, redirect, session, flash
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "ali_sabea_secret_key"

DEFAULT_PASSWORD = "12345678"
EXCEL_FILE = "برنامج الترقيات 7-1-2026.xlsx"

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        emp_no = request.form.get("emp_no")
        password = request.form.get("password")

        if not os.path.exists(EXCEL_FILE):
            flash("ملف البيانات غير موجود")
            return redirect("/")

        df = pd.read_excel(EXCEL_FILE)

        if emp_no not in df["الرقم الوظيفي"].astype(str).values:
            flash("لم ترد الأضبارة")
            return redirect("/")

        if password != DEFAULT_PASSWORD:
            flash("كلمة المرور غير صحيحة")
            return redirect("/")

        session["emp_no"] = emp_no
        return redirect("/dashboard")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "emp_no" not in session:
        return redirect("/")

    df = pd.read_excel(EXCEL_FILE)
    row = df[df["الرقم الوظيفي"].astype(str) == session["emp_no"]].iloc[0]

    return render_template("dashboard.html", row=row)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=
