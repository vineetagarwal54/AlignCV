@echo off
REM Quick start script for AlignCV

echo ========================================
echo AlignCV - Quick Start
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "myenv\Scripts\activate.bat" (
    echo Error: Virtual environment not found!
    echo Please create it first: python -m venv myenv
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call myenv\Scripts\activate.bat

REM Check for API key
if "%GOOGLE_API_KEY%"=="" (
    echo.
    echo ERROR: GOOGLE_API_KEY not set!
    echo.
    echo Set it with:
    echo   set GOOGLE_API_KEY=your-api-key-here
    echo.
    pause
    exit /b 1
)

echo API Key: %GOOGLE_API_KEY:~0,10%...
echo.

REM Run setup test
echo Running setup test...
python test_setup.py

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo To start the application:
echo   1. Backend:  uvicorn main:app --reload
echo   2. Streamlit: streamlit run streamlit_app.py
echo.
pause
