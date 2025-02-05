import cv2
import numpy as np
from moviepy.editor import ImageClip
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from config.settings import VIDEO_WIDTH, VIDEO_HEIGHT, IMAGE_DURATION, MAX_WORKERS
from exceptions.custom_exceptions import ImageProcessingError
from utils.helpers import get_device_info, calculate_dimensions

class ImageProcessor:
    def __init__(self):
        self.has_cuda, self.has_gpu = get_device_info()
        self.max_workers = MAX_WORKERS

    def process_image(self, img_path: str, duration: float = IMAGE_DURATION) -> ImageClip:
        """Process a single image"""
        try:
            if self.has_gpu:
                return self._process_image_gpu(img_path, duration)
            return self._process_image_cpu(img_path, duration)
        except Exception as e:
            raise ImageProcessingError(f"Error processing image {img_path}: {str(e)}")

    def _process_image_gpu(self, img_path: str, duration: float) -> ImageClip:
        """Process image using GPU acceleration"""
        img = cv2.imread(img_path)
        if img is None:
            raise ImageProcessingError(f"Could not read image: {img_path}")
        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Upload to GPU
        gpu_img = cv2.cuda_GpuMat()
        gpu_img.upload(img)
        
        # Calculate new dimensions
        new_width, new_height = calculate_dimensions(
            img.shape[1], img.shape[0],
            VIDEO_WIDTH, VIDEO_HEIGHT
        )
        
        # Resize on GPU
        gpu_img = cv2.cuda.resize(gpu_img, (new_width, new_height))
        
        # Download result
        img = gpu_img.download()
        
        # Create and crop clip
        clip = ImageClip(img)
        clip = self._crop_clip(clip, duration)
        
        return clip

    def _process_image_cpu(self, img_path: str, duration: float) -> ImageClip:
        """Process image using CPU"""
        clip = ImageClip(img_path)
        
        # Calculate new dimensions
        new_width, new_height = calculate_dimensions(
            clip.size[0], clip.size[1],
            VIDEO_WIDTH, VIDEO_HEIGHT
        )
        
        # Resize clip
        clip = clip.resize((new_width, new_height))
        clip = self._crop_clip(clip, duration)
        
        return clip

    def _crop_clip(self, clip: ImageClip, duration: float) -> ImageClip:
        """Crop clip to target dimensions and set duration"""
        return (clip.crop(
            x_center=clip.size[0]/2,
            y_center=clip.size[1]/2,
            width=VIDEO_WIDTH,
            height=VIDEO_HEIGHT)
        .set_duration(duration))

    def process_images_parallel(self, image_paths: List[str], 
                              transitions: Optional[List[str]] = None,
                              progress_callback=None) -> List[ImageClip]:
        """Process multiple images in parallel"""
        clips = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_img = {
                executor.submit(self.process_image, img_path): img_path 
                for img_path in image_paths
            }
            
            completed = 0
            for future in as_completed(future_to_img):
                completed += 1
                if progress_callback:
                    progress_callback(completed, len(image_paths))
                
                clip = future.result()
                if clip is not None:
                    clips.append(clip)
        
        return clips