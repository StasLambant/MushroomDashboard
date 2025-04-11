@echo off
SETLOCAL

REM === Configuration ===
SET PI_USER=slambant1
SET PI_HOST=raspberrypi.local
SET PI_PROJECT_DIR=/home/slambant1/Desktop/MushroomDashboard
SET GIT_BRANCH=main

echo.
echo Deploying code to Raspberry Pi (%PI_HOST%)...
echo --------------------------------------------

ssh %PI_USER%@%PI_HOST% "cd %PI_PROJECT_DIR% && git reset --hard HEAD && git clean -fdx -e __pycache__/ -e '*.pyc' -e '*.pyo' -e '*.pyd' -e '*.db' -e venv/ -e venv/** -e venv/**/* -e .venv/ -e .vscode/ -e .DS_Store -e Thumbs.db && git pull origin %GIT_BRANCH% && sudo systemctl restart flask_server.service"

echo --------------------------------------------
echo Deployment complete!
ENDLOCAL
pause
