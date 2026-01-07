from flask import Flask, render_template, request, redirect, session, flash
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "ali_sabea_secret_key"

DEFAULT_PASSWORD = "12345678"
EXCEL_FILE = "برنامج الترقيات 7-1-2026.xlsx"
SHEET_INDEX = 0


def load_df():
    # قراءة الشيت المعتمد
 df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_INDEX)

    # تنظيف أسماء الأعمدة
    df.columns = df.columns.astype(str).str.strip()

    # التأكد من وجود العمود الأساسي
    if "الرقم الوظيفي" not in df.columns:
        raise ValueError("عمود الرقم الوظيفي غير موجود")

    # تنظيف أرقام الموظفين (يشيل مسافات ويشيل .0)
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

        # التحقق من وجود الموظف
        if emp_no not in df["الرقم الوظيفي"].values:
            flash("لم ترد الأضبارة")
            return redirect("/")

        # كلمة المرور الموحدة حالياً
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

    try:
        df = load_df()

        row = df[df["الرقم الوظيفي"] == session["emp_no"]]

        if row.empty:
            return "ERROR: الموظف موجود بالجلسة لكن غير موجود بالبيانات"

        return render_template("dashboard.html", row=row.iloc[0])

    except Exception as e:
        return f"ERROR DETAILS: {e}"
