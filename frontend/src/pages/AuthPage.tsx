import { useState } from "react";
import { api } from "../api/client";
import type { AuthResponse, AuthUser } from "../types";

export function AuthPage({ onAuthenticated }: { onAuthenticated: (user: AuthUser) => void }) {
  const [registering, setRegistering] = useState(true);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    const data = new FormData(event.currentTarget);
    try {
      const response = await api.post<AuthResponse>(registering ? "/auth/register" : "/auth/login", {
        name: registering ? data.get("name") : undefined,
        email: data.get("email"),
        password: data.get("password"),
      });
      localStorage.setItem("job-agent-token", response.data.access_token);
      onAuthenticated(response.data.user);
    } catch (requestError: any) {
      setError(requestError.response?.data?.detail ?? "Authentication failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="main-content">
      <section className="detail-drawer" style={{ maxWidth: 520, margin: "80px auto" }}>
        <header>
          <div>
            <h1>{registering ? "Create account" : "Sign in"}</h1>
            <p>Your resumes, jobs, matches, and application materials are private to your account.</p>
          </div>
        </header>
        <form className="form-grid" onSubmit={submit}>
          {registering && (
            <label className="field full">
              <span>Name</span>
              <input name="name" data-testid="auth-name" />
            </label>
          )}
          <label className="field full">
            <span>Email</span>
            <input name="email" type="email" required data-testid="auth-email" />
          </label>
          <label className="field full">
            <span>Password</span>
            <input name="password" type="password" minLength={8} required data-testid="auth-password" />
          </label>
          <button className="primary-button" type="submit" disabled={loading} data-testid="auth-submit">
            {loading ? "Please wait..." : registering ? "Create account" : "Sign in"}
          </button>
        </form>
        {error && <p className="notice">{error}</p>}
        <button className="secondary-button" type="button" onClick={() => setRegistering((value) => !value)}>
          {registering ? "Already have an account? Sign in" : "Need an account? Register"}
        </button>
      </section>
    </main>
  );
}
