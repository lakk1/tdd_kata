import cv2
import torch
from typing import Tuple
import gc

def get_device_info() -> Tuple[bool, bool]:
    """
    Get information about available hardware acceleration
    Returns: (has_cuda, has_gpu)
    """
    has_cuda = torch.cuda.is_available()
    has_gpu = cv2.cuda.getCudaEnabledDeviceCount() > 0
    return has_cuda, has_gpu

def calculate_dimensions(current_width: int, current_height: int, 
                       target_width: int, target_height: int) -> Tuple[int, int]:
    """
    Calculate new dimensions maintaining aspect ratio
    """
    current_ratio = current_width / current_height
    target_ratio = target_width / target_height
    
    if current_ratio > target_ratio:
        new_height = target_height
        new_width = int(new_height * current_ratio)
    else:
        new_width = target_width
        new_height = int(new_width / current_ratio)
    
    return new_width, new_height

def cleanup_gpu_memory():
    """
    Clean up GPU memory safely
    """
    try:
        # Clear PyTorch CUDA cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        # Clear OpenCV CUDA cache
        if cv2.cuda.getCudaEnabledDeviceCount() > 0:
            cv2.cuda.Stream.Null.waitForCompletion()
            
        # Force garbage collection
        gc.collect()
        
    except Exception as e:
        print(f"Warning: GPU cleanup error - {str(e)}")