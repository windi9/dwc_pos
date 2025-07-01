@echo off
echo Starting DWC POS Development Server...

:: Check if Poetry is installed and activated
:: This assumes poetry.exe is in your PATH or you're running from a Poetry shell
:: Alternatively, you might need to specify the full path to poetry if not in PATH

:: Optional: Activate Poetry shell if not already in one (can be tricky with batch)
:: For simplicity, assume user is already in Poetry shell or Poetry is in PATH.

echo Running Uvicorn...
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level info

echo Server stopped.
pause