from moviepy.editor import CompositeVideoClip, ColorClip, AudioFileClip
import whisper
import os
from typing import Tuple, List, Optional
from .caption_generator import HighlightedCaptionStyle, get_word_timing
from src.utils.config import (
    AUDIO_DIR,
    SILENT_DIR,
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
    FONT_NAME,
    FONT_SIZE,
)


class VideoProcessor:
    def __init__(self):
        self.model = self.load_whisper_model()

    @staticmethod
    def get_output_paths(filename: str) -> Tuple[str, str]:
        """Generate paths for output videos with and without audio"""
        audio_path = os.path.join(AUDIO_DIR, f"{filename}_with_audio.mp4")
        silent_path = os.path.join(SILENT_DIR, f"{filename}_without_audio.mp4")
        return audio_path, silent_path

    @staticmethod
    def load_whisper_model(model_name: str = "base") -> Optional[whisper.Whisper]:
        try:
            return whisper.load_model(model_name)
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            return None

    def transcribe_audio_file(self, audio_path: str) -> List[Tuple[float, float, str]]:
        if self.model is None:
            return []
        try:
            result = self.model.transcribe(audio_path)
            return [
                (segment["start"], segment["end"], segment["text"].strip())
                for segment in result["segments"]
            ]
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return []

    def generate_video_with_captions(
        self, audio_path: str, base_filename: str
    ) -> Tuple[bool, str]:
        try:
            audio_output, silent_output = self.get_output_paths(base_filename)
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration

            captions = self.transcribe_audio_file(audio_path)
            if not captions:
                return False, "Failed to generate captions"

            background = ColorClip(
                size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(0, 0, 0), duration=duration
            )

            caption_style = HighlightedCaptionStyle(FONT_NAME, FONT_SIZE, VIDEO_WIDTH)
            text_clips = []
            for start, end, text in captions:
                words = get_word_timing(text, start, end)
                text_clips.extend(caption_style.create_word_clips(words))

            final_video = CompositeVideoClip([background] + text_clips)
            final_video.write_videofile(
                silent_output, fps=24, codec="libx264", audio=False
            )

            final_video = final_video.set_audio(audio_clip)
            final_video.write_videofile(
                audio_output, fps=24, codec="libx264", audio_codec="aac"
            )

            audio_clip.close()
            final_video.close()

            return True, f"Videos generated at:\n{audio_output}\n{silent_output}"

        except Exception as e:
            return False, f"Error generating video: {str(e)}"
