@echo off
setlocal EnableExtensions

cd /d "%~dp0"

if not exist "requirements.txt" (
  echo requirements.txt tidak ditemukan.
  exit /b 1
)

set "PYTHON_CMD="
call :resolve_python
if errorlevel 1 exit /b 1

set "REBUILD_VENV=0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -c "import sys" >nul 2>&1
  if errorlevel 1 set "REBUILD_VENV=1"
) else (
  set "REBUILD_VENV=1"
)

if "%REBUILD_VENV%"=="1" (
  if exist ".venv" (
    echo Virtual environment rusak atau tidak lengkap. Membuat ulang...
    rmdir /s /q ".venv"
  ) else (
    echo Membuat virtual environment...
  )
  call %PYTHON_CMD% -m venv ".venv"
  if errorlevel 1 (
    echo Gagal membuat virtual environment.
    exit /b 1
  )
)

call ".venv\Scripts\activate.bat"
if errorlevel 1 (
  echo Gagal mengaktifkan virtual environment.
  exit /b 1
)

python -m ensurepip --upgrade >nul 2>&1

echo Mengecek dan menginstall dependencies...
python -m pip install --upgrade pip >nul 2>&1
if errorlevel 1 (
  echo Gagal mengupdate pip.
  exit /b 1
)

python -m pip install -r requirements.txt
if errorlevel 1 (
  echo Gagal menginstall dependency dari requirements.txt.
  exit /b 1
)

echo Mengecek browser Playwright...
python -m playwright install
if errorlevel 1 (
  echo Gagal menginstall browser Playwright.
  exit /b 1
)

echo Setup selesai.
exit /b 0

:resolve_python
where py >nul 2>&1
if not errorlevel 1 (
  py -3 -c "import sys" >nul 2>&1
  if not errorlevel 1 (
    set "PYTHON_CMD=py -3"
    goto :python_ready
  )
)

where python >nul 2>&1
if not errorlevel 1 (
  python -c "import sys" >nul 2>&1
  if not errorlevel 1 (
    set "PYTHON_CMD=python"
    goto :python_ready
  )
)

echo Python belum tersedia. Mencoba install otomatis via winget...
where winget >nul 2>&1
if errorlevel 1 (
  echo winget tidak ditemukan. Install Python manual lalu jalankan ulang.
  exit /b 1
)

winget install --id Python.Python.3.11 -e --accept-package-agreements --accept-source-agreements --scope user >nul
if errorlevel 1 (
  winget install --id Python.Python.3.12 -e --accept-package-agreements --accept-source-agreements --scope user >nul
)

set "PATH=%PATH%;%LocalAppData%\Programs\Python\Python311\;%LocalAppData%\Programs\Python\Python311\Scripts\;%LocalAppData%\Programs\Python\Python312\;%LocalAppData%\Programs\Python\Python312\Scripts\;"

where py >nul 2>&1
if not errorlevel 1 (
  py -3 -c "import sys" >nul 2>&1
  if not errorlevel 1 (
    set "PYTHON_CMD=py -3"
    goto :python_ready
  )
)

where python >nul 2>&1
if not errorlevel 1 (
  python -c "import sys" >nul 2>&1
  if not errorlevel 1 (
    set "PYTHON_CMD=python"
    goto :python_ready
  )
)

echo Python masih tidak terdeteksi setelah auto-install.
exit /b 1

:python_ready
for /f "delims=" %%V in ('%PYTHON_CMD% --version 2^>^&1') do echo Menggunakan %%V
exit /b 0
