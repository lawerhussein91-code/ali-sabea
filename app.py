emp_no = request.form.get("emp_no", "").strip()
password = request.form.get("password")

# قراءة الإكسل بدون افتراض العناوين
raw_df = pd.read_excel(EXCEL_FILE, sheet_name=0, header=None)

# البحث عن صف العناوين الحقيقي
header_row = None
for i in range(len(raw_df)):
    if "الرقم الوظيفي" in raw_df.iloc[i].astype(str).values:
        header_row = i
        break

if header_row is None:
    flash("لم يتم العثور على عناوين الجدول")
    return redirect("/")

# إعادة قراءة الإكسل مع صف العناوين الصحيح
df = pd.read_excel(EXCEL_FILE, sheet_name=0, header=header_row)

# تنظيف أسماء الأعمدة
df.columns = df.columns.astype(str).str.strip()

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
