# Video Generation Fix

## Problem
The video generation was creating text files and empty MP4 files instead of actual viewable videos when MoviePy was not available.

## Solution
Fixed the video generator to:
1. Check for required dependencies before attempting video creation
2. Create actual MP4 video files using MoviePy + PIL
3. Show clear error messages if dependencies are missing
4. Ensure download endpoint serves files with proper headers

## Files Changed
1. `video/video/generator.py` - Fixed video generation logic
2. `video/app/routes.py` - Updated generate-video and download endpoints

## Installation

### Step 1: Install Dependencies
Run the installation script:
```bash
cd video
install_video_deps.bat
```

Or manually install:
```bash
pip install moviepy==1.0.3 Pillow numpy
```

### Step 2: Verify Installation
```bash
python -c "import moviepy; from PIL import Image; import numpy; print('All dependencies installed!')"
```

### Step 3: Restart Video Service
```bash
cd video
python -m app.main
```

## How It Works

### Video Generation Process
1. User uploads a text script
2. Script is parsed into sentences
3. Each sentence becomes a 3-second frame
4. Frames are combined into a 1920x1080 MP4 video
5. Video is saved and can be downloaded

### Download Process
1. Generated video is stored in `bucket/videos/{content_id}.mp4`
2. Download endpoint serves the file with:
   - `Content-Type: video/mp4`
   - `Content-Disposition: attachment` (forces download)
   - CORS headers for frontend access

## API Endpoints

### Generate Video
```
POST /api/v1/step3/generate-video
Content-Type: multipart/form-data

Parameters:
- file: .txt script file
- title: Video title

Response:
{
  "content_id": "abc123",
  "title": "My Video",
  "download_url": "/download/abc123",
  "stream_url": "/stream/abc123"
}
```

### Download Video
```
GET /api/v1/step4/download/{content_id}

Response: MP4 file download
```

## Testing

### Test Video Generation
```bash
curl -X POST http://localhost:9000/api/v1/step3/generate-video \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@script.txt" \
  -F "title=Test Video"
```

### Test Download
```bash
curl -O -J http://localhost:9000/api/v1/step4/download/abc123
```

## Troubleshooting

### "Missing required packages" Error
**Solution**: Install dependencies
```bash
pip install moviepy==1.0.3 Pillow numpy
```

### "Video file is empty" Error
**Solution**: Check MoviePy installation and FFmpeg
```bash
python -c "import moviepy; print(moviepy.__file__)"
```

### Video Won't Play
**Solution**: Ensure the file is a valid MP4
- Check file size: Should be > 0 bytes
- Check file type: Should be video/mp4
- Try downloading with: `curl -I http://localhost:9000/api/v1/step4/download/{content_id}`

### Frontend Can't Download
**Solution**: Check CORS settings
- Backend should have CORS enabled for frontend URL
- Check browser console for CORS errors

## Technical Details

### Video Format
- Resolution: 1920x1080 (Full HD)
- Codec: H.264 (libx264)
- FPS: 24
- Frame Duration: 3 seconds per sentence
- Audio: None

### Dependencies
- **moviepy==1.0.3**: Video editing and encoding
- **Pillow**: Image generation for text frames
- **numpy**: Array operations for video frames
- **FFmpeg**: Video codec (usually included with moviepy)

## Future Improvements
1. Add background images/colors
2. Add transition effects between frames
3. Add background music option
4. Add text animations
5. Support for video templates
