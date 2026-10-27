P1 AI CITY TRAFFIC COMMAND CENTRE

1. Extract this ZIP into the P1 project root (C:\Users\reshm\Downloads\P1), merging folders.
2. Open PowerShell in the P1 root.
3. Run: powershell -ExecutionPolicy Bypass -File .\install_dashboard.ps1
4. Run using the existing Python environment: & $py .\run.py
   If $py is not defined, use the original venv interpreter path:
   & 'C:\Users\reshm\Downloads\AI_CITY_TRAFFIC_SYSTEM\venv\Scripts\python.exe' .\run.py
5. Browser opens at http://127.0.0.1:8000. Keep the terminal open. Ctrl+C stops the server.

The installer preserves the original run.py as run_s14_13_backup.py (only if that backup doesn't already exist).
The dashboard's city-wide junction counts, weather, incidents, and forecasts are demo/simulated. The video analysis button invokes the existing S14.13 controller on data/videos/traffic.mp4. No real traffic lights are controlled.
