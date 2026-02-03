import sys
import os
import cv2
import numpy as np
import base64
import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO

# Add the parent directory to sys.path to import agent modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.brain import agent_decision

app = FastAPI(title="Civic-Eye AI Backend")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load YOLO model
# Assuming 'model/best.pt' is in the root directory relative to where uvicorn is run
try:
    model = YOLO("model/best.pt")
    print("✅ YOLO Model loaded successfully")
except Exception as e:
    print(f"❌ Error loading YOLO model: {e}")
    # Fallback/Mock for robustness if model path is wrong (during dev) or raise
    model = None

def pixel_to_m2(pixel_area):
    # Calibration: 1 pixel = 1cm (0.01m) -> 1 sq pixel = 0.0001 sq m ??
    # Previous logic in app.py: meters_per_pixel = 0.01 -> area * (0.01**2)
    meters_per_pixel = 0.01
    return pixel_area * (meters_per_pixel ** 2)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Civic-Eye AI Backend"}

@app.post("/analyze")
async def analyze_road(
    image: UploadFile = File(...),
    road_type: str = Form(...),
    traffic_level: str = Form(...)
):
    if not model:
        raise HTTPException(status_code=500, detail="Model not loaded")

    # Read Image
    contents = await image.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # YOLO Inference
    results = model(img)
    result = results[0]

    # Calculate Area
    pixel_area = 0
    if result.masks is not None:
        for mask in result.masks.data:
            pixel_area += int(mask.sum().item())
    
    damaged_area_m2 = pixel_to_m2(pixel_area)

    # Get plotted image for frontend preview
    plotted_img = result.plot()
    # Convert to base64
    _, buffer = cv2.imencode('.jpg', plotted_img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    # Agent Decision
    try:
        decision = agent_decision(
            damaged_area_m2=damaged_area_m2,
            road_type=road_type,
            traffic_level=traffic_level
        )
    except Exception as e:
        print(f"Agent Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "damaged_area_m2": round(damaged_area_m2, 4),
        "severity": decision["severity"],
        "priority": decision["priority"],
        "estimated_cost": decision["estimated_cost"],
        "repair_time_days": decision["repair_time_days"],
        "annotated_image": f"data:image/jpeg;base64,{img_base64}"
    }

if __name__ == "__main__":
    import uvicorn
    # Run from root with: python -m backend.main
    uvicorn.run(app, host="0.0.0.0", port=8000)
