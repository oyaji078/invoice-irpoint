@echo off
setlocal

cd /d "%~dp0"

set PORT=8010

call "%~dp0setup_app.bat"
if errorlevel 1 (
  echo Setup gagal. Aplikasi tidak dijalankan.
  exit /b 1
)

if exist ".venv\Scripts\activate.bat" (
  call ".venv\Scripts\activate.bat"
)

start "" "http://127.0.0.1:%PORT%"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m uvicorn main:app --reload --port %PORT%
) else (
  echo Interpreter virtual environment tidak ditemukan.
  exit /b 1
)
