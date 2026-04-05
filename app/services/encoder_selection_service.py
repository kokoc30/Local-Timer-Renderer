from app.services.ffmpeg_detection_service import ffmpeg_detection_service

class EncoderSelectionService:
    def select_encoder(self, preference: str) -> str:
        """
        preference is one of: "auto", "nvidia", "cpu"
        returns the target encoder string for FFmpeg (e.g., 'libx264', 'h264_nvenc')
        """
        if preference == "cpu":
            return "libx264"
            
        capabilities = ffmpeg_detection_service.get_full_capabilities()
        has_nvenc = capabilities.get("encoders", {}).get("h264_nvenc", False)
        
        if preference == "nvidia":
            if has_nvenc:
                return "h264_nvenc"
            else:
                raise ValueError("NVIDIA (nvenc) encoding was explicitly requested, but 'h264_nvenc' was not detected in FFmpeg.")
                
        # auto mode
        if has_nvenc:
            return "h264_nvenc"
        return "libx264"

encoder_selection_service = EncoderSelectionService()
