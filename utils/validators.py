import os
from typing import List
from config.settings import SUPPORTED_IMAGE_FORMATS, SUPPORTED_AUDIO_FORMATS
from exceptions.custom_exceptions import ValidationError

def validate_image_folder(folder_path: str) -> List[str]:
    """
    Validate image folder and return list of valid image paths
    """
    if not os.path.exists(folder_path):
        raise ValidationError(f"Image folder does not exist: {folder_path}")
    
    valid_images = [
        f for f in os.listdir(folder_path) 
        if f.lower().endswith(SUPPORTED_IMAGE_FORMATS)
    ]
    
    if not valid_images:
        raise ValidationError("No valid images found in folder")
    
    return [os.path.join(folder_path, img) for img in sorted(valid_images)]

def validate_audio_file(audio_path: str) -> bool:
    """
    Validate audio file exists and has valid format
    """
    if not os.path.exists(audio_path):
        raise ValidationError(f"Audio file does not exist: {audio_path}")
    
    if not audio_path.lower().endswith(SUPPORTED_AUDIO_FORMATS):
        raise ValidationError(f"Unsupported audio format: {audio_path}")
    
    return True

def validate_output_path(output_path: str) -> bool:
    """
    Validate output path is writable
    """
    try:
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        return True
    except Exception as e:
        raise ValidationError(f"Invalid output path: {str(e)}")