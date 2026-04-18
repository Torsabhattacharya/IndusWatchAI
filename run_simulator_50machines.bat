@echo off
cd C:\IndusWatchAI
echo Starting IndusWatchAI Simulator with 50 Machines...
python simulator/iot_simulator.py --machines 50 --start-id 1
pause