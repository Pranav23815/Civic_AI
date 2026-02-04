
from datetime import datetime
import math

class RewardSystem:
    def __init__(self):
        # Mock database structure
        self.users = {}      # { user_id: { "trust_score": float, "total_points": int } }
        self.rewards = []    # List of reward transactions
        self.reports = {}    # { report_id: { "status": str, "user_id": str } }

    def calculate_points(self, report_data):
        """
        Calculate points based on report significance.
        Args:
            report_data (dict): Contains 'issue_type', 'risk_score', 'priority', 'is_unique'
        Returns:
            int: Calculated points
        """
        base_points = 10
        
        # Priority Multiplier
        priority_mult = {
            "Critical": 3.0,
            "High": 2.0,
            "Medium": 1.5,
            "Low": 1.0
        }
        
        # Risk Score Bonus
        risk_bonus = report_data.get('risk_score', 0) * 0.5  # Max 50 points
        
        # Issue Type Base
        type_base = {
            "pothole": 20,
            "street_light": 15,
            "garbage": 10
        }
        
        points = (type_base.get(report_data['issue_type'], 10) * 
                 priority_mult.get(report_data['priority'], 1.0)) + \
                 base_points + risk_bonus
                 
        # Uniqueness Check - First reporter gets full points, others get minimal
        if not report_data.get('is_unique', True):
            points = points * 0.1  # 10% confirmation bonus
            
        return int(points)

    def process_reward(self, user_id, report_id, report_data):
        """
        Main logic to assign rewards and update trust score.
        Expected to be called AFTER report verification.
        """
        
        # 1. Initialize User if new
        if user_id not in self.users:
            self.users[user_id] = {"trust_score": 50.0, "total_points": 0} # Start neutral
            
        user = self.users[user_id]
        
        # 2. Prevent Double Dipping
        if self._is_already_rewarded(report_id):
            return {"status": "skipped", "reason": "Already rewarded"}

        # 3. Calculate Points
        points = self.calculate_points(report_data)
        
        # 4. Update Trust Score
        # Verification Status impacts trust
        verification_status = report_data.get('verification_status', 'manual_review')
        
        trust_delta = 0
        if verification_status in ['auto_verified', 'manual_verified']:
             trust_delta = 2.0  # +2 for valid report
             if report_data.get('priority') == 'Critical':
                 trust_delta += 1.0 # Bonus for critical
        elif verification_status == 'rejected':
             trust_delta = -5.0 # Penalty for rejection
             points = 0 # No points for rejected
        
        user['trust_score'] = max(0, min(100, user['trust_score'] + trust_delta))
        user['total_points'] += points
        
        # 5. Log Transaction
        transaction = {
            "tx_id": f"tx_{datetime.now().timestamp()}",
            "user_id": user_id,
            "report_id": report_id,
            "points": points,
            "trust_delta": trust_delta,
            "timestamp": datetime.now()
        }
        self.rewards.append(transaction)
        
        return {
            "status": "success",
            "points_awarded": points,
            "new_trust_score": user['trust_score'],
            "new_total_balance": user['total_points']
        }

    def _is_already_rewarded(self, report_id):
        for tx in self.rewards:
            if tx['report_id'] == report_id:
                return True
        return False

# Singleton
reward_engine = RewardSystem()
