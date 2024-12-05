// Add this function at the top of the file
function setupAuthHeaderInterceptor() {
    const token = localStorage.getItem('access_token');
    if (token) {
        return {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
        };
    }
    return {};
}

async function checkAuthAndRedirect() {
    const currentPath = window.location.pathname;
    // Skip check for login and signup pages
    if (['/auth/login', '/auth/register'].includes(currentPath)) {
        return;
    }

    try {
        const response = await fetch('/auth/me', {
            headers: {
                Authorization: `Bearer ${localStorage.getItem('access_token')}`,
            },
        });

        console.log(response);

        if (!response.ok) {
            // Redirect to login if unauthorized
            window.location.href = '/auth/login';
        }
    } catch (error) {
        console.error('Auth check failed:', error);
        window.location.href = '/auth/login';
    }
}

async function handleSignup(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    try {
        const response = await fetch('/auth/register', {
            method: 'POST',
            body: formData,
        });

        const data = await response.json();

        if (response.ok) {
            // Store the token
            localStorage.setItem('access_token', data.access_token);
            // Redirect to home
            window.location.href = '/';
        } else {
            // Display error message
            const errorDiv =
                document.querySelector('.error-message') ||
                document.createElement('div');
            errorDiv.className = 'error-message';
            errorDiv.textContent = data.detail;
            form.insertBefore(errorDiv, form.querySelector('button'));
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

async function handleLogout() {
    try {
        const response = await fetch('/logout', {
            method: 'POST',
            credentials: 'include',
            // Remove redirect: 'follow' as we'll handle it manually
        });

        if (response.ok) {
            // If logout successful, manually redirect to login page
            window.location.href = '/login';
        } else {
            const data = await response.json();
            showError(data.detail || 'Logout failed');
        }
    } catch (error) {
        showError('Network error during logout');
    }
}

async function handleLogin(event) {
    event.preventDefault();

    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    try {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);
        const response = await fetch('/auth/token', {
            method: 'POST',
            body: formData,
        });

        const data = await response.json();

        if (data.access_token) {
            localStorage.setItem('access_token', data.access_token);
            // Use fetch with authorization header
            const homeResponse = await fetch('/', {
                headers: setupAuthHeaderInterceptor(),
            });

            if (homeResponse.ok) {
                window.location.href = '/';
            } else {
                alert('Error accessing home page. Please try again.');
            }
        } else {
            alert('Login failed: ' + (data.detail || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error during login:', error);
        alert('An error occurred. Please try again.');
    }
}

// Initialize error handling
document.addEventListener('DOMContentLoaded', () => {
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', (e) => {
            e.preventDefault();
            handleLogout();
        });
    }

    checkAuthAndRedirect();

    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', handleSignup);
    }

    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
});
