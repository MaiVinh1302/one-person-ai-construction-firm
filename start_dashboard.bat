@echo off
chcp 65001 >nul
echo =======================================================================
echo   T^&T ONE-PERSON AI CONSTRUCTION ENTERPRISE - DASHBOARD LAUNCHER
echo =======================================================================
echo.
echo Dang khoi dong Portal Dieu Hanh Doanh Nghiep Xay Dung 1 Nguoi...
echo Founder: Mai Quang Vinh (Level 4 - Supreme Authority)
echo.

cd /d "%~dp0"
echo Dang khoi chay FastAPI Server tai http://localhost:8000 ...
python -m uvicorn web.server:app --host 0.0.0.0 --port 8000 --reload

pause
