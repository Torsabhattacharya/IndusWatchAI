from kafka import KafkaProducer
import json
import logging
from typing import Dict, Any
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class SensorDataProducer:
    """Kafka producer for sensor data"""
    
    def __init__(self, bootstrap_servers: str = 'localhost:9092', topic: str = 'sensor-data'):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer = None
        self.connect()
        
    def connect(self):
        """Connect to Kafka with retry mechanism"""
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                    acks='all',  # Wait for all replicas
                    retries=3,
                    max_in_flight_requests_per_connection=5,
                    compression_type='gzip'
                )
                logger.info(f"✅ Connected to Kafka at {self.bootstrap_servers}")
                return True
            except Exception as e:
                logger.warning(f"⚠️ Kafka connection attempt {attempt+1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    
        logger.error("❌ Failed to connect to Kafka after all retries")
        return False
    
    def send_sensor_data(self, sensor_data: Dict[str, Any]) -> bool:
        """Send sensor data to Kafka topic"""
        if not self.producer:
            logger.error("Kafka producer not connected")
            return False
            
        try:
            # Add processing timestamp
            sensor_data['kafka_timestamp'] = datetime.utcnow().isoformat()
            
            # Send to Kafka
            future = self.producer.send(self.topic, value=sensor_data)
            result = future.get(timeout=10)
            
            logger.debug(f"✅ Data sent to Kafka: Partition={result.partition}, Offset={result.offset}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send to Kafka: {e}")
            return False
    
    def close(self):
        """Close Kafka connection"""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logger.info("Kafka producer closed")