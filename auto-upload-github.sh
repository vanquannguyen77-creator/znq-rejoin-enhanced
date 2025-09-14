#!/bin/bash

# Auto GitHub Upload Script
# Giúp upload ZNQ Rejoin lên GitHub một cách tự động

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_banner() {
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════╗"
    echo "║          AUTO GITHUB UPLOADER              ║"
    echo "║         ZNQ Rejoin Enhanced                ║"
    echo "╚════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_requirements() {
    print_status "Checking requirements..."
    
    # Check git
    if ! command -v git &> /dev/null; then
        print_error "Git not installed! Install with: pkg install git"
        exit 1
    fi
    
    # Check files
    local required_files=("znq-rejoin.py" "setup.sh" "run-znq.sh" "requirements.txt" "README.md")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "Required file missing: $file"
            exit 1
        fi
    done
    
    print_success "All requirements met"
}

check_github_auth() {
    print_status "Checking GitHub authentication..."
    
    # Check if gh CLI is authenticated
    if command -v gh &> /dev/null; then
        if gh auth status &>/dev/null; then
            print_success "GitHub CLI authenticated"
            return 0
        else
            print_warning "GitHub CLI not authenticated"
        fi
    fi
    
    # Check git credentials
    if git config --global user.name &>/dev/null && git config --global user.email &>/dev/null; then
        print_warning "Git configured but GitHub auth not verified"
    else
        print_warning "Git not fully configured"
    fi
    
    # Show authentication options
    cat << EOF

${YELLOW}[AUTHENTICATION REQUIRED]${NC}
You need to authenticate with GitHub first. Choose one:

${CYAN}Option 1: GitHub CLI (Recommended)${NC}
  pkg install gh
  gh auth login

${CYAN}Option 2: Personal Access Token${NC}
  1. Go to: https://github.com/settings/tokens
  2. Create token with 'repo' permissions
  3. Use token as password when pushing

${CYAN}Option 3: SSH Keys${NC}
  1. ssh-keygen -t ed25519 -C "your-email@example.com"
  2. Add ~/.ssh/id_ed25519.pub to GitHub

EOF

    read -p "Have you set up authentication? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Please set up authentication first"
        exit 1
    fi
    
    print_success "Authentication check completed"
}

get_user_input() {
    print_status "Getting repository information..."
    
    echo -n "Enter your GitHub username: "
    read -r GITHUB_USER
    
    echo -n "Enter repository name (default: znq-rejoin-enhanced): "
    read -r REPO_NAME
    REPO_NAME=${REPO_NAME:-znq-rejoin-enhanced}
    
    echo -n "Repository description (optional): "
    read -r REPO_DESC
    REPO_DESC=${REPO_DESC:-"ZNQ Rejoin Enhanced - Roblox Auto-Rejoin Tool for Android/Termux"}
    
    echo -n "Make repository public? (y/n, default: y): "
    read -r -n 1 IS_PUBLIC
    IS_PUBLIC=${IS_PUBLIC:-y}
    echo
    
    print_success "Repository info collected"
    print_status "Repository: https://github.com/$GITHUB_USER/$REPO_NAME"
}

setup_git_config() {
    print_status "Setting up git configuration..."
    
    if [ -z "$(git config --global user.name)" ]; then
        echo -n "Enter your name for git: "
        read -r GIT_NAME
        git config --global user.name "$GIT_NAME"
    fi
    
    if [ -z "$(git config --global user.email)" ]; then
        echo -n "Enter your email for git: "
        read -r GIT_EMAIL
        git config --global user.email "$GIT_EMAIL"
    fi
    
    print_success "Git configuration completed"
}

create_github_repo() {
    print_status "Creating GitHub repository..."
    
    # Check if gh CLI is available
    if command -v gh &> /dev/null; then
        print_status "Using GitHub CLI to create repository..."
        
        local visibility="public"
        if [[ $IS_PUBLIC =~ ^[Nn]$ ]]; then
            visibility="private"
        fi
        
        if gh repo create "$REPO_NAME" --"$visibility" --description "$REPO_DESC" --clone=false; then
            print_success "Repository created successfully via GitHub CLI"
            return 0
        else
            print_warning "GitHub CLI creation failed, continuing with manual setup"
        fi
    fi
    
    # Manual instructions
    cat << EOF

${YELLOW}[MANUAL SETUP REQUIRED]${NC}
GitHub CLI not available. Please create repository manually:

1. Go to https://github.com/new
2. Repository name: ${CYAN}$REPO_NAME${NC}
3. Description: ${CYAN}$REPO_DESC${NC}
4. Visibility: ${CYAN}$([ "$IS_PUBLIC" = "y" ] && echo "Public" || echo "Private")${NC}
5. ✅ Initialize with README
6. Click "Create repository"

Press Enter when repository is created...
EOF
    read -r
}

