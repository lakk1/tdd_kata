import os
import numpy as np
from typing import List, Dict, Optional
from moviepy.config import change_settings
import torch
import cv2
from concurrent.futures import ThreadPoolExecutor, as_completed
from moviepy.editor import *
import whisper

# Set the path to the ImageMagick binary
MAGICK_HOME = 'C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe'
IMAGEMAGICK_BINARY = os.getenv('IMAGEMAGICK_BINARY', MAGICK_HOME)
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_BINARY})

class VideoGenerator:
    TRANSITION_TYPES = {
        'crossfade': lambda clip, duration: clip.crossfadein(duration),
        'fade': lambda clip, duration: clip.fadein(duration),
        'slide_left': lambda clip, duration: clip.set_position(
            lambda t: ('center' if t > duration else 1080 + (t * -1080/duration), 'center')
        ),
        'slide_right': lambda clip, duration: clip.set_position(
            lambda t: ('center' if t > duration else -1080 + (t * 1080/duration), 'center')
        ),
        'zoom_in': lambda clip, duration: clip.resize(
            lambda t: 1 + 0.1 * t if t < duration else 1.1
        )
    }

    def __init__(self):
        self.image_duration = 5
        self.transition_duration = 1
        
        # Initialize CUDA if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        if torch.cuda.is_available():
            torch.backends.cudnn.benchmark = True
            
        # Load Whisper model on GPU
        self.whisper_model = whisper.load_model("base").to(self.device)
        
        self.video_width = 1080
        self.video_height = 1920
        self.video = None
        self.audio = None
        
        self.max_workers = os.cpu_count()
        self.use_cuda = cv2.cuda.getCudaEnabledDeviceCount() > 0

    def preprocess_image(self, img_path: str):
        try:
            if self.use_cuda:
                # GPU-accelerated image processing
                img = cv2.imread(img_path)
                if img is None:
                    raise ValueError(f"Failed to load image: {img_path}")
                
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                gpu_img = cv2.cuda_GpuMat()
                gpu_img.upload(img)

                # Calculate dimensions
                img_ar = img.shape[1] / img.shape[0]
                target_ar = self.video_width / self.video_height
                
                if img_ar > target_ar:
                    new_height = self.video_height
                    new_width = int(new_height * img_ar)
                else:
                    new_width = self.video_width
                    new_height = int(new_width / img_ar)

                # GPU resize
                gpu_img = cv2.cuda.resize(gpu_img, (new_width, new_height))
                img = gpu_img.download()
                
                clip = ImageClip(img)
            else:
                # CPU processing
                clip = ImageClip(img_path)
                img_ar = clip.size[0] / clip.size[1]
                target_ar = self.video_width / self.video_height
                
                if img_ar > target_ar:
                    new_height = self.video_height
                    new_width = int(new_height * img_ar)
                else:
                    new_width = self.video_width
                    new_height = int(new_width / img_ar)
                
                clip = clip.resize((new_width, new_height))

            # Final crop and duration setting
            clip = (clip
                   .crop(x_center=clip.size[0]/2,
                        y_center=clip.size[1]/2,
                        width=self.video_width,
                        height=self.video_height)
                   .set_duration(self.image_duration))
            
            return clip

        except Exception as e:
            print(f"Error processing image {img_path}: {str(e)}")
            return None

    def process_images_parallel(self, image_files: List[str], image_folder: str, 
                            transitions: Optional[List[str]], progress_callback=None) -> List[ImageClip]:
        """Process images in parallel"""
        clips = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_img = {
                executor.submit(self.preprocess_image, os.path.join(image_folder, img_file)): img_file 
                for img_file in image_files
            }
            
            completed = 0
            for future in as_completed(future_to_img):
                completed += 1
                if progress_callback:
                    progress_callback(completed, len(image_files))
                
                clip = future.result()
                if clip is not None:
                    clips.append(clip)
        
        # Apply transitions after parallel processing
        if transitions:
            for idx, clip in enumerate(clips):
                if idx < len(transitions):
                    clips[idx] = self.apply_transition(clip, transitions[idx])
        
        return clips

    def validate_inputs(self, image_folder: str, audio_path: str):
        """Validate input paths and files"""
        if not os.path.exists(image_folder):
            raise ValueError(f"Image folder does not exist: {image_folder}")
        if not os.path.exists(audio_path):
            raise ValueError(f"Audio file does not exist: {audio_path}")
        
        # Check if folder contains valid images
        valid_images = [f for f in os.listdir(image_folder) 
                    if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not valid_images:
            raise ValueError("No valid images found in folder")
    def cleanup(self):
        """Clean up resources"""
        try:
            # Close any open clips
            if hasattr(self, 'video') and self.video:
                self.video.close()
            if hasattr(self, 'audio') and self.audio:
                self.audio.close()
                
            # Force garbage collection
            import gc
            gc.collect()
            
        except Exception as e:
            print(f"Cleanup error: {str(e)}")   

    def create_video(self, image_folder: str, audio_path: str, output_path: str,
                    transitions: Optional[List[str]] = None,
                    add_captions: bool = True,
                    progress_callback=None) -> tuple:
        try:
            self.validate_inputs(image_folder, audio_path)
            
            # Process images
            image_files = sorted([f for f in os.listdir(image_folder) 
                                if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
            
            image_clips = self.process_images_parallel(
                image_files, image_folder, transitions, progress_callback
            )
            
            self.video = concatenate_videoclips(image_clips, method="compose")
            self.audio = AudioFileClip(audio_path)
            
            # Duration adjustment
            if self.audio.duration > self.video.duration:
                self.audio = self.audio.subclip(0, self.video.duration)
            elif self.video.duration > self.audio.duration:
                self.video = self.video.subclip(0, self.audio.duration)
            
            # Caption generation with GPU acceleration
            if add_captions:
                with torch.cuda.amp.autocast():
                    captions = self.generate_captions(audio_path)
                caption_clips = self.create_caption_clips(
                    captions, (self.video_width, self.video_height)
                )
                self.video = CompositeVideoClip([self.video] + caption_clips)
            
            final_video = self.video.set_audio(self.audio)
            
            # Optimized video writing settings
            write_videofile_kwargs = {
                'fps': 30,
                'codec': 'h264_nvenc' if torch.cuda.is_available() else 'libx264',
                'audio_codec': 'aac',
                'threads': self.max_workers,
                'preset': 'p7' if torch.cuda.is_available() else 'medium',
                'bitrate': '8000k',
                'ffmpeg_params': [
                    '-vsync', '0',
                    '-hwaccel', 'cuda',
                    '-hwaccel_output_format', 'cuda'
                ] if torch.cuda.is_available() else None
            }
            
            # Remove None values from ffmpeg_params
            if write_videofile_kwargs['ffmpeg_params'] is None:
                del write_videofile_kwargs['ffmpeg_params']
            
            final_video.write_videofile(output_path, **write_videofile_kwargs)
            
            return True, "Video created successfully!"
            
        except Exception as e:
            return False, f"Error creating video: {str(e)}"
        finally:
            self.cleanup()

    # [Previous methods remain unchanged: validate_inputs, generate_captions, 
    # create_caption_clips, apply_transition, cleanup, process_images_parallel]