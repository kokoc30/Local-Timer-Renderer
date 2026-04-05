import os
import shutil
import re
from typing import List, Dict, Optional
from app.utils.process_utils import run_command
from app.models.system_capabilities import FFmpegInfo

class FFmpegDetectionService:
    """Service to detect FFmpeg and its capabilities on the local machine."""

    def find_ffmpeg(self) -> Optional[str]:
        """
        Locates the FFmpeg executable.
        Priority:
        1. FFMPEG_BINARY environment variable
        2. PATH
        """
        # 1. Environment variable
        env_path = os.environ.get("FFMPEG_BINARY")
        if env_path and os.path.isfile(env_path):
            return env_path
        
        # 2. PATH
        path_cmd = shutil.which("ffmpeg")
        if path_cmd:
            return path_cmd
            
        return None

    def get_info(self) -> FFmpegInfo:
        """Runs diagnostics and returns structured info."""
        path = self.find_ffmpeg()
        if not path:
            return FFmpegInfo(
                installed=False,
                callable=False,
                error="FFmpeg was not found on PATH or via FFMPEG_BINARY."
            )
            
        # Try running -version
        success, stdout, stderr = run_command([path, "-version"])
        if not success:
            return FFmpegInfo(
                installed=True,
                callable=False,
                path=path,
                error=stderr or "FFmpeg was found but failed to run -version."
            )
            
        # Parse version (usually the first line)
        version_line = stdout.split('\n')[0] if stdout else "Unknown"
        
        return FFmpegInfo(
            installed=True,
            callable=True,
            path=path,
            version=version_line
        )

    def get_encoders(self, ffmpeg_path: str) -> Dict[str, bool]:
        """Detects available video encoders."""
        success, stdout, stderr = run_command([ffmpeg_path, "-encoders"])
        if not success:
            return {}
            
        # Typical encoders we care about
        targets = [
            "libx264", "h264_nvenc", "hevc_nvenc",
            "h264_qsv", "hevc_qsv", "h264_amf", "hevc_amf"
        ]
        
        results = {t: False for t in targets}
        if stdout:
            for line in stdout.split('\n'):
                for target in targets:
                    if f" {target} " in line:
                        results[target] = True
                        
        return results

    def get_hwaccels(self, ffmpeg_path: str) -> List[str]:
        """Detects available hardware acceleration methods."""
        success, stdout, stderr = run_command([ffmpeg_path, "-hwaccels"])
        if not success:
            return []
            
        hwaccels = []
        if stdout:
            # Skip the header line
            lines = stdout.strip().split('\n')
            if len(lines) > 1:
                for line in lines[1:]:
                    accel = line.strip()
                    if accel:
                        hwaccels.append(accel)
        return hwaccels

    def get_full_capabilities(self) -> Dict:
        """
        Returns a complete dictionary of FFmpeg info, encoders, and hwaccels.
        Helper for other services (like EncoderSelectionService).
        """
        info = self.get_info()
        encoders = {}
        hwaccels = []
        
        if info.callable and info.path:
            encoders = self.get_encoders(info.path)
            hwaccels = self.get_hwaccels(info.path)
            
        return {
            "info": info,
            "encoders": encoders,
            "hwaccels": hwaccels
        }

    def run_smoke_test(self, ffmpeg_path: str, encoder: str) -> bool:
        """
        Runs a very small synthetic render to ensure the encoder actually works.
        ffmpeg -f lavfi -i color=c=black:s=128x128:d=0.1 -c:v [encoder] -f null -
        """
        # Limit duration to 0.1s, resolution to 128x128
        args = [
            ffmpeg_path,
            "-f", "lavfi",
            "-i", "color=c=black:s=128x128:d=0.1",
            "-c:v", encoder,
            "-f", "null",
            "-"
        ]
        success, _, _ = run_command(args, timeout=3)
        return success

# Singleton instance
ffmpeg_detection_service = FFmpegDetectionService()
