import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np
from agent.brain import agent_decision

# -----------------------------
# Load YOLO model
# -----------------------------
MODEL_PATH = "model/best.pt"
model = YOLO(MODEL_PATH)

# -----------------------------
# Utility: Convert pixel area → m²
# -----------------------------
def pixel_to_m2(pixel_area):
    # Hackathon-safe calibration constant
    meters_per_pixel = 0.01
    return pixel_area * (meters_per_pixel ** 2)

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Civic-Eye AI")
st.title("🚧 Civic-Eye AI – Smart City Auto Inspector")

uploaded = st.file_uploader("Upload Road Image", type=["jpg", "png", "jpeg"])

# Context inputs (NEW)
road_type = st.selectbox(
    "Road Type",
    ["Highway", "MainRoad", "Residential"]
)

traffic_level = st.selectbox(
    "Traffic Level",
    ["Low", "Medium", "High"]
)

if uploaded:

    # -----------------------------
    # Read image
    # -----------------------------
    bytes_data = uploaded.read()
    np_img = np.frombuffer(bytes_data, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    st.image(img, caption="Uploaded Image")

    # -----------------------------
    # YOLO inference
    # -----------------------------
    results = model(img)

    plotted = results[0].plot()
    st.image(plotted, caption="AI Detection")

    # -----------------------------
    # Compute damaged area (pixels)
    # -----------------------------
    pixel_area = 0
    if results[0].masks is not None:
        for mask in results[0].masks.data:
            pixel_area += int(mask.sum().item())

    # Convert to real-world area
    damaged_area_m2 = pixel_to_m2(pixel_area)

    # -----------------------------
    # Agent decision (UPDATED)
    # -----------------------------
    decision = agent_decision(
        damaged_area_m2=damaged_area_m2,
        road_type=road_type,
        traffic_level=traffic_level
    )

    # -----------------------------
    # Output
    # -----------------------------
    st.subheader("🧠 Agent Decision")
    st.json(decision)

    st.caption(
        f"Estimated damaged area: {damaged_area_m2:.2f} m² "
        "(calibrated approximation)"
    )
