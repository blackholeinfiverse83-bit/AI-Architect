// Samrachna - AI Design & Architecture Frontend
// API Configuration
// For local development: 'http://127.0.0.1:8000'
// For Render deployment, update this to your backend URL:
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? `http://${window.location.hostname}:8000` // Dynamically match the current hostname
    : 'https://design-engine-api-gvch.onrender.com';


// State Management
const AUTH_API_BASE_URL = 'https://ai-being-ecwj.onrender.com';

const state = {
    authToken: localStorage.getItem('authToken'),
    user: localStorage.getItem('user'),
    lastSpecId: null,
    lastSpecJson: null,
    lastPreviewUrl: null,
    lastCost: 0,
    recentDesigns: [],
    apiConnected: false,
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


async function login(email, password) {
    try {
        const response = await fetch(`${AUTH_API_BASE_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Login failed');
        }

        const data = await response.json();
        const token = data.token;
        const userName = data.user.name || data.user.email || email;
        
        state.authToken = token;
        state.user = userName;
        localStorage.setItem('authToken', token);
        localStorage.setItem('user', userName);
        
        return data;
    } catch (error) {
        throw error;
    }
}

async function signup(email, password, name) {
    try {
        const response = await fetch(`${AUTH_API_BASE_URL}/api/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name || email.split('@')[0],
                email: email,
                password: password
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Signup failed');
        }

        const data = await response.json();
        const token = data.token;
        const userName = data.user.name || data.user.email || email;
        
        state.authToken = token;
        state.user = userName;
        localStorage.setItem('authToken', token);
        localStorage.setItem('user', userName);
        
        return data;
    } catch (error) {
        throw error;
    }
}

async function checkAuth() {
    const token = localStorage.getItem('authToken');
    if (!token) return false;

    try {
        const response = await fetch(`${AUTH_API_BASE_URL}/api/auth/me`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            state.authToken = null;
            state.user = null;
            localStorage.removeItem('authToken');
            localStorage.removeItem('user');
            return false;
        }

        const data = await response.json();
        state.user = data.user.name || data.user.email;
        localStorage.setItem('user', state.user);
        return true;
    } catch (error) {
        console.error('Auth verification failed:', error);
        return false;
    }
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


function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
        element.classList.add('show');
        setTimeout(() => element.classList.remove('show'), 5000);
    }
    // Hide success message when showing error
    const successEl = document.getElementById('login-success');
    if (successEl) successEl.classList.remove('show');
}

function showSuccess(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
        element.classList.add('show');
        setTimeout(() => element.classList.remove('show'), 5000);
    }
    // Hide error message when showing success
    const errorEl = document.getElementById('login-error');
    if (errorEl) errorEl.classList.remove('show');
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
            <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                <span>✅ Design Generated Successfully</span>
                <button id="tts-report-btn" class="btn btn-secondary btn-sm" style="background: rgba(2, 114, 194, 0.1); border: 1px solid var(--primary);">
                    🔊 Listen to Report
                </button>
            </div>
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
                <div class="info-value"><a href="${previewUrl.startsWith('http') ? previewUrl : API_BASE_URL + previewUrl}" target="_blank">${previewUrl.length > 50 ? previewUrl.substring(0, 50) + '...' : previewUrl}</a></div>
            </div>
            ` : ''}
        </div>
        <div class="json-viewer">${formatJSON(specJson)}</div>
    `;

    // Attach TTS handler
    const ttsBtn = document.getElementById('tts-report-btn');
    if (ttsBtn) {
        ttsBtn.addEventListener('click', () => handleListenReport(specJson, ttsBtn));
    }
}

/**
 * Converts a design JSON object into a readable report text for TTS
 */
function jsonToReadableText(obj) {
    const lines = ["Design report summary."];
    
    if (obj.objects && Array.isArray(obj.objects)) {
        lines.push(`This design contains ${obj.objects.length} elements.`);
        
        obj.objects.forEach((item, index) => {
            const type = item.type || 'item';
            const material = item.material || 'unknown material';
            const color = item.color_hex || 'standard color';
            
            let dimStr = "";
            if (item.dimensions) {
                const d = item.dimensions;
                dimStr = `with dimensions: width ${d.width || 0}, length ${d.length || 0}, height ${d.height || 0}.`;
            }
            
            lines.push(`Element ${index + 1} is a ${type}, made of ${material}, ${dimStr}`);
        });
    }

    if (obj.features) {
        lines.push("Key features include: " + Object.keys(obj.features).join(", ") + ".");
    }

    return lines.join(" ");
}

