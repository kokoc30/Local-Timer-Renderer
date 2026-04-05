from typing import Dict, Optional
from app.models.system_capabilities import Recommendation

class EncoderRecommendationService:
    """Recommends export strategy based on available hardware and software."""

    @staticmethod
    def get_recommendation(
        ffmpeg_installed: bool,
        encoders: Dict[str, bool]
    ) -> Recommendation:
        """Determines the best encoder to use."""
        if not ffmpeg_installed:
            return Recommendation(
                encoder_preference=None,
                video_encoder=None,
                reason="FFmpeg is not installed, so export is not ready."
            )
            
        # Priority 1: NVIDIA H.264
        if encoders.get("h264_nvenc"):
            return Recommendation(
                encoder_preference="nvidia",
                video_encoder="h264_nvenc",
                reason="NVIDIA H.264 hardware encoding detected. Fastest for this system."
            )
            
        # Priority 2: CPU H.264
        if encoders.get("libx264"):
            return Recommendation(
                encoder_preference="cpu",
                video_encoder="libx264",
                reason="CPU-based H.264 encoding (libx264) detected as fallback."
            )
            
        return Recommendation(
            encoder_preference=None,
            video_encoder=None,
            reason="FFmpeg is present, but no supported H.264 encoders (nvenc/libx264) were found."
        )

    @staticmethod
    def map_preference_to_label(preference: Optional[str]) -> str:
        """Helper to return a readable label for the preference."""
        labels = {
            "nvidia": "NVIDIA GPU",
            "cpu": "Basic CPU",
            "intel": "Intel QSV",
            "amd": "AMD AMF"
        }
        return labels.get(preference, "No Encoder Found")
