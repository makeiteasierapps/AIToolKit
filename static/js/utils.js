let errorTimeout = null;

function showError(message, duration = 3000) {
  const errorContainer = document.querySelector(".error-container");
  if (!errorContainer) {
    console.error("Error container not found in DOM");
    return;
  }

  // Clear any existing timeouts and remove existing listeners
  if (errorTimeout) {
    clearTimeout(errorTimeout);
  }

  // Remove any existing transitionend listeners
  errorContainer.removeEventListener("transitionend", handleTransitionEnd);

  const errorMessage = errorContainer.querySelector(".error-message");
  if (!errorMessage) {
    console.error("Error message element not found in DOM");
    return;
  }

  // First remove d-none and set message
  errorContainer.classList.remove("d-none");
  errorMessage.textContent = message;

  // Force a reflow before adding the show class
  void errorContainer.offsetWidth;

  // Add show class to trigger animation
  errorContainer.classList.add("show");

  // Set new timeout
  errorTimeout = setTimeout(() => {
    hideError();
  }, duration);
}

// Separate function to handle transition end
function handleTransitionEnd() {
  const errorContainer = document.querySelector(".error-container");
  if (!errorContainer) return;

  if (!errorContainer.classList.contains("show")) {
    errorContainer.classList.add("d-none");
    const errorMessage = errorContainer.querySelector(".error-message");
    if (errorMessage) {
      errorMessage.textContent = "";
    }
  }
}

function hideError() {
  const errorContainer = document.querySelector(".error-container");
  if (!errorContainer) {
    console.error("Error container not found in DOM");
    return;
  }

  // Clear any existing timeout
  if (errorTimeout) {
    clearTimeout(errorTimeout);
    errorTimeout = null;
  }

  // Add the transition end listener
  errorContainer.addEventListener("transitionend", handleTransitionEnd, {
    once: true,
  });

  // Remove show class to trigger hide animation
  errorContainer.classList.remove("show");
}

// Add this function to handle protected route navigation
async function checkAuthAndRedirect() {
  console.log("running function");
  const currentPath = window.location.pathname;
  // Skip check for login and signup pages
  if (["/auth/login", "/auth/register"].includes(currentPath)) {
    return;
  }

  try {
    const response = await fetch("/auth/me", {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
      },
    });

    console.log(response);

    if (!response.ok) {
      // Redirect to login if unauthorized
      window.location.href = "/auth/login";
    }
  } catch (error) {
    console.error("Auth check failed:", error);
    window.location.href = "/auth/login";
  }
}

async function handleLogout() {
  try {
    const response = await fetch("/logout", {
      method: "POST",
      credentials: "include",
      // Remove redirect: 'follow' as we'll handle it manually
    });

    if (response.ok) {
      // If logout successful, manually redirect to login page
      window.location.href = "/login";
    } else {
      const data = await response.json();
      showError(data.detail || "Logout failed");
    }
  } catch (error) {
    showError("Network error during logout");
  }
}

async function handleSignup(event) {
  event.preventDefault();

  const form = event.target;
  const formData = new FormData(form);

  try {
    const response = await fetch("/auth/register", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (response.ok) {
      // Store the token
      localStorage.setItem("token", data.access_token);
      // Redirect to home
      window.location.href = "/";
    } else {
      // Display error message
      const errorDiv =
        document.querySelector(".error-message") ||
        document.createElement("div");
      errorDiv.className = "error-message";
      errorDiv.textContent = data.detail;
      form.insertBefore(errorDiv, form.querySelector("button"));
    }
  } catch (error) {
    console.error("Error:", error);
  }
}

// Initialize error handling
document.addEventListener("DOMContentLoaded", () => {
  const errorContainer = document.querySelector(".error-container");
  if (!errorContainer) {
    console.error("Error container not found during initialization");
    return;
  }

  const closeButton = errorContainer.querySelector(".btn-close");
  if (!closeButton) {
    console.error("Close button not found in error container");
    return;
  }

  closeButton.addEventListener("click", () => {
    hideError();
  });

  document.querySelectorAll(".nav-link").forEach((link) => {
    link.addEventListener("click", (e) => {
      const currentPath = window.location.pathname;
      const targetPath = link.getAttribute("href");

      // If we're already on this page, prevent navigation
      if (currentPath === targetPath) {
        e.preventDefault();
      }
    });
  });

  const logoutButton = document.getElementById("logoutButton");
  if (logoutButton) {
    logoutButton.addEventListener("click", (e) => {
      e.preventDefault();
      handleLogout();
    });
  }

  checkAuthAndRedirect();

  const signupForm = document.getElementById("signup-form");
  if (signupForm) {
    signupForm.addEventListener("submit", handleSignup);
  }
});
