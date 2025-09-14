#!/bin/bash

# ZNQ Rejoin Setup Script for Android/Termux
# Author: ZNQ Enhanced
# Version: 1.0

set -e

echo "🚀 ZNQ Rejoin Setup Starting..."
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on Android/Termux
check_environment() {
    print_status "Checking environment..."
    
    if [ ! -d "/data/data/com.termux" ]; then
        print_warning "This script is designed for Termux on Android"
        read -p "Continue anyway? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    print_success "Environment check completed"
}

# Update packages
update_packages() {
    print_status "Updating packages..."
    
    if ! pkg update -y; then
        print_error "Failed to update packages"
        exit 1
    fi
    
    if ! pkg upgrade -y; then
        print_error "Failed to upgrade packages" 
        exit 1
    fi
    
    print_success "Packages updated successfully"
}

# Install essential packages
install_essentials() {
    print_status "Installing essential packages..."
    
    local packages=(
        "python"
        "python-pip" 
        "git"
        "wget"
        "curl"
        "openssh"
        "termux-api"
        "root-repo"
        "tsu"
    )
    
    for package in "${packages[@]}"; do
        print_status "Installing $package..."
        if ! pkg install -y "$package"; then
            print_warning "Failed to install $package, continuing..."
        fi
    done
    
    print_success "Essential packages installed"
}

# Upgrade pip and install Python packages
install_python_packages() {
    print_status "Installing Python packages..."
    
    # Upgrade pip first
    print_status "Upgrading pip..."
    if ! pip install --upgrade pip setuptools wheel; then
        print_error "Failed to upgrade pip"
        exit 1
    fi
    
    # Core packages (required)
    local core_packages=(
        "psutil"
        "requests"
        "urllib3"
        "certifi"
    )
    
    print_status "Installing core packages..."
    for package in "${core_packages[@]}"; do
        print_status "Installing $package..."
        if ! pip install --no-cache-dir "$package"; then
            print_error "Failed to install required package: $package"
            exit 1
        fi
    done
    
    # UI packages
    local ui_packages=(
        "rich"
        "prettytable"
        "colorama"
        "textual"
        "tqdm"
    )
    
    print_status "Installing UI packages..."
    for package in "${ui_packages[@]}"; do
        print_status "Installing $package..."
        if ! pip install --no-cache-dir "$package"; then
            print_warning "Failed to install UI package: $package"
        fi
    done
    
    # Network packages
    local network_packages=(
        "httpx"
        "aiohttp"
        "websockets"
        "discord-webhook"
    )
    
    print_status "Installing network packages..."
    for package in "${network_packages[@]}"; do
        print_status "Installing $package..."
        if ! pip install --no-cache-dir "$package"; then
            print_warning "Failed to install network package: $package"
        fi
    done
    
    # Utility packages
    local utility_packages=(
        "pytz"
        "schedule" 
        "python-crontab"
        "qrcode[pil]"
    )
    
    print_status "Installing utility packages..."
    for package in "${utility_packages[@]}"; do
        print_status "Installing $package..."
        if ! pip install --no-cache-dir "$package"; then
            print_warning "Failed to install utility package: $package"
        fi
    done
    
    print_success "Python packages installation completed"
}

# Setup Termux permissions
setup_permissions() {
    print_status "Setting up permissions..."
    
    # Storage access
    print_status "Setting up storage access..."
    if ! termux-setup-storage; then
        print_warning "Failed to setup storage access"
    fi
    
    # Wake lock
    print_status "Acquiring wake lock..."
    if ! termux-wake-lock; then
        print_warning "Failed to acquire wake lock"
    fi
    
    print_success "Permissions setup completed"
}

# Test installation
test_installation() {
    print_status "Testing installation..."
    
    # Test Python imports
    python3 -c "
import sys
import psutil
import requests
import rich
import prettytable
print('✅ Core packages: OK')

try:
    import colorama
    import textual
    import tqdm
    print('✅ UI packages: OK')
except ImportError as e:
    print(f'⚠️  UI packages: {e}')

try:
    import httpx
    import aiohttp
    print('✅ Network packages: OK') 
except ImportError as e:
    print(f'⚠️  Network packages: {e}')

try:
    import pytz
    import schedule
    print('✅ Utility packages: OK')
except ImportError as e:
    print(f'⚠️  Utility packages: {e}')

print('🎉 Installation test completed!')
"
    
    if [ $? -eq 0 ]; then
        print_success "Installation test passed!"
    else
        print_error "Installation test failed!"
        exit 1
    fi
}

