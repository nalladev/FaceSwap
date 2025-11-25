#!/usr/bin/env python3
"""Setup script for FaceSwap application."""

from setuptools import setup, find_packages
from pathlib import Path
import sys
import platform

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
requirements_file = this_directory / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Version
version = "1.0.1"

# Platform-specific requirements
platform_requirements = []
if platform.system() == "Windows":
    platform_requirements.extend([
        "opencv-python>=4.5.0",
        # Windows-specific optimized builds
    ])
elif platform.system() == "Linux":
    platform_requirements.extend([
        "opencv-python>=4.5.0",
        "scikit-image>=0.18.0",  # Optional advanced warping
        "psutil>=5.8.0",  # Memory monitoring
    ])
elif platform.system() == "Darwin":  # macOS
    platform_requirements.extend([
        "opencv-python>=4.5.0",
        "scikit-image>=0.18.0",
    ])

# Combine base and platform requirements
all_requirements = requirements + platform_requirements

setup(
    name="faceswap-local",
    version=version,
    author="FaceSwap Team",
    author_email="contact@faceswap.local",
    description="Local face swapping tool with advanced computer vision",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/FaceSwap",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Image Processing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=all_requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=22.0",
            "flake8>=4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "faceswap=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt"],
        "gui": ["*.ui"],
        "assets": ["*.png", "*.jpg", "*.ico"],
    },
    zip_safe=False,
    keywords=[
        "face-swap",
        "computer-vision",
        "video-processing",
        "opencv",
        "dlib",
        "gui",
        "local",
        "privacy"
    ],
    platforms=["Windows", "macOS", "Linux"],
)
