import os
import platform
from PIL import ImageFont

class FontService:
    def __init__(self):
        self._font_cache = {}
        self._default_font_name = self._find_system_font()

    def _find_system_font(self):
        """
        Attempt to find a clean, sans-serif or monospace font on the host system.
        """
        system = platform.system()
        candidates = []
        
        if system == "Windows":
            candidates = [
                "C:/Windows/Fonts/consola.ttf", # Consolas
                "C:/Windows/Fonts/arial.ttf",   # Arial
                "C:/Windows/Fonts/calibri.ttf", # Calibri
            ]
        elif system == "Darwin": # macOS
            candidates = [
                "/System/Library/Fonts/Menlo.ttc",
                "/Library/Fonts/Arial.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
            ]
        else: # Linux
            candidates = [
                "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
                "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf",
            ]
            
        for font_path in candidates:
            if os.path.exists(font_path):
                return font_path
                
        return None # Will trigger Pillow's default bitmap font

    def get_font(self, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        """
        Returns an ImageFont for the requested size, caching it to avoid reloading.
        Falls back to Pillow's default bitmap font if no system font is found.
        """
        if size in self._font_cache:
            return self._font_cache[size]
            
        if self._default_font_name:
            try:
                font = ImageFont.truetype(self._default_font_name, size)
                self._font_cache[size] = font
                return font
            except Exception:
                pass # Fall through to default if load fails
        
        # Fallback to the default bitmap font (size arg is ignored by load_default)
        font = ImageFont.load_default()
        self._font_cache[size] = font
        return font

# Singleton instance
font_service = FontService()
