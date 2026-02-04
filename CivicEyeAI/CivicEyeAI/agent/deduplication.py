import math
from datetime import datetime, timedelta
import imagehash
from PIL import Image

class DuplicateDetector:
    def __init__(self):
        # In-memory indices for prototype simplicity
        # In production: Use Redis (Geo) or PostgreSQL (PostGIS)
        self.spatial_index = [] 
        self.image_hashes = {} 

    def check(self, new_report):
        """
        Main check function.
        Args:
            new_report (dict): {
                'lat': float, 'lon': float, 
                'image': PIL.Image object, 
                'issue_type': str,
                'user_id': str
            }
        Returns:
            (status, reason, merged_id)
            status: 'New', 'Duplicate', 'Suspicious'
        """
        
        # 1. VISUAL CHECK (Exact or Near-Exact Image Match)
        # Prevents users downloading someone else's photo and re-uploading
        if new_report.get('image'):
            # Calculate perceptual hash (resistant to resizing/compression)
            p_hash = str(imagehash.phash(new_report['image']))
            
            # Simple Hamming distance check against DB
            for existing_hash, existing_id in self.image_hashes.items():
                if self._hamming_distance(p_hash, existing_hash) <= 5: # Threshold for similarity
                    return "Suspicious", f"Image visually identical to report {existing_id}", existing_id
            
            # Store hash if valid later (logic handled by caller usually, but simulating here)
            # In a real flow, we only store AFTER verification. 
            # Ideally this check happens first.

        # 2. SPATIAL-TEMPORAL CHECK
        lat = new_report['lat']
        lon = new_report['lon']
        issue = new_report['issue_type']
        
        curr_time = datetime.now()
        
        for record in self.spatial_index:
            # Filter by Issue Type
            if record['issue_type'] != issue:
                continue
                
            # Filter by Time (e.g., 24h window)
            time_diff = (curr_time - record['timestamp']).total_seconds() / 3600
            if time_diff > 24:
                continue
            
            # Check Distance
            dist = self._haversine(lat, lon, record['lat'], record['lon'])
            
            if dist < 15.0: # 15 meters
                return "Duplicate", f"Similar issue reported {dist:.1f}m away at {record['timestamp'].strftime('%H:%M')}", record['id']

        return "New", "No matches found.", None

    def register_report(self, report_id, report_data):
        """
        Adds a verified report to the index.
        """
        entry = {
            "id": report_id,
            "lat": report_data['lat'],
            "lon": report_data['lon'],
            "issue_type": report_data['issue_type'],
            "timestamp": datetime.now()
        }
        self.spatial_index.append(entry)
        
        if report_data.get('image'):
            p_hash = str(imagehash.phash(report_data['image']))
            self.image_hashes[p_hash] = report_id

    # --- Utils ---

    def _haversine(self, lat1, lon1, lat2, lon2):
        R = 6371000  # meters
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        
        a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

    def _hamming_distance(self, s1, s2):
        if len(s1) != len(s2):
            return float("inf")
        return sum(c1 != c2 for c1, c2 in zip(s1, s2))

# Singleton
deduplicator = DuplicateDetector()
