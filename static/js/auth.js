class Auth {
    static getAuthHeaders() {
        return {
            'Content-Type': 'application/json',
        };
    }

    static async handleResponse(response) {
        if (response.status === 401) {
            if (!window.location.pathname.includes('/auth/login')) {
                window.location.href = '/auth/login';
            }
            throw new Error('Unauthorized');
        }

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.detail || 'Request failed');
        }
        return data;
    }

    static async login(username, password) {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch('/auth/token', {
            method: 'POST',
            body: formData,
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            credentials: 'include',
        });

        const data = await this.handleResponse(response);
        if (data.status === 'success') {
            window.location.href = '/';
        }
    }

    static async signup(formData) {
        const response = await fetch('/auth/register', {
            method: 'POST',
            body: formData,
        });

        const data = await this.handleResponse(response);
        if (data.access_token) {
            localStorage.setItem('access_token', data.access_token);
            window.location.href = '/';
        }
    }

    static async logout() {
        try {
            const response = await fetch('/auth/logout', {
                method: 'POST',
                credentials: 'include',
            });

            if (response.ok) {
                window.location.href = '/auth/login';
            }
        } catch (error) {
            console.error('Logout failed:', error);
            window.location.href = '/auth/login';
        }
    }
}

// Event handlers
async function handleLogin(event) {
    event.preventDefault();

    const errorDiv =
        document.querySelector('.error-message') ||
        document.createElement('div');
    errorDiv.className = 'error-message';

    try {
        await Auth.login(
            document.getElementById('login-username').value,
            document.getElementById('login-password').value
        );
    } catch (error) {
        errorDiv.textContent = error.message;
        const form = document.getElementById('login-form');
        form.insertBefore(errorDiv, form.querySelector('button'));
    }
}

async function handleSignup(event) {
    event.preventDefault();

    const errorDiv =
        document.querySelector('.error-message') ||
        document.createElement('div');
    errorDiv.className = 'error-message';

    try {
        const formData = new FormData(event.target);
        await Auth.signup(formData);
    } catch (error) {
        errorDiv.textContent = error.message;
        const form = document.getElementById('signup-form');
        form.insertBefore(errorDiv, form.querySelector('button'));
    }
}

// Initialize event listeners
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const logoutButton = document.getElementById('logoutButton');

    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    if (signupForm) {
        signupForm.addEventListener('submit', handleSignup);
    }

    if (logoutButton) {
        logoutButton.addEventListener('click', (e) => {
            e.preventDefault();
            Auth.logout();
        });
    }
});
