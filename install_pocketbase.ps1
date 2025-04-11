# 1. Check if pocketbase exists
function Check-PocketBase {
    if (Test-Path ".\pb\pocketbase.exe") {
        Write-Host "Detected ./pb/pocketbase already exists, please delete it manually and try again" -ForegroundColor Red
        exit 1
    }
    
    if (-not (Test-Path ".\pb")) {
        New-Item -ItemType Directory -Path ".\pb"
    }
}

# 2. Get available versions
function Get-PocketBaseVersions {
    Write-Host "Fetching available versions..." -ForegroundColor Green
    $response = Invoke-RestMethod -Uri "https://api.github.com/repos/pocketbase/pocketbase/releases"
    $global:VERSIONS = $response | ForEach-Object { $_.tag_name }
    $global:LATEST_VERSION = $VERSIONS[0]
}

# 3. Select version with arrow keys
function Select-PocketBaseVersion {
    Clear-Host
    $current = 0
    $total = $VERSIONS.Count
    
    while ($true) {
        Clear-Host
        Write-Host "Available versions (Use ↑↓ arrows to select, Enter to confirm):" -ForegroundColor Yellow
        Write-Host "----------------------------------------"
        
        for ($i = 0; $i -lt $total; $i++) {
            if ($i -eq $current) {
                Write-Host ("-> " + $VERSIONS[$i]) -ForegroundColor Green
            } else {
                Write-Host ("   " + $VERSIONS[$i])
            }
        }
        
        $key = $host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        
        switch ($key.VirtualKeyCode) {
            38 { # Up arrow
                if ($current -gt 0) { $current-- }
            }
            40 { # Down arrow
                if ($current -lt ($total - 1)) { $current++ }
            }
            13 { # Enter
                $global:SELECTED_VERSION = $VERSIONS[$current]
                Write-Host "`nSelected version: $SELECTED_VERSION" -ForegroundColor Green
                return
            }
        }
    }
}

# 4. Download PocketBase
function Download-PocketBase {
    $versionNum = $SELECTED_VERSION -replace '^v'
    $fileName = "pocketbase_${versionNum}_windows_amd64.zip"
    $downloadUrl = "https://github.com/pocketbase/pocketbase/releases/download/$SELECTED_VERSION/$fileName"
    $outputPath = ".\pb\pocketbase.zip"
    
    Write-Host "Downloading PocketBase $SELECTED_VERSION..." -ForegroundColor Green
    Invoke-WebRequest -Uri $downloadUrl -OutFile $outputPath
    
    Write-Host "Extracting files..." -ForegroundColor Green
    Expand-Archive -Path $outputPath -DestinationPath ".\pb" -Force
    Remove-Item $outputPath
}

# 5. Configure admin account
function Configure-AdminAccount {
    Write-Host "`nConfiguring admin account" -ForegroundColor Yellow
    
    do {
        $email = Read-Host "Enter admin email"
    } while (-not ($email -match "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"))
    
    do {
        $password = Read-Host "Enter admin password (no '&' in the password and at least 10 characters)" -AsSecureString
        $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($password)
        $passwordText = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
    } while ($passwordText.Length -lt 10) # 修正为 10，与提示一致
    
    $global:ADMIN_EMAIL = $email
    $global:ADMIN_PASSWORD = $passwordText
}

# 6. Create admin account in PocketBase
function Create-AdminAccount {
    Write-Host "`nCreating PocketBase admin account..." -ForegroundColor Yellow
    
    try {
        $pbExe = ".\pb\pocketbase.exe"
        
        # Run migrations to initialize database
        Write-Host "Running database migrations..." -ForegroundColor Green
        $migrateOutput = & $pbExe migrate up 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Failed to run migrations: $migrateOutput" -ForegroundColor Red
            exit 1
        }
        
        # Create admin account
        Write-Host "Creating admin account for $ADMIN_EMAIL..." -ForegroundColor Green
        $createOutput = & $pbExe admin create $ADMIN_EMAIL $ADMIN_PASSWORD 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Failed to create admin account: $createOutput" -ForegroundColor Red
            exit 1
        }
        
        Write-Host "Admin account created successfully!" -ForegroundColor Green
    }
    catch {
        Write-Host "Error creating admin account: $_" -ForegroundColor Red
        exit 1
    }
}

# 7. Configure environment file
function Configure-Environment {
    if (-not (Test-Path ".\core\.env")) {
        Copy-Item "env_sample" -Destination ".\core\.env"
        Write-Host "Created new .env file from template" -ForegroundColor Green
    } else {
        Write-Host "Found existing .env file" -ForegroundColor Yellow
    }
    
    $envContent = Get-Content ".\core\.env"
    $envContent = $envContent -replace 'export PB_API_AUTH="[^"]*"', "export PB_API_AUTH=`"$ADMIN_EMAIL|$ADMIN_PASSWORD`""
    Set-Content ".\core\.env" $envContent
    
    Write-Host "Updated PB_API_AUTH in .env with new credentials" -ForegroundColor Green
}

# Main execution
function Main {
    Write-Host "Starting PocketBase installation..." -ForegroundColor Cyan
    Check-PocketBase
    Get-PocketBaseVersions
    Select-PocketBaseVersion
    Download-PocketBase
    Configure-AdminAccount
    Create-AdminAccount
    Configure-Environment
    Write-Host "PocketBase installation completed!" -ForegroundColor Green
}

# Run the script
Main
