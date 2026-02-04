import sys
import os
import joblib
from ultralytics import YOLO

# Add path like backend/main.py
sys.path.append(os.path.abspath("."))

log_file = "debug_log.txt"

def log(msg):
    print(msg)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

if os.path.exists(log_file):
    os.remove(log_file)

log("--- Debugging Startup ---")
log(f"CWD: {os.getcwd()}")

log("\n1. Checking YOLO model...")
try:
    model = YOLO("model/best.pt")
    log("✅ YOLO Model loaded.")
except Exception as e:
    log(f"❌ YOLO Failed: {e}")

log("\n2. Checking Agent Models...")
models_dir = "agent/models"
files = ["severity.pkl", "priority.pkl", "cost.pkl", "time.pkl", "sev_encoder.pkl", "pri_encoder.pkl", "feature_columns.pkl"]
for f in files:
    path = os.path.join(models_dir, f)
    if not os.path.exists(path):
        log(f"❌ Missing file: {path}")
    else:
        try:
            joblib.load(path)
            log(f"✅ Loaded {f}")
        except Exception as e:
            log(f"❌ Failed to load {f}: {e}")

log("\n3. Testing imports...")
try:
    from agent.brain import agent_decision
    log("✅ Imported agent_decision")
except Exception as e:
    log(f"❌ Failed to import agent.brain: {e}")

log("--- Debugging Complete ---")
