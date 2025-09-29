@echo off
setlocal EnableDelayedExpansion

REM Windows Batch script for WiseFlow environment setup and startup
REM Equivalent functionality to run.sh

REM ANSI color codes for Windows 10+ (if supported)
for /F %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
set "GREEN=%ESC%[32m"
set "YELLOW=%ESC%[33m"
set "RED=%ESC%[31m"
set "NC=%ESC%[0m"

REM Function equivalents using labels and goto
goto :main

:print_info
echo %GREEN% [INFO]%NC% %~1
goto :eof

:print_warning
echo %YELLOW%  [WARNING]%NC% %~1
goto :eof

:print_error
echo %RED% [ERROR]%NC% %~1
goto :eof

:check_port_8090
REM Check if port 8090 is in use using netstat
netstat -an | findstr ":8090" | findstr "LISTENING" >nul 2>&1
if %ERRORLEVEL% == 0 (
    set "PORT_IN_USE=1"
) else (
    set "PORT_IN_USE=0"
)
goto :eof

:check_pocketbase_process
REM Check if pocketbase process is running
tasklist | findstr /i "pocketbase.exe" >nul 2>&1
if %ERRORLEVEL% == 0 (
    set "PB_RUNNING=1"
) else (
    set "PB_RUNNING=0"
)
goto :eof

:main

REM Check if uv is installed
call :print_info "Checking for uv installation..."
uv --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    call :print_error "uv is not installed. Please install uv first:"
    echo   powershell -c "Invoke-WebRequest -Uri https://astral.sh/uv/install.ps1 -UseBasicParsing | Invoke-Expression"
    echo   Or visit: https://docs.astral.sh/uv/getting-started/installation/
    exit /b 1
)

REM Sync dependencies using uv
call :print_info "Syncing dependencies with uv..."
uv sync
if %ERRORLEVEL% neq 0 (
    call :print_error "Failed to sync dependencies with uv"
    exit /b 1
)

REM Check if we're already in a virtual environment
if defined VIRTUAL_ENV (
    call :print_info "Already in virtual environment: %VIRTUAL_ENV%"
) else (
    REM Check if .venv exists
    if exist ".venv" (
        call :print_info "Activating virtual environment..."
        if exist ".venv\Scripts\activate.bat" (
            call .venv\Scripts\activate.bat
            if defined VIRTUAL_ENV (
                call :print_info "Virtual environment activated: %VIRTUAL_ENV%"
            ) else (
                call :print_error "Failed to activate virtual environment"
                exit /b 1
            )
        ) else (
            call :print_error "Virtual environment activation script not found"
            exit /b 1
        )
    ) else (
        call :print_warning "No .venv directory found. Running uv sync should have created it."
        call :print_info "Trying to activate virtual environment..."
        if exist ".venv\Scripts\activate.bat" (
            call .venv\Scripts\activate.bat
        ) else (
            call :print_error "Could not activate virtual environment. Please run 'uv sync' manually."
            exit /b 1
        )
    )
)

REM Check and start PocketBase
call :check_port_8090
call :check_pocketbase_process

if !PORT_IN_USE! == 1 (
    call :print_info "Port 8090 is already in use, checking if it's PocketBase..."
    
    if !PB_RUNNING! == 1 (
        call :print_info "PocketBase is already running."
    ) else (
        call :print_warning "Port 8090 is in use by another process. Please stop it first or use a different port."
    )
) else (
    REM Port is available, check if pocketbase process exists anyway
    if !PB_RUNNING! == 1 (
        call :print_warning "PocketBase process found but not using port 8090. It might have crashed."
        call :print_info "Attempting to start PocketBase on port 8090..."
    ) else (
        call :print_info "Starting PocketBase..."
    )
    
    REM Start PocketBase
    if exist "pb\pocketbase.exe" (
        start /b "" "pb\pocketbase.exe" serve --http=127.0.0.1:8090
        
        REM Give it a moment to start and check if it's running
        timeout /t 2 /nobreak >nul
        call :check_port_8090
        if !PORT_IN_USE! == 1 (
            call :print_info "PocketBase started successfully on port 8090."
        ) else (
            call :print_error "Failed to start PocketBase. Please check for errors."
        )
    ) else (
        call :print_error "PocketBase executable not found at pb\pocketbase.exe"
        exit /b 1
    )
)

REM Run the main application
call :print_info "Starting WiseFlow application..."
python core\run_task.py

REM End of script
endlocal
