# Local Timer Renderer - Product Requirements, Architecture, and Task Execution Plan

## 1. Project Summary

Build a **local desktop-style web app** that generates high-quality countdown timer videos **without real-time recording**. The app should let the user create timer videos such as **1 hour**, **2 hours**, or custom durations, choose a visual style, choose export settings, and render directly to **MP4** using **FFmpeg** with optional **NVIDIA NVENC GPU acceleration**.

The product should solve the main problems seen in browser-based timer websites:

- real-time or semi-real-time recording limitations
- forced `.webm` outputs instead of `.mp4`
- weak control over duration handling
- low max speed multipliers
- unreliable zero-length exports
- limited rendering/export control

This app should compute the timer frames programmatically, then render/export them locally. That means a **1-hour countdown should not require waiting 1 real hour**.

---

## 2. Primary Goal

Create a local tool that can:

1. Generate countdown timer videos from a user-defined start time.
2. Render faster than real time using frame-based generation.
3. Export directly to **MP4**.
4. Use **GPU encoding when available** for faster export.
5. Support high speed multipliers such as **10x, 20x, 50x, 100x**.
6. Provide clean visual styles and black-background rendering.
7. Run locally on Windows in a simple browser-based UI.

---

## 3. Recommended Product Direction

### Recommended stack

**Frontend**
- HTML
- CSS
- JavaScript

**Backend**
- Python
- FastAPI

**Rendering / Export**
- HTML5 Canvas for preview rendering
- FFmpeg for final video encoding
- `h264_nvenc` when NVIDIA GPU encoding is available
- CPU fallback when NVENC is unavailable

### Why this stack

This stack gives:
- easy local setup
- a simple clean interface
- strong backend control for rendering jobs
- direct MP4 export
- GPU/CPU encoder selection
- room for future presets and advanced features

---

## 4. Product Scope

### In scope for MVP

- Countdown timer generation
- Black background output
- White timer text by default
- Output resolution presets (1080p minimum)
- FPS options (30, 60)
- Start time input
- Export duration handling
- Speed multiplier selection
- MP4 export
- GPU encoding if available
- Local render progress
- Download/open output file
- Canvas preview in browser

### Out of scope for MVP

- full video editing timeline
- drag-and-drop compositing system
- multiple layered timer tracks
- audio/music editing
- cloud rendering
- account system
- online hosting

### Post-MVP ideas

- transparent background MOV/WebM export
- count-up mode
- circular progress indicators
- watch-frame themes
- flash/end cues
- segment markers
- batch exports
- subtitle overlays
- preset templates
- image/logo watermark
- social export presets (TikTok, YouTube, Shorts)

---

## 5. Core Product Behavior

### 5.1 User flow

1. User opens local app.
2. User chooses timer mode and settings.
3. User previews timer visually.
4. User chooses speed multiplier.
5. User chooses export settings.
6. User clicks **Render MP4**.
7. Backend generates the timer frames mathematically.
8. Backend encodes frames using FFmpeg.
9. If NVIDIA encoder is available, use GPU path.
10. User sees progress and gets final MP4 path/download.

### 5.2 Key principle

The app must **not rely on screen recording**.

Instead, it must:
- calculate the timer value for each frame
- render each frame deterministically
- assemble/export the video

This is the reason it can be much faster than real time.

---

## 6. Functional Requirements

## 6.1 Timer Inputs

The app must support:
- countdown start input in `HH:MM:SS` and/or `MM:SS`
- optional preset buttons:
  - 00:30
  - 01:00
  - 05:00
  - 10:00
  - 30:00
  - 60:00
- stop at `00:00`
- optional end behavior:
  - hard stop at zero
  - hold last frame for N seconds

### Validation rules
- no negative durations
- at least 1 second total duration
- format must be parsed safely
- if input is `MM:SS`, interpret correctly
- if input is `HH:MM:SS`, support 1+ hour durations

---

## 6.2 Speed Controls

The app must support export-time speed multipliers:
- 1x
- 2x
- 4x
- 10x
- 20x
- 50x
- 100x
- custom value input

### Meaning of speed

This multiplier defines how much faster the timer is rendered relative to real-time playback.

