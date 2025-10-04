\
import os
import json
from flask import Flask, render_template, jsonify, Response
import pandas as pd
import numpy as np

app = Flask(__name__)

MODEL_PATH = os.path.join("C:\\Users\\amanp\\Desktop\\odoo\\frontend\\model\\final_expense_model.pkl")
PRED_CSV = os.path.join("C:\\Users\\amanp\\Desktop\\odoo\\frontend\\data", "predicted_expenses.csv")
LATEST_FEATURES = os.path.join("C:\\Users\\amanp\\Desktop\\odoo\\frontend\\data", "latest_features.csv")
try:
    import joblib
except Exception:
    joblib = None

def load_predictions():
    if os.path.exists(PRED_CSV):
        df = pd.read_csv(PRED_CSV, parse_dates=["year_month"])
        if "predicted_amount" not in df.columns and "predicted" in df.columns:
            df = df.rename(columns={"predicted":"predicted_amount"})
        return df

    if os.path.exists(MODEL_PATH) and os.path.exists(LATEST_FEATURES) and joblib is not None:
        model = joblib.load(MODEL_PATH)
        feats = pd.read_csv(LATEST_FEATURES, parse_dates=["year_month"])
        if "company_id" in feats.columns and "category" in feats.columns:
            feature_cols = [c for c in feats.columns if c not in ("company_id","category","year_month")]
            X = feats[feature_cols].fillna(0)
            try:
                preds = model.predict(X)
            except Exception:
                preds = np.array(model.predict(X)).ravel()
            feats["predicted_amount"] = preds
            return feats[["company_id","category","year_month","predicted_amount"]]

    now = pd.Timestamp.today().normalize().to_period('M').to_timestamp()
    categories = ["Travel","Meals","Supplies","Software","Marketing"]
    rows = []
    for c in categories:
        rows.append({
            "company_id": "demo_co",
            "category": c,
            "year_month": now + pd.offsets.MonthBegin(1),
            "predicted_amount": float(np.round(1000 + np.random.rand()*4000, 2))
        })
    return pd.DataFrame(rows)

@app.route("/api/predictions")
def api_predictions():
    df = load_predictions()
    df_group = df.groupby("category", as_index=False)["predicted_amount"].sum().reset_index(drop=True)
    df["year_month"] = df["year_month"].astype(str)
    df_group["predicted_amount"] = df_group["predicted_amount"].round(2)
    result = {
        "predictions": df.to_dict(orient="records"),
        "category_summary": df_group.to_dict(orient="records")
    }
    return jsonify(result)

@app.route("/api/predictions/download")
def download_predictions():
    df = load_predictions()
    csv = df.to_csv(index=False)
    # Return as attachment-like response; front-end will trigger download
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=predicted_expenses.csv"}
    )

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
