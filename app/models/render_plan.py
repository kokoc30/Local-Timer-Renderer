from pydantic import BaseModel
from typing import List

class FrameSample(BaseModel):
    """
    Metadata for a frame in the render plan.
    """
    frame_index: int
    display_time: str
    is_keyframe: bool = False

class RenderPlan(BaseModel):
    """
    Detailed render plan for a specific timer configuration.
    """
    total_display_seconds: int
    output_duration_seconds: float
    total_frames: int
    fps: int
    resolution: str
    summary_text: str
    
    # Optimization metadata (Task 10)
    is_optimized: bool = False
    total_unique_states: int = 0
    
    # Samples for UI verification
    first_frame: FrameSample
    mid_frame: FrameSample
    last_frame: FrameSample
