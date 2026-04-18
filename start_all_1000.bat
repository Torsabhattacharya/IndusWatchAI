

echo Starting IndusWatchAI with 1000 Machines...

echo [1/8] Starting Zookeeper...
start "1-Zookeeper" cmd /k "cd C:\kafka && ""C:\Program Files\Java\jre1.8.0_481\bin\java"" -cp ""libs\*"" org.apache.zookeeper.server.quorum.QuorumPeerMain config\zookeeper.properties"
timeout /t 3 /nobreak > nul

echo [2/8] Starting Kafka Broker...
start "2-Kafka" cmd /k "cd C:\kafka && ""C:\Program Files\Java\jre1.8.0_481\bin\java"" -cp ""libs\*"" kafka.Kafka config\server.properties"
timeout /t 5 /nobreak > nul

echo [3/8] Starting PostgreSQL...
start "3-PostgreSQL" cmd /k "net start postgresql-x64-18"
timeout /t 2 /nobreak > nul

echo [4/8] Starting Backend API...
start "4-Backend API" cmd /k "cd C:\IndusWatchAI\backend && python main.py"
timeout /t 5 /nobreak > nul

echo [5/8] Starting Consumer...
start "5-Consumer" cmd /k "cd C:\IndusWatchAI\processing-service && python consumer.py"
timeout /t 2 /nobreak > nul

echo [6/8] Starting Alert Service...
start "6-Alert Service" cmd /k "cd C:\IndusWatchAI\alert-service && python alert_service.py"
timeout /t 2 /nobreak > nul

echo [7/8] Starting Simulator (1000 Machines)...
start "7-Simulator" cmd /k "cd C:\IndusWatchAI && python simulator/iot_simulator.py --machines 1000"
timeout /t 3 /nobreak > nul

echo [8/8] Starting React Dashboard...
start "8-Dashboard" cmd /k "cd C:\IndusWatchAI\frontend && npm start"

echo.
echo ========================================
echo All services started with 1000 machines!
echo ========================================
echo.
echo Dashboard: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo Kafka UI: http://localhost:8080
echo Prometheus: http://localhost:9090
echo Grafana: http://localhost:3001 (admin/admin)
echo.
pause


