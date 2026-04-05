import os
import subprocess
from datetime import datetime
from app.models.render_job import RenderJob
from app.services.ffmpeg_detection_service import ffmpeg_detection_service

def execute_ffmpeg_export(job: RenderJob, selected_encoder: str) -> None:
    """Executes the FFmpeg export process for a render job."""
    ffmpeg_path = ffmpeg_detection_service.find_ffmpeg()
    if not ffmpeg_path:
        job.error_message = "FFmpeg executable not found."
        job.output_mp4_exists = False
        return
        
    job.export_started_at = datetime.utcnow().isoformat() + "Z"
    
    fps = job.settings.fps
    input_pattern = os.path.join(job.frames_dir, "frame_%06d.png")
    output_mp4 = os.path.join(job.output_dir, "final_render.mp4")
    
    # Optimization mode check (Task 10)
    is_optimized = getattr(job.plan, 'is_optimized', False)
    input_fps = "1" if is_optimized else str(fps)
    
    # Standard high quality flags for browser playback compatibility
    cmd = [
        ffmpeg_path,
        "-y", # overwrite
        "-framerate", input_fps,
        "-i", input_pattern,
    ]
    
    # If optimized, we must force the output framerate to the target FPS
    # so FFmpeg duplicates the 1fps input frames correctly.
    if is_optimized:
        cmd.extend(["-r", str(fps)])
        
    cmd.extend([
        "-c:v", selected_encoder,
        "-pix_fmt", "yuv420p"
    ])
    
    if selected_encoder == "libx264":
        cmd.extend(["-preset", "fast", "-crf", "23"])
    elif selected_encoder == "h264_nvenc":
        cmd.extend(["-preset", "p4"]) # A balanced NVENC preset
        
    cmd.append(output_mp4)
    
    job.ffmpeg_command_summary = " ".join(cmd)
    job.output_mp4_path = output_mp4
    
    try:
        # Run ffmpeg synchronously on the thread
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        
        job.export_completed_at = datetime.utcnow().isoformat() + "Z"
        
        if os.path.exists(output_mp4):
            job.output_mp4_exists = True
            job.output_mp4_size_bytes = os.path.getsize(output_mp4)
        else:
            job.error_message = "FFmpeg completed without error, but output MP4 is missing."
            job.output_mp4_exists = False
            
    except subprocess.CalledProcessError as e:
        stderr_last = e.stderr.strip().split('\n')[-5:] if e.stderr else ["No stderr output"]
        job.error_message = f"FFmpeg failed (code {e.returncode}). Error: {' '.join(stderr_last)}"
        print(f"FFmpeg Error for job {job.job_id}: {e.stderr}")
        job.output_mp4_exists = False
        
    except Exception as e:
        job.error_message = f"Exception during FFmpeg execution: {str(e)}"
        job.output_mp4_exists = False
