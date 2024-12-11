const API_ROUTES = {
    LOGIN: '/auth/token',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
};

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
            const response = await fetch(url, {
                ...defaultOptions,
                ...options,
            });
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
    static async login(username, password) {
        const formData = new URLSearchParams({ username, password });
        await ApiClient.request(API_ROUTES.LOGIN, {
            method: 'POST',
            body: formData,
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        });
    }

    static async signup(formData) {
        const data = Object.fromEntries(formData.entries());
        await ApiClient.request(API_ROUTES.REGISTER, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    static async logout() {
        await ApiClient.request(API_ROUTES.LOGOUT, { method: 'POST' });
    }
}

class FormValidator {
    static passwordRegex =
        /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/;
    static validatePassword(password) {
        return this.passwordRegex.test(password);
    }
    static validatePasswordMatch(password, confirmPassword) {
        return password === confirmPassword;
    }
    static validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    static validateUsername(username) {
        return username.length >= 3;
    }
    static getPasswordStrength(password) {
        let strength = 0;
        if (password.length >= 8) strength++;
        if (password.match(/[A-Z]/)) strength++;
        if (password.match(/[a-z]/)) strength++;
        if (password.match(/[0-9]/)) strength++;
        if (password.match(/[^A-Za-z0-9]/)) strength++;
        return strength;
    }
}
class AuthUI {
    static forms = {
        login: {
            id: 'login-form',
            button: null,
            isSubmitting: false,
            hasInteracted: false,
        },
        signup: {
            id: 'signup-form',
            button: null,
            isSubmitting: false,
            hasInteracted: false,
        },
    };

    static showError(formId, message) {
        const form = document.getElementById(formId);
        const errorDiv =
            form.querySelector('.error-message') ||
            document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        form.insertBefore(errorDiv, form.querySelector('button'));
    }
    static setSubmitting(formType, isSubmitting) {
        const form = this.forms[formType];
        form.isSubmitting = isSubmitting;
        form.button.disabled = isSubmitting;
        form.button.innerHTML = isSubmitting
            ? '<span class="spinner"></span> Processing...'
            : formType === 'login'
            ? 'Sign In'
            : 'Sign Up';
    }
    static validateForm(formId) {
        const form = document.getElementById(formId);
        const formType = formId === 'login-form' ? 'login' : 'signup';
        if (formType === 'signup') {
            const password = form.querySelector('#signup-password').value;
            const confirmPassword = form.querySelector(
                '#signup-confirm-password'
            ).value;
            const email = form.querySelector('#signup-email').value;
            const username = form.querySelector('#signup-username').value;
            if (!FormValidator.validateUsername(username)) {
                this.showError(
                    formId,
                    'Username must be at least 3 characters long'
                );
                return false;
            }
            if (!FormValidator.validateEmail(email)) {
                this.showError(formId, 'Please enter a valid email address');
                return false;
            }
            if (!FormValidator.validatePassword(password)) {
                this.showError(formId, 'Password does not meet requirements');
                return false;
            }
            if (
                !FormValidator.validatePasswordMatch(password, confirmPassword)
            ) {
                this.showError(formId, 'Passwords do not match');
                return false;
            }
        }
        return true;
    }
    static async handleSubmit(event, action) {
        event.preventDefault();
        if (this.forms[action].isSubmitting) return;
        if (!this.validateForm(event.target.id)) return;

        try {
            this.setSubmitting(action, true);
            if (action === 'login') {
                await Auth.login(
                    document.getElementById('login-username').value,
                    document.getElementById('login-password').value
                );
            } else if (action === 'signup') {
                const formData = new FormData(event.target);
                formData.delete('confirm_password');
                await Auth.signup(formData);
            }
        } catch (error) {
            this.showError(event.target.id, error.message);
        } finally {
            this.setSubmitting(action, false);
        }
    }
    static setupFormValidation() {
        const signupForm = document.getElementById('signup-form');
        if (signupForm) {
            const inputs = signupForm.querySelectorAll('input');
            const submitButton = signupForm.querySelector(
                'button[type="submit"]'
            );
            // Initialize validation state
            let validationStarted = false;
            const startValidation = () => {
                if (!validationStarted) {
                    validationStarted = true;
                    inputs.forEach((input) => {
                        // Add required attribute and other validation attributes
                        if (input.dataset.validation) {
                            const validations =
                                input.dataset.validation.split(' ');
                            if (validations.includes('required')) {
                                input.required = true;
                            }
                            if (validations.includes('email')) {
                                input.type = 'email';
                            }
                        }
                    });
                }
            };
            const validateInputs = () => {
                if (!validationStarted) return;
                const password =
                    signupForm.querySelector('#signup-password').value;
                const confirmPassword = signupForm.querySelector(
                    '#signup-confirm-password'
                ).value;
                const email = signupForm.querySelector('#signup-email').value;
                const username =
                    signupForm.querySelector('#signup-username').value;
                let isValid = true;
                // Username validation
                const usernameInput =
                    signupForm.querySelector('#signup-username');
                if (username) {
                    if (!FormValidator.validateUsername(username)) {
                        usernameInput.classList.add('is-invalid');
                        isValid = false;
                    } else {
                        usernameInput.classList.remove('is-invalid');
                        usernameInput.classList.add('is-valid');
                    }
                }
                // Email validation
                const emailInput = signupForm.querySelector('#signup-email');
                if (email) {
                    if (!FormValidator.validateEmail(email)) {
                        emailInput.classList.add('is-invalid');
                        isValid = false;
                    } else {
                        emailInput.classList.remove('is-invalid');
                        emailInput.classList.add('is-valid');
                    }
                }
                // Password validation
                const passwordInput =
                    signupForm.querySelector('#signup-password');
                const confirmPasswordInput = signupForm.querySelector(
                    '#signup-confirm-password'
                );
                if (password) {
                    if (!FormValidator.validatePassword(password)) {
                        passwordInput.classList.add('is-invalid');
                        isValid = false;
                    } else {
                        passwordInput.classList.remove('is-invalid');
                        passwordInput.classList.add('is-valid');
                    }
                }
                // Confirm password validation
                if (confirmPassword) {
                    const matchMessage = signupForm.querySelector(
                        '.password-match-message'
                    );
                    if (password !== confirmPassword) {
                        confirmPasswordInput.classList.add('is-invalid');
                        matchMessage.style.display = 'block';
                        isValid = false;
                    } else {
                        confirmPasswordInput.classList.remove('is-invalid');
                        confirmPasswordInput.classList.add('is-valid');
                        matchMessage.style.display = 'none';
                    }
                }
                submitButton.disabled = !isValid;
            };
            // Add input event listeners
            inputs.forEach((input) => {
                input.addEventListener('focus', () => {
                    startValidation();
                });
                input.addEventListener('input', () => {
                    validateInputs();
                });
            });
            // Add form submit validation
            signupForm.addEventListener('submit', (e) => {
                startValidation();
                validateInputs();
                if (!validationStarted || !signupForm.checkValidity()) {
                    e.preventDefault();
                    return false;
                }
            });
        }
    }
    static init() {
        // Store button references
        this.forms.login.button = document.querySelector(
            '#login-form button[type="submit"]'
        );
        this.forms.signup.button = document.querySelector(
            '#signup-form button[type="submit"]'
        );
        // Setup form handlers
        Object.entries(this.forms).forEach(([action, form]) => {
            const formElement = document.getElementById(form.id);
            if (formElement) {
                formElement.addEventListener('submit', (e) =>
                    this.handleSubmit(e, action)
                );
            }
        });
        // Setup real-time validation
        this.setupFormValidation();
        // Setup logout handler
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
document.addEventListener('DOMContentLoaded', () => {
    AuthUI.init();
});
