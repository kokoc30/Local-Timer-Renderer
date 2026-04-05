/**
 * Local Timer Renderer - Frontend Orchestrator (Task 3)
 * 
 * Responsibilities:
 * - Initialize State, Renderer, and Controls.
 * - Handle form input and backend communication.
 * - Synchronize UI panels with the preview state.
 */

import { StateManager } from "./js/state_manager.js";
import { PreviewRenderer } from "./js/preview_renderer.js";
import { PreviewControls } from "./js/preview_controls.js";
import { CapabilitiesManager } from "./js/capabilities_manager.js";

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Core Modules
    const state = new StateManager();
    const renderer = new PreviewRenderer("preview-canvas");
    const controls = new PreviewControls(state, "preview-controls-overlay");
    const capabilities = new CapabilitiesManager();

    // 2. UI Elements
    const statusText = document.getElementById('status-text');
    const statusIndicator = document.getElementById('system-status-indicator');
    const settingsForm = document.getElementById('timer-settings-form');
    const renderBtn = document.getElementById('render-btn');

    // Plan Display Elements
    const planDisplayDuration = document.getElementById('plan-display-duration');
    const planOutputDuration = document.getElementById('plan-output-duration');
    const planTotalFrames = document.getElementById('plan-total-frames');
    const planFps = document.getElementById('plan-fps');
    const planSummary = document.getElementById('render-plan-summary');

    /**
     * checkSystemStatus
     */
    async function checkSystemStatus() {
        try {
            const response = await fetch('/api/system/status');
            const data = await response.json();
            if (data.ok) {
                statusText.textContent = `Connected (v${data.version})`;
                statusIndicator.className = 'status-badge online';
            }
        } catch (e) {
            statusText.textContent = 'Disconnected';
            statusIndicator.className = 'status-badge offline';
        }
    }

    /**
     * getSettings
     */
    function getSettings() {
        const formData = new FormData(settingsForm);
        const res = formData.get('resolution').split('x');
        return {
            mode: "countdown",
            start_time: formData.get('start-time'),
            display_format: formData.get('display-format'),
            preview_speed: parseFloat(formData.get('preview-speed')),
            width: parseInt(res[0]),
            height: parseInt(res[1]),
            fps: parseInt(formData.get('fps')),
            style_preset: formData.get('style-preset'),
            background_color: "#000000",
            text_color: "#FFFFFF",
            output_format: "mp4",
            encoder_preference: formData.get('encoder-preference')
        };
    }

    /**
     * updateRenderPlan
     */
    async function updateRenderPlan() {
        const settings = getSettings();
        try {
            const response = await fetch('/api/render/plan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
            });
            const data = await response.json();

            if (response.ok) {
                // Update Logic State
                state.updatePlan(settings, data);
                renderer.setResolution(settings.width, settings.height);
                
                // Update Plan UI
                planDisplayDuration.textContent = data.total_display_seconds + 's';
                planOutputDuration.textContent = data.output_duration_seconds.toFixed(2) + 's';
                planTotalFrames.textContent = data.total_frames;
                planFps.textContent = data.fps;
                planSummary.textContent = data.summary_text;
                planSummary.classList.remove('error');
                
                // Initial draw
                renderer.draw(state);
            } else {
                handlePlanningError(data.detail);
            }
        } catch (error) {
            handlePlanningError("Backend connection lost");
        }
    }

    function handlePlanningError(message) {
        state.updatePlan(null, null); // Clear state
        planDisplayDuration.textContent = '--';
        planOutputDuration.textContent = '--';
        planTotalFrames.textContent = '--';
        planFps.textContent = '--';
        
        if (Array.isArray(message)) {
            const err = message[0];
            planSummary.textContent = `Error: ${err.loc.join('.')} - ${err.msg}`;
        } else {
            planSummary.textContent = `Error: ${message}`;
        }
        planSummary.classList.add('error');
        
        // Clear canvas
        renderer.draw(state);
    }

    // Job State
    let activeJobId = null;
    let pollInterval = null;

    // View Elements
    const viewPlanning = document.getElementById('view-planning');
    const viewProgress = document.getElementById('view-progress');
    const viewResults = document.getElementById('view-results');

    // Output UI Elements
    const statusContainer = document.getElementById('render-status-container');
    const statusMessage = document.getElementById('render-status-message');
    const statusBadge = document.getElementById('render-status-badge');
    const progressBar = document.getElementById('progress-bar');
    const progressPercent = document.getElementById('progress-percent');
    const progressFrames = document.getElementById('progress-frames');
    const heroStatusMessage = document.getElementById('hero-status-message');
    const heroSpinner = document.getElementById('hero-spinner');
    
    // Results Elements
    const videoPlayer = document.getElementById('result-video-player');
    const btnDownload = document.getElementById('btn-download-mp4');
    const btnCopyPath = document.getElementById('btn-copy-path');
    const btnNewRender = document.getElementById('btn-new-render');
    const resJobId = document.getElementById('res-job-id');
    const resEncoder = document.getElementById('res-encoder');
    const resSize = document.getElementById('res-size');
    const resTime = document.getElementById('res-time');

    // History Element
    const historyList = document.getElementById('history-list');

    function showView(viewId) {
        [viewPlanning, viewProgress, viewResults].forEach(v => v.classList.remove('active-view'));
        document.getElementById(viewId).classList.add('active-view');
        
        // Safety: pause video if navigating away
        if(viewId !== 'view-results') {
            videoPlayer.pause();
        }
    }

    btnNewRender.addEventListener('click', () => {
        showView('view-planning');
        videoPlayer.src = ""; // Stop buffering
    });

    /**
     * Job Management
     */
    async function startRenderJob() {
        if (activeJobId) {
            console.warn("A job is already running.");
            return;
        }

        if (!state.plan) {
            alert("No valid render plan available. Fix settings before rendering.");
            return;
        }

        const settings = getSettings();
        try {
            const response = await fetch('/api/render/jobs', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
            });
            const data = await response.json();

            if (response.ok) {
                activeJobId = data.job.job_id;
                setupJobUI(activeJobId);
                startPolling(activeJobId);
                fetchSessionHistory(); // Update history immediately
            } else {
                alert("Failed to start job: " + (data.detail || "Unknown error"));
            }
        } catch (error) {
            alert("Failed to connect to backend to start job.");
        }
    }

    function setupJobUI(jobId) {
        showView('view-progress');
        heroStatusMessage.textContent = "Booting Render Pipeline...";
        heroSpinner.style.borderTopColor = "var(--accent)";
        heroSpinner.style.animation = "spin 1s linear infinite";

        statusMessage.textContent = `Job ID: ${jobId}`;
        statusBadge.textContent = 'Queued';
        statusBadge.style.color = "var(--primary-light)";
        progressBar.style.width = '0%';
        progressPercent.textContent = '0%';
        progressFrames.textContent = `0 / ${state.plan.total_frames} frames`;
        renderBtn.disabled = true;
    }

    function startPolling(jobId) {
        if (pollInterval) clearInterval(pollInterval);
        
        pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/render/jobs/${jobId}`);
                if (!response.ok) throw new Error("Status API failed");
                const data = await response.json();
                const job = data.job;

                // Update UI visually
                statusBadge.textContent = job.status.toUpperCase();
                progressBar.style.width = `${job.progress_percent}%`;
                progressPercent.textContent = `${job.progress_percent}%`;
                progressFrames.textContent = `${job.progress_current_frame} / ${job.total_frames} frames`;

                if (job.status === 'running') {
                    statusBadge.style.color = "chartreuse";
                    heroStatusMessage.textContent = "Rendering Frames...";
                } else if (job.status === 'encoding_video') {
                    statusBadge.style.color = "orange";
                    statusMessage.textContent = "Processing Video Stream...";
                    heroStatusMessage.textContent = "Encoding MP4...";
                    heroSpinner.style.borderTopColor = "orange";
                    heroSpinner.style.animation = "spin 0.5s linear infinite";
                } else if (job.status === 'completed' || job.status === 'failed') {
                    clearInterval(pollInterval);
                    activeJobId = null;
                    renderBtn.disabled = false;
                    
                    if (job.status === 'completed') {
                        statusBadge.style.color = "var(--accent)";
                        heroStatusMessage.textContent = "Ready.";
                        heroSpinner.style.animation = "none";
                        showJobResults(job);
                    } else {
                        statusBadge.style.color = "var(--danger)";
                        heroStatusMessage.textContent = "Job Failed";
                        heroSpinner.style.borderTopColor = "var(--danger)";
                        heroSpinner.style.animation = "none";
                        statusMessage.textContent = `Job ${jobId} Failed: ${job.error_message}`;
                        alert(`Job failed: ${job.error_message}`);
                        showView('view-planning'); // Fallback to planning
                    }
                    fetchSessionHistory(); // Refresh history
                }
            } catch (error) {
                console.error("Polling error", error);
            }
        }, 1000);
    }

    function showJobResults(job) {
        if (!job.output_mp4_exists) {
            alert("Warning: Job finished but MP4 does not exist.");
            return;
        }

        resJobId.textContent = job.job_id;
        resEncoder.textContent = job.selected_video_encoder || "Unknown";
        resSize.textContent = (job.output_mp4_size_bytes / (1024 * 1024)).toFixed(2) + " MB";
        
        const dt = new Date(job.updated_at);
        resTime.textContent = dt.toLocaleTimeString();

        const videoSrc = `/api/render/jobs/${job.job_id}/download`;
        videoPlayer.src = videoSrc;
        
        btnDownload.href = videoSrc;
        btnDownload.download = `timer_${job.job_id}.mp4`;
        
        btnCopyPath.onclick = () => {
             navigator.clipboard.writeText(job.output_mp4_path).then(()=>alert("Output path copied to clipboard!"));
        };

        showView('view-results');
    }

    async function fetchSessionHistory() {
        try {
            const response = await fetch('/api/render/jobs');
            if (response.ok) {
                const data = await response.json();
                renderHistory(data.jobs);
                
                // Job Resumption Logic (Task 9)
                // If we aren't currently polling, check if any job is still in a running state.
                if (!activeJobId && data.jobs && data.jobs.length > 0) {
                    const latestJob = data.jobs[0]; // Already sorted newest first
                    const terminalStates = ['completed', 'failed', 'cancelled'];
                    if (!terminalStates.includes(latestJob.status)) {
                        console.log("Resuming poll for active job:", latestJob.job_id);
                        activeJobId = latestJob.job_id;
                        
                        // Sync state plan first if possible
                        state.updatePlan(latestJob.settings, latestJob.plan);
                        
                        setupJobUI(activeJobId);
                        startPolling(activeJobId);
                    }
                }
            }
        } catch (error) {
            console.error("Could not fetch history", error);
        }
    }

    function renderHistory(jobs) {
        if (!jobs || jobs.length === 0) {
            historyList.innerHTML = `<div class="empty-history" style="font-size: 0.85rem; color: var(--text-muted);">No jobs run in this session.</div>`;
            return;
        }

        historyList.innerHTML = '';
        jobs.forEach(job => {
            const card = document.createElement('div');
            card.className = `history-card`;
            
            const dt = new Date(job.created_at);
            const timeStr = dt.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'});
            
            let statusColor = "var(--text-muted)";
            if (job.status === 'completed') statusColor = "var(--accent)";
            else if (job.status === 'failed') statusColor = "var(--danger)";
            else if (['running', 'encoding_video', 'queued'].includes(job.status)) statusColor = "var(--primary-light)";

            card.innerHTML = `
                <div class="hc-header">
                    <span class="hc-id">${job.job_id.split('_').pop()}</span>
                    <span class="hc-status" style="color: ${statusColor}">${job.status}</span>
                </div>
                <div class="hc-time">${timeStr}</div>
            `;

            // Allow clicking to preview completed jobs again
            if (job.status === 'completed') {
                card.onclick = () => {
                    if(!activeJobId) { // Only if not currently rendering
                        showJobResults(job);
                        
                        // Highlight active card
                        document.querySelectorAll('.history-card').forEach(c => c.classList.remove('active'));
                        card.classList.add('active');
                    }
                };
            } else {
                card.style.opacity = "0.6";
                card.style.cursor = "default";
            }

            historyList.appendChild(card);
        });
    }

    // 3. Global Listeners & Loops
    settingsForm.addEventListener('input', debounce(updateRenderPlan, 400));
    window.addEventListener('resize', () => {
        renderer.resize();
        renderer.draw(state);
    });
    
    renderBtn.addEventListener('click', startRenderJob);

    // Sync Renderer with state changes (playback loop)
    state.subscribe((s) => {
        renderer.draw(s);
    });

    // 4. Initialize
    checkSystemStatus();
    updateRenderPlan();
    fetchSessionHistory(); // Fetch any existing jobs on load

    // Helper: Debounce
    function debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    console.log('Local Timer Renderer: Task 5 Orchestrator Loaded.');
});
