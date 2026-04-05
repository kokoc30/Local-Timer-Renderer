# API Reference Guide

The **Local Timer Renderer** is powered by a FastAPI backend. This document provides a concise summary of the core REST endpoints used for system status, planning, and rendering.

---

## 🛠️ System API

### `GET /api/system/status`
Retrieves the overall system readiness.
- **Used for**: Launcher diagnostics and browser health polling.
- **Response**: `{ "ok": true, "version": "1.0.0", "app_name": "Local Timer Renderer" }`.

---

## 📐 Planning API

### `POST /api/render/plan`
Generates a mathematical plan for a potential timer configurations.
- **Request Body**: `RenderSettings` (start\_time, width, height, fps, style\_preset, etc.).
- **Response**: `RenderPlan` details:
    - `total_display_seconds`: 3600 (for 60 minutes).
    - `total_frames`: 216000 (at 60fps).
    - `is_optimized`: `true` (if per-second optimization is active).
    - `total_unique_states`: 3600.
    - `summary_text`: Human-readable summary.

---

## 🚦 Render Job API

### `POST /api/render/jobs`
Creates and queues a new background render job.
- **Request Body**: `RenderSettings`.
- **Response**: `{ "job": RenderJob }`.

### `GET /api/render/jobs`
Lists all render jobs in the current session (sorted newest first).
- **Response**: `{ "jobs": [RenderJob, ...] }`.

### `GET /api/render/jobs/{job_id}`
Retrieves the current status and progress of a specific job.
- **Status Enum**: `queued`, `running`, `encoding_video`, `completed`, `failed`, `cancelled`.
- **Progress**: `progress_current_frame`, `progress_percent`, `job_id`.

### `GET /api/render/jobs/{job_id}/download`
Provides a file stream for the final `final_render.mp4` artifact.
- **Used for**: Downloading or playing the video directly in the browser via HTML5.

### `DELETE /api/render/jobs/{job_id}` (Future)
Cleanup of job artifacts.

---

## 🗃️ Models (Summary)

### `RenderSettings`
- `start_time`: `str` (e.g., "10:00")
- `fps`: `int` (30 or 60)
- `width`: `int` (default 1920)
- `height`: `int` (default 1080)
- `encoder_preference`: `str` ("auto", "nvidia", "cpu")

### `RenderJob`
- `job_id`: `str`
- `status`: `JobStatus`
- `progress_percent`: `float`
- `selected_video_encoder`: `str` (e.g., "h264_nvenc")
- `output_mp4_exists`: `bool`
