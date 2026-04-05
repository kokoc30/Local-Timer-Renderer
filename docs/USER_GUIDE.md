# User Guide

This guide will help you create high-quality countdown timer videos using the **Local Timer Renderer**.

## 🏗️ Basic Workflow

1. **Launch**: Run `.\start.ps1` from your terminal. This will automatically open the app in your default browser.
2. **Configure**: Use the sidebar to set your timer duration, visual style, and FPS (30 or 60).
3. **Plan & Validate**: Update any setting and observe the **Render Plan Summary**. It will confirm how long the final video will be and which visual states are generated.
4. **Preview**: Click anywhere in the preview area to see a live simulation. Use "Preview Playback Speed" to speed up long timers (this doesn't affect the final export).
5. **Start Render**: Click the **Start Frame Render** button.
6. **Download**: Once the job reaches 100%, you can watch the video directly in the browser or download it from the results page.

## ⚙️ Key Settings

### ✅ Timer Duration
Enter your countdown time in `MM:SS` or `HH:MM:SS` format.
- Max duration: **24:00:00** (24 hours).
- Min duration: **00:01** (1 second).

### ⏩ Preview Playback Speed
Use this to quickly check the visuals of a long timer (e.g., 60 minutes) without waiting 60 minutes.
- **Tip**: Set this to **50x** or **100x** for hour-long timers to verify they look correct before starting the render.
- **Note**: This setting **only affects the in-browser preview**, not the final MP4 duration.

### 🎨 Visual Styles
- **Minimal Digital**: Simple white text on a black background.
- **Watch Frame**: A subtle bezel ring around the timer for a refined, hardware-inspired look.
- **Bold Center**: (Future style placeholder) high-contrast large fonts.

### 🎥 Encoder Preference
- **Auto (Recommended)**: Use NVIDIA GPU if available; otherwise, fall back to CPU.
- **NVIDIA (NVENC)**: Force-use NVIDIA encoding (requires compatible hardware).
- **CPU (libx264)**: Force-use CPU encoding.

## 📁 Accessing Your Renders

All rendered videos are stored locally on your machine for permanent access.
- **Metadata**: Each job has its own folder in `app/outputs/jobs/{timestamp}_{random_id}/`.
- **Final Video**: Look for `final_render.mp4` within the job folder.
- **PNG Frames**: The unique frames generated during the render are stored in the `frames/` subfolder.

---

## 📜 Session History
The **Render History** panel (lower-left) persists across browser refreshes. You can click on any completed job to download it or re-examine its metadata at any time.
- To clear the history, simply restart the application server.
