from flask import Flask, request, render_template, jsonify
import config, pickle
import pandas as pd

app = Flask(__name__)

# -------------------------------
# LOAD TRAINED SCALER + MODEL
# -------------------------------
with open(config.POWER_TRANSFORMENR, "rb") as f:
    pt = pickle.load(f)             # PowerTransformer

with open(config.KNN_MODEL, "rb") as f:
    model = pickle.load(f)          # best_model_v2


# -------------------------------
# ENCODING DICTIONARIES
# -------------------------------
education_map = {"Graduate": 1, "Not Graduate": 0}
self_emp_map = {"Yes": 1, "No": 0}


# -------------------------------
# PREDICTION API ROUTE
# -------------------------------
@app.route("/")
def predict_page():
    return render_template("/predict.html")

@app.route("/api/predict", methods=["POST"])
def predict():

    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    required_fields = [
        "no_of_dependents", "education", "self_employed",
        "income_annum", "loan_amount", "loan_term", "cibil_score",
        "residential_assets_value", "commercial_assets_value",
        "luxury_assets_value", "bank_asset_value"
    ]

    # Validate missing fields
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    # Convert to DataFrame
    user_df = pd.DataFrame([data])

    # Apply Encoding
    try:
        user_df["education"] = user_df["education"].map(education_map)
        user_df["self_employed"] = user_df["self_employed"].map(self_emp_map)
    except:
        return jsonify({"error": "Invalid categorical value"}), 400

    # Apply Scaling
    try:
        user_scaled = pt.transform(user_df)
    except:
        return jsonify({"error": "Scaling failed"}), 500

    # Prediction
    prediction = int(model.predict(user_scaled)[0])
    probability = float(model.predict_proba(user_scaled)[0][1])

    # If request came from HTML form then it will Show HTML result
    if not request.is_json:
        result = "Approved ✔️" if prediction == 1 else "Rejected ❌"
        return render_template("/predict.html", prediction=result)

    # API JSON Response
    return jsonify({
        "prediction": "Approved" if prediction == 1 else "Rejected",
        "prediction_raw": prediction,
        "approval_probability": round(probability, 4)
    })

if __name__ == "__main__":
    app.run(debug=True)