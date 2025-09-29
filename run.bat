@echo off
setlocal EnableDelayedExpansion

REM Colors for output (using ANSI escape codes)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "NC=[0m"

REM Enable ANSI color support in Windows 10/11
for /f "tokens=2 delims=[]" %%i in ('ver') do set winver=%%i
for /f "tokens=2,3,4 delims=. " %%i in ("!winver!") do (
    if %%i GEQ 10 (
        REM Enable virtual terminal processing for color support
        reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1
    )
)

REM Function to print colored output
goto :main

:print_info
echo %GREEN%✅ [INFO]%NC% %~1
goto :eof

:print_warning
echo %YELLOW%⚠️  [WARNING]%NC% %~1
goto :eof

:print_error
echo %RED%❌ [ERROR]%NC% %~1
goto :eof

:main

REM Check if uv is installed
call :print_info "Checking if uv is installed..."
uv --version >nul 2>&1
if errorlevel 1 (
    call :print_error "uv is not installed. Please install uv first:"
    echo   curl -LsSf https://astral.sh/uv/install.sh ^| sh
    echo   Or visit: https://docs.astral.sh/uv/getting-started/installation/
    echo   For Windows: winget install astral-sh.uv
    pause
    exit /b 1
)

REM Sync dependencies using uv
call :print_info "Syncing dependencies with uv..."
uv sync
if errorlevel 1 (
    call :print_error "Failed to sync dependencies with uv"
    pause
    exit /b 1
)

REM Check if we're already in a virtual environment
if defined VIRTUAL_ENV (
    call :print_info "Already in virtual environment: %VIRTUAL_ENV%"
) else (
    REM Check if .venv exists
    if exist ".venv" (
        call :print_info "Activating virtual environment..."
        call .venv\Scripts\activate.bat
        if defined VIRTUAL_ENV (
            call :print_info "Virtual environment activated: %VIRTUAL_ENV%"
        ) else (
            call :print_error "Failed to activate virtual environment"
            pause
            exit /b 1
        )
    ) else (
        call :print_warning "No .venv directory found. Running uv sync should have created it."
        call :print_info "Trying to activate virtual environment..."
        call .venv\Scripts\activate.bat >nul 2>&1
        if not defined VIRTUAL_ENV (
            call :print_error "Could not activate virtual environment. Please run 'uv sync' manually."
            pause
            exit /b 1
        )
    )
)

REM Check and start PocketBase
REM First check if port 8090 is in use
call :print_info "Checking if port 8090 is available..."
netstat -an | findstr ":8090" >nul 2>&1
if not errorlevel 1 (
    call :print_info "Port 8090 is already in use, checking if it's PocketBase..."
    
    REM Check if it's actually pocketbase using the port
    tasklist /FI "IMAGENAME eq pocketbase.exe" 2>nul | findstr /I "pocketbase.exe" >nul
    if not errorlevel 1 (
        call :print_info "PocketBase is already running."
    ) else (
        call :print_warning "Port 8090 is in use by another process. Please stop it first or use a different port."
    )
) else (
    REM Port is available, check if pocketbase process exists anyway
    tasklist /FI "IMAGENAME eq pocketbase.exe" 2>nul | findstr /I "pocketbase.exe" >nul
    if not errorlevel 1 (
        call :print_warning "PocketBase process found but not using port 8090. It might have crashed."
        call :print_info "Attempting to start PocketBase on port 8090..."
    ) else (
        call :print_info "Starting PocketBase..."
    )
    
    REM Start PocketBase
    start /B pb\pocketbase.exe serve --http=127.0.0.1:8090
    
    REM Give it a moment to start and check if it's running
    timeout /t 2 /nobreak >nul
    netstat -an | findstr ":8090" >nul 2>&1
    if not errorlevel 1 (
        call :print_info "PocketBase started successfully on port 8090."
    ) else (
        call :print_error "Failed to start PocketBase. Please check for errors."
    )
)

REM Run the main application
call :print_info "Starting WiseFlow application..."
python core\run_task.py

pause
