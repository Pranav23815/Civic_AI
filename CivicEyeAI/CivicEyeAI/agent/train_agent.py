import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import os

data = pd.read_csv("agent/agent_data.csv")

X = data[["detections", "area"]]

le_sev = LabelEncoder()
le_pri = LabelEncoder()

y_sev = le_sev.fit_transform(data["severity"])
y_pri = le_pri.fit_transform(data["priority"])
y_cost = data["cost"]
y_time = data["time"]

severity_model = RandomForestClassifier()
priority_model = RandomForestClassifier()
cost_model = RandomForestRegressor()
time_model = RandomForestRegressor()

severity_model.fit(X, y_sev)
priority_model.fit(X, y_pri)
cost_model.fit(X, y_cost)
time_model.fit(X, y_time)

os.makedirs("agent/models", exist_ok=True)

joblib.dump(severity_model, "agent/models/severity.pkl")
joblib.dump(priority_model, "agent/models/priority.pkl")
joblib.dump(cost_model, "agent/models/cost.pkl")
joblib.dump(time_model, "agent/models/time.pkl")

joblib.dump(le_sev, "agent/models/sev_encoder.pkl")
joblib.dump(le_pri, "agent/models/pri_encoder.pkl")

print("Agent models trained successfully")
