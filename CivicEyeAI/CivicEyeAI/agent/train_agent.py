import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_absolute_error, r2_score

# -----------------------------
# Load dataset
# -----------------------------
data = pd.read_csv("agent/agent_data.csv")
print("CSV Columns:", list(data.columns))

# -----------------------------
# Features (INPUTS)
# -----------------------------
X = data[
    ["damaged_area_m2", "road_type", "traffic_level"]
]

# One-hot encode categorical features
X = pd.get_dummies(X)

# Save feature columns for inference alignment
os.makedirs("agent/models", exist_ok=True)
joblib.dump(X.columns.tolist(), "agent/models/feature_columns.pkl")

# -----------------------------
# Targets (OUTPUTS)
# -----------------------------
le_sev = LabelEncoder()
le_pri = LabelEncoder()

y_sev = le_sev.fit_transform(data["severity"])
y_pri = le_pri.fit_transform(data["priority"])
y_cost = data["repair_cost_in_INR"]
y_time = data["repair_time_days"]

# Split data
X_train, X_test, y_sev_train, y_sev_test, y_pri_train, y_pri_test, y_cost_train, y_cost_test, y_time_train, y_time_test = train_test_split(
    X, y_sev, y_pri, y_cost, y_time, test_size=0.2, random_state=42
)

# -----------------------------
# Models
# -----------------------------
severity_model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

priority_model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

cost_model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

time_model = RandomForestRegressor(
    n_estimators=200,
    random_state=42
)

# -----------------------------
# Train
# -----------------------------
severity_model.fit(X_train, y_sev_train)
priority_model.fit(X_train, y_pri_train)
cost_model.fit(X_train, y_cost_train)
time_model.fit(X_train, y_time_train)

# -----------------------------
# Evaluation
# -----------------------------
sev_acc = accuracy_score(y_sev_test, severity_model.predict(X_test))
pri_acc = accuracy_score(y_pri_test, priority_model.predict(X_test))
cost_mae = mean_absolute_error(y_cost_test, cost_model.predict(X_test))
time_mae = mean_absolute_error(y_time_test, time_model.predict(X_test))

print("\n--- Model Performance ---")
print(f"Severity Accuracy: {sev_acc:.2%}")
print(f"Priority Accuracy: {pri_acc:.2%}")
print(f"Cost MAE: INR {cost_mae:.2f}")
print(f"Time MAE: {time_mae:.2f} days")

# -----------------------------
# Save models & encoders (retrain on full data for production)
# -----------------------------
severity_model.fit(X, y_sev)
priority_model.fit(X, y_pri)
cost_model.fit(X, y_cost)
time_model.fit(X, y_time)

joblib.dump(severity_model, "agent/models/severity.pkl")
joblib.dump(priority_model, "agent/models/priority.pkl")
joblib.dump(cost_model, "agent/models/cost.pkl")
joblib.dump(time_model, "agent/models/time.pkl")

joblib.dump(le_sev, "agent/models/sev_encoder.pkl")
joblib.dump(le_pri, "agent/models/pri_encoder.pkl")

print("\nAgent models trained and saved successfully.")
