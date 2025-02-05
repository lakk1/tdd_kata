from typing import List, Dict, Optional, Tuple
from moviepy.editor import concatenate_videoclips, CompositeVideoClip
from moviepy.config import change_settings
from config.settings import (
    IMAGEMAGICK_BINARY, VIDEO_WIDTH, VIDEO_HEIGHT,
    DEFAULT_FPS, DEFAULT_BITRATE
)
from core.image_processor import ImageProcessor
from core.audio_processor import AudioProcessor
from core.caption_generator import CaptionGenerator
from utils.validators import (
    validate_image_folder, validate_audio_file, validate_output_path
)
from utils.helpers import cleanup_gpu_memory
import whisper

# Configure ImageMagick
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_BINARY})

class VideoGenerator:
    def __init__(self):
        self.image_processor = ImageProcessor()
        self.audio_processor = AudioProcessor()
        self.caption_generator = CaptionGenerator()
        self.video = None
        self.video_width = VIDEO_WIDTH
        self.device =  "cpu"
        self.image_duration = 5
        self.transition_duration = 1
        self.whisper_model = whisper.load_model("base").to(self.device)
        
    def create_video(self,
                    image_folder: str,
                    audio_path: str,
                    output_path: str,
                    add_captions: bool = True,
                    progress_callback=None) -> Tuple[bool, str]:
        """Create video from images and audio"""
        try:
            # Validate inputs
            image_paths = validate_image_folder(image_folder)
            validate_audio_file(audio_path)
            validate_output_path(output_path)
            
            # Process images
            image_clips = self.image_processor.process_images_parallel(
                image_paths,
                progress_callback=progress_callback
            )
            
            # Create video
            self.video = concatenate_videoclips(image_clips, method="compose")
            
            # Process audio
            audio = self.audio_processor.load_audio(audio_path)
            
            # Adjust durations
            if audio.duration > self.video.duration:
                audio = self.audio_processor.adjust_duration(self.video.duration)
            elif self.video.duration > audio.duration:
                self.video = self.video.subclip(0, audio.duration)
            
            # Add captions if requested
            if add_captions:
                captions = self.caption_generator.generate_captions(audio_path)
                caption_clips = self.caption_generator.create_caption_clips(captions)
                self.video = CompositeVideoClip([self.video] + caption_clips)
            
            # Combine video and audio
            final_video = self.video.set_audio(audio)
            
            # Write video file
            final_video.write_videofile(
                output_path,
                fps=DEFAULT_FPS,
                codec='libx264',  # Use CPU codec
                audio_codec='aac',
                bitrate=DEFAULT_BITRATE,
                threads=self.image_processor.max_workers,
                preset='medium'  # Use CPU preset
            )
            
            return True, "Video created successfully!"
            
        except Exception as e:
            return False, f"Error creating video: {str(e)}"
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        if self.video is not None:
            self.video.close()
        self.audio_processor.cleanup()
        self.caption_generator.cleanup()
        cleanup_gpu_memory()