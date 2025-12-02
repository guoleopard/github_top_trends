@echo off
set VENV_DIR=venv
if not exist "%VENV_DIR%" (
    echo Creating virtual environment...
    python -m venv %VENV_DIR%
)

echo Activating virtual environment...
call %VENV_DIR%\Scripts\activate.bat
echo Virtual environment activated.
echo.
echo To install dependencies: pip install -r requirements.txt
echo To run the crawler: python github_trending_crawler.py