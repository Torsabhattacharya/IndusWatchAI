
import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { getMachines, getHealth, getMetrics, getSensorHistory } from '../services/api';
import axios from 'axios';

const Dashboard: React.FC = () => {
  const [machines, setMachines] = useState<string[]>([]);
  const [health, setHealth] = useState<any>(null);
  const [metrics, setMetrics] = useState<any>(null);
  const [sensorHistory, setSensorHistory] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const machinesData = await getMachines();
      const healthData = await getHealth();
      const metricsData = await getMetrics();
      const historyData = await getSensorHistory(30);
      
      // Fetch real alerts from database
      const alertsResponse = await axios.get('http://localhost:8000/alerts?limit=20');
      
      setMachines(machinesData.active_machines || []);
      setHealth(healthData);
      setMetrics(metricsData);
      setSensorHistory(historyData.history || []);
      setAlerts(alertsResponse.data.alerts || []);
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch(severity) {
      case 'CRITICAL': return 'error';
      case 'HIGH': return 'warning';
      case 'MEDIUM': return 'info';
      default: return 'default';
    }
  };

  const formatTime = (timestamp: string) => {
    if (!timestamp) return 'Just now';
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    return date.toLocaleTimeString();
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

  if (loading) {
    return (
      <Container>
        <Typography variant="h4" sx={{ mt: 4 }}>
          Loading IndusWatchAI Dashboard...
        </Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          🏭 IndusWatchAI
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Industrial Failure Prediction System | Real-time Monitoring Dashboard
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          📊 Showing REAL data from PostgreSQL database | {sensorHistory.length} sensor records | {alerts.length} alerts loaded
        </Typography>
      </Box>

      {/* Stats Cards Row 1 */}
      <Box sx={{ display: 'flex', gap: 3, mb: 4, flexWrap: 'wrap' }}>
        <Card sx={{ flex: 1, minWidth: 200 }}>
          <CardContent>
            <Typography color="text.secondary" gutterBottom>Active Machines</Typography>
            <Typography variant="h3">{machines.length}</Typography>
          </CardContent>
        </Card>
        <Card sx={{ flex: 1, minWidth: 200 }}>
          <CardContent>
            <Typography color="text.secondary" gutterBottom>Total Requests</Typography>
            <Typography variant="h3">{metrics?.total_requests || 0}</Typography>
          </CardContent>
        </Card>
        <Card sx={{ flex: 1, minWidth: 200 }}>
          <CardContent>
            <Typography color="text.secondary" gutterBottom>System Health</Typography>
            <Typography variant="h3" color={health?.kafka_connected ? 'success.main' : 'error.main'}>
              {health?.status || 'N/A'}
            </Typography>
          </CardContent>
        </Card>
        <Card sx={{ flex: 1, minWidth: 200 }}>
          <CardContent>
            <Typography color="text.secondary" gutterBottom>Total Alerts</Typography>
            <Typography variant="h3" color="error.main">{alerts.length}</Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Charts Row */}
      <Box sx={{ display: 'flex', gap: 3, mb: 4, flexWrap: 'wrap' }}>
        <Paper sx={{ flex: 2, p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Live Sensor Data (Last {sensorHistory.length} readings from Database)
          </Typography>
          {sensorHistory.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={sensorHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis yAxisId="left" domain={[0, 150]} />
                <YAxis yAxisId="right" orientation="right" domain={[0, 3]} />
                <Tooltip />
                <Legend />
                <Line yAxisId="left" type="monotone" dataKey="temperature" stroke="#ff7300" name="Temperature (°C)" />
                <Line yAxisId="right" type="monotone" dataKey="vibration" stroke="#82ca9d" name="Vibration (mm/s)" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <Typography>No sensor data yet. Run simulator to see data.</Typography>
          )}
        </Paper>
        <Paper sx={{ flex: 1, p: 2 }}>
          <Typography variant="h6" gutterBottom>Machine Distribution</Typography>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={machines.map((m, i) => ({ name: m, value: 1 }))}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry) => entry.name}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {machines.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <Typography variant="body2" align="center" sx={{ mt: 2 }}>
            Total Machines: {machines.length}
          </Typography>
        </Paper>
      </Box>

      {/* Alerts Table */}
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom color="error">
          ⚠️ Recent Alerts from Database ({alerts.length} total)
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Machine ID</TableCell>
                <TableCell>Severity</TableCell>
                <TableCell>Message</TableCell>
                <TableCell>Time</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {alerts.slice(0, 10).map((alert) => (
                <TableRow key={alert.id}>
                  <TableCell>{alert.machine_id}</TableCell>
                  <TableCell>
                    <Chip 
                      label={alert.severity} 
                      color={getSeverityColor(alert.severity) as any} 
                      size="small" 
                    />
                  </TableCell>
                  <TableCell>{alert.message}</TableCell>
                  <TableCell>{formatTime(alert.timestamp)}</TableCell>
                </TableRow>
              ))}
              {alerts.length === 0 && (
                <TableRow>
                  <TableCell colSpan={4} align="center">
                    No alerts yet. Run simulator to generate alerts.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Container>
  );
};

export default Dashboard;
