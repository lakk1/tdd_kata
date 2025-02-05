import os

# Video dimensions
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920

# Font settings
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
