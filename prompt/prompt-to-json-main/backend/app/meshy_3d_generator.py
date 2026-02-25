import asyncio
import logging
import os

import httpx
from app.config import settings

logger = logging.getLogger(__name__)


async def generate_3d_with_meshy(prompt: str, dimensions: dict) -> bytes:
    """Generate realistic 3D construction model using Meshy AI"""
    MESHY_API_KEY = os.getenv("MESHY_API_KEY") or getattr(settings, "MESHY_API_KEY", None)

    if not MESHY_API_KEY:
        logger.warning("Meshy API key not configured")
        return None

    logger.info(f"Using Meshy API key: {MESHY_API_KEY[:10]}...")

    width = dimensions.get("width", 10)
    length = dimensions.get("length", 10)
    height = dimensions.get("height", 3)

    detailed_prompt = f"""Realistic 3D architectural construction model: {prompt}
Exact dimensions: {width}m wide × {length}m long × {height}m tall
Include: concrete foundation, brick/concrete walls, flat roof slab, wooden doors, aluminum windows
Modern residential construction style with realistic textures
Detailed architectural visualization"""

    try:
        # Increased timeout to 5 minutes to allow Meshy to complete
        async with httpx.AsyncClient(timeout=300.0) as client:
            logger.info(f"Starting Meshy 3D generation...")
            response = await client.post(
                "https://api.meshy.ai/v2/text-to-3d",
                headers={"Authorization": f"Bearer {MESHY_API_KEY}"},
                json={
                    "mode": "preview",
                    "prompt": detailed_prompt,
                    "art_style": "realistic",
                    "negative_prompt": "cartoon, low quality, distorted",
                },
            )

            if response.status_code not in [200, 202]:
                logger.error(f"Meshy error: {response.status_code} - {response.text}")
                return None

            task_id = response.json()["result"]
            logger.info(f"Meshy task created: {task_id}, waiting for completion...")
            print(f"Task ID: {task_id}")
            print("Polling status every 2 seconds...")

            # Increased timeout to allow Meshy to complete (3D generation can take 3-8 minutes)
            max_attempts = 300  # 10 minutes total (300 attempts * 2 seconds = 600 seconds)
            stuck_at_99_count = 0
            max_stuck_attempts = 150  # If stuck at 99% for 150 attempts (5 minutes), timeout
            # Note: Meshy sometimes shows 99% for a while before completing, so we wait much longer
            # Also, Meshy may have model_urls ready even when status is still IN_PROGRESS
            
            for attempt in range(max_attempts):
                await asyncio.sleep(2)
                status_resp = await client.get(
                    f"https://api.meshy.ai/v2/text-to-3d/{task_id}",
                    headers={"Authorization": f"Bearer {MESHY_API_KEY}"},
                )

                if status_resp.status_code == 200:
                    result = status_resp.json()
                    status = result.get("status")
                    progress = result.get("progress", 0)
                    model_urls = result.get("model_urls", {})
                    
                    # Log every 10th attempt or on important status changes to reduce spam
                    if attempt % 10 == 0 or status == "SUCCEEDED" or status == "FAILED" or progress < 99:
                        print(f"Attempt {attempt + 1}/{max_attempts}: Status={status}, Progress={progress}%")
                    
                    # CRITICAL FIX: Check for model_urls even when status is IN_PROGRESS
                    # Meshy sometimes has the model ready before status changes to SUCCEEDED
                    glb_url = model_urls.get("glb")
                    if glb_url:
                        try:
                            print(f"✅ Found GLB URL at progress {progress}% (status: {status}), downloading...")
                            glb_resp = await client.get(glb_url, timeout=30.0)
                            if glb_resp.status_code == 200 and len(glb_resp.content) > 0:
                                logger.info(f"✅ Meshy 3D generated: {len(glb_resp.content)} bytes")
                                print(f"✅ Successfully downloaded {len(glb_resp.content)} bytes")
                                return glb_resp.content
                            else:
                                print(f"⚠️ GLB URL returned empty or error: {glb_resp.status_code}")
                        except Exception as e:
                            print(f"⚠️ Failed to download GLB: {e}, continuing to wait...")
                            # Continue waiting if download fails - might not be ready yet

                    if status == "SUCCEEDED":
                        # Double-check with SUCCEEDED status
                        if glb_url:
                            print(f"Downloading GLB from: {glb_url}")
                            glb_resp = await client.get(glb_url)
                            logger.info(f"✅ Meshy 3D generated: {len(glb_resp.content)} bytes")
                            return glb_resp.content
                    elif status == "FAILED":
                        error = result.get("error", "Unknown error")
                        logger.error(f"Meshy failed: {error}")
                        print(f"Task failed: {error}")
                        return None
                    elif status == "IN_PROGRESS" and progress >= 99:
                        stuck_at_99_count += 1
                        # Log every 20 attempts when stuck at 99%
                        if stuck_at_99_count % 20 == 0:
                            print(f"⏳ Still at 99%: {stuck_at_99_count}/{max_stuck_attempts} attempts (waiting for model to complete...)")
                        if stuck_at_99_count >= max_stuck_attempts:
                            logger.warning(f"Meshy stuck at 99% for {stuck_at_99_count} attempts, timing out")
                            print(f"⚠️ Meshy stuck at 99%, timing out after {max_stuck_attempts} attempts")
                            return None
                    else:
                        stuck_at_99_count = 0  # Reset counter if progress changes
                else:
                    print(f"Status check failed: HTTP {status_resp.status_code}")

            logger.warning("Meshy timeout after 10 minutes or stuck at 99% for 5 minutes")
            return None
    except Exception as e:
        logger.error(f"Meshy error: {e}")
        return None
