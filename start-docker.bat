@echo off
echo Starting Odoo Docker Setup...
echo.

echo Checking Docker installation...
docker --version
if %ERRORLEVEL% NEQ 0 (
    echo Docker is not installed or not in PATH
    echo Please install Docker Desktop first
    pause
    exit /b 1
)

echo Checking Docker Compose installation...
docker-compose --version
if %ERRORLEVEL% NEQ 0 (
    echo Docker Compose is not installed or not in PATH
    echo Please install Docker Compose first
    pause
    exit /b 1
)

echo.
echo Pulling Docker images...
docker-compose pull

echo.
echo Building Odoo image...
docker-compose build

echo.
echo Starting services...
docker-compose up -d

echo.
echo Waiting for services to start...
timeout /t 30 /nobreak > nul

echo.
echo Checking service status...
docker-compose ps

echo.
echo Setup complete!
echo.
echo Access Odoo at: http://localhost:8069
echo Username: admin
echo Password: admin
echo.
echo To view logs: docker-compose logs -f
echo To stop services: docker-compose down
echo.

pause