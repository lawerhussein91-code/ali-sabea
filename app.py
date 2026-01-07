from flask import Flask, render_template, request, redirect, session, flash
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "ali_sabea_secret_key"

DEFAULT_PASSWORD = "12345678"
EXCEL_FILE = "برنامج الترقيات 7-1-2026.xlsx"
SHEET_INDEX = 1  # الشيت الثاني


def load_df():
    df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_INDEX)

    df.columns = df.columns.astype(str).str.strip()

    if "الرقم الوظيفي" not in df.columns:
        raise ValueError("عمود الرقم الوظيفي غير موجود")

    df["الرقم الوظيفي"] = (
        df["الرقم الوظيفي"]
        .astype(str)
        .str.strip()
        .str.replace(".0", "", regex=False)
    )

    return df


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        emp_no = request.form.get("emp_no", "").strip()
        password = request.form.get("password", "")

        try:
            df = load_df()
        except Exception as e:
            flash(f"خطأ بملف الإكسل: {e}")
            return redirect("/")

        if emp_no not in df["الرقم الوظيفي"].values:
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

    df = load_df()
    row = df[df["الرقم الوظيفي"] == session["emp_no"]]

    if row.empty:
        flash("لم ترد الأضبارة")
        return redirect("/")

    return render_template("dashboard.html", row=row.iloc[0])


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
    

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
