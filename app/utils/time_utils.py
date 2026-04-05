import re

def parse_time_string(time_str: str) -> int:
    """
    Parses a time string into total seconds.
    Supports formats:
    - MM:SS (e.g., 60:00, 05:00)
    - HH:MM:SS (e.g., 01:00:00, 00:05:00)
    - H:MM:SS (e.g., 1:05:00)
    
    Returns:
        int: Total seconds
    
    Raises:
        ValueError: If format is invalid
    """
    # Consolidated regex to match RenderSettings validation
    # Group explanation:
    # 1: ((hours):)? optional hours part
    # 2: (hours) hours digits
    # 3: (minutes) minutes digits
    # 4: (seconds) [0-5]\d seconds digits
    match = re.match(r"^(?:(\d+):)?(\d+):([0-5]\d)$", time_str)
    if match:
        hours_str, minutes_str, seconds_str = match.groups()
        hours = int(hours_str) if hours_str else 0
        minutes = int(minutes_str)
        seconds = int(seconds_str)
        return hours * 3600 + minutes * 60 + seconds
        
    raise ValueError(f"Invalid time format: {time_str}. Expected MM:SS or HH:MM:SS.")

def format_seconds(total_seconds: int, format_str: str = "MM:SS") -> str:
    """
    Formats total seconds into a human-readable string.
    
    Args:
        total_seconds: Total duration in seconds
        format_str: "MM:SS" or "HH:MM:SS"
        
    Returns:
        str: Formatted time string
    """
    total_seconds = max(0, total_seconds)
    
    if format_str == "HH:MM:SS" or total_seconds >= 3600:
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
