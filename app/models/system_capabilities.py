from pydantic import BaseModel
from typing import List, Optional, Dict

class FFmpegInfo(BaseModel):
    """Details about the FFmpeg executable."""
    installed: bool
    callable: bool
    path: Optional[str] = None
    version: Optional[str] = None
    error: Optional[str] = None

class EncoderCapabilities(BaseModel):
    """Availability of specific video encoders."""
    libx264: bool = False
    h264_nvenc: bool = False
    hevc_nvenc: bool = False
    h264_qsv: bool = False
    hevc_qsv: bool = False
    h264_amf: bool = False
    hevc_amf: bool = False

class Recommendation(BaseModel):
    """System recommendation for export settings."""
    encoder_preference: Optional[str] = None # 'nvidia', 'cpu', etc.
    video_encoder: Optional[str] = None      # 'h264_nvenc', 'libx264'
    reason: str

class SystemCapabilitiesResponse(BaseModel):
    """Full structured report on system capabilities."""
    ok: bool
    ffmpeg: FFmpegInfo
    encoders: Dict[str, bool]
    hwaccels: List[str]
    recommendation: Recommendation
