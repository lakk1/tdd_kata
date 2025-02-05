import os

# ImageMagick Configuration
MAGICK_HOME = 'C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe'
IMAGEMAGICK_BINARY = os.getenv('IMAGEMAGICK_BINARY', MAGICK_HOME)

# Video Settings
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
IMAGE_DURATION = 5
TRANSITION_DURATION = 1

# Processing Settings
MAX_WORKERS = os.cpu_count()

# Video Export Settings
DEFAULT_FPS = 30
DEFAULT_BITRATE = '8000k'

# Supported Formats
SUPPORTED_IMAGE_FORMATS = ('.png', '.jpg', '.jpeg')
SUPPORTED_AUDIO_FORMATS = ('.mp3', '.wav')

# Transition Types
TRANSITION_TYPES = {
    'crossfade': 'crossfadein',
    'fade': 'fadein',
    'slide_left': 'slide_left',
    'slide_right': 'slide_right',
    'zoom_in': 'zoom_in'
}

# Caption Settings
CAPTION_FONT = 'Arial'
CAPTION_FONTSIZE = 50
CAPTION_COLOR = 'white'
CAPTION_STROKE_COLOR = 'black'
CAPTION_STROKE_WIDTH = 3