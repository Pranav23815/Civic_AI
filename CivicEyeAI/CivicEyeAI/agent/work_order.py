from datetime import datetime

class WorkOrderGenerator:
    def __init__(self):
        self.department_map = {
            "pothole": "Roads & Transport Department",
            "street_light": "Electrical Engineering Division",
            "garbage": "Sanitation & Waste Management"
        }
        self.disclaimer = (
            "NOTICE: This is an automatically generated draft Work Order based on "
            "Civic-Eye AI assessment. Estimates are algorithmic. "
            "Site engineer approval required before tendering."
        )

    def generate_draft(self, report_id, location, agent_decision):
        """
        Generates a formal work order draft.
        
        Args:
            report_id (str): Unique report ID
            location (dict): { "lat", "lon", "address" }
            agent_decision (dict): { "issue_type", "severity", "priority", "recommended_action", "cost", "time", "risk_score" }
        
        Returns:
            dict: { "work_order_id", "text_content", "structured_data" }
        """
        
        # Guard clause: Only High/Critical
        if agent_decision.get('priority') not in ["High", "Critical"]:
            return None # No auto-draft for routine issues
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        issue_type = agent_decision.get('issue_type', 'maintenance').title()
        dept_name = self.department_map.get(agent_decision.get('issue_type'), "General Maintenance")
        
        work_order_id = f"WO-{datetime.now().strftime('%Y%m%d')}-{report_id[:6].upper()}"
        
        # Plain Text Template (Government Style)
        text_content = f"""MUNICIPAL CORPORATION - WORK ORDER DRAFT
------------------------------------------------------------
Order ID:       {work_order_id}
Date:           {timestamp}
Department:     {dept_name}
Subject:        URGENT REPAIR - {agent_decision.get('priority').upper()} PRIORITY

1. SITE LOCATION
   Coordinates: {location.get('lat')}, {location.get('lon')}
   Approx Addr: {location.get('address', 'N/A')}

2. ISSUE ASSESSMENT
   Type:        {issue_type}
   Severity:    {agent_decision.get('severity')}
   Risk Score:  {agent_decision.get('risk_score')}/100

3. ACTION PLAN
   Recommendation: {agent_decision.get('recommended_action')}

4. LOGISTICS ESTIMATES
   Est. Cost:   Rs. {agent_decision.get('estimated_cost')}
   Est. Time:   {agent_decision.get('repair_time_days')} Days

------------------------------------------------------------
{self.disclaimer}
------------------------------------------------------------
"""

        # Structured Data for PDF/Database
        structured_data = {
            "header": {
                "order_id": work_order_id,
                "date": timestamp,
                "department": dept_name,
                "priority_flag": agent_decision.get('priority') == "Critical"
            },
            "location": location,
            "technical_specs": {
                "issue_type": issue_type,
                "risk_score": agent_decision.get('risk_score'),
                "action_code": agent_decision.get('recommended_action')
            },
            "budget": {
                "estimated_inr": agent_decision.get('estimated_cost'),
                "contingency_fund": int(agent_decision.get('estimated_cost', 0) * 0.10) # 10% buffer
            }
        }

        return {
            "work_order_id": work_order_id,
            "text_preview": text_content,
            "pdf_data": structured_data
        }

# Singleton
drafter = WorkOrderGenerator()