# Download ZNQ Rejoin script
download_script() {
    print_status "Checking for znq-rejoin.py..."
    
    if [ ! -f "znq-rejoin.py" ]; then
        print_warning "znq-rejoin.py not found in current directory"
        print_status "Please ensure znq-rejoin.py is in the same directory as this setup script"
        
        # Check if user wants to continue anyway
        read -p "Continue without downloading the script? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        print_success "znq-rejoin.py found"
        
        # Make it executable
        chmod +x znq-rejoin.py
        print_success "Made znq-rejoin.py executable"
    fi
}

# Create launcher script
create_launcher() {
    print_status "Creating launcher script..."
    
    cat > run-znq.sh << 'EOF'
#!/bin/bash

# ZNQ Rejoin Launcher
# Quick launcher for ZNQ Rejoin tool

echo "🚀 Starting ZNQ Rejoin..."

# Check if script exists
if [ ! -f "znq-rejoin.py" ]; then
    echo "❌ znq-rejoin.py not found!"
    echo "Please ensure the script is in the current directory"
    exit 1
fi

# Check if running with root (optional)
if [ "$1" = "--root" ] || [ "$1" = "-r" ]; then
    echo "🔒 Running with root privileges..."
    if command -v tsu &> /dev/null; then
        tsu -c "python znq-rejoin.py"
    else
        echo "❌ tsu not found! Install with: pkg install tsu"
        exit 1
    fi
else
    echo "🔧 Running in normal mode..."
    python znq-rejoin.py
fi
EOF

    chmod +x run-znq.sh
    print_success "Launcher script created: run-znq.sh"
}

# Create uninstaller
create_uninstaller() {
    print_status "Creating uninstaller..."
    
    cat > uninstall-znq.sh << 'EOF'
#!/bin/bash

# ZNQ Rejoin Uninstaller
echo "🗑️  ZNQ Rejoin Uninstaller"
echo "=========================="

read -p "Are you sure you want to uninstall ZNQ Rejoin? (y/n): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing Python packages..."
    pip uninstall -y psutil requests rich prettytable colorama textual tqdm httpx aiohttp websockets discord-webhook pytz schedule python-crontab qrcode
    
    echo "Removing scripts..."
    rm -f znq-rejoin.py run-znq.sh uninstall-znq.sh setup.sh
    rm -f requirements.txt README.md
    rm -f roblox_config.json
    
    echo "✅ ZNQ Rejoin uninstalled successfully!"
else
    echo "❌ Uninstallation cancelled"
fi
EOF

    chmod +x uninstall-znq.sh
    print_success "Uninstaller created: uninstall-znq.sh"
}

# Main installation function
main() {
    echo -e "${CYAN}"
    cat << "EOF"
    ███████╗███╗   ██╗ ██████╗     ██████╗ ███████╗      ██╗ ██████╗ ██╗███╗   ██╗
    ╚══███╔╝████╗  ██║██╔═══██╗    ██╔══██╗██╔════╝      ██║██╔═══██╗██║████╗  ██║
      ███╔╝ ██╔██╗ ██║██║   ██║    ██████╔╝█████╗        ██║██║   ██║██║██╔██╗ ██║
     ███╔╝  ██║╚██╗██║██║▄▄ ██║    ██╔══██╗██╔══╝   ██   ██║██║   ██║██║██║╚██╗██║
    ███████╗██║ ╚████║╚██████╔╝    ██║  ██║███████╗ ╚█████╔╝╚██████╔╝██║██║ ╚████║
    ╚══════╝╚═╝  ╚═══╝ ╚══▀▀═╝     ╚═╝  ╚═╝╚══════╝  ╚════╝  ╚═════╝ ╚═╝╚═╝  ╚═══╝
EOF
    echo -e "${NC}"
    echo "                    🚀 Enhanced Setup Script 🚀"
    echo ""
    
    print_status "Starting installation process..."
    
    # Run installation steps
    check_environment
    update_packages
    install_essentials
    install_python_packages
    setup_permissions
    test_installation
    download_script
    create_launcher
    create_uninstaller
    
    echo ""
    echo -e "${GREEN}🎉 Installation completed successfully!${NC}"
    echo ""
    echo "📋 Next steps:"
    echo "  1. Run the tool: ${CYAN}./run-znq.sh${NC}"
    echo "  2. Run with root: ${CYAN}./run-znq.sh --root${NC}"
    echo "  3. Uninstall: ${CYAN}./uninstall-znq.sh${NC}"
    echo ""
    echo "📁 Files created:"
    echo "  - run-znq.sh (launcher)"
    echo "  - uninstall-znq.sh (uninstaller)" 
    echo "  - requirements.txt (package list)"
    echo ""
    print_success "Setup completed! Enjoy ZNQ Rejoin! 🚀"
}

# Error handling
trap 'print_error "Setup failed! Check the error messages above."; exit 1' ERR

# Run main function
main "$@"
