# 🏭 IndusWatchAI - Industrial IoT Failure Prediction Platform

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org)
[![Kafka](https://img.shields.io/badge/Kafka-3.6-black.svg)](https://kafka.apache.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13-blue.svg)](https://postgresql.org)
[![ML](https://img.shields.io/badge/ML-RandomForest-orange.svg)](https://scikit-learn.org)
[![JWT](https://img.shields.io/badge/JWT-Auth-red.svg)](https://jwt.io)

---

📌 Project Description

**IndusWatchAI** is a **production-grade Industrial Internet of Things (IIoT) monitoring system** that predicts machine failures in real-time using Machine Learning. Designed for manufacturing plants, factories, and industrial environments, it continuously monitors critical machine parameters (temperature, vibration, pressure, RPM) and generates instant alerts before failures occur.
The system simulates **500+ industrial machines** sending real-time sensor data, processes it through **Apache Kafka** for high-throughput message queuing, runs predictions using a **Random Forest ML model (85% accuracy)**, stores all data in **PostgreSQL**, and presents actionable insights through a **modern React TypeScript dashboard** with JWT authentication.

🎯 Key Capabilities

| Capability | Description |
|------------|-------------|
| **Real-time Monitoring** | Millisecond-level sensor data processing |
| **Predictive Maintenance** | ML-based failure prediction before breakdown |
| **Scalable Architecture** | Handles 500+ machines (architected for 1000+) |
| **Multi-machine Support** | CNC, Pump, Conveyor, Compressor, Generator types |
| **Instant Alerts** | Email/SMS ready for CRITICAL and HIGH risks |
| **Complete Observability** | Prometheus metrics + Grafana dashboards |

---
| Problem | Impact |
|---------|--------|
| **Unexpected Machine Downtime** | $50,000+ loss per hour in manufacturing |
| **Manual Monitoring Impossible** | 500+ machines can't be tracked manually |
| **Delayed Failure Detection** | Small issues become catastrophic failures |
| **No Historical Data** | Cannot analyze failure patterns |
| **Reactive Maintenance** | Fix only after breakdown, not before |
| **Data Silos** | Machine data isolated, no central view |

### The Solution
IndusWatchAI provides a **complete predictive maintenance platform** that:
1. **Continuously monitors** every machine in real-time
2. **Predicts failures** before they happen (85% accuracy)
3. **Sends instant alerts** when risk is detected
4. **Stores all data** for historical analysis
5. **Provides centralized dashboard** for complete visibility
6. **Scales horizontally** to support thousands of machines

---

## ✨ Features
### 🏗️ Architecture & Scalability
| Feature | Implementation |
|---------|---------------|
| **500+ Concurrent Machines** | Tested with 500 machines, architected for 1000+ |
| **Microservices Architecture** | Decoupled services for independent scaling |
| **Apache Kafka Queue** | 3 topics with 3 partitions each, 10,000+ msgs/sec |
| **Async Processing** | Non-blocking I/O with FastAPI |
| **Horizontal Scaling** | Add more consumers to increase throughput |

### 🤖 Machine Learning
| Feature | Value |
|---------|-------|
| **Algorithm** | Random Forest Classifier |
| **Training Data** | 10,000+ synthetic samples |
| **Accuracy** | 85.2% |
| **Precision** | 0.84 |
| **Recall** | 0.86 |
| **F1-Score** | 0.85 |
| **Inference Time** | <10ms per prediction |
| **Feature Importance** | Temperature (32%), Vibration (28%), Pressure (22%), RPM (18%) |

### 📡 Real-time Dashboard

| Feature | Description |
|---------|-------------|
| **Live Sensor Data** | Temperature, vibration, pressure, RPM in real-time |
| **Machine Status** | All machines with types and health scores |
| **Alert System** | Severity-based alerts (CRITICAL/HIGH/MEDIUM/LOW) |
| **Analytics** | Risk distribution, machine type distribution |
| **System Health** | Kafka, PostgreSQL, ML model status |
| **Dark Theme** | Professional black/violet/deep blue UI |
| **Auto-refresh** | Updates every 5 seconds |

### 🔐 Security

| Feature | Implementation |
|---------|----------------|
| **JWT Authentication** | Bearer token-based auth |
| **Login System** | Secure login page with form validation |
| **Protected Routes** | Dashboard accessible only after login |
| **Token Storage** | Local storage with automatic session management |
| **Logout Functionality** | Clear token and redirect to login |
| **Role-based Access** | Admin and operator roles (extensible) |

### 📊 Data Pipeline

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Data Ingestion** | FastAPI | REST API for sensor data |
| **Message Queue** | Apache Kafka | Async, fault-tolerant message processing |
| **Stream Processing** | Python Consumer | Feature extraction, risk calculation |
| **ML Inference** | Scikit-learn | Real-time failure prediction |
| **Storage** | PostgreSQL | Persistent storage (3 tables) |
| **Alerting** | SMTP/Twilio | Email and SMS notifications |

### 📈 Monitoring & Observability

| Tool | Purpose | Endpoint |
|------|---------|----------|
| **Prometheus** | Metrics collection | `/prometheus-metrics` |
| **Grafana** | Visualization dashboard | `http://localhost:3001` |
| **Health Check** | Service status | `/health` |
| **Custom Metrics** | Request counts, latency | `/metrics` |

### 🐳 DevOps Ready

| Feature | Implementation |
|---------|----------------|
| **Containerization** | Dockerfile for each service |
| **Orchestration** | Kubernetes deployment ready |
| **Docker Compose** | One-command local setup |
| **CI/CD Ready** | GitHub Actions compatible |
| **Environment Config** | `.env` file support |

---
🏗️ System Architecture:
         IoT Sensors (Simulator) → FastAPI → Kafka → Consumer → ML Model → PostgreSQL
                                ↓
                         Alert Service
                                ↓
                         React Dashboard


📁 Project Structure:
IndusWatchAI/
├── backend/                    # FastAPI application
│   ├── main.py                # Main API server (JWT + endpoints)
│   ├── database.py            # PostgreSQL connection
│   ├── auth.py                # JWT authentication logic
│   ├── models.py              # Pydantic data models
│   └── kafka_producer.py      # Kafka producer
│
├── frontend/                   # React TypeScript dashboard
│   ├── src/
│   │   ├── components/
│   │   │   ├── Login.tsx      # Login page component
│   │   │   └── UnifiedDashboard.tsx  # Main dashboard
│   │   ├── services/
│   │   │   └── api.ts         # API service layer
│   │   └── App.tsx            # Root component (auth logic)
│   └── package.json
│
├── processing-service/         # Kafka consumer
│   └── consumer.py            # Message processor with ML
│
├── alert-service/              # Alert system
│   └── alert_service.py       # Email/SMS alerts
│
├── ml-service/                 # Machine Learning
│   ├── train_model.py         # Model training script
│   ├── ml_predictor.py        # Prediction service
│   └── models/                # Saved models
│
├── simulator/                  # IoT sensor simulator
│   └── iot_simulator.py       # Generates fake sensor data
│
├── docker/                     # Docker configurations
│   └── docker-compose.yml
│
├── start_all_500.bat          # One-click startup (500 machines)
├── start_all_1000.bat         # One-click startup (1000 machines)
├── requirements.txt           # Python dependencies
└── README.md                  # This file


## 🔐 Default Login Credentials

| Username | Password |
|----------|----------|
| **admin** | **admin123** 



## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.11
- **Message Queue**: Apache Kafka, Zookeeper  
- **Database**: PostgreSQL 
- **ML Model**: Scikit-learn (Random Forest, 85% accuracy)
- **Frontend**: React 18, TypeScript, Recharts, Material-UI
- **Authentication**: JWT
- **Monitoring**: Prometheus, Grafana
- **Container**: Docker

 🖥️ Running Commands:
 One-Click Startup :
 # For 500 machines
start_all_500.bat
# For 1000 machines  
start_all_1000.bat

## 🖥️ Manual Startup (8 Terminals - Exact Order)
Terminal 1: Zookeeper
cd C:\kafka
"C:\Program Files\Java\jre1.8.0_481\bin\java" -cp "libs\*" org.apache.zookeeper.server.quorum.QuorumPeerMain config\zookeeper.properties

Terminal 2: Kafka Broker
cd C:\kafka
"C:\Program Files\Java\jre1.8.0_481\bin\java" -cp "libs\*" kafka.Kafka config\server.properties


Terminal 3: PostgreSQL
docker start postgres-induswatch

Terminal 4: Backend API
cd C:\IndusWatchAI\backend
python main.py

Terminal 5: Kafka Consumer
cd C:\IndusWatchAI\processing-service
python consumer.py

Terminal 6: Alert Service
cd C:\IndusWatchAI\alert-service
python alert_service.py

Terminal 7: Simulator (500 Machines)
cd C:\IndusWatchAI
python simulator/iot_simulator.py --machines 500

Terminal 8: React Dashboard
cd C:\IndusWatchAI\frontend
npm start


👨‍💻 Author
Torsa Bhattacharya

GitHub: @Torsabhattacharya

Project Link: https://github.com/Torsabhattacharya/IndusWatchAI
