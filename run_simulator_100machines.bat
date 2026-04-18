@echo off
cd C:\IndusWatchAI
echo Starting IndusWatchAI Simulator with 100 Machines...
python simulator/iot_simulator.py --machines 100 --start-id 1
pause