/**
 * Handles TTS generation and playback
 */
async function handleListenReport(specJson, btn) {
    const originalText = btn.innerHTML;
    const text = jsonToReadableText(specJson);
    
    btn.innerHTML = '<span class="spinner"></span> Synthesizing...';
    btn.disabled = true;

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/tts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': state.authToken ? `Bearer ${state.authToken}` : ''
            },
            body: JSON.stringify({ text })
        });

        if (!response.ok) throw new Error('Failed to generate audio');

        const blob = await response.blob();
        const audioUrl = URL.createObjectURL(blob);
        const audio = new Audio(audioUrl);
        
        btn.innerHTML = '⏸ Playing...';
        btn.disabled = false;
        
        audio.onended = () => {
            btn.innerHTML = originalText;
            URL.revokeObjectURL(audioUrl);
        };

        btn.onclick = () => {
            if (audio.paused) {
                audio.play();
                btn.innerHTML = '⏸ Playing...';
            } else {
                audio.pause();
                btn.innerHTML = '▶ Resume';
            }
        };

        audio.play();
    } catch (e) {
        console.error("TTS Error:", e);
        btn.innerHTML = "❌ Error";
        setTimeout(() => { btn.innerHTML = originalText; btn.disabled = false; }, 3000);
    }
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

    const email = document.getElementById('login-email').value;
    const password = document.getElementById('password').value;
    const btn = e.target.querySelector('button[type="submit"]');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span> Logging in...';
    btn.disabled = true;

    try {
        await login(email, password);
        document.getElementById('login-screen').classList.add('hidden');
        document.getElementById('main-screen').classList.remove('hidden');
        document.getElementById('user-name').textContent = state.user;
        checkAPIHealth();
    } catch (error) {
        showError('login-error', error.message);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

async function handleSignup(e) {
    e.preventDefault();

    const email = document.getElementById('signup-email').value.trim();
    const name = document.getElementById('signup-name').value.trim();
    const password = document.getElementById('signup-password').value;
    const confirmPassword = document.getElementById('signup-confirm-password').value;

    // Client-side validation
    if (!email.includes('@')) {
        showError('login-error', 'Please enter a valid email address');
        return;
    }

    if (password.length < 6) {
        showError('login-error', 'Password must be at least 6 characters');
        return;
    }

    if (password !== confirmPassword) {
        showError('login-error', 'Passwords do not match');
        return;
    }

    const btn = e.target.querySelector('button[type="submit"]');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span> Creating account...';
    btn.disabled = true;

    try {
        const data = await signup(email, password, name);
        // Auto-login after successful signup
        document.getElementById('login-screen').classList.add('hidden');
        document.getElementById('main-screen').classList.remove('hidden');
        document.getElementById('user-name').textContent = state.user;
        checkAPIHealth();
    } catch (error) {
        showError('login-error', error.message);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

function setupAuthToggle() {
    const toggleLogin = document.getElementById('toggle-login');
    const toggleSignup = document.getElementById('toggle-signup');
    const linkLogin = document.getElementById('link-login');
    const linkSignup = document.getElementById('link-signup');
    
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const errorEl = document.getElementById('login-error');
    const successEl = document.getElementById('login-success');

    const showLogin = () => {
        toggleLogin.classList.add('active');
        toggleSignup.classList.remove('active');
        loginForm.classList.remove('hidden');
        signupForm.classList.add('hidden');
        if (errorEl) errorEl.classList.remove('show');
        if (successEl) successEl.classList.remove('show');
    };

    const showSignup = () => {
        toggleSignup.classList.add('active');
        toggleLogin.classList.remove('active');
        signupForm.classList.remove('hidden');
        loginForm.classList.add('hidden');
        if (errorEl) errorEl.classList.remove('show');
        if (successEl) successEl.classList.remove('show');
    };

    toggleLogin.addEventListener('click', showLogin);
    toggleSignup.addEventListener('click', showSignup);
    
    if (linkLogin) {
        linkLogin.addEventListener('click', (e) => {
            e.preventDefault();
            showLogin();
        });
    }
    
    if (linkSignup) {
        linkSignup.addEventListener('click', (e) => {
            e.preventDefault();
            showSignup();
        });
    }
}

async function handleQuickGenerate() {
    const btn = document.getElementById('quick-generate-btn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span class="spinner"></span> Generating...';
    btn.disabled = true;

    try {
        let decodedUserId = state.user || 'user';
        if (state.authToken) {
            try {
                const payloadStr = atob(state.authToken.split('.')[1]);
                const payloadObj = JSON.parse(payloadStr);
                if (payloadObj.id) {
                    decodedUserId = payloadObj.id;
                }
            } catch (e) {
                console.warn("Could not decode user ID from token", e);
            }
        }

        const payload = {
            user_id: decodedUserId,
            prompt: document.getElementById('quick-prompt').value,
            city: document.getElementById('quick-city').value,
            style: document.getElementById('quick-style').value,
            context: {}
        };

        const budgetEl = document.getElementById('quick-budget');
        const budget = budgetEl ? parseInt(budgetEl.value, 10) : 0;
        if (Number.isFinite(budget) && budget > 0) {
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
            loadHistory(); // Refresh history grid with new design

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

            // Auto-load preview when Geometry tab is opened
            if (tabId === 'geometry') {
                setTimeout(() => {
                    loadPreviewFromLastDesign();
                }, 300);
            }
        });
    });
}

function setupThemeToggle() {
    const themeToggleBtn = document.getElementById('theme-toggle');
    const currentTheme = localStorage.getItem('theme') || 'light';

    if (currentTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        if (themeToggleBtn) themeToggleBtn.textContent = '☀️';
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
            if (isDark) {
                document.documentElement.removeAttribute('data-theme');
                localStorage.setItem('theme', 'light');
                themeToggleBtn.textContent = '🌙';
            } else {
                document.documentElement.setAttribute('data-theme', 'dark');
                localStorage.setItem('theme', 'dark');
                themeToggleBtn.textContent = '☀️';
            }
        });
    }
}

