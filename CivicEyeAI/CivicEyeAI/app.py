import streamlit as st
from ultralytics import YOLO
import cv2
import numpy as np
from agent.brain import agent_decision

MODEL_PATH = "model/best.pt"
model = YOLO(MODEL_PATH)

st.set_page_config(page_title="Civic-Eye AI")
st.title("🚧 Civic-Eye AI – Smart City Auto Inspector")

uploaded = st.file_uploader("Upload Image", type=["jpg","png","jpeg"])

if uploaded:

    bytes_data = uploaded.read()
    np_img = np.frombuffer(bytes_data, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    st.image(img, caption="Uploaded Image")

    results = model(img)

    plotted = results[0].plot()

    st.image(plotted, caption="AI Detection")

    detections = len(results[0].boxes)

    area = 0
    if results[0].masks:
        for mask in results[0].masks.data:
            area += int(mask.sum().item())

    decision = agent_decision(detections, area)

    st.subheader("🧠 Agent Decision")
    st.json(decision)