prepare_files() {
    print_status "Preparing files for upload..."
    
    # Make scripts executable
    chmod +x setup.sh run-znq.sh znq-rejoin.py
    
    # Update README with correct links
    if [ -f "README.md" ]; then
        print_status "Updating README links..."
        sed -i "s/\[YOUR-USERNAME\]/$GITHUB_USER/g" README.md
        sed -i "s/\[REPO-NAME\]/$REPO_NAME/g" README.md
        print_success "README updated with repository info"
    fi
    
    print_success "Files prepared"
}

upload_to_github() {
    print_status "Uploading to GitHub..."
    
    # Initialize git if needed
    if [ ! -d ".git" ]; then
        git init
        print_status "Git repository initialized"
    fi
    
    # Add remote
    local repo_url="https://github.com/$GITHUB_USER/$REPO_NAME.git"
    if git remote get-url origin &>/dev/null; then
        git remote set-url origin "$repo_url"
    else
        git remote add origin "$repo_url"
    fi
    
    # Add all files
    git add .
    print_status "Files staged for commit"
    
    # Create commit
    local commit_msg="Add ZNQ Rejoin Enhanced v1.0

🚀 Complete Roblox auto-rejoin tool for Android/Termux

Features:
- ✅ Enhanced stability and error handling  
- ✅ Beautiful dashboard UI with real-time monitoring
- ✅ Smart process detection (Android compatible)
- ✅ Safe database operations with backup
- ✅ Managed threading with graceful shutdown
- ✅ Auto setup script for easy installation

Installation:
curl -sL https://raw.githubusercontent.com/$GITHUB_USER/$REPO_NAME/main/setup.sh | bash"

    git commit -m "$commit_msg"
    print_success "Commit created"
    
    # Push to GitHub
    print_status "Pushing to GitHub..."
    if git push -u origin main; then
        print_success "Successfully uploaded to GitHub!"
    elif git push -u origin master; then
        print_success "Successfully uploaded to GitHub (master branch)!"
    else
        print_error "Failed to push to GitHub"
        print_status "You may need to authenticate with GitHub"
        print_status "Try: git push -u origin main"
        exit 1
    fi
}

create_release() {
    print_status "Creating release..."
    
    if command -v gh &> /dev/null; then
        print_status "Creating release via GitHub CLI..."
        
        local release_notes="🚀 **ZNQ Rejoin Enhanced v1.0 - Stable Release**

Complete Roblox auto-rejoin tool optimized for Android/Termux

**New Features:**
- ✅ Enhanced stability and error handling
- ✅ Beautiful dashboard UI with real-time monitoring  
- ✅ Smart process detection (Android compatible)
- ✅ Safe database operations with backup
- ✅ Managed threading with graceful shutdown
- ✅ Auto setup script for easy installation

**Quick Install:**
\`\`\`bash
curl -sL https://raw.githubusercontent.com/$GITHUB_USER/$REPO_NAME/main/setup.sh | bash
\`\`\`

**Usage:**
\`\`\`bash
./run-znq.sh --root
\`\`\`"

        if gh release create "v1.0.0" --title "ZNQ Rejoin Enhanced v1.0" --notes "$release_notes"; then
            print_success "Release created successfully!"
        else
            print_warning "Release creation failed, you can create it manually later"
        fi
    else
        print_status "Create release manually at: https://github.com/$GITHUB_USER/$REPO_NAME/releases/new"
    fi
}

show_final_info() {
    echo ""
    echo -e "${GREEN}🎉 SUCCESS! Your ZNQ Rejoin Enhanced is now on GitHub!${NC}"
    echo ""
    echo -e "${CYAN}Repository URL:${NC} https://github.com/$GITHUB_USER/$REPO_NAME"
    echo -e "${CYAN}Clone command:${NC} git clone https://github.com/$GITHUB_USER/$REPO_NAME.git"
    echo -e "${CYAN}Install command:${NC} curl -sL https://raw.githubusercontent.com/$GITHUB_USER/$REPO_NAME/main/setup.sh | bash"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Share the install command with users"
    echo "  2. Create a release (if not done automatically)"
    echo "  3. Add topics/tags to your repository"
    echo "  4. Star your own repo! ⭐"
    echo ""
}

main() {
    print_banner
    check_requirements
    check_github_auth
    get_user_input
    setup_git_config
    create_github_repo
    prepare_files
    upload_to_github
    create_release
    show_final_info
}

# Error handling
trap 'print_error "Upload failed! Check the error messages above."; exit 1' ERR

# Run main function
main "$@"
