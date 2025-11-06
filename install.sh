#!/bin/bash

# FaceSwap Installation Script for Linux/macOS
# This script automates the installation of FaceSwap and its dependencies

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_info() {
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

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# Install system dependencies
install_system_deps() {
    local os=$(detect_os)
    
    print_info "Installing system dependencies for $os..."
    
    if [ "$os" = "linux" ]; then
        if command_exists apt-get; then
            # Ubuntu/Debian
            print_info "Detected Ubuntu/Debian system"
            sudo apt-get update
            sudo apt-get install -y \
                build-essential \
                cmake \
                libopenblas-dev \
                liblapack-dev \
                libx11-dev \
                libgtk-3-dev \
                python3-dev \
                libboost-all-dev \
                libavcodec-dev \
                libavformat-dev \
                libswscale-dev \
                libv4l-dev \
                libxvidcore-dev \
                libx264-dev \
                libjpeg-dev \
                libpng-dev \
                libtiff-dev \
                gfortran \
                pkg-config \
                python3-pip \
                python3-venv
        elif command_exists yum; then
            # RHEL/CentOS/Fedora
            print_info "Detected RHEL/CentOS/Fedora system"
            sudo yum install -y \
                gcc gcc-c++ \
                cmake \
                openblas-devel \
                lapack-devel \
                libX11-devel \
                gtk3-devel \
                python3-devel \
                boost-devel \
                ffmpeg-devel \
                libjpeg-devel \
                libpng-devel \
                libtiff-devel \
                gcc-gfortran \
                pkgconfig \
                python3-pip
        else
            print_warning "Unknown Linux distribution. Please install dependencies manually."
        fi
    elif [ "$os" = "macos" ]; then
        print_info "Detected macOS system"
        if ! command_exists brew; then
            print_error "Homebrew not found. Please install Homebrew first:"
            print_error "https://brew.sh/"
            exit 1
        fi
        
        brew install cmake boost boost-python3 pkg-config
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

# Check Python version
check_python() {
    print_info "Checking Python installation..."
    
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    local python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    local required_version="3.8"
    
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        print_error "Python 3.8 or higher is required. Found: $python_version"
        exit 1
    fi
    
    print_success "Python $python_version found"
}

# Create virtual environment
create_venv() {
    print_info "Creating Python virtual environment..."
    
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists. Removing old one..."
        rm -rf venv
    fi
    
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip wheel setuptools
    
    print_success "Virtual environment created and activated"
}

# Install Python dependencies
install_python_deps() {
    print_info "Installing Python dependencies..."
    
    # Make sure we're in the virtual environment
    if [ -z "$VIRTUAL_ENV" ]; then
        source venv/bin/activate
    fi
    
    # Install dependencies with fallback strategies
    print_info "Installing OpenCV..."
    pip install opencv-python>=4.8.0
    
    print_info "Installing PySide6..."
    pip install PySide6>=6.6.0
    
    print_info "Installing NumPy and Pillow..."
    pip install numpy>=1.24.0 Pillow>=10.0.0
    
    print_info "Installing dlib (this may take a while)..."
    # Try multiple approaches for dlib
    pip install cmake
    
    if ! pip install dlib>=19.24.0; then
        print_warning "Failed to install dlib via pip. Trying conda-forge..."
        if ! pip install --extra-index-url https://pypi.anaconda.org/conda-forge/simple dlib>=19.24.0; then
            print_warning "Failed to install dlib from conda-forge. Trying to build from source..."
            export CMAKE_ARGS="-DCMAKE_POLICY_VERSION_MINIMUM=3.5"
            if ! pip install dlib>=19.24.0 --no-cache-dir --verbose; then
                print_error "Failed to install dlib. Please check the error messages above."
                print_error "You may need to install additional system dependencies."
                exit 1
            fi
        fi
    fi
    
    print_success "All Python dependencies installed"
}

# Download models
download_models() {
    print_info "Downloading AI models..."
    
    # Make sure we're in the virtual environment
    if [ -z "$VIRTUAL_ENV" ]; then
        source venv/bin/activate
    fi
    
    if [ -f "download_models.py" ]; then
        python download_models.py
    else
        print_warning "download_models.py not found. You'll need to download models manually."
        print_info "Create a 'models' directory and download:"
        print_info "1. http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
        print_info "2. http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2"
        print_info "Extract them to the models/ directory"
    fi
}

# Create desktop launcher (Linux only)
create_launcher() {
    if [ "$(detect_os)" = "linux" ]; then
        print_info "Creating desktop launcher..."
        
        local desktop_file="$HOME/.local/share/applications/faceswap.desktop"
        local current_dir=$(pwd)
        
        mkdir -p "$HOME/.local/share/applications"
        
        cat > "$desktop_file" << EOF
[Desktop Entry]
Name=FaceSwap
Comment=Local Face Swapping Tool
Exec=$current_dir/run.sh
Icon=$current_dir/assets/icon.png
Terminal=false
Type=Application
Categories=AudioVideo;Video;
EOF
        
        # Create run script
        cat > "run.sh" << EOF
#!/bin/bash
cd "$current_dir"
source venv/bin/activate
python main.py
EOF
        
        chmod +x run.sh
        
        print_success "Desktop launcher created"
    fi
}

# Main installation function
main() {
    print_info "=== FaceSwap Installation Script ==="
    print_info "This script will install FaceSwap and all its dependencies"
    
    # Check if we're in the right directory
    if [ ! -f "main.py" ]; then
        print_error "main.py not found. Please run this script from the FaceSwap directory."
        exit 1
    fi
    
    # Ask for confirmation
    echo
    read -p "Do you want to continue with the installation? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Installation cancelled by user"
        exit 0
    fi
    
    print_info "Starting installation..."
    
    # Check Python
    check_python
    
    # Install system dependencies
    if [ "$(id -u)" != "0" ]; then
        print_info "Installing system dependencies (may require sudo password)..."
        install_system_deps
    else
        print_warning "Running as root. Skipping system dependency installation."
    fi
    
    # Create virtual environment
    create_venv
    
    # Install Python dependencies
    install_python_deps
    
    # Download models
    download_models
    
    # Create launcher
    create_launcher
    
    print_success "=== Installation Complete! ==="
    print_info ""
    print_info "To run FaceSwap:"
    print_info "1. Activate the virtual environment: source venv/bin/activate"
    print_info "2. Run the application: python main.py"
    print_info ""
    print_info "Or use the run script: ./run.sh"
    
    if [ "$(detect_os)" = "linux" ]; then
        print_info "You can also find FaceSwap in your application menu."
    fi
    
    print_info ""
    print_info "Enjoy using FaceSwap!"
}

# Handle interruption
trap 'print_error "Installation interrupted by user"; exit 1' INT TERM

# Run main function
main "$@"