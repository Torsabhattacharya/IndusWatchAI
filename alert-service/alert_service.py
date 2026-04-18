import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
from kafka import KafkaConsumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlertService:
    def __init__(self):
        # Email configuration (update with your email)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "your-email@gmail.com"  # Update this
        self.sender_password = "your-password"       # Update this
        self.alert_email = "maintenance@factory.com"  # Update this
        
        # SMS configuration (Twilio - optional)
        self.sms_enabled = False
        
    def send_email_alert(self, machine_id, risk_level, message):
        """Send email alert"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.alert_email
            msg['Subject'] = f"⚠️ INDUSTRIAL ALERT - {machine_id} - {risk_level}"
            
            body = f"""
            INDUSTRIAL FAILURE ALERT SYSTEM
            
            Machine: {machine_id}
            Risk Level: {risk_level}
            Time: {datetime.now()}
            
            Alert: {message}
            
            Action Required: Immediate attention needed.
            
            IndusWatchAI System
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Uncomment to actually send email
            # server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            # server.starttls()
            # server.login(self.sender_email, self.sender_password)
            # server.send_message(msg)
            # server.quit()
            
            logger.info(f"📧 EMAIL ALERT: {machine_id} - {risk_level}")
            return True
            
        except Exception as e:
            logger.error(f"Email failed: {e}")
            return False
    
    def send_sms_alert(self, phone_number, message):
        """Send SMS alert via Twilio"""
        if not self.sms_enabled:
            logger.info(f"📱 SMS would send to {phone_number}: {message[:50]}")
            return True
        return False
    
    def process_alert(self, prediction):
        """Process alert from prediction"""
        machine_id = prediction.get('machine_id')
        risk_level = prediction.get('risk_level', 'LOW')
        failure_prob = prediction.get('failure_probability', 0)
        message = prediction.get('alert_message', f'Failure probability: {failure_prob:.1%}')
        
        if risk_level in ['HIGH', 'CRITICAL']:
            # Send email
            self.send_email_alert(machine_id, risk_level, message)
            
            # Send SMS for CRITICAL
            if risk_level == 'CRITICAL':
                self.send_sms_alert("+1234567890", f"CRITICAL: {machine_id} - {message[:50]}")
            
            # Save to database
            self.save_alert_to_db(machine_id, risk_level, message)
            
            logger.warning(f"🚨 ALERT TRIGGERED: {machine_id} - {risk_level} - {message}")
        
        return True
    
    def save_alert_to_db(self, machine_id, severity, message):
        """Save alert to PostgreSQL"""
        try:
            import psycopg2
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="induswatchai",
                user="postgres",
                password="torsa"
            )
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO alerts (machine_id, severity, message, timestamp, acknowledged)
                VALUES (%s, %s, %s, %s, %s)
            """, (machine_id, severity, message, datetime.now(), False))
            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f"💾 Alert saved to database: {machine_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save alert: {e}")
            return False

class AlertConsumer:
    def __init__(self):
        self.alert_service = AlertService()
        self.consumer = None
        
    def connect(self):
        try:
            self.consumer = KafkaConsumer(
                'predictions',
                bootstrap_servers='localhost:9092',
                group_id='alert-group',
                auto_offset_reset='latest',
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            logger.info("✅ Alert consumer connected to Kafka")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    def start(self):
        if not self.connect():
            return
        
        logger.info("🚀 Alert consumer started. Waiting for predictions...")
        
        try:
            for message in self.consumer:
                prediction = message.value
                logger.info(f"📨 Received prediction for {prediction.get('machine_id')}")
                self.alert_service.process_alert(prediction)
                
        except KeyboardInterrupt:
            logger.info("Stopping alert consumer...")
        finally:
            if self.consumer:
                self.consumer.close()

if __name__ == "__main__":
    consumer = AlertConsumer()
    consumer.start()
