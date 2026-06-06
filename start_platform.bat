@echo off
echo =========================================================================
echo  AI Demand Forecasting & Inventory Intelligence Platform - Desktop Launcher
echo =========================================================================
echo.
echo [1/3] Activating Virtual Environment...
call "%~dp0..\forecast_env\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate forecast_env virtual environment.
    pause
    exit /b %errorlevel%
)

echo [2/3] Checking and applying database migrations...
python "%~dp0manage.py" migrate
if %errorlevel% neq 0 (
    echo [ERROR] Database migration check failed.
    pause
    exit /b %errorlevel%
)

echo [3/3] Opening your browser to the platform portal...
start http://127.0.0.1:8000/

echo.
echo =========================================================================
echo  SERVER LAUNCHED! 
echo  * Keep this terminal window open to run the platform.
echo  * Minimize it to let it run in the background.
echo  * To stop the server, simply close this terminal window.
echo =========================================================================
echo.
python "%~dp0manage.py" runserver
pause
