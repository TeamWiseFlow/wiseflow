#!/bin/bash

# 1. Check if pocketbase exists
check_pocketbase() {
    if [ -f "./pb/pocketbase" ]; then
        echo "Detected ./pb/pocketbase already exists, please delete it manually and try again"
        exit 1
    fi
    
    # Create directory if it doesn't exist
    if [ ! -d "./pb" ]; then
        mkdir -p ./pb
    fi
}

# 2. Get available versions
get_versions() {
    echo "Fetching available versions..."
    VERSIONS=($(curl -s https://api.github.com/repos/pocketbase/pocketbase/releases | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/'))
    LATEST_VERSION=${VERSIONS[0]}
}

# 3. Select version with arrow keys
select_version() {
    # Clear screen
    clear
    
    # Array to store versions
    local versions=("${VERSIONS[@]}")
    local current=0
    local key
    local total=${#versions[@]}
    
    while true; do
        # Clear screen
        clear
        echo "Available versions (Use ↑↓ arrows to select, Enter to confirm):"
        echo "----------------------------------------"
        
        # Display versions
        for i in "${!versions[@]}"; do
            if [ $i -eq $current ]; then
                echo -e "\033[32m-> ${versions[$i]}\033[0m"
            else
                echo "   ${versions[$i]}"
            fi
        done
        
        # Read a single character
        read -rsn1 key
        
        # Special key sequences
        if [[ $key = $'\x1b' ]]; then
            read -rsn2 key
            case $key in
                '[A') # Up arrow
                    ((current--))
                    [ $current -lt 0 ] && current=$((total - 1))
                    ;;
                '[B') # Down arrow
                    ((current++))
                    [ $current -ge $total ] && current=0
                    ;;
            esac
        elif [[ $key = "" ]]; then # Enter key
            SELECTED_VERSION=${versions[$current]}
            break
        fi
    done
    
    echo -e "\nSelected version: $SELECTED_VERSION"
}

# 4. Download corresponding system version
download_pocketbase() {
    # Detect OS and architecture
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    ARCH=$(uname -m)
    
    # Remove 'v' prefix from version number
    VERSION_NUM=${SELECTED_VERSION#v}
    
    case "$OS" in
        "darwin") 
            case "$ARCH" in
                "x86_64") FILENAME="pocketbase_${VERSION_NUM}_darwin_amd64.zip" ;;
                "arm64") FILENAME="pocketbase_${VERSION_NUM}_darwin_arm64.zip" ;;
            esac
            ;;
        "linux")
            case "$ARCH" in
                "x86_64") FILENAME="pocketbase_${VERSION_NUM}_linux_amd64.zip" ;;
                "aarch64") FILENAME="pocketbase_${VERSION_NUM}_linux_arm64.zip" ;;
            esac
            ;;
        *)
            echo "Unsupported operating system"
            exit 1
            ;;
    esac

    # Download and extract
    DOWNLOAD_URL="https://github.com/pocketbase/pocketbase/releases/download/${SELECTED_VERSION}/${FILENAME}"
    echo "Downloading: $DOWNLOAD_URL"
    
    # Download with retry mechanism
    MAX_RETRIES=3
    RETRY_COUNT=0
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if curl -L "$DOWNLOAD_URL" -o "./pb/${FILENAME}" --fail --silent --show-error; then
            if [ -f "./pb/${FILENAME}" ] && [ -s "./pb/${FILENAME}" ]; then
                echo "Download completed successfully"
                break
            fi
        fi
        
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            echo "Download failed, retrying ($RETRY_COUNT/$MAX_RETRIES)..."
            sleep 2
        else
            echo "Download failed after $MAX_RETRIES attempts"
            exit 1
        fi
    done
    
    # Extract only the pocketbase executable
    cd ./pb || exit 1
    
    if ! unzip -j -o "${FILENAME}" "pocketbase" > /dev/null 2>&1; then
        echo "Failed to extract pocketbase executable"
        cd ..
        exit 1
    fi
    
    rm "${FILENAME}"  # Remove the zip file
    
    if [ ! -f "pocketbase" ]; then
        echo "pocketbase executable not found after extraction"
        cd ..
        exit 1
    fi
    
    chmod +x pocketbase
    cd ..
    
    echo "Successfully installed pocketbase"
}

# Validate email format
validate_email() {
    local email=$1
    if [[ ! "$email" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
        return 1
    fi
    return 0
}

# Validate password requirements
validate_password() {
    local password=$1
    # Check minimum length of 8 characters
    if [ ${#password} -lt 8 ]; then
        return 1
    fi
    return 0
}

# 5. Configure admin account
configure_admin() {
    local valid_input=false
    
    while [ "$valid_input" = false ]; do
        # Get email
        while true; do
            echo "Please set superuser email:"
            read EMAIL
            
            if validate_email "$EMAIL"; then
                break
            else
                echo "Invalid email format. Please try again."
            fi
        done
        
        # Get password
        while true; do
            echo "Please set superuser password (minimum 8 characters):"
            read -s PASSWORD
            echo
            
            if validate_password "$PASSWORD"; then
                # Confirm password
                echo "Please confirm password:"
                read -s PASSWORD_CONFIRM
                echo
                
                if [ "$PASSWORD" = "$PASSWORD_CONFIRM" ]; then
                    valid_input=true
                    break
                else
                    echo "Passwords do not match. Please try again."
                fi
            else
                echo "Password must be at least 8 characters long. Please try again."
            fi
        done
    done

    cd ./pb
    ./pocketbase migrate up
    
    # Try to create superuser
    if ! ./pocketbase --dev superuser create "$EMAIL" "$PASSWORD"; then
        echo "Failed to create superuser. Please check the error message above."
        exit 1
    fi
    cd ..
    
    echo "Superuser created successfully!"
}

# 6. Configure environment file
configure_env() {
    # Create .env if it doesn't exist
    if [ ! -f "./core/.env" ]; then
        mkdir -p ./core
        cp env_sample ./core/.env
        echo "Created new .env file from template"
    else
        echo "Found existing .env file"
    fi
    
    # Update authentication info in environment file using sed
    if [ "$(uname)" = "Darwin" ]; then
        # macOS version
        sed -i '' 's/export PB_API_AUTH="[^"]*"/export PB_API_AUTH="'$EMAIL'|'$PASSWORD'"/' "./core/.env"
    else
        # Linux version
        sed -i 's/export PB_API_AUTH="[^"]*"/export PB_API_AUTH="'$EMAIL'|'$PASSWORD'"/' "./core/.env"
    fi
    
    echo "Updated PB_API_AUTH in .env with new credentials"
}

main() {
    echo "Starting PocketBase installation..."
    check_pocketbase
    get_versions
    select_version
    download_pocketbase
    configure_admin
    configure_env
    echo "PocketBase installation completed!"
}

main