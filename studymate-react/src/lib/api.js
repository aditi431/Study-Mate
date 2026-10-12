const apiBaseUrl = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api")
    .replace(/\/+$/, "");

/**
 * Make an authenticated API request to the StudyMate backend.
 * Handles 401 responses by clearing the stored token.
 */
export async function apiRequest(path, { token, ...options } = {}) {
    const headers = new Headers(options.headers || {});
    if (options.body) {
        headers.set("Content-Type", "application/json");
    }
    const storedToken = localStorage.getItem("studymate_access_token") ||
        sessionStorage.getItem("studymate_access_token");
    const activeToken = storedToken || token;
    if (activeToken) {
        headers.set("Authorization", `Bearer ${activeToken}`);
    }

    const response = await fetch(`${apiBaseUrl}${path}`, { ...options, headers });

    if (response.status === 401) {
        // Token expired or invalid — clear and signal logout
        localStorage.removeItem("studymate_access_token");
        sessionStorage.removeItem("studymate_access_token");
        window.dispatchEvent(new Event("studymate:auth-expired"));
    }

    if (!response.ok) {
        const result = await response.json().catch(() => null);
        const message = result?.detail || `Request failed (${response.status}).`;
        throw new Error(message);
    }
    if (response.status === 204) {
        return null;
    }
    return response.json();
}

export function mapNote(note) {
    return {
        ...note,
        topics: note.topics_count
    };
}

/**
 * Sign in with email and password using the local backend.
 * Returns the access token on success.
 */
export async function signIn(email, password) {
    const response = await fetch(`${apiBaseUrl}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
    });
    const result = await response.json().catch(() => null);
    if (!response.ok) {
        throw new Error(result?.detail || "Authentication failed. Check your details and try again.");
    }
    return result; // { access_token, user_id, email, name }
}

/**
 * Register a new account using the local backend.
 */
export async function signUp(email, password, name) {
    const response = await fetch(`${apiBaseUrl}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, name: name || undefined }),
    });
    const result = await response.json().catch(() => null);
    if (!response.ok) {
        throw new Error(result?.detail || "Registration failed. Please try again.");
    }
    return result; // { access_token, user_id, email, name }
}

export function saveToken(token) {
    localStorage.setItem("studymate_access_token", token);
}

export function getStoredToken() {
    return localStorage.getItem("studymate_access_token");
}

export function clearToken() {
    localStorage.removeItem("studymate_access_token");
    sessionStorage.removeItem("studymate_access_token");
}
