#!/bin/bash

# FaceSwap Release Creation Script
# This script helps you create releases manually using GitHub CLI

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "Not in a git repository"
        exit 1
    fi
    
    # Check if GitHub CLI is installed
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI (gh) is not installed"
        echo "Install it from: https://cli.github.com/"
        exit 1
    fi
    
    # Check if GitHub CLI is authenticated
    if ! gh auth status &> /dev/null; then
        print_error "GitHub CLI is not authenticated"
        echo "Run: gh auth login"
        exit 1
    fi
    
    print_success "All prerequisites met"
}

# Function to get the next version
get_version_input() {
    echo
    print_status "Current repository: $(gh repo view --json nameWithOwner -q .nameWithOwner)"
    
    # Show existing releases
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

# Function to trigger workflow
trigger_workflow() {
    print_status "Triggering build workflow..."
    
    # Trigger the workflow
    if gh workflow run "build-release.yml" --field version="$VERSION"; then
        print_success "Workflow triggered successfully"
        
        # Wait a moment for the workflow to start
        sleep 3
        
        # Show the workflow run
        print_status "Monitoring workflow run..."
        gh run list --workflow="build-release.yml" --limit 1
        
        echo
        print_status "You can monitor the progress at:"
        echo "$(gh repo view --json url -q .url)/actions"
        
        # Ask if user wants to watch the run
        read -p "Watch the workflow run in real-time? (y/N): " watch_run
        if [[ "$watch_run" =~ ^[Yy]$ ]]; then
            # Get the latest run ID
            RUN_ID=$(gh run list --workflow="build-release.yml" --limit 1 --json databaseId -q '.[0].databaseId')
            if [ -n "$RUN_ID" ]; then
                gh run watch "$RUN_ID"
            fi
        fi
        
    else
        print_error "Failed to trigger workflow"
        exit 1
    fi
}

# Function to create manual release (fallback)
create_manual_release() {
    print_warning "Manual release creation (fallback method)"
    
    read -p "Do you have the build artifacts ready? (y/N): " has_artifacts
    if [[ ! "$has_artifacts" =~ ^[Yy]$ ]]; then
        print_error "Please build the artifacts first or use the automated workflow"
        exit 1
    fi
    
    read -p "Path to Linux tarball: " LINUX_ARTIFACT
    read -p "Path to Windows zip: " WINDOWS_ARTIFACT
    
    # Verify files exist
    if [[ ! -f "$LINUX_ARTIFACT" ]]; then
        print_error "Linux artifact not found: $LINUX_ARTIFACT"
        exit 1
    fi
    
    if [[ ! -f "$WINDOWS_ARTIFACT" ]]; then
        print_error "Windows artifact not found: $WINDOWS_ARTIFACT"
        exit 1
    fi
    
    # Create release notes
    RELEASE_NOTES="## FaceSwap $VERSION

### What's New
- Local face swapping with advanced computer vision
- No cloud dependencies - everything runs on your machine
- Intuitive GUI built with PySide6
- High-quality results using Poisson blending
- Support for multiple video formats

### Installation

#### Windows
1. Download \`FaceSwap-Windows-x64.zip\`
2. Extract the archive
3. Run \`FaceSwap.exe\`

#### Linux
1. Download \`FaceSwap-Linux-x64.tar.gz\`
2. Extract: \`tar -xzf FaceSwap-Linux-x64.tar.gz\`
3. Run: \`./FaceSwap/FaceSwap\`

### System Requirements
- **OS**: Windows 10+, Ubuntu 18.04+
- **RAM**: 4GB minimum, 8GB recommended
- **CPU**: Multi-core processor recommended
- **Storage**: 2GB free space

### Usage
1. Select a video file
2. Scan for faces (this may take a few minutes)
3. Assign swap images to detected faces
4. Process the video
5. Find your swapped video in ~/Videos/

### Notes
- First run may take longer as models are loaded
- Processing time depends on video length and resolution
- For best results, use high-quality source images with clear faces
- The tool works entirely offline - no internet required after download

### Troubleshooting
- If you encounter issues, check the log file in the application directory
- Ensure your system meets the minimum requirements
- Try reducing video resolution for faster processing"
    
    # Create the release
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

# Main script
main() {
    echo "🚀 FaceSwap Release Creation Tool"
    echo "================================"
    
    check_prerequisites
    get_version_input
    
    echo
    echo "Release options:"
    echo "1. Trigger automated workflow (recommended)"
    echo "2. Create manual release (requires pre-built artifacts)"
    echo "3. Exit"
    
    read -p "Choose option (1-3): " option
    
    case $option in
        1)
            trigger_workflow
            ;;
        2)
            create_manual_release
            ;;
        3)
            echo "Goodbye!"
            exit 0
            ;;
        *)
            print_error "Invalid option"
            exit 1
            ;;
    esac
    
    echo
    print_success "Release process completed!"
    echo
    print_status "Next steps:"
    echo "1. Verify the release was created successfully"
    echo "2. Test the downloadable artifacts"
    echo "3. Update documentation if needed"
}

# Run the script
main "$@"