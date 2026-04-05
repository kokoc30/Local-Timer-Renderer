/**
 * Shared utility to format raw seconds into various countdown strings.
 * Standardizes time representation across the app.
 */

export function formatTimeSeconds(totalSeconds, format = "MM:SS") {
    totalSeconds = Math.max(0, totalSeconds);
    
    // For countdown style, we normally show H:MM:SS or MM:SS
    const hrs = Math.floor(totalSeconds / 3600);
    const mins = Math.floor((totalSeconds % 3600) / 60);
    const secs = Math.floor(totalSeconds % 60);

    if (format === "HH:MM:SS" || hrs > 0) {
        return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else if (format === "H:MM:SS") {
        return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else if (format === "M:SS") {
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    } else {
        // Default MM:SS
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
}
