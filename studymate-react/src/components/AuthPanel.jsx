import { useState } from "react";
import { signIn, signUp, saveToken } from "../lib/api";

function AuthPanel({ onAuthenticated }) {
    const [mode, setMode] = useState("signin");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [name, setName] = useState("");
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState("");
    const [message, setMessage] = useState("");

    async function handleSubmit(event) {
        event.preventDefault();
        setBusy(true);
        setError("");
        setMessage("");
        try {
            let result;
            if (mode === "signup") {
                result = await signUp(email.trim(), password, name.trim() || undefined);
                setMessage(`Welcome, ${result.name || result.email}! Your account is ready.`);
            } else {
                result = await signIn(email.trim(), password);
            }
            saveToken(result.access_token);
            onAuthenticated(result.access_token);
            setPassword("");
        } catch (authError) {
            setError(authError.message || "Could not authenticate. Please try again.");
        } finally {
            setBusy(false);
        }
    }

    return (
        <form className="note-form auth-form" onSubmit={handleSubmit} noValidate>
            <div className="form-heading">
                <div>
                    <p className="form-kicker">YOUR PRIVATE STUDY SPACE</p>
                    <h3>{mode === "signin" ? "Sign in to your account" : "Create your account"}</h3>
                </div>
            </div>
            <p className="auth-description">
                Notes are private and saved to your account. No external services required — everything runs locally!
            </p>

            {mode === "signup" && (
                <>
                    <label htmlFor="auth-name">Name (optional)</label>
                    <input
                        id="auth-name"
                        type="text"
                        autoComplete="name"
                        placeholder="Your name"
                        value={name}
                        onChange={(event) => setName(event.target.value)}
                    />
                </>
            )}

            <label htmlFor="auth-email">Email</label>
            <input
                id="auth-email"
                type="email"
                autoComplete="email"
                required
                placeholder="you@example.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
            />
            <label htmlFor="auth-password">Password</label>
            <input
                id="auth-password"
                type="password"
                autoComplete={mode === "signin" ? "current-password" : "new-password"}
                minLength="6"
                required
                placeholder={mode === "signup" ? "At least 6 characters" : "Your password"}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
            />
            {error && <p className="form-error" role="alert">{error}</p>}
            {message && <p className="auth-message" role="status">{message}</p>}
            <div className="form-actions">
                <button className="save-btn" type="submit" disabled={busy}>
                    {busy ? "Please wait..." : mode === "signin" ? "Sign in" : "Create account"}
                </button>
                <button
                    className="cancel-btn"
                    type="button"
                    disabled={busy}
                    onClick={() => {
                        setMode(mode === "signin" ? "signup" : "signin");
                        setError("");
                        setMessage("");
                    }}
                >
                    {mode === "signin" ? "Create account" : "I have an account"}
                </button>
            </div>
        </form>
    );
}

export default AuthPanel;
