from fastapi import APIRouter
from app.core import config
from app.services.ffmpeg_detection_service import ffmpeg_detection_service

router = APIRouter(prefix="/api/system", tags=["system"])

@router.get("/status")
async def get_status():
    """
    Returns basic application status and system configuration.
    """
    ffmpeg_info = ffmpeg_detection_service.get_info()
    encoders = {}
    if ffmpeg_info.callable and ffmpeg_info.path:
        encoders = ffmpeg_detection_service.get_encoders(ffmpeg_info.path)
        
    return {
        "ok": True,
        "app_name": config.APP_NAME,
        "version": config.VERSION,
        "system_info": {
            "ffmpeg_installed": ffmpeg_info.installed,
            "nvenc_available": encoders.get("h264_nvenc", False),
        }
    }
