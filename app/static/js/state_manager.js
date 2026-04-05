/**
 * Manages the current playback and render-plan state.
 * Implements a simple subscriber pattern to notify UI and Renderer.
 */

export class StateManager {
    constructor() {
        this.settings = null;
        this.plan = null;
        
        // Playback state
        this.currentTime = 0; // Current output timeline time (0 to output_duration_seconds)
        this.isPlaying = false;
        this.isSeeking = false;
        
        this.subscribers = [];
    }

    /**
     * updatePlan
     * Sets the latest validated render plan from the backend.
     */
    updatePlan(settings, plan) {
        this.settings = settings;
        this.plan = plan;
        
        // Reset playback when a new plan is loaded
        this.currentTime = 0;
        this.isPlaying = false;
        
        this.notify();
    }

    /**
     * setPlaybackTime
     * Forces playback to a specific output second.
     */
    setPlaybackTime(time) {
        if (!this.plan) return;
        this.currentTime = Math.max(0, Math.min(time, this.plan.output_duration_seconds));
        this.notify();
    }

    /**
     * togglePlay
     */
    togglePlay() {
        if (!this.plan) return;
        this.isPlaying = !this.isPlaying;
        this.notify();
    }

    /**
     * subscribe
     */
    subscribe(callback) {
        this.subscribers.push(callback);
    }

    /**
     * notify
     */
    notify() {
        this.subscribers.forEach(cb => cb(this));
    }

    /**
     * getProgress
     * Returns 0.0 to 1.0 progress.
     */
    getProgress() {
        if (!this.plan || this.plan.output_duration_seconds === 0) return 0;
        return this.currentTime / this.plan.output_duration_seconds;
    }

    /**
     * getRemainingDisplaySeconds
     * The core math for the countdown value.
     */
    getRemainingDisplaySeconds() {
        if (!this.plan) return 0;
        const progress = this.getProgress();
        
        // Strategy: 1.0 progress is 0, 0.0 progress is total_display_seconds
        // We use ceil() to ensure the first frame shows the full duration.
        const remaining = this.plan.total_display_seconds * (1 - progress);
        return Math.ceil(remaining);
    }

    /**
     * getCurrentFrame
     */
    getCurrentFrame() {
        if (!this.plan) return 0;
        const frame = Math.floor(this.currentTime * this.plan.fps);
        return Math.min(frame, this.plan.total_frames - 1);
    }
}
