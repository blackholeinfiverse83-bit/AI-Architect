// Samrachna - AI Design & Architecture Frontend
// API Configuration
// For local development: 'http://127.0.0.1:8000'
// For Render deployment, update this to your backend URL:
const API_BASE_URL = window.location.hostname === 'localhost'
    ? 'http://127.0.0.1:8000'
    : 'https://design-engine-api-y8e7.onrender.com';

// Video API now uses the same backend
const VIDEO_API_BASE_URL = API_BASE_URL;

// State Management
const state = {
    authToken: null,
    user: null,
    lastSpecId: null,
    lastSpecJson: null,
    lastPreviewUrl: null,
    lastCost: 0,
    recentDesigns: [],
    apiConnected: false,
    videoApiConnected: false,
    videos: []
};

// Utility Functions
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        const r = Math.random() * 16 | 0;
        const v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

function formatCurrency(amount) {
    if (!amount || amount === 0) return 'N/A';
    return '₹' + amount.toLocaleString('en-IN');
}

function formatJSON(obj) {
    return JSON.stringify(obj, null, 2);
}

// API Functions
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        state.apiConnected = response.ok;
        updateAPIStatus(response.ok);
        return response.ok;
    } catch (error) {
        state.apiConnected = false;
        updateAPIStatus(false);
        return false;
    }
}

async function checkVideoAPIHealth() {
    try {
        const response = await fetch(`${VIDEO_API_BASE_URL}/api/v1/video/health`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        });
        state.videoApiConnected = response.ok;
        updateVideoAPIStatus(response.ok);
        return response.ok;
    } catch (error) {
        state.videoApiConnected = false;
        updateVideoAPIStatus(false);
        return false;
    }
}

async function videoApiPost(endpoint, formData) {
    const headers = {};
    if (state.authToken) {
        headers['Authorization'] = `Bearer ${state.authToken}`;
    }

    const response = await fetch(`${VIDEO_API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers,
        body: formData
    });

    return response;
}

async function videoApiGet(endpoint, params = {}) {
    const headers = {};
    if (state.authToken) {
        headers['Authorization'] = `Bearer ${state.authToken}`;
    }

    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${VIDEO_API_BASE_URL}${endpoint}?${queryString}` : `${VIDEO_API_BASE_URL}${endpoint}`;

    const response = await fetch(url, {
        method: 'GET',
        headers
    });

    return response;
}

async function login(username, password) {
    try {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }

        const data = await response.json();
        state.authToken = data.access_token;
        state.user = username;
        return data;
    } catch (error) {
        throw error;
    }
}

// Video API now uses the same backend, so no separate login needed
async function loginVideoAPI() {
    // Video API is now part of main backend, use existing auth
    return null;
}

