
REM Check virtual environment exists
if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] Virtual environment not found at .venv\Scripts\python.exe
  echo Create it first with:
  echo    python -m venv .venv
  exit /b 1
)

REM Activate virtual environment
call ".venv\Scripts\activate.bat"

REM Install dependencies if requirements file exists
if exist "requirements.txt" (
  echo Installing/updating dependencies...
  python -m pip install -r requirements.txt
)

REM Launch Streamlit app
echo Starting Streamlit app...
streamlit run app.py

endlocal
