// Constants
const API_ROUTES = {
    LOGIN: '/auth/token',
    REFRESH: '/auth/refresh',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    VALIDATE: '/auth/validate',
};
// Utility functions

const redirectTo = (path) => (window.location.href = path);

// Error handling utility
class ApiError extends Error {
    constructor(message, status) {
        super(message);
        this.status = status;
    }
}
class ApiClient {
    static async request(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            credentials: 'include',
        };
        try {
            let response = await fetch(url, { ...defaultOptions, ...options });
            // Handle 401 responses
            if (response.status === 401) {
                const refreshToken = localStorage.getItem('refresh_token');
                if (refreshToken) {
                    try {
                        // Attempt to refresh the token
                        const newToken = await Auth.refreshToken();
                        if (newToken) {
                            // Retry the original request
                            response = await fetch(url, {
                                ...defaultOptions,
                                ...options,
                            });
                        }
                    } catch (refreshError) {
                        // If refresh fails, redirect to login
                        Auth.handleAuthFailure();
                        throw refreshError;
                    }
                } else {
                    Auth.handleAuthFailure();
                }
            }
            const data = await response.json();
            if (!response.ok) {
                throw new ApiError(
                    data.detail || 'Request failed',
                    response.status
                );
            }
            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }
}
class Auth {
    static async refreshToken() {
        try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (!refreshToken) return null;
            const data = await ApiClient.request(API_ROUTES.REFRESH, {
                method: 'POST',
                body: JSON.stringify({ token: refreshToken }),
            });
            return data.access_token;
        } catch {
            this.handleAuthFailure();
            return null;
        }
    }
    static async login(username, password) {
        const formData = new URLSearchParams({ username, password });
        const response = await ApiClient.request(API_ROUTES.LOGIN, {
            method: 'POST',
            body: formData,
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        });
        if (response.status === 'success') {
            localStorage.setItem('refresh_token', response.refresh_token);
            redirectTo('/');
        }
    }
    static async signup(formData) {
        const response = await ApiClient.request(API_ROUTES.REGISTER, {
            method: 'POST',
            body: formData,
        });
        if (response.status === 'success') {
            redirectTo('/');
        }
    }
    static async logout() {
        try {
            await ApiClient.request(API_ROUTES.LOGOUT, { method: 'POST' });
        } finally {
            localStorage.removeItem('refresh_token');
            redirectTo('/auth/login');
        }
    }
    static async validateSession() {
        try {
            // Make a lightweight request to validate the current session
            await ApiClient.request(API_ROUTES.VALIDATE, {
                method: 'GET',
            });
            return true;
        } catch (error) {
            if (error.status === 401) {
                this.handleAuthFailure();
            }
            return false;
        }
    }
    static handleAuthFailure() {
        localStorage.removeItem('refresh_token');
        redirectTo('/auth/login');
    }
}
// UI Handler
class AuthUI {
    static showError(formId, message) {
        const form = document.getElementById(formId);
        const errorDiv =
            form.querySelector('.error-message') ||
            document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        form.insertBefore(errorDiv, form.querySelector('button'));
    }
    static async handleSubmit(event, action) {
        event.preventDefault();
        try {
            if (action === 'login') {
                await Auth.login(
                    document.getElementById('login-username').value,
                    document.getElementById('login-password').value
                );
            } else if (action === 'signup') {
                await Auth.signup(new FormData(event.target));
            }
        } catch (error) {
            this.showError(event.target.id, error.message);
        }
    }
    static init() {
        const forms = {
            'login-form': 'login',
            'signup-form': 'signup',
        };
        Object.entries(forms).forEach(([formId, action]) => {
            const form = document.getElementById(formId);
            if (form) {
                form.addEventListener('submit', (e) =>
                    this.handleSubmit(e, action)
                );
            }
        });
        const logoutButton = document.getElementById('logoutButton');
        if (logoutButton) {
            logoutButton.addEventListener('click', (e) => {
                e.preventDefault();
                Auth.logout();
            });
        }
    }
}
// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    if (!window.location.pathname.includes('/auth/')) {
        await Auth.validateSession();
    }
    AuthUI.init();
});
