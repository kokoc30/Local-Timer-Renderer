/**
 * Logic for playback buttons and seek bar.
 * Handles the animation loop using requestAnimationFrame.
 */

import { formatTimeSeconds } from "./display_formatting.js";

export class PreviewControls {
    constructor(state, rootElementId) {
        this.state = state;
        this.root = document.getElementById(rootElementId);
        
        // Element caching
        this.playPauseBtn = null;
        this.resetBtn = null;
        this.seekSlider = null;
        this.timeDisplay = null;
        this.frameCounter = null;
        this.progressPercent = null;
        
        // Internal state for Loop
        this.lastFrameTime = 0;
        
        this.setupUI();
        this.bindEvents();
        
        // Register for updates from the StateManager
        this.state.subscribe(() => this.updateUI());
    }

    /**
     * setupUI
     * Grabs control elements from DOM.
     */
    setupUI() {
        if (!this.root) return;
        this.playPauseBtn = this.root.querySelector('#preview-play-pause');
        this.resetBtn = this.root.querySelector('#preview-reset');
        this.seekSlider = this.root.querySelector('#preview-seek');
        this.timeDisplay = this.root.querySelector('#preview-time-info');
        this.frameCounter = this.root.querySelector('#preview-frame-info');
        this.progressPercent = this.root.querySelector('#preview-progress-percent');
        
        // Add Jump Buttons if target exists
        this.jumpStart = this.root.querySelector('#jump-start');
        this.jumpMid = this.root.querySelector('#jump-mid');
        this.jumpEnd = this.root.querySelector('#jump-end');
    }

    /**
     * bindEvents
     */
    bindEvents() {
        if (this.playPauseBtn) {
            this.playPauseBtn.addEventListener('click', () => {
                this.state.togglePlay();
                if (this.state.isPlaying) {
                    this.startLoop();
                }
            });
        }
        
        if (this.resetBtn) {
            this.resetBtn.addEventListener('click', () => {
                this.state.isPlaying = false;
                this.state.setPlaybackTime(0);
            });
        }
        
        if (this.seekSlider) {
            this.seekSlider.addEventListener('input', (e) => {
                const val = parseFloat(e.target.value);
                this.state.setPlaybackTime(val);
                this.state.isPlaying = false;
            });
        }
        
        if (this.jumpStart) this.jumpStart.addEventListener('click', () => this.state.setPlaybackTime(0));
        if (this.jumpMid) this.jumpMid.addEventListener('click', () => {
            if (this.state.plan) this.state.setPlaybackTime(this.state.plan.output_duration_seconds / 2);
        });
        if (this.jumpEnd) this.jumpEnd.addEventListener('click', () => {
            if (this.state.plan) this.state.setPlaybackTime(this.state.plan.output_duration_seconds);
        });
    }

    /**
     * startLoop
     */
    startLoop() {
        this.lastFrameTime = performance.now();
        requestAnimationFrame((t) => this.loop(t));
    }

    /**
     * loop
     * Animation loop core.
     */
    loop(time) {
        if (!this.state.isPlaying) return;

        const delta = (time - this.lastFrameTime) / 1000;
        this.lastFrameTime = time;
        
        const speed = this.state.settings.preview_speed || 1.0;
        const newTime = this.state.currentTime + (delta * speed);
        this.state.setPlaybackTime(newTime);
        
        // Auto-pause at the end
        if (this.state.plan && newTime >= this.state.plan.output_duration_seconds) {
            this.state.isPlaying = false;
            this.updateUI();
            return;
        }
        
        requestAnimationFrame((t) => this.loop(t));
    }

    /**
     * updateUI
     * Updates the control panel based on state.
     */
    updateUI() {
        if (!this.state.plan) {
            this.disableControls();
            return;
        }
        this.enableControls();

        // Update button text / icon
        if (this.playPauseBtn) {
            this.playPauseBtn.innerHTML = this.state.isPlaying ? "<span>⏸</span>" : "<span>▶</span>";
        }
        
        // Update seek bar
        if (this.seekSlider) {
            this.seekSlider.max = this.state.plan.output_duration_seconds;
            this.seekSlider.value = this.state.currentTime;
        }
        
        // Update Readouts
        if (this.timeDisplay) {
            const currentFormatted = formatTimeSeconds(this.state.currentTime, "MM:SS");
            const totalFormatted = formatTimeSeconds(this.state.plan.output_duration_seconds, "MM:SS");
            this.timeDisplay.textContent = `${currentFormatted} / ${totalFormatted}`;
        }
        
        if (this.frameCounter) {
            const frame = this.state.getCurrentFrame();
            this.frameCounter.textContent = `Frame: ${frame} / ${this.state.plan.total_frames}`;
        }
        
        if (this.progressPercent) {
            const p = Math.round(this.state.getProgress() * 100);
            this.progressPercent.textContent = `${p}%`;
        }
    }

    disableControls() {
        if (this.root) this.root.style.opacity = '0.5';
        if (this.seekSlider) this.seekSlider.disabled = true;
    }
    
    enableControls() {
        if (this.root) this.root.style.opacity = '1';
        if (this.seekSlider) this.seekSlider.disabled = false;
    }
}
