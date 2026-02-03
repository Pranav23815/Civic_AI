# Civic-Eye AI – Autonomous Urban Infrastructure Decision System

> **Automating road maintenance decisions with Vision AI and Agentic Workflows.**

Civic-Eye AI is an intelligent infrastructure management system designed to assist municipal corporations. It combines **Computer Vision (YOLOv8)** for damage detection with a **Learning-Based Decision Agent** to autonomously assess severity, prioritize repairs, and estimate municipal costs.

---

## 🏗️ Problem Statement

Municipal road maintenance in India and many developing nations faces critical bottlenecks:
*   **Manual Inspection:** Engineers physically survey roads, which is slow and error-prone.
*   **Subjective Decisions:** Assessments of severity and priority vary between officials.
*   **Planning Latency:** Delays between detection and work-order generation caused by bureaucratic estimation processes.

## 💡 Solution Overview

Civic-Eye AI replaces subjective manual surveys with an objective, data-driven pipeline:
1.  **Vision Layer:** Instantly detects potholes and segmentation masks using YOLOv8.
2.  **Context Layer:** Ingests context like Road Type (Highway/Residential) and Traffic Level.
3.  **Decision Agent:** A trained Random Forest agent predicts:
    *   **Severity:** (Low/Medium/High)
    *   **Priority:** (Immediate/Scheduled/Routine)
    *   **Logistics:** Estimated Repair Cost (₹) & Time.

---

## ⚙️ System Architecture

```mermaid
graph LR
    User[User / Muni Official] -->|Upload Image + Context| Frontend
    Frontend[React + Tailwind UI] -->|POST /analyze| Backend
    Backend[FastAPI] -->|Image| Vision[YOLOv8 Vision Engine]
    Vision -->|Damaged Area (m²)| Agent
    Backend -->|Road Type + Traffic| Agent[Decision Agent (RF)]
    Agent -->|JSON Decision| Backend
    Backend -->|Analysis Result| Frontend
```

---

## 🚀 Key Features

*   **Automated Pothole Segmentation:** Precise pixel-level detection of road damage.
*   **Smart Severity Grading:** AI decides if a repair is critical based on size and location.
*   **Dynamic Cost Estimation:** Estimates repair costs based on real-world engineering rates (calibrated for Indian infrastructure).
*   **Priority Matrix:** Automatically prioritizes high-traffic highways over residential lanes.
*   **Full-Stack Deployment:** Professional React frontend coupled with a robust FastAPI python backend.

## 🛠️ Tech Stack

*   **Frontend:** React.js, Tailwind CSS, Vite, Axios
*   **Backend:** FastAPI, Uvicorn, Python
*   **AI/ML:** YOLOv8 (Ultralytics), Scikit-Learn (Random Forest), OpenCV, Pandas
*   **Data:** Synthetic dataset calibrated with municipal engineering standards

---

## 📂 Folder Structure

```
CivicEyeAI/
├── agent/              # Decision agent logic & training scripts
│   ├── brain.py        # Inference logic
│   ├── models/         # Trained .pkl models
│   └── agent_data.csv  # Training dataset
├── backend/            # FastAPI backend
│   └── main.py         # API entry point
├── frontend/           # React application
│   ├── src/            # UI Components
│   └── package.json
├── model/              # YOLOv8 weights
│   └── best.pt
├── requirements.txt    # Python dependencies
└── README.md
```

---

## ⚡ How to Run

### 1. Backend Setup (Python)

Navigate to the root directory `CivicEyeAI`:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API server
uvicorn backend.main:app --reload --port 8000
```
*The backend will start at `http://localhost:8000`*

### 2. Frontend Setup (React)

Open a new terminal and navigate to the `frontend` folder:

```bash
cd frontend

# Install Node modules
npm install

# Start the development server
npm run dev
```
*The UI will launch at `http://localhost:3000`*

---

## 📊 Dataset & Accuracy

*   **Vision Model:** Trained on a refined subset of the "Pothole-600" dataset, achieving steady mAP on test splits.
*   **Decision Agent:** Trained on `agent_data.csv`, a dataset containing 1,000 synthetic records modeled after real-world correlations (e.g., Highway damage = Higher Priority/Cost). It achieves ~95% accuracy in adhering to logic rules.

## ⚠️ Disclaimer

*This project is a functional prototype developed for demonstration/hackathon purposes. Cost estimates and repair timelines are algorithmic approximations and should be validated by civil engineers before real-world tendering.*
