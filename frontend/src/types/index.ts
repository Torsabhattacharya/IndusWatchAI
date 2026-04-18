export interface SensorData {
  machine_id: string;
  machine_type: string;
  timestamp: string;
  temperature: number;
  vibration: number;
  pressure: number;
  rpm: number;
  is_anomaly: boolean;
  failure_risk: number;
  health_score: number;
}

export interface Alert {
  id: number;
  machine_id: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  message: string;
  timestamp: string;
  acknowledged: boolean;
}

export interface MachineStatus {
  machine_id: string;
  machine_type: string;
  health_score: number;
  failure_risk: number;
  last_update: string;
}
