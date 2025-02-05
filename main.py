import os
from src.utils.config import INPUT_AUDIO_PATH
from src.processors.video_generator import VideoProcessor


def main():
    if not os.path.exists(INPUT_AUDIO_PATH):
        print(f"Please place your audio file at: {INPUT_AUDIO_PATH}")
        return

    processor = VideoProcessor()
    success, message = processor.generate_video_with_captions(
        INPUT_AUDIO_PATH,
        "captions",  # Base filename for output
    )
    print(message)


if __name__ == "__main__":
    main()
