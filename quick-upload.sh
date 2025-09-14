#!/bin/bash

# Quick GitHub Upload Script
# Sử dụng: ./quick-upload.sh "commit message"

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Get commit message
COMMIT_MSG=${1:-"Update code $(date +'%Y-%m-%d %H:%M:%S')"}

print_status "Quick GitHub Upload Starting..."

# Check if git repo exists
if [ ! -d ".git" ]; then
    print_error "Not a git repository! Run 'git init' first."
    exit 1
fi

# Check if remote exists
if ! git remote get-url origin &>/dev/null; then
    print_error "No remote 'origin' found!"
    echo "Add remote with: git remote add origin https://github.com/USERNAME/REPO.git"
    exit 1
fi

# Add all changes
print_status "Adding files..."
git add .

# Check if there are changes
if git diff --staged --quiet; then
    print_error "No changes to commit"
    exit 1
fi

# Commit
print_status "Creating commit..."
git commit -m "$COMMIT_MSG"

# Push
print_status "Pushing to GitHub..."
if git push; then
    print_success "Successfully uploaded to GitHub!"
    
    # Get repository URL
    REPO_URL=$(git remote get-url origin | sed 's/\.git$//')
    echo -e "${GREEN}Repository:${NC} $REPO_URL"
    
    # Show latest commit
    echo -e "${GREEN}Latest commit:${NC} $(git log --oneline -1)"
else
    print_error "Failed to push to GitHub"
    echo "Check your authentication and try again"
    exit 1
fi