Examples:
- 1-hour timer at 1x = 1-hour output video
- 1-hour timer at 10x = 6-minute output video
- 1-hour timer at 100x = 36-second output video

### Required behavior
The UI must clearly show:
- source timer duration
- chosen speed multiplier
- expected output video duration

Formula:

`output_duration_seconds = source_duration_seconds / speed_multiplier`

---

## 6.3 Visual Style Controls

MVP should support:
- black background
- white timer text
- center alignment
- font family selection
- font weight selection
- font size scaling
- style preset selection

Suggested initial presets:
- Minimal Digital
- Watch Frame
- Bold Center
- Thin Modern

Optional later:
- glow
- stroke
- shadow
- flash on final seconds
- color themes

---

## 6.4 Format Controls

Support display format options:
- `MM:SS`
- `HH:MM:SS`
- `M:SS`
- `H:MM:SS`

Behavior rules:
- if total duration is >= 1 hour and user selects compact mode, still display correctly
- prevent format mismatch issues
- preview and render must match exactly

---

## 6.5 Output Settings

MVP output options:
- MP4
- 1920x1080
- optional 1280x720
- FPS 30 or 60
- output file name
- output folder selection or default exports folder

Later:
- 4K
- alpha background export
- MOV / ProRes / WebM

---

## 6.6 Preview

The frontend preview must:
- render current timer style on canvas
- reflect real chosen settings
- support short live preview simulation
- let the user confirm appearance before rendering

Preview does **not** need to render the full final export in real time.
It just needs to accurately show style/layout/timing behavior.

---

## 6.7 Render System

The backend render system must:
- accept a render job config from the frontend
- validate config
- compute target frame count
- generate frames based on timer math
- encode video with FFmpeg
- show progress to frontend
- store final MP4 in output directory

---

## 6.8 Encoder Selection

The backend must:
- detect whether FFmpeg is installed
- detect whether `h264_nvenc` is available
- prefer GPU encoder when available
- fall back to CPU encoder if not

### Priority
1. `h264_nvenc`
2. CPU fallback (`libx264`)

### User-facing behavior
Show encoder status such as:
- GPU encoder available
- CPU fallback active
- FFmpeg missing

---

## 7. Non-Functional Requirements

### Performance
- Must avoid real-time screen recording architecture
- Must be able to export faster than real time
- Must remain responsive during render

### Reliability
- No zero-length outputs
- No incorrect duration mismatch
- No hidden settings altering timer behavior unexpectedly

### Usability
- UI should be clean and simple
- defaults should work for common use cases
- timer preview should match export

### Local-first
- no internet required
- no accounts required
- fully local generation

---

## 8. Technical Architecture

## 8.1 High-level architecture

### Frontend
Responsible for:
- form inputs
- style controls
- preview canvas
- render submission
- progress display
- final download link / file path

### Backend
Responsible for:
- settings validation
- duration calculations
- frame generation orchestration
- FFmpeg invocation
- encoder detection
- export handling

### FFmpeg layer
Responsible for:
- encoding image sequence or raw pipe input to MP4
- using NVENC if available
- using CPU fallback if needed

---

## 8.2 Recommended rendering strategy

### Preferred MVP strategy
Use **Python + PIL/Pillow frame rendering** for final export.

Flow:
1. Backend calculates each frame timestamp.
2. Backend renders timer text into each frame.
3. Backend writes frames to a temp directory or pipes them directly.
4. FFmpeg encodes frames into MP4.

### Why this is preferred for MVP
- simpler and more controllable than trying to export browser canvas directly
- deterministic rendering
- easier validation
- easier to align preview/output logic

### Frontend preview strategy
Use browser canvas for preview only.

---

## 8.3 Timing math

Let:
- `source_duration_seconds` = countdown start total seconds
- `speed_multiplier` = chosen render speed
- `fps` = target frame rate
- `output_duration_seconds` = `source_duration_seconds / speed_multiplier`
- `total_frames` = `ceil(output_duration_seconds * fps)`

For each frame index `i`:
- `video_time = i / fps`
- `source_elapsed = video_time * speed_multiplier`
- `remaining = max(source_duration_seconds - source_elapsed, 0)`

