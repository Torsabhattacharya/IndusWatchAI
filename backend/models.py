from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class MachineType(str, Enum):
    CNC = "CNC"
    PUMP = "Pump"
    CONVEYOR = "Conveyor"
    COMPRESSOR = "Compressor"
    GENERATOR = "Generator"

class SensorData(BaseModel):
    """Sensor data model"""
    machine_id: str = Field(..., example="M0001")
    machine_type: MachineType = Field(..., example="CNC")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    temperature: float = Field(..., ge=0, le=200, example=75.5)
    vibration: float = Field(..., ge=0, le=5, example=0.35)
    pressure: float = Field(..., ge=0, le=300, example=101.2)
    rpm: float = Field(..., ge=0, le=10000, example=1450)
    is_anomaly: bool = Field(default=False)
    anomaly_type: Optional[str] = Field(default=None)
    failure_risk: float = Field(default=0.0, ge=0, le=1)
    health_score: float = Field(default=100.0, ge=0, le=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "machine_id": "M0001",
                "machine_type": "CNC",
                "temperature": 75.5,
                "vibration": 0.35,
                "pressure": 101.2,
                "rpm": 1450,
                "is_anomaly": False,
                "failure_risk": 0.0,
                "health_score": 100.0
            }
        }

class PredictionResult(BaseModel):
    """ML prediction result model"""
    machine_id: str
    timestamp: datetime
    failure_probability: float
    predicted_failure_in_hours: Optional[float]
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    recommended_action: str
    
class Alert(BaseModel):
    """Alert model"""
    alert_id: str
    machine_id: str
    severity: str  # INFO, WARNING, CRITICAL
    message: str
    timestamp: datetime
    acknowledged: bool = False