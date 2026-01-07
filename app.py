from flask import Flask, render_template, request, redirect, session, flash
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "ali_sabea_secret_key"

DEFAULT_PASSWORD = "12345678"
EXCEL_FILE = "برنامج الترقيات 7-1-2026.xlsx"
SHEET_INDEX = 1   # الشيت الثاني


def normalize(text):
    """تطبيع النص لإزالة المسافات والرموز الخفية"""
    return (
        str(text)
        .replace("\u00a0", "")
        .replace(" ", "")
        .replace("ـ", "")
        .strip()
    )


def load_df():
    # قراءة الإكسل (الشيت الثاني)
    df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_INDEX)

    # تنظيف أسماء الأعمدة
    df.columns = df.columns.astype(str).str.strip()

    # البحث الذكي عن عمود الرقم الوظيفي
    emp_col = None
    for col in df.columns:
        col_norm = normalize(col)
        if "رقم" in col_norm and "وظيف" in col_norm:
            emp_col = col
            break

    if emp_col is None:
        raise ValueError(f"لم يتم العثور على عمود الرقم الوظيفي. الأعمدة الموجودة: {list(df.columns)}")

    # تنظيف الرقم الوظيفي
    df[emp_col] = (
        df[emp_col]
        .astype(str)
        .str.strip()
        .str.replace(".0", "", regex=False)
    )

    # نخزن اسم العمود حتى نستخدمه بباقي الدوال
    df.attrs["emp_col"] = emp_col
    return df


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        emp_no = request.form.get("emp_no", "").strip()
        password = request.form.get("password", "")

        try:
            df = load_df()
            emp_col = df.attrs["emp_col"]
        except Exception as e:
            flash(f"خطأ بملف الإكسل: {e}")
            return redirect("/")

        if emp_no not in df[emp_col].values:
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

    try:
        df = load_df()
        emp_col = df.attrs["emp_col"]
        row = df[df[emp_col] == session["emp_no"]]

        if row.empty:
            flash("لم ترد الأضبارة")
            return redirect("/")

        return render_template("dashboard.html", row=row.iloc[0])

    except Exception as e:
        return f"ERROR: {e}"


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
