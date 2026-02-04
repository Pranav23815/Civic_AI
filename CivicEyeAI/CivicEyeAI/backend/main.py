
import sys
import os
import cv2
import numpy as np
import base64
import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
from pydantic import BaseModel

# Add the parent directory to sys.path to import agent modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all agent sub-modules
from agent.brain import agent_decision
from agent.verification import verifier
from agent.rewards import reward_engine
from agent.work_order import drafter
from agent.communication import dispatcher
from backend.pdf_generator import generate_work_order_pdf
from fastapi.responses import Response

app = FastAPI(title="Civic-Eye AI Backend")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load YOLO model
try:
    model = YOLO("model/best.pt")
    print("✅ YOLO Model loaded successfully")
except Exception as e:
    print(f"❌ Error loading YOLO model: {e}")
    model = None

def pixel_to_m2(pixel_area):
    meters_per_pixel = 0.01
    return pixel_area * (meters_per_pixel ** 2)

# --- REQUEST MODELS ---
class VerifyRequest(BaseModel):
    vision_confidence: float
    agent_result: dict
    location: dict

class RewardRequest(BaseModel):
    report_id: str
    user_id: str
    report_data: dict

class WorkOrderRequest(BaseModel):
    report_id: str
    location: dict
    agent_decision: dict

class EmailRequest(BaseModel):
    work_order_data: dict

# --- ENDPOINTS ---

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Civic-Eye AI Backend"}

@app.post("/analyze")
async def analyze_road(
    image: UploadFile = File(...),
    road_type: str = Form(...),
    traffic_level: str = Form(...),
    issue_type: str = Form(...)
):
    try:
        if not model:
            raise HTTPException(status_code=500, detail="Model not loaded")

        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file")

        results = model(img)
        result = results[0]

        # Calculate Area & Confidence
        pixel_area = 0
        box_conf = 0.0
        if result.masks is not None:
            for mask in result.masks.data:
                pixel_area += int(mask.sum().item())
        
        if result.boxes:
            box_conf = float(result.boxes.conf.mean().item()) if result.boxes.conf.numel() > 0 else 0.0

        damaged_area_m2 = pixel_to_m2(pixel_area)

        plotted_img = result.plot()
        _, buffer = cv2.imencode('.jpg', plotted_img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        # Agent Decision
        decision = agent_decision(
            damaged_area_m2=damaged_area_m2,
            road_type=road_type,
            traffic_level=traffic_level,
            issue_type=issue_type
        )

        # Merge basic vision metadata into response for frontend pipeline state
        decision["annotated_image"] = f"data:image/jpeg;base64,{img_base64}"
        decision["vision_confidence"] = box_conf
        return decision

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        print(f"❌ PIPELINE ERROR: {e}")
        with open("backend_error.log", "a", encoding="utf-8") as f:
            f.write(f"\n--- ERROR ---\n{err_msg}\n")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/verify")
def verify_report(payload: VerifyRequest):
    # Pass data to Verification Engine
    result = verifier.verify_submission(
        vision_metadata={"box_confidence": payload.vision_confidence},
        agent_result=payload.agent_result,
        location_data=payload.location
    )
    return result

@app.post("/reward")
def grant_reward(payload: RewardRequest):
    # Pass to Reward Engine
    result = reward_engine.process_reward(
        user_id=payload.user_id,
        report_id=payload.report_id,
        report_data=payload.report_data
    )
    return result

@app.post("/work-order")
def generate_work_order(payload: WorkOrderRequest):
    # Pass to Drafting Engine
    result = drafter.generate_draft(
        report_id=payload.report_id,
        location=payload.location,
        agent_decision=payload.agent_decision
    )
    return result

@app.post("/dispatch-email")
def send_email(payload: EmailRequest):
    # Pass to Email Dispatcher
    result = dispatcher.dispatch_work_order(payload.work_order_data)
    return result

@app.post("/generate-pdf")
def generate_pdf(payload: dict):
    # Expects the same structure as WorkOrderRequest or just the dict
    # Re-using the pdf generator logic
    try:
        pdf_buffer = generate_work_order_pdf(payload)
        return Response(content=pdf_buffer.getvalue(), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=work_order.pdf"})
    except Exception as e:
        print(f"PDF Gen Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
