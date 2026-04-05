from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import Optional, List
from app.models.render_settings import RenderSettings
from app.models.render_plan import RenderPlan
from datetime import datetime

class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    ENCODING_VIDEO = "encoding_video"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class RenderJob(BaseModel):
    """
    State and metadata for a frame rendering job.
    """
    model_config = ConfigDict(use_enum_values=True)
    
    job_id: str
    status: JobStatus = JobStatus.QUEUED
    created_at: str
    updated_at: str
    
    # Progress
    progress_current_frame: int = 0
    total_frames: int = 0
    progress_percent: float = 0.0
    
    # Paths & outputs
    output_dir: str = ""
    frames_dir: str = ""
    error_message: Optional[str] = None
    sample_output_paths: List[str] = []
    
    # MP4 Export Metadata
    export_started_at: Optional[str] = None
    export_completed_at: Optional[str] = None
    selected_video_encoder: Optional[str] = None
    encoder_mode_requested: Optional[str] = None
    output_mp4_path: Optional[str] = None
    output_mp4_exists: bool = False
    output_mp4_size_bytes: int = 0
    ffmpeg_command_summary: Optional[str] = None
    
    # Original Data
    settings: RenderSettings
    plan: RenderPlan
