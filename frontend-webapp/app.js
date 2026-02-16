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
    videos: [],
    uploadedGLBFile: null  // Store uploaded GLB file info
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
            
            // Store preview URL for Geometry tab (will auto-load when tab is opened)
            // Preview will be shown automatically when user switches to Geometry tab
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

// Removed handlers for Generate, Switch, Iterate, Evaluate, and History tabs
// Removed handleListGeometry and handleGenerateGeometry - Geometry tab is now preview-only

function displayGeometryPreview(glbUrl, title = '3D Model', isFile = false) {
    const previewSection = document.getElementById('geometry-preview-section');
    const viewer = document.getElementById('geometry-viewer');
    const previewInfo = document.getElementById('geometry-preview-info');
    const noPreview = document.getElementById('geometry-no-preview');
    const clearBtn = document.getElementById('clear-preview-btn');
    const dropZone = document.getElementById('geometry-drop-zone');
    
    if (!viewer || !previewSection) return;
    
    if (!glbUrl) {
        // Hide preview, show no preview message
        if (viewer) viewer.style.display = 'none';
        if (previewInfo) previewInfo.style.display = 'none';
        if (noPreview) noPreview.style.display = 'block';
        if (clearBtn) clearBtn.style.display = 'none';
        if (dropZone) dropZone.style.display = 'flex';
        return;
    }
    
    // Hide no preview message and drop zone, show preview
    if (noPreview) noPreview.style.display = 'none';
    if (dropZone) dropZone.style.display = 'none';
    if (viewer) viewer.style.display = 'block';
    if (previewInfo) previewInfo.style.display = 'block';
    if (clearBtn) clearBtn.style.display = 'inline-block';
    
    // Load GLB file (works with both URLs and object URLs)
    viewer.src = glbUrl;
    viewer.alt = title;
    
    // Update info
    if (previewInfo) {
        const sourceType = isFile ? 'Uploaded File' : 'Generated Design';
        previewInfo.innerHTML = `
            <div class="info-item">
                <div class="info-label">Source</div>
                <div class="info-value">${sourceType}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Model</div>
                <div class="info-value">${title}</div>
            </div>
            ${!isFile ? `
            <div class="info-item">
                <div class="info-label">Preview URL</div>
                <div class="info-value"><a href="${glbUrl}" target="_blank">${glbUrl.length > 60 ? glbUrl.substring(0, 60) + '...' : glbUrl}</a></div>
            </div>
            ` : ''}
        `;
    }
}

function handleGLBFileUpload(file) {
    if (!file) {
        console.error('No file provided');
        return;
    }
    
    console.log('Handling file upload:', file.name, file.type);
    
    // Check file type
    if (!file.name.toLowerCase().endsWith('.glb') && !file.name.toLowerCase().endsWith('.gltf')) {
        alert('Please upload a GLB or GLTF file');
        return;
    }
    
    // Create object URL for the file
    const objectUrl = URL.createObjectURL(file);
    console.log('Created object URL:', objectUrl);
    
    // Display preview
    displayGeometryPreview(objectUrl, file.name, true);
    
    // Store file info in state
    state.uploadedGLBFile = {
        name: file.name,
        url: objectUrl,
        file: file
    };
    
    console.log('File uploaded successfully');
}

function clearPreview() {
    // Revoke object URL if it was an uploaded file
    if (state.uploadedGLBFile && state.uploadedGLBFile.url) {
        URL.revokeObjectURL(state.uploadedGLBFile.url);
        state.uploadedGLBFile = null;
    }
    
    // Clear preview
    displayGeometryPreview(null, null);
}

function loadPreviewFromLastDesign() {
    if (state.lastPreviewUrl && state.lastPreviewUrl.endsWith('.glb')) {
        // Clear any uploaded file first
        if (state.uploadedGLBFile) {
            URL.revokeObjectURL(state.uploadedGLBFile.url);
            state.uploadedGLBFile = null;
        }
        displayGeometryPreview(state.lastPreviewUrl, state.lastSpecId || 'Last Generated Design', false);
    } else {
        displayGeometryPreview(null, null);
        // Show message
        const noPreview = document.getElementById('geometry-no-preview');
        if (noPreview) {
            noPreview.innerHTML = `
                <p style="text-align: center; color: var(--text-secondary); padding: 40px;">
                    No 3D model preview available.<br>
                    Upload a GLB file or generate a design from the Dashboard.
                </p>
            `;
        }
    }
}

// Geometry file upload setup
function setupGeometryFileUpload() {
    const dropZone = document.getElementById('geometry-drop-zone');
    const fileInput = document.getElementById('geometry-file-input');
    
    console.log('Setting up geometry file upload...');
    console.log('Drop zone:', dropZone);
    console.log('File input:', fileInput);
    
    if (!dropZone || !fileInput) {
        console.error('Geometry upload elements not found');
        console.error('Drop zone:', dropZone);
        console.error('File input:', fileInput);
        return;
    }
    
    console.log('Geometry upload elements found, attaching handlers...');
    
    // File input change handler
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            handleGLBFileUpload(file);
        }
    });
    
    // Drag and drop handlers
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add('drag-over');
    });
    
    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('drag-over');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleGLBFileUpload(files[0]);
        }
    });
    
    // Click to browse (but don't trigger on label click)
    dropZone.addEventListener('click', (e) => {
        // Don't trigger if clicking on the label button
        if (e.target.tagName !== 'LABEL' && e.target.closest('label') === null) {
            fileInput.click();
        }
    });
    
    // Prevent default drag behaviors on window
    window.addEventListener('dragover', (e) => {
        e.preventDefault();
    });
    
    window.addEventListener('drop', (e) => {
        e.preventDefault();
    });
}

// Removed handlers for Reports and RL Training tabs

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
            
            // Auto-load preview when Geometry tab is opened
            if (tabId === 'geometry') {
                setTimeout(() => {
                    loadPreviewFromLastDesign();
                }, 300);
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

    // Setup all button handlers (only Dashboard, Geometry, and Video Lab)
    document.getElementById('quick-generate-btn').addEventListener('click', handleQuickGenerate);
    document.getElementById('load-preview-btn').addEventListener('click', loadPreviewFromLastDesign);
    document.getElementById('clear-preview-btn').addEventListener('click', clearPreview);
    
    // Setup Geometry file upload handlers (with delay to ensure DOM is ready)
    setTimeout(() => {
        setupGeometryFileUpload();
    }, 500);

    // Video Lab handlers
    document.getElementById('generate-video-btn').addEventListener('click', handleGenerateVideo);
    document.getElementById('refresh-video-list-btn').addEventListener('click', handleRefreshVideoList);
});
