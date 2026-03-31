import sys

with open(r'c:\Users\PIXEL\Desktop\Sid\prompt\frontend-webapp\app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Make the changes
content = content.replace(
    "const state = {\n    authToken: null,\n    user: null,", 
    "const AUTH_API_BASE_URL = 'https://ai-being-ecwj.onrender.com';\n\nconst state = {\n    authToken: localStorage.getItem('authToken'),\n    user: localStorage.getItem('user'),"
)

# And if it is \r\n
content = content.replace(
    "const state = {\r\n    authToken: null,\r\n    user: null,", 
    "const AUTH_API_BASE_URL = 'https://ai-being-ecwj.onrender.com';\n\nconst state = {\n    authToken: localStorage.getItem('authToken'),\n    user: localStorage.getItem('user'),"
)

# Replace login
login_start = content.find('async function login(email, password) {')
login_end = content.find('}', content.find('catch (error) {', login_start)) + 1
new_login = """async function login(email, password) {
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
}"""
content = content[:login_start] + new_login + content[login_end:]

# Replace signup
signup_start = content.find('async function signup(email, password, name) {')
signup_end = content.find('}', content.find('catch (error) {', signup_start)) + 1
new_signup = """async function signup(email, password, name) {
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
}"""
content = content[:signup_start] + new_signup + content[signup_end:]

# Replace init handling
init_target = """    checkAPIHealth();
    checkVideoAPIHealth();"""

init_replacement = """    checkAPIHealth();
    checkVideoAPIHealth();

    const isAuthenticated = await checkAuth();
    if (isAuthenticated) {
        document.getElementById('login-screen').classList.add('hidden');
        document.getElementById('main-screen').classList.remove('hidden');
        document.getElementById('user-name').textContent = state.user;
    }"""
content = content.replace(init_target, init_replacement)
content = content.replace(init_target.replace('\n', '\r\n'), init_replacement.replace('\n', '\r\n'))

logout_target = """    document.getElementById('logout-btn').addEventListener('click', () => {
        state.authToken = null;
        state.user = null;
        document.getElementById('main-screen').classList.add('hidden');
        document.getElementById('login-screen').classList.remove('hidden');
    });"""
logout_replacement = """    document.getElementById('logout-btn').addEventListener('click', () => {
        state.authToken = null;
        state.user = null;
        localStorage.removeItem('authToken');
        localStorage.removeItem('user');
        document.getElementById('main-screen').classList.add('hidden');
        document.getElementById('login-screen').classList.remove('hidden');
    });"""
content = content.replace(logout_target, logout_replacement)
content = content.replace(logout_target.replace('\n', '\r\n'), logout_replacement.replace('\n', '\r\n'))

# Write back
with open(r'c:\Users\PIXEL\Desktop\Sid\prompt\frontend-webapp\app.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated app.js")
