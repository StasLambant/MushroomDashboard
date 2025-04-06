@echo off
SETLOCAL

REM === Configuration ===
SET PI_USER=slambant1
SET PI_HOST=192.168.1.36
SET PI_PROJECT_DIR=/home/slambant1/Desktop/MushroomDashboard
SET GIT_BRANCH=main

echo.
echo Deploying code to Raspberry Pi (%PI_HOST%)...
echo --------------------------------------------

ssh %PI_USER%@%PI_HOST% "cd %PI_PROJECT_DIR% && git pull origin %GIT_BRANCH% && sudo systemctl restart flask_server.service"

echo --------------------------------------------
echo Deployment complete!
ENDLOCAL
pause