async function apiPost(endpoint, payload = {}) {
    const headers = {
        'Content-Type': 'application/json'
    };

    if (state.authToken) {
        headers['Authorization'] = `Bearer ${state.authToken}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload)
    });

    return response;
}

async function apiGet(endpoint, params = {}) {
    const headers = {};

    if (state.authToken) {
        headers['Authorization'] = `Bearer ${state.authToken}`;
    }

    const queryString = new URLSearchParams(params).toString();
    const url = queryString ? `${API_BASE_URL}${endpoint}?${queryString}` : `${API_BASE_URL}${endpoint}`;

    const response = await fetch(url, {
        method: 'GET',
        headers
    });

    return response;
}

// UI Functions
function updateAPIStatus(isOnline) {
    const indicator = document.getElementById('api-status-indicator');
    const text = document.getElementById('api-status-text');
    const headerDot = document.getElementById('header-status-dot');
    const headerText = document.getElementById('header-status-text');
    const dashboardStatus = document.getElementById('dashboard-api-status');

    if (isOnline) {
        indicator?.classList.add('online');
        indicator?.classList.remove('checking');
        if (text) text.textContent = 'API Online';
        if (headerDot) headerDot.classList.remove('offline');
        if (headerText) headerText.textContent = 'Online';
        if (dashboardStatus) dashboardStatus.textContent = 'Online';
    } else {
        indicator?.classList.remove('online');
        if (text) text.textContent = 'API Offline';
        if (headerDot) headerDot.classList.add('offline');
        if (headerText) headerText.textContent = 'Offline';
        if (dashboardStatus) dashboardStatus.textContent = 'Offline';
    }
}

function updateVideoAPIStatus(isOnline) {
    const dot = document.getElementById('video-api-status-dot');
    const text = document.getElementById('video-api-status-text');

    if (isOnline) {
        dot?.classList.add('online');
        if (text) text.textContent = 'Video API Online';
    } else {
        dot?.classList.remove('online');
        if (text) text.textContent = 'Video API Offline';
    }
}

function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
        element.classList.add('show');
        setTimeout(() => element.classList.remove('show'), 5000);
    }
}

function showResult(containerId, data, isError = false) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.classList.remove('hidden', 'success', 'error');
    container.classList.add(isError ? 'error' : 'success');

    if (isError) {
        container.innerHTML = `
            <div class="result-header error">
                <span>❌</span> Error
            </div>
            <div class="json-viewer">${typeof data === 'string' ? data : formatJSON(data)}</div>
        `;
    } else {
        container.innerHTML = `
            <div class="result-header success">
                <span>✅</span> Success
            </div>
            <div class="json-viewer">${formatJSON(data)}</div>
        `;
    }
}

function displayDesignResult(containerId, data) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.classList.remove('hidden');
    container.classList.add('success');

    const specId = data.spec_id || 'N/A';
    const cost = data.estimated_cost || 0;
    const previewUrl = data.preview_url || null;
    const specJson = data.spec_json || {};

    container.innerHTML = `
        <div class="result-header success">
            <span>✅</span> Design Generated Successfully
        </div>
        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">Spec ID</div>
                <div class="info-value">${specId}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Estimated Cost</div>
                <div class="info-value">${formatCurrency(cost)}</div>
            </div>
            ${previewUrl ? `
            <div class="info-item">
                <div class="info-label">Preview URL</div>
                <div class="info-value"><a href="${previewUrl}" target="_blank">${previewUrl}</a></div>
            </div>
            ` : ''}
        </div>
        <div class="json-viewer">${formatJSON(specJson)}</div>
    `;
}

function updateDashboard() {
    document.getElementById('dashboard-designs').textContent = state.recentDesigns.length;

    const specId = state.lastSpecId || 'None';
    document.getElementById('dashboard-last-spec').textContent =
        specId.length > 12 ? specId.substring(0, 12) + '...' : specId;

    document.getElementById('dashboard-cost').textContent = formatCurrency(state.lastCost);
}

function updateInputValues() {
    // Update all spec ID inputs with the last spec ID
    const specInputs = [
        'switch-spec-id', 'iterate-spec-id', 'eval-spec-id',
        'hist-spec-id', 'report-spec-id', 'rl-spec-id'
    ];

    specInputs.forEach(id => {
        const input = document.getElementById(id);
        if (input && state.lastSpecId) {
            input.value = state.lastSpecId;
        }
    });

    // Update RL design A
    const designA = document.getElementById('rl-design-a');
    if (designA && state.lastSpecId) {
        designA.value = state.lastSpecId;
    }
}

// Event Handlers
async function handleLogin(e) {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        await login(username, password);
        document.getElementById('login-screen').classList.add('hidden');
        document.getElementById('main-screen').classList.remove('hidden');
        document.getElementById('user-name').textContent = username;
        checkAPIHealth();
    } catch (error) {
        showError('login-error', error.message);
    }
}

async function handleQuickGenerate() {
    const btn = document.getElementById('quick-generate-btn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span> Generating...';
    btn.disabled = true;

    try {
        const payload = {
            user_id: state.user || 'user',
            prompt: document.getElementById('quick-prompt').value,
            city: document.getElementById('quick-city').value,
            style: document.getElementById('quick-style').value,
            context: {}
        };

        const budget = parseInt(document.getElementById('quick-budget').value);
        if (budget > 0) {
            payload.context.budget = budget;
        }

        const response = await apiPost('/api/v1/generate', payload);
        const data = await response.json();

        if (response.ok) {
            state.lastSpecId = data.spec_id;
            state.lastSpecJson = data.spec_json;
            state.lastPreviewUrl = data.preview_url;
            state.lastCost = data.estimated_cost || 0;

            state.recentDesigns.push({
                spec_id: data.spec_id,
                prompt: payload.prompt,
                city: payload.city
            });

            displayDesignResult('quick-result', data);
            updateDashboard();
            updateInputValues();
        } else {
            showResult('quick-result', data, true);
        }
    } catch (error) {
        showResult('quick-result', error.message, true);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

async function handleGenerate() {
    const btn = document.getElementById('generate-btn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span> Generating...';
    btn.disabled = true;

    try {
        const payload = {
            user_id: state.user || 'user',
            prompt: document.getElementById('gen-prompt').value,
            city: document.getElementById('gen-city').value,
            style: document.getElementById('gen-style').value,
            context: {}
        };

        const budget = parseInt(document.getElementById('gen-budget').value);
        if (budget > 0) {
            payload.context.budget = budget;
        }

        const response = await apiPost('/api/v1/generate', payload);
        const data = await response.json();

        if (response.ok) {
            state.lastSpecId = data.spec_id;
            state.lastSpecJson = data.spec_json;
            state.lastPreviewUrl = data.preview_url;
            state.lastCost = data.estimated_cost || 0;

            state.recentDesigns.push({
                spec_id: data.spec_id,
                prompt: payload.prompt,
                city: payload.city
            });

            displayDesignResult('gen-result', data);
            updateDashboard();
            updateInputValues();
        } else {
            showResult('gen-result', data, true);
        }
    } catch (error) {
        showResult('gen-result', error.message, true);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

async function handleSwitch() {
    const btn = document.getElementById('switch-btn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span> Applying...';
    btn.disabled = true;

    try {
        const payload = {
            spec_id: document.getElementById('switch-spec-id').value,
            query: document.getElementById('switch-query').value
        };

        if (!payload.spec_id || !payload.query) {
            showResult('switch-result', 'Spec ID and query are required', true);
            return;
        }

        const response = await apiPost('/api/v1/switch', payload);
        const data = await response.json();

        showResult('switch-result', data, !response.ok);
    } catch (error) {
        showResult('switch-result', error.message, true);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

async function handleIterate() {
    const btn = document.getElementById('iterate-btn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span> Iterating...';
    btn.disabled = true;

    try {
        const payload = {
            user_id: state.user || 'user',
            spec_id: document.getElementById('iterate-spec-id').value,
            strategy: document.getElementById('iterate-strategy').value
        };

        if (!payload.spec_id) {
            showResult('iterate-result', 'Spec ID is required', true);
            return;
        }

        const response = await apiPost('/api/v1/iterate', payload);
        const data = await response.json();

        showResult('iterate-result', data, !response.ok);
    } catch (error) {
        showResult('iterate-result', error.message, true);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

async function handleEvaluate() {
    const btn = document.getElementById('eval-btn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span> Submitting...';
    btn.disabled = true;

    try {
        const payload = {
            user_id: state.user || 'user',
            spec_id: document.getElementById('eval-spec-id').value,
            rating: parseInt(document.getElementById('eval-rating').value),
            notes: document.getElementById('eval-notes').value,
            feedback_text: document.getElementById('eval-feedback').value
        };

        if (!payload.spec_id) {
            showResult('eval-result', 'Spec ID is required', true);
            return;
        }

        const response = await apiPost('/api/v1/evaluate', payload);
        const data = await response.json();

        showResult('eval-result', data, !response.ok);
    } catch (error) {
        showResult('eval-result', error.message, true);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// Compliance function removed

async function handleLoadHistory() {
    const btn = document.getElementById('load-history-btn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span> Loading...';
    btn.disabled = true;

    try {
        const limit = document.getElementById('hist-limit').value;
        const response = await apiGet('/api/v1/history', { limit });
        const data = await response.json();

        showResult('history-result', data, !response.ok);
    } catch (error) {
        showResult('history-result', error.message, true);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

async function handleLoadSpecHistory() {
    const btn = document.getElementById('load-spec-history-btn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span> Loading...';
    btn.disabled = true;

    try {
        const specId = document.getElementById('hist-spec-id').value;
        if (!specId) {
            showResult('spec-history-result', 'Spec ID is required', true);
            return;
        }

        const response = await apiGet(`/api/v1/history/${specId}`, { limit: 50 });
        const data = await response.json();

        showResult('spec-history-result', data, !response.ok);
    } catch (error) {
        showResult('spec-history-result', error.message, true);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

async function handleListGeometry() {
    const btn = document.getElementById('list-geometry-btn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span> Loading...';
    btn.disabled = true;

    try {
        const response = await apiGet('/api/v1/geometry/list');
        const data = await response.json();

        showResult('geometry-list-result', data, !response.ok);
    } catch (error) {
        showResult('geometry-list-result', error.message, true);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

async function handleGenerateGeometry() {
    const btn = document.getElementById('generate-geometry-btn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span> Generating...';
    btn.disabled = true;

    try {
        if (!state.lastSpecJson) {
            showResult('geometry-result', 'Generate a design first to create geometry', true);
            return;
        }

        const payload = {
            spec_json: state.lastSpecJson,
            request_id: document.getElementById('geom-request-id').value || `req_${generateUUID().substring(0, 6)}`,
            format: document.getElementById('geom-format').value
        };

        const response = await apiPost('/api/v1/geometry/generate', payload);
        const data = await response.json();

        showResult('geometry-result', data, !response.ok);
    } catch (error) {
        showResult('geometry-result', error.message, true);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

async function handleGenerateReport() {
    const btn = document.getElementById('generate-report-btn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span> Generating...';
    btn.disabled = true;

    try {
        const specId = document.getElementById('report-spec-id').value;
        if (!specId) {
            showResult('report-result', 'Spec ID is required', true);
            return;
        }

        const response = await apiGet(`/api/v1/reports/${specId}`);
        const data = await response.json();

        showResult('report-result', data, !response.ok);
    } catch (error) {
        showResult('report-result', error.message, true);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

async function handleSubmitFeedback() {
    const btn = document.getElementById('submit-feedback-btn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span> Submitting...';
    btn.disabled = true;

    try {
        const payload = {
            design_a_id: document.getElementById('rl-design-a').value,
            design_b_id: document.getElementById('rl-design-b').value,
            preference: parseInt(document.getElementById('rl-preference').value)
        };

        const response = await apiPost('/api/v1/rl/feedback', payload);
        const data = await response.json();

        showResult('feedback-result', data, !response.ok);
    } catch (error) {
        showResult('feedback-result', error.message, true);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

async function handleTrainRLHF() {
    const btn = document.getElementById('train-rlhf-btn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span> Training...';
    btn.disabled = true;

    try {
        const payload = {
            num_samples: parseInt(document.getElementById('rlhf-samples').value)
        };

        const response = await apiPost('/api/v1/rl/train/rlhf', payload);
        const data = await response.json();

        showResult('rlhf-result', data, !response.ok);
    } catch (error) {
        showResult('rlhf-result', error.message, true);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

async function handleTrainPPO() {
    const btn = document.getElementById('train-ppo-btn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span> Training...';
    btn.disabled = true;

    try {
        const payload = {
            num_iterations: parseInt(document.getElementById('ppo-iterations').value)
        };

        const response = await apiPost('/api/v1/rl/train/opt', payload);
        const data = await response.json();

        showResult('ppo-result', data, !response.ok);
    } catch (error) {
        showResult('ppo-result', error.message, true);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

async function handleGenerateVideo() {
    const btn = document.getElementById('generate-video-btn');
    const originalText = btn.innerHTML;
    const fileInput = document.getElementById('video-script-file');

    const file = fileInput.files[0];

    if (!file) {
        showResult('video-gen-result', 'Please select a script file (.txt)', true);
        return;
    }

    // Use filename (without extension) as the title
    const title = file.name.replace(/\.[^/.]+$/, "");

    btn.innerHTML = '<span class="spinner"></span> Generating...';
    btn.disabled = true;

    try {
        // Try to authenticate with video API if not already authenticated
        if (!state.authToken) {
            await loginVideoAPI();
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('title', title);

        const response = await videoApiPost('/api/v1/video/generate-video', formData);
        const data = await response.json();

        if (response.ok) {
            showResult('video-gen-result', data);
            // Add new video ID to sessionStorage
            if (data.content_id) {
                const existingIds = JSON.parse(sessionStorage.getItem('videoIds') || '[]');
                existingIds.push(data.content_id);
                sessionStorage.setItem('videoIds', JSON.stringify(existingIds));
            }
            // Refresh video list to show the new video
            await handleRefreshVideoList();
        } else {
            // If 401, try to login and retry
            if (response.status === 401) {
                await loginVideoAPI();
                const retryResponse = await videoApiPost('/generate-video', formData);
                const retryData = await retryResponse.json();
                if (retryResponse.ok) {
                    showResult('video-gen-result', retryData);
                    handleRefreshVideoList();
                } else {
                    showResult('video-gen-result', retryData, true);
                }
            } else {
                showResult('video-gen-result', data, true);
            }
        }
    } catch (error) {
        showResult('video-gen-result', error.message, true);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

async function handleRefreshVideoList() {
    const gallery = document.getElementById('video-gallery');

    try {
        const response = await videoApiGet('/api/v1/video/contents');
        const data = await response.json();

        if (response.ok) {
            state.videos = data.items || [];
            // Store video IDs in sessionStorage for cleanup on refresh
            const videoIds = state.videos.map(v => v.content_id);
            sessionStorage.setItem('videoIds', JSON.stringify(videoIds));
            renderVideoGallery(state.videos);
        } else {
            gallery.innerHTML = `<div class="info-item error">Error loading videos: ${data.message || 'Unknown error'}</div>`;
        }
    } catch (error) {
        gallery.innerHTML = `<div class="info-item error">Error connecting to Video API: ${error.message}</div>`;
    }
}

async function deleteVideo(contentId) {
    try {
        const headers = {};
        if (state.authToken) {
            headers['Authorization'] = `Bearer ${state.authToken}`;
        }

        const response = await fetch(`${VIDEO_API_BASE_URL}/api/v1/video/content/${contentId}`, {
            method: 'DELETE',
            headers
        });

        return response.ok;
    } catch (error) {
        console.error(`Failed to delete video ${contentId}:`, error);
        return false;
    }
}

async function cleanupVideosOnRefresh() {
    // Get video IDs from sessionStorage
    const videoIdsJson = sessionStorage.getItem('videoIds');
    if (!videoIdsJson) {
        return;
    }

    try {
        const videoIds = JSON.parse(videoIdsJson);
        // Delete all videos in parallel (fire and forget - don't wait)
        videoIds.forEach(contentId => {
            deleteVideo(contentId).catch(err => {
                console.error(`Error deleting video ${contentId}:`, err);
            });
        });
        
        // Clear sessionStorage after cleanup
        sessionStorage.removeItem('videoIds');
    } catch (error) {
        console.error('Error during video cleanup:', error);
    }
}

function renderVideoGallery(videos) {
    const gallery = document.getElementById('video-gallery');

    if (videos.length === 0) {
        gallery.innerHTML = '<div class="info-item"><p style="text-align: center; color: var(--text-secondary);">No videos generated yet</p></div>';
        return;
    }

    gallery.innerHTML = videos.map(video => `
        <div class="video-card" data-id="${video.content_id}">
            <div class="video-player-container">
                <video controls preload="metadata" crossorigin="anonymous" style="width: 100%; max-height: 400px;">
                    <source src="${VIDEO_API_BASE_URL}${video.stream_url || `/api/v1/video/stream/${video.content_id}`}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
            <div class="video-info">
                <div class="video-title">${video.title || 'Untitled Video'}</div>
                <div class="video-meta">
                    <span>📅 ${video.uploaded_at ? new Date(typeof video.uploaded_at === 'number' ? video.uploaded_at * 1000 : new Date(video.uploaded_at).getTime()).toLocaleDateString() : 'N/A'}</span>
                    <span>⏱️ ${video.duration_ms ? Math.round(video.duration_ms / 1000) : 0}s</span>
                </div>
                <div class="tag-container" id="tags-${video.content_id}">
                    ${(() => {
                        try {
                            const tags = typeof video.current_tags === 'string' ? JSON.parse(video.current_tags || '[]') : (video.current_tags || []);
                            return tags.map(tag => `<span class="tag">${tag}</span>`).join('');
                        } catch(e) {
                            return '';
                        }
                    })()}
                </div>
                <a href="${VIDEO_API_BASE_URL}${video.download_url || `/api/v1/video/download/${video.content_id}`}" class="btn btn-primary btn-sm mt-2" style="width: 100%; display: block; text-align: center; text-decoration: none;" download="${video.content_id}.mp4">
                    <span>⬇️</span> Download Video
                </a>
            </div>
        </div>
    `).join('');
}


// Tab Navigation
function setupTabs() {
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const tabId = item.getAttribute('data-tab');

            // Update nav items
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');

            // Update tab contents
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `tab-${tabId}`) {
                    content.classList.add('active');
                }
            });
            
            // Auto-load videos when Video Lab tab is opened
            if (tabId === 'videogen') {
                handleRefreshVideoList();
            }
        });
    });
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Check API health on load
    checkAPIHealth();
    checkVideoAPIHealth();

    // Setup login form
    document.getElementById('login-form').addEventListener('submit', handleLogin);

    // Setup tabs
    setupTabs();

    // Setup logout
    document.getElementById('logout-btn').addEventListener('click', () => {
        state.authToken = null;
        state.user = null;
        document.getElementById('main-screen').classList.add('hidden');
        document.getElementById('login-screen').classList.remove('hidden');
    });

    // Cleanup videos from previous session on page load
    cleanupVideosOnRefresh();

    // Cleanup videos on page refresh/unload
    window.addEventListener('beforeunload', () => {
        // Try to cleanup current session videos (fire and forget)
        const videoIdsJson = sessionStorage.getItem('videoIds');
        if (videoIdsJson) {
            try {
                const videoIds = JSON.parse(videoIdsJson);
                videoIds.forEach(contentId => {
                    // Use fetch with keepalive for fire-and-forget deletion
                    const headers = {};
                    if (state.authToken) {
                        headers['Authorization'] = `Bearer ${state.authToken}`;
                    }
                    fetch(`${VIDEO_API_BASE_URL}/api/v1/video/content/${contentId}`, {
                        method: 'DELETE',
                        headers,
                        keepalive: true
                    }).catch(() => {}); // Ignore errors
                });
            } catch (e) {
                // Ignore errors during unload
            }
        }
    });
    
    // Also cleanup on page visibility change (when user switches tabs)
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            // Page is now hidden, cleanup videos
            cleanupVideosOnRefresh();
        }
    });

    // Setup all button handlers
    document.getElementById('quick-generate-btn').addEventListener('click', handleQuickGenerate);
    document.getElementById('generate-btn').addEventListener('click', handleGenerate);
    document.getElementById('switch-btn').addEventListener('click', handleSwitch);
    document.getElementById('iterate-btn').addEventListener('click', handleIterate);
    document.getElementById('eval-btn').addEventListener('click', handleEvaluate);
    document.getElementById('load-history-btn').addEventListener('click', handleLoadHistory);
    document.getElementById('load-spec-history-btn').addEventListener('click', handleLoadSpecHistory);
    document.getElementById('list-geometry-btn').addEventListener('click', handleListGeometry);
    document.getElementById('generate-geometry-btn').addEventListener('click', handleGenerateGeometry);
    document.getElementById('generate-report-btn').addEventListener('click', handleGenerateReport);
    document.getElementById('submit-feedback-btn').addEventListener('click', handleSubmitFeedback);
    document.getElementById('train-rlhf-btn').addEventListener('click', handleTrainRLHF);
    document.getElementById('train-ppo-btn').addEventListener('click', handleTrainPPO);

    // Video Lab handlers
    document.getElementById('generate-video-btn').addEventListener('click', handleGenerateVideo);
    document.getElementById('refresh-video-list-btn').addEventListener('click', handleRefreshVideoList);

    // Rating slider display
    const ratingSlider = document.getElementById('eval-rating');
    const ratingDisplay = document.getElementById('rating-display');
    if (ratingSlider && ratingDisplay) {
        ratingSlider.addEventListener('input', (e) => {
            const stars = '⭐'.repeat(parseInt(e.target.value));
            ratingDisplay.textContent = stars;
        });
    }
});
