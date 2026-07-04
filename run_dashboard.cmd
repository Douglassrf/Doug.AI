@echo off
cd /d "%~dp0"
set PYTHONPATH=%CD%
set DOUG_MODE=paper
set DEMO_MODE=1
".venv\Scripts\python.exe" -m streamlit run dashboard/app.py --server.port 8501
