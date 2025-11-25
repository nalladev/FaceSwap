#!/bin/bash

# FaceSwap Release Creation Script
# Creates releases using GitHub CLI

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "Not in a git repository"
        exit 1
    fi
    
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI (gh) is not installed"
        echo "Install it from: https://cli.github.com/"
        exit 1
    fi
    
    if ! gh auth status &> /dev/null; then
        print_error "GitHub CLI is not authenticated"
        echo "Run: gh auth login"
        exit 1
    fi
    
    print_success "All prerequisites met"
}

get_version_input() {
    echo
    print_status "Current repository: $(gh repo view --json nameWithOwner -q .nameWithOwner)"
    
    print_status "Existing releases:"
    gh release list --limit 5 || echo "No existing releases"
    
    echo
    read -p "Enter version tag (e.g., v1.0.1): " VERSION
    
    if [[ ! "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-.*)?$ ]]; then
        print_warning "Version should follow semantic versioning (e.g., v1.0.1)"
        read -p "Continue anyway? (y/N): " confirm
        if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    echo "Selected version: $VERSION"
}

create_optimized_release() {
    local platform=$1
    local exclude_patterns=""
    
    # Platform-specific exclusions
    case $platform in
        "windows")
            exclude_patterns="--exclude=tests/ --exclude=*.pyc --exclude=__pycache__/ --exclude=.pytest_cache/"
            print_status "Creating optimized Windows build (excluding test files)"
            ;;
        "linux")
            exclude_patterns="--exclude=*.pyc --exclude=__pycache__/"
            print_status "Creating full Linux build"
            ;;
    esac
    
    # Create archive with exclusions
    if [[ "$platform" == "windows" ]]; then
        zip -r "FaceSwap-Windows-x64.zip" . $exclude_patterns
    else
        tar --exclude='tests' --exclude='*.pyc' --exclude='__pycache__' -czf "FaceSwap-Linux-x64.tar.gz" .
    fi
}

create_manual_release() {
    print_warning "Manual release creation"
    
    read -p "Path to Linux tarball: " LINUX_ARTIFACT
    read -p "Path to Windows zip: " WINDOWS_ARTIFACT
    
    if [[ ! -f "$LINUX_ARTIFACT" ]]; then
        print_error "Linux artifact not found: $LINUX_ARTIFACT"
        exit 1
    fi
    
    if [[ ! -f "$WINDOWS_ARTIFACT" ]]; then
        print_error "Windows artifact not found: $WINDOWS_ARTIFACT"
        exit 1
    fi
    
    print_status "Optimizing build sizes..."
    
    # Check if builds exist and their sizes
    if [[ -f "$WINDOWS_ARTIFACT" ]]; then
        WINDOWS_SIZE=$(du -h "$WINDOWS_ARTIFACT" | cut -f1)
        print_status "Windows build size: $WINDOWS_SIZE"
    fi
    
    if [[ -f "$LINUX_ARTIFACT" ]]; then
        LINUX_SIZE=$(du -h "$LINUX_ARTIFACT" | cut -f1)
        print_status "Linux build size: $LINUX_SIZE"
    fi
    
    # Simple release notes
    RELEASE_NOTES="## FaceSwap $VERSION

### Features
- Local face swapping with computer vision
- No cloud dependencies
- PySide6 GUI interface
- High-quality Poisson blending

### Installation

**Windows:** Download and extract \`FaceSwap-Windows-x64.zip\`, run \`FaceSwap.exe\`
**Linux:** Download and extract \`FaceSwap-Linux-x64.tar.gz\`, run \`./FaceSwap/FaceSwap\`

### System Requirements
- OS: Windows 10+, Ubuntu 18.04+
- RAM: 4GB minimum, 8GB recommended
- CPU: Multi-core recommended

Works completely offline after download."
    
    print_status "Creating GitHub release..."
    if gh release create "$VERSION" \
        --title "FaceSwap $VERSION" \
        --notes "$RELEASE_NOTES" \
        "$LINUX_ARTIFACT" \
        "$WINDOWS_ARTIFACT"; then
        print_success "Release created successfully!"
        echo "Release URL: $(gh repo view --json url -q .url)/releases/tag/$VERSION"
    else
        print_error "Failed to create release"
        exit 1
    fi
}

main() {
    echo "🚀 FaceSwap Release Creation Tool"
    echo "================================"
    
    check_prerequisites
    get_version_input
    
    echo
    echo "Creating manual release..."
    create_manual_release
    
    echo
    print_success "Release process completed!"
}

main "$@"