# main.py
import os
import time
from core.video_generator import VideoGenerator

def progress_callback(completed: int, total: int):
    """Simple progress callback"""
    percentage = (completed / total) * 100
    print(f"Progress: {percentage:.2f}%")

def ensure_directory_exists(file_path: str):
    """Ensure the directory for the file exists"""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

def main():
    # Initialize video generator
    generator = VideoGenerator()
    
    # Set paths - use absolute paths or proper relative paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    image_folder = os.path.join(current_dir, "input", "images")
    audio_path = os.path.join(current_dir, "input", "input_audio.mp3")
    output_path = os.path.join(current_dir, "output", "output_video.mp4")
    
    # Ensure directories exist
    ensure_directory_exists(output_path)
    
    # Validate input paths exist
    if not os.path.exists(image_folder):
        print(f"Error: Image folder not found at {image_folder}")
        return
    
    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found at {audio_path}")
        return
    
    print(f"Processing video with:")
    print(f"Images from: {image_folder}")
    print(f"Audio from: {audio_path}")
    print(f"Output to: {output_path}")
    
    # Record start time
    start_time = time.time()
    
    try:
        # Generate video
        success, message = generator.create_video(
            image_folder=image_folder,
            audio_path=audio_path,
            output_path=output_path,
            add_captions=True,
            progress_callback=progress_callback
        )
        
        # Print result
        print(message)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        
    finally:
        print(f"Time taken: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main()