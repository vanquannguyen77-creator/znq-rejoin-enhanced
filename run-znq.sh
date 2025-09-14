#!/bin/bash

# ZNQ Rejoin Launcher Script
# Quick launcher for ZNQ Rejoin tool

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_banner() {
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
    echo -e "${GREEN}                    🚀 Enhanced Rejoin Tool 🚀${NC}"
    echo ""
}

check_requirements() {
    echo -e "${BLUE}[INFO]${NC} Checking requirements..."
    
    # Check Python
    if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
        echo -e "${RED}[ERROR]${NC} Python not found! Please install Python first."
        echo "Run: pkg install python"
        exit 1
    fi
    
    # Check znq-rejoin.py
    if [ ! -f "znq-rejoin.py" ]; then
        echo -e "${RED}[ERROR]${NC} znq-rejoin.py not found!"
        echo "Please ensure the script is in the current directory"
        exit 1
    fi
    
    # Check dependencies
    python -c "import psutil, requests, rich" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}[WARNING]${NC} Some dependencies might be missing"
        echo "Run setup.sh to install all dependencies"
        read -p "Continue anyway? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    echo -e "${GREEN}[SUCCESS]${NC} Requirements check completed"
}

show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --root, -r     Run with root privileges (recommended)"
    echo "  --help, -h     Show this help message"
    echo "  --version, -v  Show version information"
    echo "  --debug, -d    Run in debug mode"
    echo "  --config, -c   Show current configuration"
    echo ""
    echo "Examples:"
    echo "  $0              # Run in normal mode"
    echo "  $0 --root       # Run with root privileges"
    echo "  $0 --debug      # Run with debug output"
    echo ""
}

show_config() {
    echo -e "${BLUE}[INFO]${NC} Current configuration:"
    
    if [ -f "roblox_config.json" ]; then
        if command -v jq &> /dev/null; then
            jq . roblox_config.json
        else
            cat roblox_config.json
        fi
    else
        echo -e "${YELLOW}[WARNING]${NC} No configuration file found (roblox_config.json)"
        echo "Configuration will be created on first run"
    fi
}

run_with_root() {
    echo -e "${PURPLE}[ROOT]${NC} Running with root privileges..."
    
    if ! command -v tsu &> /dev/null; then
        echo -e "${RED}[ERROR]${NC} 'tsu' not found! Install with: pkg install tsu"
        exit 1
    fi
    
    echo -e "${GREEN}[SUCCESS]${NC} Starting ZNQ Rejoin with root access..."
    tsu -c "python znq-rejoin.py"
}

run_normal() {
    echo -e "${BLUE}[INFO]${NC} Running in normal mode..."
    echo -e "${GREEN}[SUCCESS]${NC} Starting ZNQ Rejoin..."
    
    # Choose Python command
    if command -v python3 &> /dev/null; then
        python3 znq-rejoin.py
    else
        python znq-rejoin.py
    fi
}

run_debug() {
    echo -e "${YELLOW}[DEBUG]${NC} Running in debug mode..."
    echo -e "${BLUE}[INFO]${NC} Extra debug information will be displayed"
    
    # Set debug environment variable
    export ZNQ_DEBUG=1
    export PYTHONPATH=$PYTHONPATH:.
    
    if command -v python3 &> /dev/null; then
        python3 -u znq-rejoin.py
    else
        python -u znq-rejoin.py
    fi
}

main() {
    # Parse command line arguments
    case "$1" in
        --root|-r)
            print_banner
            check_requirements
            run_with_root
            ;;
        --help|-h)
            print_banner
            show_usage
            ;;
        --version|-v)
            print_banner
            echo -e "${GREEN}ZNQ Rejoin Enhanced v1.0${NC}"
            echo -e "${BLUE}Built for Android/Termux${NC}"
            echo -e "${CYAN}© 2024 ZNQ Team${NC}"
            ;;
        --config|-c)
            print_banner
            show_config
            ;;
        --debug|-d)
            print_banner
            check_requirements
            run_debug
            ;;
        "")
            print_banner
            check_requirements
            run_normal
            ;;
        *)
            print_banner
            echo -e "${RED}[ERROR]${NC} Unknown option: $1"
            echo ""
            show_usage
            exit 1
            ;;
    esac
}

# Error handling
trap 'echo -e "\n${RED}[ERROR]${NC} Script interrupted!"; exit 1' INT TERM

# Run main function
main "$@"
