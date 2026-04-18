from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime
from typing import List, Dict, Any
import asyncio
from collections import defaultdict

from models import SensorData, PredictionResult, Alert
from kafka_producer import SensorDataProducer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables
kafka_producer = None
sensor_buffer = defaultdict(list)  # Temporary buffer for metrics
request_counter = 0

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global kafka_producer
    
    # Startup
    logger.info("🚀 Starting IndusWatchAI Backend API...")
    
    # Initialize Kafka producer
    kafka_producer = SensorDataProducer(
        bootstrap_servers='localhost:9092',
        topic='sensor-data'
    )
    
    # Start background metrics collector
    asyncio.create_task(metrics_collector())
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down...")
    if kafka_producer:
        kafka_producer.close()

# Create FastAPI app
app = FastAPI(
    title="IndusWatchAI API",
    description="Industrial Failure Prediction System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics collector
async def metrics_collector():
    """Collect and log metrics every minute"""
    while True:
        await asyncio.sleep(60)
        if sensor_buffer:
            total_readings = sum(len(readings) for readings in sensor_buffer.values())
            logger.info(f"📊 Metrics: Total readings in last minute: {total_readings}, Active machines: {len(sensor_buffer)}")
            sensor_buffer.clear()

# API Endpoints

@app.post("/sensor-data")
async def receive_sensor_data(
    sensor_data: SensorData,
    background_tasks: BackgroundTasks
):
    """Receive sensor data from IoT devices"""
    global request_counter
    
    try:
        request_counter += 1
        
        # Log receipt
        logger.info(f"📡 Received data from {sensor_data.machine_id} - Health: {sensor_data.health_score}%")
        
        # Store in buffer for metrics
        sensor_buffer[sensor_data.machine_id].append(sensor_data)
        
        # Send to Kafka asynchronously
        background_tasks.add_task(
            kafka_producer.send_sensor_data,
            sensor_data.dict()
        )
        
        # Return immediate acknowledgment
        return {
            "status": "success",
            "message": "Data received and queued",
            "request_id": request_counter,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error processing sensor data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "kafka_connected": kafka_producer.producer is not None if kafka_producer else False,
        "total_requests": request_counter
    }

@app.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    return {
        "total_requests": request_counter,
        "active_machines": len(sensor_buffer),
        "kafka_status": "connected" if kafka_producer and kafka_producer.producer else "disconnected",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/batch-sensor-data")
async def receive_batch_sensor_data(
    sensor_data_list: List[SensorData],
    background_tasks: BackgroundTasks
):
    """Receive batch sensor data (for high throughput)"""
    
    try:
        for sensor_data in sensor_data_list:
            sensor_buffer[sensor_data.machine_id].append(sensor_data)
            background_tasks.add_task(
                kafka_producer.send_sensor_data,
                sensor_data.dict()
            )
        
        return {
            "status": "success",
            "message": f"Received {len(sensor_data_list)} readings",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error processing batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/machines")
async def get_active_machines():
    """Get list of active machines"""
    return {
        "active_machines": list(sensor_buffer.keys()),
        "count": len(sensor_buffer)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )