#!/usr/bin/env python3
"""
Setup script for FaceSwap application.
"""

from setuptools import setup, find_packages
from pathlib import Path
import sys

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
version = "1.0.0"

setup(
    name="faceswap-local",
    version=version,
    author="FaceSwap Team",
    author_email="contact@faceswap.local",
    description="Local face swapping tool with advanced computer vision",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/FaceSwap",
    project_urls={
        "Bug Reports": "https://github.com/your-username/FaceSwap/issues",
        "Source": "https://github.com/your-username/FaceSwap",
        "Documentation": "https://github.com/your-username/FaceSwap/blob/main/README.md",
    },
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
        "Environment :: X11 Applications :: Qt",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
        "build": [
            "pyinstaller>=5.0",
            "wheel>=0.37",
            "setuptools>=60.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "faceswap=main:main",
        ],
        "gui_scripts": [
            "faceswap-gui=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
        "gui": ["*.ui", "*.qrc"],
        "assets": ["*.png", "*.jpg", "*.ico"],
    },
    data_files=[
        ("share/applications", ["assets/faceswap.desktop"]) if sys.platform.startswith("linux") else None,
        ("share/pixmaps", ["assets/faceswap.png"]) if sys.platform.startswith("linux") else None,
    ],
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