Display timer based on `remaining`.

This is the core logic that lets the app render a long timer into a shorter video.

---

## 8.4 File structure recommendation

```text
local-timer-renderer/
  README.md
  requirements.txt
  .gitignore
  app/
    main.py
    api/
      routes_render.py
      routes_system.py
    core/
      config.py
      models.py
      validation.py
      encoder_detection.py
      time_math.py
      render_service.py
      ffmpeg_service.py
      preview_service.py
    renderers/
      timer_frame_renderer.py
      style_presets.py
      text_layout.py
    static/
      index.html
      styles.css
      app.js
    temp/
    outputs/
  docs/
    BUILD_PLAN.md
    TASKS.md
```

---

## 9. API Design (Suggested)

## 9.1 System endpoints

### `GET /api/system/status`
Returns:
- ffmpeg installed or not
- NVENC available or not
- default output folder
- app version

### `POST /api/render/preview-metadata`
Returns computed metadata for UI:
- parsed source duration
- output duration
- total frames
- encoder choice estimate

### `POST /api/render/start`
Starts a render job with config.

### `GET /api/render/{job_id}`
Returns render progress and status.

### `GET /api/render/{job_id}/result`
Returns final output file metadata.

MVP can keep this simple and even start with synchronous rendering before background jobs if needed.

---

## 10. UX Requirements

## 10.1 Main form fields

- Timer mode: Countdown
- Start time
- Display format
- Speed multiplier
- Resolution
- FPS
- Style preset
- Font family
- Font weight
- Background color
- Text color
- Output file name
- Encoder preference (Auto / GPU / CPU)

---

## 10.2 Main actions

- Preview
- Calculate output duration
- Render MP4
- Open output folder
- Reset to defaults

---

## 10.3 UX safety requirements

Before rendering, the UI must clearly show:
- start time
- speed multiplier
- expected final video length
- target resolution
- target fps
- encoder selected

This avoids confusion like “I expected 1 hour but got 36 seconds.”

---

## 11. Default MVP Settings

Recommended defaults:

- Mode: Countdown
- Start time: `60:00`
- Format: `MM:SS`
- Speed: `10x`
- Resolution: `1920x1080`
- FPS: `60`
- Background: `#000000`
- Text color: `#FFFFFF`
- Font: system sans / Arial / Inter equivalent
- Weight: `700`
- Style: Minimal Digital
- Encoder: Auto
- Output: MP4

---

## 12. Risks and Edge Cases

### Edge cases
- start time is invalid
- start time is zero
- speed multiplier is zero or negative
- output duration becomes less than one frame
- FFmpeg missing
- NVENC unavailable
- font unavailable on system
- timer format overflow
- preview differs from export

### Required handling
- explicit validation errors
- clear UI messages
- fallback behavior when GPU unavailable
- no silent incorrect outputs

---

## 13. MVP Acceptance Criteria

The MVP is complete when all are true:

1. User can enter a countdown start time.
2. User can choose 10x, 20x, 50x, or 100x.
3. App calculates final output duration correctly.
4. App previews the timer style in browser.
5. App renders a valid MP4 locally.
6. App uses `h264_nvenc` when available, otherwise falls back to CPU.
7. A 1-hour timer can be exported as a shorter video without real-time recording.
8. Output file has the expected duration and visible countdown.
9. App runs locally from VS Code with simple setup.

---

## 14. Implementation Plan

## Task 1 - Project Scaffold and Local App Boot

### Goal
Set up the project structure, FastAPI backend, and static frontend.

### Deliverables
- project folder structure
- FastAPI app booting locally
- static `index.html`, `styles.css`, `app.js`
- health/status route
- README with setup commands

### Acceptance
- backend starts successfully
- frontend loads in browser
- `/api/system/status` returns JSON

### Prompt for Task 1

```text
Analyze the entire project before making changes. Then implement only Task 1 from the BUILD_PLAN.md.

Task 1 scope only:
- Create the recommended project structure.
- Set up a FastAPI backend in app/main.py.
- Serve a static frontend from app/static.
- Add a basic GET /api/system/status endpoint.
- Build a clean minimal frontend shell with sections for timer settings, preview, render status, and output.
- Add a README with exact local setup and run instructions for Windows PowerShell.

Requirements:
- Do not implement rendering yet.
- Do not add placeholder complexity.
- Keep code clean, modular, and production-minded.
- Use clear naming and minimal dependencies.
- After implementation, summarize what was added, what files changed, and how to run it.
```

