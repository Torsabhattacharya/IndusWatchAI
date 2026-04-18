from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from contextlib import asynccontextmanager
import logging
from datetime import datetime
from typing import List, Dict, Any
import asyncio
from collections import defaultdict
from database import db

from models import SensorData, PredictionResult, Alert
from kafka_producer import SensorDataProducer
from auth import authenticate_user, create_access_token, verify_token

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST, CollectorRegistry

# Create new registry to avoid duplication
registry = CollectorRegistry()

# Metrics with custom registry
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'], registry=registry)
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', registry=registry)

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

@app.post("/token")
async def login(username: str, password: str):
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/protected")
async def protected_route(payload = Depends(verify_token)):
    return {"message": "Access granted", "user": payload}

@app.post("/sensor-data")
async def receive_sensor_data(
    sensor_data: SensorData,
    background_tasks: BackgroundTasks
):
    """Receive sensor data from IoT devices"""
    global request_counter
    
    try:
        request_counter += 1
        
        # Update Prometheus metrics
        REQUEST_COUNT.labels(method="POST", endpoint="/sensor-data").inc()
        
        # Log receipt
        logger.info(f"📡 Received data from {sensor_data.machine_id} - Health: {sensor_data.health_score}%")
        
        # Store in buffer for metrics
        sensor_buffer[sensor_data.machine_id].append(sensor_data)
        
        # Send to Kafka asynchronously
        background_tasks.add_task(
            kafka_producer.send_sensor_data,
            sensor_data.dict()
        )
        
        # Save to database
        background_tasks.add_task(
            db.save_sensor_data,
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
    REQUEST_COUNT.labels(method="GET", endpoint="/health").inc()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "kafka_connected": kafka_producer.producer is not None if kafka_producer else False,
        "total_requests": request_counter
    }

@app.get("/metrics")
async def get_metrics():
    """Get system metrics (custom)"""
    REQUEST_COUNT.labels(method="GET", endpoint="/metrics").inc()
    return {
        "total_requests": request_counter,
        "active_machines": len(sensor_buffer),
        "kafka_status": "connected" if kafka_producer and kafka_producer.producer else "disconnected",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/prometheus-metrics")
async def get_prometheus_metrics():
    """Get Prometheus format metrics"""
    return Response(content=generate_latest(registry), media_type=CONTENT_TYPE_LATEST)

@app.get("/sensor-history")
async def get_sensor_history(limit: int = 50):
    """Get real sensor data from database"""
    REQUEST_COUNT.labels(method="GET", endpoint="/sensor-history").inc()
    try:
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT machine_id, temperature, vibration, pressure, timestamp 
            FROM sensor_data 
            ORDER BY id DESC 
            LIMIT %s
        """, (limit,))
        rows = cursor.fetchall()
        cursor.close()
        
        # Format for chart
        history = []
        for row in rows:
            history.append({
                "time": row[4].strftime("%H:%M:%S") if row[4] else "",
                "temperature": row[1],
                "vibration": row[2],
                "pressure": row[3],
                "machine_id": row[0]
            })
        
        return {"history": history[::-1]}  # Reverse to show chronological order
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        return {"history": []}

@app.get("/alerts")
async def get_alerts(limit: int = 20):
    """Get recent alerts from database"""
    REQUEST_COUNT.labels(method="GET", endpoint="/alerts").inc()
    try:
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT id, machine_id, severity, message, timestamp, acknowledged
            FROM alerts 
            ORDER BY id DESC 
            LIMIT %s
        """, (limit,))
        rows = cursor.fetchall()
        cursor.close()
        
        alerts = []
        for row in rows:
            alerts.append({
                "id": row[0],
                "machine_id": row[1],
                "severity": row[2],
                "message": row[3],
                "timestamp": row[4].isoformat() if row[4] else "",
                "acknowledged": row[5]
            })
        
        return {"alerts": alerts}
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        return {"alerts": []}

@app.post("/batch-sensor-data")
async def receive_batch_sensor_data(
    sensor_data_list: List[SensorData],
    background_tasks: BackgroundTasks
):
    """Receive batch sensor data (for high throughput)"""
    REQUEST_COUNT.labels(method="POST", endpoint="/batch-sensor-data").inc()
    
    try:
        for sensor_data in sensor_data_list:
            sensor_buffer[sensor_data.machine_id].append(sensor_data)
            background_tasks.add_task(
                kafka_producer.send_sensor_data,
                sensor_data.dict()
            )
            # Save to database
            background_tasks.add_task(
                db.save_sensor_data,
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
    REQUEST_COUNT.labels(method="GET", endpoint="/machines").inc()
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