import sys
import os
import joblib
import pandas as pd
import numpy as np
import cv2
from ultralytics import YOLO

# Add path
sys.path.append(os.path.abspath("."))

log_file = "debug_functional_log_2.txt"

def log(msg):
    print(msg)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

if os.path.exists(log_file):
    os.remove(log_file)

log("--- Functional Debugging Round 2 ---")

try:
    log("1. Loading YOLO model...")
    model = YOLO("model/best.pt")
    log("✅ YOLO Loaded.")

    log("2. creating dummy image...")
    # Create a black image 640x640
    img = np.zeros((640, 640, 3), dtype=np.uint8)
    
    log("3. Running Inference...")
    results = model(img)
    log(f"✅ Inference Successful. Result count: {len(results)}")
    
    result = results[0]
    if result.masks:
        log("   Has masks.")
    else:
        log("   No masks (expected for black image).")
        
    pixel_area = 0
    # Simulate mask calculation logic from backend
    if result.masks is not None:
        for mask in result.masks.data:
            pixel_area += int(mask.sum().item())
    log(f"   Pixel Area Calculation: {pixel_area}")

except Exception as e:
    log(f"❌ YOLO Inference Failed: {e}")
    import traceback
    log(traceback.format_exc())

log("--- Functional Debugging Round 2 Complete ---")
