import pandas as pd
import joblib

# -----------------------------
# Load trained models
# -----------------------------
severity_model = joblib.load("agent/models/severity.pkl")
priority_model = joblib.load("agent/models/priority.pkl")
cost_model = joblib.load("agent/models/cost.pkl")
time_model = joblib.load("agent/models/time.pkl")

# Load encoders
sev_enc = joblib.load("agent/models/sev_encoder.pkl")
pri_enc = joblib.load("agent/models/pri_encoder.pkl")

# Load feature columns used during training
feature_columns = joblib.load("agent/models/feature_columns.pkl")

# -----------------------------
# Agent decision function
# -----------------------------
def agent_decision(damaged_area_m2, road_type, traffic_level):

    # Build input dataframe
    X = pd.DataFrame([{
        "damaged_area_m2": damaged_area_m2,
        "road_type": road_type,
        "traffic_level": traffic_level
    }])

    # One-hot encode and align with training columns
    X = pd.get_dummies(X).reindex(
        columns=feature_columns,
        fill_value=0
    )

    # Predictions
    sev_pred = severity_model.predict(X)
    pri_pred = priority_model.predict(X)

    cost_pred = cost_model.predict(X)[0]
    time_pred = time_model.predict(X)[0]

    # Decode labels
    severity = sev_enc.inverse_transform(sev_pred)[0]
    priority = pri_enc.inverse_transform(pri_pred)[0]

    return {
        "severity": severity,
        "priority": priority,
        "estimated_cost": f"₹{int(cost_pred)}",
        "repair_time_days": int(time_pred)
    }
