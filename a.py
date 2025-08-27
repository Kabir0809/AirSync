import cv2
import torch

# Check PyTorch GPU detection
print("===== PyTorch GPU Detection =====")
if torch.cuda.is_available():
    print(f"PyTorch: CUDA is available")
    print(f"Number of GPU: {torch.cuda.device_count()}")
    print(f"GPU Name: {torch.cuda.get_device_name()}")
else:
    print("PyTorch: CUDA is not available")

# Check OpenCV GPU detection
print("\n===== OpenCV GPU Detection =====")
CUDA_AVAILABLE = cv2.cuda.getCudaEnabledDeviceCount() > 0

if CUDA_AVAILABLE:
    print(f"OpenCV: CUDA is available with {cv2.cuda.getCudaEnabledDeviceCount()} device(s)")
    # Initialize CUDA device
    cv2.cuda.setDevice(0)
else:
    print("OpenCV: CUDA is not available, falling back to CPU processing")

# Print OpenCV build information (relevant parts)
print("\n===== OpenCV Build Information =====")
build_info = cv2.getBuildInformation()
cuda_info = [line for line in build_info.split('\n') if "CUDA" in line]
for line in cuda_info:
    print(line.strip())

print("\nOpenCV version:", cv2.__version__)