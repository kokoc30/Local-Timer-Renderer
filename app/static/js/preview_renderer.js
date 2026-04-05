/**
 * Handles HTML5 Canvas drawing for style presets.
 * Deterministic: Always draws current state without local playback state.
 */

import { formatTimeSeconds } from "./display_formatting.js";

export class PreviewRenderer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        
        // Internal resolution (1920x1080 default)
        this.renderWidth = 1920;
        this.renderHeight = 1080;
    }

    /**
     * setResolution
     * Internal logical resolution resize.
     */
    setResolution(w, h) {
        this.renderWidth = w;
        this.renderHeight = h;
        this.resize();
    }

    /**
     * resize
     * Handles CSS size vs internal canvas size vs devicePixelRatio.
     */
    resize() {
        if (!this.canvas) return;
        const dpr = window.devicePixelRatio || 1;
        const rect = this.canvas.parentElement.getBoundingClientRect();
        
        // We want to fill the container while preserving aspect ratio
        // For now, assume 16:9 for current container logic
        const displayWidth = rect.width;
        const displayHeight = rect.width * (this.renderHeight / this.renderWidth);
        
        this.canvas.style.width = `${displayWidth}px`;
        this.canvas.style.height = `${displayHeight}px`;
        
        this.canvas.width = displayWidth * dpr;
        this.canvas.height = displayHeight * dpr;
        
        this.ctx.scale(dpr, dpr);
    }

    /**
     * draw
     * Entry point for rendering a frame based on current state.
     */
    draw(state) {
        if (!this.ctx || !state.plan) return;

        const w = parseFloat(this.canvas.style.width);
        const h = parseFloat(this.canvas.style.height);
        
        // Clear background
        this.ctx.fillStyle = state.settings.background_color || "#000000";
        this.ctx.fillRect(0, 0, w, h);

        const remainingSeconds = state.getRemainingDisplaySeconds();
        const displayTimeStr = formatTimeSeconds(remainingSeconds, state.settings.display_format);
        
        this.ctx.save();
        
        // Scale coordinate system to 1920x1080 logical units for preset math
        const scale = w / this.renderWidth;
        this.ctx.scale(scale, scale);

        // Style Preset Dispatch
        const preset = state.settings.style_preset;
        if (preset === "watch-frame") {
            this.drawWatchFrame(displayTimeStr, state.settings.text_color);
        } else {
            this.drawMinimal(displayTimeStr, state.settings.text_color);
        }

        this.ctx.restore();
    }

    /**
     * drawMinimal
     * Simply center the text.
     */
    drawMinimal(text, color) {
        this.ctx.fillStyle = color || "#FFFFFF";
        this.ctx.textAlign = "center";
        this.ctx.textBaseline = "middle";
        
        // Bold MONO font for timer
        this.ctx.font = "bold 320px 'JetBrains Mono', monospace";
        this.ctx.fillText(text, this.renderWidth / 2, this.renderHeight / 2);
    }

    /**
     * drawWatchFrame
     * Center text inside a premium digital-watch style bezel.
     */
    drawWatchFrame(text, color) {
        const centerX = this.renderWidth / 2;
        const centerY = this.renderHeight / 2;
        
        // Draw Bezel / Outer Ring
        this.ctx.strokeStyle = "rgba(255,255,255,0.15)";
        this.ctx.lineWidth = 15;
        this.ctx.beginPath();
        this.ctx.roundRect(centerX - 550, centerY - 300, 1100, 600, 80);
        this.ctx.stroke();

        // Inner soft glow or border
        this.ctx.strokeStyle = "rgba(255,255,255,0.05)";
        this.ctx.lineWidth = 40;
        this.ctx.stroke();

        // Text
        this.ctx.fillStyle = color || "#FFFFFF";
        this.ctx.textAlign = "center";
        this.ctx.textBaseline = "middle";
        this.ctx.font = "bold 360px 'JetBrains Mono', monospace";
        
        // Shadow for premium look
        this.ctx.shadowColor = "rgba(255,255,255,0.3)";
        this.ctx.shadowBlur = 20;
        
        this.ctx.fillText(text, centerX, centerY);
    }
}
