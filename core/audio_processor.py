from moviepy.editor import AudioFileClip
from exceptions.custom_exceptions import AudioProcessingError

class AudioProcessor:
    def __init__(self):
        self.audio_clip = None

    def load_audio(self, audio_path: str) -> AudioFileClip:
        """Load audio file"""
        try:
            self.audio_clip = AudioFileClip(audio_path)
            return self.audio_clip
        except Exception as e:
            raise AudioProcessingError(f"Error loading audio: {str(e)}")

    def adjust_duration(self, target_duration: float) -> AudioFileClip:
        """Adjust audio duration to match video duration"""
        if self.audio_clip is None:
            raise AudioProcessingError("No audio loaded")
            
        try:
            if self.audio_clip.duration > target_duration:
                self.audio_clip = self.audio_clip.subclip(0, target_duration)
            return self.audio_clip
        except Exception as e:
            raise AudioProcessingError(f"Error adjusting audio duration: {str(e)}")

    def cleanup(self):
        """Clean up resources"""
        if self.audio_clip is not None:
            self.audio_clip.close()
            self.audio_clip = None