---

## Task 2 - Settings Model, Validation, and Duration Math

### Goal
Implement input parsing, config validation, and output-duration calculation.

### Deliverables
- request/response models
- time parsing utilities
- validation rules
- output duration calculator
- metadata preview endpoint

### Acceptance
- start time parses correctly
- speed multiplier changes output duration correctly
- invalid inputs return clear errors

### Prompt for Task 2

```text
Analyze the existing codebase first. Then implement only Task 2 from the BUILD_PLAN.md.

Task 2 scope only:
- Add data models for timer configuration.
- Implement robust time parsing for MM:SS and HH:MM:SS.
- Add validation for duration, fps, speed multiplier, and resolution.
- Add backend time math that computes source duration, output duration, and total frames.
- Add POST /api/render/preview-metadata to return computed metadata.
- Update the frontend form so the user can calculate and view output duration before rendering.

Requirements:
- Keep logic modular in core/validation.py and core/time_math.py.
- Return clean JSON validation errors.
- Do not implement final video rendering yet.
- After implementation, show example valid/invalid cases.
```

---

## Task 3 - Frontend Preview Canvas

### Goal
Build a real preview canvas that reflects current settings.

### Deliverables
- browser canvas preview
- style preset switching
- color/font controls reflected in preview
- simulated playback preview button

### Acceptance
- preview visibly matches selected style
- timer text updates correctly
- preview respects chosen format and styling

### Prompt for Task 3

```text
Analyze the current project state first. Then implement only Task 3 from the BUILD_PLAN.md.

Task 3 scope only:
- Build a canvas-based preview area in the frontend.
- Add style presets: Minimal Digital, Watch Frame, Bold Center, Thin Modern.
- Wire preview rendering to the current form values.
- Add a short simulated preview play button so the timer visibly counts down in-browser.
- Keep preview logic frontend-only and separate from export logic.

Requirements:
- Do not implement backend frame rendering yet.
- Preview should be visually clean and centered.
- Ensure preview and backend format assumptions stay aligned.
- Summarize all new UI behavior after implementation.
```

---

## Task 4 - FFmpeg Detection and Encoder Detection

### Goal
Detect FFmpeg and available encoders, especially NVENC.

### Deliverables
- FFmpeg presence check
- encoder detection utility
- system status reporting in frontend

### Acceptance
- app can report whether `h264_nvenc` is available
- frontend shows Auto/GPU/CPU availability clearly

### Prompt for Task 4

```text
Analyze the current codebase first. Then implement only Task 4 from the BUILD_PLAN.md.

Task 4 scope only:
- Add FFmpeg detection logic.
- Add encoder detection logic for h264_nvenc with clean fallback behavior.
- Expand GET /api/system/status to report FFmpeg and encoder availability.
- Show the detected status clearly in the frontend.
- Add an encoder preference control: Auto, GPU, CPU.

Requirements:
- Do not implement full export yet.
- Handle missing FFmpeg gracefully.
- Avoid OS-specific hardcoding where possible, but make sure Windows works well.
- Provide a short note in the README on FFmpeg installation expectations.
```

---

## Task 5 - Backend Frame Renderer

### Goal
Create the actual backend frame renderer for countdown images.

### Deliverables
- deterministic frame generation
- timer text rendered with chosen style
- temp frame output system

### Acceptance
- backend can generate a valid sequence of frames for a timer config
- remaining time is correct frame-by-frame

### Prompt for Task 5

```text
Analyze the entire current project first. Then implement only Task 5 from the BUILD_PLAN.md.

Task 5 scope only:
- Build a backend frame renderer using Python.
- Use Pillow/PIL to generate countdown frames.
- Implement frame-by-frame timer value calculation from source duration, speed multiplier, and fps.
- Support at least the MVP style presets in export rendering.
- Save frames into a temporary render directory per job.

Requirements:
- Do not encode to video yet.
- Keep rendering deterministic and modular.
- Ensure text layout is centered and visually consistent.
- Add enough internal logging to debug rendering issues.
```

