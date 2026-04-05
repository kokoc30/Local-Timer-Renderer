from pydantic import BaseModel, Field, validator, field_validator
from typing import Optional
import re

class RenderSettings(BaseModel):
    """
    Canonical model for timer render settings.
    Includes validation for all fields.
    """
    mode: str = Field(default="countdown", description="Timer mode: countdown")
    start_time: str = Field(default="60:00", description="Initial timer value: MM:SS or HH:MM:SS")
    display_format: str = Field(default="MM:SS", description="Timer display style")
    preview_speed: float = Field(default=1.0, gt=0, le=500.0, description="Preview playback speed (Internal render is always 1:1)")
    width: int = Field(default=1920, ge=160, le=3840, description="Video width")
    height: int = Field(default=1080, ge=90, le=2160, description="Video height")
    fps: int = Field(default=60, ge=1, le=120, description="Frames per second")
    style_preset: str = Field(default="watch-frame", description="Visual style preset")
    background_color: str = Field(default="#000000", description="Background hex color")
    text_color: str = Field(default="#FFFFFF", description="Text hex color")
    output_format: str = Field(default="mp4", description="Output container format")
    encoder_preference: str = Field(default="auto", description="Preferred encoder: auto, cpu, nvidia")

    @field_validator("start_time")
    @classmethod
    def validate_start_time(cls, v):
        # Match MM:SS or HH:MM:SS or H:MM:SS
        if not re.match(r"^(?:(\d+):)?(\d+):([0-5]\d)$", v):
            raise ValueError("Start time must be in MM:SS or HH:MM:SS format.")
        
        # Additional check: prevent 0 duration
        from app.utils.time_utils import parse_time_string
        try:
            seconds = parse_time_string(v)
            if seconds <= 0:
                raise ValueError("Start time must be at least 1 second.")
            if seconds > 86400: # 24 hours max for this tool
                raise ValueError("Start time cannot exceed 24 hours.")
        except Exception:
            pass # Let the regex handle basic format errors
            
        return v

    @field_validator("background_color", "text_color")
    @classmethod
    def validate_hex_color(cls, v):
        if not re.match(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$", v):
            raise ValueError("Color must be a valid hex code (e.g., #000000).")
        return v.upper()

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v):
        if v.lower() != "countdown":
            raise ValueError("Currently only 'countdown' mode is supported.")
        return v.lower()

    @field_validator("display_format")
    @classmethod
    def validate_display_format(cls, v):
        if v not in ["MM:SS", "HH:MM:SS", "M:SS", "H:MM:SS"]:
            raise ValueError("Invalid display format.")
        return v

    @field_validator("style_preset")
    @classmethod
    def validate_style_preset(cls, v):
        # Standardize to kebab-case
        v = v.replace("_", "-").lower()
        presets = ["minimal-digital", "watch-frame", "bold-center", "thin-modern"]
        if v not in presets:
            raise ValueError(f"Unknown style preset: {v}. Available: {', '.join(presets)}")
        return v

    @field_validator("encoder_preference")
    @classmethod
    def validate_encoder(cls, v):
        valid = ["auto", "cpu", "gpu", "nvidia"]
        if v.lower() not in valid:
            raise ValueError(f"Invalid encoder preference. Available: {', '.join(valid)}")
        return v.lower()
