from app.models.render_settings import RenderSettings
from app.models.render_plan import RenderPlan, FrameSample
from app.utils.time_utils import parse_time_string, format_seconds
import math

def calculate_render_plan(settings: RenderSettings) -> RenderPlan:
    """
    Computes the mathematical render plan for a given timer configuration.
    
    Planning Concept:
    - Display Duration: The internal timer value (e.g. 60:00 = 3600s).
    - Output Duration: How long the final MP4 will be (Display / Speed).
    - Total Frames: Output Duration * FPS.
    
    Frame Mapping:
    - For each frame `i`, the countdown value is:
      display_remaining = max(start_seconds - ((i / fps) * speed), 0)
    """
    
    # 1. Parse source duration
    try:
        total_display_seconds = parse_time_string(settings.start_time)
    except ValueError as e:
        # This shouldn't happen if validation passed, but we handle it just in case
        raise e
        
    # 2. Compute durations (1:1 fixed mapping)
    output_duration_seconds = float(total_display_seconds)
    
    # 3. Compute frame counts
    total_frames = math.ceil(output_duration_seconds * settings.fps)
    
    # Guard against zero-frame videos
    if total_frames <= 0:
        total_frames = 1
        
    # Helper to calculate samples for the plan
    def get_sample(idx: int) -> FrameSample:
        # Calculate how much 'timer time' has passed by this frame index (1:1)
        elapsed_seconds_in_timer = (idx / settings.fps)
        # Use ceil for countdown: 60.0 stays 60 until 59.9... which also stays 60 until it hits 59.0
        remaining = max(total_display_seconds - elapsed_seconds_in_timer, 0)
        
        display_val = math.ceil(remaining)
        return FrameSample(
            frame_index=idx,
            display_time=format_seconds(display_val, settings.display_format)
        )

    # 4. Generate summary info
    summary = (
        f"A {settings.start_time} countdown "
        f"will export as a {format_seconds(math.ceil(output_duration_seconds), settings.display_format)} "
        f"({settings.width}x{settings.height}, {settings.fps}fps) video. "
        f"(Optimized render path active: {total_display_seconds} unique states)"
    )
    
    mid_idx = total_frames // 2
    last_idx = max(0, total_frames - 1)
    
    return RenderPlan(
        total_display_seconds=total_display_seconds,
        output_duration_seconds=output_duration_seconds,
        total_frames=total_frames,
        fps=settings.fps,
        resolution=f"{settings.width}x{settings.height}",
        summary_text=summary,
        is_optimized=True, # Always optimized for these formats (Task 10)
        total_unique_states=total_display_seconds,
        first_frame=get_sample(0),
        mid_frame=get_sample(mid_idx),
        last_frame=get_sample(last_idx)
    )
