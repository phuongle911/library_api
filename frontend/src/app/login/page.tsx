"use client";

import { useState } from "react";
import { loginUser, saveToken } from "@/services/auth";
import "./login.css";

export default function LoginPage() {
  const [email, setEmail] = useState("phuong123@example.com");
  const [password, setPassword] = useState("phuong123");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    try {
      setLoading(true);
      const response = await loginUser({ email, password });
      saveToken(response.access_token);
      alert("Login successful!");
    } catch (error) {
      console.error(error);
      setError("Login failed. Please check API URL, backend, or credentials.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-page">
      <div className="login-card">
        <h1>Welcome Back</h1>
        <p>Login to access the library system.</p>

        <form onSubmit={handleLogin}>
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {error && <div className="login-error">{error}</div>}

          <button disabled={loading}>
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>
      </div>
    </main>
  );
}
