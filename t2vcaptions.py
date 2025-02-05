from moviepy.editor import (
    CompositeVideoClip,
    ColorClip,
    AudioFileClip,
    VideoFileClip,
)
import whisper
import os
from typing import Tuple, List, Optional
from caption_styles import HighlightedCaptionStyle, get_word_timing

# Constants
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FONT_SIZE = 64
FONT_NAME = "Arial"

# Directory structure
WORKING_DIR = os.getcwd()
INPUT_DIR = os.path.join(WORKING_DIR, "input")
OUTPUT_DIR = os.path.join(WORKING_DIR, "output")
AUDIO_DIR = os.path.join(OUTPUT_DIR, "with_audio")
SILENT_DIR = os.path.join(OUTPUT_DIR, "without_audio")

# File paths
INPUT_AUDIO_PATH = os.path.join(INPUT_DIR, "input_audio.mp3")

# Create required directories
for directory in [INPUT_DIR, OUTPUT_DIR, AUDIO_DIR, SILENT_DIR]:
    os.makedirs(directory, exist_ok=True)


# Generate output paths
def get_output_paths(filename: str) -> Tuple[str, str]:
    """Generate paths for output videos with and without audio"""
    audio_path = os.path.join(AUDIO_DIR, f"{filename}_with_audio.mp4")
    silent_path = os.path.join(SILENT_DIR, f"{filename}_without_audio.mp4")
    return audio_path, silent_path


def load_whisper_model(model_name: str = "base") -> Optional[whisper.Whisper]:
    """Load Whisper model.

    Args:
        model_name: Name of Whisper model to load
    Returns:
        Loaded Whisper model or None if error
    """
    try:
        return whisper.load_model(model_name)
    except Exception as e:
        print(f"Error loading Whisper model: {e}")
        return None


def transcribe_audio_file(
    model: whisper.Whisper, audio_path: str
) -> List[Tuple[float, float, str]]:
    """Transcribe audio file using Whisper model.

    Args:
        model: Loaded Whisper model
        audio_path: Path to audio file
    Returns:
        List of tuples containing (start_time, end_time, text)
    """
    try:
        result = model.transcribe(audio_path)
        return [
            (segment["start"], segment["end"], segment["text"].strip())
            for segment in result["segments"]
        ]
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return []


def transcribe_audio(audio_path: str) -> List[Tuple[float, float, str]]:
    """Transcribe audio file to text segments.

    Args:
        audio_path: Path to audio file
    Returns:
        List of tuples containing (start_time, end_time, text)
    """
    model = load_whisper_model()
    if model is None:
        return []
    return transcribe_audio_file(model, audio_path)


def generate_video_with_captions(
    audio_path: str, base_filename: str
) -> Tuple[bool, str]:
    """Generate video with captions from audio file."""
    try:
        # Generate output paths
        audio_output, silent_output = get_output_paths(base_filename)

        # Load audio and get duration
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration

        # Get captions
        captions = transcribe_audio(audio_path)
        if not captions:
            return False, "Failed to generate captions"

        # Create background
        background = ColorClip(
            size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(0, 0, 0), duration=duration
        )

        # Create caption clips
        text_clips = []
        # for start, end, text in captions:
        #     clip = (
        #         TextClip(
        #             text,
        #             font=FONT_NAME,
        #             fontsize=FONT_SIZE,
        #             color="white",
        #             size=(VIDEO_WIDTH * 0.9, None),
        #             method="caption",
        #         )
        #         .set_position(("center", "center"))
        #         .set_start(start)
        #         .set_end(end)
        #     )
        # Create caption style
        caption_style = HighlightedCaptionStyle(FONT_NAME, FONT_SIZE, VIDEO_WIDTH)

        # Create caption clips with highlighting
        text_clips = []
        for start, end, text in captions:
            words = get_word_timing(text, start, end)
            text_clips.extend(caption_style.create_word_clips(words))

            # text_clips.append(clip)

        # Create final video
        final_video = CompositeVideoClip([background] + text_clips)

        # Generate silent version
        final_video.write_videofile(silent_output, fps=24, codec="libx264", audio=False)

        # Generate version with audio
        final_video = final_video.set_audio(audio_clip)
        final_video.write_videofile(
            audio_output, fps=24, codec="libx264", audio_codec="aac"
        )

        # Cleanup
        audio_clip.close()
        final_video.close()

        return True, f"Videos generated at:\n{audio_output}\n{silent_output}"

    except Exception as e:
        return False, f"Error generating video: {str(e)}"


def check_video_has_audio(video_path: str) -> bool:
    """Check if video file contains audio track."""
    try:
        with VideoFileClip(video_path) as video:
            return video.audio is not None
    except Exception as e:
        print(f"Error checking audio: {e}")
        return False


def process_video_with_audio(video_path: str) -> Tuple[bool, Optional[str]]:
    """Process video file that contains audio."""
    try:
        video = VideoFileClip(video_path)
        if not video.audio:
            return False, "No audio track found"

        # Extract audio for processing
        audio = video.audio
        audio_path = os.path.splitext(video_path)[0] + "_audio.mp3"
        audio.write_audiofile(audio_path)

        video.close()
        audio.close()
        return True, audio_path
    except Exception as e:
        return False, str(e)


def process_video_without_audio(
    video_path: str,
) -> Tuple[bool, Optional[VideoFileClip]]:
    """Process video file without audio track."""
    try:
        video = VideoFileClip(video_path)
        if video.audio:
            video.set_audio(None)
        return True, video
    except Exception:
        return False, None


def process_video(video_path: str) -> Tuple[bool, Optional[str]]:
    """Main function to process video based on audio presence."""
    if not os.path.exists(video_path):
        return False, "File not found"

    has_audio = check_video_has_audio(video_path)
    if has_audio:
        return process_video_with_audio(video_path)
    else:
        success, video = process_video_without_audio(video_path)
        if success and video:
            return True, "Video processed without audio"
        return False, "Failed to process video"


if __name__ == "__main__":
    # Use fixed input path
    input_audio = os.path.join(INPUT_DIR, "input_audio.mp3")

    if not os.path.exists(input_audio):
        print(f"Please place your audio file at: {input_audio}")
    else:
        success, message = generate_video_with_captions(
            input_audio,
            "captions",  # Base filename for output
        )
        print(message)
