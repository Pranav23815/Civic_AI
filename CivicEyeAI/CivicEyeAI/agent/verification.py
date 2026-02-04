import uuid
from datetime import datetime, timedelta
import math

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
THRESHOLDS = {
    "vision_confidence_min": 0.40,       # Below this = Rejected
    "vision_confidence_auto": 0.75,      # Above this = Candidate for Auto
    "agent_confidence_min": 0.60,        # Below this = Manual Review
    "critical_risk_flag": 85.0,          # Risk above this = Force Manual Review (Safety)
    "duplicate_distance_meters": 15.0,   # Radius to check for duplicates
    "duplicate_time_window_hours": 24    # Time window for duplicates
}

class VerificationEngine:
    def __init__(self):
        # In a real system, this would be a Redis or PostGIS database connection.
        # Storing structure: { "id": str, "lat": float, "lon": float, "time": datetime }
        self._mock_report_db = []

    def verify_submission(self, vision_metadata, agent_result, location_data):
        """
        Main pipeline to verify a citizen infrastructure report.
        
        Args:
            vision_metadata (dict): {"box_confidence": float, "class": str}
            agent_result (dict): Output from CivicAgent (risk_score, etc.)
            location_data (dict): {"lat": float, "lon": float} (Mock for now)
        
        Returns:
            dict: Verification Object
        """
        
        report_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        # 1. Vision Confidence Check
        vis_conf = vision_metadata.get("box_confidence", 0.0)
        if vis_conf < THRESHOLDS["vision_confidence_min"]:
            return self._build_response(report_id, False, "rejected", 
                f"Vision confidence too low ({vis_conf:.2f}). Please retake photo.")

        # 2. Duplicate Detection
        is_duplicate, original_id = self._check_duplicate(location_data, timestamp)
        if is_duplicate:
            # We accept it but flag it as a duplicate linked to original
            return self._build_response(report_id, True, "auto_merged", 
                f"Duplicate of report {original_id}. Votes consolidated.")

        # 3. Agent Confidence & Risk Check
        agent_conf = agent_result.get("confidence_score", 0.0)
        risk_score = agent_result.get("risk_score", 0.0)
        
        # 4. Status Determination logic
        status = "manual_review" # Default safe state
        reason = "Standard verification flow."
        
        if risk_score >= THRESHOLDS["critical_risk_flag"]:
            # Critical issues must be human-verified before dispatching emergency crews
            status = "manual_review"
            reason = f"High Risk Score ({risk_score}) requires human safety validation."
            
        elif vis_conf >= THRESHOLDS["vision_confidence_auto"] and agent_conf >= THRESHOLDS["agent_confidence_min"]:
            # High confidence on all fronts
            status = "auto_verified"
            reason = "High confidence AI detection. Auto-approved."
            
        else:
            # Marginal cases
            status = "manual_review"
            reason = f"Moderate confidence (Vision: {vis_conf:.2f}, Agent: {agent_conf:.2f})."

        # Cache valid report for future duplicate checking
        if status in ["auto_verified", "manual_review"]:
            self._cache_report(report_id, location_data, timestamp)

        return self._build_response(report_id, True, status, reason)

    # ---------------------------------------------------------
    # UTILITIES
    # ---------------------------------------------------------

    def _build_response(self, r_id, is_ver, status, reason):
        return {
            "report_id": r_id,
            "is_verified": is_ver,
            "verification_status": status,
            "verification_reason": reason,
            "timestamp": datetime.now().isoformat()
        }

    def _check_duplicate(self, loc, current_time):
        """
        Checks if a similar report exists within radius and time window.
        """
        if not loc or "lat" not in loc:
            return False, None

        current_lat = loc["lat"]
        current_lon = loc["lon"]

        for report in self._mock_report_db:
            # Time check
            time_diff = current_time - report["time"]
            if time_diff > timedelta(hours=THRESHOLDS["duplicate_time_window_hours"]):
                continue # Too old to be a duplicate
            
            # Distance check (Haversine approx for short distances)
            dist = self._haversine_distance(current_lat, current_lon, report["lat"], report["lon"])
            if dist <= THRESHOLDS["duplicate_distance_meters"]:
                return True, report["id"]
        
        return False, None

    def _cache_report(self, r_id, loc, time):
        if loc and "lat" in loc:
            self._mock_report_db.append({
                "id": r_id,
                "lat": loc["lat"],
                "lon": loc["lon"],
                "time": time
            })

    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        # Approx distance in meters
        R = 6371000 # Earth radius in meters
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

# Singleton instance
verifier = VerificationEngine()
