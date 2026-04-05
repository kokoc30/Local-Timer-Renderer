import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import Dict, Any

from app.models.render_settings import RenderSettings
from app.services.planning_service import calculate_render_plan
from app.services.render_job_service import render_job_service

router = APIRouter(prefix="/api/render/jobs", tags=["render-jobs"])

@router.post("")
async def create_render_job(settings: RenderSettings):
    """
    Validates settings, generates a plan, and queues a frame render job.
    """
    try:
        # Re-use exact same planning logic
        plan = calculate_render_plan(settings)
        
        # Create and queue the job
        job = render_job_service.create_job(settings, plan)
        
        # Start immediately in background
        render_job_service.start_job(job.job_id)
        
        return {
            "ok": True,
            "job": job.model_dump()
        }
        
    except ValueError as e:
        # Clear validation errors from Pydantic or custom logic
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Unexpected errors
        print(f"ERROR starting job: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: Could not start render job. {str(e)}")

@router.get("")
async def list_jobs():
    """
    Returns all recent jobs in the current session.
    """
    jobs = render_job_service.get_all_jobs()
    return {
        "ok": True,
        "jobs": [j.model_dump() for j in jobs]
    }

@router.get("/{job_id}")
async def get_job_status(job_id: str):
    """
    Returns the current status and progress of a render job.
    """
    job = render_job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")
        
    return {
        "ok": True,
        "job": job.model_dump()
    }

@router.get("/{job_id}/files")
async def get_job_files(job_id: str):
    """
    Returns a listing of relevant files outputted by the job.
    Note: Paths are relative or symbolic depending on static serving config.
    """
    job = render_job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")

    # Convert absolute filesystem paths to API/Static relative paths if needed,
    # but for Task 5, we can just return the absolute paths for inspection or 
    # we can try to make them relative to app/outputs if requested.
    # We will just return the paths recorded in the job object.
    
    return {
        "ok": True,
        "job_id": job.job_id,
        "frames_dir": job.frames_dir,
        "frame_count": max(0, job.progress_current_frame),
        "sample_frames": job.sample_output_paths,
        "metadata_file": os.path.join(job.output_dir, "metadata.json"),
        "mp4_path": job.output_mp4_path if job.output_mp4_exists else None,
        "mp4_size_bytes": job.output_mp4_size_bytes
    }

@router.get("/{job_id}/download")
async def download_mp4(job_id: str):
    job = render_job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found.")
        
    if not job.output_mp4_exists or not job.output_mp4_path:
        raise HTTPException(status_code=404, detail="MP4 file not ready or does not exist.")
        
    if not os.path.exists(job.output_mp4_path):
        raise HTTPException(status_code=404, detail="MP4 file not found on disk.")
        
    filename = f"timer_{job.job_id}.mp4"
    return FileResponse(
        path=job.output_mp4_path,
        media_type="video/mp4",
        filename=filename,
        content_disposition_type="inline" # Allow inline playback if accessing directly
    )
