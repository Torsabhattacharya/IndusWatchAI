
from kafka import KafkaConsumer, KafkaProducer
import json
import logging
from datetime import datetime
import sys
import os

# Add ml-service to path
sys.path.insert(0, 'C:/IndusWatchAI/ml-service')

try:
    from ml_predictor import MLPredictor
    ML_AVAILABLE = True
    logging.info("✅ ML Predictor loaded")
except ImportError as e:
    ML_AVAILABLE = False
    logging.warning(f"⚠️ ML Predictor not available: {e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SensorDataConsumer:
    def __init__(self, bootstrap_servers='localhost:9092', topic='sensor-data'):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.consumer = None
        self.producer = None
        self.ml_predictor = None
        
        if ML_AVAILABLE:
            self.ml_predictor = MLPredictor()
        
    def connect(self):
        try:
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id='processing-group',
                auto_offset_reset='latest',
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            logger.info(f"✅ Connected to Kafka topic: {self.topic}")
            
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
            )
            logger.info(f"✅ Connected to Kafka producer")
            
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    def predict_risk(self, data):
        """Get ML prediction or fallback to simple risk"""
        if self.ml_predictor:
            return self.ml_predictor.predict(data)
        else:
            # Fallback: use failure_risk from sensor
            return data.get('failure_risk', 0)
    
    def start(self):
        if not self.connect():
            return
        
        logger.info("🚀 Starting consumer with ML model..." if self.ml_predictor else "🚀 Starting consumer (ML disabled)...")
        
        try:
            for message in self.consumer:
                data = message.value
                
                # Get prediction
                ml_probability = self.predict_risk(data)
                
                # Determine risk level
                if ml_probability > 0.8:
                    risk_level = "CRITICAL"
                elif ml_probability > 0.6:
                    risk_level = "HIGH"
                elif ml_probability > 0.4:
                    risk_level = "MEDIUM"
                else:
                    risk_level = "LOW"
                
                logger.info(f"📨 {data.get('machine_id')} - ML Prediction: {ml_probability:.1%} ({risk_level})")
                
                # Send to predictions topic
                prediction_data = {
                    "machine_id": data.get('machine_id'),
                    "timestamp": datetime.utcnow().isoformat(),
                    "failure_probability": ml_probability,
                    "risk_level": risk_level,
                    "predicted_failure_hours": 1 if risk_level == "CRITICAL" else (4 if risk_level == "HIGH" else 12),
                    "alert_message": f"ML Model predicts {risk_level} risk ({ml_probability:.1%})"
                }
                
                self.producer.send('predictions', value=prediction_data)
                
        except KeyboardInterrupt:
            logger.info("Stopping...")
        finally:
            if self.consumer:
                self.consumer.close()
            if self.producer:
                self.producer.close()

if __name__ == "__main__":
    consumer = SensorDataConsumer()
    consumer.start()
