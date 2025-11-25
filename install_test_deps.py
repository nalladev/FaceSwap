import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def install_minimal_deps():
    """Install minimal dependencies for testing."""
    
    # Essential packages only
    minimal_packages = [
        "torch",
        "torchvision", 
        "opencv-python",
        "numpy",
        "psutil"
    ]
    
    for package in minimal_packages:
        try:
            logger.info(f"Installing {package}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                package, "--quiet", "--no-cache-dir"
            ])
            logger.info(f"✅ {package} installed")
        except subprocess.CalledProcessError:
            logger.warning(f"❌ Failed to install {package}")

if __name__ == "__main__":
    logger.info("Installing minimal dependencies for testing...")
    install_minimal_deps()
    logger.info("Installation complete!")
