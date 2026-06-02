import os
import time
import logging
import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from gtts import gTTS

# Optional Coqui TTS import
try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

router = APIRouter()
logger = logging.getLogger(__name__)

# Settings
TEMP_AUDIO_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "temp_audio")
os.makedirs(TEMP_AUDIO_DIR, exist_ok=True)

# Initialize TTS Model (Global to avoid reloading)
tts_model = None

def get_tts_model():
    global tts_model
    if TTS_AVAILABLE and tts_model is None:
        try:
            logger.info("Initializing Coqui XTTS v2...")
            # Using xtts_v2 which is high quality
            tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2", gpu=False) # Default to CPU for stability
            logger.info("Coqui XTTS v2 initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Coqui TTS: {e}")
            return None
    return tts_model

class TTSRequest(BaseModel):
    text: str
    speed: float = 1.0
    voice_id: str = "Claribel Dervla" # Default Coqui voice

def cleanup_file(filepath: str):
    """Delete a file after a delay."""
    try:
        time.sleep(60) # Wait 1 minute before cleanup
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.debug(f"Cleaned up temp audio: {filepath}")
    except Exception as e:
        logger.error(f"Cleanup failed for {filepath}: {e}")

@router.post("/tts")
async def generate_tts(request: TTSRequest, background_tasks: BackgroundTasks):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    filename = f"tts_{uuid.uuid4().hex}.mp3"
    filepath = os.path.join(TEMP_AUDIO_DIR, filename)

    try:
        model = get_tts_model()
        
        if model:
            logger.info(f"Generating audio with Coqui XTTS: '{request.text[:50]}...'")
            model.tts_to_file(
                text=request.text,
                file_path=filepath,
                speaker=request.voice_id,
                language="en"
            )
        else:
            try:
                logger.info(f"Coqui not available, trying gTTS: '{request.text[:50]}...'")
                tts = gTTS(text=request.text, lang='en')
                tts.save(filepath)
            except Exception as e:
                logger.warning(f"gTTS failed (likely network error): {e}. Falling back to pyttsx3 (Offline).")
                try:
                    import pyttsx3
                    engine = pyttsx3.init()
                    # On Windows, pyttsx3.save_to_file works well without needing a manual loop
                    engine.save_to_file(request.text, filepath)
                    engine.runAndWait()
                    logger.info("Successfully generated audio using pyttsx3 (Offline)")
                except ImportError:
                    logger.error("pyttsx3 not installed. Cannot perform offline fallback.")
                    raise e
                except Exception as ex:
                    logger.error(f"pyttsx3 also failed: {ex}")
                    raise e

        if not os.path.exists(filepath):
             raise HTTPException(status_code=500, detail="Audio file generation failed")

        # Schedule cleanup
        background_tasks.add_task(cleanup_file, filepath)

        return FileResponse(
            path=filepath, 
            media_type="audio/mpeg", 
            filename=filename
        )

    except Exception as e:
        logger.error(f"TTS Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
