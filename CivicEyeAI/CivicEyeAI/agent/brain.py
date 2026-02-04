import joblib
import pandas as pd
import numpy as np
import random

# ---------------------------------------------------------
# CIVIC CORTEX: CONSTANTS & CONFIG
# ---------------------------------------------------------

RISK_WEIGHTS = {
    "pothole": {"safety": 0.5, "exposure": 0.3, "scale": 0.2},
    "street_light": {"safety": 0.6, "exposure": 0.4, "scale": 0.0},
    "garbage": {"safety": 0.3, "exposure": 0.2, "scale": 0.5}
}

TRAFFIC_MULTIPLIERS = {"Low": 1.0, "Medium": 1.5, "High": 2.2}
ROAD_MULTIPLIERS = {"Residential": 1.0, "Secondary": 1.2, "MajorRoad": 1.5, "Highway": 2.0}

ACTION_MATRIX = {
    "Critical": "🚨 EMERGENCY: Dispatch Rapid Response Team immediately.",
    "High": "URGENT: Schedule repair within 48 hours.",
    "Medium": "ROUTINE: Add to weekly maintenance queue.",
    "Low": "MONITOR: Flag for review in next sector audit."
}

# ---------------------------------------------------------
# CIVIC AGENT CLASS
# ---------------------------------------------------------

