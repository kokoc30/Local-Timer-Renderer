from PIL import Image, ImageDraw
from app.services.font_service import font_service

def draw_frame(width: int, height: int, display_text: str, style: str) -> Image.Image:
    """
    Renders a single timer frame to a Pillow Image.
    
    Args:
        width: Frame width in pixels.
        height: Frame height in pixels.
        display_text: The timer text to display (e.g. "60:00").
        style: The visual style preset ("minimal" or "watch_frame").
        
    Returns:
        A new PIL Image object representing the frame.
    """
    # 1. Create base image (Black background)
    img = Image.new('RGB', (width, height), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 2. Determine base visual sizing
    # E.g. text height is ~25% of the frame height
    base_text_size = int(height * 0.25)
    font = font_service.get_font(base_text_size)
    
    # Center text coordinates
    text_bbox = draw.textbbox((0, 0), display_text, font=font)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]
    
    x = (width - text_w) / 2
    y = (height - text_h) / 2 - text_bbox[1] # offset adjustment
    
    # 3. Apply style decorations
    if style == "watch_frame" or style == "watch-frame":
        # Draw a subtle grey outline ring/bezel
        center_x = width / 2
        center_y = height / 2
        radius = min(width, height) * 0.4
        
        # Draw ring
        thickness = max(2, int(min(width, height) * 0.01))
        draw.ellipse(
            [(center_x - radius, center_y - radius), (center_x + radius, center_y + radius)],
            outline=(100, 100, 100),
            width=thickness
        )
    # else logic minimal applies automatically as just black bg with text
    
    # 4. Draw text (White)
    draw.text((x, y), display_text, font=font, fill=(255, 255, 255))
    
    return img
