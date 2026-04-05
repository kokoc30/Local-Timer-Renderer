/**
 * CapabilitiesManager - Task 4
 * Handles fetching system diagnostics and updating the readiness UI.
 */
export class CapabilitiesManager {
    constructor() {
        // UI Elements
        this.ffmpegItem = document.getElementById('ffmpeg-status-item');
        this.nvencItem = document.getElementById('nvenc-status-item');
        this.recommendationBox = document.getElementById('readiness-recommendation');
        this.refreshBtn = document.getElementById('refresh-diagnostics-btn');
        
        // Detailed Info Elements
        this.pathVal = document.getElementById('diag-ffmpeg-path');
        this.versionVal = document.getElementById('diag-ffmpeg-version');
        this.encodersVal = document.getElementById('diag-encoders-list');

        this.init();
    }

    init() {
        if (this.refreshBtn) {
            this.refreshBtn.addEventListener('click', () => this.fetchCapabilities(true));
        }
        // Initial fetch
        this.fetchCapabilities();
    }

    async fetchCapabilities(isRefresh = false) {
        if (isRefresh) {
            this.refreshBtn.classList.add('spinning');
        }

        try {
            const response = await fetch('/api/system/capabilities');
            const data = await response.json();

            if (data.ok) {
                this.updateUI(data);
            }
        } catch (error) {
            console.error("Failed to fetch system capabilities:", error);
            this.showError("Connection lost. Cannot verify diagnostics.");
        } finally {
            if (isRefresh) {
                setTimeout(() => this.refreshBtn.classList.remove('spinning'), 500);
            }
        }
    }

    updateUI(data) {
        const { ffmpeg, encoders, recommendation } = data;

        // 1. Update FFmpeg Item
        if (ffmpeg.installed && ffmpeg.callable) {
            this.ffmpegItem.className = 'readiness-item ready';
            this.ffmpegItem.querySelector('.value').textContent = 'Installed';
        } else {
            this.ffmpegItem.className = 'readiness-item missing';
            this.ffmpegItem.querySelector('.value').textContent = 'Missing';
        }

        // 2. Update NVENC Item
        if (encoders.h264_nvenc) {
            this.nvencItem.className = 'readiness-item ready';
            this.nvencItem.querySelector('.value').textContent = 'Available';
        } else if (ffmpeg.installed) {
            this.nvencItem.className = 'readiness-item warning';
            this.nvencItem.querySelector('.value').textContent = 'No GPU';
        } else {
            this.nvencItem.className = 'readiness-item missing';
            this.nvencItem.querySelector('.value').textContent = '--';
        }

        // 3. Update Recommendation Box
        this.recommendationBox.className = ffmpeg.installed ? 'recommendation-box' : 'recommendation-box error';
        this.recommendationBox.querySelector('.text').textContent = recommendation.reason;
        this.recommendationBox.querySelector('.icon').textContent = ffmpeg.installed ? '✅' : '⚠️';

        // 4. Update Details
        this.pathVal.textContent = ffmpeg.path || 'Not found';
        this.versionVal.textContent = ffmpeg.version || 'N/A';
        
        const availableEncoders = Object.entries(encoders)
            .filter(([_, available]) => available)
            .map(([name]) => name);
        
        this.encodersVal.textContent = availableEncoders.length > 0 
            ? availableEncoders.join(', ') 
            : 'None detected';
    }

    showError(msg) {
        this.recommendationBox.className = 'recommendation-box error';
        this.recommendationBox.querySelector('.text').textContent = msg;
    }
}
