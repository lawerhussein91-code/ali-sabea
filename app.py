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
        emp_no = request.form.get("emp_no", "").strip()
        password = request.form.get("password")

        # قراءة الشيت النظيف
        df = pd.read_excel(EXCEL_FILE)

        # تنظيف أسماء الأعمدة
        df.columns = df.columns.astype(str).str.strip()

        # التأكد من وجود العمود
        if "الرقم الوظيفي" not in df.columns:
            flash("عمود الرقم الوظيفي غير موجود")
            return redirect("/")

        # تنظيف الرقم الوظيفي
        df["الرقم الوظيفي"] = (
            df["الرقم الوظيفي"]
            .astype(str)
            .str.strip()
            .str.replace(".0", "", regex=False)
        )

        if emp_no not in df["الرقم الوظيفي"].values:
            flash("لم ترد الأضبارة")
            return redirect("/")

        # (حاليًا باسوورد موحد)
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
    df.columns = df.columns.astype(str).str.strip()

    row = df[df["الرقم الوظيفي"].astype(str).str.strip() == session["emp_no"]].iloc[0]

    return render_template("dashboard.html", row=row)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
