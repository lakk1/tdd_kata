import whisper
from moviepy.editor import TextClip
from typing import List, Dict
from config.settings import (
    CAPTION_FONT, CAPTION_FONTSIZE, CAPTION_COLOR,
    CAPTION_STROKE_COLOR, CAPTION_STROKE_WIDTH,
    VIDEO_WIDTH, VIDEO_HEIGHT
)
from exceptions.custom_exceptions import CaptionGenerationError

class CaptionGenerator:
    def __init__(self):
        self.device = "cpu"
        self.model = whisper.load_model("base").to(self.device)

    def generate_captions(self, audio_path: str) -> List[Dict]:
        """Generate captions using Whisper"""
        try:
            result = self.model.transcribe(audio_path)
            return result["segments"]
        except Exception as e:
            raise CaptionGenerationError(f"Error generating captions: {str(e)}")

    def create_caption_clips(self, captions: List[Dict]) -> List[TextClip]:
        """Create caption clips from whisper segments"""
        caption_clips = []
        
        try:
            for segment in captions:
                txt_clip = (TextClip(
                    segment['text'],
                    font=CAPTION_FONT,
                    fontsize=CAPTION_FONTSIZE,
                    color=CAPTION_COLOR,
                    stroke_color=CAPTION_STROKE_COLOR,
                    stroke_width=CAPTION_STROKE_WIDTH,
                    size=(VIDEO_WIDTH-100, None),
                    method='caption'
                )
                .set_position(('center', VIDEO_HEIGHT-200))
                .set_start(segment['start'])
                .set_end(segment['end']))
                
                caption_clips.append(txt_clip)
            
            return caption_clips
        except Exception as e:
            raise CaptionGenerationError(f"Error creating caption clips: {str(e)}")

    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'model'):
            del self.model