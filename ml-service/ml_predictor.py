import joblib
import numpy as np
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLPredictor:
    def __init__(self):
        self.model = None
        self.model_path = "C:/IndusWatchAI/ml-service/models/failure_model.pkl"
        self.load_model()
    
    def load_model(self):
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
            logger.info("✅ ML Model loaded successfully")
        else:
            logger.warning("⚠️ Model not found. Run train_model.py first")
    
    def predict(self, sensor_data):
        if self.model is None:
            return self._fallback_predict(sensor_data)
        
        features = np.array([[
            sensor_data.get('temperature', 75),
            sensor_data.get('vibration', 0.4),
            sensor_data.get('pressure', 100),
            sensor_data.get('rpm', 1500)
        ]])
        
        probability = self.model.predict_proba(features)[0][1]
        return round(float(probability), 3)
    
    def _fallback_predict(self, sensor_data):
        risk = sensor_data.get('failure_risk', 0)
        return round(risk, 3)
