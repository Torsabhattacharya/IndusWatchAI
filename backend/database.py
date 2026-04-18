import psycopg2
from psycopg2.extras import RealDictCursor
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.conn = None
        self.connect()
    
    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="induswatchai",
                user="postgres",
                password="torsa"
            )
            logger.info("✅ Connected to PostgreSQL")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
    
    def save_sensor_data(self, data):
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO sensor_data 
                (machine_id, machine_type, timestamp, temperature, vibration, pressure, rpm, is_anomaly, failure_risk, health_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data.get('machine_id'),
                data.get('machine_type'),
                data.get('timestamp'),
                data.get('temperature'),
                data.get('vibration'),
                data.get('pressure'),
                data.get('rpm'),
                data.get('is_anomaly'),
                data.get('failure_risk'),
                data.get('health_score')
            ))
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"Save failed: {e}")
            return False

db = Database()
