"use client";
import React, { useState } from "react";
import { apiFetch } from "@/lib/api";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    setError(null);
    setLoading(true);
    try {
      await apiFetch(`/auth/forgot-password`, {
        method: "POST",
        body: { email },
      });
      setMessage("If an account exists, a reset email has been sent.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to send reset email");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto w-full max-w-md">
      <h1 className="mb-6 text-2xl font-semibold">Forgot password</h1>
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="mb-1 block text-sm">Email</label>
          <input type="email" className="w-full rounded border px-3 py-2" required value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        {message && <p className="text-sm text-green-600">{message}</p>}
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button disabled={loading} className="w-full rounded bg-gray-900 px-4 py-2 text-white disabled:opacity-50">{loading ? "Sending..." : "Send reset email"}</button>
      </form>
    </div>
  );
}


