from flask import Flask, session
import pandas as pd

app = Flask(__name__)
app.secret_key = "test"

@app.route("/")
def home():
    return "APP IS RUNNING OK"

@app.route("/test")
def test():
    df = pd.read_excel("Book1.xlsx")
    return str(list(df.columns))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
