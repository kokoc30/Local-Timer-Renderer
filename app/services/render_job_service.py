import os
import uuid
import threading
from datetime import datetime
from typing import Dict, Optional

from app.core import config
from app.models.render_settings import RenderSettings
from app.models.render_plan import RenderPlan
from app.models.render_job import RenderJob, JobStatus
from app.services.frame_render_service import process_render_job_frames

class RenderJobService:
    def __init__(self):
        # In-memory store of jobs.
        # In a real app, this would be a DB or Redis cache.
        self._jobs: Dict[str, RenderJob] = {}
        
    def create_job(self, settings: RenderSettings, plan: RenderPlan) -> RenderJob:
        """
        Creates a new queued RenderJob and initializes output directories.
        """
        # Generate unique ID
        job_id = f"job_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Setup paths
        output_dir = os.path.join(config.OUTPUT_DIR, "jobs", job_id)
        frames_dir = os.path.join(output_dir, "frames")
        
        # We don't create the dirs here, the worker thread will do it 
        # (or we could do it here to return paths immediately)
        
        now_str = datetime.utcnow().isoformat()
        job = RenderJob(
            job_id=job_id,
            status=JobStatus.QUEUED,
            created_at=now_str,
            updated_at=now_str,
            output_dir=output_dir,
            frames_dir=frames_dir,
            settings=settings,
            plan=plan
        )
        
        self._jobs[job_id] = job
        return job

    def start_job(self, job_id: str):
        """
        Spawns a background thread to process the job.
        """
        job = self.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found.")
            
        thread = threading.Thread(target=process_render_job_frames, args=(job,), daemon=True)
        thread.start()

    def get_job(self, job_id: str) -> Optional[RenderJob]:
        """ Retrieves the job state. """
        return self._jobs.get(job_id)

    def get_all_jobs(self) -> list[RenderJob]:
        """ Retrieves a list of all jobs, sorted newest first. """
        jobs = list(self._jobs.values())
        return sorted(jobs, key=lambda j: j.created_at, reverse=True)

    def cancel_job(self, job_id: str) -> bool:
        """ Attempts to mark a job as cancelled. """
        job = self.get_job(job_id)
        if job and job.status in [JobStatus.QUEUED, JobStatus.RUNNING]:
            job.status = JobStatus.CANCELLED
            return True
        return False

# Singleton instance
render_job_service = RenderJobService()
