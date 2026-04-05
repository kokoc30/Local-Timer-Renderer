import os
import json
from datetime import datetime
from app.models.render_job import RenderJob, JobStatus
from app.services.draw_service import draw_frame
from app.services.encoder_selection_service import encoder_selection_service
from app.services.ffmpeg_export_service import execute_ffmpeg_export

def process_render_job_frames(job: RenderJob):
    """
    Synchronous worker loop that renders the PNG frame sequence for a given job.
    Updates the `job` object in place, which the main thread can inspect for status.
    """
    try:
        job.status = JobStatus.RUNNING
        job.updated_at = datetime.utcnow().isoformat()
        
        # Setup paths
        os.makedirs(job.frames_dir, exist_ok=True)
        
        # Unpack settings
        w = job.settings.width
        h = job.settings.height
        style = job.settings.style_preset
        format_str = job.settings.display_format
        fps = job.settings.fps
        fps = job.settings.fps

        total_display_seconds = job.plan.total_display_seconds
        total_frames = job.plan.total_frames
        
        job.total_frames = total_frames
        
        # Local formatter utility matching plan calculation
        from app.utils.time_utils import format_seconds
        
        # Render loop
        sample_paths = []
        is_optimized = getattr(job.plan, 'is_optimized', False)
        
        if is_optimized:
            # OPTIMIZED PATH: Render once per unique display second
            total_steps = job.plan.total_unique_states
            # Temporarily update job.total_frames so frontend progress bar fills correctly for the render phase
            job.total_frames = total_steps
            
            for i in range(total_steps):
                if job.status == JobStatus.CANCELLED:
                    break
                
                # Math: Display the integer second (e.g. 10, 9, 8...)
                display_val = total_display_seconds - i
                display_text = format_seconds(display_val, format_str)
                
                img = draw_frame(width=w, height=h, display_text=display_text, style=style)
                
                # Save frame sequentially for FFmpeg
                frame_filename = f"frame_{i+1:06d}.png"
                frame_path = os.path.join(job.frames_dir, frame_filename)
                img.save(frame_path, format="PNG")
                
                # Update progress
                job.progress_current_frame = i + 1
                job.progress_percent = round(((i + 1) / total_steps) * 100, 2)
                job.updated_at = datetime.utcnow().isoformat()
                
                # Samples
                if i == 0 or i == total_steps // 2 or i == total_steps - 1:
                    sample_paths.append(frame_path)
        else:
            # LEGACY PATH: Render every single frame
            for i in range(total_frames):
                if job.status == JobStatus.CANCELLED:
                    break
                    
                elapsed_seconds_in_timer = (i / fps)
                remaining = max(total_display_seconds - elapsed_seconds_in_timer, 0)
                
                import math
                display_val = math.ceil(remaining)
                display_text = format_seconds(display_val, format_str)
                
                img = draw_frame(width=w, height=h, display_text=display_text, style=style)
                
                frame_filename = f"frame_{i+1:06d}.png"
                frame_path = os.path.join(job.frames_dir, frame_filename)
                img.save(frame_path, format="PNG")
                
                job.progress_current_frame = i + 1
                job.progress_percent = round(((i + 1) / total_frames) * 100, 2)
                job.updated_at = datetime.utcnow().isoformat()
                
                if i == 0 or i == total_frames // 2 or i == total_frames - 1:
                    sample_paths.append(frame_path)
                
        if job.status != JobStatus.CANCELLED:
            job.status = JobStatus.ENCODING_VIDEO
            job.updated_at = datetime.utcnow().isoformat()
            
            # MP4 Assemble Step
            job.encoder_mode_requested = job.settings.encoder_preference
            try:
                selected_encoder = encoder_selection_service.select_encoder(job.settings.encoder_preference)
                job.selected_video_encoder = selected_encoder
                
                # Hand over to export service execution (blocking)
                execute_ffmpeg_export(job, selected_encoder)
                
                if job.output_mp4_exists:
                    job.status = JobStatus.COMPLETED
                else:
                    job.status = JobStatus.FAILED
                    
            except Exception as export_err:
                job.status = JobStatus.FAILED
                job.error_message = f"Encoding failed: {str(export_err)}"
                job.updated_at = datetime.utcnow().isoformat()
            job.sample_output_paths = sample_paths
            job.updated_at = datetime.utcnow().isoformat()
            
    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        job.updated_at = datetime.utcnow().isoformat()
        print(f"Job {job.job_id} failed: {e}")
        
    finally:
        # Write metadata.json
        write_job_metadata(job)

def write_job_metadata(job: RenderJob):
    """ Writes the final job state to metadata.json in the output dir. """
    try:
        metadata_path = os.path.join(job.output_dir, "metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(job.model_dump(), f, indent=2)
    except Exception as e:
        print(f"Failed to write metadata for job {job.job_id}: {e}")
