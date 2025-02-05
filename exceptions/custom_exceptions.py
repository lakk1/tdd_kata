class VideoGenerationError(Exception):
    """Base exception for video generation errors"""
    pass

class ImageProcessingError(VideoGenerationError):
    """Raised when there's an error processing images"""
    pass

class AudioProcessingError(VideoGenerationError):
    """Raised when there's an error processing audio"""
    pass

class ValidationError(VideoGenerationError):
    """Raised when input validation fails"""
    pass

class CaptionGenerationError(VideoGenerationError):
    """Raised when there's an error generating captions"""
    pass

class TransitionError(VideoGenerationError):
    """Raised when there's an error applying transitions"""
    pass