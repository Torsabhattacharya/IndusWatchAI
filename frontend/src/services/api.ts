
import axios from 'axios';
import { SensorData, Alert, MachineStatus } from '../types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getMachines = async () => {
  const response = await api.get('/machines');
  return response.data;
};

export const getHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const getMetrics = async () => {
  const response = await api.get('/metrics');
  return response.data;
};

export const getSensorHistory = async (limit: number = 50) => {
  const response = await api.get(`/sensor-history?limit=${limit}`);
  return response.data;
};

export const getAlerts = async (limit: number = 20) => {
  // Note: You'll need to add this endpoint to backend
  const response = await api.get(`/alerts?limit=${limit}`);
  return response.data;
};

export const sendSensorData = async (data: SensorData) => {
  const response = await api.post('/sensor-data', data);
  return response.data;
};

export default api;