---

## Task 6 - FFmpeg MP4 Export Pipeline

### Goal
Encode generated frames into MP4 using FFmpeg.

### Deliverables
- MP4 export pipeline
- GPU/CPU encoder choice
- output directory handling

### Acceptance
- valid MP4 output is created
- duration is correct
- encoder selection works as expected

### Prompt for Task 6

```text
Analyze the project carefully first. Then implement only Task 6 from the BUILD_PLAN.md.

Task 6 scope only:
- Add an FFmpeg service to encode generated frames into MP4.
- Support encoder preference: Auto, GPU, CPU.
- Use h264_nvenc when available and appropriate.
- Fall back cleanly to libx264 if GPU encoding is unavailable.
- Save the final MP4 into the outputs directory with a user-defined or generated filename.

Requirements:
- Keep FFmpeg command construction centralized in one service file.
- Add clear error messages for FFmpeg failures.
- Do not implement background job polling yet unless needed for code cleanliness.
- After implementation, document the exact FFmpeg command patterns being used.
```

---

## Task 7 - Render Job Flow and Frontend Integration

### Goal
Connect the frontend form to the backend render pipeline.

### Deliverables
- render button
- render status/progress UI
- final result link/path

### Acceptance
- user can render from the UI end-to-end
- status updates are visible
- result is accessible

### Prompt for Task 7

```text
Analyze the current project state first. Then implement only Task 7 from the BUILD_PLAN.md.

Task 7 scope only:
- Connect the frontend form to the backend render pipeline.
- Add a Render MP4 button.
- Add render status and progress reporting.
- Display the final output path and success/failure message in the UI.
- Keep the UX clean and explicit.

Requirements:
- Make the flow reliable for longer renders.
- Do not over-engineer job queues unless necessary.
- Handle frontend and backend errors clearly.
- Summarize the full end-to-end user flow after implementation.
```

---

## Task 8 - QA, Edge Cases, and README Finalization

### Goal
Stabilize the app for real use.

### Deliverables
- validation cleanup
- edge-case fixes
- final README
- run/test checklist

### Acceptance
- common invalid cases are handled cleanly
- README is complete
- app is usable by a non-developer following steps

### Prompt for Task 8

```text
Analyze the full project first. Then implement only Task 8 from the BUILD_PLAN.md.

Task 8 scope only:
- Review the full app for edge cases and reliability issues.
- Fix invalid input handling, duration mismatches, preview/export mismatches, and encoder fallback issues.
- Finalize the README with exact setup, run, FFmpeg, and troubleshooting steps.
- Add a short manual QA checklist covering 1-minute, 5-minute, and 1-hour countdown exports at multiple speed multipliers.

Requirements:
- Do not add unrelated features.
- Keep the app focused and stable.
- Clearly document any known limitations that remain.
```

---

## 15. Suggested Build Order for You

Use the prompts in this order:

1. Task 1
2. Task 2
3. Task 3
4. Task 4
5. Task 5
6. Task 6
7. Task 7
8. Task 8

Do not ask the coding agent to do all tasks at once.
Keep it strictly task-by-task.

---

## 16. Recommended Initial Test Cases

### Test 1
- Start time: `01:00`
- Speed: `1x`
- FPS: `30`
- Expected output: ~60 seconds

### Test 2
- Start time: `60:00`
- Speed: `10x`
- FPS: `60`
- Expected output: ~360 seconds

### Test 3
- Start time: `60:00`
- Speed: `100x`
- FPS: `60`
- Expected output: ~36 seconds

### Test 4
- Start time: `02:00:00`
- Speed: `50x`
- Expected output: ~144 seconds

---

## 17. Final Recommendation

Build the app as a **local web UI + Python backend + FFmpeg export pipeline**.
That is the best balance of:
- speed
- control
- local simplicity
- clean MP4 export
- future extensibility

Do not build this as a browser-only recording tool.
Do not build this as a real-time recorder.
The correct architecture is **frame-based generation + local encoding**.