// ── History ──────────────────────────────────────────────────────────────────

function formatCurrencyCompact(amount) {
    if (!amount || amount === 0) return 'N/A';
    if (amount >= 10000000) return '₹' + (amount / 10000000).toFixed(1) + 'Cr';
    if (amount >= 100000) return '₹' + (amount / 100000).toFixed(1) + 'L';
    return '₹' + Math.round(amount).toLocaleString('en-IN');
}

async function loadHistory() {
    if (!state.authToken) return;

    const grid    = document.getElementById('history-grid');
    const loading = document.getElementById('history-loading');
    const empty   = document.getElementById('history-empty');
    const errEl   = document.getElementById('history-error');

    if (!grid) return;

    // Show loading state
    loading?.classList.remove('hidden');
    empty?.classList.add('hidden');
    errEl?.classList.add('hidden');
    grid.innerHTML = '';

    try {
        const response = await apiGet('/api/v1/history', { limit: 20 });
        const data = await response.json();

        loading?.classList.add('hidden');

        if (!response.ok) {
            errEl.textContent = `Error: ${data.detail || data.message || 'Failed to load history'}`;
            errEl?.classList.remove('hidden');
            return;
        }

        const specs = data.specs || [];

        // Update dashboard total count with real DB total
        const totalEl = document.getElementById('dashboard-designs');
        if (totalEl) totalEl.textContent = data.total_specs || specs.length;

        if (specs.length === 0) {
            empty?.classList.remove('hidden');
            return;
        }

        renderHistoryGrid(specs);
    } catch (err) {
        loading?.classList.add('hidden');
        if (errEl) {
            errEl.textContent = `Connection error: ${err.message}`;
            errEl.classList.remove('hidden');
        }
    }
}