class CivicAgent:
    def __init__(self):
        self._load_models()
        self.feature_columns = joblib.load("agent/models/feature_columns.pkl")
    
    def _load_models(self):
        """Loads existing ML models for logistics prediction."""
        try:
            self.models = {
                "severity": joblib.load("agent/models/severity.pkl"),
                "priority": joblib.load("agent/models/priority.pkl"),
                "cost": joblib.load("agent/models/cost.pkl"),
                "time": joblib.load("agent/models/time.pkl"),
                "sev_enc": joblib.load("agent/models/sev_encoder.pkl"),
                "pri_enc": joblib.load("agent/models/pri_encoder.pkl")
            }
            self.ml_ready = True
        except:
            print("⚠️ WARNING: ML Models not found. Agent running in HEURISTIC ONLY mode.")
            self.ml_ready = False

    def decide(self, issue_type, metrics, context):
        """
        Main decision pipeline.
        
        Args:
            issue_type (str): 'pothole', 'street_light', 'garbage'
            metrics (dict): {'area': float, 'count': int, ...}
            context (dict): {'road_type': str, 'traffic_level': str}
        """
        
        # 1. Calculate Risk Score (0-100)
        risk_score = self._calculate_risk_score(issue_type, metrics, context)
        
        # 2. Determine Severity & Priority based on Risk
        severity, priority = self._categorize_risk(risk_score)
        
        # 3. Predict Logistics (Cost/Time)
        # Use ML for potholes, Heuristics for others
        if issue_type == "pothole" and self.ml_ready:
            logistics = self._predict_ml_logistics(metrics, context)
        else:
            logistics = self._estimate_heuristic_logistics(issue_type, metrics, risk_score)
            
        # 4. Synthesize Recommendation
        action = self._recommend_action(priority, issue_type)
        
        # 5. Generate Explanation
        explanation = self._generate_explanation(issue_type, risk_score, priority, context)
        
        # 6. Confidence Score (Prototype logic)
        confidence = self._calculate_confidence(risk_score, logistics)
        
        return {
            "issue_type": issue_type,
            "severity": severity,
            "priority": priority,
            "risk_score": round(risk_score, 1),
            "recommended_action": action,
            "estimated_cost": logistics["cost"],
            "repair_time_days": logistics["time"],
            "confidence_score": confidence,
            "decision_explanation": explanation
        }

    def _calculate_risk_score(self, issue_type, metrics, context):
        """Computes a weighted risk score based on physics and context."""
        weights = RISK_WEIGHTS.get(issue_type, RISK_WEIGHTS["pothole"])
        
        # Normalized Factors (0-10 roughly)
        
        # Scale Factor
        scale_score = 0
        if issue_type == "pothole":
            # Cap area impact at ~50m2
            scale_score = min(metrics.get('area', 0) / 5.0, 10.0) 
        elif issue_type == "garbage":
            scale_score = min(metrics.get('volume', 0) / 10.0, 10.0)
            
        # Exposure Factor
        t_mult = TRAFFIC_MULTIPLIERS.get(context.get('traffic_level'), 1.0)
        r_mult = ROAD_MULTIPLIERS.get(context.get('road_type'), 1.0)
        exposure_score = min(t_mult * r_mult * 2.5, 10.0)
        
        # Safety Factor (Inherent to issue + Context)
        safety_base = 5.0
        if context.get('traffic_level') == "High" and issue_type == "pothole":
            safety_base = 9.0 # High speed road pothole = deadly
        safety_score = safety_base

        # Composite Weighted Sum (Max ~10)
        raw_score = (
            (safety_score * weights["safety"]) +
            (exposure_score * weights["exposure"]) +
            (scale_score * weights["scale"])
        )
        
        # Scale to 0-100
        final_score = min(raw_score * 10, 100)
        return final_score

    def _categorize_risk(self, score):
        if score >= 80: return "High", "Critical"
        if score >= 60: return "High", "High"
        if score >= 40: return "Medium", "Medium"
        return "Low", "Low"

    def _predict_ml_logistics(self, metrics, context):
        # Prepare Input Vector
        input_data = {
            "damaged_area_m2": metrics.get('area', 0),
            "road_type": context.get('road_type', 'Residential'),
            "traffic_level": context.get('traffic_level', 'Low')
        }
        
        df = pd.DataFrame([input_data])
        X = pd.get_dummies(df).reindex(columns=self.feature_columns, fill_value=0)
        
        cost = self.models["cost"].predict(X)[0]
        time = self.models["time"].predict(X)[0]
        
        return {"cost": int(cost), "time": int(time)}

    def _estimate_heuristic_logistics(self, issue_type, metrics, risk_score):
        # Fallback for non-ML issues
        base_cost = 500
        base_time = 1
        
        if issue_type == "garbage":
            base_cost = 200 * (metrics.get('volume', 1) * 0.5)
            base_time = 1
        elif issue_type == "street_light":
            base_cost = 2000
            base_time = 2
            
        # Risk Multiplier
        multiplier = 1 + (risk_score / 100)
        
        return {
            "cost": int(base_cost * multiplier), 
            "time": int(base_time * multiplier)
        }

    def _recommend_action(self, priority, issue_type):
        if issue_type == "pothole":
            if priority == "Critical": return "🚧 CLOSE LANE & REPAIR ASAP. Cold-patch immediately."
            if priority == "High": return "Schedule specialized repair crew (Hot Mix) within 48h."
            if priority == "Medium": return "Queue for weekly neighborhood patching."
            return "Monitor for expansion. No immediate action."
        
        return ACTION_MATRIX.get(priority, "Inspect and report.")

    def _generate_explanation(self, issue_type, risk_score, priority, context):
        reason = ""
        if context.get('road_type') == "Highway" and priority in ["Critical", "High"]:
            reason = "High-speed corridor detected. "
        elif context.get('traffic_level') == "High":
            reason = "High traffic volume increases accident probability. "
            
        return (
            f"Risk Score {risk_score}/100 ({priority}). {reason}"
            f"Automated assessment based on {issue_type} severity and {context.get('road_type')} guidelines."
        )

    def _calculate_confidence(self, risk_score, logistics):
        # Mock confidence metric
        # Real systems would use model probability + outlier detection
        base_conf = 0.85
        if risk_score > 90 or risk_score < 10: base_conf += 0.1 # Clear cut cases
        return min(base_conf, 0.99)

# ---------------------------------------------------------
# INSTANCE & EXPORT WRAPPER
# ---------------------------------------------------------

agent = CivicAgent()

def agent_decision(damaged_area_m2, road_type, traffic_level, issue_type="pothole"):
    """
    Wrapper function to maintain backward compatibility with app.py/backend
    while utilizing the new CivicAgent class.
    """
    
    metrics = {"area": damaged_area_m2}
    context = {"road_type": road_type, "traffic_level": traffic_level}
    
    decision = agent.decide(issue_type, metrics, context)
    
    # Map to simpler format expected by current frontend/backend contract
    # But adding the new fields too (Frontend will just ignore them if not updated, 
    # but Backend passes generic dict so it will go through!)
    return {
    "damaged_area_m2": damaged_area_m2,
    "severity": decision["severity"],
    "priority": decision["priority"],

    # KEEP NUMERIC — DO NOT FORMAT HERE
    "estimated_cost": decision["estimated_cost"],
    "repair_time_days": decision["repair_time_days"],

    # ADVANCED FIELDS
    "risk_score": decision["risk_score"],
    "recommended_action": decision["recommended_action"],
    "confidence_score": decision["confidence_score"],
    "decision_explanation": decision["decision_explanation"]
}

