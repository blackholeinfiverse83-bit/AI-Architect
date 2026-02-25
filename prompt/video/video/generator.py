# video/generator.py - FIXED VERSION
import os
import sys
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

# Add the parent directory to sys.path to import core modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Check for required dependencies
def check_dependencies():
    """Check if all required dependencies are available"""
    missing = []
    
    try:
        import moviepy
    except ImportError:
        missing.append("moviepy==1.0.3")
    
    try:
        import PIL
    except ImportError:
        missing.append("Pillow")
    
    try:
        import numpy
    except ImportError:
        missing.append("numpy")
    
    return missing

# Check at module load
MISSING_DEPS = check_dependencies()
if MISSING_DEPS:
    print(f"WARNING: Missing dependencies: {', '.join(MISSING_DEPS)}")
    print("Install with: pip install moviepy==1.0.3 Pillow numpy")
    MOVIEPY_AVAILABLE = False
else:
    MOVIEPY_AVAILABLE = True

try:
    from core import bhiv_bucket
except ImportError:
    bhiv_bucket = None

def create_downloadable_video(text: str, output_path: str, frame_duration: float = 3.0) -> str:
    """
    Create an actual MP4 video file that can be downloaded and played.
    Each sentence becomes a frame in the video.
    
    Returns:
        str: Path to the created MP4 file
    
    Raises:
        ImportError: If required dependencies are missing
        ValueError: If video creation fails
    """
    # Check dependencies first
    missing = check_dependencies()
    if missing:
        raise ImportError(f"Missing required packages: {', '.join(missing)}. Run: pip install {' '.join(missing)}")
    
    try:
        from moviepy.editor import ColorClip, CompositeVideoClip, concatenate_videoclips
        from moviepy.video.VideoClip import ImageClip
        import numpy as np
        from PIL import Image, ImageDraw, ImageFont
        import re
    except ImportError as e:
        raise ImportError(f"Failed to import required modules: {e}")
    
    if not text or not text.strip():
        text = "No content provided"
    
    # Parse sentences from text
    sentences = []
    for line in text.split('\n'):
        line = line.strip()
        if line:
            # Split by sentence endings but keep the content
            parts = re.split(r'[.!?]+', line)
            for part in parts:
                part = part.strip()
                if part and len(part) > 2:  # Only add meaningful sentences
                    sentences.append(part)
    
    if not sentences:
        sentences = ["Generated Video"]
    
    print(f"Creating video with {len(sentences)} frames...")
    
    # Create output directory
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    clips = []
    
    # Load font with fallbacks
    font = None
    font_paths = [
        "arial.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    
    for font_path in font_paths:
        try:
            font = ImageFont.truetype(font_path, 60)
            print(f"Using font: {font_path}")
            break
        except:
            continue
    
    if font is None:
        font = ImageFont.load_default()
        print("Using default font")
    
    max_width = 1800  # Leave margins for 1920 width
    
    for i, sentence in enumerate(sentences):
        print(f"Processing frame {i+1}/{len(sentences)}: {sentence[:50]}...")
        
        # Create black background
        bg_clip = ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=frame_duration)
        
        # Create text image
        img = Image.new('RGB', (1920, 1080), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Handle text wrapping
        bbox = draw.textbbox((0, 0), sentence, font=font)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width:
            # Single line
            display_text = sentence
        else:
            # Wrap text
            words = sentence.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                test_bbox = draw.textbbox((0, 0), test_line, font=font)
                
                if test_bbox[2] - test_bbox[0] <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            display_text = "\n".join(lines)
        
        # Calculate centered position
        bbox = draw.multiline_textbbox((0, 0), display_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (1920 - text_width) // 2
        y = (1080 - text_height) // 2
        
        # Draw white text
        draw.multiline_text((x, y), display_text, font=font, fill=(255, 255, 255), align='center')
        
        # Convert to numpy array and create clip
        img_array = np.array(img)
        text_clip = ImageClip(img_array, duration=frame_duration)
        
        # Combine background and text
        frame_clip = CompositeVideoClip([bg_clip, text_clip])
        clips.append(frame_clip)
    
    print(f"Concatenating {len(clips)} clips...")
    
    # Concatenate all frames
    final_clip = concatenate_videoclips(clips, method="compose")
    
    # Export as MP4 with proper codec
    print(f"Exporting video to: {output_path}")
    final_clip.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio=False,
        verbose=False,
        logger=None,
        threads=4,
        preset='medium'
    )
    
    # Clean up
    final_clip.close()
    for clip in clips:
        clip.close()
    
    # Verify file was created
    if not os.path.exists(output_path):
        raise ValueError(f"Video file was not created: {output_path}")
    
    file_size = os.path.getsize(output_path)
    if file_size == 0:
        raise ValueError(f"Video file is empty: {output_path}")
    
    print(f"Video created successfully: {output_path} ({file_size} bytes)")
    return output_path


def get_video_info(video_path: str) -> Dict:
    """Get information about the video file"""
    try:
        video_file = Path(video_path)
        
        if not video_file.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        file_size = video_file.stat().st_size
        
        # Try to get video metadata using moviepy
        try:
            from moviepy.editor import VideoFileClip
            with VideoFileClip(str(video_file)) as clip:
                duration = clip.duration
                fps = clip.fps
                size = clip.size
        except:
            duration = 0
            fps = 24
            size = (1920, 1080)
        
        return {
            "file_path": str(video_file),
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2),
            "duration_seconds": round(duration, 2),
            "fps": fps,
            "resolution": f"{size[0]}x{size[1]}" if size else "1920x1080",
            "exists": True
        }
        
    except Exception as e:
        return {
            "file_path": str(video_path),
            "error": str(e),
            "exists": False
        }


# Keep backward compatibility aliases
create_multi_frame_video = create_downloadable_video
create_simple_video = create_downloadable_video

def render_video_from_storyboard(storyboard: Dict, output_path: str, width: int = 1280, height: int = 720) -> str:
    """Generate video from storyboard - delegates to main function"""
    # Extract text from storyboard
    text_content = ""
    for scene in storyboard.get("scenes", []):
        for frame in scene.get("frames", []):
            text = frame.get("text", "")
            if text:
                text_content += text + ". "
    
    if not text_content:
        text_content = "Generated Video"
    
    return create_downloadable_video(text_content, output_path)
