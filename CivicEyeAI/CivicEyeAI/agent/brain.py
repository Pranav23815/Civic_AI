import joblib
import numpy as np

severity_model = joblib.load("agent/models/severity.pkl")
priority_model = joblib.load("agent/models/priority.pkl")
cost_model = joblib.load("agent/models/cost.pkl")
time_model = joblib.load("agent/models/time.pkl")
sev_enc = joblib.load("agent/models/sev_encoder.pkl")
pri_enc = joblib.load("agent/models/pri_encoder.pkl")

def agent_decision(detections, area):

    X = np.array([[detections, area]])

    sev = sev_enc.inverse_transform(
        severity_model.predict(X)
    )[0]

    pri = pri_enc.inverse_transform(
        priority_model.predict(X)
    )[0]

    cost = int(cost_model.predict(X)[0])
    time = int(time_model.predict(X)[0])

    return {
        "detections": detections,
        "severity": sev,
        "priority": pri,
        "estimated_cost": f"₹{cost}",
        "repair_time(days)": time
    }
