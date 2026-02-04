
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
from datetime import datetime

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmailDispatcher:
    def __init__(self):
        # Configuration - In production these come from os.environ
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.sender_email = os.getenv("SENDER_EMAIL", "alert@civic-eye.ai")
        self.sender_password = os.getenv("SENDER_PASSWORD", "mock_password")
        
        # Real department emails (Mocked for dev)
        self.dept_contacts = {
            "pothole": "roads@municipality.gov.in",
            "street_light": "electric@municipality.gov.in",
            "garbage": "sanity@municipality.gov.in",
            "admin": "admin@civic-eye.ai"
        }

    def dispatch_work_order(self, work_order_data, recipient_override=None):
        """
        Sends an email with the work order draft.
        Returns: { "status": "sent" | "failed" | "mocked", "msg": ... }
        """
        
        # 1. Validate Eligibility
        # Only draft generated for high/critical are passed here theoretically, 
        # but let's double check if WO exists
        if not work_order_data or "work_order_id" not in work_order_data:
            logger.warning("Attempted to dispatch invalid work order.")
            return {"status": "failed", "msg": "Invalid work order data"}

        # 2. Determine Recipient
        # Extract issue type from text or structured data
        # For simplicity, assuming caller passes the issue_type or we infer it
        # Let's check structured data first
        specs = work_order_data.get('pdf_data', {}).get('technical_specs', {})
        issue_type_raw = specs.get('issue_type', 'pothole').lower()
        
        # Map back from Title Case if needed
        if "pothole" in issue_type_raw: issue_key = "pothole"
        elif "light" in issue_type_raw: issue_key = "street_light"
        elif "garbage" in issue_type_raw: issue_key = "garbage"
        else: issue_key = "admin"

        recipient = recipient_override if recipient_override else self.dept_contacts.get(issue_key, self.dept_contacts["admin"])

        # 3. Construct Email
        wo_id = work_order_data['work_order_id']
        subject = f"ACTION REQUIRED: Work Order {wo_id} - High Priority Alert"
        
        body_text = work_order_data['text_preview']
        
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body_text, 'plain'))

        # 4. Send (with Mock Mode fallback)
        try:
            # Check if we are in a real sending environment
            if self.sender_password == "mock_password":
                # Simulate success for dev/hackathon without crashing
                logger.info(f"[MOCK EMAIL] To: {recipient} | Subject: {subject}")
                self._log_dispatch(wo_id, recipient, "MOCKED_SUCCESS")
                return {"status": "mocked", "msg": f"Email simulated to {recipient}"}
            
            # Real Send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {recipient}")
            self._log_dispatch(wo_id, recipient, "SENT")
            return {"status": "sent", "msg": f"Email sent to {recipient}"}

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            self._log_dispatch(wo_id, recipient, f"FAILED: {str(e)}")
            return {"status": "failed", "msg": str(e)}

    def _log_dispatch(self, wo_id, recipient, status):
        """
        Audit log for accountability.
        """
        # In prod: Write to database audit_logs table
        # Here: Print is sufficient as it goes to system logs
        print(f"AUDIT_LOG: {datetime.now()} | DISPATCH | {wo_id} | {recipient} | {status}")

# Singleton
dispatcher = EmailDispatcher()
