let errorTimeout = null;

export function showError(message, duration = 10000) {
    const errorContainer = document.querySelector('.error-container');
    if (!errorContainer) {
        console.error('Error container not found in DOM');
        return;
    }

    // Clear any existing timeouts and remove existing listeners
    if (errorTimeout) {
        clearTimeout(errorTimeout);
    }

    // Remove any existing transitionend listeners
    errorContainer.removeEventListener('transitionend', handleTransitionEnd);

    const errorMessage = errorContainer.querySelector('.error-message');
    if (!errorMessage) {
        console.error('Error message element not found in DOM');
        return;
    }

    // First remove d-none and set message
    errorContainer.classList.remove('d-none');
    errorMessage.textContent = message;

    // Force a reflow before adding the show class
    void errorContainer.offsetWidth;

    // Add show class to trigger animation
    errorContainer.classList.add('show');

    // Set new timeout
    errorTimeout = setTimeout(() => {
        hideError();
    }, duration);
}

// Separate function to handle transition end
function handleTransitionEnd() {
    const errorContainer = document.querySelector('.error-container');
    if (!errorContainer) return;

    if (!errorContainer.classList.contains('show')) {
        errorContainer.classList.add('d-none');
        const errorMessage = errorContainer.querySelector('.error-message');
        if (errorMessage) {
            errorMessage.textContent = '';
        }
    }
}

export function hideError() {
    const errorContainer = document.querySelector('.error-container');
    if (!errorContainer) {
        console.error('Error container not found in DOM');
        return;
    }

    // Clear any existing timeout
    if (errorTimeout) {
        clearTimeout(errorTimeout);
        errorTimeout = null;
    }

    // Add the transition end listener
    errorContainer.addEventListener('transitionend', handleTransitionEnd, {
        once: true,
    });

    // Remove show class to trigger hide animation
    errorContainer.classList.remove('show');
}

// Initialize error handling
document.addEventListener('DOMContentLoaded', () => {
    const errorContainer = document.querySelector('.error-container');
    if (!errorContainer) {
        console.error('Error container not found during initialization');
        return;
    }

    const closeButton = errorContainer.querySelector('.btn-close');
    if (!closeButton) {
        console.error('Close button not found in error container');
        return;
    }

    closeButton.addEventListener('click', () => {
        hideError();
    });

    document.querySelectorAll('.nav-link').forEach((link) => {
        link.addEventListener('click', (e) => {
            const currentPath = window.location.pathname;
            const targetPath = link.getAttribute('href');

            // If we're already on this page, prevent navigation
            if (currentPath === targetPath) {
                e.preventDefault();
            }
        });
    });

    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', (e) => {
            e.preventDefault();
            handleLogout();
        });
    }

    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', handleSignup);
    }
});
