# PowerShell script for WiseFlow environment setup and startup

# Function to print colored output
function Write-Info {
    param([string]$Message)
    Write-Host "✅ [INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  [WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ [ERROR] $Message" -ForegroundColor Red
}

# Check if uv is installed
try {
    $uvVersion = uv --version
    Write-Info "uv is installed: $uvVersion"
} catch {
    Write-Error "uv is not installed. Please install uv first:"
    Write-Host "  Invoke-WebRequest -Uri https://astral.sh/uv/install.ps1 -UseBasicParsing | Invoke-Expression"
    Write-Host "  Or visit: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
}

# Sync dependencies using uv
Write-Info "Syncing dependencies with uv..."
try {
    uv sync
} catch {
    Write-Error "Failed to sync dependencies with uv"
    exit 1
}

# Check if we're in a virtual environment
if ($env:VIRTUAL_ENV) {
    Write-Info "Already in virtual environment: $env:VIRTUAL_ENV"
} else {
    # Check if .venv exists
    if (Test-Path ".venv") {
        Write-Info "Activating virtual environment..."
        try {
            & .\.venv\Scripts\Activate.ps1
            if ($env:VIRTUAL_ENV) {
                Write-Info "Virtual environment activated: $env:VIRTUAL_ENV"
            } else {
                Write-Error "Failed to activate virtual environment"
                exit 1
            }
        } catch {
            Write-Error "Could not activate virtual environment. Please run 'uv sync' manually."
            exit 1
        }
    } else {
        Write-Warning "No .venv directory found. Running uv sync should have created it."
        Write-Info "Trying to activate virtual environment..."
        try {
            & .\.venv\Scripts\Activate.ps1
        } catch {
            Write-Error "Could not activate virtual environment. Please run 'uv sync' manually."
            exit 1
        }
    }
}

# Check and start PocketBase
$pocketbaseProcess = Get-Process -Name "pocketbase" -ErrorAction SilentlyContinue
$portInUse = Get-NetTCPConnection -LocalPort 8090 -ErrorAction SilentlyContinue

if (-not $pocketbaseProcess) {
    if (-not $portInUse) {
        Write-Info "Starting PocketBase..."
        Start-Process -FilePath ".\pb\pocketbase.exe" -ArgumentList "serve --http=127.0.0.1:8090" -NoNewWindow
    } else {
        Write-Warning "Port 8090 is already in use."
    }
} else {
    Write-Info "PocketBase is already running."
}

# Run the main application
Write-Info "Starting WiseFlow application..."
python core/run_task.py 