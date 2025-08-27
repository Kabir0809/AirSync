import cv2
import torch
import numpy as np
import time

def benchmark_comparison():
    """Compare CPU vs GPU processing time for a common image operation"""
    # Load image
    image = cv2.imread("C:/Users/harsh/OneDrive/Pictures/2c89at5d5pyd1.jpeg")
    if image is None:
        # Create a test image if no file is available
        image = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
    
    # OpenCV CPU operation
    start_time = time.time()
    cpu_result = cv2.GaussianBlur(image, (15, 15), 0)
    cpu_time = time.time() - start_time
    print(f"OpenCV CPU time: {cpu_time:.4f}s")
    
    # PyTorch GPU operation (if available)
    if torch.cuda.is_available():
        # Convert OpenCV image to PyTorch tensor
        image_tensor = torch.from_numpy(image).permute(2, 0, 1).float().unsqueeze(0).cuda()
        
        # Create Gaussian kernel for PyTorch
        kernel_size = 15
        sigma = 2.5
        channels = 3
        
        # Create 2D Gaussian kernel
        x = torch.arange(kernel_size) - (kernel_size - 1) / 2
        x = x.view(1, -1).expand(kernel_size, -1)
        y = x.transpose(0, 1)
        gaussian_kernel = torch.exp(-(x.pow(2) + y.pow(2)) / (2 * sigma ** 2))
        gaussian_kernel = gaussian_kernel / gaussian_kernel.sum()
        
        # Expand kernel for 3 channels
        gaussian_kernel = gaussian_kernel.view(1, 1, kernel_size, kernel_size)
        gaussian_kernel = gaussian_kernel.expand(channels, 1, kernel_size, kernel_size).cuda()
        
        # Apply convolution
        start_time = time.time()
        padding = kernel_size // 2
        gpu_result = torch.nn.functional.conv2d(
            image_tensor, 
            gaussian_kernel, 
            padding=padding, 
            groups=channels
        )
        torch.cuda.synchronize()  # Make sure GPU operation is complete
        gpu_time = time.time() - start_time
        print(f"PyTorch GPU time: {gpu_time:.4f}s")
        
        # Convert back to OpenCV format
        gpu_result = gpu_result.squeeze(0).permute(1, 2, 0).cpu().numpy().astype(np.uint8)
        
        # Show speed improvement
        print(f"Speed improvement: {cpu_time / gpu_time:.2f}x faster on GPU")
        
        # Show results
        cv2.imshow("CPU Result", cpu_result)
        cv2.imshow("GPU Result", gpu_result)
        cv2.waitKey(0)
    else:
        print("PyTorch CUDA not available")

if __name__ == "__main__":
    benchmark_comparison()
