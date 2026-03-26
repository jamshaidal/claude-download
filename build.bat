@echo off
echo Building Video Downloader for Production...
echo.

REM Build frontend
echo [1/2] Building React frontend...
cd frontend
call npm install
call npm run build
if errorlevel 1 (
    echo ERROR: Frontend build failed
    pause
    exit /b 1
)
cd ..

echo.
echo [2/2] Backend is ready (no build step required)
echo.
echo Build complete!
echo.
echo To test locally:
echo   cd backend && python app.py
echo   Then open http://localhost:5000
echo.
echo To deploy, follow DEPLOYMENT.md instructions
echo.
pause