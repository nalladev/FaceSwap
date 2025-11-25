#!/bin/bash

echo "🔍 Quick GPU Acceleration Test"
echo "==============================="

# Check system resources
echo "System Resources:"
free -h | head -2
echo "CPU cores: $(nproc)"
echo ""

# Check if required packages are available
echo "📦 Checking dependencies..."
python3 -c "import torch; print(f'✅ PyTorch {torch.__version__}')" 2>/dev/null || echo "❌ PyTorch not available"
python3 -c "import cv2; print(f'✅ OpenCV {cv2.__version__}')" 2>/dev/null || echo "❌ OpenCV not available"
python3 -c "import numpy; print(f'✅ NumPy {numpy.__version__}')" 2>/dev/null || echo "❌ NumPy not available"
echo ""

# Run lightweight tests
echo "🧪 Running lightweight tests..."
python3 test_gpu_acceleration.py

echo ""
echo "Test complete! Check output above for results."
