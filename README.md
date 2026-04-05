# Local Timer Renderer ⏳

This is a simple project I made to help generate countdown timer videos directly on your own computer. Instead of recording your screen while a timer runs, this app draws each frame and saves it as a high-quality video file.

It is designed to be easy to use on Windows with a single startup script.

## What it does
- You enter how long you want the timer to be (like 01:00:00 for one hour).
- You can see a live preview of how the timer will look.
- It builds the video in the background and lets you download it as an MP4 when it is finished.
- It uses a special "optimized" mode for long timers so it doesn't have to draw every single frame if the text only changes every second.

## Main Features
- **Easy Startup**: Just one command to get everything running.
- **Smart Port Scanning**: If port 8001 is busy, it automatically tries to find another open port.
- **Live Preview**: You can play the timer in your browser first to make sure the style looks right.
- **Auto-Encoder**: It tries to use your graphics card (NVIDIA) for faster video making, but it will switch to your CPU if you don't have one.
- **Job History**: It keeps a list of your recent renders so you can find them later.

## Tools and Tech
- **Python (FastAPI)**: This runs the backend server and handles the math.
- **Vanilla JavaScript & HTML**: The frontend UI where you enter your settings.
- **Pillow**: A Python library used to draw the actual text onto each video frame.
- **FFmpeg**: The engine that takes all the individual frames and turns them into a video file.

## How to Install
1. **Clone the project**:
   ```powershell
   git clone https://github.com/kokoc30/Local-Timer-Renderer.git
   cd Local-Timer-Renderer
   ```

2. **Set up your environment**:
   You should use a virtual environment so you don't mess up your global Python install.
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

3. **Check FFmpeg**:
   Make sure you have FFmpeg installed on your computer and added to your PATH. If you type `ffmpeg -version` in your terminal and see text, you are good to go.

## How to Run
On Windows, you can just run the launcher script:
```powershell
.\start.ps1
```
This script will:
- Check your Python environment.
- Start the backend server.
- Find an available port.
- Open your web browser automatically to the right page.

## How the App Works
When you click "Start Frame Render", the app follows these steps:
1. **Planning**: It calculates exactly how many frames are needed based on your time and FPS.
2. **Drawing**: It uses the "Draw Service" to create PNG images for the timer states.
3. **Encoding**: It calls FFmpeg to stitch those images together into an MP4 video.
4. **Saving**: The final video and some metadata are saved into a folder in `app/outputs/jobs/`.

## Project Structure
- `app/api/`: Contains the code for all the website routes (like /status or /jobs).
- `app/services/`: This is where the heavy work happens, like drawing frames and running FFmpeg.
- `app/static/`: This has the HTML, CSS, and JS files that show up in your browser.
- `app/outputs/`: This is where your finished videos will be stored.
- `docs/`: Extra notes and guides on how the parts fit together.

## Notes & Troubleshooting
- **Port Busy**: If the app says a port is busy, just let it scan for the next one, or close whatever else is running on that port.
- **NVIDIA vs CPU**: If your video export is slow, check if your graphics card is being used. If not, the app will still work, it just uses more CPU power.
- **Execution Policy**: If Windows blocks the `.ps1` script, you might need to run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in your terminal first.

For more technical details, you can look at the files in the [docs/](docs/) folder.

## Author
Made by Koko Jamgotchian
