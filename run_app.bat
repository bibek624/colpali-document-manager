@echo off
echo ========================================
echo   Document Manager - Streamlit App
echo ========================================
echo.

REM Check if Qdrant is accessible
echo Checking Qdrant connection...
curl -s http://localhost:6333 >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Cannot connect to Qdrant at http://localhost:6333
    echo Please ensure Qdrant is running before using the app.
    echo.
    echo To start Qdrant with Docker:
    echo   docker run -p 6333:6333 qdrant/qdrant
    echo.
    pause
)

echo.
echo Starting Document Manager...
echo.

REM Navigate to the document_manager directory
cd /d "%~dp0"

REM Run Streamlit
streamlit run app.py

pause





