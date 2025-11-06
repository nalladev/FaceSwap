@echo off
REM FaceSwap Installation Script for Windows
REM This script automates the installation of FaceSwap and its dependencies

setlocal enabledelayedexpansion

REM Colors for output (using echo with special characters)
set "INFO=[INFO]"
set "SUCCESS=[SUCCESS]"
set "WARNING=[WARNING]"
set "ERROR=[ERROR]"

echo =================================================================
echo              FaceSwap Installation Script for Windows
echo =================================================================
echo This script will install FaceSwap and all its dependencies
echo.

REM Check if we're in the right directory
if not exist "main.py" (
    echo %ERROR% main.py not found. Please run this script from the FaceSwap directory.
    pause
    exit /b 1
)

REM Ask for confirmation
set /p "confirm=Do you want to continue with the installation? (y/N): "
if /i not "%confirm%"=="y" if /i not "%confirm%"=="yes" (
    echo %INFO% Installation cancelled by user
    pause
    exit /b 0
)

echo %INFO% Starting installation...
echo.

REM Check Python installation
echo %INFO% Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %ERROR% Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo %SUCCESS% Python %PYTHON_VERSION% found

REM Check if Python version is 3.8+
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo %ERROR% Python 3.8 or higher is required. Found: %PYTHON_VERSION%
    echo Please install a newer version from https://python.org
    pause
    exit /b 1
)

REM Check if pip is available
echo %INFO% Checking pip installation...
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %ERROR% pip is not available. Please reinstall Python with pip.
    pause
    exit /b 1
)

echo %SUCCESS% pip is available

REM Create virtual environment
echo %INFO% Creating Python virtual environment...
if exist "venv" (
    echo %WARNING% Virtual environment already exists. Removing old one...
    rmdir /s /q venv
)

python -m venv venv
if %errorlevel% neq 0 (
    echo %ERROR% Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo %INFO% Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo %ERROR% Failed to activate virtual environment
    pause
    exit /b 1
)

echo %SUCCESS% Virtual environment created and activated

REM Upgrade pip
echo %INFO% Upgrading pip...
python -m pip install --upgrade pip wheel setuptools
if %errorlevel% neq 0 (
    echo %WARNING% Failed to upgrade pip, continuing anyway...
)

REM Install Python dependencies
echo %INFO% Installing Python dependencies...
echo This may take several minutes, please be patient...
echo.

REM Install OpenCV
echo %INFO% Installing OpenCV...
python -m pip install opencv-python>=4.8.0
if %errorlevel% neq 0 (
    echo %ERROR% Failed to install OpenCV
    pause
    exit /b 1
)

REM Install PySide6
echo %INFO% Installing PySide6...
python -m pip install PySide6>=6.6.0
if %errorlevel% neq 0 (
    echo %ERROR% Failed to install PySide6
    pause
    exit /b 1
)

REM Install NumPy and Pillow
echo %INFO% Installing NumPy and Pillow...
python -m pip install numpy>=1.24.0 Pillow>=10.0.0
if %errorlevel% neq 0 (
    echo %ERROR% Failed to install NumPy and Pillow
    pause
    exit /b 1
)

REM Install dlib (most challenging part on Windows)
echo %INFO% Installing dlib (this may take a while)...
echo %WARNING% If this fails, you may need to install Visual Studio Build Tools

REM Try to install cmake first
python -m pip install cmake
if %errorlevel% neq 0 (
    echo %WARNING% Failed to install cmake, continuing anyway...
)

REM Try multiple approaches for dlib
echo %INFO% Attempting to install dlib...
python -m pip install dlib>=19.24.0
if %errorlevel% neq 0 (
    echo %WARNING% Failed to install dlib via pip. Trying precompiled wheel...
    
    REM Try with conda-forge
    python -m pip install --extra-index-url https://pypi.anaconda.org/conda-forge/simple dlib>=19.24.0
    if !errorlevel! neq 0 (
        echo %WARNING% Failed to install dlib from conda-forge.
        echo %ERROR% Dlib installation failed. This usually means:
        echo   1. You need Visual Studio Build Tools installed
        echo   2. Or you need to install a precompiled wheel
        echo.
        echo Please visit: https://visualstudio.microsoft.com/visual-cpp-build-tools/
        echo Or try installing a precompiled dlib wheel from:
        echo https://github.com/ageitgey/dlib-models
        pause
        exit /b 1
    )
)

echo %SUCCESS% All Python dependencies installed

REM Download models
echo %INFO% Downloading AI models...
if exist "download_models.py" (
    python download_models.py
    if %errorlevel% neq 0 (
        echo %WARNING% Model download failed. You may need to download them manually.
        echo See README.md for instructions.
    )
) else (
    echo %WARNING% download_models.py not found. You'll need to download models manually.
    echo Create a 'models' directory and download:
    echo 1. http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
    echo 2. http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2
    echo Extract them to the models\ directory
)

REM Create run script
echo %INFO% Creating run script...
echo @echo off > run.bat
echo call venv\Scripts\activate.bat >> run.bat
echo python main.py >> run.bat
echo pause >> run.bat

REM Create desktop shortcut (optional)
echo %INFO% Creating desktop shortcut...
set "desktop=%USERPROFILE%\Desktop"
set "shortcut=%desktop%\FaceSwap.lnk"
set "target=%cd%\run.bat"
set "icon=%cd%\assets\icon.ico"

REM Create VBS script to make shortcut
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%shortcut%" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%target%" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%cd%" >> CreateShortcut.vbs
echo oLink.Description = "FaceSwap - Local Face Swapping Tool" >> CreateShortcut.vbs
if exist "assets\icon.ico" (
    echo oLink.IconLocation = "%icon%" >> CreateShortcut.vbs
)
echo oLink.Save >> CreateShortcut.vbs

REM Execute VBS script
cscript CreateShortcut.vbs >nul 2>&1
if %errorlevel% equ 0 (
    echo %SUCCESS% Desktop shortcut created
) else (
    echo %WARNING% Could not create desktop shortcut
)

REM Clean up VBS script
del CreateShortcut.vbs >nul 2>&1

echo.
echo %SUCCESS% =================================================================
echo %SUCCESS%              Installation Complete!
echo %SUCCESS% =================================================================
echo.
echo To run FaceSwap:
echo 1. Double-click the desktop shortcut "FaceSwap"
echo 2. Or run: run.bat
echo 3. Or manually:
echo    - Open Command Prompt in this folder
echo    - Run: venv\Scripts\activate.bat
echo    - Run: python main.py
echo.
echo %INFO% Enjoy using FaceSwap!
echo.

REM Keep window open
pause