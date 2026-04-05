# Troubleshooting Guide

This guide provides solutions to common issues you may encounter when setting up or using the **Local Timer Renderer**.

## 🛑 Startup Issues

### 1. Port Already in Use (Port Conflict)
- **Problem**: The app fails to start because port 8001 (or another port) is occupied.
- **Solution**:
    - **Automatic**: The standard launcher (`.\start.ps1`) automatically scans for the next available port. Simply run it without parameters to allow this scan.
    - **Manual**: If you need a specific port, use the `-Port` parameter:
        `.\start.ps1 -Port 8010`
    - **Check Existing Instance**: If the app is already running, the launcher will detect it and simply open the browser at the existing URL.

### 2. FFmpeg Not Found
- **Problem**: The system status shows "FFmpeg Not Found" or the export fails immediately.
- **Solution**:
    - **Install FFmpeg**: Ensure you have a functioning FFmpeg build. [Download here](https://ffmpeg.org/download.html).
    - **Check PATH**: Open your terminal (Cmd or PowerShell) and type `ffmpeg -version`. If this fails, add your FFmpeg `bin` folder to the matching **Environmental Variables (PATH)** in Windows.

---

## 🎥 Rendering & Encoding Issues

### 1. NVIDIA NVENC Error
- **Problem**: You selected "NVIDIA" as the encoder, but the render fails with an encoding error.
- **Solution**:
    - **HW Support**: Ensure you have an NVIDIA GPU (GeForce GTX 600 series or newer).
    - **Drivers**: Update your NVIDIA drivers to the latest Game Ready or Studio Driver.
    - **Fallback**: Set **Encoder Preference** to **Auto** (recommended). The system will automatically fall back to CPU encoding if your GPU is not detected or supported by your current FFmpeg build.

### 2. "App is Disconnected" Message
- **Problem**: The UI shows "Disconnected" in the top-right and the "Start Render" button is disabled.
- **Solution**:
    - **Refresh**: Try refreshing the browser page (`F5`).
    - **Restart Server**: Check your terminal. If the PowerShell script has stopped, run `.\start.ps1` again.
    - **Verify URL**: Ensure the browser URL matches the port listed in the terminal output.

### 3. Slow Export Speed
- **Problem**: The export seems much slower for high-FPS videos (e.g., 60fps).
- **Solution**:
    - **Optimization**: Long timers (multi-minute) use a **Per-Second Rendering Path**. This is extremely fast. If you notice a slowdown, it may be due to complex styles or high resolution (4K).
    - **Background Tasks**: Ensure your CPU is not being throttled by other intensive background processes during the export phase.

---

## 🏗️ Virtual Environment Issues
- **Problem**: Red text about "pip not found" or "python not found".
- **Solution**:
    - **Re-setup**: Delete the `.venv` folder and run `.\start.ps1` again. It will rebuild the environment and reinstall `requirements.txt` from scratch.
