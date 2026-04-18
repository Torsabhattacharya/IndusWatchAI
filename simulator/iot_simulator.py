import requests
import random
import time
import json
from datetime import datetime
import threading
import logging
import argparse
import yaml
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

# Setup logging
log_dir = Path("C:/IndusWatchAI/logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "simulator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class MachineConfig:
    """Configuration for each machine"""
    machine_id: str
    machine_type: str  # CNC, Conveyor, Pump, Compressor, Generator
    normal_temp_range: tuple = (65, 85)
    normal_vib_range: tuple = (0.1, 0.5)
    normal_pressure_range: tuple = (95, 105)
    normal_rpm_range: tuple = (1400, 1600)
    anomaly_probability: float = 0.15
    critical_threshold: float = 0.85

class IndustrialSensorSimulator:
    """Enhanced simulator supporting unlimited machines"""
    
    # Predefined machine types with their characteristics
    MACHINE_TYPES = {
        "CNC": {
            "temp_range": (60, 90),
            "vib_range": (0.05, 0.8),
            "pressure_range": (80, 120),
            "rpm_range": (1000, 5000),
            "anomaly_prob": 0.12
        },
        "Conveyor": {
            "temp_range": (40, 70),
            "vib_range": (0.1, 0.6),
            "pressure_range": (90, 110),
            "rpm_range": (300, 800),
            "anomaly_prob": 0.18
        },
        "Pump": {
            "temp_range": (50, 85),
            "vib_range": (0.2, 1.0),
            "pressure_range": (100, 150),
            "rpm_range": (800, 2400),
            "anomaly_prob": 0.15
        },
        "Compressor": {
            "temp_range": (70, 110),
            "vib_range": (0.3, 1.2),
            "pressure_range": (120, 180),
            "rpm_range": (600, 1800),
            "anomaly_prob": 0.14
        },
        "Generator": {
            "temp_range": (75, 105),
            "vib_range": (0.15, 0.7),
            "pressure_range": (85, 115),
            "rpm_range": (1200, 3600),
            "anomaly_prob": 0.13
        }
    }
    
    def __init__(self, machine_config: MachineConfig, api_url: str = "http://localhost:8000/sensor-data"):
        self.config = machine_config
        self.api_url = api_url
        self.running = False
        self.data_count = 0
        self.failure_count = 0
        self.anomaly_count = 0
        self.critical_alerts = 0
        
        # Get machine type characteristics
        self.char = self.MACHINE_TYPES.get(machine_config.machine_type, self.MACHINE_TYPES["CNC"])
        
    def generate_sensor_data(self):
        """Generate realistic sensor readings with machine-specific patterns"""
        
        # Normal operating ranges from machine config
        temperature = random.uniform(*self.char["temp_range"])
        vibration = random.uniform(*self.char["vib_range"])
        pressure = random.uniform(*self.char["pressure_range"])
        rpm = random.uniform(*self.char["rpm_range"])
        
        # Determine if anomaly occurs
        anomaly = random.random() < self.char["anomaly_prob"]
        failure_risk = 0.0
        anomaly_type = None
        
        if anomaly:
            self.anomaly_count += 1
            # Anomaly patterns based on machine type
            if self.config.machine_type == "CNC":
                anomaly_type = random.choice(['tool_wear', 'spindle_overload', 'coolant_failure'])
                if anomaly_type == 'tool_wear':
                    vibration = random.uniform(1.5, 3.0)
                    failure_risk = random.uniform(0.6, 0.85)
                elif anomaly_type == 'spindle_overload':
                    temperature = random.uniform(100, 150)
                    rpm = random.uniform(4000, 5500)
                    failure_risk = random.uniform(0.7, 0.9)
                else:  # coolant_failure
                    temperature = random.uniform(110, 160)
                    failure_risk = random.uniform(0.5, 0.8)
                    
            elif self.config.machine_type == "Pump":
                anomaly_type = random.choice(['cavitation', 'seal_leak', 'bearing_failure'])
                if anomaly_type == 'cavitation':
                    vibration = random.uniform(1.2, 2.5)
                    pressure = random.uniform(60, 90)
                    failure_risk = random.uniform(0.5, 0.75)
                elif anomaly_type == 'seal_leak':
                    pressure = random.uniform(50, 80)
                    failure_risk = random.uniform(0.4, 0.7)
                else:  # bearing_failure
                    temperature = random.uniform(90, 130)
                    vibration = random.uniform(1.0, 2.0)
                    failure_risk = random.uniform(0.7, 0.9)
                    
            else:  # Other machine types
                anomaly_type = random.choice(['overheating', 'high_vibration', 'pressure_spike', 'rpm_drop'])
                if anomaly_type == 'overheating':
                    temperature = random.uniform(100, 150)
                    failure_risk = random.uniform(0.6, 0.9)
                elif anomaly_type == 'high_vibration':
                    vibration = random.uniform(1.5, 3.5)
                    failure_risk = random.uniform(0.5, 0.85)
                elif anomaly_type == 'pressure_spike':
                    pressure = random.uniform(150, 200)
                    failure_risk = random.uniform(0.4, 0.75)
                else:  # rpm_drop
                    rpm = random.uniform(200, 600)
                    failure_risk = random.uniform(0.5, 0.8)
            
            logger.warning(f"[{self.config.machine_id}] {anomaly_type.upper()} detected! {anomaly_type}")
        
        # Critical failure condition (30% chance if anomaly exists)
        if anomaly and random.random() < 0.3:
            failure_risk = random.uniform(0.85, 0.99)
            self.critical_alerts += 1
            logger.critical(f"💀 [{self.config.machine_id}] CRITICAL FAILURE IMMINENT! Risk: {failure_risk:.2%}")
        
        return {
            "machine_id": self.config.machine_id,
            "machine_type": self.config.machine_type,
            "timestamp": datetime.utcnow().isoformat(),
            "temperature": round(temperature, 2),
            "vibration": round(vibration, 3),
            "pressure": round(pressure, 2),
            "rpm": round(rpm, 2),
            "is_anomaly": anomaly,
            "anomaly_type": anomaly_type if anomaly else None,
            "failure_risk": round(failure_risk, 3),
            "health_score": round((1 - failure_risk) * 100, 1) if failure_risk > 0 else 100
        }
    
    def send_data(self, data):
        """Send data to API endpoint with retry mechanism"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                headers = {'Content-Type': 'application/json'}
                response = requests.post(
                    self.api_url, 
                    json=data, 
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code == 200:
                    self.data_count += 1
                    # Visual indicator based on risk level
                    if data['failure_risk'] > 0.85:
                        emoji = "💀🔥"
                    elif data['failure_risk'] > 0.7:
                        emoji = "⚠️⚠️"
                    elif data['failure_risk'] > 0.5:
                        emoji = "⚠️"
                    elif data['is_anomaly']:
                        emoji = "🔶"
                    else:
                        emoji = "✅"
                    
                    logger.info(f"{emoji} [{data['machine_id']}/{data['machine_type']}] #{self.data_count}: T={data['temperature']}°C, V={data['vibration']}mm/s, P={data['pressure']}PSI, Health={data['health_score']}%")
                    return True
                    
                elif response.status_code == 429:
                    logger.warning(f"Rate limited, slowing down...")
                    time.sleep(2)
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"✗ [{self.config.machine_id}] Attempt {attempt+1} error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
        
        self.failure_count += 1
        return False
    
    def start(self):
        """Start continuous data generation"""
        self.running = True
        logger.info(f"🏭 Starting [{self.config.machine_type}] Machine {self.config.machine_id}")
        
        while self.running:
            data = self.generate_sensor_data()
            self.send_data(data)
            # Dynamic interval based on machine criticality
            interval = 0.5 if data['failure_risk'] > 0.7 else 1.0
            time.sleep(interval)
    
    def stop(self):
        self.running = False
        logger.info(f"🛑 Stopped Machine {self.config.machine_id}")
        logger.info(f"📊 Stats - Sent: {self.data_count}, Failed: {self.failure_count}, Anomalies: {self.anomaly_count}, Critical: {self.critical_alerts}")

class SimulatorManager:
    """Manages multiple machine simulators"""
    
    def __init__(self, api_url: str = "http://localhost:8000/sensor-data"):
        self.api_url = api_url
        self.machines: List[IndustrialSensorSimulator] = []
        self.threads: List[threading.Thread] = []
        
    def add_machines(self, count: int, start_id: int = 1, machine_types: Optional[List[str]] = None):
        """Add multiple machines dynamically"""
        if machine_types is None:
            # Cycle through machine types
            machine_types = list(IndustrialSensorSimulator.MACHINE_TYPES.keys())
        
        for i in range(count):
            machine_id = f"M{start_id + i:04d}"  # M0001, M0002, etc.
            machine_type = machine_types[i % len(machine_types)]
            
            config = MachineConfig(
                machine_id=machine_id,
                machine_type=machine_type
            )
            
            simulator = IndustrialSensorSimulator(config, self.api_url)
            self.machines.append(simulator)
            
        logger.info(f"✅ Added {count} machines (Total: {len(self.machines)})")
        
    def start_all(self):
        """Start all machine simulators"""
        for machine in self.machines:
            thread = threading.Thread(target=machine.start)
            thread.daemon = True
            thread.start()
            self.threads.append(thread)
            time.sleep(0.1)  # Stagger startup to avoid thundering herd
            
        logger.info(f"🚀 Started {len(self.machines)} simulators")
        
    def stop_all(self):
        """Stop all simulators"""
        for machine in self.machines:
            machine.stop()
            
    def get_stats(self):
        """Get overall statistics"""
        total_sent = sum(m.data_count for m in self.machines)
        total_failed = sum(m.failure_count for m in self.machines)
        total_anomalies = sum(m.anomaly_count for m in self.machines)
        total_critical = sum(m.critical_alerts for m in self.machines)
        
        return {
            "total_machines": len(self.machines),
            "total_data_sent": total_sent,
            "total_failed": total_failed,
            "total_anomalies": total_anomalies,
            "total_critical_alerts": total_critical,
            "success_rate": (total_sent / (total_sent + total_failed) * 100) if (total_sent + total_failed) > 0 else 0
        }

def main():
    parser = argparse.ArgumentParser(description='IndusWatchAI - Industrial Sensor Simulator')
    parser.add_argument('--machines', '-m', type=int, default=10, help='Number of machines to simulate (default: 10)')
    parser.add_argument('--api-url', default='http://localhost:8000/sensor-data', help='API endpoint URL')
    parser.add_argument('--start-id', type=int, default=1, help='Starting machine ID (default: 1)')
    parser.add_argument('--machine-types', nargs='+', help='List of machine types (CNC, Pump, Conveyor, etc.)')
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("🏭 INDUSWATCHAI - INDUSTRIAL SENSOR SIMULATOR (PRODUCTION GRADE)")
    print("=" * 80)
    print(f"📍 Logs: C:/IndusWatchAI/logs")
    print(f"🎯 Target API: {args.api_url}")
    print(f"🤖 Simulating {args.machines} industrial machines...")
    print(f"📊 Machine types: {args.machine_types if args.machine_types else 'Auto-cycle (CNC, Pump, Conveyor, Compressor, Generator)'}")
    print("=" * 80)
    print("Press Ctrl+C to stop\n")
    
    # Create manager
    manager = SimulatorManager(api_url=args.api_url)
    
    # Add machines
    manager.add_machines(
        count=args.machines,
        start_id=args.start_id,
        machine_types=args.machine_types
    )
    
    # Start all simulators
    manager.start_all()
    
    # Statistics reporter thread
    def report_stats():
        while True:
            time.sleep(30)  # Report every 30 seconds
            stats = manager.get_stats()
            print("\n" + "=" * 60)
            print(f"📊 LIVE STATISTICS:")
            print(f"   Active Machines: {stats['total_machines']}")
            print(f"   Total Data Sent: {stats['total_data_sent']}")
            print(f"   Success Rate: {stats['success_rate']:.1f}%")
            print(f"   Anomalies Detected: {stats['total_anomalies']}")
            print(f"   Critical Alerts: {stats['total_critical_alerts']}")
            print("=" * 60 + "\n")
    
    stats_thread = threading.Thread(target=report_stats)
    stats_thread.daemon = True
    stats_thread.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Stopping all simulators...")
        manager.stop_all()
        print("✅ All simulators stopped")
        final_stats = manager.get_stats()
        print(f"\n📊 FINAL STATISTICS:")
        print(f"   Total Machines: {final_stats['total_machines']}")
        print(f"   Total Data Points: {final_stats['total_data_sent']}")
        print(f"   Overall Success Rate: {final_stats['success_rate']:.1f}%")
        print(f"   Anomalies: {final_stats['total_anomalies']}")
        print(f"   Critical Alerts: {final_stats['total_critical_alerts']}")

if __name__ == "__main__":
    main()