# FaceSwap - Local Face Swapping Tool

A powerful, local face swapping application that runs entirely on your machine. No cloud dependencies, no data upload required.

## 🚀 Quick Start

### One-Command Setup

```bash
# Complete setup (install dependencies + download models + test)
make setup

# Or using Python
python scripts/build.py setup
```

### For End Users (Recommended)

**Download the pre-built app - no Python knowledge needed:**

#### Windows
1. **Download**: [FaceSwap-Windows-x64.zip](https://github.com/your-username/faceswap/releases/latest)
2. **Extract** and run `FaceSwap.exe`

#### Linux
1. **Download**: [FaceSwap-Linux-x64.tar.gz](https://github.com/your-username/faceswap/releases/latest)
2. **Extract**: `tar -xzf FaceSwap-Linux-x64.tar.gz`
3. **Run**: `./FaceSwap/FaceSwap`

### For Developers

```bash
# Clone and setup
git clone https://github.com/your-username/faceswap.git
cd faceswap

# Option 1: Using Makefile (recommended)
make setup        # Complete setup
make test-quick   # Quick tests
make app         # Run application

# Option 2: Manual setup
pip install -r requirements.txt
python download_models.py
python run_tests.py --installation
python main.py
```

## 🛠️ Development Commands

```bash
# Setup and installation
make install      # Install dependencies only
make models       # Download AI models only
make dev-install  # Install with dev dependencies

# Testing
make test-quick   # Quick tests (no slow/integration tests)
make test-all     # All tests including slow ones
make test-install # Installation verification

# Code quality
make format       # Format code with Black
make lint         # Run linting
make clean        # Clean temporary files

# Run application
make app          # Start FaceSwap GUI
```

## ✨ Features

- **🔒 100% Local**: Everything runs on your machine
- **🎯 Auto Face Detection**: Finds and groups faces automatically
- **🖥️ Easy GUI**: Simple point-and-click interface
- **✨ High Quality**: Professional Poisson blending
- **📊 Real-time Progress**: See exactly what's happening

## 🎬 How to Use

1. **Select Video**: Choose your input video file
2. **Scan Faces**: App automatically detects all unique people
3. **Assign Images**: Click + to add replacement face images
4. **Process**: Click "Start Face Swap" and wait
5. **Done**: Find your video in `~/Videos/FaceSwap/`

## 🔧 System Requirements

- **OS**: Windows 10+, Ubuntu 18.04+, macOS 10.14+
- **RAM**: 4GB minimum, 8GB recommended
- **CPU**: Multi-core processor recommended
- **Storage**: 2GB free space

## 📁 Project Structure

```
FaceSwap/
├── main.py                # Application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Dependencies
├── Makefile              # Build automation
├── run_tests.py          # Test runner
├── download_models.py    # Model downloader
├── face_detector.py      # Face detection (auto-created)
├── face_swapper.py       # Face swapping (auto-created)
├── gui/                  # User interface
│   ├── main_window.py
│   ├── face_card.py
│   └── progress_dialog.py
├── utils/                # Utilities
│   ├── video_utils.py
│   └── smoothing.py
├── tests/                # Test suite
│   ├── conftest.py
│   ├── test_core.py
│   └── test_installation.py
├── scripts/              # Build scripts
│   ├── build.py
│   └── create_release.sh
└── models/               # AI models (auto-downloaded)
```

## 🛠️ Troubleshooting

### Common Issues

**Installation fails**: Run `python run_tests.py --installation` to diagnose

**Models won't download**: Try `python download_models.py` manually

**GUI won't start**: Check `python -c "import PySide6"` works

**Poor results**: Use high-quality source images with clear faces

### Getting Help

- Check [GitHub Issues](https://github.com/your-username/faceswap/issues)
- Run diagnostic: `make test-install`
- Include error logs from `logs/` folder when reporting bugs

## ⚖️ Legal & Ethics

**Use Responsibly:**
- ✅ Educational and creative projects
- ✅ Your own videos and images
- ❌ Creating misleading content
- ❌ Using without permission

**Privacy**: Your videos stay on your computer - nothing is uploaded anywhere.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with [OpenCV](https://opencv.org/), [Dlib](http://dlib.net/), and [PySide6](https://wiki.qt.io/Qt_for_Python).