function renderHistoryGrid(specs) {
    const grid = document.getElementById('history-grid');
    if (!grid) return;

    grid.innerHTML = specs.map(spec => {
        const date = spec.created_at
            ? new Date(spec.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
            : 'Unknown date';
        const cost = formatCurrencyCompact(spec.estimated_cost);
        const city = spec.city || '—';
        const prompt = spec.prompt || 'No prompt';
        const shortPrompt = prompt.length > 80 ? prompt.substring(0, 80) + '…' : prompt;
        const designType = spec.design_type || 'Design';
        const specId = spec.spec_id || '';
        const shortId = specId.length > 16 ? specId.substring(0, 16) + '…' : specId;

        return `
        <div class="history-card" data-spec-id="${specId}">
            <div class="history-card-header">
                <span class="history-badge">${designType}</span>
                <span class="history-date">${date}</span>
            </div>
            <p class="history-prompt">${shortPrompt}</p>
            <div class="history-meta">
                <span class="history-meta-item">📍 ${city}</span>
                <span class="history-meta-item">💰 ${cost}</span>
            </div>
            <div class="history-card-footer">
                <code class="history-spec-id" title="${specId}">${shortId}</code>
                <button class="btn btn-secondary btn-xs history-view-btn" data-spec-id="${specId}">View JSON</button>
            </div>
        </div>`;
    }).join('');

    // Attach View JSON handlers
    grid.querySelectorAll('.history-view-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const sid = btn.getAttribute('data-spec-id');
            btn.textContent = 'Loading…';
            btn.disabled = true;
            try {
                const res = await apiGet(`/api/v1/history/${sid}`);
                const data = await res.json();
                const resultEl = document.getElementById('quick-result');
                if (resultEl) {
                    resultEl.classList.remove('hidden', 'error');
                    resultEl.classList.add('success');
                    const specJson = data.spec_json || data;
                    resultEl.innerHTML = `
                        <div class="result-header success">
                            <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                                <span>📄 Spec: ${sid}</span>
                                <button id="tts-history-btn" class="btn btn-secondary btn-sm" style="background: rgba(2, 114, 194, 0.1); border: 1px solid var(--primary);">
                                    🔊 Listen to Report
                                </button>
                            </div>
                        </div>
                        <div class="json-viewer">${formatJSON(specJson)}</div>`;
                    
                    const ttsBtn = document.getElementById('tts-history-btn');
                    if (ttsBtn) {
                        ttsBtn.addEventListener('click', () => handleListenReport(specJson, ttsBtn));
                    }
                    
                    resultEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            } catch (e) {
                alert('Failed to load spec: ' + e.message);
            } finally {
                btn.textContent = 'View JSON';
                btn.disabled = false;
            }
        });
    });
}

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    // Setup login and signup forms immediately for responsiveness
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    
    if (loginForm) loginForm.addEventListener('submit', handleLogin);
    if (signupForm) signupForm.addEventListener('submit', handleSignup);
    
    setupAuthToggle();
    setupThemeToggle();
    setupTabs();

    // Check API health on load
    checkAPIHealth();

    const isAuthenticated = await checkAuth();
    if (isAuthenticated) {
        document.getElementById('login-screen').classList.add('hidden');
        document.getElementById('main-screen').classList.remove('hidden');
        document.getElementById('user-name').textContent = state.user;
        loadHistory(); // Load history for returning users
    }

    // Setup logout
    document.getElementById('logout-btn').addEventListener('click', () => {
        state.authToken = null;
        state.user = null;
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        document.getElementById('main-screen').classList.add('hidden');
        document.getElementById('login-screen').classList.remove('hidden');
    });

    // Setup all button handlers (only Dashboard and Geometry)
    document.getElementById('quick-generate-btn')?.addEventListener('click', handleQuickGenerate);
    document.getElementById('load-preview-btn')?.addEventListener('click', loadPreviewFromLastDesign);
    document.getElementById('clear-preview-btn')?.addEventListener('click', clearPreview);
    document.getElementById('refresh-history-btn')?.addEventListener('click', loadHistory);

    // Setup Geometry file upload handlers (with delay to ensure DOM is ready)
    setTimeout(() => {
        setupGeometryFileUpload();
    }, 500);

});
