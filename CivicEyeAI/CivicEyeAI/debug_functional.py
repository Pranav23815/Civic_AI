import sys
import os
import joblib
import pandas as pd
import numpy as np
from ultralytics import YOLO

# Add path
sys.path.append(os.path.abspath("."))

log_file = "debug_functional_log.txt"

def log(msg):
    print(msg)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

if os.path.exists(log_file):
    os.remove(log_file)

log("--- Functional Debugging ---")

try:
    from agent.brain import agent_decision
    log("✅ Imported agent_decision")
except Exception as e:
    log(f"❌ Failed to import agent.brain: {e}")
    sys.exit(1)

log("\n1. Testing Agent Decision with UI inputs...")
try:
    # Inputs from screenshot: Main Road, Medium traffic.
    # We'll use dummy area.
    test_inputs = {
        "damaged_area_m2": 5.0,
        "road_type": "Main Road",
        "traffic_level": "Medium",
        "issue_type": "pothole"
    }
    
    log(f"   Inputs: {test_inputs}")
    
    result = agent_decision(**test_inputs)
    log(f"✅ Agent Decision Result: {result}")

except Exception as e:
    log(f"❌ Agent Decision Failed: {e}")
    import traceback
    log(traceback.format_exc())

log("\n2. Checking Feature Columns...")
try:
    cols = joblib.load("agent/models/feature_columns.pkl")
    log(f"   Feature Columns: {cols}")
except Exception as e:
    log(f"❌ Failed to load feature columns: {e}")

log("--- Functional Debugging Complete ---")
