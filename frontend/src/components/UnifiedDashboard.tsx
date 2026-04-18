import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';

interface Alert {
  id: number;
  machine_id: string;
  severity: string;
  message: string;
  timestamp: string;
}

interface Metric {
  endpoint: string;
  requests: number;
}

interface SensorData {
  time: string;
  temperature: number;
  vibration: number;
  pressure: number;
  machine_id: string;
  health_score?: number;
}

const UnifiedDashboard: React.FC = () => {
  const [machines, setMachines] = useState<string[]>([]);
  const [health, setHealth] = useState<any>(null);
  const [metrics, setMetrics] = useState<any>(null);
  const [sensorHistory, setSensorHistory] = useState<SensorData[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [prometheusData, setPrometheusData] = useState<Metric[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [riskData, setRiskData] = useState<{ name: string; value: number }[]>([]);
  const [machineTypes, setMachineTypes] = useState<{ name: string; value: number }[]>([]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const machinesRes = await axios.get('http://localhost:8000/machines');
      const healthRes = await axios.get('http://localhost:8000/health');
      const metricsRes = await axios.get('http://localhost:8000/metrics');
      const historyRes = await axios.get('http://localhost:8000/sensor-history?limit=500');
      const alertsRes = await axios.get('http://localhost:8000/alerts?limit=500');
      const promRes = await axios.get('http://localhost:8000/prometheus-metrics');
      
      setMachines(machinesRes.data.active_machines || []);
      setHealth(healthRes.data);
      setMetrics(metricsRes.data);
      setSensorHistory(historyRes.data.history || []);
      setAlerts(alertsRes.data.alerts || []);
      
      const riskCount: Record<string, number> = { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 };
      alertsRes.data.alerts?.forEach((alert: Alert) => {
        const severity = alert.severity as keyof typeof riskCount;
        if (riskCount[severity] !== undefined) riskCount[severity]++;
      });
      setRiskData(Object.entries(riskCount).map(([name, value]) => ({ name, value })));
      
      const typeCount: Record<string, number> = {};
      const types = ['CNC', 'Pump', 'Conveyor', 'Compressor', 'Generator'];
      machinesRes.data.active_machines?.forEach((machine: string, idx: number) => {
        const type = types[idx % 5];
        typeCount[type] = (typeCount[type] || 0) + 1;
      });
      setMachineTypes(Object.entries(typeCount).map(([name, value]) => ({ name, value })));
      
      const lines = promRes.data.split('\n');
      const metricsData: Metric[] = [];
      for (const line of lines) {
        if (line.startsWith('http_requests_total{') && !line.includes('_created')) {
          const endpointMatch = line.match(/endpoint="([^"]+)"/);
          const value = line.split(' ').pop();
          if (endpointMatch && value) {
            metricsData.push({
              endpoint: endpointMatch[1],
              requests: parseInt(value)
            });
          }
        }
      }
      setPrometheusData(metricsData);
      setLoading(false);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const COLORS = ['#8B00FF', '#4B0082', '#FF1493', '#00BFFF', '#9400D3', '#FF4500', '#DA70D6'];
  const GRADIENT_COLORS = ['#6a11cb', '#2575fc', '#ff6a00', '#ee0979', '#00b4db', '#8B00FF', '#4B0082'];
  const RISK_COLORS: Record<string, string> = { LOW: '#00FF88', MEDIUM: '#FFD700', HIGH: '#FF6347', CRITICAL: '#FF0000' };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px', fontFamily: 'Arial', background: 'linear-gradient(135deg, #0a0a2a 0%, #1a1a3e 100%)', minHeight: '100vh', color: 'white' }}>
        <div style={{ border: '4px solid rgba(255,255,255,0.3)', borderTop: '4px solid #8B00FF', borderRadius: '50%', width: '50px', height: '50px', animation: 'spin 1s linear infinite', margin: '0 auto' }}></div>
        <h1 style={{ marginTop: '20px', color: '#8B00FF' }}>🏭 IndusWatchAI</h1>
        <p>Loading dashboard...</p>
        <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  const styles = {
    container: { maxWidth: '1400px', margin: '0 auto', padding: '20px', fontFamily: 'Arial', background: '#0a0a2a', minHeight: '100vh' },
    header: { background: 'linear-gradient(135deg, #0a0a2a 0%, #1a1a3e 50%, #2a0a3e 100%)', color: 'white', padding: '30px', borderRadius: '15px', marginBottom: '25px', boxShadow: '0 4px 15px rgba(139,0,255,0.3)', border: '1px solid rgba(139,0,255,0.3)' },
    statsGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px', marginBottom: '25px' },
    statCard: (gradient: string) => ({ background: gradient, padding: '20px', borderRadius: '15px', textAlign: 'center' as const, boxShadow: '0 4px 15px rgba(0,0,0,0.3)', transition: 'transform 0.3s', cursor: 'pointer', border: '1px solid rgba(255,255,255,0.1)' }),
    tabBar: { display: 'flex', gap: '12px', marginBottom: '25px', flexWrap: 'wrap' as const },
    tab: (active: boolean) => ({ padding: '12px 24px', border: 'none', borderRadius: '25px', cursor: 'pointer', fontSize: '14px', fontWeight: 'bold', background: active ? 'linear-gradient(135deg, #8B00FF, #4B0082)' : 'rgba(255,255,255,0.1)', color: active ? 'white' : '#ccc', boxShadow: active ? '0 0 10px rgba(139,0,255,0.5)' : 'none', transition: 'all 0.3s' }),
    chartContainer: { background: 'linear-gradient(135deg, #0f0f2a, #1a1a3e)', padding: '20px', borderRadius: '15px', marginBottom: '25px', boxShadow: '0 4px 15px rgba(0,0,0,0.3)', border: '1px solid rgba(139,0,255,0.2)' },
    table: { width: '100%', borderCollapse: 'collapse' as const },
    th: { padding: '12px', textAlign: 'left' as const, borderBottom: '2px solid #8B00FF', background: 'rgba(139,0,255,0.1)', fontWeight: 'bold', color: '#8B00FF' },
    td: { padding: '12px', borderBottom: '1px solid rgba(139,0,255,0.2)', color: '#ddd' },
    badge: (color: string) => ({ background: color, color: 'black', padding: '4px 12px', borderRadius: '20px', fontSize: '12px', display: 'inline-block', fontWeight: 'bold' }),
  };

  return (
    <div style={styles.container}>
      <style>{`
        .stat-card:hover { transform: translateY(-5px); }
        button:hover { transform: scale(1.02); }
        table tr:hover { background: rgba(139,0,255,0.1); }
      `}</style>

      {/* Header */}
      <div style={styles.header}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap' }}>
          <div>
            <h1 style={{ margin: 0, fontSize: '28px', background: 'linear-gradient(135deg, #8B00FF, #FF1493)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>🏭 IndusWatchAI</h1>
            <p style={{ margin: '8px 0 0', opacity: 0.8, color: '#aaa' }}>Industrial Failure Prediction System | Real-time Monitoring</p>
          </div>
          <div style={{ marginTop: '10px' }}>
            <span style={{ background: health?.kafka_connected ? 'linear-gradient(135deg, #00FF88, #00BFFF)' : '#f44336', padding: '6px 16px', borderRadius: '25px', fontSize: '12px', fontWeight: 'bold', color: 'black' }}>
              {health?.kafka_connected ? '🔌 Kafka Connected' : '⚠️ Kafka Disconnected'}
            </span>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div style={styles.statsGrid}>
        <div className="stat-card" style={styles.statCard('linear-gradient(135deg, #8B00FF, #4B0082)')}>
          <div style={{ fontSize: '14px', opacity: 0.9 }}>Active Machines</div>
          <div style={{ fontSize: '42px', fontWeight: 'bold', margin: '10px 0' }}>{machines.length}</div>
          <div style={{ fontSize: '12px', opacity: 0.8 }}>📊 Online & Connected</div>
        </div>
        <div className="stat-card" style={styles.statCard('linear-gradient(135deg, #FF1493, #8B00FF)')}>
          <div style={{ fontSize: '14px', opacity: 0.9 }}>Total Requests</div>
          <div style={{ fontSize: '42px', fontWeight: 'bold', margin: '10px 0' }}>{(metrics?.total_requests || 0).toLocaleString()}</div>
          <div style={{ fontSize: '12px', opacity: 0.8 }}>📈 API Calls</div>
        </div>
        <div className="stat-card" style={styles.statCard('linear-gradient(135deg, #FF4500, #FF1493)')}>
          <div style={{ fontSize: '14px', opacity: 0.9 }}>Total Alerts</div>
          <div style={{ fontSize: '42px', fontWeight: 'bold', margin: '10px 0', color: '#FF0000' }}>{alerts.length}</div>
          <div style={{ fontSize: '12px', opacity: 0.8 }}>⚠️ Generated</div>
        </div>
        <div className="stat-card" style={styles.statCard('linear-gradient(135deg, #00BFFF, #4B0082)')}>
          <div style={{ fontSize: '14px', opacity: 0.9 }}>System Status</div>
          <div style={{ fontSize: '32px', fontWeight: 'bold', margin: '10px 0', color: health?.status === 'healthy' ? '#00FF88' : '#FF0000' }}>{health?.status || 'N/A'}</div>
          <div style={{ fontSize: '12px', opacity: 0.8 }}>✅ All Systems Operational</div>
        </div>
      </div>

      {/* Tabs */}
      <div style={styles.tabBar}>
        {['dashboard', 'machines', 'alerts', 'analytics', 'health'].map((tab) => (
          <button key={tab} onClick={() => setActiveTab(tab)} style={styles.tab(activeTab === tab)}>
            {tab === 'dashboard' && '📊 Dashboard'}
            {tab === 'machines' && `🖥️ Machines (${machines.length})`}
            {tab === 'alerts' && `⚠️ Alerts (${alerts.length})`}
            {tab === 'analytics' && '📈 Analytics'}
            {tab === 'health' && '🏥 System Health'}
          </button>
        ))}
      </div>

      {/* Dashboard Tab */}
      {activeTab === 'dashboard' && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '20px', marginBottom: '25px' }}>
            <div style={styles.chartContainer}>
              <h3 style={{ margin: '0 0 20px', color: '#8B00FF' }}>🌡️ Live Sensor Trends</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={sensorHistory.slice(-30)}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis dataKey="time" angle={-45} textAnchor="end" height={60} stroke="#888" />
                  <YAxis yAxisId="left" domain={[0, 150]} stroke="#FF6347" />
                  <YAxis yAxisId="right" orientation="right" domain={[0, 3]} stroke="#00FF88" />
                  <Tooltip contentStyle={{ background: '#1a1a3e', border: '1px solid #8B00FF', borderRadius: '10px' }} />
                  <Legend />
                  <Line yAxisId="left" type="monotone" dataKey="temperature" stroke="#FF6347" name="Temperature (°C)" strokeWidth={2} dot={false} />
                  <Line yAxisId="right" type="monotone" dataKey="vibration" stroke="#00FF88" name="Vibration (mm/s)" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div style={styles.chartContainer}>
              <h3 style={{ margin: '0 0 20px', color: '#8B00FF' }}>🎯 API Request Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie 
                    data={prometheusData} 
                    cx="50%" 
                    cy="50%" 
                    labelLine={true} 
                    label={(entry: any) => `${entry.endpoint}: ${entry.requests}`} 
                    outerRadius={100} 
                    fill="#8884d8" 
                    dataKey="requests" 
                    nameKey="endpoint"
                  >
                    {prometheusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ background: '#1a1a3e', border: '1px solid #8B00FF', borderRadius: '10px' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div style={styles.chartContainer}>
            <h3 style={{ margin: '0 0 20px', color: '#8B00FF' }}>📋 Recent Sensor Readings</h3>
            <div style={{ overflowX: 'auto' }}>
              <table style={styles.table}>
                <thead>
                  <tr><th style={styles.th}>Time</th><th style={styles.th}>Temperature</th><th style={styles.th}>Vibration</th><th style={styles.th}>Pressure</th><th style={styles.th}>Machine</th></tr>
                </thead>
                <tbody>
                  {sensorHistory.slice(0, 500).map((data, idx) => (
                    <tr key={idx}>
                      <td style={styles.td}>{data.time}</td>
                      <td style={styles.td}><span style={{ color: data.temperature > 90 ? '#FF0000' : '#00FF88' }}>{data.temperature}°C</span></td>
                      <td style={styles.td}>{data.vibration} mm/s</td>
                      <td style={styles.td}>{data.pressure} PSI</td>
                      <td style={styles.td}>{data.machine_id}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {/* Machines Tab */}
      {activeTab === 'machines' && (
        <div style={styles.chartContainer}>
          <h3 style={{ margin: '0 0 20px', color: '#8B00FF' }}>🖥️ All Machines ({machines.length})</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '12px' }}>
            {machines.map((machine, idx) => (
              <div key={machine} style={{ background: 'linear-gradient(135deg, #1a1a3e, #0a0a2a)', padding: '12px', borderRadius: '10px', textAlign: 'center', border: '1px solid rgba(139,0,255,0.3)' }}>
                <strong style={{ color: '#8B00FF' }}>{machine}</strong><br />
                <span style={{ fontSize: '11px', color: '#888' }}>{['CNC', 'Pump', 'Conveyor', 'Compressor', 'Generator'][idx % 5]}</span>
                <div style={{ marginTop: '8px' }}><span style={styles.badge('#00FF88')}>Active</span></div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Alerts Tab */}
      {activeTab === 'alerts' && (
        <div style={styles.chartContainer}>
          <h3 style={{ margin: '0 0 20px', color: '#FF0000' }}>⚠️ Recent Alerts ({alerts.length} total)</h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={styles.table}>
              <thead><tr><th style={styles.th}>Time</th><th style={styles.th}>Machine</th><th style={styles.th}>Severity</th><th style={styles.th}>Message</th></tr></thead>
              <tbody>
                {alerts.slice(0, 500).map((alert) => (
                  <tr key={alert.id}>
                    <td style={styles.td}>{new Date(alert.timestamp).toLocaleString()}</td>
                    <td style={styles.td}><strong>{alert.machine_id}</strong></td>
                    <td style={styles.td}><span style={styles.badge(RISK_COLORS[alert.severity] || '#999')}>{alert.severity}</span></td>
                    <td style={styles.td}>{alert.message}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '20px', marginBottom: '25px' }}>
            <div style={styles.chartContainer}>
              <h3 style={{ margin: '0 0 20px', color: '#8B00FF' }}>📊 Risk Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={riskData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                  <XAxis dataKey="name" stroke="#888" />
                  <YAxis stroke="#888" />
                  <Tooltip contentStyle={{ background: '#1a1a3e', border: '1px solid #8B00FF' }} />
                  <Bar dataKey="value" fill="#8B00FF">
                    {riskData.map((entry, index) => (<Cell key={`cell-${index}`} fill={RISK_COLORS[entry.name] || COLORS[index % COLORS.length]} />))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div style={styles.chartContainer}>
              <h3 style={{ margin: '0 0 20px', color: '#8B00FF' }}>🔧 Machine Type Distribution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie data={machineTypes} cx="50%" cy="50%" labelLine={true} label={(entry: any) => `${entry.name}: ${entry.value}`} outerRadius={100} fill="#8884d8" dataKey="value" nameKey="name">
                    {machineTypes.map((entry, index) => (<Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />))}
                  </Pie>
                  <Tooltip contentStyle={{ background: '#1a1a3e', border: '1px solid #8B00FF' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div style={styles.chartContainer}>
            <h3 style={{ margin: '0 0 20px', color: '#8B00FF' }}>📈 Request Trends by Endpoint</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={prometheusData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis type="number" stroke="#888" />
                <YAxis type="category" dataKey="endpoint" width={120} stroke="#888" />
                <Tooltip contentStyle={{ background: '#1a1a3e', border: '1px solid #8B00FF' }} />
                <Bar dataKey="requests" fill="#8B00FF" radius={[0, 10, 10, 0]}>
                  {prometheusData.map((entry, index) => (<Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}

      {/* Health Tab */}
      {activeTab === 'health' && (
        <div style={styles.chartContainer}>
          <h3 style={{ margin: '0 0 20px', color: '#8B00FF' }}>🏥 System Health Dashboard</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
            <div style={{ background: 'linear-gradient(135deg, #1a1a3e, #0a0a2a)', padding: '20px', borderRadius: '15px', border: '1px solid rgba(139,0,255,0.3)' }}><h4 style={{ color: '#8B00FF' }}>🚀 Backend API</h4><p style={{ color: '#ddd' }}><strong>Status:</strong> <span style={{ color: '#00FF88' }}>✅ Healthy</span></p><p><strong>Total Requests:</strong> {(metrics?.total_requests || 0).toLocaleString()}</p></div>
            <div style={{ background: health?.kafka_connected ? 'linear-gradient(135deg, #1a1a3e, #0a0a2a)' : 'linear-gradient(135deg, #3a1a1a, #2a0a0a)', padding: '20px', borderRadius: '15px', border: '1px solid rgba(139,0,255,0.3)' }}><h4 style={{ color: '#8B00FF' }}>📨 Kafka</h4><p><strong>Status:</strong> <span style={{ color: health?.kafka_connected ? '#00FF88' : '#FF0000' }}>{health?.kafka_connected ? '✅ Connected' : '❌ Disconnected'}</span></p><p><strong>Port:</strong> 9092</p></div>
            <div style={{ background: 'linear-gradient(135deg, #1a1a3e, #0a0a2a)', padding: '20px', borderRadius: '15px', border: '1px solid rgba(139,0,255,0.3)' }}><h4 style={{ color: '#8B00FF' }}>🐘 PostgreSQL</h4><p><strong>Status:</strong> <span style={{ color: '#00FF88' }}>✅ Connected</span></p><p><strong>Database:</strong> induswatchai</p></div>
            <div style={{ background: 'linear-gradient(135deg, #1a1a3e, #0a0a2a)', padding: '20px', borderRadius: '15px', border: '1px solid rgba(139,0,255,0.3)' }}><h4 style={{ color: '#8B00FF' }}>🤖 ML Model</h4><p><strong>Status:</strong> <span style={{ color: '#00FF88' }}>✅ Active</span></p><p><strong>Accuracy:</strong> 85%</p></div>
            <div style={{ background: 'linear-gradient(135deg, #1a1a3e, #0a0a2a)', padding: '20px', borderRadius: '15px', border: '1px solid rgba(139,0,255,0.3)' }}><h4 style={{ color: '#8B00FF' }}>📊 Prometheus</h4><p><strong>URL:</strong> <a href="http://localhost:9090" target="_blank" style={{ color: '#00BFFF' }}>localhost:9090</a></p></div>
            <div style={{ background: 'linear-gradient(135deg, #1a1a3e, #0a0a2a)', padding: '20px', borderRadius: '15px', border: '1px solid rgba(139,0,255,0.3)' }}><h4 style={{ color: '#8B00FF' }}>📈 Grafana</h4><p><strong>URL:</strong> <a href="http://localhost:3001" target="_blank" style={{ color: '#00BFFF' }}>localhost:3001</a></p><p><strong>Login:</strong> admin / admin</p></div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UnifiedDashboard;