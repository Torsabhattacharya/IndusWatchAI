
import React, { useState } from 'react';
import axios from 'axios';

interface LoginProps {
  onLogin: (token: string) => void;
}

const Login: React.FC<LoginProps> = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`http://localhost:8000/token?username=${username}&password=${password}`);
      const token = response.data.access_token;
      localStorage.setItem('token', token);
      onLogin(token);
    } catch (err) {
      setError('Invalid username or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0a0a2a 0%, #1a1a3e 50%, #2a0a3e 100%)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      fontFamily: 'Arial'
    }}>
      <div style={{
        background: 'rgba(255,255,255,0.1)',
        backdropFilter: 'blur(10px)',
        padding: '40px',
        borderRadius: '20px',
        width: '400px',
        boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
        border: '1px solid rgba(139,0,255,0.3)'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <h1 style={{ fontSize: '48px', margin: 0 }}>🏭</h1>
          <h2 style={{ color: 'white', margin: '10px 0 5px' }}>IndusWatchAI</h2>
          <p style={{ color: '#aaa', fontSize: '14px' }}>Industrial Failure Prediction System</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ color: '#ddd', display: 'block', marginBottom: '8px' }}>Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '1px solid rgba(139,0,255,0.5)',
                background: 'rgba(0,0,0,0.3)',
                color: 'white',
                fontSize: '16px'
              }}
              placeholder="Enter username"
              required
            />
          </div>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ color: '#ddd', display: 'block', marginBottom: '8px' }}>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                borderRadius: '8px',
                border: '1px solid rgba(139,0,255,0.5)',
                background: 'rgba(0,0,0,0.3)',
                color: 'white',
                fontSize: '16px'
              }}
              placeholder="Enter password"
              required
            />
          </div>

          {error && (
            <div style={{
              background: 'rgba(255,0,0,0.2)',
              padding: '10px',
              borderRadius: '8px',
              color: '#ff6b6b',
              textAlign: 'center',
              marginBottom: '20px'
            }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '12px',
              background: 'linear-gradient(135deg, #8B00FF, #4B0082)',
              border: 'none',
              borderRadius: '8px',
              color: 'white',
              fontSize: '16px',
              fontWeight: 'bold',
              cursor: 'pointer',
              transition: 'transform 0.3s'
            }}
            onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.02)'}
            onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '20px', color: '#888', fontSize: '12px' }}>
          Demo credentials: admin / admin123
        </div>
      </div>
    </div>
  );
};

export default Login;
