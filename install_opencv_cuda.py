"""
Instructions to install OpenCV with CUDA support.
Run the commands in your terminal/command prompt.
"""

# Method 1: Using pip (easiest but limited versions)
print("""
# Method 1: Install pre-built OpenCV with CUDA support
pip uninstall opencv-python opencv-python-headless opencv-contrib-python -y
pip install opencv-contrib-python-cuda
""")

# Method 2: Building from source
print("""
# Method 2: Build OpenCV from source with CUDA support
# This is more complex but gives you control over the build

# Prerequisites:
# 1. Install Visual Studio with C++ development tools (on Windows)
# 2. Install CUDA Toolkit matching your GPU driver version
# 3. Install CMake

# Clone repositories
git clone https://github.com/opencv/opencv.git
git clone https://github.com/opencv/opencv_contrib.git

# Configure with CMake
cd opencv
mkdir build
cd build
cmake -DWITH_CUDA=ON ^
      -DOPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules ^
      -DCUDA_ARCH_BIN=8.6 ^  # Set this to your GPU architecture
      -DBUILD_opencv_world=ON ^
      -DWITH_CUDNN=ON ^
      -DOPENCV_DNN_CUDA=ON ^
      -DCMAKE_BUILD_TYPE=Release ^
      ..

# Build
cmake --build . --config Release -j8

# Install
cmake --install .
""")

# Testing the installation
print("""
# Test your installation with:
import cv2
print(cv2.getBuildInformation())
# Look for "CUDA: YES" in the output
""")
