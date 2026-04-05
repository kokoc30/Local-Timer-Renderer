from fastapi import APIRouter
from app.services.ffmpeg_detection_service import ffmpeg_detection_service
from app.services.encoder_recommendation_service import EncoderRecommendationService
from app.models.system_capabilities import SystemCapabilitiesResponse

router = APIRouter(prefix="/api/system/capabilities", tags=["capabilities"])

@router.get("", response_model=SystemCapabilitiesResponse)
async def get_capabilities():
    """
    Returns a structured system capability report.
    This includes FFmpeg availability, encoders, and hardware acceleration types.
    """
    # 1. FFmpeg metadata
    ffmpeg_info = ffmpeg_detection_service.get_info()
    
    # 2. Advanced diagnostics (if ffmpeg is available)
    encoders = {}
    hwaccels = []
    if ffmpeg_info.callable and ffmpeg_info.path:
        encoders = ffmpeg_detection_service.get_encoders(ffmpeg_info.path)
        hwaccels = ffmpeg_detection_service.get_hwaccels(ffmpeg_info.path)
        
    # 3. Recommendation
    recommendation = EncoderRecommendationService.get_recommendation(
        ffmpeg_info.installed,
        encoders
    )
    
    return {
        "ok": True,
        "ffmpeg": ffmpeg_info,
        "encoders": encoders,
        "hwaccels": hwaccels,
        "recommendation": recommendation
    }

@router.post("/refresh")
async def refresh_capabilities():
    """
    Manually refreshes capabilities detection.
    Useful for interactive diagnostics in the UI.
    """
    return await get_capabilities()
