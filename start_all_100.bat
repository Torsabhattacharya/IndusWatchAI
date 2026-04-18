
@echo off
echo Starting IndusWatchAI with 1000 Machines...
start "Zookeeper" cmd /k "cd C:\kafka && & ""C:\Program Files\Java\jre1.8.0_481\bin\java"" -cp ""libs\*"" org.apache.zookeeper.server.quorum.QuorumPeerMain config\zookeeper.properties"
timeout /t 3 /nobreak > nul
start "Kafka" cmd /k "cd C:\kafka && & ""C:\Program Files\Java\jre1.8.0_481\bin\java"" -cp ""libs\*"" kafka.Kafka config\server.properties"
timeout /t 5 /nobreak > nul
start "PostgreSQL" cmd /k "docker start postgres-induswatch"
timeout /t 2 /nobreak > nul
start "Backend API" cmd /k "cd C:\IndusWatchAI\backend && python main.py"
timeout /t 5 /nobreak > nul
start "Consumer" cmd /k "cd C:\IndusWatchAI\processing-service && python consumer.py"
timeout /t 2 /nobreak > nul
start "Alert Service" cmd /k "cd C:\IndusWatchAI\alert-service && python alert_service.py"
timeout /t 2 /nobreak > nul
start "Simulator (1000 Machines)" cmd /k "cd C:\IndusWatchAI && python simulator/iot_simulator.py --machines 1000"
timeout /t 3 /nobreak > nul
start "React Dashboard" cmd /k "cd C:\IndusWatchAI\frontend && npm start"
echo All services started with 1000 machines!
echo.
echo Dashboard: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo Kafka UI: http://localhost:8080
echo Prometheus: http://localhost:9090
echo Grafana: http://localhost:3001 (admin/admin)
echo.
pause


