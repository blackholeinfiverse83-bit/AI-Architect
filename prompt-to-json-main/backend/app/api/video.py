"""
Video Generation API - Integrated into main backend
Handles video generation from text scripts
"""
import os
import time
import uuid
import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Request
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from pydantic import BaseModel
from app.database import get_current_user_optional

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Video Generation"])

# Video generation models
class VideoGenerationResponse(BaseModel):
    content_id: str
    title: str
    status: str
    file_path: str
    download_url: str
    stream_url: str
    duration_ms: Optional[int] = None
    processing_status: str
    next_step: str

class ContentListResponse(BaseModel):
    items: list
    total_count: int

def create_demo_user():
    """Create demo user if needed"""
    try:
        from app.database import get_db, User
        from sqlalchemy.orm import Session
        db = next(get_db())
        demo_user = db.query(User).filter(User.username == 'demo').first()
        if not demo_user:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            demo_user = User(
                username='demo',
                password_hash=pwd_context.hash('demo1234'),
                email='demo@example.com'
            )
            db.add(demo_user)
            db.commit()
        return demo_user
    except Exception as e:
        logger.warning(f"Could not create demo user: {e}")
        return None

@router.post('/generate-video', response_model=VideoGenerationResponse, status_code=202)
async def generate_video(
    request: Request,
    file: UploadFile = File(...),
    title: str = Form(...)
):
    """Generate video from text script"""
    try:
        # Get current user (optional authentication)
        current_user = get_current_user_optional(request)
        
        # Handle unauthenticated requests
        if not current_user:
            demo_user = create_demo_user()
            user_id = demo_user.id if demo_user else "demo"
        else:
            user_id = current_user if isinstance(current_user, str) else getattr(current_user, 'username', 'demo')
        
        # Validate file
        ext = os.path.splitext(file.filename or '')[1].lower()
        if ext != '.txt':
            raise HTTPException(status_code=400, detail="Only .txt files allowed")
        if file.size is not None and file.size > 1_048_576:
            raise HTTPException(status_code=413, detail="Script file too large (max 1MB)")
        
        # Read script
        script_content = (await file.read()).decode('utf-8').strip()
        if not script_content:
            raise HTTPException(status_code=400, detail="Empty script content")
        
        # Generate content ID
        content_id = uuid.uuid4().hex[:12]
        
        # Create bucket directory if needed (use absolute path)
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        bucket_dir = os.path.join(backend_dir, "bucket", "videos")
        os.makedirs(bucket_dir, exist_ok=True)
        video_path = os.path.join(bucket_dir, f"{content_id}.mp4")
        # Normalize path for Windows
        video_path = os.path.normpath(video_path)
        
        # Generate video using MoviePy with PIL (no ImageMagick required)
        try:
            from moviepy.editor import ColorClip, CompositeVideoClip, concatenate_videoclips
            from moviepy.video.VideoClip import ImageClip
            from PIL import Image, ImageDraw, ImageFont
            import numpy as np
            import re
            
            # Parse lines from script
            lines = [line.strip() for line in script_content.split('\n') if line.strip()]
            if not lines:
                raise HTTPException(status_code=400, detail="No valid lines in script")
            
            # Load font with fallbacks
            font = None
            font_paths = [
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/calibri.ttf",
                "C:/Windows/Fonts/segoeui.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
            ]
            
            for font_path in font_paths:
                try:
                    if os.path.exists(font_path):
                        font = ImageFont.truetype(font_path, 60)
                        break
                except:
                    continue
            
            if font is None:
                font = ImageFont.load_default()
            
            clips = []
            frame_duration = 3.0
            max_width = 1200  # For 1280 width with margins
            
            for line in lines:
                # Create black background clip
                bg_clip = ColorClip(size=(1280, 720), color=(0, 0, 0), duration=frame_duration)
                
                # Create text image using PIL
                img = Image.new('RGB', (1280, 720), (0, 0, 0))
                draw = ImageDraw.Draw(img)
                
                # Handle text wrapping
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                
                if text_width <= max_width:
                    display_text = line
                else:
                    # Wrap text
                    words = line.split()
                    lines_wrapped = []
                    current_line = ""
                    
                    for word in words:
                        test_line = current_line + " " + word if current_line else word
                        test_bbox = draw.textbbox((0, 0), test_line, font=font)
                        
                        if test_bbox[2] - test_bbox[0] <= max_width:
                            current_line = test_line
                        else:
                            if current_line:
                                lines_wrapped.append(current_line)
                            current_line = word
                    
                    if current_line:
                        lines_wrapped.append(current_line)
                    
                    display_text = "\n".join(lines_wrapped)
                
                # Calculate centered position
                bbox = draw.multiline_textbbox((0, 0), display_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (1280 - text_width) // 2
                y = (720 - text_height) // 2
                
                # Draw white text
                draw.multiline_text((x, y), display_text, font=font, fill=(255, 255, 255), align='center')
                
                # Convert to numpy array and create clip
                img_array = np.array(img)
                text_clip = ImageClip(img_array, duration=frame_duration)
                
                # Combine background and text
                frame_clip = CompositeVideoClip([bg_clip, text_clip])
                clips.append(frame_clip)
            
            if not clips:
                raise HTTPException(status_code=400, detail="No valid lines in script")
            
            # Concatenate clips
            final_clip = concatenate_videoclips(clips, method="compose")
            final_clip.write_videofile(
                video_path, 
                fps=24, 
                codec='libx264', 
                audio=False,
                preset='medium',
                threads=4
            )
            final_clip.close()
            
            # Clean up individual clips
            for clip in clips:
                clip.close()
            
            # Calculate duration
            duration_ms = len(clips) * int(frame_duration * 1000)
            
        except ImportError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Video generation dependencies missing: {str(e)}. Install: pip install moviepy pillow numpy"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")
        
        # Save to database (try to create table if it doesn't exist)
        try:
            from app.database import get_db, engine
            from app.models import Content, Base
            from sqlalchemy import inspect
            
            # Ensure table exists
            inspector = inspect(engine)
            if 'content' not in inspector.get_table_names():
                logger.info("Creating content table...")
                Base.metadata.create_all(bind=engine, tables=[Content.__table__])
            
            db = next(get_db())
            content = Content(
                content_id=content_id,
                uploader_id=user_id,
                title=title,
                file_path=video_path,
                content_type='video/mp4',
                duration_ms=duration_ms,
                uploaded_at=time.time()
            )
            db.add(content)
            db.commit()
            logger.info(f"Video saved to database: {content_id}")
        except Exception as e:
            logger.warning(f"Could not save to database (video file still available): {e}")
            # Video file is still created, just not in database
        
        return VideoGenerationResponse(
            content_id=content_id,
            title=title,
            status="completed",
            file_path=video_path,
            download_url=f"/api/v1/video/download/{content_id}",
            stream_url=f"/api/v1/video/stream/{content_id}",
            duration_ms=duration_ms,
            processing_status="completed",
            next_step=f"Use /api/v1/video/content/{content_id} to view details"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/health')
async def video_health():
    """Video API health check"""
    return {"status": "ok", "service": "Video Generation API"}

@router.get('/contents', response_model=ContentListResponse)
async def list_contents(
    limit: int = 20,
    request: Request
):
    """List all generated videos"""
    # Get current user (optional authentication)
    current_user = get_current_user_optional(request)
    
    items = []
    
    # Try database first
    try:
        from app.database import get_db
        from app.models import Content
        db = next(get_db())
        
        contents = db.query(Content).filter(
            Content.content_type == 'video/mp4'
        ).order_by(Content.uploaded_at.desc()).limit(limit).all()
        
        for content in contents:
            items.append({
                'content_id': content.content_id,
                'title': content.title or 'Untitled Video',
                'file_path': content.file_path,
                'duration_ms': content.duration_ms or 0,
                'uploaded_at': content.uploaded_at or time.time(),
                'download_url': f"/api/v1/video/download/{content.content_id}",
                'stream_url': f"/api/v1/video/stream/{content.content_id}"
            })
    except Exception as db_error:
        logger.warning(f"Database query failed, trying file system: {db_error}")
        # Fallback: scan file system for videos
        try:
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            videos_dir = os.path.join(backend_dir, "bucket", "videos")
            videos_dir = os.path.normpath(videos_dir)
            
            if os.path.exists(videos_dir):
                video_files = [f for f in os.listdir(videos_dir) if f.endswith('.mp4')]
                for video_file in sorted(video_files, key=lambda x: os.path.getmtime(os.path.join(videos_dir, x)), reverse=True)[:limit]:
                    content_id = os.path.splitext(video_file)[0]
                    file_path = os.path.join(videos_dir, video_file)
                    file_stat = os.stat(file_path)
                    
                    items.append({
                        'content_id': content_id,
                        'title': video_file.replace('.mp4', ''),
                        'file_path': file_path,
                        'duration_ms': 0,  # Unknown without reading file
                        'uploaded_at': file_stat.st_mtime,
                        'download_url': f"/api/v1/video/download/{content_id}",
                        'stream_url': f"/api/v1/video/stream/{content_id}"
                    })
        except Exception as fs_error:
            logger.error(f"File system scan failed: {fs_error}")
    
    return ContentListResponse(items=items, total_count=len(items))

@router.get('/content/{content_id}')
async def get_content(content_id: str):
    """Get video content details"""
    # Try database first
    try:
        from app.database import get_db
        from app.models import Content
        db = next(get_db())
        
        content = db.query(Content).filter(
            Content.content_id == content_id,
            Content.content_type == 'video/mp4'
        ).first()
        
        if content:
            return {
                'content_id': content.content_id,
                'title': content.title or 'Untitled Video',
                'file_path': content.file_path,
                'duration_ms': content.duration_ms or 0,
                'uploaded_at': content.uploaded_at or time.time(),
                'download_url': f"/api/v1/video/download/{content.content_id}",
                'stream_url': f"/api/v1/video/stream/{content.content_id}"
            }
    except Exception:
        pass  # Fall through to file system lookup
    
    # Fallback: check file system
    try:
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        video_path = os.path.join(backend_dir, "bucket", "videos", f"{content_id}.mp4")
        video_path = os.path.normpath(video_path)
        
        if os.path.exists(video_path):
            file_stat = os.stat(video_path)
            return {
                'content_id': content_id,
                'title': os.path.basename(video_path).replace('.mp4', ''),
                'file_path': video_path,
                'duration_ms': 0,
                'uploaded_at': file_stat.st_mtime,
                'download_url': f"/api/v1/video/download/{content_id}",
                'stream_url': f"/api/v1/video/stream/{content_id}"
            }
    except Exception:
        pass
    
    raise HTTPException(status_code=404, detail="Content not found")

@router.get('/download/{content_id}')
async def download_video(content_id: str):
    """Download video file"""
    file_path = None
    
    # Try database first
    try:
        from app.database import get_db
        from app.models import Content
        db = next(get_db())
        
        content = db.query(Content).filter(
            Content.content_id == content_id,
            Content.content_type == 'video/mp4'
        ).first()
        
        if content:
            file_path = content.file_path
    except Exception:
        pass  # Fall through to file system lookup
    
    # Fallback: check file system
    if not file_path:
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        file_path = os.path.join(backend_dir, "bucket", "videos", f"{content_id}.mp4")
        file_path = os.path.normpath(file_path)
    
    # Normalize and resolve file path
    if file_path:
        file_path = file_path.replace('\\', '/')
        if not os.path.isabs(file_path):
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            file_path = os.path.join(backend_dir, file_path)
        file_path = os.path.normpath(file_path)
    
    # Try multiple possible locations
    if not file_path or not os.path.exists(file_path):
        # Try just the filename in bucket/videos
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        alt_path = os.path.join(backend_dir, "bucket", "videos", f"{content_id}.mp4")
        alt_path = os.path.normpath(alt_path)
        if os.path.exists(alt_path):
            file_path = alt_path
        else:
            raise HTTPException(status_code=404, detail=f"Video file not found for content_id: {content_id}")
    
    return FileResponse(
        file_path,
        media_type='video/mp4',
        filename=f"{content_id}.mp4",
        headers={
            "Content-Disposition": f"attachment; filename={content_id}.mp4",
            "Access-Control-Allow-Origin": "*"
        }
    )

@router.get('/stream/{content_id}')
async def stream_video(content_id: str, request: Request):
    """Stream video with range support"""
    file_path = None
    
    # Try database first
    try:
        from app.database import get_db
        from app.models import Content
        db = next(get_db())
        
        content = db.query(Content).filter(
            Content.content_id == content_id,
            Content.content_type == 'video/mp4'
        ).first()
        
        if content:
            file_path = content.file_path
    except Exception:
        pass  # Fall through to file system lookup
    
    # Fallback: check file system
    if not file_path:
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        file_path = os.path.join(backend_dir, "bucket", "videos", f"{content_id}.mp4")
        file_path = os.path.normpath(file_path)
    
    # Normalize and resolve file path
    if file_path:
        file_path = file_path.replace('\\', '/')
        if not os.path.isabs(file_path):
            backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            file_path = os.path.join(backend_dir, file_path)
        file_path = os.path.normpath(file_path)
    
    # Try multiple possible locations
    if not file_path or not os.path.exists(file_path):
        # Try just the filename in bucket/videos
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        alt_path = os.path.join(backend_dir, "bucket", "videos", f"{content_id}.mp4")
        alt_path = os.path.normpath(alt_path)
        if os.path.exists(alt_path):
            file_path = alt_path
        else:
            raise HTTPException(status_code=404, detail=f"Video file not found for content_id: {content_id}")
    
    file_size = os.path.getsize(file_path)
    range_header = request.headers.get('range')
    
    if range_header:
        # Handle range requests
        start = int(range_header.replace('bytes=', '').split('-')[0])
        end = min(start + 1024 * 1024, file_size - 1)  # 1MB chunks
        
        def iter_file():
            with open(file_path, 'rb') as f:
                f.seek(start)
                remaining = end - start + 1
                while remaining > 0:
                    chunk_size = min(1024 * 1024, remaining)
                    data = f.read(chunk_size)
                    if not data:
                        break
                    remaining -= len(data)
                    yield data
        
        return StreamingResponse(
            iter_file(),
            status_code=206,
            headers={
                'Content-Range': f'bytes {start}-{end}/{file_size}',
                'Accept-Ranges': 'bytes',
                'Content-Length': str(end - start + 1),
                'Content-Type': 'video/mp4',
                'Access-Control-Allow-Origin': '*'
            },
            media_type='video/mp4'
        )
    else:
        # Full file
        return FileResponse(
            file_path,
            media_type='video/mp4',
            headers={
                'Accept-Ranges': 'bytes',
                'Content-Length': str(file_size),
                'Access-Control-Allow-Origin': '*'
            }
        )

@router.delete('/content/{content_id}')
async def delete_content(content_id: str):
    """Delete video content"""
    try:
        from app.database import get_db
        from app.models import Content
        db = next(get_db())
        
        content = db.query(Content).filter(
            Content.content_id == content_id,
            Content.content_type == 'video/mp4'
        ).first()
        
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        file_path = content.file_path
        
        # Delete from database
        db.delete(content)
        db.commit()
        
        # Delete file
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return {"status": "success", "message": "Content deleted successfully", "content_id": content_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
