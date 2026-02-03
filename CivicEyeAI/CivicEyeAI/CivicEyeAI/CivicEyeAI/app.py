import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np

# -------------------------
# LOAD MODEL (ABSOLUTE PATH)
# -------------------------

MODEL_PATH = r"D:\uDDDDD\civic_eye_project\CivicEyeAI\CivicEyeAI\model\best.pt"
model = YOLO(MODEL_PATH)

# -------------------------
# STREAMLIT UI
# -------------------------

st.set_page_config(page_title="Civic-Eye AI", layout="centered")

st.title("🚧 Civic-Eye AI – Smart City Auto Inspector")

issue_type = st.selectbox(
    "Select Issue Type",
    ["Pothole", "Garbage", "Streetlight"]
)

uploaded = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

# -------------------------
# AGENT DECISION LOGIC
# -------------------------

def agent_decision(issue, detections):

    base_cost = {
        "Pothole": 1500,
        "Garbage": 800,
        "Streetlight": 2000
    }

    cost = base_cost[issue] * detections

    if detections <= 2:
        priority = "Low"
    elif detections <= 5:
        priority = "Medium"
    else:
        priority = "High"

    return {
        "issue_type": issue,
        "detections": detections,
        "estimated_cost": f"₹{cost}",
        "priority": priority,
        "action": "Auto Work Order Generated"
    }

# -------------------------
# MAIN PIPELINE
# -------------------------

if uploaded:
    try:
        file_bytes = np.asarray(bytearray(uploaded.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)

        st.image(img, caption="Uploaded Image")

        results = model(img)[0]
        annotated = results.plot()

        st.image(annotated, caption="AI Detection")

        detections = len(results.boxes)

        decision = agent_decision(issue_type, detections)

        st.subheader("🧠 Agent Decision")
        st.json(decision)

    except Exception as e:
        st.error(f"ERROR: {e}")
