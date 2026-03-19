@echo off
setlocal

cd /d "%~dp0"
set "ROOT=%cd%"

echo [1/5] Checking Python...
where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python not found. Please install Python 3.11+ and add it to PATH.
  exit /b 1
)

echo [2/5] Checking npm...
where npm >nul 2>nul
if errorlevel 1 (
  echo [ERROR] npm not found. Please install Node.js 18+ and add it to PATH.
  exit /b 1
)

echo [3/5] Checking backend dependencies...
python -c "import fastapi,uvicorn" >nul 2>nul
if errorlevel 1 (
  echo Installing backend dependencies from backend\requirements.txt ...
  python -m pip install -r "%ROOT%\backend\requirements.txt"
  if errorlevel 1 (
    echo [ERROR] Failed to install backend dependencies.
    exit /b 1
  )
)

echo [4/5] Checking frontend dependencies...
if not exist "%ROOT%\frontend\node_modules" (
  echo Installing frontend dependencies...
  cd /d "%ROOT%\frontend"
  if exist "%ROOT%\frontend\package-lock.json" (
    call npm ci
  ) else (
    call npm install
  )
  if errorlevel 1 (
    echo [ERROR] Failed to install frontend dependencies.
    exit /b 1
  )
  cd /d "%ROOT%"
)

echo [5/5] Starting services...
start "NovelAS Backend" cmd /k "cd /d ""%ROOT%"" && python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"
start "NovelAS Frontend" cmd /k "cd /d ""%ROOT%\frontend"" && npm run dev"

timeout /t 2 >nul
start "" "http://localhost:5173"

echo.
echo NovelAS-Universal started:
echo - Backend:  http://127.0.0.1:8000/api/health
echo - Frontend: http://127.0.0.1:5173
echo.
echo Keep both opened terminal windows running.

endlocal
